/**
 * Category Manager Component
 * Manage content categories (create, edit, delete)
 */

import React, { useState, useEffect } from 'react';
import { categoryAPI } from '../api';

function CategoryManager() {
  // State
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Form state
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
  });

  // Load categories on mount
  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const response = await categoryAPI.getAll();
      setCategories(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load categories');
      setLoading(false);
    }
  };

  // Auto-generate slug from name
  const generateSlug = (name) => {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Auto-generate slug when name changes
    if (name === 'name' && !editingId) {
      setFormData((prev) => ({
        ...prev,
        slug: generateSlug(value),
      }));
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingId) {
        // Update existing category
        await categoryAPI.update(editingId, formData);
        setSuccess('Category updated successfully!');
      } else {
        // Create new category
        await categoryAPI.create(formData);
        setSuccess('Category created successfully!');
      }

      // Reset form and reload categories
      setShowForm(false);
      setEditingId(null);
      setFormData({ name: '', slug: '', description: '' });
      loadCategories();
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to save category';
      setError(message);
    }
  };

  // Start editing a category
  const handleEdit = (category) => {
    setEditingId(category.id);
    setFormData({
      name: category.name,
      slug: category.slug,
      description: category.description || '',
    });
    setShowForm(true);
    setError('');
    setSuccess('');
  };

  // Delete a category
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure? This may affect existing content.')) {
      return;
    }

    try {
      await categoryAPI.delete(id);
      setSuccess('Category deleted successfully!');
      loadCategories();
    } catch (err) {
      setError('Failed to delete category');
    }
  };

  // Cancel editing
  const handleCancel = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({ name: '', slug: '', description: '' });
    setError('');
  };

  if (loading) {
    return <div className="loading">Loading categories...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2>Category Manager</h2>
        {!showForm && (
          <button onClick={() => setShowForm(true)}>
            + Add Category
          </button>
        )}
      </div>

      {error && <div className="alert error">{error}</div>}
      {success && <div className="alert success">{success}</div>}

      {/* Category Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="card">
          <h3>{editingId ? 'Edit Category' : 'Create Category'}</h3>

          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Category name"
            />
          </div>

          <div className="form-group">
            <label>Slug (URL) *</label>
            <input
              type="text"
              name="slug"
              value={formData.slug}
              onChange={handleChange}
              required
              placeholder="category-slug"
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Optional description"
              rows={3}
            />
          </div>

          <div className="actions">
            <button type="submit">
              {editingId ? 'Update Category' : 'Create Category'}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={handleCancel}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Categories List */}
      <div className="card">
        <h3>Existing Categories ({categories.length})</h3>
        
        {categories.length === 0 ? (
          <p>No categories yet. Create one to get started!</p>
        ) : (
          <ul className="content-list">
            {categories.map((category) => (
              <li key={category.id} className="content-item">
                <div>
                  <h3>{category.name}</h3>
                  <div className="content-meta">
                    <span>Slug: {category.slug}</span>
                  </div>
                  {category.description && (
                    <p className="content-excerpt">{category.description}</p>
                  )}
                </div>

                <div className="actions">
                  <button onClick={() => handleEdit(category)}>
                    Edit
                  </button>
                  <button
                    className="danger"
                    onClick={() => handleDelete(category.id)}
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default CategoryManager;

