#!/usr/bin/env python3
"""
GALION.STUDIO - Web Admin Panel
Control everything from your browser, not cursor!
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import subprocess
import requests
import psutil
import os
import signal
import time
import json

app = Flask(__name__)
CORS(app)

# Store process IDs
PROCESSES = {
    'backend': None,
    'frontend': None
}

# Admin panel HTML
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>GALION.STUDIO - Admin Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0A0A0A;
            color: #FFF;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            font-size: 32px;
            margin-bottom: 10px;
            color: #00D9FF;
        }
        .subtitle {
            color: #A0A0A0;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: linear-gradient(135deg, #2A2A2A 0%, #1A1A1A 100%);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #3A3A3A;
        }
        .card h2 {
            font-size: 18px;
            margin-bottom: 16px;
            color: #00D9FF;
        }
        .status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-dot.running { background: #00FF88; }
        .status-dot.stopped { background: #FF3B3B; }
        .status-dot.starting { background: #FFB800; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #2A2A2A;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 16px;
            position: relative;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00D9FF 0%, #00FF88 100%);
            transition: width 0.5s ease-out;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: 600;
        }
        button {
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
            margin-right: 10px;
        }
        .btn-start {
            background: #00FF88;
            color: #000;
        }
        .btn-start:hover {
            background: #00DD77;
            transform: translateY(-1px);
        }
        .btn-stop {
            background: #FF3B3B;
            color: #FFF;
        }
        .btn-stop:hover {
            background: #DD3333;
        }
        .btn-secondary {
            background: #2A2A2A;
            color: #FFF;
        }
        .btn-secondary:hover {
            background: #3A3A3A;
        }
        .log {
            background: #1A1A1A;
            border: 1px solid #2A2A2A;
            border-radius: 8px;
            padding: 16px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        .log-entry {
            margin-bottom: 8px;
            color: #A0A0A0;
        }
        .log-entry.success { color: #00FF88; }
        .log-entry.error { color: #FF3B3B; }
        .log-entry.info { color: #00D9FF; }
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        .metric {
            background: #2A2A2A;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
        }
        .metric-label { color: #A0A0A0; }
        .metric-value { color: #00FF88; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 GALION.STUDIO - Admin Panel</h1>
        <p class="subtitle">Control everything from your browser. No cursor needed!</p>

        <div class="quick-actions">
            <button class="btn-start" onclick="startAll()">▶ Start All</button>
            <button class="btn-stop" onclick="stopAll()">⏹ Stop All</button>
            <button class="btn-secondary" onclick="restartAll()">🔄 Restart All</button>
            <button class="btn-secondary" onclick="openApp()">🌐 Open App</button>
            <button class="btn-secondary" onclick="updateAnalytics()">📊 Refresh Analytics</button>
        </div>

        <div class="grid">
            <!-- Backend Card -->
            <div class="card">
                <h2>Backend Server</h2>
                <div class="status">
                    <div class="status-dot" id="backend-dot"></div>
                    <span id="backend-status">Checking...</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="backend-progress" style="width: 0%">0%</div>
                </div>
                <div class="metric">
                    <span class="metric-label">Port</span>
                    <span class="metric-value">5000</span>
                </div>
                <div class="metric">
                    <span class="metric-label">URL</span>
                    <span class="metric-value">localhost:5000</span>
                </div>
                <button class="btn-start" onclick="startBackend()">Start Backend</button>
                <button class="btn-stop" onclick="stopBackend()">Stop</button>
            </div>

            <!-- Frontend Card -->
            <div class="card">
                <h2>Frontend App</h2>
                <div class="status">
                    <div class="status-dot" id="frontend-dot"></div>
                    <span id="frontend-status">Checking...</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="frontend-progress" style="width: 0%">0%</div>
                </div>
                <div class="metric">
                    <span class="metric-label">Port</span>
                    <span class="metric-value">3001</span>
                </div>
                <div class="metric">
                    <span class="metric-label">URL</span>
                    <span class="metric-value">localhost:3001</span>
                </div>
                <button class="btn-start" onclick="startFrontend()">Start Frontend</button>
                <button class="btn-stop" onclick="stopFrontend()">Stop</button>
            </div>

            <!-- System Info Card -->
            <div class="card">
                <h2>System Info</h2>
                <div class="metric">
                    <span class="metric-label">CPU Usage</span>
                    <span class="metric-value" id="cpu-usage">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory</span>
                    <span class="metric-value" id="memory-usage">0 MB</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Backend PID</span>
                    <span class="metric-value" id="backend-pid">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Frontend PID</span>
                    <span class="metric-value" id="frontend-pid">-</span>
                </div>
                <button class="btn-secondary" onclick="seedDatabase()">🌱 Seed Database</button>
            </div>
        </div>

        <!-- Analytics Section -->
        <div class="card" style="grid-column: 1 / -1;">
            <h2>📊 Analytics Dashboard</h2>
            <div id="analytics-container">
                <div class="metric">
                    <span class="metric-label">Loading analytics...</span>
                    <span class="metric-value">Please wait</span>
                </div>
            </div>
        </div>

        <!-- Logs -->
        <div class="card" style="grid-column: 1 / -1;">
            <h2>Activity Log</h2>
            <div class="log" id="log"></div>
        </div>
    </div>

    <script>
        function log(message, type = 'info') {
            const logEl = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            const timestamp = new Date().toLocaleTimeString();
            entry.textContent = `[${timestamp}] ${message}`;
            logEl.appendChild(entry);
            logEl.scrollTop = logEl.scrollHeight;
        }

        async function api(endpoint, method = 'POST') {
            try {
                const response = await fetch(`http://localhost:9000${endpoint}`, { method });
                const data = await response.json();
                return data;
            } catch (error) {
                log(`Error: ${error.message}`, 'error');
                return null;
            }
        }

        async function startBackend() {
            log('Starting backend...', 'info');
            updateProgress('backend', 10, 'Starting...');
            const result = await api('/api/admin/start-backend');
            if (result && result.status === 'success') {
                log('Backend started successfully!', 'success');
                simulateProgress('backend', 100);
            } else {
                log('Failed to start backend', 'error');
            }
        }

        async function stopBackend() {
            log('Stopping backend...', 'info');
            const result = await api('/api/admin/stop-backend');
            if (result && result.status === 'success') {
                log('Backend stopped', 'success');
                updateProgress('backend', 0, 'Stopped');
            }
        }

        async function startFrontend() {
            log('Starting frontend...', 'info');
            updateProgress('frontend', 10, 'Installing dependencies...');
            const result = await api('/api/admin/start-frontend');
            if (result && result.status === 'success') {
                log('Frontend started successfully!', 'success');
                simulateProgress('frontend', 100, [
                    { progress: 20, text: 'Installing...' },
                    { progress: 40, text: 'Compiling...' },
                    { progress: 70, text: 'Building...' },
                    { progress: 90, text: 'Starting server...' },
                    { progress: 100, text: 'Ready!' }
                ]);
            }
        }

        async function stopFrontend() {
            log('Stopping frontend...', 'info');
            const result = await api('/api/admin/stop-frontend');
            if (result && result.status === 'success') {
                log('Frontend stopped', 'success');
                updateProgress('frontend', 0, 'Stopped');
            }
        }

        async function startAll() {
            log('Starting all services...', 'info');
            await startBackend();
            setTimeout(() => seedDatabase(), 5000);
            setTimeout(() => startFrontend(), 8000);
        }

        async function stopAll() {
            log('Stopping all services...', 'info');
            await stopBackend();
            await stopFrontend();
        }

        async function restartAll() {
            await stopAll();
            setTimeout(() => startAll(), 2000);
        }

        async function seedDatabase() {
            log('Seeding database...', 'info');
            try {
                const response = await fetch('http://localhost:5000/api/seed', { method: 'POST' });
                const data = await response.json();
                log(`Database seeded: ${data.users} users, ${data.tasks} tasks`, 'success');
            } catch (error) {
                log('Failed to seed database (backend not running?)', 'error');
            }
        }

        function openApp() {
            window.open('http://localhost:3001', '_blank');
            log('Opening GALION.STUDIO app...', 'info');
        }

        function updateProgress(service, percent, text) {
            const progressEl = document.getElementById(`${service}-progress`);
            progressEl.style.width = `${percent}%`;
            progressEl.textContent = text || `${percent}%`;
            
            const dot = document.getElementById(`${service}-dot`);
            const status = document.getElementById(`${service}-status`);
            
            if (percent === 0) {
                dot.className = 'status-dot stopped';
                status.textContent = 'Stopped';
            } else if (percent === 100) {
                dot.className = 'status-dot running';
                status.textContent = 'Running';
            } else {
                dot.className = 'status-dot starting';
                status.textContent = text || 'Starting...';
            }
        }

        function simulateProgress(service, target, steps = null) {
            if (steps) {
                let index = 0;
                const interval = setInterval(() => {
                    if (index < steps.length) {
                        updateProgress(service, steps[index].progress, steps[index].text);
                        index++;
                    } else {
                        clearInterval(interval);
                    }
                }, 3000);
            } else {
                updateProgress(service, target, target === 100 ? 'Running' : 'Starting...');
            }
        }

        // Check status every 3 seconds
        async function checkStatus() {
            const status = await api('/api/admin/status', 'GET');
            if (status) {
                // Update backend
                if (status.backend.running) {
                    updateProgress('backend', 100, 'Running');
                } else {
                    updateProgress('backend', 0, 'Stopped');
                }
                
                // Update frontend
                if (status.frontend.running) {
                    updateProgress('frontend', 100, 'Running');
                } else {
                    updateProgress('frontend', 0, 'Stopped');
                }

                // Update PIDs
                document.getElementById('backend-pid').textContent = status.backend.pid || '-';
                document.getElementById('frontend-pid').textContent = status.frontend.pid || '-';
                
                // Update system info
                document.getElementById('cpu-usage').textContent = status.system.cpu + '%';
                document.getElementById('memory-usage').textContent = status.system.memory;
            }
        }

        // Fetch and display analytics
        async function updateAnalytics() {
            const container = document.getElementById('analytics-container');
            
            try {
                const analytics = await api('/api/admin/analytics', 'GET');
                
                if (analytics && !analytics.error) {
                    // Build analytics HTML
                    let html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px;">';
                    
                    // Database Stats
                    html += '<div style="background: #1A1A1A; padding: 16px; border-radius: 8px;">';
                    html += '<h3 style="color: #00D9FF; margin-bottom: 12px;">📊 Database</h3>';
                    html += `<div class="metric"><span class="metric-label">Users</span><span class="metric-value">${analytics.database.total_users || 0}</span></div>`;
                    html += `<div class="metric"><span class="metric-label">Workspaces</span><span class="metric-value">${analytics.database.total_workspaces || 0}</span></div>`;
                    html += `<div class="metric"><span class="metric-label">Tasks</span><span class="metric-value">${analytics.database.total_tasks || 0}</span></div>`;
                    html += `<div class="metric"><span class="metric-label">Time Logs</span><span class="metric-value">${analytics.database.total_time_logs || 0}</span></div>`;
                    html += '</div>';
                    
                    // Tasks Analytics
                    if (analytics.tasks) {
                        html += '<div style="background: #1A1A1A; padding: 16px; border-radius: 8px;">';
                        html += '<h3 style="color: #00D9FF; margin-bottom: 12px;">📝 Tasks</h3>';
                        html += `<div class="metric"><span class="metric-label">Total Tasks</span><span class="metric-value">${analytics.tasks.total || 0}</span></div>`;
                        html += `<div class="metric"><span class="metric-label">Backlog</span><span class="metric-value">${analytics.tasks.by_status?.backlog || 0}</span></div>`;
                        html += `<div class="metric"><span class="metric-label">In Progress</span><span class="metric-value">${analytics.tasks.by_status?.in_progress || 0}</span></div>`;
                        html += `<div class="metric"><span class="metric-label">Done</span><span class="metric-value">${analytics.tasks.by_status?.done || 0}</span></div>`;
                        html += `<div class="metric"><span class="metric-label">Est. Hours</span><span class="metric-value">${analytics.tasks.total_estimated_hours || 0}h</span></div>`;
                        html += `<div class="metric"><span class="metric-label">Est. Cost</span><span class="metric-value">$${analytics.tasks.total_estimated_cost || 0}</span></div>`;
                        html += '</div>';
                    }
                    
                    // Time Tracking Analytics
                    if (analytics.time_tracking) {
                        html += '<div style="background: #1A1A1A; padding: 16px; border-radius: 8px;">';
                        html += '<h3 style="color: #00D9FF; margin-bottom: 12px;">⏱️ Time Tracking</h3>';
                        html += `<div class="metric"><span class="metric-label">Total Entries</span><span class="metric-value">${analytics.time_tracking.total_entries || 0}</span></div>`;
                        html += `<div class="metric"><span class="metric-label">Hours Logged</span><span class="metric-value">${analytics.time_tracking.total_hours_logged || 0}h</span></div>`;
                        html += `<div class="metric"><span class="metric-label">Amount Earned</span><span class="metric-value">$${analytics.time_tracking.total_amount_earned || 0}</span></div>`;
                        html += `<div class="metric"><span class="metric-label">Avg Rate</span><span class="metric-value">$${analytics.time_tracking.average_hourly_rate || 0}/h</span></div>`;
                        html += '</div>';
                    }
                    
                    // Compensation Analytics
                    if (analytics.compensation) {
                        html += '<div style="background: #1A1A1A; padding: 16px; border-radius: 8px;">';
                        html += '<h3 style="color: #00D9FF; margin-bottom: 12px;">💰 Compensation</h3>';
                        html += `<div class="metric"><span class="metric-label">Total Paid</span><span class="metric-value">$${analytics.compensation.total_paid || 0}</span></div>`;
                        html += `<div class="metric"><span class="metric-label">Avg Rate</span><span class="metric-value">$${analytics.compensation.average_rate || 0}/h</span></div>`;
                        if (analytics.compensation.highest_earner) {
                            html += `<div class="metric"><span class="metric-label">Top Earner</span><span class="metric-value">${analytics.compensation.highest_earner.user_name}</span></div>`;
                            html += `<div class="metric"><span class="metric-label">Amount</span><span class="metric-value">$${analytics.compensation.highest_earner.total_amount || 0}</span></div>`;
                        }
                        html += '</div>';
                    }
                    
                    html += '</div>';
                    
                    // User List
                    if (analytics.database.users && analytics.database.users.length > 0) {
                        html += '<div style="margin-top: 20px; background: #1A1A1A; padding: 16px; border-radius: 8px;">';
                        html += '<h3 style="color: #00D9FF; margin-bottom: 12px;">👥 Users</h3>';
                        html += '<table style="width: 100%; color: #FFF; border-collapse: collapse;">';
                        html += '<tr style="border-bottom: 1px solid #3A3A3A;"><th style="text-align: left; padding: 8px;">Name</th><th style="text-align: left; padding: 8px;">Email</th><th style="text-align: left; padding: 8px;">Rate</th><th style="text-align: left; padding: 8px;">Role</th></tr>';
                        analytics.database.users.forEach(user => {
                            html += `<tr style="border-bottom: 1px solid #2A2A2A;"><td style="padding: 8px;">${user.name}</td><td style="padding: 8px;">${user.email}</td><td style="padding: 8px;">$${user.hourly_rate}/h</td><td style="padding: 8px;">${user.role}</td></tr>`;
                        });
                        html += '</table></div>';
                    }
                    
                    container.innerHTML = html;
                } else {
                    container.innerHTML = `<div class="metric"><span class="metric-label">${analytics?.message || 'Backend not running'}</span><span class="metric-value">Start backend to see analytics</span></div>`;
                }
            } catch (error) {
                container.innerHTML = '<div class="metric"><span class="metric-label">Error loading analytics</span><span class="metric-value">Check backend status</span></div>';
            }
        }

        // Initial check and periodic updates
        checkStatus();
        updateAnalytics();
        setInterval(checkStatus, 3000);
        setInterval(updateAnalytics, 5000);  // Update analytics every 5 seconds
        
        log('Admin panel loaded', 'success');
        log('Click "Start All" to launch GALION.STUDIO', 'info');
        log('Analytics dashboard updating every 5 seconds', 'info');
    </script>
</body>
</html>
"""

