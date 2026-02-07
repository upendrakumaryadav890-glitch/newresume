"""
TXT Parser for Resume Intelligence Engine
"""
from pathlib import Path
from .base_parser import BaseParser, ResumeData, Experience, Education, Certification, Project


class TxtParser(BaseParser):
    """Parser for plain text resume files"""
    
    SUPPORTED_FORMATS = ["txt"]
    
    def parse(self) -> ResumeData:
        """Parse TXT resume and extract all relevant information"""
        self.raw_text = self._extract_text()
        resume_data = ResumeData()
        
        resume_data.raw_text = self.raw_text
        resume_data.file_path = self.file_path
        resume_data.file_type = "txt"
        
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
        
        # Extract experiences with improved parsing
        resume_data.experiences = self._extract_experiences(self.raw_text)
        
        resume_data.education = self._extract_education(self.raw_text)
        resume_data.certifications = self._extract_certifications(self.raw_text)
        resume_data.projects = self._extract_projects(self.raw_text)
        
        return resume_data
    
    def _extract_text(self) -> str:
        """Extract text from TXT file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self._clean_text(text)
        except Exception as e:
            raise ValueError(f"Error reading TXT file: {str(e)}")
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name from text"""
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            return ""
        
        for i, line in enumerate(lines[:5]):
            # Skip lines that look like contact info
            if '@' in line or 'email' in line.lower():
                continue
            if any(c.isdigit() for c in line):
                continue
            
            # Skip section headers
            skip_words = ['summary', 'experience', 'education', 'skills', 
                         'certifications', 'projects', 'contact', 'resume', 'curriculum']
            if line.lower() in skip_words:
                continue
            
            # Name should have 2-4 words
            words = line.split()
            if 2 <= len(words) <= 4:
                # Each word should start with uppercase
                if all(w[0].isupper() for w in words if w):
                    return line
        
        return lines[0] if lines else ""
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        import re
        
        # Look for summary section
        patterns = [
            r'(?i)professional\s*summary[:\s]*(.+?)(?=\n(?:experience|education|skills|certifications|projects)|$)',
            r'(?i)summary[:\s]*(.+?)(?=\n(?:experience|education|skills|certifications|projects)|$)',
            r'(?i)profile[:\s]*(.+?)(?=\n(?:experience|education|skills|certifications|projects)|$)',
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
        import re
        experiences = []
        
        # Find experience section
        lines = text.split('\n')
        
        in_exp_section = False
        exp_lines = []
        
        section_headers = ['experience', 'employment', 'work history', 'professional experience']
        other_sections = ['education', 'skills', 'certifications', 'projects', 'awards', 'publications']
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Check if we're starting a new section
            if any(header in line_lower for header in section_headers) and ':' not in line and len(line) < 30:
                in_exp_section = True
                exp_lines = []
                continue
            
            # Check if we've hit another section
            if in_exp_section:
                if any(header in line_lower for header in other_sections) and ':' not in line and len(line) < 30:
                    break
                exp_lines.append(line)
        
        # Parse experience entries from exp_lines
        if exp_lines:
            current_exp = {}
            pending_role = None
            
            for line in exp_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for various date patterns
                # Pattern 1: "Jan 2020 - Present" or "2020 - 2023"
                date_pattern1 = r'^(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|\d{4})\s*[-–—to]+\s*(?:present|current|\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4})'
                date_match1 = re.match(date_pattern1, line, re.I)
                
                # Pattern 2: "2020 - 2023" (year only)
                date_pattern2 = r'^(\d{4})\s*[-–—to]+\s*(\d{4}|present|current)'
                date_match2 = re.match(date_pattern2, line)
                
                # Pattern 3: Dates inline with role like "Software Engineer - Jan 2020 - Present"
                inline_date_pattern = r'^(.+?)\s*[-–—]\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}|\d{4})\s*[-–—to]+\s*(?:present|current|\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4})'
                inline_date_match = re.match(inline_date_pattern, line, re.I)
                
                # Check if line is a bullet point
                is_bullet = line.startswith('-') or line.startswith('*') or line.startswith('•')
                
                # Role/company pattern (role - company) - simpler pattern
                role_pattern = r'^(.+?)\s*[-–—]\s*(.+)$'
                role_match = re.match(role_pattern, line)
                
                if inline_date_match:
                    # This line has role and dates inline
                    if current_exp.get('role') and current_exp.get('duration'):
                        exp = Experience(
                            role=current_exp.get('role', ''),
                            company=current_exp.get('company', ''),
                            duration=current_exp.get('duration', ''),
                            description=current_exp.get('description', '')[:500]
                        )
                        experiences.append(exp)
                    
                    current_exp = {
                        'role': inline_date_match.group(1).strip(),
                        'duration': line,
                        'description': ''
                    }
                    
                elif date_match1 or date_match2:
                    # This is a duration line
                    current_exp['duration'] = line
                    
                    # If we have a pending role from previous line, use it
                    if pending_role:
                        current_exp['role'] = pending_role['role']
                        current_exp['company'] = pending_role['company']
                        pending_role = None
                        
                elif role_match and not is_bullet and not date_match1 and not date_match2:
                    # This is a role/company line
                    # First, save any previous entry if we have both role and duration
                    if current_exp.get('role') and current_exp.get('duration'):
                        exp = Experience(
                            role=current_exp.get('role', ''),
                            company=current_exp.get('company', ''),
                            duration=current_exp.get('duration', ''),
                            description=current_exp.get('description', '')[:500]
                        )
                        experiences.append(exp)
                        current_exp = {'description': ''}
                    
                    # Store this role but wait for duration
                    pending_role = {
                        'role': role_match.group(1).strip(),
                        'company': role_match.group(2).strip()
                    }
                elif is_bullet:
                    # This is a bullet point
                    if 'description' not in current_exp:
                        current_exp['description'] = ''
                    current_exp['description'] += line + ' '
                else:
                    # Other line - could be continuing description or something else
                    if current_exp.get('role') and current_exp.get('duration'):
                        if 'description' not in current_exp:
                            current_exp['description'] = ''
                        current_exp['description'] += line + ' '
                    elif not current_exp.get('role'):
                        # Treat as role if no role yet
                        current_exp['role'] = line
            
            # Don't forget the last entry
            if current_exp.get('role'):
                exp = Experience(
                    role=current_exp.get('role', ''),
                    company=current_exp.get('company', ''),
                    duration=current_exp.get('duration', ''),
                    description=current_exp.get('description', '')[:500]
                )
                experiences.append(exp)
        
        return experiences
    
    def _extract_education(self, text: str) -> list:
        """Extract education entries"""
        import re
        education = []
        
        lines = text.split('\n')
        
        in_edu_section = False
        edu_lines = []
        
        section_headers = ['education', 'academic', 'qualifications']
        other_sections = ['experience', 'skills', 'certifications', 'projects', 'awards']
        
        for line in lines:
            line_lower = line.strip().lower()
            
            if any(header in line_lower for header in section_headers) and ':' not in line and len(line) < 25:
                in_edu_section = True
                edu_lines = []
                continue
            
            if in_edu_section:
                if any(header in line_lower for header in other_sections) and ':' not in line and len(line) < 25:
                    break
                edu_lines.append(line)
        
        # Parse education
        current_edu = {}
        for line in edu_lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for degree
            degree_patterns = [
                r'(bachelor|master|ph\.?d|mba|b\.?s|m\.?s|b\.?a|m\.?a)',
                r'(associate|diploma|certificate)'
            ]
            
            found_degree = False
            for pattern in degree_patterns:
                match = re.search(pattern, line, re.I)
                if match:
                    degree = match.group(0).title()
                    institution = re.sub(pattern, '', line, flags=re.I).strip()
                    institution = re.sub(r'^[\s,\-]+|[\s,\-]+$', '', institution)
                    
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    year = year_match.group() if year_match else ''
                    
                    edu = Education(
                        degree=degree,
                        institution=institution,
                        year=year,
                        details=line
                    )
                    education.append(edu)
                    found_degree = True
                    break
        
        return education
    
    def _extract_certifications(self, text: str) -> list:
        """Extract certification entries"""
        certifications = []
        
        lines = text.split('\n')
        
        in_cert_section = False
        cert_lines = []
        
        section_headers = ['certifications', 'certificates', 'licenses']
        other_sections = ['experience', 'education', 'skills', 'projects']
        
        for line in lines:
            line_lower = line.strip().lower()
            
            if any(header in line_lower for header in section_headers) and ':' not in line and len(line) < 25:
                in_cert_section = True
                cert_lines = []
                continue
            
            if in_cert_section:
                if any(header in line_lower for header in other_sections) and ':' not in line and len(line) < 25:
                    break
                cert_lines.append(line)
        
        # Parse certifications
        for line in cert_lines:
            line = line.strip()
            if not line or line.startswith('-') or line.startswith('•'):
                continue
            
            cert = Certification(
                name=line.lstrip('-• ').split('(')[0].strip(),
                issuer='',
                date=''
            )
            certifications.append(cert)
        
        return certifications
    
    def _extract_projects(self, text: str) -> list:
        """Extract project entries"""
        import re
        projects = []
        
        lines = text.split('\n')
        
        in_proj_section = False
        proj_lines = []
        
        section_headers = ['projects', 'portfolio', 'personal projects']
        other_sections = ['experience', 'education', 'skills', 'certifications']
        
        for line in lines:
            line_lower = line.strip().lower()
            
            if any(header in line_lower for header in section_headers) and ':' not in line and len(line) < 25:
                in_proj_section = True
                proj_lines = []
                continue
            
            if in_proj_section:
                if any(header in line_lower for header in other_sections) and ':' not in line and len(line) < 25:
                    break
                proj_lines.append(line)
        
        # Parse projects
        current_proj = {}
        for line in proj_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a project name (not a bullet point)
            if not line.startswith('-') and not line.startswith('•') and not line.startswith('*'):
                if current_proj.get('name'):
                    proj = Project(
                        name=current_proj.get('name', ''),
                        description=current_proj.get('description', ''),
                        technologies=current_proj.get('technologies', [])
                    )
                    projects.append(proj)
                
                current_proj = {'name': line, 'description': '', 'technologies': []}
            elif current_proj.get('name'):
                # Extract technologies
                tech_patterns = ['python', 'java', 'javascript', 'react', 'node', 'django', 
                                'flask', 'aws', 'docker', 'kubernetes', 'sql', 'mongodb']
                
                line_lower = line.lower()
                for tech in tech_patterns:
                    if tech in line_lower and tech not in current_proj.get('technologies', []):
                        current_proj['technologies'].append(tech.title())
                
                current_proj['description'] += line + ' '
        
        # Don't forget the last project
        if current_proj.get('name'):
            proj = Project(
                name=current_proj.get('name', ''),
                description=current_proj.get('description', ''),
                technologies=current_proj.get('technologies', [])
            )
            projects.append(proj)
        
        return projects
