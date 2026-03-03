"""
BASED MONEY - Reallocation Rules Configuration
Defines capital allocation rules for theme-based portfolio
"""

# ============================================================
# WEEKLY AGENT REALLOCATION RULES
# Based on last 7 days of performance
# ============================================================

WEEKLY_AGENT_RULES = {
    "top_performer": {
        "criteria": {"win_rate": 0.60, "profit_pct": 5.0},
        "allocation_pct": 40.0,  # % of theme capital
        "description": "Win rate ≥60% AND profit ≥5%"
    },
    "good_performer": {
        "criteria": {"win_rate": 0.50, "profit_pct": 5.0},
        "allocation_pct": 35.0,
        "description": "Win rate ≥50% AND profit ≥5%"
    },
    "underperformer": {
        "criteria": {"win_rate": 0.0, "profit_pct": -100.0},  # Catch-all
        "allocation_pct": 25.0,
        "description": "Win rate <50% OR profit <5%"
    },
}

# ============================================================
# WEEKLY THEME REALLOCATION RULES
# Applied to entire theme based on aggregate performance
# ============================================================

WEEKLY_THEME_RULES = {
    "winner": {
        "criteria": {"profit_pct": 5.0, "win_rate": 0.55},
        "capital_adjustment": 1.10,  # Increase by 10%
        "description": "Profit ≥5% AND win rate ≥55%"
    },
    "underperformer": {
        "criteria": {"profit_pct": 0.0},  # Any loss
        "capital_adjustment": 0.95,  # Decrease by 5%
        "description": "Negative profit for the week"
    },
}

# ============================================================
# PROBATION RULES
# Triggered by consecutive poor performance
# ============================================================

PROBATION_RULES = {
    "theme_probation": {
        "trigger": {"consecutive_losing_weeks": 2},
        "action": {"capital_adjustment": 0.80},  # Reduce by 20%
        "description": "2 consecutive losing weeks"
    },
    "agent_probation": {
        "trigger": {"win_rate": 0.40, "period_weeks": 2},
        "action": {"allocation_pct": 10.0},  # Minimum allocation
        "description": "Win rate <40% for 2 weeks"
    },
}

# ============================================================
# MONTHLY THEME ROTATION RULES
# Applied on 1st of each month based on 30-day performance
# ============================================================

MONTHLY_ROTATION_RULES = {
    "pause_theme": {
        "trigger": {"consecutive_losing_months": 2},
        "action": {"status": "PAUSED", "reallocate": True},
        "description": "Theme loses 2+ consecutive months"
    },
    "boost_winner": {
        "trigger": {"rank": 1},  # Top performing theme
        "action": {"steal_from_bottom": 10.0},  # Take 10% from worst theme
        "description": "Top theme gets capital from bottom theme"
    },
}

# ============================================================
# MINIMUM ALLOCATIONS
# Safety limits to prevent total capital loss
# ============================================================

MIN_THEME_CAPITAL = 500.0  # $500 minimum per theme
MIN_AGENT_CAPITAL = 100.0  # $100 minimum per agent
MAX_THEME_CAPITAL_PCT = 50.0  # No theme can exceed 50% of total portfolio

# ============================================================
# REALLOCATION FREQUENCY
# ============================================================

WEEKLY_REALLOCATION_DAY = 6  # Sunday (0=Monday, 6=Sunday)
MONTHLY_REALLOCATION_DAY = 1  # 1st of month

# ============================================================
# PERFORMANCE TARGETS
# ============================================================

WEEKLY_PROFIT_TARGET = 5.0  # 5% per week target
MONTHLY_PROFIT_TARGET = 20.0  # 20% per month target (compounded weekly)
MIN_ACCEPTABLE_WIN_RATE = 0.55  # 55% win rate minimum

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_agent_allocation_pct(win_rate: float, profit_pct: float) -> float:
    """
    Determine agent's capital allocation percentage within its theme.
    
    Args:
        win_rate: Agent's win rate (0-1)
        profit_pct: Agent's profit percentage
    
    Returns:
        Allocation percentage of theme capital (0-100)
    """
    if win_rate >= 0.60 and profit_pct >= 5.0:
        return WEEKLY_AGENT_RULES["top_performer"]["allocation_pct"]
    elif win_rate >= 0.50 and profit_pct >= 5.0:
        return WEEKLY_AGENT_RULES["good_performer"]["allocation_pct"]
    else:
        return WEEKLY_AGENT_RULES["underperformer"]["allocation_pct"]


def get_theme_capital_adjustment(profit_pct: float, win_rate: float, 
                                  consecutive_losing_weeks: int) -> float:
    """
    Determine theme's capital adjustment multiplier.
    
    Args:
        profit_pct: Theme's profit percentage this week
        win_rate: Theme's aggregate win rate
        consecutive_losing_weeks: Number of consecutive weeks with losses
    
    Returns:
        Capital adjustment multiplier (e.g., 1.10 = +10%, 0.80 = -20%)
    """
    # Check probation first
    if consecutive_losing_weeks >= PROBATION_RULES["theme_probation"]["trigger"]["consecutive_losing_weeks"]:
        return PROBATION_RULES["theme_probation"]["action"]["capital_adjustment"]
    
    # Check winner criteria
    if profit_pct >= WEEKLY_THEME_RULES["winner"]["criteria"]["profit_pct"] and \
       win_rate >= WEEKLY_THEME_RULES["winner"]["criteria"]["win_rate"]:
        return WEEKLY_THEME_RULES["winner"]["capital_adjustment"]
    
    # Check underperformer
    if profit_pct < WEEKLY_THEME_RULES["underperformer"]["criteria"]["profit_pct"]:
        return WEEKLY_THEME_RULES["underperformer"]["capital_adjustment"]
    
    # No change
    return 1.0


def should_pause_theme(consecutive_losing_months: int) -> bool:
    """
    Check if theme should be paused based on monthly performance.
    
    Args:
        consecutive_losing_months: Number of consecutive months with losses
    
    Returns:
        True if theme should be paused
    """
    return consecutive_losing_months >= MONTHLY_ROTATION_RULES["pause_theme"]["trigger"]["consecutive_losing_months"]