def check_port(port):
    """Check if a port is in use"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return True
    return False

@app.route('/')
def admin_panel():
    """Serve admin panel"""
    return render_template_string(ADMIN_HTML)

@app.route('/api/admin/status', methods=['GET'])
def get_status():
    """Get status of all services"""
    backend_running = check_port(5000)
    frontend_running = check_port(3001)
    
    return jsonify({
        'backend': {
            'running': backend_running,
            'pid': PROCESSES.get('backend'),
            'port': 5000
        },
        'frontend': {
            'running': frontend_running,
            'pid': PROCESSES.get('frontend'),
            'port': 3001
        },
        'system': {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': f"{psutil.Process().memory_info().rss / 1024 / 1024:.0f} MB"
        }
    })

@app.route('/api/admin/analytics', methods=['GET'])
def get_analytics():
    """Get comprehensive analytics for all services and features"""
    try:
        analytics_data = {
            'database': {},
            'tasks': {},
            'compensation': {},
            'time_tracking': {},
            'workspaces': {}
        }
        
        # Check if backend is running
        if not check_port(5000):
            return jsonify({
                'error': 'Backend not running',
                'message': 'Start the backend to see analytics'
            }), 503
        
        # Fetch database statistics
        try:
            # Get user count
            users_response = requests.get('http://localhost:5000/api/users', timeout=2)
            users_data = users_response.json() if users_response.ok else []
            analytics_data['database']['total_users'] = len(users_data)
            analytics_data['database']['users'] = users_data
            
            # Get workspace count
            workspaces_response = requests.get('http://localhost:5000/api/workspaces', timeout=2)
            workspaces_data = workspaces_response.json() if workspaces_response.ok else []
            analytics_data['database']['total_workspaces'] = len(workspaces_data)
            analytics_data['workspaces']['list'] = workspaces_data
            
            # Get tasks
            tasks_response = requests.get('http://localhost:5000/api/tasks', timeout=2)
            tasks_data = tasks_response.json() if tasks_response.ok else []
            analytics_data['database']['total_tasks'] = len(tasks_data)
            
            # Task analytics by status
            status_counts = {'backlog': 0, 'in_progress': 0, 'done': 0}
            priority_counts = {'low': 0, 'medium': 0, 'high': 0, 'urgent': 0}
            total_estimated_cost = 0
            total_estimated_hours = 0
            
            for task in tasks_data:
                status = task.get('status', 'backlog')
                priority = task.get('priority', 'medium')
                status_counts[status] = status_counts.get(status, 0) + 1
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                total_estimated_cost += task.get('total_cost', 0)
                total_estimated_hours += task.get('hours_estimate', 0)
            
            analytics_data['tasks'] = {
                'total': len(tasks_data),
                'by_status': status_counts,
                'by_priority': priority_counts,
                'total_estimated_cost': round(total_estimated_cost, 2),
                'total_estimated_hours': round(total_estimated_hours, 2),
                'recent_tasks': tasks_data[:5]  # Last 5 tasks
            }
            
            # Get time logs
            time_logs_response = requests.get('http://localhost:5000/api/time-logs', timeout=2)
            time_logs_data = time_logs_response.json() if time_logs_response.ok else []
            analytics_data['database']['total_time_logs'] = len(time_logs_data)
            
            # Time tracking analytics
            total_hours_logged = sum(log.get('hours', 0) for log in time_logs_data)
            total_amount_earned = sum(log.get('amount', 0) for log in time_logs_data)
            
            analytics_data['time_tracking'] = {
                'total_entries': len(time_logs_data),
                'total_hours_logged': round(total_hours_logged, 2),
                'total_amount_earned': round(total_amount_earned, 2),
                'average_hourly_rate': round(total_amount_earned / total_hours_logged, 2) if total_hours_logged > 0 else 0,
                'recent_logs': time_logs_data[:5]
            }
            
            # Compensation analytics (if workspace exists)
            if workspaces_data:
                workspace_id = workspaces_data[0].get('id')
                comp_response = requests.get(
                    f'http://localhost:5000/api/analytics/compensation?workspace_id={workspace_id}',
                    timeout=2
                )
                comp_data = comp_response.json() if comp_response.ok else []
                
                total_compensation = sum(user.get('total_amount', 0) for user in comp_data)
                
                analytics_data['compensation'] = {
                    'total_paid': round(total_compensation, 2),
                    'by_user': comp_data,
                    'highest_earner': max(comp_data, key=lambda x: x.get('total_amount', 0)) if comp_data else None,
                    'average_rate': round(sum(user.get('hourly_rate', 0) for user in comp_data) / len(comp_data), 2) if comp_data else 0
                }
            
        except requests.exceptions.RequestException as e:
            analytics_data['error'] = f'Error fetching data from backend: {str(e)}'
        
        return jsonify(analytics_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/start-backend', methods=['POST'])
def start_backend():
    """Start backend server"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Start backend
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(
                ['py', 'app.py'],
                cwd=script_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Mac/Linux
            process = subprocess.Popen(
                ['python3', 'app.py'],
                cwd=script_dir
            )
        
        PROCESSES['backend'] = process.pid
        time.sleep(3)  # Wait for backend to start
        
        # Seed database
        try:
            requests.post('http://localhost:5000/api/seed', timeout=5)
        except:
            pass
        
        return jsonify({'status': 'success', 'pid': process.pid})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/stop-backend', methods=['POST'])
def stop_backend():
    """Stop backend server"""
    try:
        if PROCESSES['backend']:
            os.kill(PROCESSES['backend'], signal.SIGTERM)
            PROCESSES['backend'] = None
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/start-frontend', methods=['POST'])
def start_frontend():
    """Start frontend server"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.join(script_dir, 'frontend')
        
        if os.name == 'nt':  # Windows
            # Set PORT environment variable and start
            process = subprocess.Popen(
                ['cmd', '/c', 'set PORT=3001 && npm start'],
                cwd=frontend_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                env={**os.environ, 'PORT': '3001'}
            )
        else:  # Mac/Linux
            process = subprocess.Popen(
                ['npm', 'start'],
                cwd=frontend_dir,
                env={**os.environ, 'PORT': '3001'}
            )
        
        PROCESSES['frontend'] = process.pid
        return jsonify({'status': 'success', 'pid': process.pid})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/stop-frontend', methods=['POST'])
def stop_frontend():
    """Stop frontend server"""
    try:
        if PROCESSES['frontend']:
            os.kill(PROCESSES['frontend'], signal.SIGTERM)
            PROCESSES['frontend'] = None
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print('\n' + '='*50)
    print('🎛️  GALION.STUDIO - ADMIN PANEL')
    print('='*50)
    print('\n✅ Admin panel starting on: http://localhost:9000')
    print('\n📋 What you can do:')
    print('   - Start/Stop backend & frontend')
    print('   - View real-time status with progress %')
    print('   - Monitor system resources')
    print('   - Seed database')
    print('   - View activity logs')
    print('\n🌐 Open your browser to: http://localhost:9000')
    print('\n' + '='*50 + '\n')
    
    app.run(debug=False, host='0.0.0.0', port=9000)

