#!/usr/bin/env python
from parsers.txt_parser import TxtParser
from pathlib import Path

try:
    parser = TxtParser(Path('sample_resume.txt'))
    data = parser.parse()
    
    print('=== EXPERIENCES ===')
    print(f'Number of experiences: {len(data.experiences)}')
    for i, exp in enumerate(data.experiences):
        print(f'Experience {i+1}:')
        print(f'  Role: [{exp.role}]')
        print(f'  Company: [{exp.company}]')
        print(f'  Duration: [{exp.duration}]')
        print()
        
    print('=== RAW TEXT ===')
    print(data.raw_text[:1000])
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
