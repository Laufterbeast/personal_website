from flask import Flask, send_from_directory, abort, jsonify, request
import os
from DAL import DatabaseAccessLayer

app = Flask(__name__)

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Data Access Layer
dal = DatabaseAccessLayer()


def _safe_send(filename):
    """Helper to send a file from project root if it exists, otherwise 404."""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path) and os.path.isfile(path):
        return send_from_directory(BASE_DIR, filename)
    abort(404)


@app.route('/')
def index():
    return _safe_send('index.html')


@app.route('/about')
def about():
    return _safe_send('about.html')


@app.route('/projects')
def projects():
    return _safe_send('projects.html')


@app.route('/contact')
def contact():
    return _safe_send('contact.html')


@app.route('/resume')
def resume_page():
    return _safe_send('resume.html')


@app.route('/thankyou')
def thankyou():
    return _safe_send('thankyou.html')

@app.route('/admin')
def admin():
    return _safe_send('admin.html')


# Serve any root-level HTML file (e.g., /about.html, /index.html)
@app.route('/<path:filename>.html')
def root_html(filename):
    # Only serve files that exist in the project root and end with .html
    requested = f"{filename}.html"
    return _safe_send(requested)


# Shortcut for the resume PDF (serve resume/Laufter_Joseph_Resume.pdf as /resume.pdf)
@app.route('/resume.pdf')
def resume_pdf():
    resume_dir = os.path.join(BASE_DIR, 'resume')
    # Find first pdf in resume dir, or try known filename
    candidates = ['Laufter_Joseph_Resume.pdf', 'resume.pdf']
    for c in candidates:
        p = os.path.join(resume_dir, c)
        if os.path.exists(p):
            return send_from_directory(resume_dir, c)
    # fallback: list files for debug (404)
    abort(404)


# Static asset routes
@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'css'), filename)


@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'images'), filename)


@app.route('/resume_file/<path:filename>')
def resume_file(filename):
    # serve files from resume/ folder (PDF)
    return send_from_directory(os.path.join(BASE_DIR, 'resume'), filename)


# API Routes for Projects
@app.route('/api/projects')
def get_projects():
    """Get all projects."""
    try:
        projects = dal.get_all_projects()
        return jsonify(projects)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch projects'}), 500

@app.route('/api/projects/<int:project_id>')
def get_project(project_id):
    """Get a specific project by ID."""
    try:
        project = dal.get_project_by_id(project_id)
        if project is None:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify(project)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch project'}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project."""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'description', 'image_path', 'project_type', 'year', 'status', 'tech_stack']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        project_id = dal.create_project(data)
        return jsonify({'id': project_id, 'message': 'Project created successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to create project'}), 500

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update an existing project."""
    try:
        data = request.get_json()
        
        success = dal.update_project(project_id, data)
        if not success:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({'message': 'Project updated successfully'})
    except Exception as e:
        return jsonify({'error': 'Failed to update project'}), 500

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project."""
    try:
        success = dal.delete_project(project_id)
        if not success:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({'message': 'Project deleted successfully'})
    except Exception as e:
        return jsonify({'error': 'Failed to delete project'}), 500


if __name__ == '__main__':
    # Initialize database on startup
    dal.init_database()
    # Run on 0.0.0.0:8000 so it's accessible on the local network
    app.run(host='0.0.0.0', port=8000, debug=True)
