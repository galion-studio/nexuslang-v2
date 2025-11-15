'use client'

import { useState } from 'react'
import { Github, Twitter, Linkedin, Mail, MapPin, Award } from 'lucide-react'

interface TeamMember {
  id: string
  name: string
  role: string
  bio: string
  image: string
  location: string
  joinDate: string
  skills: string[]
  social: {
    github?: string
    twitter?: string
    linkedin?: string
    email?: string
  }
  achievements: string[]
}

const teamMembers: TeamMember[] = [
  {
    id: 'elon-musk',
    name: 'Elon Musk',
    role: 'Visionary & Chief Architect',
    bio: 'Serial entrepreneur and founder of multiple groundbreaking companies. Leading Galion\'s mission to accelerate human scientific discovery through AI.',
    image: '/api/placeholder/200/200',
    location: 'Austin, TX',
    joinDate: '2023',
    skills: ['AI', 'Space', 'Electric Vehicles', 'Sustainable Energy'],
    social: {
      twitter: 'https://twitter.com/elonmusk',
      linkedin: 'https://linkedin.com/in/elonmusk'
    },
    achievements: [
      'Founded Tesla, SpaceX, Neuralink',
      'Advanced AI safety research',
      'Sustainable energy pioneer'
    ]
  },
  {
    id: 'sarah-chen',
    name: 'Sarah Chen',
    role: 'Chief Technology Officer',
    bio: 'Former Google AI researcher with 15+ years in machine learning and natural language processing. Leads our technical vision and voice AI innovations.',
    image: '/api/placeholder/200/200',
    location: 'San Francisco, CA',
    joinDate: '2024',
    skills: ['Machine Learning', 'NLP', 'Voice AI', 'Distributed Systems'],
    social: {
      github: 'https://github.com/sarahchen',
      linkedin: 'https://linkedin.com/in/sarahchen',
      email: 'sarah@galion.ai'
    },
    achievements: [
      'PhD in Computer Science from Stanford',
      'Published 50+ papers in top AI conferences',
      'Former Google Brain researcher'
    ]
  },
  {
    id: 'marcus-johnson',
    name: 'Marcus Johnson',
    role: 'Head of Product Design',
    bio: 'Award-winning UX designer passionate about creating intuitive interfaces. Previously designed products used by millions at Meta and Apple.',
    image: '/api/placeholder/200/200',
    location: 'New York, NY',
    joinDate: '2024',
    skills: ['UX Design', 'Product Strategy', 'Voice Interfaces', 'Design Systems'],
    social: {
      linkedin: 'https://linkedin.com/in/marcusjohnson',
      twitter: 'https://twitter.com/marcusdesign',
      email: 'marcus@galion.ai'
    },
    achievements: [
      'Red Dot Design Award winner',
      'Designed interfaces for 100M+ users',
      'Former Apple design lead'
    ]
  },
  {
    id: 'dr-amara-patel',
    name: 'Dr. Amara Patel',
    role: 'AI Ethics & Safety Lead',
    bio: 'Philosopher and AI ethicist ensuring our technology benefits humanity. Former advisor to the UN AI Ethics Committee and author of "Ethical AI Design".',
    image: '/api/placeholder/200/200',
    location: 'Boston, MA',
    joinDate: '2024',
    skills: ['AI Ethics', 'Philosophy', 'Policy', 'Risk Assessment'],
    social: {
      linkedin: 'https://linkedin.com/in/amarapatel',
      twitter: 'https://twitter.com/amarapatel',
      email: 'amara@galion.ai'
    },
    achievements: [
      'Author of "Ethical AI Design" book',
      'UN AI Ethics Committee advisor',
      'PhD in Philosophy of Technology'
    ]
  },
  {
    id: 'alex-rodriguez',
    name: 'Alex Rodriguez',
    role: 'Lead Engineer',
    bio: 'Full-stack engineer with expertise in scalable systems and real-time applications. Previously built infrastructure serving billions of requests at Netflix.',
    image: '/api/placeholder/200/200',
    location: 'Seattle, WA',
    joinDate: '2024',
    skills: ['System Architecture', 'Real-time Systems', 'Cloud Infrastructure', 'Performance Optimization'],
    social: {
      github: 'https://github.com/alexrodriguez',
      linkedin: 'https://linkedin.com/in/alexrodriguez',
      email: 'alex@galion.ai'
    },
    achievements: [
      'Built Netflix streaming infrastructure',
      'Open source contributor to Kubernetes',
      'AWS certified solutions architect'
    ]
  },
  {
    id: 'lisa-zhang',
    name: 'Lisa Zhang',
    role: 'Voice AI Researcher',
    bio: 'Leading our voice processing innovations with groundbreaking work in conversational AI. Former research scientist at OpenAI and DeepMind.',
    image: '/api/placeholder/200/200',
    location: 'Palo Alto, CA',
    joinDate: '2024',
    skills: ['Voice AI', 'Conversational Systems', 'Speech Recognition', 'Neural Networks'],
    social: {
      github: 'https://github.com/lisazhang',
      linkedin: 'https://linkedin.com/in/lisazhang',
      email: 'lisa@galion.ai'
    },
    achievements: [
      'Published breakthrough paper on voice synthesis',
      'Former OpenAI speech research lead',
      'PhD in Speech Processing'
    ]
  }
]

