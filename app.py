from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
import os
import json
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL if DATABASE_URL is provided (for future upgrades)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Use SQLite with persistent storage on Render
    db_path = os.environ.get('RENDER_DATA_PATH', '/opt/render/project/data')
    if not os.path.exists(db_path):
        os.makedirs(db_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_path, "remivo.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    preferences = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reminders = db.relationship('Reminder', backref='user', lazy=True, cascade='all, delete-orphan')
    classes = db.relationship('ClassSchedule', backref='user', lazy=True, cascade='all, delete-orphan')

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='General')
    due_date = db.Column(db.Date, nullable=False)
    due_time = db.Column(db.Time)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClassSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    color = db.Column(db.String(7), default='#4A90E2')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Authentication Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Initialize Database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html')
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username

        return jsonify({
            'message': 'Registration successful',
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid username or password'}), 401

        session['user_id'] = user.id
        session['username'] = user.username

        return jsonify({
            'message': 'Login successful',
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/user/current')
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': {'id': user.id, 'username': user.username, 'email': user.email}}), 200

# Reminder Routes
@app.route('/api/reminders', methods=['GET'])
@login_required
def get_reminders():
    try:
        user_id = session['user_id']
        category = request.args.get('category')
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'due_date')

        query = Reminder.query.filter_by(user_id=user_id)

        if category:
            query = query.filter_by(category=category)
        if status == 'completed':
            query = query.filter_by(completed=True)
        elif status == 'pending':
            query = query.filter_by(completed=False)

        if sort_by == 'due_date':
            query = query.order_by(Reminder.due_date, Reminder.due_time)
        elif sort_by == 'created':
            query = query.order_by(Reminder.created_at.desc())

        reminders = query.all()

        return jsonify({
            'reminders': [{
                'id': r.id,
                'title': r.title,
                'description': r.description,
                'category': r.category,
                'due_date': r.due_date.isoformat() if r.due_date else None,
                'due_time': r.due_time.strftime('%H:%M') if r.due_time else None,
                'completed': r.completed,
                'completed_at': r.completed_at.isoformat() if r.completed_at else None,
                'created_at': r.created_at.isoformat()
            } for r in reminders]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders', methods=['POST'])
@login_required
def create_reminder():
    try:
        data = request.get_json()
        user_id = session['user_id']

        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', 'General')
        due_date_str = data.get('due_date')
        due_time_str = data.get('due_time')

        if not title:
            return jsonify({'error': 'Title is required'}), 400

        if not due_date_str:
            return jsonify({'error': 'Due date is required'}), 400

        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        due_time = None
        if due_time_str:
            due_time = datetime.strptime(due_time_str, '%H:%M').time()

        reminder = Reminder(
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            due_date=due_date,
            due_time=due_time
        )
        db.session.add(reminder)
        db.session.commit()

        return jsonify({
            'message': 'Reminder created',
            'reminder': {
                'id': reminder.id,
                'title': reminder.title,
                'description': reminder.description,
                'category': reminder.category,
                'due_date': reminder.due_date.isoformat(),
                'due_time': reminder.due_time.strftime('%H:%M') if reminder.due_time else None,
                'completed': reminder.completed
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
@login_required
def update_reminder(reminder_id):
    try:
        user_id = session['user_id']
        reminder = Reminder.query.filter_by(id=reminder_id, user_id=user_id).first()

        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404

        data = request.get_json()

        if 'title' in data:
            reminder.title = data['title'].strip()
        if 'description' in data:
            reminder.description = data['description'].strip()
        if 'category' in data:
            reminder.category = data['category']
        if 'due_date' in data:
            reminder.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        if 'due_time' in data:
            if data['due_time']:
                reminder.due_time = datetime.strptime(data['due_time'], '%H:%M').time()
            else:
                reminder.due_time = None
        if 'completed' in data:
            reminder.completed = data['completed']
            if data['completed']:
                reminder.completed_at = datetime.utcnow()
            else:
                reminder.completed_at = None

        reminder.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Reminder updated',
            'reminder': {
                'id': reminder.id,
                'title': reminder.title,
                'description': reminder.description,
                'category': reminder.category,
                'due_date': reminder.due_date.isoformat(),
                'due_time': reminder.due_time.strftime('%H:%M') if reminder.due_time else None,
                'completed': reminder.completed
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
@login_required
def delete_reminder(reminder_id):
    try:
        user_id = session['user_id']
        reminder = Reminder.query.filter_by(id=reminder_id, user_id=user_id).first()

        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404

        db.session.delete(reminder)
        db.session.commit()

        return jsonify({'message': 'Reminder deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Class Routes
@app.route('/api/classes', methods=['GET'])
@login_required
def get_classes():
    try:
        user_id = session['user_id']
        classes = ClassSchedule.query.filter_by(user_id=user_id).order_by(
            ClassSchedule.day_of_week, ClassSchedule.start_time
        ).all()

        return jsonify({
            'classes': [{
                'id': c.id,
                'subject': c.subject,
                'day_of_week': c.day_of_week,
                'start_time': c.start_time.strftime('%H:%M'),
                'end_time': c.end_time.strftime('%H:%M'),
                'color': c.color
            } for c in classes]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes', methods=['POST'])
@login_required
def create_class():
    try:
        data = request.get_json()
        user_id = session['user_id']

        subject = data.get('subject', '').strip()
        day_of_week = data.get('day_of_week')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        color = data.get('color', '#4A90E2')

        if not subject:
            return jsonify({'error': 'Subject is required'}), 400
        if not day_of_week:
            return jsonify({'error': 'Day of week is required'}), 400
        if not start_time_str or not end_time_str:
            return jsonify({'error': 'Start and end times are required'}), 400

        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()

        if start_time >= end_time:
            return jsonify({'error': 'End time must be after start time'}), 400

        # Check for overlapping classes
        existing_classes = ClassSchedule.query.filter_by(
            user_id=user_id,
            day_of_week=day_of_week
        ).all()

        for existing in existing_classes:
            if (start_time < existing.end_time and end_time > existing.start_time):
                return jsonify({'error': 'Class time overlaps with existing class'}), 400

        class_schedule = ClassSchedule(
            user_id=user_id,
            subject=subject,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            color=color
        )
        db.session.add(class_schedule)
        db.session.commit()

        return jsonify({
            'message': 'Class created',
            'class': {
                'id': class_schedule.id,
                'subject': class_schedule.subject,
                'day_of_week': class_schedule.day_of_week,
                'start_time': class_schedule.start_time.strftime('%H:%M'),
                'end_time': class_schedule.end_time.strftime('%H:%M'),
                'color': class_schedule.color
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/<int:class_id>', methods=['PUT'])
@login_required
def update_class(class_id):
    try:
        user_id = session['user_id']
        class_schedule = ClassSchedule.query.filter_by(id=class_id, user_id=user_id).first()

        if not class_schedule:
            return jsonify({'error': 'Class not found'}), 404

        data = request.get_json()

        if 'subject' in data:
            class_schedule.subject = data['subject'].strip()
        if 'day_of_week' in data:
            class_schedule.day_of_week = data['day_of_week']
        if 'start_time' in data:
            class_schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
            class_schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        if 'color' in data:
            class_schedule.color = data['color']

        # Validate time range
        if class_schedule.start_time >= class_schedule.end_time:
            return jsonify({'error': 'End time must be after start time'}), 400

        # Check for overlapping classes (excluding current class)
        existing_classes = ClassSchedule.query.filter_by(
            user_id=user_id,
            day_of_week=class_schedule.day_of_week
        ).filter(ClassSchedule.id != class_id).all()

        for existing in existing_classes:
            if (class_schedule.start_time < existing.end_time and
                class_schedule.end_time > existing.start_time):
                return jsonify({'error': 'Class time overlaps with existing class'}), 400

        class_schedule.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Class updated',
            'class': {
                'id': class_schedule.id,
                'subject': class_schedule.subject,
                'day_of_week': class_schedule.day_of_week,
                'start_time': class_schedule.start_time.strftime('%H:%M'),
                'end_time': class_schedule.end_time.strftime('%H:%M'),
                'color': class_schedule.color
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes/<int:class_id>', methods=['DELETE'])
@login_required
def delete_class(class_id):
    try:
        user_id = session['user_id']
        class_schedule = ClassSchedule.query.filter_by(id=class_id, user_id=user_id).first()

        if not class_schedule:
            return jsonify({'error': 'Class not found'}), 404

        db.session.delete(class_schedule)
        db.session.commit()

        return jsonify({'message': 'Class deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard Data
@app.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    try:
        user_id = session['user_id']
        today = date.today()

        # Today's reminders
        today_reminders = Reminder.query.filter_by(
            user_id=user_id,
            due_date=today,
            completed=False
        ).order_by(Reminder.due_time).all()

        # Upcoming reminders (next 7 days)
        upcoming_date = today + timedelta(days=7)
        upcoming_reminders = Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.due_date > today,
            Reminder.due_date <= upcoming_date,
            Reminder.completed == False
        ).order_by(Reminder.due_date, Reminder.due_time).all()

        # Completed today
        completed_today = Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.completed == True,
            Reminder.completed_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()

        # Pending reminders
        pending_reminders = Reminder.query.filter_by(
            user_id=user_id,
            completed=False
        ).count()

        # Today's classes
        day_name = today.strftime('%A')
        today_classes = ClassSchedule.query.filter_by(
            user_id=user_id,
            day_of_week=day_name
        ).order_by(ClassSchedule.start_time).all()

        return jsonify({
            'today_reminders': [{
                'id': r.id,
                'title': r.title,
                'category': r.category,
                'due_time': r.due_time.strftime('%H:%M') if r.due_time else None
            } for r in today_reminders],
            'upcoming_reminders': [{
                'id': r.id,
                'title': r.title,
                'category': r.category,
                'due_date': r.due_date.isoformat(),
                'due_time': r.due_time.strftime('%H:%M') if r.due_time else None
            } for r in upcoming_reminders],
            'completed_today': completed_today,
            'pending_reminders': pending_reminders,
            'today_classes': [{
                'id': c.id,
                'subject': c.subject,
                'start_time': c.start_time.strftime('%H:%M'),
                'end_time': c.end_time.strftime('%H:%M'),
                'color': c.color
            } for c in today_classes]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Day Planner
@app.route('/api/planner/generate', methods=['POST'])
@login_required
def generate_schedule():
    try:
        data = request.get_json()
        user_id = session['user_id']

        selected_reminders = data.get('reminders', [])
        available_time = data.get('available_time', 2)  # hours
        priority = data.get('priority', 'normal')
        break_interval = data.get('break_interval', 15)  # minutes

        if not selected_reminders:
            return jsonify({'error': 'No reminders selected'}), 400

        # Get actual reminder objects
        reminders = Reminder.query.filter(
            Reminder.id.in_(selected_reminders),
            Reminder.user_id == user_id,
            Reminder.completed == False
        ).all()

        if not reminders:
            return jsonify({'error': 'No valid reminders found'}), 400

        # Simple scheduling algorithm
        available_minutes = available_time * 60
        break_minutes = break_interval
        task_duration = 30  # Default 30 minutes per task

        if priority == 'high':
            # Sort by due date
            reminders.sort(key=lambda r: r.due_date)
        elif priority == 'category':
            # Group by category
            reminders.sort(key=lambda r: r.category)

        schedule = []
        current_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        scheduled_count = 0
        unscheduled = []

        for reminder in reminders:
            if available_minutes >= task_duration:
                end_time = current_time + timedelta(minutes=task_duration)
                schedule.append({
                    'title': reminder.title,
                    'category': reminder.category,
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': end_time.strftime('%H:%M'),
                    'reminder_id': reminder.id
                })
                current_time = end_time + timedelta(minutes=break_minutes)
                available_minutes -= (task_duration + break_minutes)
                scheduled_count += 1
            else:
                unscheduled.append({
                    'id': reminder.id,
                    'title': reminder.title,
                    'category': reminder.category
                })

        return jsonify({
            'schedule': schedule,
            'scheduled_count': scheduled_count,
            'unscheduled': unscheduled,
            'message': f'Scheduled {scheduled_count} tasks' + (f'. {len(unscheduled)} tasks could not be scheduled due to insufficient time.' if unscheduled else '')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Calendar Data
@app.route('/api/calendar', methods=['GET'])
@login_required
def get_calendar():
    try:
        user_id = session['user_id']
        year = int(request.args.get('year', date.today().year))
        month = int(request.args.get('month', date.today().month))

        # Get reminders for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        reminders = Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.due_date >= start_date,
            Reminder.due_date < end_date
        ).all()

        # Get all classes
        classes = ClassSchedule.query.filter_by(user_id=user_id).all()

        # Map dates to events
        events = {}
        for reminder in reminders:
            day = reminder.due_date.day
            if day not in events:
                events[day] = []
            events[day].append({
                'type': 'reminder',
                'title': reminder.title,
                'category': reminder.category,
                'completed': reminder.completed,
                'id': reminder.id
            })

        for class_item in classes:
            # Find all dates in the month for this day of week
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_index = day_names.index(class_item.day_of_week)

            for day in range(1, 32):
                try:
                    check_date = date(year, month, day)
                    if check_date.weekday() == day_index:
                        if day not in events:
                            events[day] = []
                        events[day].append({
                            'type': 'class',
                            'title': class_item.subject,
                            'start_time': class_item.start_time.strftime('%H:%M'),
                            'end_time': class_item.end_time.strftime('%H:%M'),
                            'color': class_item.color,
                            'id': class_item.id
                        })
                except ValueError:
                    break

        return jsonify({
            'year': year,
            'month': month,
            'events': events
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Reports
@app.route('/api/reports', methods=['GET'])
@login_required
def get_reports():
    try:
        user_id = session['user_id']

        # Total reminders
        total_reminders = Reminder.query.filter_by(user_id=user_id).count()

        # Completed reminders
        completed_reminders = Reminder.query.filter_by(user_id=user_id, completed=True).count()

        # Pending reminders
        pending_reminders = total_reminders - completed_reminders

        # Completion rate
        completion_rate = (completed_reminders / total_reminders * 100) if total_reminders > 0 else 0

        # Total classes
        total_classes = ClassSchedule.query.filter_by(user_id=user_id).count()

        # Today's activity
        today = date.today()
        today_completed = Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.completed == True,
            Reminder.completed_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()

        # Weekly activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_completed = Reminder.query.filter(
            Reminder.user_id == user_id,
            Reminder.completed == True,
            Reminder.completed_at >= week_ago
        ).count()

        # Upcoming classes (today)
        day_name = today.strftime('%A')
        upcoming_classes = ClassSchedule.query.filter_by(
            user_id=user_id,
            day_of_week=day_name
        ).count()

        return jsonify({
            'total_reminders': total_reminders,
            'completed_reminders': completed_reminders,
            'pending_reminders': pending_reminders,
            'completion_rate': round(completion_rate, 1),
            'total_classes': total_classes,
            'today_completed': today_completed,
            'weekly_completed': weekly_completed,
            'upcoming_classes': upcoming_classes
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Preferences
@app.route('/api/preferences', methods=['GET'])
@login_required
def get_preferences():
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        preferences = json.loads(user.preferences) if user.preferences else {}
        return jsonify({'preferences': preferences}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preferences', methods=['PUT'])
@login_required
def update_preferences():
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        current_preferences = json.loads(user.preferences) if user.preferences else {}
        current_preferences.update(data)
        user.preferences = json.dumps(current_preferences)
        db.session.commit()

        return jsonify({'message': 'Preferences updated', 'preferences': current_preferences}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
