'use client'

/**
 * Developer Platform - API Documentation Hub
 * Complete reference for all Galion APIs
 */

import { useState } from 'react'
import Link from 'next/link'
import { Code, Book, Zap, Key, FileText, Github } from 'lucide-react'

export default function DevelopersPage() {
  const [selectedAPI, setSelectedAPI] = useState('nexuslang')
  
  const apis = [
    {
      id: 'nexuslang',
      name: 'NexusLang API',
      description: 'Execute AI-native code, compile to binary, analyze programs',
      icon: Code,
      color: 'purple',
      endpoints: 4,
      cost: '1 credit per execution'
    },
    {
      id: 'ai',
      name: 'AI Generation API',
      description: 'Text, images, videos, voice - 30+ models via OpenRouter',
      icon: Zap,
      color: 'blue',
      endpoints: 8,
      cost: '2-50 credits per request'
    },
    {
      id: 'grokopedia',
      name: 'Grokopedia API',
      description: 'Semantic search, knowledge graph, fact verification',
      icon: Book,
      color: 'green',
      endpoints: 6,
      cost: '1 credit per search'
    },
    {
      id: 'content',
      name: 'Content Manager API',
      description: 'Multi-platform publishing, scheduling, analytics',
      icon: FileText,
      color: 'orange',
      endpoints: 12,
      cost: '5 credits per post'
    }
  ]
  
  const exampleCode = {
    nexuslang: {
      curl: `curl -X POST https://api.developer.galion.app/api/v2/nexuslang/run \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "code": "fn main() { print(\\"Hello, NexusLang!\\") }\\nmain()",
    "compile_to_binary": false
  }'`,
      javascript: `import { GalionClient } from '@galion/sdk'

const client = new GalionClient('YOUR_API_KEY')

// Execute NexusLang code
const result = await client.nexuslang.run(\`
  fn main() {
    print("Hello, NexusLang!")
  }
  main()
\`)

console.log(result.output)  // "Hello, NexusLang!"
console.log(result.execution_time)  // 67.2ms
console.log(result.credits_used)  // 1`,
      python: `from galion import GalionClient

client = GalionClient(api_key='YOUR_API_KEY')

# Execute NexusLang code
result = client.nexuslang.run("""
  fn main() {
    print("Hello, NexusLang!")
  }
  main()
""")

print(result['output'])  # "Hello, NexusLang!"
print(result['execution_time'])  # 67.2
print(result['credits_used'])  # 1`
    },
    ai: {
      curl: `curl -X POST https://api.developer.galion.app/api/v2/ai/chat \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "messages": [
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "model": "anthropic/claude-3.5-sonnet",
    "max_tokens": 1000
  }'`,
      javascript: `const client = new GalionClient('YOUR_API_KEY')

// Chat with Claude via OpenRouter
const response = await client.ai.chat([
  { role: 'user', content: 'Explain quantum computing' }
], {
  model: 'anthropic/claude-3.5-sonnet',
  max_tokens: 1000
})

console.log(response.content)
console.log(\`Used \${response.credits_used} credits\`)`,
      python: `client = GalionClient(api_key='YOUR_API_KEY')

# Chat with Claude via OpenRouter
response = client.ai.chat(
    messages=[
        {'role': 'user', 'content': 'Explain quantum computing'}
    ],
    model='anthropic/claude-3.5-sonnet',
    max_tokens=1000
)

print(response['content'])
print(f"Used {response['credits_used']} credits")`
    },
    grokopedia: {
      curl: `curl -X GET "https://api.developer.galion.app/api/v2/grokopedia/search?q=machine+learning" \\
  -H "Authorization: Bearer YOUR_API_KEY"`,
      javascript: `const client = new GalionClient('YOUR_API_KEY')

// Search knowledge base
const results = await client.grokopedia.search('machine learning')

results.forEach(entry => {
  console.log(entry.title)
  console.log(entry.summary)
  console.log(\`Confidence: \${entry.confidence}\`)
})`,
      python: `client = GalionClient(api_key='YOUR_API_KEY')

# Search knowledge base
results = client.grokopedia.search('machine learning')

for entry in results:
    print(entry['title'])
    print(entry['summary'])
    print(f"Confidence: {entry['confidence']}")`
    },
    content: {
      curl: `curl -X POST https://api.developer.galion.app/api/v2/content-manager/posts \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "brand_id": "YOUR_BRAND_ID",
    "title": "Check out our new feature!",
    "content": "We just launched something amazing...",
    "platforms": ["twitter", "linkedin", "reddit"]
  }'`,
      javascript: `const client = new GalionClient('YOUR_API_KEY')

// Create multi-platform post
const post = await client.content.createPost({
  brand_id: 'YOUR_BRAND_ID',
  title: 'Check out our new feature!',
  content: 'We just launched something amazing...',
  platforms: ['twitter', 'linkedin', 'reddit']
})

console.log(\`Post created: \${post.id}\`)
console.log(\`Publishing to \${post.platforms.length} platforms\`)`,
      python: `client = GalionClient(api_key='YOUR_API_KEY')

# Create multi-platform post
post = client.content.create_post(
    brand_id='YOUR_BRAND_ID',
    title='Check out our new feature!',
    content='We just launched something amazing...',
    platforms=['twitter', 'linkedin', 'reddit']
)

print(f"Post created: {post['id']}")
print(f"Publishing to {len(post['platforms'])} platforms")`
    }
  }
  
  const [codeLanguage, setCodeLanguage] = useState<'curl' | 'javascript' | 'python'>('javascript')
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      {/* Hero */}
      <div className="border-b border-zinc-800">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="text-center mb-12">
            <div className="mb-4">
              <span className="px-4 py-2 bg-blue-600/20 text-blue-400 rounded-full text-sm font-semibold">
                DEVELOPER PLATFORM
              </span>
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              Build with Galion APIs
            </h1>
            <p className="text-xl text-zinc-400 mb-8">
              Access NexusLang, AI generation, knowledge base, and more through simple REST APIs
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                href="/auth/register"
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 
                           hover:to-purple-700 text-white rounded-lg font-semibold transition"
              >
                Get API Key (Free)
              </Link>
              <Link
                href="https://api.developer.galion.app/docs"
                target="_blank"
                className="px-8 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-semibold transition"
              >
                View API Docs
              </Link>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 text-center">
              <div className="text-3xl font-bold text-purple-400 mb-2">54</div>
              <div className="text-zinc-400">API Endpoints</div>
            </div>
            <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 text-center">
              <div className="text-3xl font-bold text-blue-400 mb-2">30+</div>
              <div className="text-zinc-400">AI Models</div>
            </div>
            <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 text-center">
              <div className="text-3xl font-bold text-green-400 mb-2">&lt;100ms</div>
              <div className="text-zinc-400">Response Time</div>
            </div>
            <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 text-center">
              <div className="text-3xl font-bold text-orange-400 mb-2">99.9%</div>
              <div className="text-zinc-400">Uptime SLA</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* API Explorer */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white mb-8">Available APIs</h2>
        
        <div className="grid lg:grid-cols-4 gap-6 mb-12">
          {apis.map(api => (
            <button
              key={api.id}
              onClick={() => setSelectedAPI(api.id)}
              className={`p-6 rounded-lg border-2 text-left transition ${
                selectedAPI === api.id
                  ? `border-${api.color}-500 bg-${api.color}-600/10`
                  : 'border-zinc-800 bg-zinc-900 hover:border-zinc-700'
              }`}
            >
              <div className={`w-12 h-12 bg-${api.color}-600/20 rounded-lg flex items-center justify-center mb-4`}>
                <api.icon className={`text-${api.color}-400`} size={24} />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{api.name}</h3>
              <p className="text-sm text-zinc-400 mb-4">{api.description}</p>
              <div className="flex items-center justify-between text-xs">
                <span className="text-zinc-500">{api.endpoints} endpoints</span>
                <span className="text-green-400">{api.cost}</span>
              </div>
            </button>
          ))}
        </div>
        
        {/* Code Examples */}
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-white">Quick Start Example</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setCodeLanguage('curl')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  codeLanguage === 'curl'
                    ? 'bg-purple-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                cURL
              </button>
              <button
                onClick={() => setCodeLanguage('javascript')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  codeLanguage === 'javascript'
                    ? 'bg-purple-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                JavaScript
              </button>
              <button
                onClick={() => setCodeLanguage('python')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  codeLanguage === 'python'
                    ? 'bg-purple-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                Python
              </button>
            </div>
          </div>
          
          <pre className="bg-zinc-950 p-6 rounded-lg overflow-x-auto">
            <code className="text-sm text-zinc-300 font-mono">
              {exampleCode[selectedAPI as keyof typeof exampleCode][codeLanguage]}
            </code>
          </pre>
          
          <div className="mt-4 flex gap-4">
            <Link
              href="https://api.developer.galion.app/docs"
              target="_blank"
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
            >
              Full API Docs
            </Link>
            <Link
              href="/auth/register"
              className="px-6 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-medium transition"
            >
              Get API Key
            </Link>
          </div>
        </div>
      </div>
      
      {/* SDKs & Tools */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white mb-8">SDKs & Tools</h2>
        
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
              <Github size={24} className="text-yellow-400" />
              JavaScript/TypeScript
            </h3>
            <p className="text-zinc-400 mb-4">
              Official SDK for Node.js, React, Next.js, and browser applications
            </p>
            <pre className="bg-zinc-950 p-3 rounded text-sm text-zinc-300 mb-4">
              npm install @galion/sdk
            </pre>
            <Link
              href="https://github.com/galion-studio/galion-sdk-js"
              target="_blank"
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              View on GitHub →
            </Link>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
              <Github size={24} className="text-blue-400" />
              Python
            </h3>
            <p className="text-zinc-400 mb-4">
              Official SDK for Python, Flask, Django, FastAPI applications
            </p>
            <pre className="bg-zinc-950 p-3 rounded text-sm text-zinc-300 mb-4">
              pip install galion-sdk
            </pre>
            <Link
              href="https://github.com/galion-studio/galion-sdk-python"
              target="_blank"
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              View on GitHub →
            </Link>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
              <Code size={24} className="text-green-400" />
              CLI Tool
            </h3>
            <p className="text-zinc-400 mb-4">
              Command-line interface for quick testing and automation
            </p>
            <pre className="bg-zinc-950 p-3 rounded text-sm text-zinc-300 mb-4">
              npm install -g @galion/cli
            </pre>
            <Link
              href="https://github.com/galion-studio/galion-cli"
              target="_blank"
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              View on GitHub →
            </Link>
          </div>
        </div>
      </div>
      
      {/* Integration Examples */}
      <div className="bg-zinc-900/50 border-y border-zinc-800">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <h2 className="text-3xl font-bold text-white mb-4 text-center">
            Integration Examples
          </h2>
          <p className="text-zinc-400 text-center mb-12">
            Real-world examples to get you started quickly
          </p>
          
          <div className="grid md:grid-cols-3 gap-6">
            <Link
              href="/developers/examples/chatbot"
              className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 hover:border-purple-600/50 transition"
            >
              <h3 className="text-xl font-bold text-white mb-2">Build a Chatbot</h3>
              <p className="text-zinc-400 mb-4">
                Create an AI chatbot with Claude Sonnet in 10 minutes
              </p>
              <span className="text-purple-400 text-sm">View Example →</span>
            </Link>
            
            <Link
              href="/developers/examples/image-generator"
              className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 hover:border-blue-600/50 transition"
            >
              <h3 className="text-xl font-bold text-white mb-2">Image Generator App</h3>
              <p className="text-zinc-400 mb-4">
                Build an image generation app with Next.js
              </p>
              <span className="text-blue-400 text-sm">View Example →</span>
            </Link>
            
            <Link
              href="/developers/examples/code-playground"
              className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 hover:border-green-600/50 transition"
            >
              <h3 className="text-xl font-bold text-white mb-2">Code Playground</h3>
              <p className="text-zinc-400 mb-4">
                Build a code execution platform with NexusLang API
              </p>
              <span className="text-green-400 text-sm">View Example →</span>
            </Link>
          </div>
        </div>
      </div>
      
      {/* Getting Started */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white mb-8 text-center">
          Getting Started in 3 Steps
        </h2>
        
        <div className="space-y-6">
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 flex items-start gap-4">
            <div className="w-10 h-10 bg-purple-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="text-purple-400 font-bold">1</span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Get Your API Key</h3>
              <p className="text-zinc-400 mb-3">
                Register for free and generate your API key from the dashboard
              </p>
              <Link
                href="/auth/register"
                className="text-purple-400 hover:text-purple-300 font-medium"
              >
                Create Account →
              </Link>
            </div>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 flex items-start gap-4">
            <div className="w-10 h-10 bg-blue-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="text-blue-400 font-bold">2</span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Install SDK or Use REST</h3>
              <p className="text-zinc-400 mb-3">
                Use our official SDKs or make direct REST API calls
              </p>
              <pre className="bg-zinc-950 p-3 rounded text-sm text-zinc-300">
                npm install @galion/sdk
              </pre>
            </div>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 flex items-start gap-4">
            <div className="w-10 h-10 bg-green-600/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="text-green-400 font-bold">3</span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Make Your First Call</h3>
              <p className="text-zinc-400 mb-3">
                Execute code, generate AI content, or search knowledge base
              </p>
              <Link
                href="https://api.developer.galion.app/docs"
                target="_blank"
                className="text-green-400 hover:text-green-300 font-medium"
              >
                View Full Documentation →
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* CTA */}
      <div className="border-t border-zinc-800">
        <div className="max-w-4xl mx-auto px-6 py-16 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Build Something Amazing?
          </h2>
          <p className="text-xl text-zinc-400 mb-8">
            Join thousands of developers using Galion APIs
          </p>
          <Link
            href="/auth/register"
            className="inline-block px-10 py-4 bg-gradient-to-r from-blue-600 to-purple-600 
                       hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-bold text-lg transition"
          >
            Get Started Free
          </Link>
          <p className="text-sm text-zinc-500 mt-4">
            100 free credits • No credit card required • 5 minutes to first API call
          </p>
        </div>
      </div>
    </div>
  )
}

