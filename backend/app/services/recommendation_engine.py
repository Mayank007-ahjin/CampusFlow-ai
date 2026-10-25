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
                answer="No facilities are currently available matching your criteria.",
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

        # Generate natural language explanation
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
        Plan optimal route across multiple facilities based on query.
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

        # Sort or prioritize based on user intent keywords in route query
        if "stationery" in query_lower or "print" in query_lower or "quick" in query_lower:
            ranked_options.sort(key=lambda x: 0 if x.facility_type == FacilityType.STATIONERY else (1 if x.facility_type == FacilityType.LIBRARY else 2))
        elif "food" in query_lower or "lunch" in query_lower or "canteen" in query_lower:
            ranked_options.sort(key=lambda x: 0 if x.facility_type == FacilityType.CANTEEN else (1 if x.facility_type == FacilityType.LIBRARY else 2))
        elif "study" in query_lower or "library" in query_lower or "group" in query_lower:
            ranked_options.sort(key=lambda x: 0 if x.facility_type == FacilityType.LIBRARY else (1 if x.facility_type == FacilityType.STATIONERY else 2))

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
                wait_str = f" Expected wait is ~{facility.estimated_wait_minutes} mins." if facility.estimated_wait_minutes else ""
                alerts.append(AlertResponse(
                    id=facility.id,
                    facility_name=facility.name,
                    alert_type="peak_rush",
                    severity="high",
                    message=f"Notice: {facility.name} is currently experiencing peak traffic.{wait_str} Consider visiting alternative locations.",
                    timestamp=datetime.utcnow()
                ))
            elif facility.type == FacilityType.LIBRARY and facility.available_seats and facility.available_seats > 30:
                alerts.append(AlertResponse(
                    id=facility.id,
                    facility_name=facility.name,
                    alert_type="optimal_study",
                    severity="info",
                    message=f"Notice: {facility.name} has strong availability ({facility.available_seats} open seats). Recommended for study sessions.",
                    timestamp=datetime.utcnow()
                ))

        if not alerts:
            alerts.append(AlertResponse(
                id=0,
                facility_name="Campus Network",
                alert_type="status_normal",
                severity="low",
                message="All campus facilities are currently operating normally with stable crowd levels.",
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
            reasons.append("Currently busy")

        if facility.estimated_wait_minutes:
            if facility.estimated_wait_minutes <= 5:
                reasons.append(f"~{facility.estimated_wait_minutes} min wait")
            else:
                reasons.append(f"{facility.estimated_wait_minutes} min wait")

        if facility.available_seats and facility.type != FacilityType.STATIONERY:
            reasons.append(f"{facility.available_seats} seats available")

        if facility.last_updated:
            age_minutes = (datetime.utcnow() - facility.last_updated).total_seconds() / 60
            if age_minutes < 5:
                reasons.append("just updated")

        return " • ".join(reasons) if reasons else "Limited data available"

    async def _generate_explanation(
        self,
        query: str,
        options: List[RecommendationOption]
    ) -> str:
        """Generate natural language explanation of recommendations."""
        if not settings.GROQ_API_KEY or not options:
            return self._fallback_explanation(options)

        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)

            query_lower = query.lower().strip()
            is_greeting = query_lower in ["hi", "hello", "hey", "sup", "good morning", "good evening", "how are you", "who are you"]

            if is_greeting:
                prompt = f"""The user said: "{query}"
Reply as a friendly campus assistant named CampusFlow AI. Greet them back warmly in 1-2 sentences and let them know you can help them find study spots, check canteen wait times, or locate print shops."""
            else:
                context = self._build_context(options)
                if len(options) == 1:
                    prompt = f"""You are a helpful campus assistant. A student asked: "{query}"

Here is the current status of the requested facility:
{context}

Provide a direct, friendly answer (1-2 sentences) about this facility's status based on the data above. Focus ONLY on this facility and do not bring up other facilities."""
                else:
                    prompt = f"""You are a helpful campus assistant. A student asked: "{query}"

Here are the current facility conditions:
{context}

Provide a brief, friendly recommendation (2-3 sentences) explaining which facility is best and why, based on the data above. Be specific about wait times and crowd levels."""

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful campus assistant providing facility recommendations based on real-time data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._fallback_explanation(options)

    async def _generate_route_explanation(
        self,
        query: str,
        options: List[RecommendationOption]
    ) -> str:
        """Generate explanation for multi-facility route planning."""
        if not options:
            return "No facilities match your requirements."

        if len(options) == 1:
            return f"{options[0].facility_name} is your best option. {options[0].reason}."

        return f"Agent Itinerary: First, visit {options[0].facility_name} ({options[0].reason}), then proceed to {options[1].facility_name} ({options[1].reason}) for optimized campus flow."

    def _build_context(self, options: List[RecommendationOption]) -> str:
        """Build context string from recommendation options."""
        lines = []
        for opt in options:
            lines.append(
                f"- {opt.facility_name}: {opt.crowd_level.value} crowd, "
                f"{opt.estimated_wait_minutes or 'unknown'} min wait, "
                f"{opt.available_seats or 'N/A'} seats"
            )
        return "\n".join(lines)

    def _fallback_explanation(self, options: List[RecommendationOption]) -> str:
        """Generate deterministic explanation without LLM."""
        if not options:
            return "No facilities are currently available."

        best = options[0]
        return (
            f"{best.facility_name} is your best option right now. "
            f"{best.reason}. "
            f"This recommendation is based on recent student reports."
        )
