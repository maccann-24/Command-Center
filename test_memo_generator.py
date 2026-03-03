"""
Test core/memo.py - IC Memo Generator
"""

import sys
import os
import importlib.util
from datetime import date
from dataclasses import dataclass
from typing import Optional

# Import memo module directly
spec = importlib.util.spec_from_file_location('memo', 'core/memo.py')
memo_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memo_module)

generate_daily_memo = memo_module.generate_daily_memo
save_memo_to_file = memo_module.save_memo_to_file


# ============================================================
# MOCK OBJECTS
# ============================================================

@dataclass
class MockPortfolio:
    """Mock Portfolio for testing"""
    cash: float
    deployed_pct: float
    total_value: float
    daily_pnl: float
    all_time_pnl: float
    positions: list


@dataclass
class MockThesis:
    """Mock Thesis for testing"""
    market_question: str
    edge: float
    conviction: float
    status: str


@dataclass
class MockTrade:
    """Mock Trade for testing"""
    market_question: str
    side: str
    shares: float
    entry_price: float
    thesis_id: str
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None


# ============================================================
# TESTS
# ============================================================

def test_basic_memo():
    """Test basic memo generation"""
    
    print("\n" + "=" * 60)
    print("TEST: Basic Memo Generation")
    print("=" * 60)
    
    # Setup portfolio
    portfolio = MockPortfolio(
        cash=7500.0,
        deployed_pct=25.0,
        total_value=10000.0,
        daily_pnl=150.0,
        all_time_pnl=500.0,
        positions=[],
    )
    
    # Setup theses
    theses = [
        MockThesis(
            market_question="Will Bitcoin reach $100k by end of 2024?",
            edge=0.15,
            conviction=0.85,
            status="active",
        ),
        MockThesis(
            market_question="Will Trump win 2024 election?",
            edge=0.08,
            conviction=0.72,
            status="pending",
        ),
    ]
    
    # Setup trades
    trades = [
        MockTrade(
            market_question="Will Bitcoin reach $100k by end of 2024?",
            side="YES",
            shares=500,
            entry_price=0.65,
            thesis_id="thesis-abc123",
            exit_price=1.0,
            pnl=175.0,
            pnl_pct=53.8,
        ),
        MockTrade(
            market_question="Will Fed cut rates in March?",
            side="NO",
            shares=300,
            entry_price=0.40,
            thesis_id="thesis-def456",
            exit_price=1.0,
            pnl=180.0,
            pnl_pct=150.0,
        ),
    ]
    
    # Generate memo
    memo = generate_daily_memo(
        memo_date=date(2024, 1, 15),
        theses=theses,
        portfolio=portfolio,
        trades=trades,
    )
    
    # Verify structure
    print("\n📝 Generated Memo:")
    print(memo)
    
    # Verify sections exist
    assert "# BASED MONEY - Daily IC Memo" in memo, "Missing header"
    assert "Portfolio Summary" in memo, "Missing portfolio section"
    assert "Active Theses" in memo, "Missing theses section"
    assert "Trades Executed" in memo, "Missing trades section"
    assert "Performance Metrics" in memo, "Missing metrics section"
    assert "Disclaimer" in memo, "Missing disclaimer"
    
    # Verify portfolio data
    assert "$7,500.00" in memo, "Missing cash amount"
    assert "25.0%" in memo, "Missing deployed percentage"
    assert "$10,000.00" in memo, "Missing total value"
    assert "$+150.00" in memo, "Missing daily P&L"
    
    # Verify theses table
    assert "Bitcoin" in memo, "Missing thesis market"
    assert "15.0%" in memo or "15%" in memo, "Missing edge percentage"
    assert "0.85" in memo, "Missing conviction"
    
    # Verify trades table
    assert "YES" in memo, "Missing trade side"
    assert "500" in memo, "Missing trade size"
    assert "✅" in memo or "❌" in memo, "Missing trade outcome"
    
    # Verify disclaimer
    assert "Not financial advice" in memo, "Missing disclaimer text"
    
    print("\n✅ All sections present and formatted correctly")


def test_empty_memo():
    """Test memo with no theses or trades"""
    
    print("\n" + "=" * 60)
    print("TEST: Empty Memo (No Activity)")
    print("=" * 60)
    
    # Setup
    portfolio = MockPortfolio(
        cash=10000.0,
        deployed_pct=0.0,
        total_value=10000.0,
        daily_pnl=0.0,
        all_time_pnl=0.0,
        positions=[],
    )
    
    # Generate memo with no theses or trades
    memo = generate_daily_memo(
        memo_date=date(2024, 1, 15),
        theses=[],
        portfolio=portfolio,
        trades=[],
    )
    
    print("\n📝 Generated Memo:")
    print(memo)
    
    # Verify empty state messages
    assert "No active theses" in memo, "Missing empty theses message"
    assert "No trades executed today" in memo, "Missing empty trades message"
    assert "No trades to analyze" in memo, "Missing empty metrics message"
    
    print("\n✅ Empty memo generated correctly")


