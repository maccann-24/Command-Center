#!/usr/bin/env python3
"""
Manually add thesis announcement chat messages after thesis postings
"""

agents = [
    'goldman_geo.py', 'bridgewater_geo.py', 'twosigma_geo.py',
    'goldman_politics.py', 'jpmorgan_politics.py', 'renaissance_politics.py',
    'morganstanley_crypto.py', 'renaissance_crypto.py', 'citadel_crypto.py',
    'renaissance_weather.py', 'morganstanley_weather.py', 'bridgewater_weather.py'
]

for agent_file in agents:
    filepath = f'agents/{agent_file}'
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this line contains thesis post_message and next line is "return thesis"
        if "self.post_message('thesis'" in line and i + 2 < len(lines):
            # Check next non-empty line
            next_line_idx = i + 1
            while next_line_idx < len(lines) and lines[next_line_idx].strip() == '':
                new_lines.append(lines[next_line_idx])
                next_line_idx += 1
                i += 1
            
            if next_line_idx < len(lines) and 'return thesis' in lines[next_line_idx]:
                # Insert chat announcement before return
                indent = '        '  # 8 spaces for standard indentation
                new_lines.append(f'{indent}\n')
                new_lines.append(f'{indent}# Announce in chat\n')
                new_lines.append(f'{indent}side_emoji = "🟢" if edge > 0 else "🔴"\n')
                new_lines.append(f'{indent}self.post_message(\'chat\', content=f"{{side_emoji}} Thesis posted: {{market.question[:60]}}... | Edge: {{edge:+.1%}} | Conviction: {{conviction:.1%}}")\n')
        
        i += 1
    
    with open(filepath, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Added thesis announcements to {agent_file}")

print("\n✅ All agents now announce theses in chat")
