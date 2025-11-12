import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import axios from 'axios';
import './KanbanBoard.css';
import TaskModal from './TaskModal';

const COLUMNS = [
  { id: 'backlog', title: 'Backlog' },
  { id: 'in_progress', title: 'In Progress' },
  { id: 'done', title: 'Done' }
];

function KanbanBoard({ workspaceId, setWorkspaceId }) {
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (workspaceId) {
      fetchTasks();
    }
  }, [workspaceId]);

  const fetchData = async () => {
    try {
      const [usersRes, workspacesRes] = await Promise.all([
        axios.get('/api/users'),
        axios.get('/api/workspaces')
      ]);
      setUsers(usersRes.data);
      setWorkspaces(workspacesRes.data);
      
      // Auto-select first workspace
      if (workspacesRes.data.length > 0 && !workspaceId) {
        setWorkspaceId(workspacesRes.data[0].id);
      }
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load data. Is the backend running?');
      setLoading(false);
    }
  };

  const fetchTasks = async () => {
    try {
      const res = await axios.get(`/api/tasks?workspace_id=${workspaceId}`);
      setTasks(res.data);
    } catch (err) {
      setError('Failed to load tasks');
    }
  };

  const handleDragEnd = async (result) => {
    if (!result.destination) return;

    const taskId = result.draggableId;
    const newStatus = result.destination.droppableId;

    // Optimistic update
    setTasks(tasks.map(task =>
      task.id === taskId ? { ...task, status: newStatus } : task
    ));

    try {
      await axios.patch(`/api/tasks/${taskId}`, { status: newStatus });
    } catch (err) {
      setError('Failed to update task status');
      fetchTasks(); // Revert on error
    }
  };

  const handleCreateTask = async (taskData) => {
    try {
      await axios.post('/api/tasks', {
        ...taskData,
        workspace_id: workspaceId
      });
      fetchTasks();
      setShowModal(false);
    } catch (err) {
      setError('Failed to create task');
    }
  };

  const handleUpdateTask = async (taskData) => {
    try {
      await axios.patch(`/api/tasks/${editingTask.id}`, taskData);
      fetchTasks();
      setShowModal(false);
      setEditingTask(null);
    } catch (err) {
      setError('Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    
    try {
      await axios.delete(`/api/tasks/${taskId}`);
      fetchTasks();
    } catch (err) {
      setError('Failed to delete task');
    }
  };

  const openEditModal = (task) => {
    setEditingTask(task);
    setShowModal(true);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (workspaces.length === 0) {
    return (
      <div className="empty-state">
        <h2>No workspaces found</h2>
        <p>Create a workspace by seeding the database:</p>
        <code>curl -X POST http://localhost:5000/api/seed</code>
      </div>
    );
  }

  return (
    <div className="kanban-container">
      {error && (
        <div className="error">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="kanban-header">
        <div>
          <h2>Tasks</h2>
          <select 
            value={workspaceId || ''} 
            onChange={(e) => setWorkspaceId(e.target.value)}
            className="workspace-select"
          >
            {workspaces.map(ws => (
              <option key={ws.id} value={ws.id}>{ws.name}</option>
            ))}
          </select>
        </div>
        <button 
          className="btn-primary" 
          onClick={() => {
            setEditingTask(null);
            setShowModal(true);
          }}
        >
          + New Task
        </button>
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="kanban-board">
          {COLUMNS.map(column => (
            <Column
              key={column.id}
              column={column}
              tasks={tasks.filter(t => t.status === column.id)}
              onEdit={openEditModal}
              onDelete={handleDeleteTask}
            />
          ))}
        </div>
      </DragDropContext>

      {showModal && (
        <TaskModal
          task={editingTask}
          users={users}
          onSave={editingTask ? handleUpdateTask : handleCreateTask}
          onClose={() => {
            setShowModal(false);
            setEditingTask(null);
          }}
        />
      )}
    </div>
  );
}

function Column({ column, tasks, onEdit, onDelete }) {
  return (
    <div className="column">
      <div className="column-header">
        <h3>{column.title}</h3>
        <span className="task-count">{tasks.length}</span>
      </div>
      
      <Droppable droppableId={column.id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`task-list ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
          >
            {tasks.map((task, index) => (
              <Draggable key={task.id} draggableId={task.id} index={index}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                  >
                    <TaskCard 
                      task={task} 
                      onEdit={onEdit}
                      onDelete={onDelete}
                      isDragging={snapshot.isDragging}
                    />
                  </div>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
            {tasks.length === 0 && (
              <div className="empty-column">No tasks</div>
            )}
          </div>
        )}
      </Droppable>
    </div>
  );
}

function TaskCard({ task, onEdit, onDelete, isDragging }) {
  return (
    <div className={`task-card ${isDragging ? 'dragging' : ''}`}>
      <div className="task-card-header">
        <h4 className="task-title">{task.title}</h4>
        <div className="task-actions">
          <button onClick={() => onEdit(task)} className="btn-icon">✏️</button>
          <button onClick={() => onDelete(task.id)} className="btn-icon">🗑️</button>
        </div>
      </div>

      {task.description && (
        <p className="task-description">{task.description}</p>
      )}

      {task.assignee && (
        <div className="task-assignee">
          <span className="avatar">{task.assignee.name[0]}</span>
          <span>{task.assignee.name}</span>
        </div>
      )}

      <div className="task-meta">
        <span className="task-hours">
          {task.hours_estimate}h @ ${task.hourly_rate}/h
        </span>
        <span className="task-cost">${task.total_cost.toLocaleString()}</span>
      </div>

      {task.priority !== 'medium' && (
        <span className={`priority-badge priority-${task.priority}`}>
          {task.priority}
        </span>
      )}
    </div>
  );
}

export default KanbanBoard;

