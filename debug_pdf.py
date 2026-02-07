#!/usr/bin/env python
from parsers.pdf_parser import PDFParser
from analyzers.experience_analyzer import ExperienceAnalyzer
from pathlib import Path

# Check if PDF exists
pdf_path = Path('uploads/resume.pdf')
print(f'PDF exists: {pdf_path.exists()}')

if pdf_path.exists():
    parser = PDFParser(pdf_path)
    data = parser.parse()
    
    print('\n=== RAW DURATIONS ===')
    print(f'Number of experiences: {len(data.experiences)}')
    for exp in data.experiences:
        print(f'Role: [{exp.role}]')
        print(f'Company: [{exp.company}]')
        print(f'Duration: [{exp.duration}]')
        print()
    
    analyzer = ExperienceAnalyzer()
    profile = analyzer.analyze_experience(data)
    
    print('\n=== EXPERIENCE PROFILE ===')
    print(f'Total years: {profile.total_years}')
    print(f'Career level: {profile.career_level}')
else:
    print('PDF file not found')
    # List available files
    print('\nAvailable files in uploads:')
    for f in Path('uploads').iterdir():
        print(f'  {f.name}')
