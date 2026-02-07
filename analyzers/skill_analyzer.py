"""
Skill Analyzer for Resume Intelligence Engine
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from config.config import SKILL_CATEGORIES, JOB_ROLES
from utils.skill_normalizer import SkillNormalizer, NormalizedSkill


@dataclass
class SkillProfile:
    """Complete skill profile for a candidate"""
    all_skills: List[str] = field(default_factory=list)
    categorized_skills: Dict[str, List[str]] = field(default_factory=dict)
    primary_skills: List[Tuple[str, str, float]] = field(default_factory=list)
    secondary_skills: List[Tuple[str, str, float]] = field(default_factory=list)
    emerging_skills: List[str] = field(default_factory=list)
    normalized_skills: List[NormalizedSkill] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    technical_skills: List[str] = field(default_factory=list)
    tools_platforms: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "all_skills": self.all_skills,
            "categorized_skills": self.categorized_skills,
            "primary_skills": [
                {"skill": s[0], "category": s[1], "score": s[2]} 
                for s in self.primary_skills
            ],
            "secondary_skills": [
                {"skill": s[0], "category": s[1], "score": s[2]} 
                for s in self.secondary_skills
            ],
            "emerging_skills": self.emerging_skills,
            "soft_skills": self.soft_skills,
            "technical_skills": self.technical_skills,
            "tools_platforms": self.tools_platforms,
            "total_skills_count": len(self.all_skills)
        }


class SkillAnalyzer:
    """Analyze and profile skills from resume data"""
    
    def __init__(self):
        self.normalizer = SkillNormalizer()
    
    def analyze_skills(self, resume_data) -> SkillProfile:
        """Analyze all skills from resume data"""
        profile = SkillProfile()
        
        # Collect all skills from resume
        all_skills = []
        
        # Add technical skills
        all_skills.extend(resume_data.technical_skills)
        
        # Add soft skills
        all_skills.extend(resume_data.soft_skills)
        
        # Add tools
        all_skills.extend(resume_data.tools)
        
        # Extract skills from other sections
        for exp in resume_data.experiences:
            all_skills.extend(self._extract_skills_from_text(exp.description))
        
        for proj in resume_data.projects:
            all_skills.extend(proj.technologies)
            all_skills.extend(self._extract_skills_from_text(proj.description))
        
        # Normalize all skills
        profile.normalized_skills = self.normalizer.normalize_list(all_skills)
        profile.all_skills = list(set([s.normalized for s in profile.normalized_skills]))
        
        # Categorize skills
        profile.categorized_skills = self.normalizer.categorize(profile.all_skills)
        
        # Separate by type
        profile.technical_skills = (
            profile.categorized_skills.get("programming_languages", []) +
            profile.categorized_skills.get("frameworks_libraries", []) +
            profile.categorized_skills.get("data_science", []) +
            profile.categorized_skills.get("devops_cloud", [])
        )
        
        profile.soft_skills = profile.categorized_skills.get("soft_skills", [])
        profile.tools_platforms = profile.categorized_skills.get("tools_platforms", [])
        
        # Identify primary and secondary skills
        scored_skills = self.normalizer.identify_primary_skills(profile.all_skills)
        
        # Split into primary (top 50%) and secondary
        mid_point = max(len(scored_skills) // 3, 1)
        profile.primary_skills = scored_skills[:mid_point]
        profile.secondary_skills = scored_skills[mid_point:]
        
        # Identify emerging skills
        profile.emerging_skills = self.normalizer.identify_emerging_skills(
            profile.all_skills,
            resume_data.summary + " " + " ".join([e.description for e in resume_data.experiences])
        )
        
        return profile
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract potential skills from text"""
        found_skills = []
        text_lower = text.lower()
        
        for category, category_skills in SKILL_CATEGORIES.items():
            for skill in category_skills:
                if skill.lower() in text_lower:
                    found_skills.append(skill)
        
        return found_skills
    
    def calculate_skill_gap(self, profile: SkillProfile, 
                            target_role: str) -> Dict:
        """Calculate skill gap for a target role"""
        if target_role not in JOB_ROLES:
            return {"error": f"Unknown role: {target_role}"}
        
        role_data = JOB_ROLES[target_role]
        required_skills = role_data["required_skills"]
        
        candidate_skills = set(s.lower() for s in profile.all_skills)
        required_skills_lower = set(s.lower() for s in required_skills)
        
        matched = candidate_skills & required_skills_lower
        missing = required_skills_lower - candidate_skills
        
        match_percentage = len(matched) / len(required_skills_lower) if required_skills_lower else 1.0
        
        # Suggest alternatives for missing skills
        suggestions = {}
        for missing_skill in missing:
            category = self.normalizer._get_category(missing_skill.title())
            if category != "unknown":
                related = self.normalizer.suggest_skill_expansion(
                    profile.all_skills, 
                    category
                )
                suggestions[missing_skill.title()] = related[:3]
        
        return {
            "target_role": role_data["title"],
            "required_skills": required_skills,
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "match_percentage": round(match_percentage, 2),
            "skill_gap_analysis": {
                "critical_missing": [s for s in missing if s in ["python", "java", "sql"]],
                "recommended_learning": list(missing)
            },
            "suggestions": suggestions
        }
    
    def get_skill_recommendations(self, profile: SkillProfile) -> Dict:
        """Get skill recommendations based on current profile"""
        recommendations = {
            "hot_skills_to_learn": [],
            "complementary_skills": [],
            "certification_suggestions": [],
            "project_ideas": []
        }
        
        # Get primary skill categories
        primary_categories = [s[1] for s in profile.primary_skills[:3]]
        
        # Suggest hot skills based on market demand
        hot_skills_db = {
            "programming_languages": ["Python", "TypeScript", "Go", "Rust"],
            "frameworks_libraries": ["React", "Next.js", "FastAPI", "TensorFlow"],
            "tools_platforms": ["Docker", "Kubernetes", "AWS", "PostgreSQL"],
            "data_science": ["Machine Learning", "Deep Learning", "NLP"],
            "devops_cloud": ["DevOps", "Cloud Architecture", "Terraform"],
        }
        
        for category in primary_categories:
            if category in hot_skills_db:
                current_lower = [s.lower() for s in profile.all_skills]
                for hot_skill in hot_skills_db[category]:
                    if hot_skill.lower() not in current_lower:
                        recommendations["hot_skills_to_learn"].append(hot_skill)
        
        # Suggest complementary skills
        complementary_db = {
            "Python": ["Django", "Flask", "FastAPI", "Pandas", "TensorFlow"],
            "JavaScript": ["React", "Node.js", "TypeScript", "GraphQL"],
            "Java": ["Spring", "Hibernate", "Maven", "Kubernetes"],
            "React": ["Redux", "TypeScript", "Next.js", "Jest"],
            "Machine Learning": ["TensorFlow", "PyTorch", "Scikit-learn", "MLOps"],
        }
        
        for skill in profile.primary_skills[:5]:
            skill_name = skill[0]
            if skill_name in complementary_db:
                current_lower = [s.lower() for s in profile.all_skills]
                for comp_skill in complementary_db[skill_name]:
                    if comp_skill.lower() not in current_lower:
                        recommendations["complementary_skills"].append(comp_skill)
        
        # Remove duplicates
        recommendations["hot_skills_to_learn"] = list(set(recommendations["hot_skills_to_learn"]))[:5]
        recommendations["complementary_skills"] = list(set(recommendations["complementary_skills"]))[:5]
        
        # Certification suggestions
        cert_db = {
            "AWS": ["AWS Solutions Architect", "AWS Developer", "AWS DevOps Engineer"],
            "Azure": ["Azure Solutions Architect", "Azure Developer", "Azure Administrator"],
            "GCP": ["Google Cloud Professional", "GCP Architect", "GCP Data Engineer"],
            "Kubernetes": ["CKA (Certified Kubernetes Administrator)", "CKAD (Developer)"],
            "Python": ["PCEP", "PCAP", "PCPP"],
            "Machine Learning": ["TensorFlow Developer", "AWS Machine Learning", "Google ML"],
            "DevOps": ["DevOps Foundation", "Site Reliability Engineer"],
            "Project Management": ["PMP", "CSM (Scrum Master)", "PRINCE2"],
        }
        
        cert_skills = [s[0] for s in profile.primary_skills if s[0] in cert_db]
        for skill in cert_skills:
            recommendations["certification_suggestions"].extend(cert_db[skill])
        
        recommendations["certification_suggestions"] = list(set(recommendations["certification_suggestions"]))[:5]
        
        return recommendations
    
    def analyze_skill_depth(self, profile: SkillProfile) -> Dict:
        """Analyze depth/breadth of candidate's skills"""
        analysis = {
            "breadth_score": 0,
            "depth_score": 0,
            "balance_score": 0,
            "strength_areas": [],
            "weak_areas": [],
            "overall_assessment": ""
        }
        
        # Calculate breadth (number of unique skill categories)
        active_categories = sum(1 for cat, skills in profile.categorized_skills.items() 
                                if skills and cat != "unknown")
        max_categories = len([c for c in SKILL_CATEGORIES.keys()])
        analysis["breadth_score"] = round(active_categories / max_categories, 2)
        
        # Calculate depth (skills per category)
        skills_per_category = {
            cat: len(skills) 
            for cat, skills in profile.categorized_skills.items() 
            if skills
        }
        
        if skills_per_category:
            avg_depth = sum(skills_per_category.values()) / len(skills_per_category)
            analysis["depth_score"] = min(avg_depth / 10, 1.0)  # Cap at 10 skills per category
        
        # Balance score
        if analysis["breadth_score"] and analysis["depth_score"]:
            analysis["balance_score"] = round(
                (analysis["breadth_score"] + analysis["depth_score"]) / 2, 2
            )
        
        # Identify strength areas
        sorted_categories = sorted(skills_per_category.items(), 
                                    key=lambda x: x[1], reverse=True)
        analysis["strength_areas"] = [cat for cat, count in sorted_categories[:3] if count >= 2]
        
        # Identify weak areas (categories with few or no skills)
        weak_cats = [cat for cat, skills in profile.categorized_skills.items() 
                    if not skills and cat != "unknown"]
        analysis["weak_areas"] = weak_cats[:3]
        
        # Overall assessment
        if analysis["balance_score"] >= 0.7:
            analysis["overall_assessment"] = "Well-rounded professional with balanced skill set"
        elif analysis["breadth_score"] > analysis["depth_score"]:
            analysis["overall_assessment"] = "Jack of many trades, consider deepening expertise"
        elif analysis["depth_score"] > analysis["breadth_score"]:
            analysis["overall_assessment"] = "Deep specialist, consider broadening skill set"
        else:
            analysis["overall_assessment"] = "Developing professional with foundational skills"
        
        return analysis
