/**
 * Content Editor Component
 * Create and edit content (blog posts, pages, articles)
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { contentAPI, categoryAPI } from '../api';

function ContentEditor() {
  const navigate = useNavigate();
  const { id } = useParams(); // Get ID from URL if editing
  const isEditing = !!id;
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    content: '',
    excerpt: '',
    content_type: 'post',
    status: 'draft',
    category_id: '',
    meta_title: '',
    meta_description: '',
    featured_image: '',
  });
  
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Load categories and content (if editing)
  useEffect(() => {
    loadCategories();
    if (isEditing) {
      loadContent();
    }
  }, [id]);

  const loadCategories = async () => {
    try {
      const response = await categoryAPI.getAll();
      setCategories(response.data);
    } catch (err) {
      console.error('Failed to load categories', err);
    }
  };

  const loadContent = async () => {
    try {
      setLoading(true);
      const response = await contentAPI.getById(id);
      const content = response.data;
      
      // Fill form with existing content
      setFormData({
        title: content.title,
        slug: content.slug,
        content: content.content,
        excerpt: content.excerpt || '',
        content_type: content.content_type,
        status: content.status,
        category_id: content.category_id || '',
        meta_title: content.meta_title || '',
        meta_description: content.meta_description || '',
        featured_image: content.featured_image || '',
      });
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load content');
      setLoading(false);
    }
  };

  // Auto-generate slug from title
  const generateSlug = (title) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-') // Replace non-alphanumeric with dashes
      .replace(/^-+|-+$/g, '');     // Remove leading/trailing dashes
  };

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Auto-generate slug when title changes
    if (name === 'title' && !isEditing) {
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
    setLoading(true);

    try {
      // Convert empty strings to null for optional fields
      const data = {
        ...formData,
        category_id: formData.category_id || null,
        excerpt: formData.excerpt || null,
        meta_title: formData.meta_title || null,
        meta_description: formData.meta_description || null,
        featured_image: formData.featured_image || null,
      };

      if (isEditing) {
        // Update existing content
        await contentAPI.update(id, data);
        setSuccess('Content updated successfully!');
      } else {
        // Create new content
        await contentAPI.create(data);
        setSuccess('Content created successfully!');
      }

      // Redirect to content list after a short delay
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to save content';
      setError(message);
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>{isEditing ? 'Edit Content' : 'Create New Content'}</h2>

      {error && <div className="alert error">{error}</div>}
      {success && <div className="alert success">{success}</div>}

      <form onSubmit={handleSubmit} className="card">
        {/* Title */}
        <div className="form-group">
          <label>Title *</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            disabled={loading}
            placeholder="Enter content title"
          />
        </div>

        {/* Slug */}
        <div className="form-group">
          <label>Slug (URL) *</label>
          <input
            type="text"
            name="slug"
            value={formData.slug}
            onChange={handleChange}
            required
            disabled={loading}
            placeholder="url-friendly-slug"
          />
          <small style={{ color: '#7f8c8d' }}>
            URL: /content/{formData.slug || 'your-slug'}
          </small>
        </div>

        {/* Content */}
        <div className="form-group">
          <label>Content *</label>
          <textarea
            name="content"
            value={formData.content}
            onChange={handleChange}
            required
            disabled={loading}
            placeholder="Write your content here..."
            rows={15}
          />
        </div>

        {/* Excerpt */}
        <div className="form-group">
          <label>Excerpt (Preview)</label>
          <textarea
            name="excerpt"
            value={formData.excerpt}
            onChange={handleChange}
            disabled={loading}
            placeholder="Short description or preview"
            rows={3}
          />
        </div>

        {/* Content Type and Status */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
          <div className="form-group">
            <label>Content Type</label>
            <select
              name="content_type"
              value={formData.content_type}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="post">Blog Post</option>
              <option value="page">Page</option>
              <option value="article">Article</option>
            </select>
          </div>

          <div className="form-group">
            <label>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="archived">Archived</option>
            </select>
          </div>

          <div className="form-group">
            <label>Category</label>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="">No Category</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* SEO Fields */}
        <h3 style={{ marginTop: '1rem' }}>SEO (Optional)</h3>
        
        <div className="form-group">
          <label>Meta Title</label>
          <input
            type="text"
            name="meta_title"
            value={formData.meta_title}
            onChange={handleChange}
            disabled={loading}
            placeholder="SEO title for search engines"
          />
        </div>

        <div className="form-group">
          <label>Meta Description</label>
          <textarea
            name="meta_description"
            value={formData.meta_description}
            onChange={handleChange}
            disabled={loading}
            placeholder="SEO description for search engines"
            rows={2}
          />
        </div>

        <div className="form-group">
          <label>Featured Image URL</label>
          <input
            type="url"
            name="featured_image"
            value={formData.featured_image}
            onChange={handleChange}
            disabled={loading}
            placeholder="https://example.com/image.jpg"
          />
        </div>

        {/* Actions */}
        <div className="actions">
          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : isEditing ? 'Update Content' : 'Create Content'}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={() => navigate('/')}
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default ContentEditor;

