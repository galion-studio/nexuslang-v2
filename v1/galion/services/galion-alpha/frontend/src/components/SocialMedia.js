import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SocialMedia.css';

// Simple Social Media CMS - no fancy integrations, just create & copy posts
function SocialMedia({ workspaceId }) {
  // State for posts list and form
  const [posts, setPosts] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingPost, setEditingPost] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    platforms: [],
    status: 'draft',
    notes: ''
  });

  // Available platforms
  const platforms = [
    { id: 'reddit', name: 'Reddit', icon: '🔴' },
    { id: 'twitter', name: 'X / Twitter', icon: '🐦' },
    { id: 'instagram', name: 'Instagram', icon: '📸' },
    { id: 'tiktok', name: 'TikTok', icon: '🎵' },
    { id: 'facebook', name: 'Facebook', icon: '👍' }
  ];

  // Load posts on mount and when workspace changes
  useEffect(() => {
    if (workspaceId) {
      loadPosts();
    }
  }, [workspaceId]);

  // Load posts from API
  const loadPosts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5000/api/social-posts?workspace_id=${workspaceId}`);
      setPosts(response.data);
    } catch (error) {
      console.error('Error loading posts:', error);
      alert('Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  // Open modal for new post
  const handleNewPost = () => {
    setEditingPost(null);
    setFormData({
      title: '',
      content: '',
      platforms: [],
      status: 'draft',
      notes: ''
    });
    setShowModal(true);
  };

  // Open modal to edit existing post
  const handleEditPost = (post) => {
    setEditingPost(post);
    setFormData({
      title: post.title,
      content: post.content,
      platforms: post.platforms || [],
      status: post.status,
      notes: post.notes || ''
    });
    setShowModal(true);
  };

  // Save post (create or update)
  const handleSavePost = async () => {
    if (!formData.title.trim() || !formData.content.trim()) {
      alert('Title and content are required');
      return;
    }

    try {
      setLoading(true);
      
      const postData = {
        ...formData,
        workspace_id: workspaceId
      };

      if (editingPost) {
        // Update existing post
        await axios.patch(`http://localhost:5000/api/social-posts/${editingPost.id}`, postData);
      } else {
        // Create new post
        await axios.post('http://localhost:5000/api/social-posts', postData);
      }

      setShowModal(false);
      loadPosts();
    } catch (error) {
      console.error('Error saving post:', error);
      alert('Failed to save post');
    } finally {
      setLoading(false);
    }
  };

  // Delete post
  const handleDeletePost = async (postId) => {
    if (!window.confirm('Delete this post?')) return;

    try {
      setLoading(true);
      await axios.delete(`http://localhost:5000/api/social-posts/${postId}`);
      loadPosts();
    } catch (error) {
      console.error('Error deleting post:', error);
      alert('Failed to delete post');
    } finally {
      setLoading(false);
    }
  };

  // Copy content to clipboard
  const handleCopyContent = (post) => {
    navigator.clipboard.writeText(post.content);
    setCopiedId(post.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Mark post as posted
  const handleMarkPosted = async (post) => {
    try {
      setLoading(true);
      await axios.patch(`http://localhost:5000/api/social-posts/${post.id}`, {
        status: 'posted'
      });
      loadPosts();
    } catch (error) {
      console.error('Error updating post:', error);
      alert('Failed to update post');
    } finally {
      setLoading(false);
    }
  };

  // Toggle platform selection
  const togglePlatform = (platformId) => {
    setFormData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter(p => p !== platformId)
        : [...prev.platforms, platformId]
    }));
  };

  // If no workspace selected
  if (!workspaceId) {
    return (
      <div className="social-media">
        <p className="empty-state">Select a workspace to manage social media posts</p>
      </div>
    );
  }

  return (
    <div className="social-media">
      {/* Header */}
      <div className="social-header">
        <div>
          <h2>Social Media CMS</h2>
          <p>Create posts for Reddit, Twitter, Instagram, TikTok, Facebook</p>
        </div>
        <button className="btn-primary" onClick={handleNewPost}>
          ➕ New Post
        </button>
      </div>

      {/* Posts List */}
      {loading && posts.length === 0 ? (
        <p className="loading">Loading posts...</p>
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <p>No posts yet. Create your first social media post!</p>
          <button className="btn-primary" onClick={handleNewPost}>Create Post</button>
        </div>
      ) : (
        <div className="posts-grid">
          {posts.map(post => (
            <div key={post.id} className="post-card">
              {/* Status Badge */}
              <div className={`status-badge status-${post.status}`}>
                {post.status === 'draft' && '📝 Draft'}
                {post.status === 'posted' && '✅ Posted'}
                {post.status === 'scheduled' && '⏰ Scheduled'}
              </div>

              {/* Post Title */}
              <h3>{post.title}</h3>

              {/* Post Content Preview */}
              <p className="content-preview">
                {post.content.substring(0, 200)}
                {post.content.length > 200 && '...'}
              </p>

              {/* Platforms */}
              <div className="platforms-row">
                {post.platforms.map(platformId => {
                  const platform = platforms.find(p => p.id === platformId);
                  return platform ? (
                    <span key={platformId} className="platform-tag">
                      {platform.icon} {platform.name}
                    </span>
                  ) : null;
                })}
              </div>

              {/* Post Metadata */}
              <div className="post-meta">
                <span>By {post.creator_name || 'Unknown'}</span>
                <span>{new Date(post.created_at).toLocaleDateString()}</span>
              </div>

              {/* Actions */}
              <div className="post-actions">
                <button 
                  className="btn-copy"
                  onClick={() => handleCopyContent(post)}
                  title="Copy content to clipboard"
                >
                  {copiedId === post.id ? '✓ Copied!' : '📋 Copy'}
                </button>
                {post.status === 'draft' && (
                  <button 
                    className="btn-mark-posted"
                    onClick={() => handleMarkPosted(post)}
                    title="Mark as posted"
                  >
                    ✅ Posted
                  </button>
                )}
                <button 
                  className="btn-edit"
                  onClick={() => handleEditPost(post)}
                >
                  ✏️ Edit
                </button>
                <button 
                  className="btn-delete"
                  onClick={() => handleDeletePost(post.id)}
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h2>{editingPost ? 'Edit Post' : 'New Post'}</h2>

            {/* Title */}
            <div className="form-group">
              <label>Title (internal reference)</label>
              <input
                type="text"
                value={formData.title}
                onChange={e => setFormData({...formData, title: e.target.value})}
                placeholder="e.g., Reddit post about First Principles"
              />
            </div>

            {/* Content */}
            <div className="form-group">
              <label>Post Content</label>
              <textarea
                value={formData.content}
                onChange={e => setFormData({...formData, content: e.target.value})}
                placeholder="Write your post content here..."
                rows={10}
              />
              <small>{formData.content.length} characters</small>
            </div>

            {/* Platforms */}
            <div className="form-group">
              <label>Platforms</label>
              <div className="platforms-select">
                {platforms.map(platform => (
                  <button
                    key={platform.id}
                    className={`platform-btn ${formData.platforms.includes(platform.id) ? 'selected' : ''}`}
                    onClick={() => togglePlatform(platform.id)}
                    type="button"
                  >
                    {platform.icon} {platform.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Status */}
            <div className="form-group">
              <label>Status</label>
              <select
                value={formData.status}
                onChange={e => setFormData({...formData, status: e.target.value})}
              >
                <option value="draft">Draft</option>
                <option value="posted">Posted</option>
                <option value="scheduled">Scheduled</option>
              </select>
            </div>

            {/* Notes */}
            <div className="form-group">
              <label>Notes (internal)</label>
              <textarea
                value={formData.notes}
                onChange={e => setFormData({...formData, notes: e.target.value})}
                placeholder="Internal notes about this post..."
                rows={3}
              />
            </div>

            {/* Modal Actions */}
            <div className="modal-actions">
              <button 
                className="btn-secondary"
                onClick={() => setShowModal(false)}
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                className="btn-primary"
                onClick={handleSavePost}
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save Post'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SocialMedia;

