'use client'

import { useState } from 'react'
import { ExternalLink, Github, Eye } from 'lucide-react'

interface PortfolioItem {
  id: string
  title: string
  description: string
  image: string
  category: string
  technologies: string[]
  liveUrl?: string
  githubUrl?: string
  featured: boolean
}

const portfolioItems: PortfolioItem[] = [
  {
    id: 'galion-app',
    title: 'Galion.app',
    description: 'Voice-first AI platform for natural human-AI interaction. Built with Next.js, TypeScript, and advanced voice processing.',
    image: '/api/placeholder/600/400',
    category: 'Web Application',
    technologies: ['Next.js', 'TypeScript', 'WebRTC', 'OpenAI API'],
    liveUrl: 'https://galion.app',
    featured: true
  },
  {
    id: 'developer-platform',
    title: 'developer.Galion.app',
    description: 'Full-featured IDE for NexusLang development with Monaco Editor, voice commands, and real-time compilation.',
    image: '/api/placeholder/600/400',
    category: 'Developer Tool',
    technologies: ['React', 'Monaco Editor', 'WebSocket', 'Node.js'],
    liveUrl: 'https://developer.galion.app',
    githubUrl: 'https://github.com/galion/developer-platform',
    featured: true
  },
  {
    id: 'nexuslang-compiler',
    title: 'NexusLang Compiler',
    description: 'High-performance compiler for the NexusLang programming language with advanced optimization techniques.',
    image: '/api/placeholder/600/400',
    category: 'Compiler',
    technologies: ['Rust', 'LLVM', 'WebAssembly', 'TypeScript'],
    githubUrl: 'https://github.com/galion/nexuslang-compiler',
    featured: true
  },
  {
    id: 'voice-processor',
    title: 'Voice Processing Engine',
    description: 'Real-time voice processing pipeline with STT, TTS, and VAD capabilities for seamless AI interaction.',
    image: '/api/placeholder/600/400',
    category: 'AI/ML',
    technologies: ['Python', 'TensorFlow', 'WebRTC', 'FastAPI'],
    githubUrl: 'https://github.com/galion/voice-processor',
    featured: false
  },
  {
    id: 'galion-studio',
    title: 'Galion.studio',
    description: 'Corporate website showcasing our mission, team, and portfolio with modern design and smooth animations.',
    image: '/api/placeholder/600/400',
    category: 'Website',
    technologies: ['Next.js', 'Tailwind CSS', 'Framer Motion', 'Vercel'],
    liveUrl: 'https://galion.studio',
    githubUrl: 'https://github.com/galion/galion-studio',
    featured: false
  }
]

interface PortfolioGalleryProps {
  className?: string
}

export function PortfolioGallery({ className = '' }: PortfolioGalleryProps) {
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedItem, setSelectedItem] = useState<PortfolioItem | null>(null)

  const categories = ['All', ...Array.from(new Set(portfolioItems.map(item => item.category)))]

  const filteredItems = selectedCategory === 'All'
    ? portfolioItems
    : portfolioItems.filter(item => item.category === selectedCategory)

  const featuredItems = portfolioItems.filter(item => item.featured)
  const regularItems = portfolioItems.filter(item => !item.featured)

  return (
    <div className={className}>
      {/* Featured Projects */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold text-foreground mb-8">Featured Projects</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {featuredItems.map((item) => (
            <div
              key={item.id}
              className="group bg-surface rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
            >
              <div className="aspect-video bg-gradient-to-br from-primary/20 to-accent/20 relative overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                      <Eye className="w-8 h-8 text-primary" />
                    </div>
                    <p className="text-sm text-foreground-muted">Preview Image</p>
                  </div>
                </div>
                {item.featured && (
                  <div className="absolute top-4 left-4 bg-primary text-primary-foreground px-2 py-1 rounded-full text-xs font-medium">
                    Featured
                  </div>
                )}
              </div>

              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-xl font-semibold text-foreground mb-1">{item.title}</h3>
                    <p className="text-sm text-primary font-medium">{item.category}</p>
                  </div>
                  <div className="flex space-x-2">
                    {item.liveUrl && (
                      <a
                        href={item.liveUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-foreground-muted hover:text-primary transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                    {item.githubUrl && (
                      <a
                        href={item.githubUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-foreground-muted hover:text-primary transition-colors"
                      >
                        <Github className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                </div>

                <p className="text-foreground-muted mb-4 line-clamp-3">{item.description}</p>

                <div className="flex flex-wrap gap-2">
                  {item.technologies.slice(0, 3).map((tech) => (
                    <span
                      key={tech}
                      className="px-2 py-1 bg-surface-hover text-foreground-muted text-xs rounded-md"
                    >
                      {tech}
                    </span>
                  ))}
                  {item.technologies.length > 3 && (
                    <span className="px-2 py-1 bg-surface-hover text-foreground-muted text-xs rounded-md">
                      +{item.technologies.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Category Filter */}
      <section>
        <div className="flex flex-wrap gap-2 mb-8">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-surface-hover text-foreground hover:bg-surface-active'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* All Projects Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="group bg-surface rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
            >
              <div className="aspect-video bg-gradient-to-br from-primary/10 to-accent/10 relative overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-2">
                      <Eye className="w-6 h-6 text-primary" />
                    </div>
                    <p className="text-xs text-foreground-muted">Preview</p>
                  </div>
                </div>
              </div>

              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-foreground">{item.title}</h3>
                  <div className="flex space-x-1">
                    {item.liveUrl && (
                      <a
                        href={item.liveUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 text-foreground-muted hover:text-primary transition-colors"
                      >
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                    {item.githubUrl && (
                      <a
                        href={item.githubUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 text-foreground-muted hover:text-primary transition-colors"
                      >
                        <Github className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>

                <p className="text-sm text-foreground-muted mb-3 line-clamp-2">{item.description}</p>

                <div className="flex flex-wrap gap-1">
                  {item.technologies.slice(0, 2).map((tech) => (
                    <span
                      key={tech}
                      className="px-2 py-1 bg-surface-hover text-foreground-muted text-xs rounded"
                    >
                      {tech}
                    </span>
                  ))}
                  {item.technologies.length > 2 && (
                    <span className="px-2 py-1 bg-surface-hover text-foreground-muted text-xs rounded">
                      +{item.technologies.length - 2}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredItems.length === 0 && (
          <div className="text-center py-12">
            <p className="text-foreground-muted">No projects found in this category.</p>
          </div>
        )}
      </section>

      {/* Project Modal (placeholder for future implementation) */}
      {selectedItem && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-surface rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-foreground">{selectedItem.title}</h3>
                <button
                  onClick={() => setSelectedItem(null)}
                  className="text-foreground-muted hover:text-foreground"
                >
                  ×
                </button>
              </div>
              <p className="text-foreground-muted">{selectedItem.description}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PortfolioGallery
