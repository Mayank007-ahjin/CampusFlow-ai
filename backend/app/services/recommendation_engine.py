from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import os

from ..models import Facility, FacilityType, CrowdLevel
from ..models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationOption,
    AlertResponse,
    AlertListResponse
)
from ..core.config import settings
from .crowd_estimator import CrowdEstimatorService


class RecommendationEngine:
    """Service for generating AI-powered facility recommendations and multi-facility route planning."""

    def __init__(self, db: Session):
        self.db = db
        self.crowd_estimator = CrowdEstimatorService(db)

    async def get_recommendations(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Generate facility recommendations based on natural language query.

        Uses deterministic scoring for ranking facilities, and optionally
        uses LLM for natural language explanation.
        """
        query_lower = request.query.lower()
        target_types = request.facility_types

        if not target_types:
            if any(w in query_lower for w in ["stationery", "print", "shop", "pen", "notebook"]):
                target_types = [FacilityType.STATIONERY]
            elif any(w in query_lower for w in ["office", "administrative", "admin", "dean", "fees", "registration"]):
                target_types = [FacilityType.OFFICE]
            elif any(w in query_lower for w in ["library", "book", "study", "read", "quiet"]):
                target_types = [FacilityType.LIBRARY]
            elif any(w in query_lower for w in ["canteen", "food", "lunch", "eat", "hungry", "snack"]):
                target_types = [FacilityType.CANTEEN]

        # Get facilities matching criteria
        facilities = self._get_candidate_facilities(
            facility_types=target_types,
            include_closed=request.include_closed
        )

        if not facilities:
            facilities = self._get_candidate_facilities(include_closed=request.include_closed)

        if not facilities:
            return RecommendationResponse(
                query=request.query,
                answer="No facilities currently available.",
                recommendations=[],
                timestamp=datetime.utcnow()
            )

        # Score and rank facilities
        ranked_options = self._rank_facilities(
            facilities=facilities,
            max_wait_minutes=request.max_wait_minutes
        )

        is_comparison = any(w in query_lower for w in ["all", "compare", "list", "everything", "best places", "what's available"])
        final_options = ranked_options if (target_types or is_comparison) else ranked_options[:1]

        # Generate structured bullet & arrow explanation (4-5 lines)
        answer = await self._generate_explanation(
            query=request.query,
            options=final_options
        )

        return RecommendationResponse(
            query=request.query,
            answer=answer,
            recommendations=final_options,
            timestamp=datetime.utcnow()
        )

    async def plan_multi_facility_route(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Plan optimal route across multiple facilities based on query using LLM and intelligent sequencing.
        """
        query_lower = request.query.lower()
        facilities = self._get_candidate_facilities(
            facility_types=request.facility_types,
            include_closed=request.include_closed
        )

        if not facilities:
            facilities = self._get_candidate_facilities(include_closed=request.include_closed)

        ranked_options = self._rank_facilities(
            facilities=facilities,
            max_wait_minutes=request.max_wait_minutes
        )

        # Intelligent sorting based on custom query keywords
        if any(w in query_lower for w in ["stationery", "print", "shop"]):
            ranked_options.sort(key=lambda x: 0 if x.facility_type == FacilityType.STATIONERY else 1)
        elif any(w in query_lower for w in ["office", "administrative", "admin"]):
            ranked_options.sort(key=lambda x: 0 if x.facility_type == FacilityType.OFFICE else 1)
        elif any(w in query_lower for w in ["food", "lunch", "canteen", "eat"]):
            ranked_options.sort(key=lambda x: 0 if x.facility_type == FacilityType.CANTEEN else 1)
        elif any(w in query_lower for w in ["study", "library", "book", "read", "quiet"]):
            ranked_options.sort(key=lambda x: 0 if x.facility_type == FacilityType.LIBRARY else 1)

        # Generate structured arrow route itinerary (4-5 lines)
        answer = await self._generate_route_explanation(
            query=request.query,
            options=ranked_options
        )

        return RecommendationResponse(
            query=request.query,
            answer=answer,
            recommendations=ranked_options,
            timestamp=datetime.utcnow()
        )

    def get_proactive_alerts(self) -> AlertListResponse:
        """
        Generate proactive peak-hour alerts and campus bottleneck warnings.
        """
        facilities = self._get_candidate_facilities(include_closed=False)
        alerts = []

        for facility in facilities:
            if facility.current_crowd_level == CrowdLevel.HIGH:
                wait_str = f" (~{facility.estimated_wait_minutes}m wait)" if facility.estimated_wait_minutes else ""
                alerts.append(AlertResponse(
                    id=facility.id,
                    facility_name=facility.name,
                    alert_type="peak_rush",
                    severity="high",
                    message=f"{facility.name}: High traffic{wait_str}. Consider alternatives.",
                    timestamp=datetime.utcnow()
                ))
            elif facility.type == FacilityType.LIBRARY and facility.available_seats and facility.available_seats > 30:
                alerts.append(AlertResponse(
                    id=facility.id,
                    facility_name=facility.name,
                    alert_type="optimal_study",
                    severity="info",
                    message=f"{facility.name}: {facility.available_seats} open seats. Recommended.",
                    timestamp=datetime.utcnow()
                ))

        if not alerts:
            alerts.append(AlertResponse(
                id=0,
                facility_name="Campus Network",
                alert_type="status_normal",
                severity="low",
                message="All campus facilities operating normally.",
                timestamp=datetime.utcnow()
            ))

        return AlertListResponse(alerts=alerts, count=len(alerts))

    def _get_candidate_facilities(
        self,
        facility_types: Optional[List[FacilityType]] = None,
        include_closed: bool = False
    ) -> List[Facility]:
        """Get facilities matching filter criteria."""
        query = self.db.query(Facility)

        if facility_types:
            enum_types = [t if isinstance(t, FacilityType) else FacilityType(t) for t in facility_types]
            query = query.filter(Facility.type.in_(enum_types))

        if not include_closed:
            query = query.filter(Facility.is_open == True)

        return query.all()

    def _rank_facilities(
        self,
        facilities: List[Facility],
        max_wait_minutes: Optional[int] = None
    ) -> List[RecommendationOption]:
        """
        Rank facilities using deterministic scoring algorithm.
        """
        options = []

        for facility in facilities:
            if max_wait_minutes is not None:
                if facility.estimated_wait_minutes and facility.estimated_wait_minutes > max_wait_minutes:
                    continue

            score = self._calculate_facility_score(facility)
            reason = self._generate_reason(facility)

            options.append(RecommendationOption(
                facility_id=facility.id,
                facility_name=facility.name,
                facility_type=facility.type,
                crowd_level=facility.current_crowd_level,
                estimated_wait_minutes=facility.estimated_wait_minutes,
                available_seats=facility.available_seats,
                score=score,
                reason=reason
            ))

        options.sort(key=lambda x: x.score, reverse=True)
        return options

    def _calculate_facility_score(self, facility: Facility) -> float:
        """Calculate facility score (0.0 to 1.0)."""
        score = 1.0

        crowd_penalties = {
            CrowdLevel.LOW: 0.0,
            CrowdLevel.MODERATE: 0.2,
            CrowdLevel.HIGH: 0.4
        }
        score -= crowd_penalties.get(facility.current_crowd_level, 0.2)

        if facility.estimated_wait_minutes:
            wait_penalty = min(facility.estimated_wait_minutes / 30.0, 0.3)
            score -= wait_penalty

        if facility.type == FacilityType.LIBRARY and facility.available_seats:
            if facility.total_capacity:
                availability_ratio = facility.available_seats / facility.total_capacity
                score += availability_ratio * 0.2

        if facility.confidence_score:
            score += facility.confidence_score * 0.1

        return max(0.0, min(1.0, score))

    def _generate_reason(self, facility: Facility) -> str:
        """Generate human-readable reason for recommendation."""
        reasons = []

        if facility.current_crowd_level == CrowdLevel.LOW:
            reasons.append("Low crowd")
        elif facility.current_crowd_level == CrowdLevel.MODERATE:
            reasons.append("Moderate crowd")
        else:
            reasons.append("Busy")

        if facility.estimated_wait_minutes:
            reasons.append(f"~{facility.estimated_wait_minutes}m wait")

        if facility.available_seats and facility.type != FacilityType.STATIONERY:
            reasons.append(f"{facility.available_seats} seats free")

        return " • ".join(reasons) if reasons else "Available"

    async def _generate_explanation(
        self,
        query: str,
        options: List[RecommendationOption]
    ) -> str:
        """Generate structured 4-5 line clean professional explanation with arrows."""
        if not options:
            return "No facilities available matching your query."

        if not settings.GROQ_API_KEY:
            best = options[0]
            return f"Recommended Facility:\n-> {best.facility_name}\n-> Status: {best.crowd_level.value.upper()} crowd ({best.reason})\n-> Optimal choice for your query."

        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            context = self._build_context(options)

            prompt = f"""Student query: "{query}"

Live facilities available:
{context}

Provide a crisp, professional, and directly informative response in exactly 4 to 5 lines using arrows (->). No emojis. Format strictly as:
Recommended Facility: [Facility Name]
-> Location & Status: [Location details] | [Crowd/Wait/Seats]
-> Key Advantage: [Short specific reason]
-> Recommendation: Optimal choice for your request."""

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional campus assistant. Provide clean, structured 4-5 line responses using arrows. Absolutely no emojis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=120
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"LLM generation failed: {e}")
            best = options[0]
            return f"Recommended Facility:\n-> {best.facility_name}\n-> Status: {best.crowd_level.value.upper()} crowd ({best.reason})\n-> Optimal choice for your query."

    async def _generate_route_explanation(
        self,
        query: str,
        options: List[RecommendationOption]
    ) -> str:
        """Generate structured 4-5 line clean professional route itinerary with numbered steps and arrows."""
        if not options:
            return "No facilities match your route."

        if not settings.GROQ_API_KEY:
            if len(options) == 1:
                return f"Optimized Itinerary:\n1. -> {options[0].facility_name} ({options[0].reason})\n-> Ready for visit."
            return f"Optimized Itinerary:\n1. -> {options[0].facility_name} ({options[0].reason})\n2. -> {options[1].facility_name} ({options[1].reason})\n-> Efficient multi-stop flow."

        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            context = self._build_context(options)

            prompt = f"""Student itinerary goal: "{query}"

Live facilities available:
{context}

Provide a crisp, professional route itinerary in exactly 4 to 5 lines using numbers (1., 2.) and arrows (->). No emojis. Format strictly as:
Optimized Itinerary Plan:
1. -> [First Facility] ([Reason])
2. -> [Second Facility] ([Reason])
-> Flow: Sequenced for minimum wait time."""

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional campus routing assistant. Provide clean 4-5 line itineraries using numbers and arrows. Absolutely no emojis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=120
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Route LLM generation failed: {e}")
            if len(options) == 1:
                return f"Optimized Itinerary:\n1. -> {options[0].facility_name} ({options[0].reason})\n-> Ready for visit."
            return f"Optimized Itinerary:\n1. -> {options[0].facility_name} ({options[0].reason})\n2. -> {options[1].facility_name} ({options[1].reason})\n-> Efficient multi-stop flow."

    def _build_context(self, options: List[RecommendationOption]) -> str:
        """Build context string from recommendation options."""
        lines = []
        for opt in options:
            lines.append(
                f"- {opt.facility_name}: {opt.crowd_level.value} crowd, {opt.estimated_wait_minutes or '0'}m wait, {opt.available_seats or 'N/A'} seats"
            )
        return "\n".join(lines)

    def _fallback_explanation(self, options: List[RecommendationOption]) -> str:
        """Generate short deterministic explanation."""
        if not options:
            return "No facilities available."
        best = options[0]
        return f"Recommended:\n-> {best.facility_name}\n{best.crowd_level.value.upper()} crowd ({best.reason})\nBest current option."
