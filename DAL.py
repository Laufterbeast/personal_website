import sqlite3
import os
from typing import List, Dict, Optional, Any

class DatabaseAccessLayer:
    """Data Access Layer for managing projects database operations."""
    
    def __init__(self, db_path: str = None):
        """Initialize the DAL with database path."""
        if db_path is None:
            # Default to projects.db in the current directory
            self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'projects.db')
        else:
            self.db_path = db_path
    
    def get_connection(self):
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize the database with projects table and sample data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                image_path TEXT NOT NULL,
                project_type TEXT NOT NULL,
                year INTEGER NOT NULL,
                status TEXT NOT NULL,
                tech_stack TEXT NOT NULL,
                github_url TEXT,
                live_url TEXT,
                featured BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert sample projects if table is empty
        cursor.execute('SELECT COUNT(*) FROM projects')
        if cursor.fetchone()[0] == 0:
            sample_projects = [
                {
                    'title': 'Campus BookShare',
                    'description': 'A comprehensive web platform enabling students to share, borrow, and lend textbooks across campus. Features user authentication, real-time messaging, and an intuitive interface for managing book transactions.',
                    'image_path': 'images/friends.jpg',
                    'project_type': 'Full-Stack Application',
                    'year': 2024,
                    'status': 'Completed',
                    'tech_stack': 'Flask,SQLite,JavaScript,CSS3,HTML5',
                    'github_url': 'https://github.com/Laufterbeast/FinalLauf.git',
                    'live_url': None,
                    'featured': 1
                },
                {
                    'title': 'Personal Website v2',
                    'description': 'A modern, responsive portfolio website showcasing clean design principles and interactive elements. Demonstrates proficiency in front-end development and user experience design.',
                    'image_path': 'images/friends_skyline.jpeg.jpeg',
                    'project_type': 'Portfolio Website',
                    'year': 2023,
                    'status': 'Completed',
                    'tech_stack': 'HTML5,CSS3,JavaScript',
                    'github_url': 'https://github.com/Laufterbeast/Personalwebv2.git',
                    'live_url': None,
                    'featured': 0
                },
                {
                    'title': 'Personal Website v1',
                    'description': 'The foundation of my web development journey, later refactored into this current site. Focused on accessibility, semantic HTML, and clean code architecture.',
                    'image_path': 'images/shellcoolcar.jpg',
                    'project_type': 'Portfolio Website',
                    'year': 2023,
                    'status': 'Refactored',
                    'tech_stack': 'HTML5,CSS3,Accessibility',
                    'github_url': None,
                    'live_url': None,
                    'featured': 0
                }
            ]
            
            for project in sample_projects:
                cursor.execute('''
                    INSERT INTO projects (title, description, image_path, project_type, year, status, tech_stack, github_url, live_url, featured)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    project['title'], project['description'], project['image_path'],
                    project['project_type'], project['year'], project['status'],
                    project['tech_stack'], project['github_url'], project['live_url'],
                    project['featured']
                ))
        
        conn.commit()
        conn.close()
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all projects ordered by featured status and year."""
        conn = self.get_connection()
        try:
            projects = conn.execute('SELECT * FROM projects ORDER BY featured DESC, year DESC').fetchall()
            return [self._row_to_dict(project) for project in projects]
        finally:
            conn.close()
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific project by ID."""
        conn = self.get_connection()
        try:
            project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
            return self._row_to_dict(project) if project else None
        finally:
            conn.close()
    
    def create_project(self, project_data: Dict[str, Any]) -> int:
        """Create a new project and return the project ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            tech_stack_str = ','.join(project_data['tech_stack']) if isinstance(project_data['tech_stack'], list) else project_data['tech_stack']
            
            cursor.execute('''
                INSERT INTO projects (title, description, image_path, project_type, year, status, tech_stack, github_url, live_url, featured)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_data['title'], project_data['description'], project_data['image_path'],
                project_data['project_type'], project_data['year'], project_data['status'],
                tech_stack_str, project_data.get('github_url'), project_data.get('live_url'),
                project_data.get('featured', False)
            ))
            
            project_id = cursor.lastrowid
            conn.commit()
            return project_id
        finally:
            conn.close()
    
    def update_project(self, project_id: int, project_data: Dict[str, Any]) -> bool:
        """Update an existing project. Returns True if successful."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if project exists
            project = cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
            if project is None:
                return False
            
            # Build update query dynamically
            update_fields = []
            update_values = []
            
            for field in ['title', 'description', 'image_path', 'project_type', 'year', 'status', 'tech_stack', 'github_url', 'live_url', 'featured']:
                if field in project_data:
                    if field == 'tech_stack' and isinstance(project_data[field], list):
                        update_fields.append(f"{field} = ?")
                        update_values.append(','.join(project_data[field]))
                    else:
                        update_fields.append(f"{field} = ?")
                        update_values.append(project_data[field])
            
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(project_id)
                
                cursor.execute(f'''
                    UPDATE projects SET {', '.join(update_fields)}
                    WHERE id = ?
                ''', update_values)
                
                conn.commit()
                return True
            
            return False
        finally:
            conn.close()
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project by ID. Returns True if successful."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if project exists
            project = cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
            if project is None:
                return False
            
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary with proper data types."""
        if row is None:
            return None
        
        return {
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'image_path': row['image_path'],
            'project_type': row['project_type'],
            'year': row['year'],
            'status': row['status'],
            'tech_stack': row['tech_stack'].split(',') if row['tech_stack'] else [],
            'github_url': row['github_url'],
            'live_url': row['live_url'],
            'featured': bool(row['featured']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
    
    def get_projects_count(self) -> int:
        """Get total number of projects."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM projects')
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def get_featured_projects(self) -> List[Dict[str, Any]]:
        """Get all featured projects."""
        conn = self.get_connection()
        try:
            projects = conn.execute('SELECT * FROM projects WHERE featured = 1 ORDER BY year DESC').fetchall()
            return [self._row_to_dict(project) for project in projects]
        finally:
            conn.close()
    
    def search_projects(self, search_term: str) -> List[Dict[str, Any]]:
        """Search projects by title or description."""
        conn = self.get_connection()
        try:
            search_pattern = f'%{search_term}%'
            projects = conn.execute('''
                SELECT * FROM projects 
                WHERE title LIKE ? OR description LIKE ? OR tech_stack LIKE ?
                ORDER BY featured DESC, year DESC
            ''', (search_pattern, search_pattern, search_pattern)).fetchall()
            return [self._row_to_dict(project) for project in projects]
        finally:
            conn.close()


