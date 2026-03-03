-- Test script for agent_messages table
-- Run this after applying the migration to verify everything works

-- Test 1: Insert a test thesis message
INSERT INTO agent_messages (
    agent_id,
    theme,
    message_type,
    market_question,
    market_id,
    current_odds,
    thesis_odds,
    edge,
    conviction,
    capital_allocated,
    reasoning,
    signals,
    status,
    tags
) VALUES (
    'twosigma_geo',
    'geopolitical',
    'thesis',
    'Will Netanyahu be Israeli PM on April 1, 2026?',
    'poly_market_123',
    0.78,
    0.85,
    0.042,
    0.71,
    147.00,
    'Coalition stable despite protests. No confidence vote unlikely before Passover. Opposition fragmented.',
    '{"news": [{"source": "reuters", "title": "Coalition stable"}], "twitter": {"mentions": 45}}'::jsonb,
    'thesis_generated',
    ARRAY['high_conviction', 'middle_east']
);

-- Test 2: Insert a conflict message
INSERT INTO agent_messages (
    agent_id,
    theme,
    message_type,
    market_question,
    market_id,
    reasoning,
    status,
    tags
) VALUES (
    'system',
    'crypto',
    'conflict',
    'Bitcoin above $70k by March 31?',
    'poly_market_456',
    'Renaissance (35% YES) vs MorganStanley (68% YES) - disagreement on Fed policy impact',
    'detected',
    ARRAY['conflict', 'requires_review']
);

-- Test 3: Insert a consensus message
INSERT INTO agent_messages (
    agent_id,
    theme,
    message_type,
    market_question,
    market_id,
    thesis_odds,
    edge,
    capital_allocated,
    reasoning,
    status,
    tags
) VALUES (
    'system',
    'us_politics',
    'consensus',
    'Trump announces VP pick by March 15?',
    'poly_market_789',
    0.25,
    0.17,
    2100.00,
    'All 3 politics agents agree: 25% YES (market at 42%). High conviction multi-agent play.',
    'detected',
    ARRAY['consensus', 'high_conviction', 'multi_agent']
);

-- Test 4: Insert an alert
INSERT INTO agent_messages (
    agent_id,
    theme,
    message_type,
    reasoning,
    status,
    tags
) VALUES (
    'risk_engine',
    'crypto',
    'alert',
    'Total crypto exposure: $4,200 (84% of crypto theme capital). Recommend pausing new positions.',
    'active',
    ARRAY['risk_warning', 'concentration']
);

-- Test 5: Insert an analyzing message
INSERT INTO agent_messages (
    agent_id,
    theme,
    message_type,
    market_question,
    market_id,
    current_odds,
    status
) VALUES (
    'goldman_geo',
    'geopolitical',
    'analyzing',
    'Will Israel and Hamas reach ceasefire by April?',
    'poly_market_999',
    0.34,
    'analyzing'
);

-- Verify inserts
SELECT 
    agent_id,
    theme,
    message_type,
    market_question,
    status,
    timestamp
FROM agent_messages
ORDER BY timestamp DESC;

-- Test indexes are working (should be fast)
EXPLAIN ANALYZE
SELECT * FROM agent_messages 
WHERE theme = 'geopolitical' 
ORDER BY timestamp DESC 
LIMIT 10;

-- Count messages by type
SELECT 
    message_type,
    COUNT(*) as count
FROM agent_messages
GROUP BY message_type
ORDER BY count DESC;

-- Count messages by theme
SELECT 
    theme,
    COUNT(*) as count
FROM agent_messages
GROUP BY theme
ORDER BY count DESC;

-- Clean up test data (optional - comment out if you want to keep test messages)
-- DELETE FROM agent_messages WHERE agent_id IN ('twosigma_geo', 'goldman_geo', 'risk_engine', 'system');
