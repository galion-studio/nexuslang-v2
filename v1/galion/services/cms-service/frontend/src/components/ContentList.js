/**
 * Content List Component
 * Displays all published content items
 * Allows authenticated users to edit and delete content
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contentAPI, categoryAPI } from '../api';
import { useAuth } from '../AuthContext';

function ContentList() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  // State
  const [content, setContent] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [statusFilter, setStatusFilter] = useState('published');

  // Load content and categories
  useEffect(() => {
    loadData();
  }, [selectedCategory, statusFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Build query parameters
      const params = {};
      if (statusFilter) {
        params.status = statusFilter;
      }
      if (selectedCategory) {
        params.category_id = selectedCategory;
      }
      
      // Load content and categories
      const [contentResponse, categoriesResponse] = await Promise.all([
        contentAPI.getAll(params),
        categoryAPI.getAll(),
      ]);
      
      setContent(contentResponse.data);
      setCategories(categoriesResponse.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load content');
      setLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this content?')) {
      return;
    }

    try {
      await contentAPI.delete(id);
      // Reload content list
      loadData();
    } catch (err) {
      alert('Failed to delete content');
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return <div className="loading">Loading content...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2>Content</h2>
        {isAuthenticated() && (
          <button onClick={() => navigate('/create')}>
            + Create New Content
          </button>
        )}
      </div>

      {error && <div className="alert error">{error}</div>}

      {/* Filters */}
      <div className="card">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {isAuthenticated() && (
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label>Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">All</option>
                <option value="published">Published</option>
                <option value="draft">Draft</option>
                <option value="archived">Archived</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Content list */}
      {content.length === 0 ? (
        <div className="card">
          <p>No content found. {isAuthenticated() && 'Create your first post!'}</p>
        </div>
      ) : (
        <ul className="content-list">
          {content.map((item) => (
            <li key={item.id} className="content-item">
              <h3>{item.title}</h3>
              
              <div className="content-meta">
                <span className={`badge ${item.status}`}>{item.status}</span>
                {item.category && (
                  <span className="badge" style={{ backgroundColor: '#3498db' }}>
                    {item.category.name}
                  </span>
                )}
                <span>By {item.author.username}</span>
                <span> • </span>
                <span>{formatDate(item.created_at)}</span>
                <span> • </span>
                <span>👁 {item.views} views</span>
              </div>

              {item.excerpt && (
                <p className="content-excerpt">{item.excerpt}</p>
              )}

              {isAuthenticated() && (
                <div className="actions">
                  <button onClick={() => navigate(`/edit/${item.id}`)}>
                    Edit
                  </button>
                  <button
                    className="danger"
                    onClick={() => handleDelete(item.id)}
                  >
                    Delete
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ContentList;

