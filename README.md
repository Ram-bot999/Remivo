# Remivo - Your Day, Remembered

A full-stack reminder and class planner web application built with Flask, HTML, CSS, and JavaScript. Remivo helps students and professionals organize their daily tasks, manage class schedules, and plan their day effectively.

## Features

- **User Authentication**: Secure registration, login, and logout with password hashing
- **Dashboard**: Overview of today's reminders, upcoming tasks, and schedule
- **Reminder Management**: Create, edit, delete, and complete reminders with categories
- **Class Timetable**: Manage weekly class schedules with time conflict detection
- **Smart Day Planner**: AI-assisted schedule generation based on available time
- **Calendar View**: Monthly calendar showing all reminders and classes
- **Reports & Progress**: Track completion rates and activity statistics
- **Dark/Light Theme**: Toggle between light and dark modes
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Browser Notifications**: Get notified about upcoming reminders

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Database**: SQLite (local and production with persistent disk)
- **Authentication**: Flask sessions with secure password hashing
- **Hosting**: Render
- **Server**: Gunicorn
- **Version Control**: Git

## Project Structure

```
Remivo/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment configuration
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── .env.example                # Environment variables template
├── templates/
│   └── index.html              # Main HTML template
├── static/
│   ├── css/
│   │   └── styles.css          # Stylesheet with themes
│   ├── js/
│   │   └── app.js              # Frontend JavaScript
│   └── images/                 # Image assets
└── tests/
    └── test_app.py             # Automated tests
```

## Local Installation (Windows)

### Prerequisites

