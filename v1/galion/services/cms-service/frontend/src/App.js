/**
 * Main App Component
 * Sets up routing and navigation for the CMS
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import ContentList from './components/ContentList';
import ContentEditor from './components/ContentEditor';
import CategoryManager from './components/CategoryManager';

// Navigation bar component
function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <h1>Simple CMS</h1>
        <div className="navbar-links">
          <Link to="/">Content</Link>
          {isAuthenticated() && (
            <>
              <Link to="/create">Create</Link>
              <Link to="/categories">Categories</Link>
              <span>👤 {user?.username}</span>
              <button onClick={logout}>Logout</button>
            </>
          )}
          {!isAuthenticated() && (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

// Protected route component
// Only allows access if user is authenticated
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return isAuthenticated() ? children : <Navigate to="/login" />;
}

// Main app component with routing
function AppContent() {
  return (
    <Router>
      <Navbar />
      <div className="container">
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<ContentList />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes - require authentication */}
          <Route
            path="/create"
            element={
              <ProtectedRoute>
                <ContentEditor />
              </ProtectedRoute>
            }
          />
          <Route
            path="/edit/:id"
            element={
              <ProtectedRoute>
                <ContentEditor />
              </ProtectedRoute>
            }
          />
          <Route
            path="/categories"
            element={
              <ProtectedRoute>
                <CategoryManager />
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

// Root app component with providers
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;

