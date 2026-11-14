from pathlib import Path
p=Path('territory-data/raw/lagos-ledu-2025.txt')
for i,t in enumerate(p.read_text().split('\f')):
 if '2.7 Slow recovery' in t or 'economy is projected to expand from' in t:print(i+1,t[:150])
