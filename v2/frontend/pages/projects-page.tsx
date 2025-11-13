/**
 * Complete Projects Page for developer.galion.app
 * Full project management with beautiful UI
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

interface Project {
  id: number;
  name: string;
  description: string;
  language: string;
  status: string;
  updated_at: string;
}

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '', language: 'nexuslang' });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v2/projects/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await res.json();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v2/projects/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newProject)
      });
      if (res.ok) {
        setShowModal(false);
        setNewProject({ name: '', description: '', language: 'nexuslang' });
        fetchProjects();
      }
    } catch (error) {
      alert('Failed to create project');
    }
  };

  return (
    <>
      <Head>
        <title>Projects - developer.galion.app</title>
      </Head>
      
      <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: '50px' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
            <div>
              <h1 style={{ fontSize: '42px', fontWeight: '800', color: '#333', marginBottom: '10px' }}>
                📂 Projects
              </h1>
              <p style={{ fontSize: '18px', color: '#666' }}>
                Manage and organize your work
              </p>
            </div>
            <button
              onClick={() => setShowModal(true)}
              style={{
                padding: '15px 30px',
                background: 'linear-gradient(135deg, #667eea, #764ba2)',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
              }}
            >
              + New Project
            </button>
          </div>

          {/* Projects Grid */}
          {loading ? (
            <div style={{ textAlign: 'center', padding: '100px', color: '#666' }}>
              Loading projects...
            </div>
          ) : projects.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '100px', background: 'white', borderRadius: '20px' }}>
              <div style={{ fontSize: '64px', marginBottom: '20px' }}>📂</div>
              <h2 style={{ fontSize: '24px', color: '#333', marginBottom: '15px' }}>No projects yet</h2>
              <p style={{ color: '#666', marginBottom: '30px' }}>Create your first project to get started!</p>
              <button
                onClick={() => setShowModal(true)}
                style={{
                  padding: '12px 30px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  cursor: 'pointer'
                }}
              >
                Create Project
              </button>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '25px' }}>
              {projects.map(project => (
                <div
                  key={project.id}
                  onClick={() => router.push(`/ide?project=${project.id}`)}
                  style={{
                    background: 'white',
                    padding: '30px',
                    borderRadius: '15px',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.08)',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    border: '1px solid #e0e0e0'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-5px)';
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 10px rgba(0,0,0,0.08)';
                  }}
                >
                  <h3 style={{ fontSize: '22px', fontWeight: '700', color: '#333', marginBottom: '12px' }}>
                    {project.name}
                  </h3>
                  <p style={{ fontSize: '14px', color: '#666', marginBottom: '20px', minHeight: '40px' }}>
                    {project.description || 'No description'}
                  </p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px', color: '#999' }}>
                    <span style={{
                      padding: '5px 12px',
                      background: '#f0f0f0',
                      borderRadius: '5px',
                      color: '#667eea',
                      fontWeight: '600'
                    }}>
                      {project.language}
                    </span>
                    <span>{new Date(project.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Create Modal */}
        {showModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              background: 'white',
              padding: '40px',
              borderRadius: '20px',
              maxWidth: '500px',
              width: '100%',
              boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
            }}>
              <h2 style={{ fontSize: '28px', marginBottom: '25px' }}>Create New Project</h2>
              <input
                type="text"
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                placeholder="Project name"
                style={{
                  width: '100%',
                  padding: '12px',
                  marginBottom: '15px',
                  fontSize: '16px',
                  border: '2px solid #ddd',
                  borderRadius: '8px'
                }}
              />
              <textarea
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                placeholder="Description"
                style={{
                  width: '100%',
                  height: '100px',
                  padding: '12px',
                  marginBottom: '15px',
                  fontSize: '16px',
                  border: '2px solid #ddd',
                  borderRadius: '8px'
                }}
              />
              <select
                value={newProject.language}
                onChange={(e) => setNewProject({ ...newProject, language: e.target.value })}
                style={{
                  width: '100%',
                  padding: '12px',
                  marginBottom: '25px',
                  fontSize: '16px',
                  border: '2px solid #ddd',
                  borderRadius: '8px'
                }}
              >
                <option value="nexuslang">NexusLang</option>
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
              </select>
              <div style={{ display: 'flex', gap: '15px' }}>
                <button
                  onClick={createProject}
                  style={{
                    flex: 1,
                    padding: '12px',
                    background: '#667eea',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Create
                </button>
                <button
                  onClick={() => setShowModal(false)}
                  style={{
                    flex: 1,
                    padding: '12px',
                    background: '#e0e0e0',
                    color: '#333',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '16px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

