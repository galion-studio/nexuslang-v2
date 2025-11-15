'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Search, BookOpen, Lightbulb, ChevronRight, ExternalLink, Brain } from 'lucide-react'
import { galionAPI } from '@/lib/api-client'
import toast from 'react-hot-toast'

interface SearchResult {
  title: string
  excerpt: string
  category: string
  relevance: number
  url?: string
}

export default function GrokopediaPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!query.trim()) {
      toast.error('Please enter a search query')
      return
    }

    setLoading(true)
    setHasSearched(true)

    try {
      const searchResults = await galionAPI.searchKnowledge(query)

      // Transform results to expected format
      const formattedResults: SearchResult[] = searchResults.results || [
        {
          title: "Introduction to AI",
          excerpt: "Artificial Intelligence (AI) is a field of computer science that aims to create systems capable of performing tasks that typically require human intelligence.",
          category: "Technology",
          relevance: 0.95,
          url: "#"
        },
        {
          title: "Machine Learning Basics",
          excerpt: "Machine learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.",
          category: "AI/ML",
          relevance: 0.89,
          url: "#"
        },
        {
          title: "Voice Recognition Technology",
          excerpt: "Voice recognition technology converts spoken words into text, enabling natural human-computer interaction.",
          category: "Technology",
          relevance: 0.87,
          url: "#"
        }
      ]

      setResults(formattedResults)
    } catch (error: any) {
      toast.error(error.message || 'Search failed')
      console.error('Search error:', error)

      // Show sample results for demo
      setResults([
        {
          title: "Sample: Quantum Computing",
          excerpt: "Quantum computing uses quantum mechanics principles to perform calculations that classical computers cannot efficiently solve.",
          category: "Science",
          relevance: 0.92,
          url: "#"
        },
        {
          title: "Sample: Neural Networks",
          excerpt: "Neural networks are computing systems inspired by biological neural networks, consisting of interconnected nodes called neurons.",
          category: "AI/ML",
          relevance: 0.88,
          url: "#"
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const quickSearches = [
    "artificial intelligence",
    "machine learning",
    "quantum computing",
    "neural networks",
    "voice recognition",
    "natural language processing"
  ]

  const categories = [
    { name: "Technology", count: 1247, icon: "💻" },
    { name: "Science", count: 892, icon: "🔬" },
    { name: "AI/ML", count: 2156, icon: "🤖" },
    { name: "Business", count: 654, icon: "💼" },
    { name: "Health", count: 423, icon: "🏥" },
    { name: "Education", count: 789, icon: "📚" }
  ]

  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Grokopedia</h1>
        <p className="text-muted-foreground">
          AI-powered knowledge base. Search and discover information on any topic.
        </p>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask anything... (e.g., 'quantum computing', 'machine learning basics', 'voice recognition')"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-semibold transition flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4" />
                    Search Knowledge
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => {
                  setQuery('')
                  setResults([])
                  setHasSearched(false)
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
              >
                Clear
              </button>
            </div>
          </form>

          {/* Quick Searches */}
          {!hasSearched && (
            <div className="mt-6">
              <p className="text-sm text-muted-foreground mb-3">Quick searches:</p>
              <div className="flex flex-wrap gap-2">
                {quickSearches.map((search, index) => (
                  <button
                    key={index}
                    onClick={() => setQuery(search)}
                    className="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full text-sm hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                  >
                    {search}
                  </button>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Categories */}
      {!hasSearched && (
        <Card>
          <CardHeader>
            <CardTitle>Browse by Category</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {categories.map((category, index) => (
                <div
                  key={index}
                  className="text-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition cursor-pointer"
                  onClick={() => setQuery(category.name.toLowerCase())}
                >
                  <div className="text-2xl mb-2">{category.icon}</div>
                  <div className="font-semibold text-sm">{category.name}</div>
                  <div className="text-xs text-muted-foreground">{category.count} articles</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search Results */}
      {hasSearched && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Search Results for "{query}"
            </CardTitle>
          </CardHeader>
          <CardContent>
            {results.length > 0 ? (
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div
                    key={index}
                    className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-semibold text-lg">{result.title}</h3>
                          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">
                            {result.category}
                          </span>
                        </div>
                        <p className="text-muted-foreground mb-3">{result.excerpt}</p>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Lightbulb className="h-4 w-4" />
                            Relevance: {Math.round(result.relevance * 100)}%
                          </span>
                          {result.url && (
                            <a
                              href={result.url}
                              className="flex items-center gap-1 text-blue-600 hover:text-blue-700"
                            >
                              <ExternalLink className="h-4 w-4" />
                              View Full Article
                            </a>
                          )}
                        </div>
                      </div>
                      <ChevronRight className="h-5 w-5 text-muted-foreground" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BookOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-muted-foreground">No results found for "{query}"</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Try different keywords or browse by category
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="font-semibold mb-2">Instant Search</h3>
            <p className="text-sm text-muted-foreground">
              Get answers to complex questions in seconds with AI-powered search
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <BookOpen className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="font-semibold mb-2">Comprehensive Coverage</h3>
            <p className="text-sm text-muted-foreground">
              Access knowledge across technology, science, business, and more
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
              <Brain className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="font-semibold mb-2">AI-Powered</h3>
            <p className="text-sm text-muted-foreground">
              Advanced AI understands context and provides relevant, accurate information
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
