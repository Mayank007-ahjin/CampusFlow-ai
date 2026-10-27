from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import logging
import re

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

logger = logging.getLogger(__name__)

# Keyword map: ordered so _detect_types returns mention-order
TYPE_KEYWORDS = {
    FacilityType.STATIONERY: ["stationery", "print", "shop", "pen", "notebook", "xerox", "photocopy"],
    FacilityType.OFFICE: ["office", "administrative", "admin", "dean", "fees", "registration"],
    FacilityType.LIBRARY: ["library", "book", "study", "read", "quiet", "seat"],
    FacilityType.CANTEEN: ["canteen", "food", "lunch", "eat", "hungry", "snack", "mess", "dinner", "breakfast"],
}

# Conversational patterns the bot handles directly (no DB query needed)
GREETINGS = {"hi", "hello", "hey", "sup", "yo", "good morning", "good afternoon",
             "good evening", "howdy", "greetings", "hii", "hiii", "hola"}

THANKS = {"thanks", "thank you", "thx", "ty", "thankyou", "thank u", "appreciate it"}

FAREWELL = {"bye", "goodbye", "see you", "see ya", "cya", "later", "good night", "gn"}


class RecommendationEngine:
    """Smart campus chatbot that queries the facility database and replies conversationally."""

    def __init__(self, db: Session):
        self.db = db
        self.crowd_estimator = CrowdEstimatorService(db)

    # ------------------------------------------------------------------
    # Main entry: get_recommendations
    # ------------------------------------------------------------------
    async def get_recommendations(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Handle any user message: greetings, questions about facilities,
        crowd status, comparisons — all answered from the live database.
        """
        query_lower = request.query.lower().strip()
        target_types = request.facility_types

        # 1. Conversational shortcuts (no DB needed)
        conv = self._handle_conversational(query_lower)
        if conv:
            return RecommendationResponse(
                query=request.query,
                answer=conv,
                recommendations=[],
                timestamp=datetime.utcnow()
            )

        # 2. Detect facility types from query
        if not target_types:
            target_types = self._detect_types(query_lower)

        # 3. Fetch matching facilities
        facilities = self._get_candidate_facilities(
            facility_types=target_types,
            include_closed=request.include_closed
        )
        # Fallback: if no type-specific results, search all
        if not facilities:
            facilities = self._get_candidate_facilities(include_closed=request.include_closed)

        if not facilities:
            return RecommendationResponse(
                query=request.query,
                answer="No facilities are available right now. Try again later!",
                recommendations=[],
                timestamp=datetime.utcnow()
            )

        # 4. Score and rank
        ranked_options = self._rank_facilities(
            facilities=facilities,
            max_wait_minutes=request.max_wait_minutes
        )

        # Show more results for comparison queries
        is_comparison = any(w in query_lower for w in [
            "all", "compare", "list", "everything", "best places",
            "what's available", "show me", "options", "which"
        ])
        final_options = ranked_options if (target_types or is_comparison) else ranked_options[:1]

        # 5. Build a natural-language answer from DB data
        answer = self._build_smart_answer(query_lower, final_options)

        return RecommendationResponse(
            query=request.query,
            answer=answer,
            recommendations=final_options,
            timestamp=datetime.utcnow()
        )

    # ------------------------------------------------------------------
    # Route planner
    # ------------------------------------------------------------------
    async def plan_multi_facility_route(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """Plan optimal route across multiple facilities."""
        query_lower = request.query.lower()
        wanted_types = request.facility_types or self._detect_types(query_lower)

        facilities = self._get_candidate_facilities(include_closed=request.include_closed)
        ranked_options = self._rank_facilities(
            facilities=facilities,
            max_wait_minutes=request.max_wait_minutes
        )

        if wanted_types:
            # One best stop per requested type, in mention order
            stops = []
            for t in wanted_types:
                t = t if isinstance(t, FacilityType) else FacilityType(t)
                best = next((o for o in ranked_options if o.facility_type == t), None)
                if best:
                    stops.append(best)
            ranked_options = stops or ranked_options[:3]
        else:
            ranked_options = ranked_options[:3]

        answer = self._build_route_answer(query_lower, ranked_options)

        return RecommendationResponse(
            query=request.query,
            answer=answer,
            recommendations=ranked_options,
            timestamp=datetime.utcnow()
        )

    # ------------------------------------------------------------------
    # Proactive alerts
    # ------------------------------------------------------------------
    def get_proactive_alerts(self) -> AlertListResponse:
        """Generate peak-hour alerts and campus bottleneck warnings."""
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

    # ------------------------------------------------------------------
    # Conversational handler (greetings, thanks, help, etc.)
    # ------------------------------------------------------------------
    def _handle_conversational(self, query: str) -> Optional[str]:
        """Return a reply for conversational messages, or None to continue to DB lookup."""
        q = query.strip().rstrip("!?.").strip()

        # Greetings
        if q in GREETINGS or (len(q) <= 12 and any(g in q for g in GREETINGS)):
            return (
                "Hey there! I'm your CampusFlow AI assistant. "
                "I can help you find quiet study spots, check canteen wait times, "
                "locate the print shop, or plan a route across campus.\n\n"
                "Just ask me anything like:\n"
                "-> \"Where should I study right now?\"\n"
                "-> \"How busy is the canteen?\"\n"
                "-> \"I need to print and eat — plan my route\""
            )

        # Thanks
        if q in THANKS or any(t in q for t in THANKS):
            return "You're welcome! Let me know if you need anything else."

        # Farewell
        if q in FAREWELL or any(f in q for f in FAREWELL):
            return "See you later! Feel free to come back anytime you need campus info."

        # Help / what can you do
        if any(w in q for w in ["help", "what can you do", "what do you do", "how to use", "features"]):
            return (
                "Here's what I can help with:\n\n"
                "-> Check live crowd levels at any facility\n"
                "-> Find available library seats right now\n"
                "-> Check canteen or stationery wait times\n"
                "-> Compare multiple facilities side by side\n"
                "-> Plan a multi-stop campus route\n\n"
                "Just type your question naturally!"
            )

        # Identity
        if any(w in q for w in ["who are you", "your name", "what are you"]):
            return (
                "I'm CampusFlow AI — your smart campus assistant. "
                "I track real-time crowd data across libraries, canteens, "
                "the stationery shop, and offices to help you save time on campus."
            )

        return None

    # ------------------------------------------------------------------
    # Smart answer builder (uses DB data, no LLM needed)
    # ------------------------------------------------------------------
    def _build_smart_answer(self, query: str, options: List[RecommendationOption]) -> str:
        """Build a conversational answer grounded in live facility data."""
        if not options:
            return "Nothing available matching your query right now. Try broadening your search!"

        now = datetime.now().strftime("%I:%M %p")

        # Single facility result
        if len(options) == 1:
            o = options[0]
            lines = [f"Based on live campus data (as of {now}):"]
            lines.append(f"-> {o.facility_name} — {o.crowd_level.value.upper()} crowd")
            if o.estimated_wait_minutes:
                lines.append(f"-> Wait time: ~{o.estimated_wait_minutes} min")
            if o.available_seats:
                lines.append(f"-> Available seats: {o.available_seats}")
            lines.append(f"-> {self._get_verdict(o)}")
            return "\n".join(lines)

        # Multiple results — comparison
        best = options[0]
        lines = [f"Here's what I found (as of {now}):"]
        lines.append(f"-> Best pick: {best.facility_name} ({best.reason})")

        for o in options[1:4]:  # Show up to 3 alternatives
            crowd = o.crowd_level.value
            wait = f", ~{o.estimated_wait_minutes}m wait" if o.estimated_wait_minutes else ""
            seats = f", {o.available_seats} seats free" if o.available_seats else ""
            lines.append(f"-> {o.facility_name}: {crowd} crowd{wait}{seats}")

        lines.append(f"\nI'd recommend {best.facility_name} — {self._get_verdict(best)}")
        return "\n".join(lines)

    def _get_verdict(self, option: RecommendationOption) -> str:
        """One-liner verdict for a facility."""
        if option.crowd_level == CrowdLevel.LOW:
            if option.available_seats and option.available_seats > 20:
                return "Great choice — low crowd with plenty of seats!"
            return "Great choice — it's pretty quiet right now."
        elif option.crowd_level == CrowdLevel.MODERATE:
            if option.estimated_wait_minutes and option.estimated_wait_minutes <= 5:
                return "Decent option — moderate crowd but short wait."
            return "Moderately busy, but should be fine."
        else:
            return "It's busy right now — consider going later or checking alternatives."

    # ------------------------------------------------------------------
    # Route answer builder
    # ------------------------------------------------------------------
    def _build_route_answer(self, query: str, options: List[RecommendationOption]) -> str:
        """Build a route itinerary from DB data."""
        if not options:
            return "No facilities match your route."

        lines = ["Here's your optimized campus route:"]
        total_wait = 0

        for i, o in enumerate(options, 1):
            wait = o.estimated_wait_minutes or 0
            total_wait += wait
            crowd = o.crowd_level.value
            wait_str = f", ~{wait}m wait" if wait else ""
            lines.append(f"{i}. -> {o.facility_name} ({crowd} crowd{wait_str})")

        lines.append(f"\n-> Total estimated time: ~{total_wait} min across all stops.")
        if total_wait > 15:
            lines.append("-> Tip: Start with the busiest stop first to avoid peak rush.")
        else:
            lines.append("-> Looks like a smooth run — all stops are manageable!")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Facility type detection (ordered by first mention in query)
    # ------------------------------------------------------------------
    def _detect_types(self, query_lower: str) -> List[FacilityType]:
        """Detect all facility types mentioned in a query, ordered by first mention, with fuzzy/substring matching."""
        hits = []
        for ftype, words in TYPE_KEYWORDS.items():
            positions = []
            for w in words:
                # Exact / plural regex search
                m = re.search(rf"\b{w}s?\b", query_lower)
                if m:
                    positions.append(m.start())
                else:
                    # Fuzzy / substring match for typos (e.g. "statinery", "canten", "libary")
                    # Check if keyword is substring or has <= 2 character difference for words > 4 chars
                    for token in query_lower.split():
                        if len(w) >= 4 and len(token) >= 4:
                            # Simple Levenshtein distance check or prefix/substring containment
                            if w in token or token in w or (abs(len(w) - len(token)) <= 2 and sum(a != b for a, b in zip(w, token)) <= 2):
                                idx = query_lower.find(token)
                                if idx != -1:
                                    positions.append(idx)
                        elif w in token or token in w:
                            idx = query_lower.find(token)
                            if idx != -1:
                                positions.append(idx)
            if positions:
                hits.append((min(positions), ftype))
        return [t for _, t in sorted(hits, key=lambda h: h[0])]

    # ------------------------------------------------------------------
    # Database queries
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------
    def _rank_facilities(
        self,
        facilities: List[Facility],
        max_wait_minutes: Optional[int] = None
    ) -> List[RecommendationOption]:
        """Rank facilities using deterministic scoring."""
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

        return " | ".join(reasons) if reasons else "Available"
