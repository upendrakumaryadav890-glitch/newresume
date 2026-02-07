"""
Job Recommender for Resume Intelligence Engine
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config.config import JOB_ROLES, SKILL_CATEGORIES
from utils.skill_normalizer import SkillNormalizer


@dataclass
class JobRecommendation:
    """Job recommendation data structure"""
    job_id: str
    title: str
    match_score: float
    why_fits: List[str]
    required_skills_vs_candidate: Dict
    missing_critical_skills: List[str]
    skill_match_percentage: float
    growth_potential: str
    demand_level: str
    
    def to_dict(self) -> Dict:
        return {
            "job_id": self.job_id,
            "title": self.title,
            "match_score": self.match_score,
            "why_fits": self.why_fits,
            "required_skills_vs_candidate": self.required_skills_vs_candidate,
            "missing_critical_skills": self.missing_critical_skills,
            "skill_match_percentage": self.skill_match_percentage,
            "growth_potential": self.growth_potential,
            "demand_level": self.demand_level
        }


class JobRecommender:
    """Recommend suitable job roles based on resume analysis"""
    
    # Job demand and growth data - including non-technical roles
    JOB_MARKET_DATA = {
        # Technical roles
        "software_engineer": {"demand": "high", "growth": "stable", "avg_salary": "$100k-$150k"},
        "data_scientist": {"demand": "very_high", "growth": "growing", "avg_salary": "$120k-$160k"},
        "frontend_developer": {"demand": "high", "growth": "stable", "avg_salary": "$90k-$130k"},
        "backend_developer": {"demand": "high", "growth": "stable", "avg_salary": "$100k-$140k"},
        "full_stack_developer": {"demand": "very_high", "growth": "growing", "avg_salary": "$110k-$150k"},
        "devops_engineer": {"demand": "high", "growth": "growing", "avg_salary": "$120k-$160k"},
        "machine_learning_engineer": {"demand": "very_high", "growth": "growing", "avg_salary": "$140k-$180k"},
        "product_manager": {"demand": "high", "growth": "stable", "avg_salary": "$120k-$170k"},
        "data_analyst": {"demand": "high", "growth": "stable", "avg_salary": "$70k-$100k"},
        "cloud_architect": {"demand": "high", "growth": "growing", "avg_salary": "$150k-$200k"},
        
        # Non-technical roles
        "project_manager": {"demand": "very_high", "growth": "stable", "avg_salary": "$90k-$140k"},
        "teacher": {"demand": "medium", "growth": "stable", "avg_salary": "$45k-$75k"},
        "sales_representative": {"demand": "high", "growth": "stable", "avg_salary": "$50k-$80k"},
        "account_manager": {"demand": "high", "growth": "stable", "avg_salary": "$70k-$110k"},
        "retail_associate": {"demand": "high", "growth": "stable", "avg_salary": "$25k-$40k"},
        "customer_service_rep": {"demand": "high", "growth": "stable", "avg_salary": "$30k-$50k"},
        "nurse": {"demand": "very_high", "growth": "growing", "avg_salary": "$70k-$120k"},
        "administrative_assistant": {"demand": "medium", "growth": "stable", "avg_salary": "$35k-$55k"},
        "accountant": {"demand": "high", "growth": "stable", "avg_salary": "$60k-$100k"},
        "hr_specialist": {"demand": "high", "growth": "stable", "avg_salary": "$55k-$90k"},
        "operations_manager": {"demand": "high", "growth": "stable", "avg_salary": "$80k-$130k"},
        "marketing_specialist": {"demand": "high", "growth": "growing", "avg_salary": "$55k-$95k"},
        "business_analyst": {"demand": "high", "growth": "stable", "avg_salary": "$75k-$115k"}
    }
    
    # Critical skills for each role
    CRITICAL_SKILLS = {
        # Technical roles
        "software_engineer": ["Python", "Java", "SQL", "Git"],
        "data_scientist": ["Python", "Machine Learning", "SQL", "Statistics"],
        "frontend_developer": ["JavaScript", "HTML", "CSS", "React"],
        "backend_developer": ["Python", "Java", "SQL", "REST API"],
        "full_stack_developer": ["JavaScript", "Python", "React", "Node.js"],
        "devops_engineer": ["Docker", "Kubernetes", "CI/CD", "AWS"],
        "machine_learning_engineer": ["Python", "TensorFlow", "PyTorch", "Machine Learning"],
        "product_manager": ["Communication", "Strategy", "Analytics"],
        "data_analyst": ["Python", "SQL", "Excel", "Tableau"],
        "cloud_architect": ["AWS", "Azure", "Docker", "Kubernetes"],
        
        # Non-technical roles
        "project_manager": ["Project Planning", "Risk Management", "Stakeholder Management", "Agile"],
        "teacher": ["Curriculum Development", "Lesson Planning", "Classroom Management", "Teaching"],
        "sales_representative": ["Sales", "Lead Generation", "Communication", "Negotiation"],
        "account_manager": ["Account Management", "Client Relations", "Communication", "Negotiation"],
        "retail_associate": ["Customer Service", "Retail", "Sales", "Point of Sale"],
        "customer_service_rep": ["Customer Service", "Communication", "Problem Solving", "Interpersonal Skills"],
        "nurse": ["Patient Care", "Clinical Skills", "Medical Terminology", "Healthcare Documentation"],
        "administrative_assistant": ["Microsoft Office", "Data Entry", "Calendar Management", "Communication"],
        "accountant": ["Financial Analysis", "Bookkeeping", "Excel", "Financial Reporting"],
        "hr_specialist": ["Recruiting", "Employee Relations", "Training and Development", "Communication"],
        "operations_manager": ["Operations Management", "Process Improvement", "Team Leadership", "Logistics"],
        "marketing_specialist": ["Digital Marketing", "Social Media Marketing", "Content Marketing", "Analytics"],
        "business_analyst": ["Analytical Skills", "Data Analysis", "Requirements Gathering", "Communication"]
    }
    
    def __init__(self):
        self.normalizer = SkillNormalizer()
    
    def recommend_jobs(self, skill_profile, experience_profile, 
                       top_n: int = 10) -> List[JobRecommendation]:
        """Recommend top job roles based on skills and experience"""
        recommendations = []
        
        candidate_skills_lower = set(s.lower() for s in skill_profile.all_skills)
        career_level = experience_profile.career_level
        total_years = experience_profile.total_years
        
        for job_id, job_data in JOB_ROLES.items():
            # Calculate match
            match_result = self._calculate_job_match(
                job_id, job_data, candidate_skills_lower, skill_profile
            )
            
            # Lower threshold to 20% for more job recommendations
            if match_result["skill_match_percentage"] >= 0.2:
                recommendation = self._create_recommendation(
                    job_id, job_data, match_result, experience_profile
                )
                recommendations.append(recommendation)
        
        # Sort by match score
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        
        return recommendations[:top_n]
    
    def _matches_experience_level(self, candidate_level: str, 
                                   required_level: str) -> bool:
        """Check if candidate experience matches job requirement"""
        level_order = ["fresher", "junior", "mid", "senior", "lead", "architect"]
        
        candidate_index = level_order.index(candidate_level) if candidate_level in level_order else 2
        required_index = level_order.index(required_level) if required_level in level_order else 2
        
        # Allow 1 level difference
        return abs(candidate_index - required_index) <= 1
    
    def _calculate_job_match(self, job_id: str, job_data: Dict,
                             candidate_skills_lower: set,
                             skill_profile) -> Dict:
        """Calculate how well candidate matches a job"""
        required_skills = [s.lower() for s in job_data["required_skills"]]
        critical_skills = [s.lower() for s in self.CRITICAL_SKILLS.get(job_id, [])]
        
        matched = candidate_skills_lower & set(required_skills)
        missing = set(required_skills) - candidate_skills_lower
        
        # Calculate match percentage
        skill_match = len(matched) / len(required_skills) if required_skills else 0
        
        # Critical skill bonus/penalty
        critical_matched = len(set(critical_skills) & matched)
        critical_missing = len(set(critical_skills) & missing)
        
        # Adjust score based on critical skills
        if critical_skills:
            critical_score = (critical_matched - critical_missing * 0.5) / len(critical_skills)
            skill_match = min(1.0, skill_match + critical_score * 0.3)
        
        # Boost for related skills
        related_boost = self._calculate_related_skill_boost(
            matched, required_skills, candidate_skills_lower
        )
        skill_match = min(1.0, skill_match + related_boost * 0.2)
        
        return {
            "skill_match_percentage": round(skill_match, 2),
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "critical_matched": critical_matched,
            "critical_missing": critical_missing,
            "related_skills_found": related_boost > 0
        }
    
    def _calculate_related_skill_boost(self, matched: set, required: set,
                                       candidate_skills: set) -> float:
        """Calculate bonus for having related skills"""
        related_mapping = {
            "python": ["django", "flask", "fastapi", "pandas", "numpy"],
            "java": ["spring", "kotlin", "scala"],
            "javascript": ["typescript", "react", "vue", "node"],
            "sql": ["postgresql", "mysql", "mongodb"],
            "aws": ["azure", "gcp", "docker"],
            "machine learning": ["deep learning", "nlp", "tensorflow"],
            "react": ["redux", "next.js", "gatsby"],
            "docker": ["kubernetes", "terraform", "jenkins"],
        }
        
        boost = 0
        for req_skill in required:
            req_lower = req_skill.lower()
            if req_lower in related_mapping:
                related = set(related_mapping[req_lower])
                if related & candidate_skills:
                    boost += 0.1
        
        return min(boost, 0.3)  # Cap boost
    
    def _create_recommendation(self, job_id: str, job_data: Dict,
                               match_result: Dict, experience_profile) -> JobRecommendation:
        """Create a job recommendation object"""
        market_data = self.JOB_MARKET_DATA.get(job_id, {"demand": "medium", "growth": "stable"})
        
        # Generate why it fits
        why_fits = self._generate_why_fits(job_data, match_result, experience_profile)
        
        # Identify missing critical skills
        critical_skills = [s for s in match_result["missing_skills"] 
                          if s.lower() in [c.lower() for c in self.CRITICAL_SKILLS.get(job_id, [])]]
        
        return JobRecommendation(
            job_id=job_id,
            title=job_data["title"],
            match_score=match_result["skill_match_percentage"],
            why_fits=why_fits,
            required_skills_vs_candidate={
                "required": job_data["required_skills"],
                "matched": match_result["matched_skills"],
                "missing": list(match_result["missing_skills"])
            },
            missing_critical_skills=critical_skills,
            skill_match_percentage=match_result["skill_match_percentage"] * 100,
            growth_potential=market_data["growth"],
            demand_level=market_data["demand"]
        )
    
    def _generate_why_fits(self, job_data: Dict, match_result: Dict,
                          experience_profile) -> List[str]:
        """Generate reasons why the job fits the candidate"""
        reasons = []
        
        # Skill match reason
        match_pct = match_result["skill_match_percentage"] * 100
        reasons.append(f"Matches {match_pct:.0f}% of required skills")
        
        # Domain expertise
        if experience_profile.domain_expertise:
            domain_reason = f"Has {experience_profile.domain_expertise[0].title()} domain experience"
            reasons.append(domain_reason)
        
        # Career level match
        reasons.append(f"Experience level aligns with {job_data['experience_level']} role")
        
        # Specific skill matches
        matched = match_result["matched_skills"]
        if len(matched) >= 2:
            reasons.append(f"Key skills: {', '.join(matched[:3])}")
        
        return reasons[:4]  # Limit to top 4 reasons
    
    def get_skill_gap_analysis(self, skill_profile, target_job_id: str) -> Dict:
        """Get detailed skill gap analysis for a target job"""
        if target_job_id not in JOB_ROLES:
            return {"error": f"Unknown job: {target_job_id}"}
        
        job_data = JOB_ROLES[target_job_id]
        required_skills = [s.lower() for s in job_data["required_skills"]]
        candidate_skills_lower = set(s.lower() for s in skill_profile.all_skills)
        
        matched = candidate_skills_lower & set(required_skills)
        missing = set(required_skills) - candidate_skills_lower
        
        # Categorize missing skills
        critical_missing = [s for s in missing 
                           if s.lower() in [c.lower() for c in self.CRITICAL_SKILLS.get(target_job_id, [])]]
        important_missing = [s for s in missing if s not in critical_missing]
        
        # Get learning resources for missing skills
        learning_resources = {}
        for skill in missing:
            learning_resources[skill.title()] = self._suggest_learning_path(skill)
        
        return {
            "target_role": job_data["title"],
            "match_percentage": round(len(matched) / len(required_skills), 2) * 100,
            "matched_skills": list(matched),
            "critical_missing_skills": critical_missing,
            "important_missing_skills": important_missing,
            "learning_resources": learning_resources,
            "time_to_job_ready": self._estimate_time_to_ready(missing, critical_missing)
        }
    
    def _suggest_learning_path(self, skill: str) -> Dict:
        """Suggest learning path for a skill"""
        skill_lower = skill.lower()
        
        learning_paths = {
            # Technical skills
            "python": {
                "resources": ["Official Python Tutorial", "Codecademy Python", "Real Python"],
                "level": "Beginner",
                "time_estimate": "2-4 weeks"
            },
            "javascript": {
                "resources": ["MDN Web Docs", "JavaScript.info", "FreeCodeCamp"],
                "level": "Intermediate",
                "time_estimate": "4-6 weeks"
            },
            "react": {
                "resources": ["Official React Docs", "React Tutorial", "Egghead.io"],
                "level": "Intermediate",
                "time_estimate": "3-4 weeks"
            },
            "machine learning": {
                "resources": ["Coursera ML Course", "Fast.ai", "Andrew Ng's ML"],
                "level": "Advanced",
                "time_estimate": "3-6 months"
            },
            "docker": {
                "resources": ["Docker Documentation", "Docker Mastery Course", "Katacoda"],
                "level": "Intermediate",
                "time_estimate": "2-3 weeks"
            },
            "kubernetes": {
                "resources": ["Kubernetes.io", "Kube Academy", "CKA Prep"],
                "level": "Advanced",
                "time_estimate": "4-6 weeks"
            },
            
            # Non-technical / Soft skills
            "project management": {
                "resources": ["PMP Certification", "CAPM Prep", "Project Management Fundamentals"],
                "level": "Intermediate",
                "time_estimate": "2-3 months"
            },
            "communication": {
                "resources": ["Dale Carnegie Course", "Toastmasters", "Business Communication Books"],
                "level": "Beginner",
                "time_estimate": "1-2 months"
            },
            "leadership": {
                "resources": ["Leadership Books", "Executive Coaching", "Leadership Workshops"],
                "level": "Advanced",
                "time_estimate": "3-6 months"
            },
            "sales": {
                "resources": ["Sales Training Programs", "Sandler Training", "SPIN Selling"],
                "level": "Beginner",
                "time_estimate": "1-2 months"
            },
            "customer service": {
                "resources": ["Customer Service Training", "Zendesk Academy", "Help Desk Certification"],
                "level": "Beginner",
                "time_estimate": "2-4 weeks"
            },
            "negotiation": {
                "resources": ["Never Split the Difference", "Harvard PON", "Negotiation Training"],
                "level": "Intermediate",
                "time_estimate": "1-2 months"
            },
            "teaching": {
                "resources": ["Teaching Certification", "Coursera Teaching", "Classroom Management Training"],
                "level": "Intermediate",
                "time_estimate": "3-6 months"
            },
            "curriculum development": {
                "resources": ["Instructional Design Courses", "ADDIE Model", "eLearning Industry"],
                "level": "Intermediate",
                "time_estimate": "2-3 months"
            },
            "data analysis": {
                "resources": ["Excel Advanced", "Tableau Training", "Google Data Analytics Certificate"],
                "level": "Beginner",
                "time_estimate": "2-3 months"
            },
            "digital marketing": {
                "resources": ["Google Digital Garage", "HubSpot Academy", "Facebook Blueprint"],
                "level": "Beginner",
                "time_estimate": "1-2 months"
            },
            "financial analysis": {
                "resources": ["Financial Modeling Courses", "CFA Preparation", "Wall Street Prep"],
                "level": "Intermediate",
                "time_estimate": "3-6 months"
            },
            "recruiting": {
                "resources": ["SHRM Certification", "LinkedIn Recruiter Training", "Recruiting Software Certifications"],
                "level": "Beginner",
                "time_estimate": "1-2 months"
            },
            "process improvement": {
                "resources": ["Six Sigma Certification", "Lean Training", "Process Excellence"],
                "level": "Intermediate",
                "time_estimate": "2-3 months"
            }
        }
        
        # Try exact match first, then partial
        if skill_lower in learning_paths:
            return learning_paths[skill_lower]
        
        for key, path in learning_paths.items():
            if key in skill_lower or skill_lower in key:
                return path
        
        return {
            "resources": ["Online courses", "Industry-specific training", "Professional certifications"],
            "level": "Intermediate",
            "time_estimate": "2-3 months"
        }
    
    def _estimate_time_to_ready(self, missing_skills: List[str],
                                critical_missing: List[str]) -> str:
        """Estimate time to become job-ready"""
        if not missing_skills:
            return "Ready now"
        
        # Base estimate on critical missing skills
        weeks_per_critical = 3
        weeks_per_other = 2
        
        total_weeks = len(critical_missing) * weeks_per_critical + \
                     (len(missing_skills) - len(critical_missing)) * weeks_per_other
        
        if total_weeks <= 2:
            return "1-2 weeks"
        elif total_weeks <= 6:
            return "1-2 months"
        elif total_weeks <= 12:
            return "2-3 months"
        else:
            return "3+ months"
    
    def get_career_roadmap(self, skill_profile, experience_profile,
                           target_job_id: str) -> Dict:
        """Generate a career roadmap to reach target job"""
        if target_job_id not in JOB_ROLES:
            return {"error": "Unknown job target"}
        
        job_data = JOB_ROLES[target_job_id]
        gap_analysis = self.get_skill_gap_analysis(skill_profile, target_job_id)
        
        roadmap = {
            "current_level": experience_profile.career_level,
            "target_role": job_data["title"],
            "target_level": job_data["experience_level"],
            "steps": []
        }
        
        # Step 1: Learn critical missing skills
        if gap_analysis.get("critical_missing_skills"):
            roadmap["steps"].append({
                "phase": "Immediate Priority",
                "actions": [f"Master {skill}" for skill in gap_analysis["critical_missing_skills"][:2]],
                "timeline": "1-2 months",
                "outcome": "Core skill gaps filled"
            })
        
        # Step 2: Build portfolio
        roadmap["steps"].append({
            "phase": "Portfolio Building",
            "actions": [
                "Build 2-3 projects showcasing target skills",
                "Contribute to open source",
                "Create case studies"
            ],
            "timeline": "1-2 months",
            "outcome": "Demonstrable experience"
        })
        
        # Step 3: Interview preparation
        roadmap["steps"].append({
            "phase": "Interview Prep",
            "actions": [
                "Practice coding interviews",
                "Prepare system design",
                "Research target companies"
            ],
            "timeline": "2-4 weeks",
            "outcome": "Interview-ready"
        })
        
        return roadmap
