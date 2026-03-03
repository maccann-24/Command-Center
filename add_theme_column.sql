-- Add theme column to markets table
ALTER TABLE markets ADD COLUMN IF NOT EXISTS theme TEXT;

-- Create index for theme queries
CREATE INDEX IF NOT EXISTS idx_markets_theme ON markets(theme);

-- Update existing markets based on category
UPDATE markets SET theme = 'politics' WHERE category = 'politics';
UPDATE markets SET theme = 'geopolitics' WHERE category = 'geopolitics';
UPDATE markets SET theme = 'crypto' WHERE category = 'crypto';
UPDATE markets SET theme = 'weather' WHERE category = 'weather';
