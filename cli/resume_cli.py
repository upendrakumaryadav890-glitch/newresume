"""
CLI Interface for Resume Intelligence Engine
"""
import argparse
import sys
from pathlib import Path
from api.resume_api import ResumeIntelligenceAPI


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Resume Intelligence Engine - Analyze and improve your resume",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  resume-analyze resume.pdf
  resume-analyze resume.docx --quick
  resume-analyze resume.txt --job "job_description.txt"
  resume-analyze resume.pdf --export report.json
        """
    )
    
    parser.add_argument(
        "resume",
        help="Path to resume file (PDF, DOCX, or TXT)"
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Show quick analysis summary only"
    )
    
    parser.add_argument(
        "--job", "-j",
        help="Path to job description file for comparison"
    )
    
    parser.add_argument(
        "--export", "-e",
        help="Export analysis to file (JSON or TXT format)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "txt"],
        default="json",
        help="Export format (default: json)"
    )
    
    parser.add_argument(
        "--skill-gap",
        help="Analyze skill gap for a specific job role"
    )
    
    parser.add_argument(
        "--roadmap",
        help="Get career roadmap to reach a target role"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed analysis"
    )
    
    args = parser.parse_args()
    
    # Check if resume file exists
    resume_path = Path(args.resume)
    if not resume_path.exists():
        print(f"Error: Resume file not found: {args.resume}")
        sys.exit(1)
    
    # Initialize API
    api = ResumeIntelligenceAPI()
    
    try:
        if args.quick:
            # Quick analysis
            result = api.get_quick_analysis(args.resume)
            print_quick_result(result)
        
        elif args.job:
            # Compare with job description
            with open(args.job, 'r') as f:
                job_description = f.read()
            result = api.compare_with_job(args.resume, job_description)
            print_job_comparison(result)
        
        elif args.skill_gap:
            # Skill gap analysis
            result = api.get_skill_gap_for_role(args.resume, args.skill_gap)
            print_skill_gap(result)
        
        elif args.roadmap:
            # Career roadmap
            result = api.get_career_roadmap(args.resume, args.roadmap)
            print_roadmap(result)
        
        elif args.export:
            # Export report
            output_path = api.export_report(
                args.resume, 
                args.export,
                format=args.format
            )
            print(f"Report exported to: {output_path}")
        
        elif args.verbose:
            # Full detailed analysis
            result = api.analyze_resume(args.resume)
            print_verbose_result(result)
        
        else:
            # Default: Full analysis
            result = api.analyze_resume(args.resume)
            print_standard_result(result)
    
    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        sys.exit(1)


def print_quick_result(result):
    """Print quick analysis result"""
    print("\n" + "=" * 50)
    print("RESUME ANALYSIS - QUICK SUMMARY")
    print("=" * 50)
    
    print(f"\n📊 Score: {result['overall_score']}/100 (Grade: {result['grade']})")
    print(f"💼 Level: {result['career_level'].title()}")
    
    print("\n🎯 Top Job Recommendations:")
    for rec in result['top_job_recommendations']:
        print(f"  • {rec['title']} - {rec['match']}")
    
    print("\n🔑 Key Skills:")
    for skill in result['key_skills']:
        print(f"  • {skill['skill']} ({skill['category']})")
    
    print(f"\n✅ Strength: {result['main_strength']}")
    print(f"💡 Tip: {result['main_improvement']}")
    
    print("\n" + "=" * 50)


def print_standard_result(result):
    """Print standard analysis result"""
    print("\n" + "=" * 60)
    print("RESUME INTELLIGENCE ANALYSIS")
    print("=" * 60)
    
    # Basic info
    basic = result['basic_info']
    print(f"\n👤 {basic['name'] or 'Unknown'}")
    print(f"   {basic['email'] or 'No email'}")
    
    # Score
    score = result['resume_score']
    print(f"\n📊 Overall Score: {score['overall_score']}/100 (Grade: {score['grade']})")
    
    # Experience
    exp = result['experience_profile']
    print(f"\n💼 Career: {exp['career_level'].title()} ({exp['total_years_experience']} years)")
    
    # Job recommendations
    print("\n🎯 Job Recommendations:")
    for i, jr in enumerate(result['job_recommendations'][:5], 1):
        print(f"  {i}. {jr['title']} - {jr['skill_match_percentage']:.0f}% match")
    
    # Top skills
    print("\n🛠️ Top Skills:")
    for skill in result['skill_profile']['primary_skills'][:5]:
        print(f"  • {skill['skill']} ({skill['category']})")
    
    # Strengths
    print("\n✅ Strengths:")
    for strength in score['strengths'][:3]:
        print(f"  ✓ {strength}")
    
    # Improvement tips
    print("\n💡 Improvement Tips:")
    for tip in score['improvement_tips'][:3]:
        print(f"  • {tip}")
    
    print("\n" + "=" * 60)


def print_verbose_result(result):
    """Print detailed analysis result"""
    import json
    
    print("\n" + "=" * 60)
    print("DETAILED RESUME ANALYSIS")
    print("=" * 60)
    
    print("\n📋 BASIC INFORMATION")
    print(json.dumps(result['basic_info'], indent=2))
    
    print("\n💼 EXPERIENCE PROFILE")
    print(json.dumps(result['experience_profile'], indent=2))
    
    print("\n🎯 JOB RECOMMENDATIONS")
    for jr in result['job_recommendations']:
        print(f"\n{jr['title']}")
        print(f"  Match: {jr['skill_match_percentage']:.0f}%")
        print(f"  Why fits: {'; '.join(jr['why_fits'])}")
        print(f"  Missing: {', '.join(jr['missing_critical_skills'][:3])}")
    
    print("\n📊 QUALITY SCORE")
    print(json.dumps(result['resume_score'], indent=2))
    
    print("\n📈 SKILL PROFILE")
    print(json.dumps(result['skill_profile'], indent=2))
    
    print("\n💡 SUGGESTIONS")
    print(json.dumps(result['suggestions'], indent=2))
    
    print("\n" + "=" * 60)


def print_job_comparison(result):
    """Print job comparison result"""
    print("\n" + "=" * 50)
    print("JOB MATCH ANALYSIS")
    print("=" * 50)
    
    print(f"\n📊 Match: {result['match_percentage']:.0f}%")
    print(f"💡 Recommendation: {result['recommendation']}")
    print(f"🎯 Level Match: {result['career_level_match']}")
    
    print("\n✅ Matched Requirements:")
    for req in result['matched_requirements'][:5]:
        print(f"  ✓ {req}")
    
    print("\n❌ Missing Requirements:")
    for req in result['missing_requirements'][:5]:
        print(f"  ✗ {req}")
    
    print("\n📊 Resume Score: {}/100".format(result['resume_score']))
    
    print("\n" + "=" * 50)


def print_skill_gap(result):
    """Print skill gap analysis"""
    print("\n" + "=" * 50)
    print(f"SKILL GAP ANALYSIS - {result['target_role']}")
    print("=" * 50)
    
    print(f"\n📊 Match: {result['match_percentage']}%")
    
    print("\n✅ Matched Skills:")
    for skill in result['matched_skills']:
        print(f"  ✓ {skill}")
    
    print("\n❌ Critical Missing:")
    for skill in result['critical_missing_skills']:
        print(f"  ✗ {skill}")
    
    print("\n📚 Learning Resources:")
    for skill, resources in result['learning_resources'].items():
        print(f"\n  {skill}:")
        print(f"    Level: {resources['level']}")
        print(f"    Time: {resources['time_estimate']}")
        print(f"    Resources: {', '.join(resources['resources'][:2])}")
    
    print(f"\n⏱️ Time to Job Ready: {result['time_to_job_ready']}")
    
    print("\n" + "=" * 50)


def print_roadmap(result):
    """Print career roadmap"""
    print("\n" + "=" * 50)
    print(f"CAREER ROADMAP - {result['target_role']}")
    print("=" * 50)
    
    print(f"\n📍 Current: {result['current_level'].title()}")
    print(f"🎯 Target: {result['target_role']} ({result['target_level']})")
    
    print("\n📝 Steps:")
    for i, step in enumerate(result['steps'], 1):
        print(f"\n{i}. {step['phase']}")
        print(f"   Timeline: {step['timeline']}")
        print(f"   Outcome: {step['outcome']}")
        print("   Actions:")
        for action in step['actions']:
            print(f"     • {action}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
