#!/usr/bin/env python
from parsers.pdf_parser import PDFParser
from pathlib import Path

pdf_path = Path('uploads/resume.pdf')
print(f'PDF exists: {pdf_path.exists()}')

if pdf_path.exists():
    parser = PDFParser(pdf_path)
    
    # Extract raw text
    raw_text = parser._extract_text()
    
    print('\n=== RAW TEXT (first 2000 chars) ===')
    print(raw_text[:2000])
    print('\n...')
    print(f'\nTotal text length: {len(raw_text)}')
    
    # Try extracting experience section
    exp_section = parser._extract_section(raw_text, 'experience')
    print('\n=== EXPERIENCE SECTION ===')
    print(f'Found: {bool(exp_section)}')
    if exp_section:
        print(exp_section[:500])
