'use client'

import { useState, useEffect } from 'react'
import { Search, Book, CheckCircle, TrendingUp, Plus, Link as LinkIcon } from 'lucide-react'
import grokopedia from '@/lib/grokopedia-api'
import type { KnowledgeEntry } from '@/lib/grokopedia-api'
import { useRouter } from 'next/navigation'

export default function GrokopediaPage() {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<KnowledgeEntry[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [popularTags, setPopularTags] = useState<Array<{ name: string, count: number }>>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  // Load popular tags on mount
  useEffect(() => {
    const loadTags = async () => {
      try {
        const data = await grokopedia.getTags(20)
        setPopularTags(data.tags || [])
      } catch (error) {
        console.error('Failed to load tags:', error)
      }
    }
    loadTags()
  }, [])
  
  // Get suggestions as user types
  useEffect(() => {
    if (query.length >= 2) {
      const getSuggestions = async () => {
        try {
          const data = await grokopedia.suggest(query, 5)
          setSuggestions(data.suggestions || [])
        } catch (error) {
          console.error('Failed to get suggestions:', error)
        }
      }
      // Debounce
      const timer = setTimeout(getSuggestions, 300)
      return () => clearTimeout(timer)
    } else {
      setSuggestions([])
    }
  }, [query])

  const handleSearch = async (searchQuery?: string) => {
    const q = searchQuery || query
    if (!q.trim()) return

    setIsSearching(true)

    try {
      const data = await grokopedia.search(q, 20)
      setResults(data.results || [])
      setQuery(q)
      setSuggestions([])
    } catch (error) {
      console.error('Search failed:', error)
      setResults([])
    } finally {
      setIsSearching(false)
    }
  }
  
  const handleEntryClick = (entry: KnowledgeEntry) => {
    // Navigate to entry detail page (create this later)
    router.push(`/grokopedia/${entry.slug}`)
  }
  
  const handleUpvote = async (entryId: string, event: React.MouseEvent) => {
    event.stopPropagation()
    try {
      const result = await grokopedia.upvote(entryId)
      // Update local state
      setResults(prev => prev.map(entry =>
        entry.id === entryId
          ? { ...entry, upvotes_count: result.upvotes_count }
          : entry
      ))
    } catch (error) {
      console.error('Upvote failed:', error)
      alert('Please login to upvote entries')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-black">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Book className="text-blue-400" size={32} />
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Grokopedia
                </h1>
                <p className="text-sm text-zinc-400">Universal AI Knowledge Base</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Search Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Action Bar */}
          <div className="flex justify-end mb-4">
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
            >
              <Plus size={18} />
              Contribute Entry
            </button>
          </div>
          
          {/* Search Bar */}
          <div className="relative mb-12">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-zinc-400" size={20} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search for any concept, theory, or topic..."
              className="w-full pl-12 pr-4 py-4 bg-zinc-900 border border-zinc-800 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={() => handleSearch()}
              disabled={isSearching}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
            
            {/* Suggestions Dropdown */}
            {suggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl z-10">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    onClick={() => handleSearch(suggestion)}
                    className="px-4 py-3 hover:bg-zinc-800 cursor-pointer transition"
                  >
                    <Search size={16} className="inline mr-2 text-zinc-400" />
                    {suggestion}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Featured Topics */}
          {results.length === 0 && !isSearching && (
            <div className="space-y-8">
              <div>
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <TrendingUp size={20} className="text-green-400" />
                  Trending Topics
                </h2>
                <div className="grid md:grid-cols-3 gap-4">
                  {TRENDING_TOPICS.map((topic) => (
                    <div
                      key={topic}
                      onClick={() => {
                        setQuery(topic)
                        handleSearch()
                      }}
                      className="p-4 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 cursor-pointer transition"
                    >
                      <p className="font-medium">{topic}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h2 className="text-xl font-bold mb-4">Popular Categories</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {CATEGORIES.map((category) => (
                    <div
                      key={category.name}
                      className="p-6 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 transition text-center"
                    >
                      <div className="text-3xl mb-2">{category.icon}</div>
                      <h3 className="font-semibold mb-1">{category.name}</h3>
                      <p className="text-sm text-zinc-400">{category.count} entries</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Search Results */}
          {results.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold">
                Found {results.length} results for "{query}"
              </h2>
              {results.map((result) => (
                <div
                  key={result.id}
                  onClick={() => handleEntryClick(result)}
                  className="p-6 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 transition cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-xl font-bold text-blue-400 flex items-center gap-2 hover:text-blue-300">
                      {result.title}
                      {result.verified && (
                        <CheckCircle size={18} className="text-green-400" title="Verified Entry" />
                      )}
                    </h3>
                    {result.similarity && (
                      <span className="text-sm text-zinc-400">
                        {(result.similarity * 100).toFixed(0)}% match
                      </span>
                    )}
                  </div>
                  <p className="text-zinc-300 mb-4">{result.summary || result.content.substring(0, 200) + '...'}</p>
                  <div className="flex items-center gap-4 text-sm text-zinc-400">
                    {result.tags && result.tags.slice(0, 3).map((tag: string) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-zinc-800 rounded hover:bg-zinc-700 transition"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleSearch(tag)
                        }}
                      >
                        #{tag}
                      </span>
                    ))}
                    <span className="flex items-center gap-1">
                      👁 {result.views_count || 0}
                    </span>
                    <button
                      onClick={(e) => handleUpvote(result.id, e)}
                      className="flex items-center gap-1 hover:text-purple-400 transition"
                    >
                      👍 {result.upvotes_count || 0}
                    </button>
                    <span className="ml-auto flex items-center gap-1 text-blue-400">
                      <LinkIcon size={14} />
                      View Details
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* No Results */}
          {results.length === 0 && isSearching === false && query && (
            <div className="text-center py-12">
              <p className="text-xl text-zinc-400 mb-4">
                No results found for "{query}"
              </p>
              <p className="text-zinc-500">
                Try different keywords or browse categories above
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const TRENDING_TOPICS = [
  'Quantum Computing',
  'Machine Learning',
  'Blockchain',
  'Neural Networks',
  'Artificial Intelligence',
  'Cryptography'
]

const CATEGORIES = [
  { name: 'Science', icon: '🔬', count: 1234 },
  { name: 'Technology', icon: '💻', count: 2341 },
  { name: 'Mathematics', icon: '📐', count: 891 },
  { name: 'Physics', icon: '⚛️', count: 756 },
  { name: 'Biology', icon: '🧬', count: 634 },
  { name: 'Chemistry', icon: '⚗️', count: 523 },
  { name: 'Engineering', icon: '⚙️', count: 445 },
  { name: 'Philosophy', icon: '🤔', count: 321 }
]

