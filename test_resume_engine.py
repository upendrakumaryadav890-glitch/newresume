"""
Test Suite for Resume Intelligence Engine
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from parsers import ResumeParser
from analyzers import SkillAnalyzer, ExperienceAnalyzer, JobRecommender
from scorer import QualityScorer
from api.resume_api import ResumeIntelligenceAPI


def test_parser():
    """Test resume parsing"""
    print("=" * 50)
    print("Testing Resume Parser")
    print("=" * 50)
    
    sample_resume = Path("sample_resume.txt")
    
    if not sample_resume.exists():
        print("Sample resume not found. Creating test text...")
        resume_text = """
JOHN SMITH
john.smith@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced Software Engineer with Python and JavaScript skills.

EXPERIENCE
Software Engineer - Tech Corp
January 2022 - Present
- Built applications using Python and React
- Deployed on AWS

EDUCATION
BS Computer Science - University
"""
        resume_data = ResumeParser.parse_text(resume_text, "txt")
    else:
        resume_data = ResumeParser.parse(sample_resume)
    
    print(f"✓ Name: {resume_data.full_name}")
    print(f"✓ Email: {resume_data.email}")
    print(f"✓ Skills found: {len(resume_data.technical_skills)}")
    print(f"✓ Experience entries: {len(resume_data.experiences)}")
    print(f"✓ Education entries: {len(resume_data.education)}")
    
    return resume_data


def test_skill_analyzer(resume_data):
    """Test skill analysis"""
    print("\n" + "=" * 50)
    print("Testing Skill Analyzer")
    print("=" * 50)
    
    analyzer = SkillAnalyzer()
    profile = analyzer.analyze_skills(resume_data)
    
    print(f"✓ Total skills: {len(profile.all_skills)}")
    print(f"✓ Technical skills: {len(profile.technical_skills)}")
    print(f"✓ Soft skills: {len(profile.soft_skills)}")
    print(f"✓ Primary skills: {len(profile.primary_skills)}")
    
    # Print categorized skills
    print("\n📂 Categorized Skills:")
    for category, skills in profile.categorized_skills.items():
        if skills:
            print(f"  {category}: {', '.join(skills[:5])}")
    
    return profile


def test_experience_analyzer(resume_data):
    """Test experience analysis"""
    print("\n" + "=" * 50)
    print("Testing Experience Analyzer")
    print("=" * 50)
    
    analyzer = ExperienceAnalyzer()
    profile = analyzer.analyze_experience(resume_data)
    
    print(f"✓ Total years: {profile.total_years}")
    print(f"✓ Career level: {profile.career_level}")
    print(f"✓ Domain expertise: {', '.join(profile.domain_expertise)}")
    print(f"✓ Leadership: {profile.leadership_experience}")
    
    return profile


def test_job_recommender(skill_profile, experience_profile):
    """Test job recommendations"""
    print("\n" + "=" * 50)
    print("Testing Job Recommender")
    print("=" * 50)
    
    recommender = JobRecommender()
    recommendations = recommender.recommend_jobs(skill_profile, experience_profile)
    
    print(f"✓ Recommendations found: {len(recommendations)}")
    
    print("\n🎯 Top Job Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"  {i}. {rec.title} - {rec.skill_match_percentage:.0f}% match")
        print(f"     Demand: {rec.demand_level} | Growth: {rec.growth_potential}")
    
    return recommendations


def test_quality_scorer(resume_data, skill_profile):
    """Test quality scoring"""
    print("\n" + "=" * 50)
    print("Testing Quality Scorer")
    print("=" * 50)
    
    scorer = QualityScorer()
    score = scorer.score_resume(resume_data, skill_profile)
    
    print(f"✓ Overall Score: {score.overall_score}/100")
    print(f"✓ Grade: {score.grade}")
    
    print("\n📊 Score Breakdown:")
    print(f"  Skill Relevance: {score.skill_relevance_score:.0f}")
    print(f"  Experience Clarity: {score.experience_clarity_score:.0f}")
    print(f"  Keyword Optimization: {score.keyword_optimization_score:.0f}")
    print(f"  Structure & Readability: {score.structure_readability_score:.0f}")
    print(f"  Completeness: {score.completeness_score:.0f}")
    
    print("\n✅ Strengths:")
    for strength in score.strengths[:3]:
        print(f"  ✓ {strength}")
    
    print("\n💡 Improvement Tips:")
    for tip in score.improvement_tips[:3]:
        print(f"  • {tip}")
    
    return score


def test_api():
    """Test the main API"""
    print("\n" + "=" * 50)
    print("Testing Main API")
    print("=" * 50)
    
    api = ResumeIntelligenceAPI()
    
    # Test with text
    sample_text = """
ALEX JOHNSON
alex.johnson@email.com

PROFESSIONAL SUMMARY
Data Scientist with strong Python and Machine Learning experience.

SKILLS
Python, Machine Learning, SQL, TensorFlow, Data Analysis

EXPERIENCE
Data Scientist - DataCorp
January 2021 - Present
- Built ML models using Python and TensorFlow
- Analyzed large datasets using Pandas and SQL
- Deployed models to production

EDUCATION
MS Data Science - MIT
"""
    
    result = api.analyze_resume_text(sample_text)
    
    print(f"✓ API Analysis Complete")
    print(f"✓ Resume Score: {result['resume_score']['overall_score']}/100")
    print(f"✓ Grade: {result['resume_score']['grade']}")
    print(f"✓ Job Recommendations: {len(result['job_recommendations'])}")
    
    # Test quick analysis
    quick_result = api.get_quick_analysis("sample_resume.txt")
    print(f"✓ Quick Analysis: {quick_result['overall_score']}/100 ({quick_result['grade']})")
    
    return result


def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀" * 20)
    print("RESUME INTELLIGENCE ENGINE - TEST SUITE")
    print("🚀" * 20)
    
    try:
        # Test 1: Parser
        resume_data = test_parser()
        
        # Test 2: Skill Analyzer
        skill_profile = test_skill_analyzer(resume_data)
        
        # Test 3: Experience Analyzer
        experience_profile = test_experience_analyzer(resume_data)
        
        # Test 4: Job Recommender
        job_recommendations = test_job_recommender(skill_profile, experience_profile)
        
        # Test 5: Quality Scorer
        quality_score = test_quality_scorer(resume_data, skill_profile)
        
        # Test 6: Main API
        test_api()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        
        print("\n📋 Summary:")
        print(f"  • Parser: Working correctly")
        print(f"  • Skill Analyzer: Found {len(skill_profile.all_skills)} skills")
        print(f"  • Experience Analyzer: Detected {experience_profile.career_level} level")
        print(f"  • Job Recommender: {len(job_recommendations)} roles recommended")
        print(f"  • Quality Scorer: Grade {quality_score.grade}")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
