'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'

interface CodeExample {
  id: string
  title: string
  description: string
  code: string
  category: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  tags: string[]
  author?: string
  featured?: boolean
}

const examples: CodeExample[] = [
  {
    id: 'hello-world',
    title: 'Hello World',
    description: 'The classic first program - print a greeting to the world',
    code: `// Hello World in NexusLang
print("Hello, NexusLang World! 🌍")

// With variables
let greeting = "Welcome to AI programming!"
print(greeting)`,
    category: 'basics',
    difficulty: 'beginner',
    tags: ['print', 'variables', 'basics'],
    featured: true
  },
  {
    id: 'personality-basic',
    title: 'Basic Personality',
    description: 'Define a simple AI personality for your applications',
    code: `// Define a helpful AI personality
personality {
    helpfulness: 0.9,
    empathy: 0.8,
    transparency: 0.7
}

// The AI will now behave according to these traits
print("AI personality configured!")`,
    category: 'personality',
    difficulty: 'beginner',
    tags: ['personality', 'traits', 'ai'],
    featured: true
  },
  {
    id: 'voice-greeting',
    title: 'Voice Greeting',
    description: 'Create an AI that greets users with voice',
    code: `// Voice-enabled AI greeting
personality {
    friendliness: 0.9,
    enthusiasm: 0.8
}

fn voice_greeting() {
    // Speak a friendly greeting
    say("Hello! Welcome to NexusLang!", emotion="excited")

    // Listen for user response
    let user_input = listen(timeout=10)

    // Respond based on input
    if user_input {
        say("I heard you say: " + user_input, emotion="friendly")
    } else {
        say("I didn't catch that. Could you try again?", emotion="helpful")
    }
}

// Execute the voice greeting
voice_greeting()`,
    category: 'voice',
    difficulty: 'intermediate',
    tags: ['voice', 'speech', 'interaction'],
    featured: true
  },
  {
    id: 'knowledge-query',
    title: 'Knowledge Query',
    description: 'Query universal knowledge base for information',
    code: `// Query knowledge about AI
let ai_facts = knowledge("artificial intelligence")

print("🤖 AI Knowledge Results:")
for fact in ai_facts {
    print("📚 " + fact["title"])
    print("   " + fact["summary"])
    print("   Confidence: " + fact["confidence"])
    print("")
}

// Query related concepts
let related = knowledge_related("machine learning")
print("🔗 Related topics:")
for topic in related {
    print("• " + topic)
}`,
    category: 'knowledge',
    difficulty: 'intermediate',
    tags: ['knowledge', 'ai', 'query'],
    featured: true
  },
  {
    id: 'neural-network',
    title: 'Simple Neural Network',
    description: 'Build and train a basic neural network',
    code: `// Simple neural network for digit recognition
personality {
    analytical: 0.9,
    precision: 0.8
}

// Define the network architecture
let model = Sequential(
    Linear(784, 128),  // Input layer (28x28 images)
    ReLU(),             // Activation function
    Linear(128, 64),    // Hidden layer
    ReLU(),
    Linear(64, 10)      // Output layer (10 digits)
)

// Training data (simplified example)
let training_data = load_mnist_training_data()
let test_data = load_mnist_test_data()

// Train the model
print("🧠 Training neural network...")
model.train(training_data, epochs=10, learning_rate=0.01)

// Evaluate performance
let accuracy = model.evaluate(test_data)
print("🎯 Model accuracy: " + (accuracy * 100).toFixed(2) + "%")

// Make a prediction
let sample_image = test_data[0]
let prediction = model.predict(sample_image)
print("🔮 Prediction for sample image: " + prediction)`,
    category: 'ml',
    difficulty: 'advanced',
    tags: ['neural-network', 'ml', 'training', 'prediction']
  },
  {
    id: 'creative-writer',
    title: 'Creative Writing AI',
    description: 'AI that generates creative stories and content',
    code: `// Creative writing AI
personality {
    creativity: 0.95,
    imagination: 0.9,
    empathy: 0.8,
    originality: 0.85
}

fn write_short_story(theme, length) {
    // Generate story premise
    let premise = generate_story_premise(theme)

    // Develop characters
    let characters = create_characters(3, theme)

    // Build plot structure
    let plot = develop_plot(premise, characters, length)

    // Write the story
    let story = write_narrative(plot, characters)

    // Add creative flair
    let enhanced_story = add_literary_devices(story)

    return enhanced_story
}

// Write a sci-fi story
let theme = "time travel adventure"
let story_length = "short"

print("📖 Generating creative story...")
let story = write_short_story(theme, story_length)

print("\\n🎭 Generated Story:")
print("==================")
print(story)
print("==================")
print("\\n✨ Story generated with creative AI!")`,
    category: 'creative',
    difficulty: 'advanced',
    tags: ['writing', 'creative', 'ai', 'storytelling']
  },
  {
    id: 'data-analysis',
    title: 'Data Analysis Pipeline',
    description: 'Analyze datasets with statistical methods and visualization',
    code: `// Data analysis pipeline
personality {
    analytical: 0.9,
    precision: 0.8,
    thoroughness: 0.85
}

fn analyze_dataset(filepath) {
    // Load the dataset
    let data = load_csv(filepath)

    print("📊 Dataset Analysis Report")
    print("==========================")

    // Basic statistics
    print("📈 Basic Statistics:")
    print("Records: " + data.length)
    print("Columns: " + data.columns.length)

    for column in data.columns {
        let stats = data[column].stats()
        print(column + " - Mean: " + stats.mean.toFixed(2) +
              ", Std: " + stats.std.toFixed(2))
    }

    // Data quality check
    print("\\n🔍 Data Quality:")
    let quality_report = data.quality_check()
    print("Missing values: " + quality_report.missing_percentage + "%")
    print("Duplicate rows: " + quality_report.duplicates)

    // Generate visualizations
    print("\\n📊 Generating visualizations...")

    // Histogram for numerical columns
    for column in data.numerical_columns {
        plot_histogram(data[column], "Histogram of " + column)
    }

    // Correlation heatmap
    plot_correlation_heatmap(data, "Feature Correlations")

    // Box plots for outlier detection
    for column in data.numerical_columns {
        plot_boxplot(data[column], "Boxplot of " + column)
    }

    // Generate insights
    let insights = generate_data_insights(data)
    print("\\n💡 Key Insights:")
    for insight in insights {
        print("• " + insight)
    }

    return data.analysis_summary()
}

// Analyze a sample dataset
let dataset_path = "sample_data.csv"
let analysis = analyze_dataset(dataset_path)

print("\\n✅ Analysis complete!")`,
    category: 'data',
    difficulty: 'advanced',
    tags: ['data-analysis', 'statistics', 'visualization', 'insights']
  },
  {
    id: 'voice-assistant',
    title: 'Complete Voice Assistant',
    description: 'Full-featured voice assistant with multiple capabilities',
    code: `// Complete voice assistant
personality {
    empathetic: 0.9,
    helpful: 0.95,
    patient: 0.8,
    knowledgeable: 0.85
}

fn voice_assistant() {
    say("Hello! I'm your NexusLang voice assistant. How can I help you today?",
        emotion="friendly")

    let conversation_active = true

    while conversation_active {
        // Listen for user input
        let user_input = listen(timeout=15)

        if !user_input {
            say("I didn't hear anything. Could you please try again?", emotion="helpful")
            continue
        }

        print("👤 User said: " + user_input)

        // Determine intent and respond
        let intent = analyze_intent(user_input)
        let response = generate_response(user_input, intent)

        // Query knowledge if needed
        if intent.requires_knowledge {
            let facts = knowledge(user_input)
            response = enhance_response_with_knowledge(response, facts)
        }

        // Speak the response
        let emotion = determine_emotion(intent, response)
        say(response, emotion=emotion)

        // Check if user wants to end conversation
        if intent.type == "goodbye" || contains_goodbye(user_input) {
            say("Goodbye! It was great talking with you. Have a wonderful day!",
                emotion="warm")
            conversation_active = false
        }
    }
}

fn analyze_intent(text) {
    // Analyze the user's intent
    let intent_analysis = {
        type: classify_intent(text),
        sentiment: analyze_sentiment(text),
        urgency: detect_urgency(text),
        requires_knowledge: contains_question(text),
        complexity: assess_complexity(text)
    }

    return intent_analysis
}

fn generate_response(input, intent) {
    // Generate contextual response
    let base_response = generate_base_response(input, intent.type)

    // Personalize based on personality traits
    let personalized_response = adapt_to_personality(base_response, intent.sentiment)

    // Add helpful suggestions if appropriate
    if intent.complexity > 0.7 {
        personalized_response += generate_followup_suggestions(input)
    }

    return personalized_response
}

fn determine_emotion(intent, response) {
    // Choose appropriate emotion for response
    if intent.sentiment == "negative" {
        return "empathetic"
    } else if intent.urgency == "high" {
        return "urgent"
    } else if intent.type == "praise" {
        return "grateful"
    } else {
        return "helpful"
    }
}

// Start the voice assistant
print("🎤 Starting NexusLang Voice Assistant...")
voice_assistant()
print("👋 Voice assistant session ended.")`,
    category: 'voice',
    difficulty: 'advanced',
    tags: ['voice-assistant', 'conversation', 'ai', 'interaction'],
    featured: true
  }
]

