"""
Base Parser for Resume Intelligence Engine
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class Experience:
    """Data class for work experience"""
    role: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""
    achievements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "company": self.company,
            "duration": self.duration,
            "description": self.description,
            "achievements": self.achievements
        }


@dataclass
class Education:
    """Data class for education"""
    degree: str = ""
    institution: str = ""
    year: str = ""
    gpa: Optional[str] = None
    details: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "degree": self.degree,
            "institution": self.institution,
            "year": self.year,
            "gpa": self.gpa,
            "details": self.details
        }


@dataclass
class Certification:
    """Data class for certifications"""
    name: str = ""
    issuer: str = ""
    date: str = ""
    expiry: Optional[str] = None
    credential_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "issuer": self.issuer,
            "date": self.date,
            "expiry": self.expiry,
            "credential_id": self.credential_id
        }


@dataclass
class Project:
    """Data class for projects"""
    name: str = ""
    description: str = ""
    technologies: List[str] = field(default_factory=list)
    url: Optional[str] = None
    role: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "technologies": self.technologies,
            "url": self.url,
            "role": self.role
        }


@dataclass
class ResumeData:
    """Complete resume data structure"""
    # Basic info
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    summary: str = ""
    
    # Skills
    technical_skills: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    
    # Experience
    experiences: List[Experience] = field(default_factory=list)
    
    # Education
    education: List[Education] = field(default_factory=list)
    
    # Certifications
    certifications: List[Certification] = field(default_factory=list)
    
    # Projects
    projects: List[Project] = field(default_factory=list)
    
    # Additional info
    languages: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    
    # Metadata
    raw_text: str = ""
    file_path: Optional[Path] = None
    file_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
            "github": self.github,
            "website": self.website,
            "summary": self.summary,
            "technical_skills": self.technical_skills,
            "soft_skills": self.soft_skills,
            "tools": self.tools,
            "experiences": [exp.to_dict() for exp in self.experiences],
            "education": [edu.to_dict() for edu in self.education],
            "certifications": [cert.to_dict() for cert in self.certifications],
            "projects": [proj.to_dict() for proj in self.projects],
            "languages": self.languages,
            "interests": self.interests,
            "raw_text_length": len(self.raw_text),
            "file_type": self.file_type
        }


class BaseParser(ABC):
    """Abstract base class for resume parsers"""
    
    SUPPORTED_FORMATS = []
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.raw_text = ""
        
    @abstractmethod
    def parse(self) -> ResumeData:
        """Parse resume file and return structured data"""
        pass
    
    @abstractmethod
    def _extract_text(self) -> str:
        """Extract raw text from file"""
        pass
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Keep newlines for section detection, just normalize other whitespace
        import re
        # Replace multiple spaces/tabs with single space, but preserve newlines
        text = re.sub(r'[ \t]+', ' ', text)
        # Remove special characters but keep basic punctuation and newlines
        text = re.sub(r'[^\w\s.,@\-\n]', '', text)
        return text.strip()
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from text"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        import re
        # Match various phone formats
        phone_patterns = [
            r'\+?1?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',
            r'\+?\d{1,3}[\s.-]?\d{2,4}[\s.-]?\d{2,4}[\s.-]?\d{2,4}',
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0].strip()
        return ""
    
    def _extract_links(self, text: str) -> Dict[str, str]:
        """Extract LinkedIn, GitHub, and other links"""
        import re
        links = {}
        
        # LinkedIn
        linkedin = re.search(r'linkedin\.com/in/[\w-]+', text)
        if linkedin:
            links["linkedin"] = f"https://{linkedin.group()}"
        
        # GitHub
        github = re.search(r'github\.com/[\w-]+', text)
        if github:
            links["github"] = f"https://{github.group()}"
        
        # Website
        website = re.search(r'https?://(?:www\.)?[\w-]+\.[\w./-]+', text)
        if website:
            url = website.group()
            if 'linkedin' not in url and 'github' not in url:
                links["website"] = url
        
        return links


class ResumeParser:
    """Factory class for resume parsing"""
    
    _parsers = {}
    
    @classmethod
    def register_parser(cls, file_type: str, parser_class: type):
        """Register a parser for a specific file type"""
        cls._parsers[file_type.lower()] = parser_class
    
    @classmethod
    def get_parser(cls, file_path: Path) -> BaseParser:
        """Get appropriate parser for file type"""
        suffix = file_path.suffix.lower()
        
        # Remove the dot from suffix
        file_type = suffix[1:] if suffix.startswith('.') else suffix
        
        if file_type not in cls._parsers:
            raise ValueError(f"No parser available for file type: {file_type}")
        
        return cls._parsers[file_type](file_path)
    
    @classmethod
    def parse(cls, file_path: Path) -> ResumeData:
        """Parse resume file using appropriate parser"""
        parser = cls.get_parser(file_path)
        return parser.parse()
    
    @classmethod
    def parse_text(cls, text: str, file_type: str = "txt") -> ResumeData:
        """Parse resume from text string"""
        # Create a temporary parser that works with text
        if file_type.lower() == "txt":
            # Create a minimal parser-like object
            from .txt_parser import TxtParser
            
            class TextParser:
                def __init__(self, text):
                    self.raw_text = text
                    self.file_path = None
                
                def parse(self) -> ResumeData:
                    """Parse text directly"""
                    from .base_parser import ResumeData, Experience, Education, Certification, Project
                    from config.config import SKILL_CATEGORIES
                    import re
                    
                    resume_data = ResumeData()
                    resume_data.raw_text = self.raw_text
                    resume_data.file_path = None
                    resume_data.file_type = "txt"
                    
                    # Extract email
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    emails = re.findall(email_pattern, self.raw_text)
                    resume_data.email = emails[0] if emails else ""
                    
                    # Extract phone
                    phone_pattern = r'\+?1?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
                    phones = re.findall(phone_pattern, self.raw_text)
                    resume_data.phone = phones[0] if phones else ""
                    
                    # Extract name
                    lines = self.raw_text.split('\n')
                    for line in lines[:10]:
                        line = line.strip()
                        if line and len(line.split()) <= 4:
                            if '@' not in line and not any(c.isdigit() for c in line):
                                skip_words = ['summary', 'experience', 'education', 'skills', 
                                             'certifications', 'projects', 'contact', 'email',
                                             'phone', 'linkedin', 'github', 'resume', 'cv']
                                if line.lower() not in skip_words:
                                    resume_data.full_name = line
                                    break
                    
                    # Extract skills
                    all_known_skills = []
                    for category in SKILL_CATEGORIES.values():
                        all_known_skills.extend([s.lower() for s in category])
                    
                    found_skills = []
                    text_lower = self.raw_text.lower()
                    
                    for skill in all_known_skills:
                        if skill in text_lower:
                            for category_skills in SKILL_CATEGORIES.values():
                                for original_skill in category_skills:
                                    if original_skill.lower() == skill and original_skill not in found_skills:
                                        found_skills.append(original_skill)
                                        break
                    
                    resume_data.technical_skills = list(set(found_skills))
                    
                    # Extract experiences
                    experience_keywords = ['experience', 'work history', 'professional experience', 
                                           'employment history', 'work experience']
                    education_keywords = ['education', 'academic', 'degree', 'university', 'college']
                    
                    lines = self.raw_text.split('\n')
                    in_experience_section = False
                    current_experience = None
                    experiences = []
                    
                    for i, line in enumerate(lines):
                        line_lower = line.lower().strip()
                        
                        # Check if we're entering an experience section
                        if any(kw in line_lower for kw in experience_keywords):
                            in_experience_section = True
                            continue
                        
                        # Check if we're entering a different section
                        if in_experience_section:
                            if any(kw in line_lower for kw in education_keywords):
                                in_experience_section = False
                                continue
                            
                            # Skip empty lines and section headers
                            if not line.strip():
                                continue
                            if len(line.strip()) < 5:
                                continue
                            
                            # Check if this looks like a role title
                            role_patterns = [
                                r'^(senior|junior|lead|principal|staff)?\s*(software|data|web|devops|cloud|frontend|backend|fullstack|mobile)?\s*(engineer|developer|analyst|designer|architect|manager|director|specialist|consultant)',
                                r'^(software|data|web|devops|cloud)?\s*(engineer|developer|analyst)',
                                r'^(intern|trainee|associate)'
                            ]
                            
                            is_role = False
                            for pattern in role_patterns:
                                if re.search(pattern, line_lower):
                                    is_role = True
                                    break
                            
                            # Check if this looks like a company
                            company_patterns = [
                                r'(inc|llc|ltd|corp|corporation|company|co\.)',
                                r'(technologies|tech|solutions|services|systems|software)',
                                r'(google|amazon|microsoft|apple|facebook|netflix|meta|ibm|oracle)',
                                r'(startup|ventures|group|partners|agency|studio)'
                            ]
                            
                            is_company = False
                            for pattern in company_patterns:
                                if re.search(pattern, line_lower):
                                    is_company = True
                                    break
                            
                            # Check for date pattern
                            date_pattern = r'\d{4}\s*(to|-|–)\s*(present|current|\d{4})'
                            has_dates = re.search(date_pattern, line_lower)
                            
                            if is_role or is_company or has_dates:
                                if current_experience:
                                    experiences.append(current_experience)
                                
                                # Create new experience
                                current_experience = {
                                    'role': '',
                                    'company': '',
                                    'duration': '',
                                    'description': []
                                }
                                
                                if has_dates:
                                    match = re.search(date_pattern, line_lower)
                                    if match:
                                        current_experience['duration'] = match.group(0)
                                        # Remove dates from line
                                        line = re.sub(date_pattern, '', line).strip()
                                
                                if is_role:
                                    current_experience['role'] = line.strip()
                                elif is_company:
                                    current_experience['company'] = line.strip()
                                else:
                                    current_experience['description'].append(line.strip())
                            elif current_experience and line.strip():
                                # This is likely a description line
                                current_experience['description'].append(line.strip())
                    
                    # Add the last experience
                    if current_experience:
                        experiences.append(current_experience)
                    
                    # Convert to Experience objects
                    from .base_parser import Experience
                    for exp in experiences:
                        if exp['role'] or exp['description']:
                            experience = Experience(
                                role=exp['role'],
                                company=exp['company'],
                                duration=exp['duration'],
                                description=' '.join(exp['description'])
                            )
                            resume_data.experiences.append(experience)
                    
                    # Extract education
                    education_keywords = ['education', 'academic', 'degree', 'university', 'college', 'school']
                    in_education_section = False
                    
                    for line in lines:
                        line_lower = line.lower().strip()
                        
                        if any(kw in line_lower for kw in education_keywords):
                            in_education_section = True
                            continue
                        
                        if in_education_section:
                            # Check if we hit a different section
                            if any(kw in line_lower for kw in experience_keywords):
                                in_education_section = False
                                continue
                            
                            if not line.strip() or len(line.strip()) < 5:
                                continue
                            
                            # Look for degree patterns
                            degree_patterns = [
                                r"(bachelor|master|phd|bs|ba|ms|ma|mba|phd|associate|b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|m\.?b\.?a\.?|ph\.?d\.?)",
                                r"(b\.?tech|m\.?tech|b\.?e\.?|m\.?e\.?)",
                                r"(computer science|engineering|mathematics|physics|information technology|software engineering|data science|ai|machine learning)"
                            ]
                            
                            has_degree = any(re.search(p, line_lower) for p in degree_patterns)
                            
                            if has_degree or 'university' in line_lower or 'college' in line_lower or 'institute' in line_lower:
                                from .base_parser import Education
                                
                                # Extract degree
                                degree = ''
                                for pattern in degree_patterns:
                                    match = re.search(pattern, line_lower, re.IGNORECASE)
                                    if match:
                                        degree = match.group(0)
                                        break
                                
                                # Extract university
                                university = line
                                # Clean up
                                if degree:
                                    university = re.sub(degree, '', university, flags=re.IGNORECASE).strip()
                                
                                education = Education(
                                    degree=degree,
                                    institution=university,
                                    year=''
                                )
                                resume_data.education.append(education)
                    
                    return resume_data
            
            parser = TextParser(text)
            return parser.parse()
        raise ValueError(f"Cannot parse text format: {file_type}")


# Register built-in parsers
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .txt_parser import TxtParser

ResumeParser.register_parser("pdf", PDFParser)
ResumeParser.register_parser("docx", DOCXParser)
ResumeParser.register_parser("txt", TxtParser)