interface TeamProfilesProps {
  className?: string
}

export function TeamProfiles({ className = '' }: TeamProfilesProps) {
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null)

  return (
    <div className={className}>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {teamMembers.map((member) => (
          <div
            key={member.id}
            className="bg-surface rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer"
            onClick={() => setSelectedMember(member)}
          >
            {/* Profile Image */}
            <div className="aspect-square bg-gradient-to-br from-primary/20 to-accent/20 relative overflow-hidden">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl font-bold text-primary">
                      {member.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <p className="text-sm text-foreground-muted">Profile Photo</p>
                </div>
              </div>
            </div>

            {/* Profile Info */}
            <div className="p-6">
              <h3 className="text-xl font-semibold text-foreground mb-1">{member.name}</h3>
              <p className="text-primary font-medium mb-3">{member.role}</p>
              <p className="text-foreground-muted text-sm mb-4 line-clamp-3">{member.bio}</p>

              {/* Location and Join Date */}
              <div className="flex items-center justify-between text-xs text-foreground-muted mb-4">
                <div className="flex items-center">
                  <MapPin className="w-3 h-3 mr-1" />
                  {member.location}
                </div>
                <span>Joined {member.joinDate}</span>
              </div>

              {/* Skills */}
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                  {member.skills.slice(0, 3).map((skill) => (
                    <span
                      key={skill}
                      className="px-2 py-1 bg-surface-hover text-foreground-muted text-xs rounded-md"
                    >
                      {skill}
                    </span>
                  ))}
                  {member.skills.length > 3 && (
                    <span className="px-2 py-1 bg-surface-hover text-foreground-muted text-xs rounded-md">
                      +{member.skills.length - 3}
                    </span>
                  )}
                </div>
              </div>

              {/* Social Links */}
              <div className="flex space-x-3">
                {member.social.github && (
                  <a
                    href={member.social.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-foreground-muted hover:text-foreground transition-colors"
                  >
                    <Github className="w-4 h-4" />
                  </a>
                )}
                {member.social.twitter && (
                  <a
                    href={member.social.twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-foreground-muted hover:text-foreground transition-colors"
                  >
                    <Twitter className="w-4 h-4" />
                  </a>
                )}
                {member.social.linkedin && (
                  <a
                    href={member.social.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-foreground-muted hover:text-foreground transition-colors"
                  >
                    <Linkedin className="w-4 h-4" />
                  </a>
                )}
                {member.social.email && (
                  <a
                    href={`mailto:${member.social.email}`}
                    className="text-foreground-muted hover:text-foreground transition-colors"
                  >
                    <Mail className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Member Detail Modal */}
      {selectedMember && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-surface rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                    <span className="text-xl font-bold text-primary">
                      {selectedMember.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">{selectedMember.name}</h2>
                    <p className="text-primary font-medium">{selectedMember.role}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedMember(null)}
                  className="text-foreground-muted hover:text-foreground text-xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">About</h3>
                  <p className="text-foreground-muted">{selectedMember.bio}</p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground mb-3">Skills</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedMember.skills.map((skill) => (
                        <span
                          key={skill}
                          className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-foreground mb-3">Location</h3>
                    <div className="flex items-center text-foreground-muted">
                      <MapPin className="w-4 h-4 mr-2" />
                      {selectedMember.location}
                    </div>
                    <div className="flex items-center text-foreground-muted mt-2">
                      <Award className="w-4 h-4 mr-2" />
                      Joined {selectedMember.joinDate}
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-3">Achievements</h3>
                  <ul className="space-y-2">
                    {selectedMember.achievements.map((achievement, index) => (
                      <li key={index} className="flex items-start">
                        <Award className="w-4 h-4 text-primary mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-foreground-muted">{achievement}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-3">Connect</h3>
                  <div className="flex space-x-4">
                    {selectedMember.social.github && (
                      <a
                        href={selectedMember.social.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 text-foreground-muted hover:text-foreground transition-colors"
                      >
                        <Github className="w-4 h-4" />
                        <span>GitHub</span>
                      </a>
                    )}
                    {selectedMember.social.twitter && (
                      <a
                        href={selectedMember.social.twitter}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 text-foreground-muted hover:text-foreground transition-colors"
                      >
                        <Twitter className="w-4 h-4" />
                        <span>Twitter</span>
                      </a>
                    )}
                    {selectedMember.social.linkedin && (
                      <a
                        href={selectedMember.social.linkedin}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 text-foreground-muted hover:text-foreground transition-colors"
                      >
                        <Linkedin className="w-4 h-4" />
                        <span>LinkedIn</span>
                      </a>
                    )}
                    {selectedMember.social.email && (
                      <a
                        href={`mailto:${selectedMember.social.email}`}
                        className="flex items-center space-x-2 text-foreground-muted hover:text-foreground transition-colors"
                      >
                        <Mail className="w-4 h-4" />
                        <span>Email</span>
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TeamProfiles
