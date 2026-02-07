"""
Main API for Resume Intelligence Engine
"""
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import json

from parsers import ResumeParser
from analyzers import SkillAnalyzer, ExperienceAnalyzer, JobRecommender
from scorer import QualityScorer


class ResumeIntelligenceAPI:
    """
    Main API for Resume Intelligence Engine
    
    Usage:
        api = ResumeIntelligenceAPI()
        result = api.analyze_resume("path/to/resume.pdf")
        print(result)
    """
    
    def __init__(self):
        self.parser = ResumeParser
        self.skill_analyzer = SkillAnalyzer()
        self.experience_analyzer = ExperienceAnalyzer()
        self.job_recommender = JobRecommender()
        self.quality_scorer = QualityScorer()
    
    def analyze_resume(self, file_path: str, 
                      job_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a complete resume and return comprehensive results
        
        Args:
            file_path: Path to resume file (PDF, DOCX, or TXT)
            job_description: Optional job description for comparison
        
        Returns:
            Dictionary containing all analysis results
        """
        # Parse resume
        resume_data = self.parser.parse(Path(file_path))
        
        # Run all analyses
        skill_profile = self.skill_analyzer.analyze_skills(resume_data)
        experience_profile = self.experience_analyzer.analyze_experience(resume_data)
        job_recommendations = self.job_recommender.recommend_jobs(
            skill_profile, experience_profile
        )
        resume_score = self.quality_scorer.score_resume(resume_data, skill_profile)
        
        # Build comprehensive result
        result = {
            "basic_info": self._extract_basic_info(resume_data),
            "skill_profile": skill_profile.to_dict(),
            "experience_profile": experience_profile.to_dict(),
            "job_recommendations": [jr.to_dict() for jr in job_recommendations],
            "resume_score": resume_score.to_dict(),
            "suggestions": {
                "skill_improvements": self.skill_analyzer.get_skill_recommendations(skill_profile),
                "skill_gap_analysis": self._get_skill_gap_analysis(skill_profile, job_recommendations),
                "experience_insights": self.experience_analyzer.get_experience_summary(experience_profile)
            }
        }
        
        # Add job description comparison if provided
        if job_description:
            job_match = self.quality_scorer.compare_with_job_description(
                resume_data, job_description
            )
            result["job_match_analysis"] = job_match
        
        return result
    
    def analyze_resume_text(self, text: str, 
                           file_type: str = "txt") -> Dict[str, Any]:
        """Analyze resume from text string"""
        resume_data = self.parser.parse_text(text, file_type)
        
        skill_profile = self.skill_analyzer.analyze_skills(resume_data)
        experience_profile = self.experience_analyzer.analyze_experience(resume_data)
        job_recommendations = self.job_recommender.recommend_jobs(
            skill_profile, experience_profile
        )
        resume_score = self.quality_scorer.score_resume(resume_data, skill_profile)
        
        return {
            "basic_info": self._extract_basic_info(resume_data),
            "skill_profile": skill_profile.to_dict(),
            "experience_profile": experience_profile.to_dict(),
            "job_recommendations": [jr.to_dict() for jr in job_recommendations],
            "resume_score": resume_score.to_dict()
        }
    
    def get_quick_analysis(self, file_path: str) -> Dict[str, Any]:
        """Get quick analysis summary"""
        result = self.analyze_resume(file_path)
        
        return {
            "overall_score": result["resume_score"]["overall_score"],
            "grade": result["resume_score"]["grade"],
            "career_level": result["experience_profile"]["career_level"],
            "top_job_recommendations": [
                {
                    "title": jr["title"],
                    "match": f"{jr['skill_match_percentage']:.0f}%"
                }
                for jr in result["job_recommendations"][:3]
            ],
            "key_skills": result["skill_profile"]["primary_skills"][:5],
            "main_strength": result["resume_score"]["strengths"][0] if result["resume_score"]["strengths"] else "N/A",
            "main_improvement": result["resume_score"]["improvement_tips"][0] if result["resume_score"]["improvement_tips"] else "N/A"
        }
    
    def compare_with_job(self, file_path: str, job_description: str) -> Dict[str, Any]:
        """Compare resume against a job description"""
        result = self.analyze_resume(file_path, job_description)
        
        return {
            "match_percentage": result.get("job_match_analysis", {}).get("match_percentage", 0),
            "recommendation": result.get("job_match_analysis", {}).get("recommendation", ""),
            "missing_requirements": result.get("job_match_analysis", {}).get("requirements_missing", []),
            "matched_requirements": result.get("job_match_analysis", {}).get("requirements_found", []),
            "resume_score": result["resume_score"]["overall_score"],
            "career_level_match": self._check_career_level_match(
                result["experience_profile"]["career_level"],
                job_description
            )
        }
    
    def get_skill_gap_for_role(self, file_path: str, role: str) -> Dict[str, Any]:
        """Get detailed skill gap for a specific role"""
        resume_data = self.parser.parse(Path(file_path))
        skill_profile = self.skill_analyzer.analyze_skills(resume_data)
        
        return self.job_recommender.get_skill_gap_analysis(skill_profile, role)
    
    def get_career_roadmap(self, file_path: str, target_role: str) -> Dict[str, Any]:
        """Get career roadmap to reach target role"""
        resume_data = self.parser.parse(Path(file_path))
        skill_profile = self.skill_analyzer.analyze_skills(resume_data)
        experience_profile = self.experience_analyzer.analyze_experience(resume_data)
        
        return self.job_recommender.get_career_roadmap(
            skill_profile, experience_profile, target_role
        )
    
    def export_report(self, file_path: str, output_path: str,
                     format: str = "json") -> str:
        """Export analysis report to file"""
        result = self.analyze_resume(file_path)
        
        if format == "json":
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
        elif format == "txt":
            self._export_text_report(result, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return output_path
    
    def _extract_basic_info(self, resume_data) -> Dict[str, Any]:
        """Extract basic information from resume"""
        return {
            "name": resume_data.full_name,
            "email": resume_data.email,
            "location": resume_data.location,
            "linkedin": resume_data.linkedin,
            "github": resume_data.github,
            "summary_preview": resume_data.summary[:200] + "..." if len(resume_data.summary) > 200 else resume_data.summary
        }
    
    def _get_skill_gap_analysis(self, skill_profile, job_recommendations) -> Dict[str, Any]:
        """Get skill gap analysis across top recommendations"""
        if not job_recommendations:
            return {}
        
        top_role = job_recommendations[0].job_id
        return self.job_recommender.get_skill_gap_analysis(skill_profile, top_role)
    
    def _check_career_level_match(self, candidate_level: str, 
                                  job_description: str) -> str:
        """Check if candidate level matches job requirements"""
        job_lower = job_description.lower()
        
        senior_keywords = ["senior", "sr", "5+ years", "7+ years"]
        junior_keywords = ["junior", "jr", "entry", "0-2 years", "recent graduate"]
        
        if any(kw in job_lower for kw in senior_keywords):
            if candidate_level in ["senior", "lead", "architect"]:
                return "Good match"
            elif candidate_level == "mid-level":
                return "Possible match with experience"
            else:
                return "May lack required experience"
        
        if any(kw in job_lower for kw in junior_keywords):
            if candidate_level in ["fresher", "junior"]:
                return "Good match"
            else:
                return "May be overqualified"
        
        return "Likely match"
    
    def _export_text_report(self, result: Dict, output_path: str):
        """Export analysis as readable text report"""
        lines = []
        lines.append("=" * 60)
        lines.append("RESUME INTELLIGENCE REPORT")
        lines.append("=" * 60)
        
        lines.append("\n📊 OVERALL SCORE")
        lines.append(f"Grade: {result['resume_score']['grade']}")
        lines.append(f"Score: {result['resume_score']['overall_score']}/100")
        
        lines.append("\n👤 BASIC INFO")
        basic = result['basic_info']
        lines.append(f"Name: {basic['name']}")
        lines.append(f"Email: {basic['email']}")
        
        lines.append("\n💼 CAREER PROFILE")
        exp = result['experience_profile']
        lines.append(f"Level: {exp['career_level'].title()}")
        lines.append(f"Experience: {exp['total_years_experience']} years")
        
        lines.append("\n🎯 TOP JOB RECOMMENDATIONS")
        for i, jr in enumerate(result['job_recommendations'][:5], 1):
            lines.append(f"{i}. {jr['title']} - {jr['skill_match_percentage']:.0f}% match")
        
        lines.append("\n📈 STRENGTHS")
        for strength in result['resume_score']['strengths'][:3]:
            lines.append(f"✓ {strength}")
        
        lines.append("\n🔧 IMPROVEMENT TIPS")
        for tip in result['resume_score']['improvement_tips'][:3]:
            lines.append(f"• {tip}")
        
        lines.append("\n" + "=" * 60)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
