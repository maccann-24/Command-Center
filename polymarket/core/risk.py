"""
BASED MONEY - Risk Engine
Pre-trade risk checks to prevent capital destruction
"""

from dataclasses import dataclass
from typing import List, Optional

# ============================================================
# RISK PARAMETERS
# ============================================================

RISK_PARAMS = {
    "max_position_pct": 20.0,  # Maximum size for any single position (% of capital)
    "max_deployed_pct": 60.0,  # Maximum total capital deployed (% of total)
    "min_conviction": 0.70,  # Minimum conviction required to trade
    "min_edge": 0.05,  # Minimum edge required (5%)
}


# ============================================================
# RISK DECISION
# ============================================================


@dataclass
class RiskDecision:
    """Result of risk evaluation"""

    approved: bool
    reason: str
    risk_notes: List[str]
    recommended_size: float = 0.0

    def __str__(self) -> str:
        """Human-readable risk decision"""
        if self.approved:
            return f"✅ APPROVED - Size: {self.recommended_size:.1f}%"
        else:
            return f"❌ REJECTED - {self.reason}"


# ============================================================
# RISK ENGINE
# ============================================================


class RiskEngine:
    """
    Pre-trade risk engine for evaluating trading theses.

    Performs 4 critical checks before allowing execution:
    1. Position size within limits
    2. Total deployed capital within limits
    3. Conviction meets minimum threshold
    4. Edge is sufficient (minimum 5%)
    """

    def __init__(self, risk_params: dict = None):
        """
        Initialize risk engine with parameters.

        Args:
            risk_params: Optional custom risk parameters (uses RISK_PARAMS if None)
        """
        self.params = risk_params if risk_params else RISK_PARAMS.copy()

    def evaluate(self, thesis, portfolio) -> RiskDecision:
        """
        Evaluate a thesis against risk constraints.

        Args:
            thesis: Thesis object with proposed_action, conviction, edge
            portfolio: Portfolio object with deployed_pct

        Returns:
            RiskDecision object with approval status and details

        Checks:
            1. Position size < max_position_pct
            2. Total deployed + new position < max_deployed_pct
            3. Conviction >= min_conviction
            4. Edge > min_edge
        """

        # Extract thesis parameters
        proposed_action = thesis.proposed_action
        proposed_size = proposed_action.get("size_pct", 0.0)
        conviction = thesis.conviction
        edge = thesis.edge

        # Extract portfolio state
        current_deployed = portfolio.deployed_pct

        # Initialize risk notes
        risk_notes = []
        failed_checks = []

        # ============================================================
        # CHECK 1: Position Size
        # ============================================================
        max_position = self.params["max_position_pct"]

        if proposed_size < max_position:
            risk_notes.append(
                f"✓ Position size {proposed_size:.1f}% ≤ {max_position:.1f}%"
            )
        else:
            risk_notes.append(
                f"✗ Position size {proposed_size:.1f}% > {max_position:.1f}%"
            )
            failed_checks.append(
                f"Position size {proposed_size:.1f}% exceeds limit {max_position:.1f}%"
            )

        # ============================================================
        # CHECK 2: Total Deployed Capital
        # ============================================================
        max_deployed = self.params["max_deployed_pct"]
        total_after_trade = current_deployed + proposed_size

        if total_after_trade < max_deployed:
            risk_notes.append(
                f"✓ Total deployed {total_after_trade:.1f}% ≤ {max_deployed:.1f}%"
            )
        else:
            risk_notes.append(
                f"✗ Total deployed {total_after_trade:.1f}% > {max_deployed:.1f}%"
            )
            failed_checks.append(
                f"Total deployed {total_after_trade:.1f}% exceeds limit {max_deployed:.1f}%"
            )

        # ============================================================
        # CHECK 3: Conviction Threshold
        # ============================================================
        min_conviction = self.params["min_conviction"]

        if conviction >= min_conviction:
            risk_notes.append(f"✓ Conviction {conviction:.2f} ≥ {min_conviction:.2f}")
        else:
            risk_notes.append(f"✗ Conviction {conviction:.2f} < {min_conviction:.2f}")
            failed_checks.append(
                f"Conviction {conviction:.2f} below minimum {min_conviction:.2f}"
            )

        # ============================================================
        # CHECK 4: Minimum Edge
        # ============================================================
        min_edge = self.params["min_edge"]

        if edge > min_edge:
            risk_notes.append(f"✓ Edge {edge:.2%} > {min_edge:.2%}")
        else:
            risk_notes.append(f"✗ Edge {edge:.2%} ≤ {min_edge:.2%}")
            failed_checks.append(
                f"Edge {edge:.2%} insufficient (minimum {min_edge:.2%})"
            )

        # ============================================================
        # DECISION
        # ============================================================

        if not failed_checks:
            # ALL CHECKS PASSED
            return RiskDecision(
                approved=True,
                reason="All checks passed",
                risk_notes=["All checks passed"],
                recommended_size=proposed_size,
            )
        else:
            # ONE OR MORE CHECKS FAILED
            reason = f"Failed: {'; '.join(failed_checks)}"

            return RiskDecision(
                approved=False,
                reason=reason,
                risk_notes=risk_notes,
                recommended_size=0.0,
            )

    def update_params(self, **kwargs):
        """
        Update risk parameters.

        Args:
            **kwargs: Risk parameter key-value pairs to update

        Example:
            risk_engine.update_params(max_position_pct=15.0, min_conviction=0.80)
        """
        for key, value in kwargs.items():
            if key in self.params:
                self.params[key] = value

    def get_max_position_size(self, portfolio) -> float:
        """
        Calculate maximum position size allowed given current portfolio state.

        Args:
            portfolio: Portfolio object

        Returns:
            Maximum position size as percentage of capital
        """
        # Maximum based on per-position limit
        max_per_position = self.params["max_position_pct"]

        # Maximum based on total deployment limit
        max_deployed = self.params["max_deployed_pct"]
        current_deployed = portfolio.deployed_pct
        max_from_deployment = max_deployed - current_deployed

        # Take the smaller of the two
        return min(max_per_position, max_from_deployment)

    def suggest_position_size(self, thesis, portfolio) -> float:
        """
        Suggest a position size based on conviction and risk constraints.

        Uses Kelly-like sizing: size = conviction * edge * max_allowed

        Args:
            thesis: Thesis object
            portfolio: Portfolio object

        Returns:
            Suggested position size as percentage
        """
        max_allowed = self.get_max_position_size(portfolio)

        # Kelly-inspired sizing
        # size = conviction * edge * max_allowed
        conviction = thesis.conviction
        edge = thesis.edge

        suggested = conviction * edge * max_allowed

        # Clamp to max allowed
        return min(suggested, max_allowed)


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================


def check_risk(thesis, portfolio, risk_params: dict = None) -> RiskDecision:
    """
    Quick risk check for a thesis.

    Args:
        thesis: Thesis object
        portfolio: Portfolio object
        risk_params: Optional custom risk parameters

    Returns:
        RiskDecision object
    """
    engine = RiskEngine(risk_params)
    return engine.evaluate(thesis, portfolio)


def is_trade_safe(thesis, portfolio, risk_params: dict = None) -> bool:
    """
    Quick boolean check if trade is safe.

    Args:
        thesis: Thesis object
        portfolio: Portfolio object
        risk_params: Optional custom risk parameters

    Returns:
        True if trade passes all risk checks, False otherwise
    """
    decision = check_risk(thesis, portfolio, risk_params)
    return decision.approved
