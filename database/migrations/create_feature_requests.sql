-- Feature Requests Table
-- Tracks feature requests from agents

CREATE TABLE IF NOT EXISTS feature_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    feature_description TEXT NOT NULL,
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    notes TEXT
);

-- Index for querying by agent
CREATE INDEX IF NOT EXISTS idx_feature_requests_agent_id ON feature_requests(agent_id);

-- Index for querying by status
CREATE INDEX IF NOT EXISTS idx_feature_requests_status ON feature_requests(status);

-- Index for querying by priority
CREATE INDEX IF NOT EXISTS idx_feature_requests_priority ON feature_requests(priority);

-- Index for recent requests
CREATE INDEX IF NOT EXISTS idx_feature_requests_created_at ON feature_requests(created_at DESC);

-- View for top feature requests (grouped by similar descriptions)
CREATE OR REPLACE VIEW feature_requests_summary AS
SELECT 
    feature_description,
    COUNT(*) as request_count,
    array_agg(DISTINCT agent_id) as requesting_agents,
    MIN(created_at) as first_requested,
    MAX(created_at) as last_requested,
    MAX(priority) as max_priority,
    MIN(status) as status
FROM feature_requests
WHERE status = 'pending'
GROUP BY feature_description
ORDER BY request_count DESC, max_priority DESC, first_requested ASC;

-- View for agent feature requests summary
CREATE OR REPLACE VIEW agent_feature_summary AS
SELECT 
    agent_id,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE status = 'pending') as pending_requests,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_requests,
    array_agg(DISTINCT feature_description) FILTER (WHERE status = 'pending') as pending_features
FROM feature_requests
GROUP BY agent_id
ORDER BY pending_requests DESC;
