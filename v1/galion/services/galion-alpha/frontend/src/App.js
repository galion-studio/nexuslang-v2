import React, { useState } from 'react';
import './App.css';
import KanbanBoard from './components/KanbanBoard';
import TimeTracking from './components/TimeTracking';
import Compensation from './components/Compensation';
import SocialMedia from './components/SocialMedia';

function App() {
  const [currentView, setCurrentView] = useState('tasks');
  const [workspaceId, setWorkspaceId] = useState(null);

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <h1 className="logo">GALION.STUDIO</h1>
          <span className="badge">ALPHA</span>
        </div>
        <nav className="nav">
          <button 
            className={`nav-link ${currentView === 'tasks' ? 'active' : ''}`}
            onClick={() => setCurrentView('tasks')}
          >
            Tasks
          </button>
          <button 
            className={`nav-link ${currentView === 'time' ? 'active' : ''}`}
            onClick={() => setCurrentView('time')}
          >
            Time Tracking
          </button>
          <button 
            className={`nav-link ${currentView === 'compensation' ? 'active' : ''}`}
            onClick={() => setCurrentView('compensation')}
          >
            Compensation
          </button>
          <button 
            className={`nav-link ${currentView === 'social' ? 'active' : ''}`}
            onClick={() => setCurrentView('social')}
          >
            📱 Social Media
          </button>
        </nav>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {currentView === 'tasks' && (
          <KanbanBoard workspaceId={workspaceId} setWorkspaceId={setWorkspaceId} />
        )}
        {currentView === 'time' && (
          <TimeTracking workspaceId={workspaceId} />
        )}
        {currentView === 'compensation' && (
          <Compensation workspaceId={workspaceId} />
        )}
        {currentView === 'social' && (
          <SocialMedia workspaceId={workspaceId} />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>Built with ⚡ Elon Musk's First Principles</p>
      </footer>
    </div>
  );
}

export default App;

