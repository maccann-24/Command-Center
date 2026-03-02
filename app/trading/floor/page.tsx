'use client';

import { useEffect, useState } from 'react';
import { getAgentMessages, subscribeToAgentMessages } from '@/lib/supabase/queries';
import type { AgentMessage } from '@/lib/supabase/queries';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export default function TradingFloorPage() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [themeFilter, setThemeFilter] = useState<string>('all');
  const [agentFilter, setAgentFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  // Extract unique values for filters
  const themes = ['all', ...Array.from(new Set(messages.map(m => m.theme).filter(Boolean)))];
  const agents = ['all', ...Array.from(new Set(messages.map(m => m.agent_id)))];
  const types = ['all', ...Array.from(new Set(messages.map(m => m.message_type)))];

  useEffect(() => {
    // Load initial messages
    const loadMessages = async () => {
      try {
        const data = await getAgentMessages({ limit: 50 });
        setMessages(data);
      } catch (error) {
        console.error('Failed to load messages:', error);
      } finally {
        setLoading(false);
      }
    };

    loadMessages();

    // Subscribe to new messages
    const unsubscribe = subscribeToAgentMessages((newMessage) => {
      setMessages((prev) => [newMessage, ...prev].slice(0, 50));
    });

    return () => {
      unsubscribe();
    };
  }, []);

  // Filter messages
  const filteredMessages = messages.filter((msg) => {
    if (themeFilter !== 'all' && msg.theme !== themeFilter) return false;
    if (agentFilter !== 'all' && msg.agent_id !== agentFilter) return false;
    if (typeFilter !== 'all' && msg.message_type !== typeFilter) return false;
    return true;
  });

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);

    if (diffSecs < 60) return `${diffSecs}s ago`;
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  const getMessageTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      chat: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
      system: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
      error: 'bg-red-500/10 text-red-500 border-red-500/20',
      tool: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
    };
    return colors[type] || 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-3xl font-bold">Trading Floor</h1>
        <div className="relative flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
          <div className="absolute w-3 h-3 bg-red-500 rounded-full animate-ping" />
        </div>
        <Badge variant="outline" className="ml-auto">
          {filteredMessages.length} messages
        </Badge>
      </div>

      {/* Filter Bar */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Theme</label>
            <Select value={themeFilter} onValueChange={setThemeFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Select theme" />
              </SelectTrigger>
              <SelectContent>
                {themes.map((theme) => (
                  <SelectItem key={theme} value={theme}>
                    {theme === 'all' ? 'All Themes' : theme}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Agent</label>
            <Select value={agentFilter} onValueChange={setAgentFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Select agent" />
              </SelectTrigger>
              <SelectContent>
                {agents.map((agent) => (
                  <SelectItem key={agent} value={agent}>
                    {agent === 'all' ? 'All Agents' : agent}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Message Type</label>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {types.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type === 'all' ? 'All Types' : type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Message Feed */}
      <div className="space-y-3">
        {loading ? (
          <Card className="p-8 text-center text-muted-foreground">
            Loading messages...
          </Card>
        ) : filteredMessages.length === 0 ? (
          <Card className="p-8 text-center text-muted-foreground">
            No messages found
          </Card>
        ) : (
          filteredMessages.map((message) => (
            <Card
              key={message.id}
              className="p-4 hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-start gap-4">
                {/* Timestamp */}
                <div className="text-xs text-muted-foreground min-w-[70px] pt-1">
                  {formatTimestamp(message.created_at)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge
                      variant="outline"
                      className={cn(
                        'text-xs',
                        getMessageTypeColor(message.message_type)
                      )}
                    >
                      {message.message_type}
                    </Badge>
                    <span className="text-sm font-medium">{message.agent_id}</span>
                    {message.theme && (
                      <Badge variant="secondary" className="text-xs">
                        {message.theme}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm break-words whitespace-pre-wrap">
                    {message.content}
                  </p>
                  {message.metadata && Object.keys(message.metadata).length > 0 && (
                    <div className="mt-2 text-xs text-muted-foreground font-mono">
                      {JSON.stringify(message.metadata, null, 2)}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
