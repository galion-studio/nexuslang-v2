#!/usr/bin/env python3
"""
GALION.STUDIO - Transparent Workplace Platform
Built with Elon Musk's First Principles: Simple, Fast, Effective

Core Features:
- Task management with transparent costs
- Time tracking
- Compensation transparency
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
import uuid
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///galion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)  # Allow frontend to connect

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """User model - keeps track of team members"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    hourly_rate = db.Column(db.Float, default=100.0)  # Transparent pay
    role = db.Column(db.String(20), default='contributor')  # owner or contributor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'hourly_rate': self.hourly_rate,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Workspace(db.Model):
    """Workspace model - one workspace per team/company"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert workspace to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(db.Model):
    """Task model - core of the system"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspace.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assignee_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='backlog')  # backlog, in_progress, done
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    hours_estimate = db.Column(db.Float, default=0)
    hourly_rate = db.Column(db.Float, default=100.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def total_cost(self):
        """Calculate total estimated cost"""
        return self.hours_estimate * self.hourly_rate

    def to_dict(self):
        """Convert task to dictionary"""
        assignee = User.query.get(self.assignee_id) if self.assignee_id else None
        return {
            'id': self.id,
            'workspace_id': self.workspace_id,
            'title': self.title,
            'description': self.description,
            'assignee_id': self.assignee_id,
            'assignee': assignee.to_dict() if assignee else None,
            'status': self.status,
            'priority': self.priority,
            'hours_estimate': self.hours_estimate,
            'hourly_rate': self.hourly_rate,
            'total_cost': self.total_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TimeLog(db.Model):
    """Time log model - tracks actual work done"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def amount(self):
        """Calculate compensation for this time log"""
        user = User.query.get(self.user_id)
        return self.hours * (user.hourly_rate if user else 0)

    def to_dict(self):
        """Convert time log to dictionary"""
        user = User.query.get(self.user_id)
        task = Task.query.get(self.task_id)
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_title': task.title if task else None,
            'user_id': self.user_id,
            'user_name': user.name if user else None,
            'hours': self.hours,
            'work_date': self.work_date.isoformat() if self.work_date else None,
            'description': self.description,
            'amount': self.amount,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SocialPost(db.Model):
    """Social media post model - content management for multiple platforms"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = db.Column(db.String(36), db.ForeignKey('workspace.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)  # Internal title
    content = db.Column(db.Text, nullable=False)  # The actual post content
    platforms = db.Column(db.String(200))  # Comma-separated: reddit,twitter,instagram,tiktok,facebook
    status = db.Column(db.String(20), default='draft')  # draft, posted, scheduled
    posted_at = db.Column(db.DateTime)  # When it was actually posted
    notes = db.Column(db.Text)  # Internal notes about the post
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert social post to dictionary"""
        creator = User.query.get(self.created_by) if self.created_by else None
        return {
            'id': self.id,
            'workspace_id': self.workspace_id,
            'title': self.title,
            'content': self.content,
            'platforms': self.platforms.split(',') if self.platforms else [],
            'status': self.status,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'notes': self.notes,
            'created_by': self.created_by,
            'creator_name': creator.name if creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user():
    """Get current user from request headers (simple auth for Alpha)"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return None
    return User.query.get(user_id)


def validate_required(data, fields):
    """Validate required fields in request data"""
    missing = [field for field in fields if field not in data or not data[field]]
    if missing:
        return {'error': f'Missing required fields: {", ".join(missing)}'}, 400
    return None


# ============================================================================
# API ENDPOINTS - USERS
# ============================================================================

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    # Validate required fields
    error = validate_required(data, ['email', 'name'])
    if error:
        return jsonify(error[0]), error[1]
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create user
    user = User(
        email=data['email'],
        name=data['name'],
        hourly_rate=data.get('hourly_rate', 100.0),
        role=data.get('role', 'contributor')
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201


@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


# ============================================================================
# API ENDPOINTS - WORKSPACES
# ============================================================================

@app.route('/api/workspaces', methods=['POST'])
def create_workspace():
    """Create a new workspace"""
    data = request.json
    
    # Validate required fields
    error = validate_required(data, ['name', 'slug'])
    if error:
        return jsonify(error[0]), error[1]
    
    # Check if slug already exists
    if Workspace.query.filter_by(slug=data['slug']).first():
        return jsonify({'error': 'Slug already exists'}), 400
    
    # Get current user
    user = get_current_user()
    
    # Create workspace
    workspace = Workspace(
        name=data['name'],
        slug=data['slug'],
        owner_id=user.id if user else data.get('owner_id')
    )
    db.session.add(workspace)
    db.session.commit()
    
    return jsonify(workspace.to_dict()), 201


@app.route('/api/workspaces', methods=['GET'])
def list_workspaces():
    """List all workspaces"""
    workspaces = Workspace.query.all()
    return jsonify([ws.to_dict() for ws in workspaces])


@app.route('/api/workspaces/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """Get a specific workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    return jsonify(workspace.to_dict())


# ============================================================================
# API ENDPOINTS - TASKS
# ============================================================================

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.json
    
    # Validate required fields
    error = validate_required(data, ['workspace_id', 'title'])
    if error:
        return jsonify(error[0]), error[1]
    
    # Validate hours estimate is positive
    if data.get('hours_estimate', 0) < 0:
        return jsonify({'error': 'Hours estimate must be positive'}), 400
    
    # Create task
    task = Task(
        workspace_id=data['workspace_id'],
        title=data['title'],
        description=data.get('description'),
        assignee_id=data.get('assignee_id'),
        hours_estimate=data.get('hours_estimate', 0),
        hourly_rate=data.get('hourly_rate', 100.0),
        status=data.get('status', 'backlog'),
        priority=data.get('priority', 'medium')
    )
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201


@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """List tasks with optional filtering"""
    workspace_id = request.args.get('workspace_id')
    assignee_id = request.args.get('assignee_id')
    status = request.args.get('status')
    
    query = Task.query
    
    # Apply filters
    if workspace_id:
        query = query.filter_by(workspace_id=workspace_id)
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@app.route('/api/tasks/<task_id>', methods=['PATCH'])
def update_task(task_id):
    """Update a task"""
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    # Update fields if provided
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'assignee_id' in data:
        task.assignee_id = data['assignee_id']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'hours_estimate' in data:
        task.hours_estimate = data['hours_estimate']
    if 'hourly_rate' in data:
        task.hourly_rate = data['hourly_rate']
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(task.to_dict())


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204


# ============================================================================
# API ENDPOINTS - TIME LOGS
# ============================================================================

@app.route('/api/time-logs', methods=['POST'])
def create_time_log():
    """Create a new time log"""
    data = request.json
    user = get_current_user()
    
    # Validate required fields
    error = validate_required(data, ['task_id', 'hours', 'work_date'])
    if error:
        return jsonify(error[0]), error[1]
    
    # Validate hours is positive
    if data['hours'] <= 0:
        return jsonify({'error': 'Hours must be positive'}), 400
    
    # Parse date
    try:
        work_date = datetime.fromisoformat(data['work_date']).date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Create time log
    time_log = TimeLog(
        task_id=data['task_id'],
        user_id=user.id if user else data.get('user_id'),
        hours=data['hours'],
        work_date=work_date,
        description=data.get('description')
    )
    db.session.add(time_log)
    db.session.commit()
    
    return jsonify(time_log.to_dict()), 201


@app.route('/api/time-logs', methods=['GET'])
def list_time_logs():
    """List time logs with optional filtering"""
    user_id = request.args.get('user_id')
    task_id = request.args.get('task_id')
    workspace_id = request.args.get('workspace_id')
    
    query = TimeLog.query
    
    # Apply filters
    if user_id:
        query = query.filter_by(user_id=user_id)
    if task_id:
        query = query.filter_by(task_id=task_id)
    if workspace_id:
        # Join with Task to filter by workspace
        query = query.join(Task).filter(Task.workspace_id == workspace_id)
    
    time_logs = query.order_by(TimeLog.work_date.desc()).all()
    return jsonify([log.to_dict() for log in time_logs])


@app.route('/api/time-logs/<log_id>', methods=['DELETE'])
def delete_time_log(log_id):
    """Delete a time log"""
    time_log = TimeLog.query.get_or_404(log_id)
    db.session.delete(time_log)
    db.session.commit()
    return '', 204


# ============================================================================
# API ENDPOINTS - ANALYTICS
# ============================================================================

@app.route('/api/analytics/compensation', methods=['GET'])
def get_compensation_summary():
    """Get compensation summary by user"""
    workspace_id = request.args.get('workspace_id')
    
    if not workspace_id:
        return jsonify({'error': 'workspace_id is required'}), 400
    
    # Get all time logs for workspace
    logs = db.session.query(TimeLog).join(Task).filter(
        Task.workspace_id == workspace_id
    ).all()
    
    # Group by user
    user_totals = {}
    for log in logs:
        if log.user_id not in user_totals:
            user = User.query.get(log.user_id)
            user_totals[log.user_id] = {
                'user_id': log.user_id,
                'user_name': user.name if user else 'Unknown',
                'hourly_rate': user.hourly_rate if user else 0,
                'total_hours': 0,
                'total_amount': 0
            }
        user_totals[log.user_id]['total_hours'] += log.hours
        user_totals[log.user_id]['total_amount'] += log.amount
    
    return jsonify(list(user_totals.values()))


# ============================================================================
# API ENDPOINTS - SOCIAL MEDIA
# ============================================================================

@app.route('/api/social-posts', methods=['POST'])
def create_social_post():
    """Create a new social media post"""
    data = request.json
    
    # Validate required fields
    error = validate_required(data, ['workspace_id', 'title', 'content'])
    if error:
        return jsonify(error[0]), error[1]
    
    # Get current user
    user = get_current_user()
    
    # Join platforms array into comma-separated string
    platforms = ','.join(data.get('platforms', [])) if data.get('platforms') else ''
    
    # Create social post
    post = SocialPost(
        workspace_id=data['workspace_id'],
        title=data['title'],
        content=data['content'],
        platforms=platforms,
        status=data.get('status', 'draft'),
        notes=data.get('notes'),
        created_by=user.id if user else data.get('created_by')
    )
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201


@app.route('/api/social-posts', methods=['GET'])
def list_social_posts():
    """List social media posts with optional filtering"""
    workspace_id = request.args.get('workspace_id')
    status = request.args.get('status')
    
    query = SocialPost.query
    
    # Apply filters
    if workspace_id:
        query = query.filter_by(workspace_id=workspace_id)
    if status:
        query = query.filter_by(status=status)
    
    posts = query.order_by(SocialPost.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts])


@app.route('/api/social-posts/<post_id>', methods=['GET'])
def get_social_post(post_id):
    """Get a specific social media post"""
    post = SocialPost.query.get_or_404(post_id)
    return jsonify(post.to_dict())


@app.route('/api/social-posts/<post_id>', methods=['PATCH'])
def update_social_post(post_id):
    """Update a social media post"""
    post = SocialPost.query.get_or_404(post_id)
    data = request.json
    
    # Update fields if provided
    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']
    if 'platforms' in data:
        post.platforms = ','.join(data['platforms']) if data['platforms'] else ''
    if 'status' in data:
        post.status = data['status']
        # If status changed to 'posted', record timestamp
        if data['status'] == 'posted' and not post.posted_at:
            post.posted_at = datetime.utcnow()
    if 'notes' in data:
        post.notes = data['notes']
    
    post.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(post.to_dict())


@app.route('/api/social-posts/<post_id>', methods=['DELETE'])
def delete_social_post(post_id):
    """Delete a social media post"""
    post = SocialPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return '', 204


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'galion-alpha',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/seed', methods=['POST'])
def seed_data():
    """Seed database with test data for development"""
    try:
        # Create users
        john = User(email='john@acme.com', name='John Doe', hourly_rate=120, role='owner')
        sarah = User(email='sarah@acme.com', name='Sarah Smith', hourly_rate=150, role='contributor')
        mike = User(email='mike@acme.com', name='Mike Johnson', hourly_rate=100, role='contributor')
        
        db.session.add_all([john, sarah, mike])
        db.session.commit()
        
        # Create workspace
        workspace = Workspace(name='Acme Corp', slug='acme-corp', owner_id=john.id)
        db.session.add(workspace)
        db.session.commit()
        
        # Create tasks
        task1 = Task(
            workspace_id=workspace.id,
            title='Build authentication system',
            description='Implement secure user authentication with JWT',
            assignee_id=john.id,
            hours_estimate=20,
            hourly_rate=120,
            status='in_progress',
            priority='high'
        )
        task2 = Task(
            workspace_id=workspace.id,
            title='Design UI mockups',
            description='Create beautiful, minimal dark theme UI designs',
            assignee_id=sarah.id,
            hours_estimate=10,
            hourly_rate=150,
            status='done',
            priority='medium'
        )
        task3 = Task(
            workspace_id=workspace.id,
            title='Set up database',
            description='Configure PostgreSQL with proper indexes',
            assignee_id=mike.id,
            hours_estimate=8,
            hourly_rate=100,
            status='backlog',
            priority='high'
        )
        
        db.session.add_all([task1, task2, task3])
        db.session.commit()
        
        # Create time logs
        log1 = TimeLog(
            task_id=task1.id,
            user_id=john.id,
            hours=8,
            work_date=date.today(),
            description='Set up authentication flow with JWT tokens'
        )
        log2 = TimeLog(
            task_id=task2.id,
            user_id=sarah.id,
            hours=10,
            work_date=date.today(),
            description='Completed all UI mockups in Figma'
        )
        
        db.session.add_all([log1, log2])
        db.session.commit()
        
        return jsonify({
            'message': 'Database seeded successfully!',
            'users': 3,
            'workspaces': 1,
            'tasks': 3,
            'time_logs': 2
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# INITIALIZE DATABASE & START SERVER
# ============================================================================

if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        print('✅ Database tables created successfully!')
        print('📊 GALION.STUDIO Alpha is ready!')
        print('🌐 API running on http://localhost:5000')
        print('📖 API docs: http://localhost:5000/health')
        print('')
        print('Quick start:')
        print('  1. Seed data: curl -X POST http://localhost:5000/api/seed')
        print('  2. List tasks: curl http://localhost:5000/api/tasks')
        print('  3. Build frontend and start working!')
    
    # Run the server
    app.run(debug=True, host='0.0.0.0', port=5000)

