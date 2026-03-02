'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AgentMessage } from '@/lib/supabase/trading';
import { ConvictionBadge } from './ConvictionBadge';

interface MessageCardProps {
  message: AgentMessage;
}

const themeIcons: Record<string, string> = {
  geopolitics: '🌍',
  'us-politics': '🇺🇸',
  crypto: '₿',
  weather: '🌦️',
  markets: '📈',
  tech: '💻',
  energy: '⚡',
};

const messageTypeStyles = {
  thesis: 'border-l-4 border-l-blue-500',
  conflict: 'border-l-4 border-l-orange-500',
  consensus: 'border-l-4 border-l-green-500',
  alert: 'border-l-4 border-l-red-500',
  analyzing: 'border-l-4 border-l-gray-500',
  chat: 'border-l-4 border-l-purple-500',
};

export function MessageCard({ message }: MessageCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const themeIcon = message.theme ? themeIcons[message.theme] || '📊' : '📊';
  const borderStyle = messageTypeStyles[message.message_type as keyof typeof messageTypeStyles] || '';

  // Extract structured data from top-level columns (agent_messages table)
  const metadata = message.metadata || {};
  const marketQuestion = (message as any).market_question || metadata.market_question as string | undefined;
  const reasoning = (message as any).reasoning || metadata.reasoning as string | undefined;
  
  // conviction can be in either top-level or metadata
  const convictionValue = (() => {
    const topLevel = (message as any).conviction;
    const metaLevel = metadata.conviction;
    const val = topLevel !== undefined ? topLevel : metaLevel;
    if (typeof val === 'number') return val;
    if (typeof val === 'string') return parseFloat(val);
    return undefined;
  })();
  
  const status = (message as any).status || metadata.status as string | undefined;
  const signals = (message as any).signals || metadata.signals as any | undefined;
  
  // Thesis-specific data from top-level columns
  const thesisData = message.message_type === 'thesis' ? {
    current: (message as any).current_odds !== undefined ? `${((message as any).current_odds * 100).toFixed(0)}%` : undefined,
    thesis: (message as any).thesis_odds !== undefined ? `${((message as any).thesis_odds * 100).toFixed(0)}%` : undefined,
    edge: (message as any).edge !== undefined ? `${((message as any).edge * 100).toFixed(1)}%` : undefined,
    capital: (message as any).capital_allocated !== undefined ? `$${(message as any).capital_allocated}` : undefined,
  } : null;

  const shouldShowExpandButton = reasoning && reasoning.length > 200;
  const displayReasoning = shouldShowExpandButton && !isExpanded 
    ? `${reasoning.slice(0, 200)}...` 
    : reasoning;

  return (
    <Card className={cn('p-4 hover:bg-accent/30 transition-colors', borderStyle)}>
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">{themeIcon}</span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm">{message.agent_id}</span>
              <Badge variant="default" className="text-xs">
                {message.message_type}
              </Badge>
              {convictionValue !== undefined && !isNaN(convictionValue) && (
                <ConvictionBadge conviction={convictionValue} />
              )}
            </div>
            <div className="text-xs text-muted-foreground mt-0.5">
              {formatTime(message.created_at)}
            </div>
          </div>
        </div>
        
        {status && (
          <Badge variant="info" className="text-xs">
            {status}
          </Badge>
        )}
      </div>

      {/* Market Question */}
      {marketQuestion && (
        <div className="mb-3 p-3 bg-accent/50 rounded-md">
          <p className="text-sm font-medium">{marketQuestion}</p>
        </div>
      )}

      {/* Thesis Grid */}
      {thesisData && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
          <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-md">
            <div className="text-xs text-muted-foreground mb-1">Current</div>
            <div className="text-sm font-semibold">{thesisData.current}</div>
          </div>
          <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-md">
            <div className="text-xs text-muted-foreground mb-1">Thesis</div>
            <div className="text-sm font-semibold">{thesisData.thesis}</div>
          </div>
          <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-md">
            <div className="text-xs text-muted-foreground mb-1">Edge</div>
            <div className="text-sm font-semibold">{thesisData.edge}</div>
          </div>
          <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-md">
            <div className="text-xs text-muted-foreground mb-1">Capital</div>
            <div className="text-sm font-semibold">{thesisData.capital}</div>
          </div>
        </div>
      )}

      {/* Content */}
      {message.content && (
        <div className="mb-3">
          <p className="text-sm whitespace-pre-wrap break-words">
            {message.content}
          </p>
        </div>
      )}

      {/* Reasoning */}
      {reasoning && (
        <div className="space-y-2">
          <div className="text-xs font-medium text-muted-foreground mb-1">
            Reasoning:
          </div>
          <div className="p-3 bg-muted/50 rounded-md">
            <p className="text-sm whitespace-pre-wrap break-words text-muted-foreground">
              {displayReasoning}
            </p>
          </div>
          {shouldShowExpandButton && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="w-4 h-4 mr-1" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4 mr-1" />
                  Show more
                </>
              )}
            </Button>
          )}
        </div>
      )}

      {/* Signals */}
      {signals && (
        <div className="mt-3 space-y-2">
          <div className="text-xs font-medium text-muted-foreground">Signals:</div>
          <div className="p-3 bg-muted/30 rounded-md border">
            {Array.isArray(signals?.matches) ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span className="font-mono">{signals.source_type || 'signals'}</span>
                  <span>
                    {typeof signals.match_count === 'number'
                      ? `${signals.match_count} sources`
                      : `${signals.matches.length} sources`}
                  </span>
                </div>
                <ul className="space-y-1">
                  {signals.matches.slice(0, 6).map((m: any, idx: number) => (
                    <li key={idx} className="text-xs">
                      <span className="text-muted-foreground">[{m?.source || 'source'}]</span>{' '}
                      <span className="text-foreground">{m?.headline || '—'}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <pre className="text-xs text-muted-foreground whitespace-pre-wrap break-words">
                {JSON.stringify(signals, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}

      {/* Theme Badge */}
      {message.theme && (
        <div className="mt-3 pt-3 border-t">
          <Badge variant="default" className="text-xs">
            {message.theme}
          </Badge>
        </div>
      )}
    </Card>
  );
}
