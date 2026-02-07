"""
Flask Web Application for Resume Intelligence Engine
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
import re
from pathlib import Path

from api.resume_api import ResumeIntelligenceAPI
from config.config import SKILL_CATEGORIES

app = Flask(__name__)
app.secret_key = 'resume-intelligence-secret-key'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize API
api = ResumeIntelligenceAPI()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_job_keywords(job_description):
    """Extract potential skill keywords from job description"""
    job_lower = job_description.lower()
    keywords = set()
    
    # Get all known skills from config
    all_known_skills = []
    for category in SKILL_CATEGORIES.values():
        all_known_skills.extend([s.lower() for s in category])
    
    # Check for known skills in job description
    for skill in all_known_skills:
        if skill in job_lower:
            keywords.add(skill)
    
    # Also extract potential skills using patterns
    # Look for phrases like "experience with X", "knowledge of X", "proficient in X"
    patterns = [
        r'experience (?:with|in|of)\s+([a-z0-9\s]+)',
        r'knowledge (?:of|in)\s+([a-z0-9\s]+)',
        r'proficient (?:in|with)\s+([a-z0-9\s]+)',
        r'skilled (?:in|with)\s+([a-z0-9\s]+)',
        r'familiar (?:with|of)\s+([a-z0-9\s]+)',
        r'must have\s+([a-z0-9\s]+)',
        r'preferred\s+([a-z0-9\s]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, job_lower)
        for match in matches:
            # Extract individual words from the match
            words = match.strip().split()
            for word in words:
                if len(word) > 2 and word not in ['and', 'the', 'with', 'have', 'must', 'also']:
                    keywords.add(word)
    
    return list(keywords)


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle resume upload and analysis"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                result = api.analyze_resume(filepath)
                return render_template('result.html', result=result, filename=filename)
            except Exception as e:
                flash(f'Error analyzing resume: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Allowed: PDF, DOCX, TXT', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')


@app.route('/quick', methods=['GET', 'POST'])
def quick_analyze():
    """Quick text-based analysis"""
    if request.method == 'POST':
        resume_text = request.form.get('resume_text', '')
        if resume_text.strip():
            try:
                result = api.analyze_resume_text(resume_text)
                return render_template('result.html', result=result, filename="Text Input")
            except Exception as e:
                flash(f'Error analyzing text: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please enter resume text', 'error')
            return redirect(request.url)
    
    return render_template('quick.html')


@app.route('/compare', methods=['GET', 'POST'])
def compare_job():
    """Compare resume against job description"""
    if request.method == 'POST':
        resume_text = request.form.get('resume_text', '')
        job_description = request.form.get('job_description', '')
        
        if not job_description.strip():
            flash('Please provide a job description', 'error')
            return redirect(request.url)
        
        if not resume_text.strip():
            flash('Please provide resume text', 'error')
            return redirect(request.url)
        
        try:
            # Analyze resume text
            result = api.analyze_resume_text(resume_text)
            
            # Get experience profile
            experience_profile = result.get('experience_profile', {})
            career_level = experience_profile.get('career_level', 'Not specified')
            total_years = experience_profile.get('total_years_experience', 0)
            
            # Get resume score
            resume_score = result.get('resume_score', {})
            overall_score = resume_score.get('overall_score', 0)
            grade = resume_score.get('grade', '')
            
            # Get all skills from resume
            all_skills = result.get('skill_profile', {}).get('all_skills', [])
            primary_skills = [s.get('skill', '') if isinstance(s, dict) else str(s) 
                            for s in result.get('skill_profile', {}).get('primary_skills', [])]
            all_skills.extend(primary_skills)
            resume_skill_set = set([s.lower() for s in all_skills])
            
            # Extract keywords from job description
            job_keywords = extract_job_keywords(job_description)
            
            # Match skills
            matched = []
            missing = []
            
            for keyword in job_keywords:
                # Check if any resume skill contains this keyword
                is_matched = False
                for skill in resume_skill_set:
                    if keyword in skill or skill in keyword:
                        matched.append(keyword)
                        is_matched = True
                        break
                if not is_matched:
                    missing.append(keyword)
            
            # Calculate match percentage
            if job_keywords:
                match_pct = (len(matched) / len(job_keywords)) * 100
            else:
                match_pct = 50
            
            # Generate recommendation
            if match_pct >= 80:
                recommendation = "Strong match! Apply with confidence."
            elif match_pct >= 60:
                recommendation = "Good match. Consider addressing missing skills."
            elif match_pct >= 40:
                recommendation = "Partial match. Some skill gaps to fill."
            else:
                recommendation = "Low match. Consider learning more required skills."
            
            job_match = {
                'match_percentage': round(match_pct, 2),
                'requirements_found': matched,
                'requirements_missing': missing,
                'recommendation': recommendation,
                'job_keywords_found': len(job_keywords),
                'career_level': career_level,
                'total_years_experience': total_years,
                'overall_score': overall_score,
                'grade': grade,
                'all_skills': list(resume_skill_set)[:10] if resume_skill_set else []
            }
            
            return render_template('compare.html', 
                                 job_match=job_match, 
                                 job_description=job_description)
            
        except Exception as e:
            flash(f'Error comparing: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('compare.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_api():
    """API endpoint for resume analysis"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            result = api.analyze_resume(filepath)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/compare', methods=['POST'])
def compare_api():
    """API endpoint for job comparison"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    resume_text = data.get('resume_text', '')
    job_description = data.get('job_description', '')
    
    if not job_description:
        return jsonify({'error': 'Job description required'}), 400
    
    try:
        if resume_text:
            result = api.analyze_resume_text(resume_text)
        else:
            return jsonify({'error': 'Resume text required'}), 400
        
        job_match = api.quality_scorer.compare_with_job_description(
            result, job_description
        )
        
        return jsonify(job_match)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return redirect(url_for('static', filename=f'uploads/{filename}'))


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Resume Intelligence Engine'})


if __name__ == '__main__':
    print("=" * 60)
    print("Resume Intelligence Engine - Web Interface")
    print("=" * 60)
    print("\nStarting local server...")
    print("\nAccess the web interface at:")
    print("  http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  POST /api/analyze - Analyze resume file")
    print("  POST /api/compare - Compare with job description")
    print("  GET  /health - Health check")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
