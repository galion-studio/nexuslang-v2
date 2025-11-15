'use client'

import { useEffect } from 'react'
import { Target, Users, Lightbulb, Award, TrendingUp, Heart } from 'lucide-react'

export default function AboutPage() {
  useEffect(() => {
    // Set platform attribute for styling
    document.documentElement.setAttribute('data-platform', 'studio')
  }, [])

  const values = [
    {
      icon: Target,
      title: 'Innovation First',
      description: 'We push the boundaries of what\'s possible with AI, creating tools that augment human creativity rather than replace it.'
    },
    {
      icon: Users,
      title: 'Human-Centered',
      description: 'Every decision we make starts with understanding human needs and how technology can serve them better.'
    },
    {
      icon: Lightbulb,
      title: 'Open Source',
      description: 'We believe in the power of community and open collaboration to accelerate technological progress.'
    },
    {
      icon: Heart,
      title: 'Ethical AI',
      description: 'Building AI that is transparent, fair, and beneficial to humanity is at the core of everything we do.'
    }
  ]

  const milestones = [
    {
      year: '2023',
      title: 'Galion Founded',
      description: 'Started with a vision to create the most intuitive AI platform ever built.'
    },
    {
      year: '2024',
      title: 'Voice-First Revolution',
      description: 'Launched NexusLang and the first truly voice-native development environment.'
    },
    {
      year: '2025',
      title: 'Global Expansion',
      description: 'Reached 10,000+ beta users and expanded to serve developers worldwide.'
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/5 to-transparent" />
        <div>
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-display font-bold italic text-primary mb-6">
              "Your imagination is the end."
            </h1>
            <p className="text-xl md:text-2xl text-foreground-muted mb-8 leading-relaxed">
              We're building the future of human-AI collaboration, one voice at a time.
            </p>
            <p className="text-lg text-foreground-muted max-w-3xl mx-auto">
              Galion is not just another AI company. We're creating a paradigm shift in how humans interact with technology.
              Through voice-first interfaces and intuitive design, we're making AI as natural as human conversation.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-surface">
        <div>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-foreground mb-8">Our Mission</h2>
            <div className="bg-gradient-to-r from-primary to-accent p-8 rounded-2xl text-white">
              <p className="text-xl leading-relaxed mb-6">
                To democratize access to powerful AI tools by making them as easy to use as speaking to a friend.
              </p>
              <p className="text-lg opacity-90">
                We believe that the best technology disappears into the background, becoming an extension of human capability rather than a barrier to overcome.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20">
        <div>
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-4">Our Values</h2>
            <p className="text-lg text-foreground-muted max-w-2xl mx-auto">
              These principles guide every decision we make and every product we build.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {values.map((value, index) => {
              const IconComponent = value.icon
              return (
                <div key={index} className="bg-surface p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mr-4">
                      <IconComponent className="w-6 h-6 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground">{value.title}</h3>
                  </div>
                  <p className="text-foreground-muted leading-relaxed">{value.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Journey Section */}
      <section className="py-20 bg-surface">
        <div>
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-4">Our Journey</h2>
            <p className="text-lg text-foreground-muted">
              From a simple idea to a global platform
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-1/2 transform -translate-x-1/2 w-0.5 h-full bg-primary/20" />

              {milestones.map((milestone, index) => (
                <div key={index} className={`relative flex items-center mb-12 ${index % 2 === 0 ? 'justify-start' : 'justify-end'}`}>
                  <div className={`w-full md:w-1/2 ${index % 2 === 0 ? 'pr-8 md:pr-16' : 'pl-8 md:pl-16'}`}>
                    <div className="bg-background p-6 rounded-xl shadow-lg">
                      <div className="flex items-center mb-3">
                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center mr-3">
                          <span className="text-primary-foreground font-bold text-sm">{milestone.year.slice(-2)}</span>
                        </div>
                        <h3 className="text-lg font-semibold text-foreground">{milestone.title}</h3>
                      </div>
                      <p className="text-foreground-muted">{milestone.description}</p>
                    </div>
                  </div>

                  {/* Timeline dot */}
                  <div className="absolute left-1/2 transform -translate-x-1/2 w-4 h-4 bg-primary rounded-full border-4 border-background" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">10,000+</div>
              <div className="text-foreground-muted">Beta Users</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">50+</div>
              <div className="text-foreground-muted">Countries</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary mb-2">99.9%</div>
              <div className="text-foreground-muted">Uptime</div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-20 bg-gradient-to-r from-primary to-accent">
        <div>
          <div className="text-center text-white">
            <h2 className="text-3xl font-bold mb-4">Join Our Mission</h2>
            <p className="text-xl mb-8 opacity-90">
              Help us build the future of human-AI interaction
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-8 py-3 bg-white text-primary font-semibold rounded-lg hover:bg-gray-100 transition-colors">
                Join Beta
              </button>
              <button className="px-8 py-3 border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-primary transition-colors">
                View Careers
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}