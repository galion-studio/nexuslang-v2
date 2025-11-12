import React, { useState, useEffect } from 'react';
import './TaskModal.css';

function TaskModal({ task, users, onSave, onClose }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assignee_id: '',
    hours_estimate: 8,
    hourly_rate: 100,
    priority: 'medium',
    status: 'backlog'
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title || '',
        description: task.description || '',
        assignee_id: task.assignee_id || '',
        hours_estimate: task.hours_estimate || 8,
        hourly_rate: task.hourly_rate || 100,
        priority: task.priority || 'medium',
        status: task.status || 'backlog'
      });
    }
  }, [task]);

  const validate = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (formData.hours_estimate <= 0) {
      newErrors.hours_estimate = 'Hours must be positive';
    }
    if (formData.hourly_rate <= 0) {
      newErrors.hourly_rate = 'Rate must be positive';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    onSave(formData);
  };

  const totalCost = formData.hours_estimate * formData.hourly_rate;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{task ? 'Edit Task' : 'Create Task'}</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {/* Title */}
          <div className="form-group">
            <label>Title *</label>
            <input
              type="text"
              value={formData.title}
              onChange={e => setFormData({...formData, title: e.target.value})}
              placeholder="Build authentication system"
              className={errors.title ? 'error' : ''}
            />
            {errors.title && <span className="error-text">{errors.title}</span>}
          </div>

          {/* Description */}
          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              placeholder="Add details..."
              rows={3}
            />
          </div>

          {/* Assignee */}
          <div className="form-group">
            <label>Assignee</label>
            <select
              value={formData.assignee_id}
              onChange={e => setFormData({...formData, assignee_id: e.target.value})}
            >
              <option value="">Unassigned</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name} (${user.hourly_rate}/h)
                </option>
              ))}
            </select>
          </div>

          {/* Hours & Rate */}
          <div className="form-row">
            <div className="form-group">
              <label>Hours Estimate *</label>
              <input
                type="number"
                step="0.5"
                value={formData.hours_estimate}
                onChange={e => setFormData({...formData, hours_estimate: parseFloat(e.target.value) || 0})}
                className={errors.hours_estimate ? 'error' : ''}
              />
              {errors.hours_estimate && <span className="error-text">{errors.hours_estimate}</span>}
            </div>

            <div className="form-group">
              <label>Hourly Rate *</label>
              <input
                type="number"
                value={formData.hourly_rate}
                onChange={e => setFormData({...formData, hourly_rate: parseFloat(e.target.value) || 0})}
                className={errors.hourly_rate ? 'error' : ''}
              />
              {errors.hourly_rate && <span className="error-text">{errors.hourly_rate}</span>}
            </div>
          </div>

          {/* Priority & Status */}
          <div className="form-row">
            <div className="form-group">
              <label>Priority</label>
              <select
                value={formData.priority}
                onChange={e => setFormData({...formData, priority: e.target.value})}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            {task && (
              <div className="form-group">
                <label>Status</label>
                <select
                  value={formData.status}
                  onChange={e => setFormData({...formData, status: e.target.value})}
                >
                  <option value="backlog">Backlog</option>
                  <option value="in_progress">In Progress</option>
                  <option value="done">Done</option>
                </select>
              </div>
            )}
          </div>

          {/* Total Cost Display */}
          <div className="total-cost-display">
            <span>Estimated Total Cost</span>
            <span className="cost-amount">${totalCost.toLocaleString()}</span>
          </div>

          {/* Actions */}
          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              {task ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TaskModal;

