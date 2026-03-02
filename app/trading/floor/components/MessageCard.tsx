'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AgentMessage } from '@/lib/supabase/queries';
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

  // Extract structured data from metadata
  const metadata = message.metadata || {};
  const marketQuestion = metadata.market_question as string | undefined;
  const reasoning = metadata.reasoning as string | undefined;
  const convictionValue = typeof metadata.conviction === 'number' 
    ? metadata.conviction 
    : typeof metadata.conviction === 'string'
    ? parseFloat(metadata.conviction)
    : undefined;
  const status = metadata.status as string | undefined;
  
  // Thesis-specific data
  const thesisData = message.message_type === 'thesis' ? {
    current: metadata.current as string | number | undefined,
    thesis: metadata.thesis as string | number | undefined,
    edge: metadata.edge as string | number | undefined,
    capital: metadata.capital as string | number | undefined,
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
              <Badge variant="outline" className="text-xs">
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
          <Badge variant="secondary" className="text-xs">
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

      {/* Theme Badge */}
      {message.theme && (
        <div className="mt-3 pt-3 border-t">
          <Badge variant="secondary" className="text-xs">
            {message.theme}
          </Badge>
        </div>
      )}
    </Card>
  );
}
