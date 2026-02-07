"""
Skill Normalizer for Resume Intelligence Engine
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config.config import SKILL_CATEGORIES


@dataclass
class NormalizedSkill:
    """Normalized skill data structure"""
    original: str
    normalized: str
    category: str
    confidence: float  # 0.0 to 1.0
    is_alias: bool
    aliases: List[str]


class SkillNormalizer:
    """Normalize and categorize skills from resumes"""
    
    # Skill aliases mapping
    SKILL_ALIASES = {
        # Programming Languages
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "rb": "Ruby",
        "cpp": "C++",
        "csharp": "C#",
        "objective-c": "Objective-C",
        "objc": "Objective-C",
        "fsharp": "F#",
        "golang": "Go",
        "rs": "Rust",
        "php": "PHP",
        "swift": "Swift",
        "kotlin": "Kotlin",
        "scala": "Scala",
        "matlab": "MATLAB",
        "r programming": "R",
        "sql": "SQL",
        "t-sql": "T-SQL",
        "plsql": "PL/SQL",
        "html5": "HTML",
        "css3": "CSS",
        
        # Frameworks & Libraries
        "reactjs": "React",
        "react.js": "React",
        "vuejs": "Vue.js",
        "vue.js": "Vue.js",
        "angularjs": "Angular",
        "angular.js": "Angular",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "expressjs": "Express.js",
        "express": "Express.js",
        "flask": "Flask",
        "django": "Django",
        "springboot": "Spring Boot",
        "spring": "Spring",
        "tensorflow": "TensorFlow",
        "pytorch": "PyTorch",
        "keras": "Keras",
        "sklearn": "Scikit-learn",
        "pandas": "Pandas",
        "numpy": "NumPy",
        "matplotlib": "Matplotlib",
        "bootstrap": "Bootstrap",
        "tailwind": "Tailwind CSS",
        "jquery": "jQuery",
        "nextjs": "Next.js",
        "nuxt": "Nuxt.js",
        "gatsby": "Gatsby",
        
        # Tools & Platforms
        "aws": "AWS",
        "amazon web services": "AWS",
        "azure": "Azure",
        "microsoft azure": "Azure",
        "gcp": "GCP",
        "google cloud": "GCP",
        "google cloud platform": "GCP",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "k8s": "Kubernetes",
        "git": "Git",
        "github": "GitHub",
        "gitlab": "GitLab",
        "jenkins": "Jenkins",
        "circleci": "CircleCI",
        "travis": "Travis CI",
        "linux": "Linux",
        "ubuntu": "Linux",
        "centos": "Linux",
        "debian": "Linux",
        "windows server": "Windows",
        "mongodb": "MongoDB",
        "postgres": "PostgreSQL",
        "mysql": "MySQL",
        "redis": "Redis",
        "elasticsearch": "Elasticsearch",
        "kafka": "Kafka",
        "rabbitmq": "RabbitMQ",
        "graphql": "GraphQL",
        "rest": "REST API",
        "restful": "REST API",
        "rest api": "REST API",
        "microservice": "Microservices",
        
        # Data Science
        "ml": "Machine Learning",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "nlp": "Natural Language Processing",
        "natural language processing": "Natural Language Processing",
        "computer vision": "Computer Vision",
        "data analytics": "Data Analysis",
        "data analysis": "Data Analysis",
        "data viz": "Data Visualization",
        "data visualization": "Data Visualization",
        "statistics": "Statistics",
        "a/b testing": "A/B Testing",
        "ab testing": "A/B Testing",
        "predictive modeling": "Predictive Modeling",
        "feature engineering": "Feature Engineering",
        
        # DevOps
        "devops": "DevOps",
        "cloud": "Cloud Architecture",
        "cloud architecture": "Cloud Architecture",
        "iaas": "Infrastructure as Code",
        "infrastructure as code": "Infrastructure as Code",
        "terraform": "Terraform",
        "ansible": "Ansible",
        "cicd": "CI/CD",
        "ci/cd": "CI/CD",
        "ci cd": "CI/CD",
        "monitoring": "Monitoring",
        "logging": "Logging",
        "security": "Security",
        "container": "Container Orchestration",
        "orchestration": "Container Orchestration",
        "service mesh": "Service Mesh",
    }
    
    # Skills that indicate learning/emerging
    LEARNING_INDICATORS = [
        "learning", "studying", "exploring", "familiarity", "beginner",
        "junior", "new to", "currently learning", "in progress", "async"
    ]
    
    def __init__(self):
        """Initialize skill normalizer with all categories"""
        self._build_reverse_mapping()
    
    def _build_reverse_mapping(self):
        """Build reverse mapping from normalized to aliases"""
        self._reverse_mapping = {}
        for alias, normalized in self.SKILL_ALIASES.items():
            if normalized not in self._reverse_mapping:
                self._reverse_mapping[normalized] = []
            self._reverse_mapping[normalized].append(alias)
    
    def normalize(self, skill: str) -> NormalizedSkill:
        """Normalize a single skill"""
        skill_lower = skill.lower().strip()
        
        # Check if it's an alias
        if skill_lower in self.SKILL_ALIASES:
            normalized = self.SKILL_ALIASES[skill_lower]
            category = self._get_category(normalized)
            return NormalizedSkill(
                original=skill,
                normalized=normalized,
                category=category,
                confidence=1.0,
                is_alias=True,
                aliases=self._reverse_mapping.get(normalized, [])
            )
        
        # Check if it's already a normalized name
        normalized = self._capitalize_skill(skill)
        category = self._get_category(normalized)
        
        if category:
            return NormalizedSkill(
                original=skill,
                normalized=normalized,
                category=category,
                confidence=0.95,
                is_alias=False,
                aliases=[]
            )
        
        # Unknown skill
        return NormalizedSkill(
            original=skill,
            normalized=self._capitalize_skill(skill),
            category="unknown",
            confidence=0.5,
            is_alias=False,
            aliases=[]
        )
    
    def normalize_list(self, skills: List[str]) -> List[NormalizedSkill]:
        """Normalize a list of skills"""
        return [self.normalize(skill) for skill in skills]
    
    def categorize(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into their respective categories"""
        categorized = {
            "programming_languages": [],
            "frameworks_libraries": [],
            "tools_platforms": [],
            "soft_skills": [],
            "data_science": [],
            "devops_cloud": [],
            "unknown": []
        }
        
        for skill in skills:
            normalized_skill = self.normalize(skill)
            category = normalized_skill.category
            
            if category in categorized:
                if normalized_skill.normalized not in categorized[category]:
                    categorized[category].append(normalized_skill.normalized)
            else:
                categorized["unknown"].append(normalized_skill.normalized)
        
        return categorized
    
    def _get_category(self, skill: str) -> str:
        """Get the category of a normalized skill"""
        skill_lower = skill.lower()
        
        for category, category_skills in SKILL_CATEGORIES.items():
            for category_skill in category_skills:
                if category_skill.lower() == skill_lower:
                    return category
        return "unknown"
    
    def _capitalize_skill(self, skill: str) -> str:
        """Capitalize skill name properly"""
        # Handle special cases
        special_cases = {
            "css": "CSS",
            "html": "HTML",
            "sql": "SQL",
            "api": "API",
            "aws": "AWS",
            "gcp": "GCP",
            "mongodb": "MongoDB",
            "graphql": "GraphQL",
            "restful": "REST API",
            "cicd": "CI/CD",
            "devops": "DevOps",
            "ml": "ML",
            "ai": "AI",
            "nlp": "NLP",
        }
        
        skill_lower = skill.lower().strip()
        if skill_lower in special_cases:
            return special_cases[skill_lower]
        
        # Title case for most skills
        return skill.strip().title()
    
    def identify_primary_skills(self, skills: List[str], 
                                 experience_years: int = 0) -> List[Tuple[str, str, float]]:
        """Identify primary skills based on frequency and relevance"""
        skill_scores = {}
        
        for skill in skills:
            normalized_skill = self.normalize(skill)
            key = normalized_skill.normalized
            
            if key not in skill_scores:
                skill_scores[key] = {
                    "count": 0,
                    "category": normalized_skill.category,
                    "confidence": normalized_skill.confidence
                }
            
            skill_scores[key]["count"] += 1
        
        # Score skills based on frequency and category importance
        priority_categories = [
            "programming_languages",
            "frameworks_libraries",
            "tools_platforms",
            "data_science",
            "devops_cloud",
            "soft_skills"
        ]
        
        scored_skills = []
        for skill, data in skill_scores.items():
            base_score = data["count"]
            
            # Boost for high-priority categories
            category = data["category"]
            if category in priority_categories:
                category_boost = len(priority_categories) - priority_categories.index(category)
            else:
                category_boost = 0  # No boost for unknown categories
            
            total_score = (base_score * 0.5) + (category_boost * 0.3) + (data["confidence"] * 0.2)
            
            scored_skills.append((skill, data["category"], round(total_score, 2)))
        
        # Sort by score descending
        scored_skills.sort(key=lambda x: x[2], reverse=True)
        
        return scored_skills
    
    def identify_emerging_skills(self, skills: List[str], 
                                  context: str = "") -> List[str]:
        """Identify skills that appear to be learning/emerging"""
        emerging = []
        context_lower = context.lower()
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check for learning indicators in context
            for indicator in self.LEARNING_INDICATORS:
                if indicator in context_lower:
                    emerging.append(skill)
                    break
            
            # Check if skill is in the alias list (less common skills)
            if skill_lower in self.SKILL_ALIASES:
                # Could be a less common variant
                continue
        
        return emerging
    
    def suggest_skill_expansion(self, skills: List[str], 
                                 category: str = "programming_languages") -> List[str]:
        """Suggest related skills based on existing skills"""
        from config.config import SKILL_CATEGORIES
        
        # Get related skills from the same category
        category_skills = SKILL_CATEGORIES.get(category, [])
        
        # Skills the user already has
        user_skills_lower = [s.lower() for s in skills]
        
        suggestions = []
        for skill in category_skills:
            if skill.lower() not in user_skills_lower:
                suggestions.append(skill)
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def calculate_skill_match(self, candidate_skills: List[str], 
                              required_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """Calculate match percentage between candidate and required skills"""
        candidate_normalized = {self.normalize(s).normalized.lower() for s in candidate_skills}
        required_normalized = {s.lower() for s in required_skills}
        
        matched = candidate_normalized & required_normalized
        missing = required_normalized - candidate_normalized
        
        if not required_normalized:
            return 1.0, [], []
        
        match_percentage = len(matched) / len(required_normalized)
        
        return (
            round(match_percentage, 2),
            list(matched),
            list(missing)
        )
    
    def get_skill_synonyms(self, skill: str) -> List[str]:
        """Get all known synonyms/aliases for a skill"""
        normalized = self.normalize(skill)
        
        if normalized.normalized in self._reverse_mapping:
            return self._reverse_mapping[normalized.normalized]
        
        return [skill]
    
    def validate_skills(self, skills: List[str]) -> Tuple[List[str], List[str]]:
        """Validate skills against known database"""
        valid = []
        invalid = []
        
        for skill in skills:
            normalized = self.normalize(skill)
            
            if normalized.category != "unknown" or normalized.confidence > 0.8:
                valid.append(normalized.normalized)
            else:
                invalid.append(skill)
        
        return valid, invalid