1. **Python 3.8 or higher** - Download from [python.org](https://www.python.org/downloads/)
2. **Git** - Download from [git-scm.com](https://git-scm.com/download/win)

### Step 1: Install Python

1. Download Python installer from python.org
2. Run the installer and **check "Add Python to PATH"**
3. Verify installation by opening PowerShell and running:
   ```powershell
   python --version
   ```

### Step 2: Clone or Download the Project

If you have the project files already, skip to Step 3.

To clone from GitHub (after uploading):
```powershell
cd D:\
git clone https://github.com/YOUR_USERNAME/remivo.git
cd remivo
```

### Step 3: Create Virtual Environment

Open PowerShell in the Remivo directory and run:

```powershell
python -m venv venv
```

### Step 4: Activate Virtual Environment

```powershell
.\venv\Scripts\activate
```

You should see `(venv)` at the beginning of your PowerShell prompt.

### Step 5: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- Flask
- Flask-SQLAlchemy
- Gunicorn
- psycopg2-binary (for PostgreSQL support)

### Step 6: Run the Application

```powershell
python app.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
```

### Step 7: Open in Chrome

1. Open Google Chrome
2. Navigate to: `http://localhost:5000`
3. The Remivo application should load

## Testing the Application

### 1. Register a New Account

1. On the login screen, click the "Register" tab
2. Enter a username (e.g., "testuser")
3. Enter an email (e.g., "test@example.com")
4. Enter a password (minimum 6 characters)
5. Click "Register"
6. You should be automatically logged in and see the dashboard

### 2. Test Reminder Creation

1. Click the "+ Add" button in the "Today's Reminders" section
2. Enter a title (e.g., "Study for Math Exam")
3. Select a category (e.g., "Study")
4. Set a due date and time
5. Click "Save"
6. The reminder should appear in your list

### 3. Test Class Scheduling

1. Navigate to "Timetable" from the sidebar
2. Click "+ Add Class"
3. Enter subject (e.g., "Mathematics")
4. Select a day (e.g., "Monday")
5. Set start and end times (e.g., 09:00 - 10:00)
6. Click "Save"
7. The class should appear in your timetable

### 4. Test Day Planner

1. Navigate to "Day Planner"
2. Select some pending tasks from the list
3. Set available time (e.g., 2 hours)
4. Click "Generate Schedule"
5. You should see a generated schedule with time slots

### 5. Test Theme Toggle

1. Click the moon icon (🌙) in the sidebar header
2. The app should switch to dark mode
3. Click again to switch back to light mode

### 6. Test Logout

1. Click the "Logout" button in the sidebar footer
2. You should be returned to the login screen
3. Try to access dashboard - you should be denied

### 7. Run Automated Tests

```powershell
python -m pytest tests/test_app.py -v
```

Or with unittest:
```powershell
python -m unittest tests.test_app
```

## Uploading to GitHub

### Step 1: Initialize Git Repository

If not already initialized:

```powershell
cd D:\Remivo
git init
```

### Step 2: Create .gitignore

The project already includes a `.gitignore` file. Verify it exists.

### Step 3: Add Files to Git

```powershell
git add .
```

### Step 4: Create Initial Commit

```powershell
git commit -m "Initial commit: Remivo full-stack application"
```

### Step 5: Create GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the "+" icon in the top-right corner
3. Select "New repository"
4. Repository name: `remivo`
5. Description: "Your day, remembered - A reminder and class planner"
6. Make it **Public** (required for free Render hosting)
7. **Do not** initialize with README, .gitignore, or license (we have these)
8. Click "Create repository"

### Step 6: Link Local Repository to GitHub

Copy the repository URL from GitHub (e.g., `https://github.com/YOUR_USERNAME/remivo.git`)

```powershell
git remote add origin https://github.com/YOUR_USERNAME/remivo.git
git branch -M main
git push -u origin main
```

If you're asked for credentials:
- Username: Your GitHub username
- Password: Your **Personal Access Token** (not your GitHub password)

To create a Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name and select "repo" scope
4. Click "Generate token"
5. Copy the token (you won't see it again)

## Deploying to Render

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Sign Up"
3. Sign up with GitHub (recommended)
4. Verify your email if required

### Step 2: Connect GitHub to Render

1. After logging in to Render, click "New +"
2. Select "Web Service"
3. Click "Connect GitHub"
4. Authorize Render to access your GitHub account
5. Find and select your `remivo` repository
6. Click "Connect"

### Step 3: Configure Web Service

Render should auto-detect your configuration from `render.yaml`. If not:

**Name**: `remivo` (or your preferred name)

**Region**: Choose the region closest to you

**Branch**: `main`

**Runtime**: `Python 3`

**Build Command**: `pip install -r requirements.txt`

**Start Command**: `gunicorn app:app`

### Step 4: Configure Database

The `render.yaml` file includes persistent disk configuration. Render will:
1. Automatically allocate 1GB of persistent disk storage
2. Set the `RENDER_DATA_PATH` environment variable
3. The application will use SQLite with persistent storage

**Note**: This configuration uses SQLite with persistent disk, which is simpler and sufficient for most use cases. The database file persists between deployments.

### Step 5: Configure Environment Variables

Render automatically generates a `SECRET_KEY`. If you need to add custom variables:

1. Scroll to "Environment" section
2. Click "Add Environment Variable"
3. Add any required variables
4. Click "Save"

### Step 6: Deploy

1. Click "Create Web Service"
2. Wait for the build to complete (this may take 2-5 minutes)
3. You'll see a live URL when deployment is complete
4. Click the URL to open your deployed application

Example URL: `https://remivo.onrender.com`

### Step 7: Verify Deployment

1. Open the deployed URL in Chrome
2. Test registration
3. Test creating reminders and classes
4. Verify all features work as expected

## Environment Variables

The application uses the following environment variables:

### For Local Development

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///remivo.db
```

**Important**: Never commit the `.env` file to GitHub!

### For Production (Render)

Render automatically sets:
- `SECRET_KEY`: Auto-generated
- `RENDER_DATA_PATH`: Auto-generated (path to persistent disk)

The application uses SQLite with persistent disk storage on Render. No additional database configuration is needed.

You can view environment variables in:
1. Go to your web service on Render
2. Scroll to "Environment" section
3. View existing environment variables

## Database Configuration

### Local Development (SQLite)

The default configuration uses SQLite:
- Database file: `remivo.db` (created automatically)
- No additional setup required
- Data persists between application restarts

### Production (SQLite with Persistent Disk)

Render uses SQLite with persistent disk storage:
- 1GB persistent disk allocated in `render.yaml`
- Database file stored at `/opt/render/project/data/remivo.db`
- Data persists between deployments
- No additional database setup required
- Configured via `render.yaml`

**Note**: The persistent disk ensures your data will not be lost when redeploying. If you need to upgrade to PostgreSQL later, you can modify the `render.yaml` to add a PostgreSQL database service.

## Troubleshooting

### Issue: "python is not recognized"

**Solution**: Make sure you added Python to PATH during installation. Reinstall Python if needed, checking "Add Python to PATH".

### Issue: "pip is not recognized"

**Solution**: Use `python -m pip` instead of `pip`, or ensure Python Scripts folder is in your PATH.

### Issue: ModuleNotFoundError

**Solution**: Make sure you activated the virtual environment:
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Port 5000 already in use

**Solution**: Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Database locked (SQLite)

**Solution**: Close all connections to the database and restart the application. Only one instance should run at a time.

### Issue: GitHub authentication failed

**Solution**: Use a Personal Access Token instead of your password:
1. Generate a token in GitHub Settings
2. Use the token as your password when pushing

### Issue: Render deployment fails

**Common causes and solutions**:

1. **Build fails**: Check the build logs in Render dashboard
2. **Missing dependencies**: Ensure `requirements.txt` is complete
3. **Port error**: Ensure Flask runs on port 5000 (default) or update Render configuration
4. **Database error**: Verify PostgreSQL is created and connected

### Issue: Application works locally but not on Render

**Solutions**:

1. Check Render logs for errors
2. Verify environment variables are set
3. Ensure database connection is working
4. Check that `render.yaml` is properly configured

### Issue: "Module not found" on Render

**Solution**: Add the missing module to `requirements.txt` and redeploy.

### Issue: Changes not reflected after deployment

**Solution**:
1. Push changes to GitHub
2. Render auto-deploys on push to main branch
3. Wait for deployment to complete
4. Clear browser cache and reload

### Issue: Browser notifications not working

**Solutions**:
1. Ensure you granted permission when prompted
2. Check browser settings for notification permissions
3. Notifications only work when the website is open
4. Some browsers block notifications on HTTP (use HTTPS on Render)

## Security Best Practices

1. **Never commit secrets**: The `.gitignore` file prevents committing `.env` files
2. **Use strong passwords**: Enforce minimum password length (6 characters)
3. **Secure sessions**: Production uses secure cookie settings
4. **Password hashing**: All passwords are hashed using Werkzeug
5. **SQL injection protection**: Using SQLAlchemy ORM prevents SQL injection
6. **Authorization checks**: All user-specific endpoints verify user identity

## Performance Considerations

- Use PostgreSQL in production for better performance
- Consider adding database indexes for frequently queried fields
- Implement pagination for large reminder lists
- Add caching for frequently accessed data
- Optimize image assets if adding custom images

## Future Enhancements

Possible features to add later:
- Email notifications for reminders
- Parent/guardian sharing portal
- Mobile app (React Native or Flutter)
- Calendar export (iCal format)
- Recurring reminders
- File attachments for reminders
- Collaboration features for study groups
- Advanced analytics and insights

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Render logs for deployment issues
3. Check GitHub Issues for known problems
4. Consult Flask documentation: https://flask.palletsprojects.com/

## License

This project is open source and available for educational purposes.

## Acknowledgments

- Flask web framework
- Render hosting platform
- Modern CSS and JavaScript APIs

---

**Ready to get started?** Follow the local installation steps above to run Remivo on your computer, then deploy to Render to share it with the world!
