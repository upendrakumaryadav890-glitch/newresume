#!/usr/bin/env python
from api.resume_api import ResumeIntelligenceAPI
api = ResumeIntelligenceAPI()

print("Testing sample_resume.txt...")
result = api.analyze_resume('sample_resume.txt')
print(f'Career Level: {result["experience_profile"]["career_level"]}')
print(f'Experience: {result["experience_profile"]["total_years_experience"]} years')
print(f'Total Skills: {result["skill_profile"]["total_skills_count"]}')
