"""
Configuration for Resume Intelligence Engine
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Create output directory if not exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Skill categories - including non-technical skills
SKILL_CATEGORIES = {
    # Technical skills
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL", "HTML", "CSS"
    ],
    "frameworks_libraries": [
        "React", "Angular", "Vue.js", "Django", "Flask", "Spring", "Node.js",
        "Express.js", "FastAPI", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
        "Pandas", "NumPy", "Matplotlib", "Bootstrap", "Tailwind CSS", "jQuery"
    ],
    "tools_platforms": [
        "Git", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", "CI/CD",
        "Linux", "Windows", "macOS", "MongoDB", "PostgreSQL", "MySQL", "Redis",
        "Elasticsearch", "RabbitMQ", "Kafka", "GraphQL", "REST API", "Microservices"
    ],
    "data_science": [
        "Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision",
        "Data Analysis", "Data Visualization", "Statistics", "A/B Testing",
        "Predictive Modeling", "Feature Engineering", "Model Deployment"
    ],
    "devops_cloud": [
        "DevOps", "Cloud Architecture", "Infrastructure as Code", "Terraform",
        "Ansible", "CI/CD Pipelines", "Monitoring", "Logging", "Security",
        "Container Orchestration", "Service Mesh"
    ],
    
    # Non-technical / General Skills
    "soft_skills": [
        "Communication", "Teamwork", "Leadership", "Problem Solving", "Critical Thinking",
        "Time Management", "Adaptability", "Creativity", "Analytical Skills",
        "Project Management", "Collaboration", "Presentation", "Negotiation",
        "Interpersonal Skills", "Customer Service", "Organizational Skills",
        "Attention to Detail", "Multitasking", "Decision Making", "Conflict Resolution"
    ],
    
    # Teaching & Education
    "education_skills": [
        "Curriculum Development", "Lesson Planning", "Classroom Management", "Teaching",
        "Education Technology", "Student Assessment", "Instructional Design", "Training",
        "Tutoring", "Academic Advising", "Course Development", "E-Learning",
        "Special Education", "Child Development", "Pedagogy"
    ],
    
    # Sales & Marketing
    "sales_marketing_skills": [
        "Sales", "Lead Generation", "Client Relations", "Negotiation", "Business Development",
        "Account Management", "Market Research", "Digital Marketing", "SEO", "SEM",
        "Social Media Marketing", "Content Marketing", "Email Marketing", "Brand Management",
        "Public Relations", "Advertising", "CRM", "Salesforce", "Revenue Growth",
        "Customer Acquisition", "Partner Relations", "Cold Calling", "Prospecting"
    ],
    
    # Retail & Customer Service
    "retail_customer_service": [
        "Customer Service", "Retail", "Point of Sale", "Inventory Management",
        "Cash Handling", "Store Operations", "Merchandising", "Stock Management",
        "Clienteling", "Product Knowledge", "Visual Merchandising", "Order Fulfillment",
        "Returns Processing", "Payment Processing", "Upselling", "Cross-selling"
    ],
    
    # Healthcare
    "healthcare_skills": [
        "Patient Care", "Clinical Skills", "Medical Terminology", "Healthcare Documentation",
        "HIPAA Compliance", "Vital Signs", "Phlebotomy", "EKG", "CPR Certified",
        "Electronic Health Records", "Patient Advocacy", "Medical Billing", "Insurance Claims",
        "Health Education", "Wellness Coaching"
    ],
    
    # Administration & Office
    "administrative_skills": [
        "Microsoft Office", "Google Workspace", "Data Entry", "Record Keeping",
        "Document Management", "Calendar Management", "Travel Coordination", "Meeting Coordination",
        "Office Administration", "Executive Assistant", "Administrative Support",
        "Correspondence", "Filing Systems", "Budgeting", "Expense Reporting"
    ],
    
    # Finance & Accounting
    "finance_accounting_skills": [
        "Financial Analysis", "Budgeting", "Forecasting", "Financial Reporting",
        "Bookkeeping", "Accounts Payable", "Accounts Receivable", "Tax Preparation",
        "Audit", "Compliance", "Risk Management", "Investment Analysis",
        "Excel", "QuickBooks", "SAP", "Oracle Financials", "Payroll Processing"
    ],
    
    # Human Resources
    "hr_skills": [
        "Recruiting", "Talent Acquisition", "Employee Relations", "Performance Management",
        "Training and Development", "HRIS", "Benefits Administration", "Onboarding",
        "Offboarding", "Succession Planning", "Workforce Planning", "HR Analytics",
        "Employee Engagement", "Policy Development", "Labor Law Compliance"
    ],
    
    # Project Management
    "project_management_skills": [
        "Project Planning", "Project Execution", "Risk Management", "Stakeholder Management",
        "Resource Allocation", "Budget Management", "Schedule Management", "Agile", "Scrum",
        "Waterfall", "Kanban", "JIRA", "Confluence", "Microsoft Project",
        "Earned Value Management", "Quality Assurance", "Vendor Management"
    ],
    
    # Operations & Logistics
    "operations_logistics": [
        "Supply Chain Management", "Logistics", "Inventory Control", "Warehouse Management",
        "Transportation", "Procurement", "Vendor Management", "Quality Control",
        "Process Improvement", "Lean Six Sigma", "Forecasting", "Demand Planning",
        "Distribution", "Order Management", "Freight Forwarding"
    ]
}

# Job roles database - including non-technical roles
JOB_ROLES = {
    # Technical roles
    "software_engineer": {
        "title": "Software Engineer",
        "required_skills": ["Python", "Java", "JavaScript", "SQL", "Git"],
        "experience_level": "mid",
        "keywords": ["development", "coding", "programming", "software"]
    },
    "data_scientist": {
        "title": "Data Scientist",
        "required_skills": ["Python", "Machine Learning", "Statistics", "SQL", "Data Analysis"],
        "experience_level": "mid",
        "keywords": ["data", "machine learning", "analytics", "modeling"]
    },
    "frontend_developer": {
        "title": "Frontend Developer",
        "required_skills": ["JavaScript", "HTML", "CSS", "React", "Vue.js"],
        "experience_level": "mid",
        "keywords": ["frontend", "UI", "UX", "web development"]
    },
    "backend_developer": {
        "title": "Backend Developer",
        "required_skills": ["Python", "Java", "Node.js", "SQL", "REST API"],
        "experience_level": "mid",
        "keywords": ["backend", "API", "server", "database"]
    },
    "full_stack_developer": {
        "title": "Full Stack Developer",
        "required_skills": ["JavaScript", "Python", "React", "Node.js", "SQL"],
        "experience_level": "senior",
        "keywords": ["full stack", "end-to-end", "complete development"]
    },
    "devops_engineer": {
        "title": "DevOps Engineer",
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux"],
        "experience_level": "senior",
        "keywords": ["devops", "infrastructure", "automation", "deployment"]
    },
    "machine_learning_engineer": {
        "title": "Machine Learning Engineer",
        "required_skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning"],
        "experience_level": "senior",
        "keywords": ["ML", "AI", "neural networks", "model training"]
    },
    
    # Non-technical roles
    "project_manager": {
        "title": "Project Manager",
        "required_skills": ["Project Planning", "Risk Management", "Stakeholder Management", "Agile", "Scrum"],
        "experience_level": "senior",
        "keywords": ["project", "planning", "execution", "delivery", "coordination"]
    },
    "product_manager": {
        "title": "Product Manager",
        "required_skills": ["Product Management", "Communication", "Analytical Skills", "Strategy"],
        "experience_level": "senior",
        "keywords": ["product", "roadmap", "stakeholders", "requirements"]
    },
    "teacher": {
        "title": "Teacher / Educator",
        "required_skills": ["Curriculum Development", "Lesson Planning", "Classroom Management", "Teaching"],
        "experience_level": "mid",
        "keywords": ["teaching", "education", "training", "instruction", "students"]
    },
    "sales_representative": {
        "title": "Sales Representative",
        "required_skills": ["Sales", "Lead Generation", "Client Relations", "Negotiation", "Communication"],
        "experience_level": "junior",
        "keywords": ["sales", "selling", "revenue", "clients", "deals"]
    },
    "account_manager": {
        "title": "Account Manager",
        "required_skills": ["Account Management", "Client Relations", "Communication", "Negotiation"],
        "experience_level": "mid",
        "keywords": ["accounts", "clients", "relationships", "retention"]
    },
    "retail_associate": {
        "title": "Retail Associate",
        "required_skills": ["Customer Service", "Retail", "Sales", "Point of Sale"],
        "experience_level": "junior",
        "keywords": ["retail", "store", "customers", "sales", "products"]
    },
    "customer_service_rep": {
        "title": "Customer Service Representative",
        "required_skills": ["Customer Service", "Communication", "Problem Solving", "Interpersonal Skills"],
        "experience_level": "junior",
        "keywords": ["customer service", "support", "clients", "inquiries"]
    },
    "nurse": {
        "title": "Nurse / Healthcare Professional",
        "required_skills": ["Patient Care", "Clinical Skills", "Medical Terminology", "Healthcare Documentation"],
        "experience_level": "mid",
        "keywords": ["healthcare", "patient", "medical", "clinical", "care"]
    },
    "administrative_assistant": {
        "title": "Administrative Assistant",
        "required_skills": ["Microsoft Office", "Data Entry", "Calendar Management", "Communication"],
        "experience_level": "junior",
        "keywords": ["administration", "office", "support", "coordination"]
    },
    "accountant": {
        "title": "Accountant",
        "required_skills": ["Financial Analysis", "Bookkeeping", "Excel", "Financial Reporting"],
        "experience_level": "mid",
        "keywords": ["accounting", "finance", "tax", "audit", "reports"]
    },
    "hr_specialist": {
        "title": "HR Specialist",
        "required_skills": ["Recruiting", "Employee Relations", "Training and Development", "HRIS"],
        "experience_level": "mid",
        "keywords": ["human resources", "HR", "recruiting", "employees"]
    },
    "operations_manager": {
        "title": "Operations Manager",
        "required_skills": ["Operations Management", "Process Improvement", "Team Leadership", "Logistics"],
        "experience_level": "senior",
        "keywords": ["operations", "logistics", "process", "efficiency"]
    },
    "marketing_specialist": {
        "title": "Marketing Specialist",
        "required_skills": ["Digital Marketing", "Social Media Marketing", "Content Marketing", "Analytics"],
        "experience_level": "mid",
        "keywords": ["marketing", "campaigns", "digital", "branding"]
    },
    "business_analyst": {
        "title": "Business Analyst",
        "required_skills": ["Analytical Skills", "Data Analysis", "Requirements Gathering", "Communication"],
        "experience_level": "mid",
        "keywords": ["business", "analysis", "requirements", "stakeholders"]
    },
    "data_analyst": {
        "title": "Data Analyst",
        "required_skills": ["Python", "SQL", "Data Analysis", "Excel", "Data Visualization"],
        "experience_level": "junior",
        "keywords": ["analytics", "reporting", "visualization", "insights"]
    }
}

# Experience level thresholds (in years)
EXPERIENCE_THRESHOLDS = {
    "fresher": 0,
    "junior": 1,
    "mid": 3,
    "senior": 5,
    "lead": 8,
    "architect": 10
}

# ATS keywords by industry - including non-technical
ATS_KEYWORDS = {
    "technology": ["agile", "scrum", "ci/cd", "devops", "microservices", "api", "cloud"],
    "finance": ["risk management", "compliance", "financial analysis", "trading", "banking"],
    "healthcare": ["hipaa", "patient care", "clinical", "healthcare analytics", "ehr"],
    "marketing": ["digital marketing", "seo", "content strategy", "analytics", "campaigns"],
    "sales": ["lead generation", "salesforce", "revenue", "client relations", "negotiation"],
    "education": ["curriculum", "lesson planning", "classroom management", "student outcomes"],
    "retail": ["customer satisfaction", "merchandising", "inventory", "sales targets"],
    "hr": ["recruitment", "employee engagement", "performance reviews", "training"],
    "operations": ["supply chain", "logistics", "process optimization", "vendor management"]
}

# Resume scoring weights
SCORING_WEIGHTS = {
    "skill_relevance": 0.25,
    "experience_clarity": 0.25,
    "keyword_optimization": 0.20,
    "structure_readability": 0.20,
    "completeness": 0.10
}
