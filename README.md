# 🤖 Resume Intelligence Engine

Advanced AI-powered resume analysis engine designed to parse, analyze, and provide insights for professional resumes across all industries.

![Resume Intelligence Engine](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### 📄 Resume Parsing
- **Multi-format Support**: Parse PDF, DOCX, and TXT resume files
- **Smart Extraction**: Automatically extract:
  - Contact information
  - Professional summary
  - Skills (technical & soft)
  - Work experience
  - Education
  - Certifications
  - Projects

### 🎯 Skill Intelligence
- **Skill Normalization**: Converts variations like "JS" → "JavaScript"
- **Categorization**: Organize skills into:
  - Programming Languages
  - Frameworks & Libraries
  - Tools & Platforms
  - Soft Skills
  - Data Science
  - DevOps/Cloud
- **Primary/Secondary/Emerging** skill identification

### 💼 Experience Analysis
- Calculate total years of experience
- Determine career level (Fresher → Architect)
- Identify domain expertise
- Assess project complexity
- Analyze career progression

### 🎯 Job Role Recommendations
- **Top 5-10 Job Matches** based on:
  - Skill relevance
  - Experience match
  - Industry demand
- For each role provides:
  - Match percentage
  - Required vs. candidate skills
  - Skill gap analysis
  - Growth potential

### 📊 Quality Scoring
- **Overall Resume Score (0-100)**
- **Grade (A+ to D)**
- Scoring dimensions:
  - Skill relevance
  - Experience clarity
  - ATS keyword optimization
  - Structure & readability
  - Completeness
- Actionable improvement tips

### 💡 Smart Insights
- Skill gap analysis
- Learning recommendations
- Certification suggestions
- Project ideas
- Career roadmap

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/resume-intelligence-engine.git
cd resume-intelligence-engine

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from api.resume_api import ResumeIntelligenceAPI

# Initialize the engine
api = ResumeIntelligenceAPI()

# Analyze a resume
result = api.analyze_resume("path/to/resume.pdf")

# Access results
print(f"Score: {result['resume_score']['overall_score']}/100")
print(f"Grade: {result['resume_score']['grade']}")
print(f"Career Level: {result['experience_profile']['career_level']}")

# Get job recommendations
for job in result['job_recommendations'][:3]:
    print(f"{job['title']} - {job['skill_match_percentage']:.0f}% match")
```

### CLI Usage

```bash
# Quick analysis
python -m cli.resume_cli resume.pdf --quick

# Compare with job description
python -m cli.resume_cli resume.pdf --job job_description.txt

# Get skill gap for specific role
python -m cli.resume_cli resume.pdf --skill-gap "data_scientist"

# Generate career roadmap
python -m cli.resume_cli resume.pdf --roadmap "machine_learning_engineer"

# Export detailed report
python -m cli.resume_cli resume.pdf --export report.json
```

## 📁 Project Structure

```
resume_intelligence/
├── config/
│   └── config.py           # Configuration & skill databases
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py      # Base parser classes
│   ├── pdf_parser.py       # PDF parsing
│   ├── docx_parser.py      # DOCX parsing
│   └── txt_parser.py       # TXT parsing
├── analyzers/
│   ├── __init__.py
│   ├── skill_analyzer.py   # Skill analysis & categorization
│   ├── experience_analyzer.py  # Experience profiling
│   └── job_recommender.py # Job recommendations
├── scorer/
│   ├── __init__.py
│   └── quality_scorer.py   # Resume quality scoring
├── api/
│   ├── __init__.py
│   └── resume_api.py       # Main API interface
├── cli/
│   ├── __init__.py
│   └── resume_cli.py       # CLI interface
├── utils/
│   ├── __init__.py
│   └── skill_normalizer.py # Skill normalization
├── data/
│   └── skills_database.json
├── sample_resume.txt       # Sample resume
├── test_resume_engine.py   # Test suite
├── main.py                # Main entry point
├── requirements.txt        # Dependencies
└── README.md             # Documentation
```

## 📊 Output Example

### Resume Analysis Result

```json
{
  "basic_info": {
    "name": "John Smith",
    "email": "john.smith@email.com"
  },
  "resume_score": {
    "overall_score": 78.5,
    "grade": "B+",
    "breakdown": {
      "skill_relevance": 85.0,
      "experience_clarity": 75.0,
      "keyword_optimization": 72.0,
      "structure_readability": 80.0,
      "completeness": 80.0
    }
  },
  "experience_profile": {
    "career_level": "mid-level",
    "total_years_experience": 5.0,
    "domain_expertise": ["technology"]
  },
  "job_recommendations": [
    {
      "title": "Software Engineer",
      "match_score": 0.85,
      "skill_match_percentage": 85.0
    },
    {
      "title": "Full Stack Developer",
      "match_score": 0.80,
      "skill_match_percentage": 80.0
    }
  ],
  "suggestions": {
    "skill_improvements": {...},
    "skill_gap_analysis": {...}
  }
}
```

## 🔧 Configuration

### Custom Skills Database

Edit `config/config.py` to customize:

```python
SKILL_CATEGORIES = {
    "programming_languages": [...],
    "frameworks_libraries": [...],
    "tools_platforms": [...],
    "soft_skills": [...],
    "data_science": [...],
    "devops_cloud": [...]
}

JOB_ROLES = {
    "software_engineer": {...},
    "data_scientist": {...},
    ...
}
```

### Adding New Job Roles

```python
JOB_ROLES = {
    "new_role": {
        "title": "New Role Title",
        "required_skills": ["Skill1", "Skill2", "Skill3"],
        "experience_level": "mid",  # fresher, junior, mid, senior, lead, architect
        "keywords": ["keyword1", "keyword2"]
    }
}
```

## 🧪 Testing

```bash
# Run test suite
python test_resume_engine.py

# Test with sample resume
python main.py sample_resume.txt
```

## 📝 API Reference

### ResumeIntelligenceAPI

| Method | Description |
|--------|-------------|
| `analyze_resume(file_path, job_description=None)` | Full resume analysis |
| `analyze_resume_text(text, file_type="txt")` | Analyze text directly |
| `get_quick_analysis(file_path)` | Quick summary analysis |
| `compare_with_job(file_path, job_description)` | Compare against job |
| `get_skill_gap_for_role(file_path, role)` | Skill gap for role |
| `get_career_roadmap(file_path, target_role)` | Career roadmap |
| `export_report(file_path, output_path, format)` | Export analysis |

## 🎯 Use Cases

1. **Job Seekers**: Optimize resume for job applications
2. **Recruiters**: Quickly assess candidate qualifications
3. **Career Coaches**: Provide data-driven career advice
4. **HR Teams**: Automated resume screening
5. **Job Boards**: Enhance job-candidate matching

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Custom job description analysis
- [ ] Interview preparation tips
- [ ] Salary benchmarking
- [ ] Resume template suggestions
- [ ] Integration with job boards

## 📄 License

MIT License - feel free to use in your projects!

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

---

Built with ❤️ for the resume intelligence community
