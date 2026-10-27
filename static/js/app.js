// Remivo Application JavaScript

class RemivoApp {
    constructor() {
        this.currentUser = null;
        this.currentView = 'dashboard';
        this.notificationsEnabled = false;
        this.init();
    }

    init() {
        this.checkAuth();
        this.bindEvents();
        this.initTheme();
        this.requestNotificationPermission();
    }

    // Authentication
    async checkAuth() {
        try {
            const response = await fetch('/api/user/current');
            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                this.showMainApp();
            } else {
                this.showAuthScreen();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            this.showAuthScreen();
        }
    }

    showAuthScreen() {
        document.getElementById('auth-screen').classList.remove('hidden');
        document.getElementById('main-app').classList.add('hidden');
    }

    showMainApp() {
        document.getElementById('auth-screen').classList.add('hidden');
        document.getElementById('main-app').classList.remove('hidden');
        document.getElementById('user-name-display').textContent = this.currentUser.username;
        this.loadDashboard();
    }

    async login(username, password) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentUser = data.user;
                this.showMainApp();
                this.showToast('Login successful!', 'success');
            } else {
                this.showAuthError(data.error);
            }
        } catch (error) {
            this.showAuthError('Login failed. Please try again.');
        }
    }

    async register(username, email, password) {
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentUser = data.user;
                this.showMainApp();
                this.showToast('Registration successful!', 'success');
            } else {
                this.showAuthError(data.error);
            }
        } catch (error) {
            this.showAuthError('Registration failed. Please try again.');
        }
    }

    async logout() {
        try {
            await fetch('/api/logout', { method: 'POST' });
            this.currentUser = null;
            this.showAuthScreen();
            this.showToast('Logged out successfully', 'info');
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }

    showAuthError(message) {
        const errorDiv = document.getElementById('auth-error');
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
        setTimeout(() => errorDiv.classList.remove('show'), 5000);
    }

    // Theme
    initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    }

    // Notifications
    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            this.notificationsEnabled = permission === 'granted';
        }
    }

    showNotification(title, body) {
        if (this.notificationsEnabled) {
            new Notification(title, { body });
        }
    }

    // Navigation
    navigateTo(view) {
        this.currentView = view;

        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === view) {
                item.classList.add('active');
            }
        });

        // Update views
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById(`${view}-view`).classList.add('active');

        // Load data for view
        switch (view) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'reminders':
                this.loadReminders();
                break;
            case 'timetable':
                this.loadTimetable();
                break;
            case 'planner':
                this.loadPlannerTasks();
                break;
            case 'calendar':
                this.loadCalendar();
                break;
            case 'reports':
                this.loadReports();
                break;
        }

        // Close mobile sidebar
        document.getElementById('sidebar').classList.remove('open');
    }

    // Dashboard
    async loadDashboard() {
        try {
            const response = await fetch('/api/dashboard');
            const data = await response.json();

            // Update stats
            document.getElementById('stat-completed').textContent = data.completed_today;
            document.getElementById('stat-pending').textContent = data.pending_reminders;
            document.getElementById('stat-classes').textContent = data.today_classes.length;

            // Update date
            const today = new Date();
            document.getElementById('current-date').textContent = today.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });

            // Render today's reminders
            this.renderReminderList('today-reminders', data.today_reminders);

            // Render today's classes
            this.renderClassList('today-classes', data.today_classes);

            // Render upcoming reminders
            this.renderReminderList('upcoming-reminders', data.upcoming_reminders);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        }
    }

    // Reminders
    async loadReminders() {
        try {
            const category = document.getElementById('filter-category').value;
            const status = document.getElementById('filter-status').value;
            const sortBy = document.getElementById('sort-reminders').value;

            let url = '/api/reminders?';
            if (category) url += `category=${category}&`;
            if (status) url += `status=${status}&`;
            url += `sort_by=${sortBy}`;

            const response = await fetch(url);
            const data = await response.json();

            this.renderReminderList('reminders-list', data.reminders);
        } catch (error) {
            console.error('Failed to load reminders:', error);
        }
    }

    renderReminderList(containerId, reminders) {
        const container = document.getElementById(containerId);

        if (!reminders || reminders.length === 0) {
            container.innerHTML = '<div class="empty-state">No reminders found</div>';
            return;
        }

        container.innerHTML = reminders.map(r => `
            <div class="reminder-item ${r.completed ? 'completed' : ''}" data-id="${r.id}">
                <input type="checkbox" class="reminder-checkbox"
                    ${r.completed ? 'checked' : ''}
                    onchange="app.toggleReminder(${r.id}, ${r.completed})">
                <div class="reminder-content">
                    <div class="reminder-title">${this.escapeHtml(r.title)}</div>
                    <div class="reminder-meta">
                        <span class="reminder-category">${this.escapeHtml(r.category)}</span>
                        ${r.due_date ? `<span>${r.due_date}</span>` : ''}
                        ${r.due_time ? `<span>${r.due_time}</span>` : ''}
                    </div>
                </div>
                <div class="reminder-actions">
                    <button class="btn-icon" onclick="app.editReminder(${r.id})" title="Edit">✏️</button>
                    <button class="btn-icon" onclick="app.deleteReminder(${r.id})" title="Delete">🗑️</button>
                </div>
            </div>
        `).join('');
    }

    async createReminder(data) {
        try {
            const response = await fetch('/api/reminders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showToast('Reminder created!', 'success');
                this.closeModal('reminder-modal');
                this.loadReminders();
                this.loadDashboard();
            } else {
                const error = await response.json();
                this.showToast(error.error, 'error');
            }
        } catch (error) {
            this.showToast('Failed to create reminder', 'error');
        }
    }

    async updateReminder(id, data) {
        try {
            const response = await fetch(`/api/reminders/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showToast('Reminder updated!', 'success');
                this.closeModal('reminder-modal');
                this.loadReminders();
                this.loadDashboard();
            } else {
                const error = await response.json();
                this.showToast(error.error, 'error');
            }
        } catch (error) {
            this.showToast('Failed to update reminder', 'error');
        }
    }

    async toggleReminder(id, currentStatus) {
        try {
            const response = await fetch(`/api/reminders/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ completed: !currentStatus })
            });

            if (response.ok) {
                this.loadReminders();
                this.loadDashboard();
            }
        } catch (error) {
            console.error('Failed to toggle reminder:', error);
        }
    }

    async deleteReminder(id) {
        if (!confirm('Are you sure you want to delete this reminder?')) return;

        try {
            const response = await fetch(`/api/reminders/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Reminder deleted', 'success');
                this.loadReminders();
                this.loadDashboard();
            }
        } catch (error) {
            this.showToast('Failed to delete reminder', 'error');
        }
    }

    editReminder(id) {
        // Find reminder data from current list
        const reminderItem = document.querySelector(`.reminder-item[data-id="${id}"]`);
        if (!reminderItem) return;

        const title = reminderItem.querySelector('.reminder-title').textContent;
        const category = reminderItem.querySelector('.reminder-category').textContent;

        document.getElementById('reminder-id').value = id;
        document.getElementById('reminder-title').value = title;
        document.getElementById('reminder-category').value = category;
        document.getElementById('reminder-modal-title').textContent = 'Edit Reminder';

        this.openModal('reminder-modal');
    }

    // Classes
    async loadTimetable(day = 'Monday') {
        try {
            const response = await fetch('/api/classes');
            const data = await response.json();

            const dayClasses = data.classes.filter(c => c.day_of_week === day);
            this.renderClassList('timetable-classes', dayClasses);
        } catch (error) {
            console.error('Failed to load timetable:', error);
        }
    }

    renderClassList(containerId, classes) {
        const container = document.getElementById(containerId);

        if (!classes || classes.length === 0) {
            container.innerHTML = '<div class="empty-state">No classes scheduled</div>';
            return;
        }

        container.innerHTML = classes.map(c => `
            <div class="class-item" data-id="${c.id}" style="border-left: 4px solid ${c.color}">
                <div class="class-time">${c.start_time} - ${c.end_time}</div>
                <div class="class-subject">${this.escapeHtml(c.subject)}</div>
                <div class="reminder-actions">
                    <button class="btn-icon" onclick="app.editClass(${c.id})" title="Edit">✏️</button>
                    <button class="btn-icon" onclick="app.deleteClass(${c.id})" title="Delete">🗑️</button>
                </div>
            </div>
        `).join('');
    }

    async createClass(data) {
        try {
            const response = await fetch('/api/classes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showToast('Class added!', 'success');
                this.closeModal('class-modal');
                this.loadTimetable();
                this.loadDashboard();
            } else {
                const error = await response.json();
                this.showToast(error.error, 'error');
            }
        } catch (error) {
            this.showToast('Failed to add class', 'error');
        }
    }

    async updateClass(id, data) {
        try {
            const response = await fetch(`/api/classes/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showToast('Class updated!', 'success');
                this.closeModal('class-modal');
                this.loadTimetable();
                this.loadDashboard();
            } else {
                const error = await response.json();
                this.showToast(error.error, 'error');
            }
        } catch (error) {
            this.showToast('Failed to update class', 'error');
        }
    }

    async deleteClass(id) {
        if (!confirm('Are you sure you want to delete this class?')) return;

        try {
            const response = await fetch(`/api/classes/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Class deleted', 'success');
                this.loadTimetable();
                this.loadDashboard();
            }
        } catch (error) {
            this.showToast('Failed to delete class', 'error');
        }
    }

    editClass(id) {
        const classItem = document.querySelector(`.class-item[data-id="${id}"]`);
        if (!classItem) return;

        const subject = classItem.querySelector('.class-subject').textContent;
        const time = classItem.querySelector('.class-time').textContent;
        const [start, end] = time.split(' - ');

        document.getElementById('class-id').value = id;
        document.getElementById('class-subject').value = subject;
        document.getElementById('class-start').value = start;
        document.getElementById('class-end').value = end;
        document.getElementById('class-modal-title').textContent = 'Edit Class';

        this.openModal('class-modal');
    }

    // Day Planner
    async loadPlannerTasks() {
        try {
            const response = await fetch('/api/reminders?status=pending');
            const data = await response.json();

            const container = document.getElementById('planner-tasks');

            if (!data.reminders || data.reminders.length === 0) {
                container.innerHTML = '<div class="empty-state">No pending tasks available</div>';
                return;
            }

            container.innerHTML = data.reminders.map(r => `
                <label class="task-checkbox">
                    <input type="checkbox" value="${r.id}" data-title="${this.escapeHtml(r.title)}" data-category="${this.escapeHtml(r.category)}">
                    <span>${this.escapeHtml(r.title)}</span>
                    <span class="reminder-category">${this.escapeHtml(r.category)}</span>
                </label>
            `).join('');
        } catch (error) {
            console.error('Failed to load planner tasks:', error);
        }
    }

    async generateSchedule() {
        const checkboxes = document.querySelectorAll('#planner-tasks input[type="checkbox"]:checked');
        const selectedReminders = Array.from(checkboxes).map(cb => parseInt(cb.value));

        if (selectedReminders.length === 0) {
            this.showToast('Please select at least one task', 'error');
            return;
        }

        const availableTime = parseInt(document.getElementById('available-time').value);
        const breakInterval = parseInt(document.getElementById('break-interval').value);
        const priority = document.getElementById('priority').value;

        try {
            const response = await fetch('/api/planner/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    reminders: selectedReminders,
                    available_time: availableTime,
                    break_interval: breakInterval,
                    priority: priority
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.renderSchedule(data);
                document.getElementById('generated-schedule').classList.remove('hidden');
                this.showToast(data.message, 'success');
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.showToast('Failed to generate schedule', 'error');
        }
    }

    renderSchedule(data) {
        const scheduleList = document.getElementById('schedule-list');
        const unscheduledTasks = document.getElementById('unscheduled-tasks');

        scheduleList.innerHTML = data.schedule.map(item => `
            <div class="schedule-item">
                <div class="schedule-time">${item.start_time} - ${item.end_time}</div>
                <div class="reminder-content">
                    <div class="reminder-title">${this.escapeHtml(item.title)}</div>
                    <div class="reminder-meta">
                        <span class="reminder-category">${this.escapeHtml(item.category)}</span>
                    </div>
                </div>
            </div>
        `).join('');

        if (data.unscheduled && data.unscheduled.length > 0) {
            unscheduledTasks.innerHTML = `
                <h4>Could not schedule ${data.unscheduled.length} tasks:</h4>
                <ul>
                    ${data.unscheduled.map(task => `<li>${this.escapeHtml(task.title)}</li>`).join('')}
                </ul>
            `;
            unscheduledTasks.classList.remove('hidden');
        } else {
            unscheduledTasks.classList.add('hidden');
        }
    }

    // Calendar
    calendarYear = new Date().getFullYear();
    calendarMonth = new Date().getMonth();

    async loadCalendar() {
        try {
            const response = await fetch(`/api/calendar?year=${this.calendarYear}&month=${this.calendarMonth + 1}`);
            const data = await response.json();

            this.renderCalendar(data);
        } catch (error) {
            console.error('Failed to load calendar:', error);
        }
    }

    renderCalendar(data) {
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];

        document.getElementById('calendar-month-year').textContent =
            `${monthNames[this.calendarMonth]} ${this.calendarYear}`;

        const container = document.getElementById('calendar-days');
        const firstDay = new Date(this.calendarYear, this.calendarMonth, 1).getDay();
        const daysInMonth = new Date(this.calendarYear, this.calendarMonth + 1, 0).getDate();
        const today = new Date();

        let html = '';

        // Empty cells before first day
        for (let i = 0; i < firstDay; i++) {
            html += '<div class="calendar-day empty"></div>';
        }

        // Days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = today.getDate() === day &&
                today.getMonth() === this.calendarMonth &&
                today.getFullYear() === this.calendarYear;

            const events = data.events[day] || [];
            const eventsHtml = events.slice(0, 3).map(e =>
                `<div class="calendar-event ${e.type}">${this.escapeHtml(e.title)}</div>`
            ).join('');

            html += `
                <div class="calendar-day ${isToday ? 'today' : ''}" onclick="app.addReminderToDay(${day})">
                    <div class="calendar-day-number">${day}</div>
                    ${eventsHtml}
                </div>
            `;
        }

        container.innerHTML = html;
    }

    changeCalendarMonth(delta) {
        this.calendarMonth += delta;

        if (this.calendarMonth > 11) {
            this.calendarMonth = 0;
            this.calendarYear++;
        } else if (this.calendarMonth < 0) {
            this.calendarMonth = 11;
            this.calendarYear--;
        }

        this.loadCalendar();
    }

    addReminderToDay(day) {
        const date = new Date(this.calendarYear, this.calendarMonth, day);
        const dateStr = date.toISOString().split('T')[0];

        document.getElementById('reminder-id').value = '';
        document.getElementById('reminder-title').value = '';
        document.getElementById('reminder-description').value = '';
        document.getElementById('reminder-category').value = 'General';
        document.getElementById('reminder-date').value = dateStr;
        document.getElementById('reminder-time').value = '';
        document.getElementById('reminder-modal-title').textContent = 'Add Reminder';

        this.openModal('reminder-modal');
    }

    // Reports
    async loadReports() {
        try {
            const response = await fetch('/api/reports');
            const data = await response.json();

            document.getElementById('report-total').textContent = data.total_reminders;
            document.getElementById('report-completed').textContent = data.completed_reminders;
            document.getElementById('report-pending').textContent = data.pending_reminders;
            document.getElementById('report-rate').textContent = `${data.completion_rate}%`;
            document.getElementById('report-classes').textContent = data.total_classes;
            document.getElementById('report-today-classes').textContent = data.upcoming_classes;
            document.getElementById('report-today-activity').textContent = data.today_completed;
            document.getElementById('report-weekly-activity').textContent = data.weekly_completed;
        } catch (error) {
            console.error('Failed to load reports:', error);
        }
    }

    // Modals
    openModal(modalId) {
        document.getElementById('modal-overlay').classList.remove('hidden');
        document.getElementById(modalId).classList.remove('hidden');
    }

    closeModal(modalId) {
        document.getElementById('modal-overlay').classList.add('hidden');
        document.getElementById(modalId).classList.add('hidden');
    }

    // Toast
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Utility
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Event Binding
    bindEvents() {
        // Auth tabs
        document.querySelectorAll('.auth-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));

                e.target.classList.add('active');
                const tabName = e.target.dataset.tab;
                document.getElementById(`${tabName}-form`).classList.add('active');
            });
        });

        // Login form
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            this.login(username, password);
        });

        // Register form
        document.getElementById('register-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('register-username').value;
            const email = document.getElementById('register-email').value;
            const password = document.getElementById('register-password').value;
            this.register(username, email, password);
        });

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => this.logout());

        // Theme toggle
        document.getElementById('theme-toggle-mobile').addEventListener('click', () => this.toggleTheme());
        document.getElementById('theme-toggle-desktop').addEventListener('click', () => this.toggleTheme());

        // Mobile menu
        document.getElementById('menu-toggle').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('open');
        });

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateTo(item.dataset.view);
            });
        });

        // Quick add buttons
        document.getElementById('quick-add-reminder').addEventListener('click', () => {
            document.getElementById('reminder-id').value = '';
            document.getElementById('reminder-title').value = '';
            document.getElementById('reminder-description').value = '';
            document.getElementById('reminder-category').value = 'General';
            document.getElementById('reminder-date').value = new Date().toISOString().split('T')[0];
            document.getElementById('reminder-time').value = '';
            document.getElementById('reminder-modal-title').textContent = 'Add Reminder';
            this.openModal('reminder-modal');
        });

        document.getElementById('quick-add-class').addEventListener('click', () => {
            document.getElementById('class-id').value = '';
            document.getElementById('class-subject').value = '';
            document.getElementById('class-day').value = 'Monday';
            document.getElementById('class-start').value = '';
            document.getElementById('class-end').value = '';
            document.getElementById('class-color').value = '#4A90E2';
            document.getElementById('class-modal-title').textContent = 'Add Class';
            this.openModal('class-modal');
        });

        // Add reminder button
        document.getElementById('add-reminder-btn').addEventListener('click', () => {
            document.getElementById('reminder-id').value = '';
            document.getElementById('reminder-title').value = '';
            document.getElementById('reminder-description').value = '';
            document.getElementById('reminder-category').value = 'General';
            document.getElementById('reminder-date').value = new Date().toISOString().split('T')[0];
            document.getElementById('reminder-time').value = '';
            document.getElementById('reminder-modal-title').textContent = 'Add Reminder';
            this.openModal('reminder-modal');
        });

        // Add class button
        document.getElementById('add-class-btn').addEventListener('click', () => {
            document.getElementById('class-id').value = '';
            document.getElementById('class-subject').value = '';
            document.getElementById('class-day').value = 'Monday';
            document.getElementById('class-start').value = '';
            document.getElementById('class-end').value = '';
            document.getElementById('class-color').value = '#4A90E2';
            document.getElementById('class-modal-title').textContent = 'Add Class';
            this.openModal('class-modal');
        });

        // Reminder filters
        document.getElementById('filter-category').addEventListener('change', () => this.loadReminders());
        document.getElementById('filter-status').addEventListener('change', () => this.loadReminders());
        document.getElementById('sort-reminders').addEventListener('change', () => this.loadReminders());

        // Timetable day tabs
        document.querySelectorAll('.day-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.day-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                this.loadTimetable(e.target.dataset.day);
            });
        });

        // Generate schedule
        document.getElementById('generate-schedule').addEventListener('click', () => this.generateSchedule());

        // Calendar navigation
        document.getElementById('prev-month').addEventListener('click', () => this.changeCalendarMonth(-1));
        document.getElementById('next-month').addEventListener('click', () => this.changeCalendarMonth(1));

        // Modal close buttons
        document.getElementById('close-reminder-modal').addEventListener('click', () => this.closeModal('reminder-modal'));
        document.getElementById('cancel-reminder').addEventListener('click', () => this.closeModal('reminder-modal'));
        document.getElementById('close-class-modal').addEventListener('click', () => this.closeModal('class-modal'));
        document.getElementById('cancel-class').addEventListener('click', () => this.closeModal('class-modal'));

        // Modal overlay click
        document.getElementById('modal-overlay').addEventListener('click', (e) => {
            if (e.target.id === 'modal-overlay') {
                document.getElementById('modal-overlay').classList.add('hidden');
                document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
            }
        });

        // Reminder form submit
        document.getElementById('reminder-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const id = document.getElementById('reminder-id').value;
            const data = {
                title: document.getElementById('reminder-title').value,
                description: document.getElementById('reminder-description').value,
                category: document.getElementById('reminder-category').value,
                due_date: document.getElementById('reminder-date').value,
                due_time: document.getElementById('reminder-time').value
            };

            if (id) {
                this.updateReminder(parseInt(id), data);
            } else {
                this.createReminder(data);
            }
        });

        // Class form submit
        document.getElementById('class-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const id = document.getElementById('class-id').value;
            const data = {
                subject: document.getElementById('class-subject').value,
                day_of_week: document.getElementById('class-day').value,
                start_time: document.getElementById('class-start').value,
                end_time: document.getElementById('class-end').value,
                color: document.getElementById('class-color').value
            };

            if (id) {
                this.updateClass(parseInt(id), data);
            } else {
                this.createClass(data);
            }
        });
    }
}

// Initialize app
const app = new RemivoApp();
