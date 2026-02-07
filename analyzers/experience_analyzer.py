"""
Experience Analyzer for Resume Intelligence Engine
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from config.config import EXPERIENCE_THRESHOLDS, SKILL_CATEGORIES


@dataclass
class ExperienceProfile:
    """Complete experience profile for a candidate"""
    total_years: float = 0
    career_level: str = ""
    domain_expertise: List[str] = field(default_factory=list)
    role_specialization: str = ""
    industry_history: List[str] = field(default_factory=list)
    company_types: List[str] = field(default_factory=list)
    leadership_experience: bool = False
    project_complexity: str = ""
    career_progression: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "total_years_experience": self.total_years,
            "career_level": self.career_level,
            "domain_expertise": self.domain_expertise,
            "role_specialization": self.role_specialization,
            "industry_history": self.industry_history,
            "company_types": self.company_types,
            "leadership_experience": self.leadership_experience,
            "project_complexity": self.project_complexity,
            "career_progression": self.career_progression
        }


class ExperienceAnalyzer:
    """Analyze work experience from resume data"""
    
    # Keywords for domain identification
    DOMAIN_KEYWORDS = {
        "technology": ["software", "web", "mobile", "cloud", "devops", "ai", "ml", "data", "software development"],
        "finance": ["banking", "fintech", "trading", "investment", "financial", "accounting"],
        "healthcare": ["health", "medical", "pharma", "clinical", "patient", "ehr", "hipaa"],
        "ecommerce": ["e-commerce", "retail", "online", "marketplace", "shopping"],
        "marketing": ["marketing", "digital", "seo", "content", "advertising", "brand"],
        "education": ["education", "e-learning", "courses", "training", "academic"],
        "consulting": ["consulting", "advisory", "strategy", "management"],
        "government": ["government", "public", "federal", "state", "policy"],
        "manufacturing": ["manufacturing", "production", "supply chain", "logistics"],
        "telecom": ["telecom", "networking", "wireless", "5g", "isp"],
    }
    
    # Keywords for role identification
    ROLE_KEYWORDS = {
        "developer": ["developer", "engineer", "programmer", "coder"],
        "designer": ["designer", "ui", "ux", "creative"],
        "analyst": ["analyst", "analytics", "insights"],
        "manager": ["manager", "lead", "head", "director", "vp"],
        "architect": ["architect", "principal", "staff"],
        "consultant": ["consultant", "advisor"],
        "researcher": ["researcher", "scientist", "research"],
        "administrator": ["administrator", "admin", "operations"],
    }
    
    # Company type indicators
    COMPANY_KEYWORDS = {
        "startup": ["startup", "seed", "series", "ycombinator"],
        "enterprise": ["enterprise", "fortune", "fortune 500", "multinational"],
        "mid_size": ["mid-size", "mid-market", "growing"],
        "agency": ["agency", "consulting firm"],
        "non_profit": ["non-profit", "nonprofit", "foundation", "ngo"],
        "government": ["government", "federal", "state", "city"],
        "academic": ["university", "college", "research institution"],
    }
    
    # Leadership indicators
    LEADERSHIP_KEYWORDS = [
        "led", "managed", "mentored", "directed", "headed", "oversaw",
        "supervised", "coordinated", "spearheaded", "championed", "built team"
    ]
    
    # Seniority indicators in role titles
    SENIOR_KEYWORDS = ["senior", "sr", "lead", "principal", "staff", "head", "director", "vp", "chief"]
    JUNIOR_KEYWORDS = ["junior", "jr", "associate", "entry", "intern", "trainee", "trainee"]
    
    def __init__(self):
        pass
    
    def analyze_experience(self, resume_data) -> ExperienceProfile:
        """Analyze all experience data from resume"""
        profile = ExperienceProfile()
        
        # Calculate total years
        profile.total_years = self._calculate_total_years(resume_data.experiences)
        
        # Determine career level based on experience
        profile.career_level = self._determine_career_level(profile.total_years)
        
        # Also check role titles for seniority indicators
        role_level = self._determine_level_from_roles(resume_data.experiences)
        if role_level != "mid":
            profile.career_level = role_level
        
        # Identify domain expertise
        profile.domain_expertise = self._identify_domains(resume_data)
        
        # Identify role specialization
        profile.role_specialization = self._identify_role(resume_data)
        
        # Industry history
        profile.industry_history = self._identify_industries(resume_data)
        
        # Company types
        profile.company_types = self._identify_company_types(resume_data)
        
        # Leadership experience
        profile.leadership_experience = self._check_leadership(resume_data)
        
        # Project complexity
        profile.project_complexity = self._assess_complexity(resume_data)
        
        # Career progression
        profile.career_progression = self._analyze_progression(resume_data)
        
        return profile
    
    def _calculate_total_years(self, experiences) -> float:
        """Calculate total years of experience"""
        if not experiences:
            return 0
        
        total_months = 0
        
        for exp in experiences:
            duration_months = self._parse_duration(exp.duration)
            if duration_months:
                total_months += duration_months
        
        return round(total_months / 12, 1)
    
    def _parse_duration(self, duration: str) -> Optional[int]:
        """Parse duration string to months"""
        if not duration:
            return None
        
        import re
        
        # Pattern for date ranges
        date_pattern = (
            r'(?i)(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{2,4}|'
            r'\d{1,2}/\d{2,4}|\d{4})\s*[-–—to]+\s*'
            r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{2,4}|'
            r'\d{1,2}/\d{2,4}|\d{4}|present|current|now)'
        )
        
        match = re.search(date_pattern, duration)
        if match:
            start_date = match.group(1)
            end_date = match.group(2)
            
            start_year = self._extract_year(start_date)
            end_year = self._extract_year(end_date)
            
            if start_year and end_year:
                months = (end_year - start_year) * 12
                return max(months, 0)
        
        # Try to find years directly
        year_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
        match = re.search(year_pattern, duration.lower())
        if match:
            return int(match.group(1)) * 12
        
        # Try to find months
        month_pattern = r'(\d+)\s*(?:months?|mos?)'
        match = re.search(month_pattern, duration.lower())
        if match:
            return int(match.group(1))
        
        # Look for year ranges like "2020 - 2023"
        year_range = r'(\d{4})\s*[-–—]\s*(\d{4})'
        match = re.search(year_range, duration)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            if end >= start:
                return (end - start) * 12
        
        return None
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string"""
        import re
        year_pattern = r'\b(19|20)\d{2}\b'
        match = re.search(year_pattern, date_str)
        if match:
            return int(match.group())
        
        # Handle present/current
        if any(word in date_str.lower() for word in ['present', 'current', 'now']):
            return datetime.now().year
        
        return None
    
    def _determine_career_level(self, total_years: float) -> str:
        """Determine career level based on experience"""
        if total_years < EXPERIENCE_THRESHOLDS["junior"]:
            return "fresher"
        elif total_years < EXPERIENCE_THRESHOLDS["mid"]:
            return "junior"
        elif total_years < EXPERIENCE_THRESHOLDS["senior"]:
            return "mid-level"
        elif total_years < EXPERIENCE_THRESHOLDS["lead"]:
            return "senior"
        elif total_years < EXPERIENCE_THRESHOLDS["architect"]:
            return "lead"
        else:
            return "architect"
    
    def _determine_level_from_roles(self, experiences) -> str:
        """Determine career level from role titles"""
        if not experiences:
            return "fresher"
        
        has_senior = False
        has_junior = False
        
        for exp in experiences:
            role_lower = exp.role.lower()
            
            for keyword in self.SENIOR_KEYWORDS:
                if keyword in role_lower:
                    has_senior = True
            
            for keyword in self.JUNIOR_KEYWORDS:
                if keyword in role_lower:
                    has_junior = True
        
        if has_senior and not has_junior:
            return "senior"
        elif has_junior and not has_senior:
            return "junior"
        
        return "mid"
    
    def _identify_domains(self, resume_data) -> List[str]:
        """Identify domains of expertise"""
        domains = set()
        text = self._get_full_text(resume_data).lower()
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    domains.add(domain)
                    break
        
        return list(domains)
    
    def _identify_role(self, resume_data) -> str:
        """Identify primary role/specialization"""
        text = self._get_full_text(resume_data).lower()
        
        # Check experience titles
        for exp in resume_data.experiences:
            exp_text = (exp.role + " " + exp.company + " " + exp.description).lower()
            
            for role_type, keywords in self.ROLE_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in exp_text:
                        return role_type
        
        # Check summary
        if resume_data.summary:
            summary_text = resume_data.summary.lower()
            for role_type, keywords in self.ROLE_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in summary_text:
                        return role_type
        
        return "general"
    
    def _identify_industries(self, resume_data) -> List[str]:
        """Identify industries worked in"""
        industries = set()
        text = self._get_full_text(resume_data).lower()
        
        for industry, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    industries.add(industry)
                    break
        
        return list(industries)
    
    def _identify_company_types(self, resume_data) -> List[str]:
        """Identify types of companies worked at"""
        company_types = set()
        
        for exp in resume_data.experiences:
            company_text = (exp.company + " " + exp.description).lower()
            
            for company_type, keywords in self.COMPANY_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in company_text:
                        company_types.add(company_type)
                        break
        
        return list(company_types)
    
    def _check_leadership(self, resume_data) -> bool:
        """Check if candidate has leadership experience"""
        for exp in resume_data.experiences:
            exp_text = (exp.role + " " + exp.description).lower()
            
            for keyword in self.LEADERSHIP_KEYWORDS:
                if keyword in exp_text:
                    return True
        
        return False
    
    def _assess_complexity(self, resume_data) -> str:
        """Assess complexity of projects worked on"""
        total_experience = len(resume_data.experiences)
        
        if not resume_data.experiences:
            return "unknown"
        
        # Check for complex technologies
        complex_techs = ["microservices", "distributed", "scalable", "enterprise", 
                         "high-traffic", "real-time", "machine learning", "ai"]
        
        complexity_score = 0
        for exp in resume_data.experiences:
            exp_text = exp.description.lower()
            for tech in complex_techs:
                if tech in exp_text:
                    complexity_score += 1
        
        # Also consider number of roles
        if total_experience >= 5:
            complexity_score += 2
        elif total_experience >= 3:
            complexity_score += 1
        
        if complexity_score >= 4:
            return "enterprise"
        elif complexity_score >= 2:
            return "intermediate"
        else:
            return "standard"
    
    def _analyze_progression(self, resume_data) -> List[Dict]:
        """Analyze career progression"""
        progression = []
        
        for i, exp in enumerate(resume_data.experiences):
            progression.append({
                "role": exp.role,
                "company": exp.company,
                "duration": exp.duration,
                "level": self._assess_role_level(exp.role),
                "sequence": i + 1
            })
        
        return progression
    
    def _assess_role_level(self, role: str) -> str:
        """Assess level of a specific role"""
        role_lower = role.lower()
        
        for keyword in self.SENIOR_KEYWORDS:
            if keyword in role_lower:
                return "senior"
        
        for keyword in self.JUNIOR_KEYWORDS:
            if keyword in role_lower:
                return "junior"
        
        return "mid"
    
    def _get_full_text(self, resume_data) -> str:
        """Get all text from resume data"""
        parts = []
        
        if resume_data.summary:
            parts.append(resume_data.summary)
        
        for exp in resume_data.experiences:
            parts.append(exp.role)
            parts.append(exp.company)
            parts.append(exp.description)
        
        for edu in resume_data.education:
            parts.append(edu.degree)
            parts.append(edu.institution)
        
        return " ".join(parts)
    
    def get_experience_summary(self, profile: ExperienceProfile) -> Dict:
        """Generate a summary of experience analysis"""
        return {
            "overview": f"{profile.total_years} years of experience as a {profile.role_specialization}",
            "level": profile.career_level.title(),
            "key_domains": ", ".join(profile.domain_expertise[:3]) if profile.domain_expertise else "Not specified",
            "leadership": "Yes" if profile.leadership_experience else "Developing",
            "complexity": profile.project_complexity.title(),
            "progression": "Progressive" if len(profile.career_progression) > 1 else "Early career",
            "recommendations": self._get_experience_recommendations(profile)
        }
    
    def _get_experience_recommendations(self, profile: ExperienceProfile) -> List[str]:
        """Get recommendations for experience improvement"""
        recommendations = []
        
        if profile.total_years < 2:
            recommendations.append("Focus on building foundational skills and completing projects")
        elif profile.total_years < 5:
            recommendations.append("Consider taking on more responsibilities or leadership roles")
        else:
            recommendations.append("Look for senior leadership or specialized positions")
        
        if not profile.leadership_experience:
            recommendations.append("Seek opportunities to mentor junior team members")
        
        if profile.domain_expertise and len(profile.domain_expertise) > 2:
            recommendations.append("Consider specializing further in your strongest domain")
        elif not profile.domain_expertise:
            recommendations.append("Identify and focus on a specific industry domain")
        
        return recommendations
