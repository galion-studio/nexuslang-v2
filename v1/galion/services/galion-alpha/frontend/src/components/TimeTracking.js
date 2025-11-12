import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TimeTracking.css';

function TimeTracking({ workspaceId }) {
  const [timeLogs, setTimeLogs] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);

  useEffect(() => {
    fetchData();
  }, [workspaceId]);

  const fetchData = async () => {
    if (!workspaceId) {
      setLoading(false);
      return;
    }

    try {
      const [logsRes, tasksRes, usersRes] = await Promise.all([
        axios.get(`/api/time-logs?workspace_id=${workspaceId}`),
        axios.get(`/api/tasks?workspace_id=${workspaceId}`),
        axios.get('/api/users')
      ]);

      setTimeLogs(logsRes.data);
      setTasks(tasksRes.data);
      setUsers(usersRes.data);
      
      // Auto-select first user
      if (usersRes.data.length > 0 && !currentUserId) {
        setCurrentUserId(usersRes.data[0].id);
      }

      setLoading(false);
    } catch (err) {
      setError('Failed to load time logs');
      setLoading(false);
    }
  };

  const handleDeleteLog = async (logId) => {
    if (!window.confirm('Are you sure you want to delete this time log?')) return;

    try {
      await axios.delete(`/api/time-logs/${logId}`);
      fetchData();
    } catch (err) {
      setError('Failed to delete time log');
    }
  };

  const totalHours = timeLogs.reduce((sum, log) => sum + log.hours, 0);
  const totalAmount = timeLogs.reduce((sum, log) => sum + log.amount, 0);

  if (!workspaceId) {
    return (
      <div className="empty-state">
        <h2>Select a workspace</h2>
        <p>Go to Tasks to select a workspace first</p>
      </div>
    );
  }

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="time-tracking-container">
      {error && (
        <div className="error">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="page-header">
        <div>
          <h2>Time Tracking</h2>
          <select 
            value={currentUserId || ''} 
            onChange={(e) => setCurrentUserId(e.target.value)}
            className="user-select"
          >
            <option value="">All Users</option>
            {users.map(user => (
              <option key={user.id} value={user.id}>{user.name}</option>
            ))}
          </select>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + Log Time
        </button>
      </div>

      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-label">Total Hours</div>
          <div className="card-value">{totalHours.toFixed(1)}h</div>
        </div>
        <div className="summary-card">
          <div className="card-label">Total Earned</div>
          <div className="card-value success">${totalAmount.toLocaleString()}</div>
        </div>
        <div className="summary-card">
          <div className="card-label">Entries</div>
          <div className="card-value">{timeLogs.length}</div>
        </div>
      </div>

      <div className="time-logs-table-container">
        <table className="time-logs-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>User</th>
              <th>Task</th>
              <th>Hours</th>
              <th>Amount</th>
              <th>Description</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {timeLogs
              .filter(log => !currentUserId || log.user_id === currentUserId)
              .map(log => (
                <tr key={log.id}>
                  <td>{new Date(log.work_date).toLocaleDateString()}</td>
                  <td>{log.user_name}</td>
                  <td className="task-title-cell">{log.task_title || 'Unknown'}</td>
                  <td>{log.hours}h</td>
                  <td className="amount-cell">${log.amount.toLocaleString()}</td>
                  <td className="description-cell">{log.description}</td>
                  <td>
                    <button 
                      onClick={() => handleDeleteLog(log.id)}
                      className="btn-delete"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            {timeLogs.length === 0 && (
              <tr>
                <td colSpan="7" className="empty-row">
                  No time logs yet. Log your first entry!
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <TimeLogModal
          tasks={tasks}
          users={users}
          currentUserId={currentUserId}
          onSave={(data) => {
            axios.post('/api/time-logs', data, {
              headers: { 'X-User-ID': data.user_id }
            }).then(() => {
              fetchData();
              setShowModal(false);
            }).catch(() => {
              setError('Failed to log time');
            });
          }}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}

function TimeLogModal({ tasks, users, currentUserId, onSave, onClose }) {
  const [formData, setFormData] = useState({
    task_id: '',
    user_id: currentUserId || '',
    hours: '',
    work_date: new Date().toISOString().split('T')[0],
    description: ''
  });

  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};

    if (!formData.task_id) {
      newErrors.task_id = 'Task is required';
    }
    if (!formData.user_id) {
      newErrors.user_id = 'User is required';
    }
    if (!formData.hours || formData.hours <= 0) {
      newErrors.hours = 'Hours must be positive';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validate()) return;

    onSave({
      ...formData,
      hours: parseFloat(formData.hours)
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Log Time</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label>Task *</label>
            <select
              value={formData.task_id}
              onChange={e => setFormData({...formData, task_id: e.target.value})}
              className={errors.task_id ? 'error' : ''}
            >
              <option value="">Select task</option>
              {tasks.map(task => (
                <option key={task.id} value={task.id}>
                  {task.title}
                </option>
              ))}
            </select>
            {errors.task_id && <span className="error-text">{errors.task_id}</span>}
          </div>

          <div className="form-group">
            <label>User *</label>
            <select
              value={formData.user_id}
              onChange={e => setFormData({...formData, user_id: e.target.value})}
              className={errors.user_id ? 'error' : ''}
            >
              <option value="">Select user</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
            {errors.user_id && <span className="error-text">{errors.user_id}</span>}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Date *</label>
              <input
                type="date"
                value={formData.work_date}
                onChange={e => setFormData({...formData, work_date: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Hours *</label>
              <input
                type="number"
                step="0.5"
                value={formData.hours}
                onChange={e => setFormData({...formData, hours: e.target.value})}
                placeholder="8.0"
                className={errors.hours ? 'error' : ''}
              />
              {errors.hours && <span className="error-text">{errors.hours}</span>}
            </div>
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              placeholder="What did you work on?"
              rows={4}
            />
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Log Time
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TimeTracking;

