'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card } from '@/components/ui/card';

interface FilterBarProps {
  themeFilter: string;
  agentFilter: string;
  typeFilter: string;
  timeRangeFilter: string;
  agents: string[];
  onThemeChange: (value: string) => void;
  onAgentChange: (value: string) => void;
  onTypeChange: (value: string) => void;
  onTimeRangeChange: (value: string) => void;
}

const themeOptions = [
  { value: 'all', label: 'All Themes' },
  { value: 'geopolitics', label: 'Geopolitical' },
  { value: 'us-politics', label: 'US Politics' },
  { value: 'crypto', label: 'Crypto' },
  { value: 'weather', label: 'Weather' },
  { value: 'markets', label: 'Markets' },
  { value: 'tech', label: 'Tech' },
  { value: 'energy', label: 'Energy' },
];

const messageTypeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'thesis', label: 'Thesis' },
  { value: 'conflict', label: 'Conflict' },
  { value: 'consensus', label: 'Consensus' },
  { value: 'alert', label: 'Alert' },
  { value: 'analyzing', label: 'Analyzing' },
  { value: 'chat', label: 'Chat' },
];

const timeRangeOptions = [
  { value: 'all', label: 'All time' },
  { value: '1h', label: 'Last hour' },
  { value: '24h', label: 'Last 24h' },
  { value: '7d', label: 'Last 7 days' },
];

export function FilterBar({
  themeFilter,
  agentFilter,
  typeFilter,
  timeRangeFilter,
  agents,
  onThemeChange,
  onAgentChange,
  onTypeChange,
  onTimeRangeChange,
}: FilterBarProps) {
  return (
    <Card className="p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Theme Filter */}
        <div>
          <label className="text-sm font-medium mb-2 block">Theme</label>
          <Select value={themeFilter} onValueChange={onThemeChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select theme" />
            </SelectTrigger>
            <SelectContent>
              {themeOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Agent Filter */}
        <div>
          <label className="text-sm font-medium mb-2 block">Agent</label>
          <Select value={agentFilter} onValueChange={onAgentChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select agent" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Agents</SelectItem>
              {agents.map((agent) => (
                <SelectItem key={agent} value={agent}>
                  {agent}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Message Type Filter */}
        <div>
          <label className="text-sm font-medium mb-2 block">Message Type</label>
          <Select value={typeFilter} onValueChange={onTypeChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              {messageTypeOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Time Range Filter */}
        <div>
          <label className="text-sm font-medium mb-2 block">Time Range</label>
          <Select value={timeRangeFilter} onValueChange={onTimeRangeChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select time range" />
            </SelectTrigger>
            <SelectContent>
              {timeRangeOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </Card>
  );
}
