#!/usr/bin/env python
from parsers.txt_parser import TxtParser
from analyzers.experience_analyzer import ExperienceAnalyzer
from pathlib import Path

parser = TxtParser(Path('sample_resume.txt'))
data = parser.parse()

print('=== RAW DURATIONS ===')
for exp in data.experiences:
    print(f'Duration: [{exp.duration}]')

analyzer = ExperienceAnalyzer()
profile = analyzer.analyze_experience(data)

print('\n=== EXPERIENCE PROFILE ===')
print(f'Total years: {profile.total_years}')
print(f'Career level: {profile.career_level}')
print(f'Domain expertise: {profile.domain_expertise}')
print(f'Role specialization: {profile.role_specialization}')

print('\n=== EXPERIENCES IN DATA ===')
print(f'Number of experiences: {len(data.experiences)}')
