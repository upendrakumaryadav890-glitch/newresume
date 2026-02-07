"""
PDF Parser for Resume Intelligence Engine
"""
from pathlib import Path
from .base_parser import ResumeData, Experience, Education, Certification, Project

# Try multiple PDF libraries
PDF_PARSER = None
try:
    from PyPDF2 import PdfReader
    PDF_PARSER = "pypdf2"
except ImportError:
    pass

try:
    import pdfplumber
    PDF_PARSER = "pdfplumber"
except ImportError:
    pass


class PDFParser:
    """Parser for PDF resume files"""
    
    SUPPORTED_FORMATS = ["pdf"]
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.raw_text = ""
    
    def parse(self) -> ResumeData:
        """Parse PDF resume and extract all relevant information"""
        self.raw_text = self._extract_text()
        resume_data = ResumeData()
        
        resume_data.raw_text = self.raw_text
        resume_data.file_path = self.file_path
        resume_data.file_type = "pdf"
        
        # Check if text was extracted
        if not self.raw_text.strip():
            # Return minimal data with helpful message
            resume_data.summary = "Note: This PDF appears to be image-based or scanned. Text extraction was not possible. Please try uploading a text-based PDF or copy-paste your resume content using the Quick Analysis feature."
            return resume_data
        
        # Extract basic information
        resume_data.email = self._extract_email(self.raw_text)
        resume_data.phone = self._extract_phone(self.raw_text)
        links = self._extract_links(self.raw_text)
        resume_data.linkedin = links.get("linkedin")
        resume_data.github = links.get("github")
        resume_data.website = links.get("website")
        
        # Extract name
        resume_data.full_name = self._extract_name(self.raw_text)
        
        # Extract sections
        resume_data.summary = self._extract_summary(self.raw_text)
        resume_data.technical_skills = self._extract_skills(self.raw_text)
        resume_data.experiences = self._extract_experiences(self.raw_text)
        resume_data.education = self._extract_education(self.raw_text)
        resume_data.certifications = self._extract_certifications(self.raw_text)
        resume_data.projects = self._extract_projects(self.raw_text)
        
        return resume_data
    
    def _extract_text(self) -> str:
        """Extract text from PDF file using available library"""
        if PDF_PARSER == "pdfplumber":
            return self._extract_with_pdfplumber()
        elif PDF_PARSER == "pypdf2":
            return self._extract_with_pypdf2()
        else:
            # Try pypdf2 as fallback
            try:
                return self._extract_with_pypdf2()
            except:
                return ""
    
    def _extract_with_pdfplumber(self) -> str:
        """Extract text using pdfplumber"""
        import pdfplumber
        text_parts = []
        with pdfplumber.open(str(self.file_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return self._clean_text(" ".join(text_parts))
    
    def _extract_with_pypdf2(self) -> str:
        """Extract text using PyPDF2"""
        from PyPDF2 import PdfReader
        text_parts = []
        reader = PdfReader(str(self.file_path))
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return self._clean_text(" ".join(text_parts))
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        import re
        # Replace multiple spaces/tabs with single space
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
        phone_patterns = [
            r'\+?1?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',
            r'\+?\d{1,3}[\s.-]?\d{2,4}[\s.-]?\d{2,4}[\s.-]?\d{2,4}',
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0].strip()
        return ""
    
    def _extract_links(self, text: str) -> dict:
        """Extract LinkedIn, GitHub, and other links"""
        import re
        links = {}
        
        linkedin = re.search(r'linkedin\.com/in/[\w-]+', text)
        if linkedin:
            links["linkedin"] = f"https://{linkedin.group()}"
        
        github = re.search(r'github\.com/[\w-]+', text)
        if github:
            links["github"] = f"https://{github.group()}"
        
        return links
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name from text"""
        lines = text.split('\n')
        if lines:
            for i, line in enumerate(lines[:10]):
                line = line.strip()
                if line and len(line.split()) <= 4:
                    if '@' not in line and not any(c.isdigit() for c in line):
                        skip_words = ['summary', 'experience', 'education', 'skills', 
                                     'certifications', 'projects', 'contact', 'email',
                                     'phone', 'linkedin', 'github', 'resume', 'cv']
                        if line.lower() not in skip_words:
                            return line
        return ""
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        import re
        
        # Look for summary section with various patterns
        patterns = [
            r'(?i)professional\s*summary[:\s]*(.+?)(?=\n\n|\nexperience|\neducation|\nskills|\ncertifications|\nprojects|$)',
            r'(?i)summary[:\s]*(.+?)(?=\n\n|\nexperience|\neducation|\nskills|\ncertifications|\nprojects|$)',
            r'(?i)profile[:\s]*(.+?)(?=\n\n|\nexperience|\neducation|\nskills|\ncertifications|\nprojects|$)',
            r'(?i)objective[:\s]*(.+?)(?=\n\n|\nexperience|\neducation|\nskills|\ncertifications|\nprojects|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                summary = match.group(1).strip()
                summary = re.sub(r'\s+', ' ', summary)
                return summary[:500]
        return ""
    
    def _extract_skills(self, text: str) -> list:
        """Extract skills from resume text"""
        from config.config import SKILL_CATEGORIES
        
        all_known_skills = []
        for category in SKILL_CATEGORIES.values():
            all_known_skills.extend([s.lower() for s in category])
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in all_known_skills:
            if skill in text_lower:
                for category_skills in SKILL_CATEGORIES.values():
                    for original_skill in category_skills:
                        if original_skill.lower() == skill and original_skill not in found_skills:
                            found_skills.append(original_skill)
                            break
        
        return list(set(found_skills))
    
    def _extract_experiences(self, text: str) -> list:
        """Extract work experience entries"""
        experiences = []
        
        exp_section = self._extract_section(text, 'experience')
        
        if exp_section:
            import re
            
            # Simpler date pattern that won't cause regex errors
            date_pattern = r'((?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|\d{4})\s*[-–—to]+\s*((?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|\d{4}|Present|Current|Now)'
            
            try:
                entries = re.split(date_pattern, exp_section, flags=re.IGNORECASE)
                
                current_entry = {}
                for i, entry in enumerate(entries):
                    entry = entry.strip()
                    if not entry:
                        continue
                    
                    # Check if this is a date part
                    date_match = re.match(
                        r'^(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|\d{4}',
                        entry,
                        re.IGNORECASE
                    )
                    
                    if date_match and i > 0:
                        # This is a date, save the previous entry
                        if current_entry.get('role'):
                            exp = Experience(
                                role=current_entry.get('role', ''),
                                company=current_entry.get('company', ''),
                                duration=current_entry.get('duration', ''),
                                description=current_entry.get('description', '')[:500]
                            )
                            experiences.append(exp)
                        current_entry = {'duration': entry}
                    elif '-' in entry and not entry.startswith('-') and not current_entry.get('role'):
                        # This might be a role - company line
                        parts = re.split(r'\s*-\s*', entry, 1)
                        if len(parts) == 2:
                            current_entry['role'] = parts[0].strip()
                            current_entry['company'] = parts[1].strip()
                        else:
                            current_entry['role'] = entry
                    elif entry.startswith('-') or entry.startswith('*'):
                        # This is a bullet point
                        if 'description' not in current_entry:
                            current_entry['description'] = ''
                        current_entry['description'] += entry + ' '
                
                # Don't forget the last entry
                if current_entry.get('role'):
                    exp = Experience(
                        role=current_entry.get('role', ''),
                        company=current_entry.get('company', ''),
                        duration=current_entry.get('duration', ''),
                        description=current_entry.get('description', '')[:500]
                    )
                    experiences.append(exp)
            except re.error:
                pass
        
        return experiences
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the resume"""
        import re
        
        # Case-insensitive section extraction
        pattern = rf'(?i)(?:^|\n)\s*{section_name}\s*[:\-]?\s*(.+?)(?=\n\n|\n(?:[A-Z]|\d|\*))'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_education(self, text: str) -> list:
        """Extract education entries"""
        education = []
        
        edu_section = self._extract_section(text, 'education')
        
        if edu_section:
            import re
            
            degree_patterns = [
                r"(bachelor['s]?|master['s]?|ph\.?d\.?|mba|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|associate['s]?)",
            ]
            
            lines = edu_section.split('\n')
            current_entry = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                for pattern in degree_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        degree = match.group(1) if match.group(1) else match.group(0)
                        institution = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                        institution = re.sub(r'^[\s,\-]+|[\s,\-]+$', '', institution)
                        
                        year_match = re.search(r'\b(19|20)\d{2}\b', line)
                        year = year_match.group() if year_match else ''
                        
                        edu = Education(
                            degree=degree.title(),
                            institution=institution.title(),
                            year=year,
                            details=line
                        )
                        education.append(edu)
                        break
        
        return education
    
    def _extract_certifications(self, text: str) -> list:
        """Extract certification entries"""
        certifications = []
        
        cert_section = self._extract_section(text, 'certifications')
        
        if cert_section:
            lines = cert_section.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('-') or line.startswith('*'):
                    continue
                
                cert = Certification(
                    name=line,
                    issuer='',
                    date=''
                )
                certifications.append(cert)
        
        return certifications
    
    def _extract_projects(self, text: str) -> list:
        """Extract project entries"""
        projects = []
        
        project_section = self._extract_section(text, 'projects')
        
        if project_section:
            import re
            lines = project_section.split('\n')
            current_project = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if not current_project.get("name"):
                    if not line.startswith(('•', '-', '*')):
                        current_project["name"] = line
                        continue
                
                if current_project.get("name"):
                    if "description" not in current_project:
                        current_project["description"] = ""
                    current_project["description"] += line + " "
                    
                    if len(current_project.get("description", "")) > 20:
                        proj = Project(
                            name=current_project.get("name", ""),
                            description=current_project.get("description", "").strip(),
                            technologies=[]
                        )
                        projects.append(proj)
                        current_project = {}
        
        return projects
