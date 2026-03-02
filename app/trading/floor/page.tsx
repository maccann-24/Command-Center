'use client';

import { useEffect, useState, useRef } from 'react';
import { getAgentMessages, subscribeToAgentMessages } from '@/lib/supabase/trading';
import type { AgentMessage } from '@/lib/supabase/trading';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MessageCard } from './components/MessageCard';
import { FilterBar } from './components/FilterBar';
import { useToast } from '@/components/ui/toast';
import { ArrowUp } from 'lucide-react';

export default function TradingFloorPage() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [themeFilter, setThemeFilter] = useState<string>('all');
  const [agentFilter, setAgentFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [timeRangeFilter, setTimeRangeFilter] = useState<string>('all');
  const [newMessageCount, setNewMessageCount] = useState(0);
  const [isScrolledDown, setIsScrolledDown] = useState(false);
  
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const { showToast } = useToast();

  // Extract unique agents for filter
  const agents = Array.from(new Set(messages.map(m => m.agent_id))).sort();

  // Scroll to top handler
  const scrollToTop = () => {
    messagesContainerRef.current?.scrollIntoView({ behavior: 'smooth' });
    setNewMessageCount(0);
    setIsScrolledDown(false);
  };

  // Track scroll position
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      setIsScrolledDown(scrollTop > 300);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Load initial messages and subscribe
  useEffect(() => {
    let unsubscribe: (() => void) | undefined;

    const loadMessages = async () => {
      try {
        const data = await getAgentMessages({ limit: 50 });
        setMessages(data);
      } catch (error) {
        console.error('Failed to load messages:', error);
        showToast('Failed to load messages', 'error');
      } finally {
        setLoading(false);
      }
    };

    loadMessages();

    // Subscribe to new messages
    unsubscribe = subscribeToAgentMessages((newMessage) => {
      setMessages((prev) => {
        // Prevent duplicates
        if (prev.some(m => m.id === newMessage.id)) {
          return prev;
        }
        return [newMessage, ...prev].slice(0, 100);
      });

      // Show toast for high-priority messages
      if (newMessage.message_type === 'conflict' || newMessage.message_type === 'consensus') {
        const icon = newMessage.message_type === 'conflict' ? '⚠️' : '✅';
        const message = newMessage.content || `New ${newMessage.message_type} from ${newMessage.agent_id}`;
        showToast(
          `${icon} ${newMessage.message_type.toUpperCase()}: ${message.slice(0, 100)}`,
          newMessage.message_type === 'conflict' ? 'error' : 'success'
        );
      }

      // Increment new message count if scrolled down
      if (window.scrollY > 300) {
        setNewMessageCount(prev => prev + 1);
      } else {
        // Auto-scroll to top if already at top
        setTimeout(() => {
          messagesContainerRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    });

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, [showToast]);

  // Filter messages
  const filteredMessages = messages.filter((msg) => {
    // Theme filter
    if (themeFilter !== 'all' && msg.theme !== themeFilter) return false;
    
    // Agent filter
    if (agentFilter !== 'all' && msg.agent_id !== agentFilter) return false;
    
    // Message type filter
    if (typeFilter !== 'all' && msg.message_type !== typeFilter) return false;
    
    // Time range filter
    if (timeRangeFilter !== 'all') {
      const messageTime = new Date(msg.created_at).getTime();
      const now = Date.now();
      const ranges: Record<string, number> = {
        '1h': 60 * 60 * 1000,
        '24h': 24 * 60 * 60 * 1000,
        '7d': 7 * 24 * 60 * 60 * 1000,
      };
      const range = ranges[timeRangeFilter];
      if (range && now - messageTime > range) return false;
    }
    
    return true;
  });

  return (
    <div className="container mx-auto p-6 space-y-6" ref={messagesContainerRef}>
      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-3xl font-bold">Trading Floor</h1>
        <div className="relative flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
          <div className="absolute w-3 h-3 bg-red-500 rounded-full animate-ping" />
        </div>
        <Badge variant="default" className="ml-auto">
          {filteredMessages.length} messages
        </Badge>
      </div>

      {/* New Messages Badge + Scroll to Top */}
      {isScrolledDown && newMessageCount > 0 && (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2">
          <Button
            onClick={scrollToTop}
            size="lg"
            className="shadow-lg"
          >
            <ArrowUp className="w-4 h-4 mr-2" />
            {newMessageCount} new {newMessageCount === 1 ? 'message' : 'messages'}
          </Button>
        </div>
      )}

      {/* Scroll to Top Button (when scrolled but no new messages) */}
      {isScrolledDown && newMessageCount === 0 && (
        <Button
          onClick={scrollToTop}
          size="sm"
          variant="secondary"
          className="fixed bottom-6 right-6 z-50 shadow-lg rounded-full w-10 h-10 p-0"
        >
          <ArrowUp className="w-4 h-4" />
        </Button>
      )}

      {/* Filter Bar */}
      <FilterBar
        themeFilter={themeFilter}
        agentFilter={agentFilter}
        typeFilter={typeFilter}
        timeRangeFilter={timeRangeFilter}
        agents={agents}
        onThemeChange={setThemeFilter}
        onAgentChange={setAgentFilter}
        onTypeChange={setTypeFilter}
        onTimeRangeChange={setTimeRangeFilter}
      />

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
            <MessageCard key={message.id} message={message} />
          ))
        )}
      </div>
    </div>
  );
}
