"""
Resume Quality Scorer for Resume Intelligence Engine
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from config.config import SCORING_WEIGHTS, ATS_KEYWORDS


@dataclass
class ResumeScore:
    """Complete resume scoring data"""
    overall_score: float
    skill_relevance_score: float
    experience_clarity_score: float
    keyword_optimization_score: float
    structure_readability_score: float
    completeness_score: float
    ats_compatibility_score: float
    strengths: List[str]
    weaknesses: List[str]
    improvement_tips: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "overall_score": round(self.overall_score, 2),
            "breakdown": {
                "skill_relevance": round(self.skill_relevance_score, 2),
                "experience_clarity": round(self.experience_clarity_score, 2),
                "keyword_optimization": round(self.keyword_optimization_score, 2),
                "structure_readability": round(self.structure_readability_score, 2),
                "completeness": round(self.completeness_score, 2),
                "ats_compatibility": round(self.ats_compatibility_score, 2)
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "improvement_tips": self.improvement_tips,
            "grade": self._get_grade()
        }
    
    def _get_grade(self) -> str:
        """Get letter grade based on score"""
        if self.overall_score >= 90:
            return "A+"
        elif self.overall_score >= 80:
            return "A"
        elif self.overall_score >= 70:
            return "B+"
        elif self.overall_score >= 60:
            return "B"
        elif self.overall_score >= 50:
            return "C+"
        elif self.overall_score >= 40:
            return "C"
        else:
            return "D"


class QualityScorer:
    """Score and evaluate resume quality"""
    
    # Required sections for a complete resume
    REQUIRED_SECTIONS = [
        "summary",
        "skills",
        "experience",
        "education"
    ]
    
    # Optional but beneficial sections
    RECOMMENDED_SECTIONS = [
        "certifications",
        "projects",
        "links"
    ]
    
    # ATS-friendly keywords by category
    ATS_KEYWORDS = {
        "technology": ["agile", "scrum", "ci/cd", "devops", "microservices", "api", "cloud",
                       "python", "java", "javascript", "sql", "git", "docker", "kubernetes"],
        "general": ["leadership", "teamwork", "communication", "problem-solving", "analytical",
                    "project management", "stakeholder", "strategy", "innovation"],
        "soft_skills": ["collaboration", "adaptability", "critical thinking", "time management",
                        "attention to detail", "organization", "multitasking"]
    }
    
    def __init__(self):
        self.weights = SCORING_WEIGHTS
    
    def score_resume(self, resume_data, skill_profile=None) -> ResumeScore:
        """Score a complete resume"""
        
        # Calculate individual scores
        skill_score = self._score_skill_relevance(resume_data, skill_profile)
        experience_score = self._score_experience_clarity(resume_data)
        keyword_score = self._score_keyword_optimization(resume_data)
        structure_score = self._score_structure_readability(resume_data)
        completeness_score = self._score_completeness(resume_data)
        ats_score = self._score_ats_compatibility(resume_data)
        
        # Calculate weighted overall score
        overall = (
            skill_score * self.weights["skill_relevance"] +
            experience_score * self.weights["experience_clarity"] +
            keyword_score * self.weights["keyword_optimization"] +
            structure_score * self.weights["structure_readability"] +
            completeness_score * self.weights["completeness"]
        )
        
        # Generate strengths and weaknesses
        strengths, weaknesses = self._analyze_strengths_weaknesses(
            skill_score, experience_score, keyword_score, 
            structure_score, completeness_score, ats_score
        )
        
        # Generate improvement tips
        tips = self._generate_improvement_tips(
            resume_data, skill_profile,
            skill_score, experience_score, keyword_score,
            structure_score, completeness_score, ats_score
        )
        
        return ResumeScore(
            overall_score=overall,
            skill_relevance_score=skill_score,
            experience_clarity_score=experience_score,
            keyword_optimization_score=keyword_score,
            structure_readability_score=structure_score,
            completeness_score=completeness_score,
            ats_compatibility_score=ats_score,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_tips=tips
        )
    
    def _score_skill_relevance(self, resume_data, skill_profile) -> float:
        """Score skill relevance"""
        if not skill_profile:
            return 50  # Default score if no profile
        
        # Check for minimum number of skills
        total_skills = len(skill_profile.all_skills)
        if total_skills < 5:
            return min(40, total_skills * 8)
        elif total_skills > 20:
            return min(95, 70 + (total_skills - 20) * 1)
        else:
            return 70 + (total_skills - 5) * 2.5
    
    def _score_experience_clarity(self, resume_data) -> float:
        """Score experience clarity"""
        score = 0
        experiences = resume_data.experiences
        
        if not experiences:
            return 20
        
        # Check for role and company clarity
        clear_entries = 0
        for exp in experiences:
            if exp.role and exp.company:
                clear_entries += 1
            if exp.duration:
                score += 5
            if exp.description and len(exp.description) > 50:
                score += 5
        
        # Base score for having experience
        base_score = min(40, len(experiences) * 10)
        
        # Clarity bonus
        clarity_bonus = (clear_entries / len(experiences)) * 30 if experiences else 0
        
        return min(100, base_score + clarity_bonus)
    
    def _score_keyword_optimization(self, resume_data) -> float:
        """Score ATS keyword optimization"""
        text = resume_data.raw_text.lower()
        
        # Count found keywords
        total_keywords = 0
        found_keywords = 0
        
        for category_keywords in self.ATS_KEYWORDS.values():
            for keyword in category_keywords:
                total_keywords += 1
                if keyword.lower() in text:
                    found_keywords += 1
        
        # Calculate score
        if total_keywords == 0:
            return 50
        
        keyword_score = (found_keywords / total_keywords) * 100
        
        # Bonus for skill variety
        skill_count = len(resume_data.technical_skills) + len(resume_data.soft_skills)
        if skill_count > 10:
            keyword_score = min(100, keyword_score + 10)
        
        return keyword_score
    
    def _score_structure_readability(self, resume_data) -> float:
        """Score structure and readability"""
        score = 50
        
        # Check for proper sections
        has_summary = bool(resume_data.summary)
        has_skills = bool(resume_data.technical_skills or resume_data.soft_skills)
        has_experience = bool(resume_data.experiences)
        has_education = bool(resume_data.education)
        
        sections_present = sum([has_summary, has_skills, has_experience, has_education])
        score += sections_present * 10
        
        # Check for contact info
        has_email = bool(resume_data.email)
        has_phone = bool(resume_data.phone)
        
        if has_email:
            score += 5
        if has_phone:
            score += 5
        
        # Check for links
        if resume_data.linkedin or resume_data.github:
            score += 5
        
        # Check for project descriptions
        if resume_data.projects:
            score += min(10, len(resume_data.projects) * 5)
        
        return min(100, score)
    
    def _score_completeness(self, resume_data) -> float:
        """Score overall completeness"""
        score = 0
        
        # Required sections
        for section in self.REQUIRED_SECTIONS:
            if section == "summary" and resume_data.summary:
                score += 15
            elif section == "skills" and (resume_data.technical_skills or resume_data.soft_skills):
                score += 15
            elif section == "experience" and resume_data.experiences:
                score += 20
            elif section == "education" and resume_data.education:
                score += 15
        
        # Recommended sections
        if resume_data.certifications:
            score += 10
        if resume_data.projects:
            score += 10
        if resume_data.linkedin or resume_data.github or resume_data.website:
            score += 5
        
        return min(100, score)
    
    def _score_ats_compatibility(self, resume_data) -> float:
        """Score ATS compatibility"""
        score = 70  # Base score
        
        text = resume_data.raw_text.lower()
        
        # Check for common ATS issues
        issues = []
        
        # Check for tables ( ATS issues)
        if "table" in text or "|" in text:
            issues.append("May contain ATS-unfriendly formatting")
        
        # Check for headers (good for ATS)
        headers = ["experience", "education", "skills", "summary"]
        found_headers = sum(1 for h in headers if h in text)
        score += found_headers * 3
        
        # Check for consistent formatting
        if resume_data.email and "@" in resume_data.email:
            score += 5
        else:
            issues.append("Missing or unclear email address")
        
        if resume_data.phone:
            score += 5
        else:
            issues.append("Missing phone number")
        
        # Check for action verbs (good for ATS)
        action_verbs = ["led", "managed", "developed", "created", "implemented", 
                       "designed", "analyzed", "improved", "increased"]
        action_count = sum(1 for verb in action_verbs if verb in text)
        score += min(10, action_count * 2)
        
        return max(0, min(100, score))
    
    def _analyze_strengths_weaknesses(self, skill: float, experience: float,
                                     keyword: float, structure: float,
                                     completeness: float, ats: float) -> Tuple[List[str], List[str]]:
        """Analyze strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        thresholds = {"excellent": 85, "good": 70, "average": 50}
        
        categories = [
            ("Skill relevance", skill),
            ("Experience clarity", experience),
            ("Keyword optimization", keyword),
            ("Structure readability", structure),
            ("Completeness", completeness),
            ("ATS compatibility", ats)
        ]
        
        for name, score in categories:
            if score >= thresholds["excellent"]:
                strengths.append(f"Strong {name.lower()}")
            elif score < thresholds["average"]:
                weaknesses.append(f"Needs improvement in {name.lower()}")
        
        return strengths, weaknesses
    
    def _generate_improvement_tips(self, resume_data, skill_profile,
                                   skill: float, experience: float,
                                   keyword: float, structure: float,
                                   completeness: float, ats: float) -> List[str]:
        """Generate actionable improvement tips"""
        tips = []
        
        # Skills tips
        if skill < 70:
            tips.append("Add more relevant technical skills to your profile")
            if skill_profile:
                missing = skill_profile.categorized_skills.get("unknown", [])
                if missing:
                    tips.append(f"Consider validating your skills: {', '.join(missing[:3])}")
        
        # Experience tips
        if experience < 70:
            tips.append("Provide clearer descriptions of your work experience")
            tips.append("Include specific achievements with metrics where possible")
        
        # Keyword tips
        if keyword < 70:
            tips.append("Research and include more industry-specific keywords")
            for category, keywords in self.ATS_KEYWORDS.items():
                relevant = [k for k in keywords if k not in resume_data.raw_text.lower()]
                if relevant:
                    tips.append(f"Consider adding: {', '.join(relevant[:3])}")
        
        # Structure tips
        if structure < 70:
            tips.append("Ensure all sections have clear headings")
            tips.append("Include your LinkedIn and GitHub profiles")
        
        # Completeness tips
        if completeness < 70:
            if not resume_data.summary:
                tips.append("Add a professional summary at the top of your resume")
            if not resume_data.projects:
                tips.append("Add relevant personal or professional projects")
            if not resume_data.certifications:
                tips.append("Consider adding relevant certifications")
        
        # ATS tips
        if ats < 70:
            tips.append("Avoid complex formatting, tables, or graphics")
            tips.append("Use standard section headings (Experience, Education, Skills)")
            tips.append("Include a clean, standard email format")
        
        # General tips
        if len(tips) < 2:
            tips.append("Quantify achievements with specific metrics and numbers")
            tips.append("Use action verbs at the start of bullet points")
        
        return tips[:8]  # Limit to 8 most important tips
    
    def compare_with_job_description(self, resume_data, job_description: str) -> Dict:
        """Compare resume with specific job description"""
        job_text = job_description.lower()
        
        # Extract key requirements from job description
        import re
        
        # Find skill mentions
        skill_patterns = [
            r"(?:required|must have|experience with)\s+([a-z+#]+(?:\s+[a-z+#]+){0,3})",
            r"(?:proficient|familiar)\s+in\s+([a-z]+(?:\s+[a-z]+){0,3})",
        ]
        
        requirements = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, job_text)
            requirements.extend(matches)
        
        # Handle both ResumeData objects and dictionaries
        if hasattr(resume_data, 'raw_text'):
            # It's a ResumeData object
            resume_text = resume_data.raw_text.lower()
        else:
            # It's a dictionary - reconstruct text from available fields
            text_parts = []
            if isinstance(resume_data, dict):
                # Get summary
                if 'basic_info' in resume_data:
                    summary = resume_data['basic_info'].get('summary_preview', '')
                    text_parts.append(summary)
                
                # Get skills
                if 'skill_profile' in resume_data:
                    skills = resume_data['skill_profile'].get('all_skills', [])
                    text_parts.extend(skills)
                
                # Get primary skills
                if 'skill_profile' in resume_data:
                    for skill in resume_data['skill_profile'].get('primary_skills', []):
                        if isinstance(skill, dict):
                            text_parts.append(skill.get('skill', ''))
                        else:
                            text_parts.append(str(skill))
            
            resume_text = ' '.join(text_parts).lower()
        
        matched = []
        missing = []
        
        for req in requirements[:10]:  # Limit to top 10 requirements
            if any(word in resume_text for word in req.split()):
                matched.append(req)
            else:
                missing.append(req)
        
        match_percentage = len(matched) / len(requirements) * 100 if requirements else 0
        
        return {
            "match_percentage": round(match_percentage, 2),
            "requirements_found": matched,
            "requirements_missing": missing,
            "recommendation": self._get_match_recommendation(match_percentage)
        }
    
    def _get_match_recommendation(self, match_percentage: float) -> str:
        """Get recommendation based on match percentage"""
        if match_percentage >= 80:
            return "Strong match! Apply with confidence."
        elif match_percentage >= 60:
            return "Good match. Consider addressing missing requirements."
        elif match_percentage >= 40:
            return "Partial match. Significant skill gaps to address."
        else:
            return "Low match. Consider applying to similar roles first."
