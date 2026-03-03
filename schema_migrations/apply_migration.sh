#!/bin/bash

# Script to apply agent_messages migration to Supabase
# Usage: ./apply_migration.sh

echo "================================================"
echo "Applying agent_messages table migration"
echo "================================================"
echo ""

# Check if SUPABASE_URL and SUPABASE_KEY are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "❌ Error: SUPABASE_URL and SUPABASE_KEY must be set"
    echo ""
    echo "Set them in your .env file or export them:"
    echo "  export SUPABASE_URL='https://your-project.supabase.co'"
    echo "  export SUPABASE_KEY='your-service-role-key'"
    exit 1
fi

# Extract project reference from URL
PROJECT_REF=$(echo $SUPABASE_URL | sed 's/https:\/\/\(.*\)\.supabase\.co/\1/')

echo "Project: $PROJECT_REF"
echo "Migration: agent_messages.sql"
echo ""

# Option 1: Using Supabase CLI (if installed)
if command -v supabase &> /dev/null; then
    echo "📦 Applying migration via Supabase CLI..."
    supabase db push --db-url "$SUPABASE_URL/db" --password "$SUPABASE_KEY"
    
# Option 2: Direct SQL execution via psql (if installed)
elif command -v psql &> /dev/null; then
    echo "📦 Applying migration via psql..."
    psql "$SUPABASE_URL/db" -f agent_messages.sql
    
# Option 3: Manual instructions
else
    echo "⚠️  Supabase CLI and psql not found"
    echo ""
    echo "📋 Manual migration steps:"
    echo ""
    echo "1. Go to: https://app.supabase.com/project/$PROJECT_REF/editor"
    echo "2. Click 'SQL Editor' in the left sidebar"
    echo "3. Click 'New Query'"
    echo "4. Copy/paste the contents of agent_messages.sql"
    echo "5. Click 'Run' to execute"
    echo ""
    echo "Or install Supabase CLI:"
    echo "  npm install -g supabase"
    echo ""
fi

echo ""
echo "✅ Migration file ready at: schema_migrations/agent_messages.sql"
