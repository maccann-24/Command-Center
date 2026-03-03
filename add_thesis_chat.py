#!/usr/bin/env python3
"""
Add chat announcements after thesis postings
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
    
    # Find thesis posting and add chat message after it
    # Pattern: self.post_message('thesis', ...) followed by return thesis
    # We want to insert a chat message between them
    
    # Find all thesis post_message calls and add chat after each
    pattern = r"(self\.post_message\('thesis',[^)]+\))\s+(return thesis)"
    
    replacement = r"""\1
        
        # Chat announcement
        side_emoji = "🟢" if edge > 0 else "🔴"
        self.post_message('chat', content=f"{side_emoji} Thesis posted: {market.question[:60]}... | Edge: {edge:+.1%} | Conviction: {conviction:.1%}")
        
        \2"""
    
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Added thesis chat to {agent_file}")

print("\n✅ All agents now announce theses in chat")