const categories = [
  { id: 'all', name: 'All Examples', icon: '📚' },
  { id: 'basics', name: 'Basics', icon: '🎯' },
  { id: 'personality', name: 'Personality', icon: '🎭' },
  { id: 'voice', name: 'Voice', icon: '🎤' },
  { id: 'knowledge', name: 'Knowledge', icon: '🧠' },
  { id: 'ml', name: 'Machine Learning', icon: '🤖' },
  { id: 'creative', name: 'Creative', icon: '🎨' },
  { id: 'data', name: 'Data Analysis', icon: '📊' }
]

interface ExamplesLibraryProps {
  onExampleSelect?: (example: CodeExample) => void
}

const ExamplesLibrary: React.FC<ExamplesLibraryProps> = ({ onExampleSelect }) => {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all')
  const [showFeatured, setShowFeatured] = useState(false)

  const filteredExamples = examples.filter(example => {
    const matchesCategory = selectedCategory === 'all' || example.category === selectedCategory
    const matchesSearch = searchQuery === '' ||
      example.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      example.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      example.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesDifficulty = selectedDifficulty === 'all' || example.difficulty === selectedDifficulty
    const matchesFeatured = !showFeatured || example.featured

    return matchesCategory && matchesSearch && matchesDifficulty && matchesFeatured
  })

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-400 bg-green-900/20'
      case 'intermediate': return 'text-yellow-400 bg-yellow-900/20'
      case 'advanced': return 'text-red-400 bg-red-900/20'
      default: return 'text-gray-400 bg-gray-900/20'
    }
  }

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🔍 Search & Filter
            <span className="text-sm text-gray-400 font-normal">
              {filteredExamples.length} examples found
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Search */}
            <Input
              placeholder="Search examples, tags, or descriptions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full"
            />

            {/* Filters */}
            <div className="flex flex-wrap gap-2">
              {/* Featured Toggle */}
              <Button
                onClick={() => setShowFeatured(!showFeatured)}
                variant={showFeatured ? "default" : "outline"}
                size="sm"
              >
                ⭐ Featured Only
              </Button>

              {/* Difficulty Filter */}
              <div className="flex gap-1">
                {['all', 'beginner', 'intermediate', 'advanced'].map((level) => (
                  <Button
                    key={level}
                    onClick={() => setSelectedDifficulty(level)}
                    variant={selectedDifficulty === level ? "default" : "outline"}
                    size="sm"
                    className="capitalize"
                  >
                    {level === 'all' ? 'All' : level}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Categories */}
      <Card>
        <CardHeader>
          <CardTitle>📂 Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
            {categories.map((category) => (
              <Button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                variant={selectedCategory === category.id ? "default" : "outline"}
                size="sm"
                className="text-xs"
              >
                <span className="mr-1">{category.icon}</span>
                {category.name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Examples Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredExamples.map((example) => (
          <Card
            key={example.id}
            className="hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => onExampleSelect?.(example)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  {example.featured && <span className="text-yellow-400">⭐</span>}
                  {example.title}
                </CardTitle>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(example.difficulty)}`}>
                  {example.difficulty}
                </span>
              </div>
              <p className="text-sm text-gray-400">{example.description}</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {/* Code Preview */}
                <div className="bg-gray-900 p-3 rounded-lg font-mono text-sm text-green-400 overflow-hidden">
                  <pre className="line-clamp-4">
                    {example.code.split('\n').slice(0, 4).join('\n')}
                    {example.code.split('\n').length > 4 && '\n...'}
                  </pre>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {example.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="text-xs bg-blue-600/50 text-blue-200 px-2 py-1 rounded"
                    >
                      #{tag}
                    </span>
                  ))}
                  {example.tags.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{example.tags.length - 3} more
                    </span>
                  )}
                </div>

                {/* Action Button */}
                <Button
                  onClick={(e) => {
                    e.stopPropagation()
                    onExampleSelect?.(example)
                  }}
                  className="w-full"
                  size="sm"
                >
                  Load Example
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredExamples.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-4xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-white mb-2">No examples found</h3>
            <p className="text-gray-400 mb-4">
              Try adjusting your search or filter criteria
            </p>
            <Button
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory('all')
                setSelectedDifficulty('all')
                setShowFeatured(false)
              }}
              variant="outline"
            >
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Stats */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-400">{examples.length}</div>
              <div className="text-sm text-gray-400">Total Examples</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-400">{examples.filter(e => e.featured).length}</div>
              <div className="text-sm text-gray-400">Featured</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-400">{categories.length - 1}</div>
              <div className="text-sm text-gray-400">Categories</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-400">
                {new Set(examples.flatMap(e => e.tags)).size}
              </div>
              <div className="text-sm text-gray-400">Tags</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ExamplesLibrary