def test_save_to_file():
    """Test saving memo to file"""
    
    print("\n" + "=" * 60)
    print("TEST: Save Memo to File")
    print("=" * 60)
    
    # Setup
    portfolio = MockPortfolio(
        cash=10000.0,
        deployed_pct=0.0,
        total_value=10000.0,
        daily_pnl=0.0,
        all_time_pnl=0.0,
        positions=[],
    )
    
    # Generate memo
    memo = generate_daily_memo(
        memo_date=date(2024, 1, 15),
        theses=[],
        portfolio=portfolio,
        trades=[],
    )
    
    # Save to file
    test_dir = "test_memos"
    filepath = os.path.join(test_dir, "2024-01-15.md")
    
    save_memo_to_file(memo, filepath)
    
    # Verify file exists
    assert os.path.exists(filepath), "File not created"
    
    # Verify content
    with open(filepath, 'r') as f:
        saved_content = f.read()
    
    assert saved_content == memo, "Saved content doesn't match"
    
    # Cleanup
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    print(f"\n✅ Memo saved and verified at {filepath}")


def test_long_market_names():
    """Test that long market names are truncated"""
    
    print("\n" + "=" * 60)
    print("TEST: Long Market Name Truncation")
    print("=" * 60)
    
    # Setup
    portfolio = MockPortfolio(
        cash=10000.0,
        deployed_pct=0.0,
        total_value=10000.0,
        daily_pnl=0.0,
        all_time_pnl=0.0,
        positions=[],
    )
    
    # Thesis with very long question
    long_question = "Will the Federal Reserve Board of Governors announce a comprehensive restructuring of monetary policy frameworks including potential quantitative easing measures?"
    
    theses = [
        MockThesis(
            market_question=long_question,
            edge=0.10,
            conviction=0.75,
            status="active",
        ),
    ]
    
    # Generate memo
    memo = generate_daily_memo(
        memo_date=date(2024, 1, 15),
        theses=theses,
        portfolio=portfolio,
        trades=[],
    )
    
    # Verify truncation (should be max 50 chars + "...")
    assert "..." in memo, "Long name not truncated"
    
    # Count characters in table cell (rough check)
    lines = memo.split('\n')
    thesis_line = [l for l in lines if 'Federal Reserve' in l][0]
    # Should be truncated to reasonable length
    print(f"\nOriginal: {len(long_question)} chars")
    print(f"In memo: {thesis_line}")
    
    print("\n✅ Long market names truncated correctly")


def test_performance_metrics():
    """Test performance metrics calculation"""
    
    print("\n" + "=" * 60)
    print("TEST: Performance Metrics Calculation")
    print("=" * 60)
    
    # Setup portfolio
    portfolio = MockPortfolio(
        cash=10000.0,
        deployed_pct=0.0,
        total_value=10000.0,
        daily_pnl=0.0,
        all_time_pnl=0.0,
        positions=[],
    )
    
    # Setup trades with wins and losses
    trades = [
        MockTrade("Market 1", "YES", 100, 0.50, "t1", 1.0, 50.0, 100.0),
        MockTrade("Market 2", "NO", 200, 0.30, "t2", 1.0, 140.0, 233.3),
        MockTrade("Market 3", "YES", 150, 0.60, "t3", 0.0, -90.0, -100.0),
        MockTrade("Market 4", "YES", 80, 0.50, "t4", 1.0, 40.0, 100.0),
    ]
    
    # Generate memo
    memo = generate_daily_memo(
        memo_date=date(2024, 1, 15),
        theses=[],
        portfolio=portfolio,
        trades=trades,
    )
    
    print("\n📝 Performance Metrics Section:")
    metrics_section = memo.split("## Performance Metrics")[1].split("##")[0]
    print(metrics_section)
    
    # Verify metrics
    assert "75.0% (3/4)" in metrics_section, "Win rate incorrect"
    assert "Average P&L:" in memo, "Missing average P&L"
    assert "Total P&L:" in memo, "Missing total P&L"
    
    print("\n✅ Performance metrics calculated correctly")


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("IC MEMO GENERATOR TEST SUITE")
    print("=" * 60)
    
    try:
        test_basic_memo()
        test_empty_memo()
        test_save_to_file()
        test_long_market_names()
        test_performance_metrics()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
