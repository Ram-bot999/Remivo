import unittest
import tempfile
import os
from app import app, db, User, Reminder, ClassSchedule
from datetime import datetime, date, time


class RemivoTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for testing
        self.db_fd, app.config['DATABASE_URI'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE_URI'])

    def test_health_endpoint(self):
        """Test the health endpoint returns success"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')

    def test_register_user(self):
        """Test user registration"""
        response = self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'testuser')

    def test_register_duplicate_username(self):
        """Test registration with duplicate username fails"""
        # First registration
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'password123'
        })

        # Second registration with same username
        response = self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_register_duplicate_email(self):
        """Test registration with duplicate email fails"""
        # First registration
        self.client.post('/api/register', json={
            'username': 'user1',
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Second registration with same email
        response = self.client.post('/api/register', json={
            'username': 'user2',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_register_short_password(self):
        """Test registration with short password fails"""
        response = self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        # Register user first
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Login
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('user', data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials fails"""
        response = self.client.post('/api/login', json={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)

    def test_create_reminder_authenticated(self):
        """Test creating reminder when authenticated"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create reminder
        response = self.client.post('/api/reminders', json={
            'title': 'Test Reminder',
            'description': 'Test description',
            'category': 'Study',
            'due_date': '2024-12-31',
            'due_time': '14:00'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('reminder', data)
        self.assertEqual(data['reminder']['title'], 'Test Reminder')

    def test_create_reminder_unauthenticated(self):
        """Test creating reminder without authentication fails"""
        response = self.client.post('/api/reminders', json={
            'title': 'Test Reminder',
            'due_date': '2024-12-31'
        })
        self.assertEqual(response.status_code, 401)

    def test_get_reminders_authenticated(self):
        """Test getting reminders when authenticated"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create reminder
        self.client.post('/api/reminders', json={
            'title': 'Test Reminder',
            'due_date': '2024-12-31'
        })

        # Get reminders
        response = self.client.get('/api/reminders')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('reminders', data)
        self.assertEqual(len(data['reminders']), 1)

    def test_update_reminder(self):
        """Test updating reminder"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create reminder
        create_response = self.client.post('/api/reminders', json={
            'title': 'Test Reminder',
            'due_date': '2024-12-31'
        })
        reminder_id = create_response.get_json()['reminder']['id']

        # Update reminder
        response = self.client.put(f'/api/reminders/{reminder_id}', json={
            'title': 'Updated Reminder',
            'completed': True
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['reminder']['title'], 'Updated Reminder')
        self.assertTrue(data['reminder']['completed'])

    def test_delete_reminder(self):
        """Test deleting reminder"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create reminder
        create_response = self.client.post('/api/reminders', json={
            'title': 'Test Reminder',
            'due_date': '2024-12-31'
        })
        reminder_id = create_response.get_json()['reminder']['id']

        # Delete reminder
        response = self.client.delete(f'/api/reminders/{reminder_id}')
        self.assertEqual(response.status_code, 200)

        # Verify deletion
        get_response = self.client.get('/api/reminders')
        data = get_response.get_json()
        self.assertEqual(len(data['reminders']), 0)

    def test_create_class(self):
        """Test creating class"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create class
        response = self.client.post('/api/classes', json={
            'subject': 'Math',
            'day_of_week': 'Monday',
            'start_time': '09:00',
            'end_time': '10:00',
            'color': '#4A90E2'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('class', data)
        self.assertEqual(data['class']['subject'], 'Math')

    def test_create_class_invalid_time_range(self):
        """Test creating class with invalid time range fails"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create class with end time before start time
        response = self.client.post('/api/classes', json={
            'subject': 'Math',
            'day_of_week': 'Monday',
            'start_time': '10:00',
            'end_time': '09:00'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_create_class_overlapping(self):
        """Test creating overlapping class fails"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create first class
        self.client.post('/api/classes', json={
            'subject': 'Math',
            'day_of_week': 'Monday',
            'start_time': '09:00',
            'end_time': '10:00'
        })

        # Create overlapping class
        response = self.client.post('/api/classes', json={
            'subject': 'Physics',
            'day_of_week': 'Monday',
            'start_time': '09:30',
            'end_time': '10:30'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_user_data_isolation(self):
        """Test that users cannot access each other's data"""
        # Register first user
        self.client.post('/api/register', json={
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'password123'
        })

        # Register second user
        self.client.post('/api/register', json={
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'password123'
        })

        # Login as user1 and create reminder
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'user1'

        self.client.post('/api/reminders', json={
            'title': 'User1 Reminder',
            'due_date': '2024-12-31'
        })

        # Login as user2
        with self.client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['username'] = 'user2'

        # Try to access user1's reminder
        response = self.client.put('/api/reminders/1', json={
            'title': 'Hacked'
        })
        self.assertEqual(response.status_code, 404)

        # User2 should only see their own reminders (none)
        response = self.client.get('/api/reminders')
        data = response.get_json()
        self.assertEqual(len(data['reminders']), 0)

    def test_dashboard_requires_auth(self):
        """Test dashboard requires authentication"""
        response = self.client.get('/api/dashboard')
        self.assertEqual(response.status_code, 401)

    def test_reminders_filter_by_category(self):
        """Test filtering reminders by category"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create reminders with different categories
        self.client.post('/api/reminders', json={
            'title': 'Study Reminder',
            'category': 'Study',
            'due_date': '2024-12-31'
        })
        self.client.post('/api/reminders', json={
            'title': 'Personal Reminder',
            'category': 'Personal',
            'due_date': '2024-12-31'
        })

        # Filter by Study category
        response = self.client.get('/api/reminders?category=Study')
        data = response.get_json()
        self.assertEqual(len(data['reminders']), 1)
        self.assertEqual(data['reminders'][0]['category'], 'Study')

    def test_reminders_filter_by_status(self):
        """Test filtering reminders by completion status"""
        # Register and login
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # Create reminders
        self.client.post('/api/reminders', json={
            'title': 'Pending Reminder',
            'due_date': '2024-12-31'
        })
        create_response = self.client.post('/api/reminders', json={
            'title': 'Completed Reminder',
            'due_date': '2024-12-31'
        })
        reminder_id = create_response.get_json()['reminder']['id']

        # Mark one as completed
        self.client.put(f'/api/reminders/{reminder_id}', json={'completed': True})

        # Filter by pending
        response = self.client.get('/api/reminders?status=pending')
        data = response.get_json()
        self.assertEqual(len(data['reminders']), 1)

        # Filter by completed
        response = self.client.get('/api/reminders?status=completed')
        data = response.get_json()
        self.assertEqual(len(data['reminders']), 1)


if __name__ == '__main__':
    unittest.main()
