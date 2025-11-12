'use client'

import { useState } from 'react'
import { Users, MessageSquare, Star, GitFork, TrendingUp } from 'lucide-react'

export default function CommunityPage() {
  const [activeTab, setActiveTab] = useState('projects')

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-black">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Users className="text-purple-400" size={32} />
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Community
                </h1>
                <p className="text-sm text-zinc-400">Share, learn, and collaborate</p>
              </div>
            </div>
            <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition">
              Share Project
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-zinc-800">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-semibold transition border-b-2 ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-400'
                  : 'border-transparent text-zinc-400 hover:text-zinc-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Public Projects</h2>
              <select className="px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg">
                <option>Most Stars</option>
                <option>Most Recent</option>
                <option>Most Forks</option>
              </select>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {PUBLIC_PROJECTS.map((project) => (
                <div
                  key={project.id}
                  className="p-6 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 transition"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-bold mb-1">{project.name}</h3>
                      <p className="text-sm text-zinc-400">by {project.author}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="flex items-center gap-1 px-3 py-1 bg-zinc-800 hover:bg-zinc-700 rounded transition">
                        <Star size={16} />
                        {project.stars}
                      </button>
                      <button className="flex items-center gap-1 px-3 py-1 bg-zinc-800 hover:bg-zinc-700 rounded transition">
                        <GitFork size={16} />
                        {project.forks}
                      </button>
                    </div>
                  </div>
                  <p className="text-zinc-300 mb-4">{project.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {project.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 text-xs bg-zinc-800 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Discussions Tab */}
        {activeTab === 'discussions' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Discussions</h2>
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition">
                New Discussion
              </button>
            </div>

            <div className="space-y-4">
              {DISCUSSIONS.map((discussion) => (
                <div
                  key={discussion.id}
                  className="p-6 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 transition"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold mb-2">{discussion.title}</h3>
                      <p className="text-zinc-400 mb-3">{discussion.preview}</p>
                      <div className="flex items-center gap-4 text-sm text-zinc-500">
                        <span>{discussion.author}</span>
                        <span>•</span>
                        <span>{discussion.date}</span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <MessageSquare size={14} />
                          {discussion.replies} replies
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="p-2 hover:bg-zinc-800 rounded transition">
                        ▲
                      </button>
                      <span className="text-lg font-bold">{discussion.upvotes}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Teams Tab */}
        {activeTab === 'teams' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Teams</h2>
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition">
                Create Team
              </button>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {TEAMS.map((team) => (
                <div
                  key={team.id}
                  className="p-6 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 transition"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg mb-4 flex items-center justify-center text-2xl font-bold">
                    {team.name[0]}
                  </div>
                  <h3 className="text-lg font-bold mb-2">{team.name}</h3>
                  <p className="text-sm text-zinc-400 mb-4">{team.description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-zinc-500">{team.members} members</span>
                    <button className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 rounded transition">
                      Join
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const TABS = [
  { id: 'projects', label: 'Projects' },
  { id: 'discussions', label: 'Discussions' },
  { id: 'teams', label: 'Teams' }
]

const PUBLIC_PROJECTS = [
  {
    id: 1,
    name: 'AI Game Engine',
    author: 'john_dev',
    description: 'Neural network-based game AI using NexusLang personality system',
    stars: 234,
    forks: 45,
    tags: ['AI', 'Games', 'Neural Networks']
  },
  {
    id: 2,
    name: 'Knowledge Graph Builder',
    author: 'sarah_ai',
    description: 'Automated knowledge graph construction from Grokopedia data',
    stars: 189,
    forks: 32,
    tags: ['Knowledge', 'Graph', 'Automation']
  },
  {
    id: 3,
    name: 'Voice Assistant Template',
    author: 'mike_voice',
    description: 'Ready-to-use voice assistant with personality customization',
    stars: 156,
    forks: 28,
    tags: ['Voice', 'Assistant', 'Template']
  },
  {
    id: 4,
    name: 'ML Model Optimizer',
    author: 'ai_researcher',
    description: 'Automatic hyperparameter tuning using optimize_self()',
    stars: 142,
    forks: 19,
    tags: ['ML', 'Optimization', 'Training']
  }
]

const DISCUSSIONS = [
  {
    id: 1,
    title: 'Best practices for personality tuning?',
    preview: 'What personality traits work best for data analysis tasks? I\'ve been experimenting with...',
    author: 'curious_coder',
    date: '2 hours ago',
    replies: 12,
    upvotes: 24
  },
  {
    id: 2,
    title: 'Binary compilation performance gains',
    preview: 'Sharing my benchmarks - achieved 15x speedup on large models by compiling to .nxb...',
    author: 'performance_guru',
    date: '5 hours ago',
    replies: 8,
    upvotes: 31
  },
  {
    id: 3,
    title: 'Integrating Grokopedia with custom knowledge',
    preview: 'Has anyone tried combining Grokopedia with domain-specific knowledge bases?',
    author: 'knowledge_seeker',
    date: '1 day ago',
    replies: 15,
    upvotes: 18
  }
]

const TEAMS = [
  {
    id: 1,
    name: 'AI Researchers',
    description: 'Advancing NexusLang for research applications',
    members: 234
  },
  {
    id: 2,
    name: 'Game Developers',
    description: 'Building AI-powered games',
    members: 156
  },
  {
    id: 3,
    name: 'Voice Innovators',
    description: 'Exploring voice-first interfaces',
    members: 89
  },
  {
    id: 4,
    name: 'Open Source Contributors',
    description: 'Contributing to NexusLang core',
    members: 312
  },
  {
    id: 5,
    name: 'Educators',
    description: 'Teaching AI with NexusLang',
    members: 67
  },
  {
    id: 6,
    name: 'Startups',
    description: 'Building products with NexusLang',
    members: 45
  }
]

