#!/usr/bin/env python3
"""
Add opening chat messages when agents start analyzing markets
"""

import re

agents = [
    'goldman_geo.py', 'bridgewater_geo.py', 'twosigma_geo.py',
    'goldman_politics.py', 'jpmorgan_politics.py', 'renaissance_politics.py',
    'morganstanley_crypto.py', 'renaissance_crypto.py', 'citadel_crypto.py',
    'renaissance_weather.py', 'morganstanley_weather.py', 'bridgewater_weather.py'
]

for agent_file in agents:
    filepath = f'agents/{agent_file}'
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the line after "if not markets:" block where we print market count
    # Pattern: print(f"📊 Analyzing {len(markets)} ... markets")
    # Add chat message right after it
    
    pattern = r"(print\(f\"📊 Analyzing \{len\(markets\)\}[^\"]+\"\))"
    
    replacement = r"""\1
            
            # Post chat message about starting analysis
            if len(markets) > 0:
                self.post_message('chat', content=f"👋 Starting analysis on {len(markets)} markets...")"""
    
    content = re.sub(pattern, replacement, content)
    
    # Also add chat when no markets found
    pattern_no_markets = r"(if not markets:\s+print\(\"⚠️ No markets found\"\))"
    
    replacement_no_markets = r"""\1
                self.post_message('chat', content="Nothing to analyze today 🤷")"""
    
    content = re.sub(pattern_no_markets, replacement_no_markets, content, flags=re.MULTILINE)
    
    # Add completion message
    pattern_complete = r"(self\._theses_cache = theses\s+print\(f\"[^\"]+Generated \{len\(theses\)\}[^\"]+\"\))"
    
    replacement_complete = r"""\1
            
            # Post completion chat
            if len(theses) > 0:
                self.post_message('chat', content=f"✅ Done! Generated {len(theses)} theses")
            else:
                self.post_message('chat', content="Analysis complete - no opportunities met threshold today")"""
    
    content = re.sub(pattern_complete, replacement_complete, content, flags=re.MULTILINE)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Added opening/closing chat to {agent_file}")

print("\n✅ All agents now post opening/closing messages")
