
"""
Main Entry Point for Resume Intelligence Engine
"""
from api.resume_api import ResumeIntelligenceAPI


def main():
    """Main entry point"""
    api = ResumeIntelligenceAPI()
    
    # Example usage
    print("Resume Intelligence Engine")
    print("=" * 50)
    
    # You can use this to test with a resume file
    import sys
    
    if len(sys.argv) > 1:
        resume_path = sys.argv[1]
        print(f"\nAnalyzing: {resume_path}")
        
        result = api.analyze_resume(resume_path)
        
        print(f"\n[SCORE] Overall Score: {result['resume_score']['overall_score']}/100")
        print(f"[GRADE] Grade: {result['resume_score']['grade']}")
        print(f"[CAREER] Career Level: {result['experience_profile']['career_level']}")
        
        print("\n[JOBS] Top Job Recommendations:")
        for jr in result['job_recommendations'][:3]:
            print(f"  - {jr['title']} - {jr['skill_match_percentage']:.0f}% match")
        
        print("\n[STRENGTHS] Top Strengths:")
        for strength in result['resume_score']['strengths'][:3]:
            print(f"  + {strength}")
        
        print("\n[TIPS] Top Improvement Tips:")
        for tip in result['resume_score']['improvement_tips'][:3]:
            print(f"  * {tip}")
    else:
        print("Usage: python main.py <resume_file>")
        print("\nSupported formats: PDF, DOCX, TXT")
        print("\nOr use the CLI:")
        print("  python -m cli.resume_cli resume.pdf --quick")
        print("  python -m cli.resume_cli resume.pdf --job job_description.txt")


if __name__ == "__main__":
    main()

