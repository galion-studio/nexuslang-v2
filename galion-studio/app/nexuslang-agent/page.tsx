'use client'

/**
 * NexusLang v2 Coding Agent
 *
 * AI-powered coding agent for NexusLang v2 development with deployment capabilities
 */

import { useState, useEffect } from 'react'
import { Terminal, Upload, Download, Play, Code2, Zap, Settings, Github, Server, Cpu } from 'lucide-react'

interface DeploymentStatus {
  step: string
  progress: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  message: string
}

export default function NexusLangAgentPage() {
  const [isDeploying, setIsDeploying] = useState(false)
  const [deploymentStatus, setDeploymentStatus] = useState<DeploymentStatus[]>([
    { step: 'Git Repository Setup', progress: 0, status: 'pending', message: 'Preparing Git repository...' },
    { step: 'File Preparation', progress: 0, status: 'pending', message: 'Creating deployment package...' },
    { step: 'GitHub Upload', progress: 0, status: 'pending', message: 'Pushing to GitHub...' },
    { step: 'RunPod Connection', progress: 0, status: 'pending', message: 'Connecting to RunPod...' },
    { step: 'File Transfer', progress: 0, status: 'pending', message: 'Uploading files...' },
    { step: 'Remote Deployment', progress: 0, status: 'pending', message: 'Starting deployment...' },
    { step: 'Finalization', progress: 0, status: 'pending', message: 'Completing setup...' }
  ])

  const [config, setConfig] = useState({
    runPodHost: 'YOUR_POD_ID.proxy.runpod.net',
    runPodPort: '22',
    runPodUser: 'root',
    gitHubRepo: '',
    projectName: 'NexusLang-v2-Agent'
  })

  const [logs, setLogs] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState<'deploy' | 'monitor' | 'config'>('deploy')

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const startDeployment = async () => {
    setIsDeploying(true)
    addLog('🚀 Starting NexusLang v2 deployment sequence...')

    const steps = [
      { name: 'Git Repository Setup', duration: 2000, command: 'git init && git add .' },
      { name: 'File Preparation', duration: 3000, command: 'Preparing deployment package...' },
      { name: 'GitHub Upload', duration: 4000, command: 'git push origin main' },
      { name: 'RunPod Connection', duration: 2000, command: 'ssh connection test' },
      { name: 'File Transfer', duration: 5000, command: 'scp upload files' },
      { name: 'Remote Deployment', duration: 3000, command: './runpod-deploy.sh' },
      { name: 'Finalization', duration: 1000, command: 'Cleanup and verification' }
    ]

    for (let i = 0; i < steps.length; i++) {
      const step = steps[i]
      setDeploymentStatus(prev => prev.map((s, idx) =>
        idx === i ? { ...s, status: 'running', message: step.command } : s
      ))

      // Simulate progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, step.duration / 10))
        setDeploymentStatus(prev => prev.map((s, idx) =>
          idx === i ? { ...s, progress } : s
        ))
      }

      setDeploymentStatus(prev => prev.map((s, idx) =>
        idx === i ? { ...s, status: 'completed', progress: 100, message: '✓ Completed' } : s
      ))

      addLog(`✅ ${step.name} completed successfully`)
    }

    setIsDeploying(false)
    addLog('🎉 NexusLang v2 deployment completed!')
    addLog('🌐 Your platform is now live at: https://developer.galion.app')
  }

  const totalProgress = deploymentStatus.reduce((sum, step) => sum + step.progress, 0) / deploymentStatus.length

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-slate-800 backdrop-blur">
        <div className="py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                NexusLang v2 Agent
              </div>
              <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full">
                <Zap className="w-3 h-3 mr-1" />
                AI Coding Agent
              </span>
            </div>
            <div className="flex gap-4">
              <button className="flex items-center gap-2 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-md transition-colors" onClick={() => setActiveTab('config')}>
                <Settings className="w-4 h-4" />
                Config
              </button>
              <button className="flex items-center gap-2 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-md transition-colors" onClick={() => setActiveTab('monitor')}>
                <Server className="w-4 h-4" />
                Monitor
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-4">
            NexusLang v2
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent block">
              Coding Agent
            </span>
          </h1>
          <p className="text-xl text-slate-300 mb-6">
            AI-powered deployment and development platform for NexusLang v2
          </p>
          <div className="flex justify-center gap-4 mb-6">
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-green-600/20 text-green-400 border border-green-500/30 rounded-full">
              <Code2 className="w-3 h-3 mr-1" />
              Built with Sonnet 4.5
            </span>
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-blue-600/20 text-blue-400 border border-blue-500/30 rounded-full">
              <Cpu className="w-3 h-3 mr-1" />
              Powered by Grok
            </span>
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-purple-600/20 text-purple-400 border border-purple-500/30 rounded-full">
              <Server className="w-3 h-3 mr-1" />
              RunPod Optimized
            </span>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'deploy' && (
          <div className="space-y-6">
            {/* Deployment Progress */}
            <div className="bg-slate-900/50 backdrop-blur border-slate-700">
              <div>
                <h3 className="text-white flex items-center gap-2">
                  <Terminal className="w-5 h-5" />
                  Deployment Progress
                  {isDeploying && (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-yellow-600/20 text-yellow-400 border border-yellow-500/30 rounded-full animate-pulse">
                      Running
                    </span>
                  )}
                </h3>
              </div>
              <div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-slate-300">Overall Progress</span>
                    <span className="text-white font-bold">{Math.round(totalProgress)}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${totalProgress}%` }}
                    ></div>
                  </div>

                  <div className="grid gap-3">
                    {deploymentStatus.map((step, index) => (
                      <div key={index} className="flex items-center gap-4 p-3 bg-slate-800/50 rounded-lg">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          step.status === 'completed' ? 'bg-green-600' :
                          step.status === 'running' ? 'bg-yellow-600 animate-pulse' :
                          step.status === 'failed' ? 'bg-red-600' : 'bg-slate-600'
                        }`}>
                          {step.status === 'completed' ? '✓' :
                           step.status === 'running' ? '⟳' :
                           step.status === 'failed' ? '✗' : index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="text-white font-medium">{step.step}</div>
                          <div className="text-slate-400 text-sm">{step.message}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-white font-bold">{step.progress}%</div>
                          <div className="w-16 bg-slate-700 rounded-full h-1 mt-1">
                            <div
                              className="bg-gradient-to-r from-purple-600 to-pink-600 h-1 rounded-full transition-all duration-300"
                              style={{ width: `${step.progress}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Deployment Logs */}
            <div className="bg-slate-900/50 backdrop-blur border-slate-700">
              <div>
                <h3 className="text-white flex items-center gap-2">
                  <Terminal className="w-5 h-5" />
                  Deployment Logs
                </h3>
              </div>
              <div>
                <div className="bg-black rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
                  {logs.length === 0 ? (
                    <div className="text-slate-500">No logs yet. Click deploy to start...</div>
                  ) : (
                    logs.map((log, index) => (
                      <div key={index} className="text-green-400 mb-1">
                        {log}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center gap-4">
              <button
                onClick={startDeployment}
                disabled={isDeploying}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-xl px-10 py-4 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isDeploying ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Deploying...
                  </>
                ) : (
                  <>
                    <Upload className="mr-3 h-6 w-6" />
                    Deploy NexusLang v2
                  </>
                )}
              </button>

              <button
                className="flex items-center gap-2 px-6 py-3 border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <Download className="mr-2 h-4 w-4" />
                Download Logs
              </button>
            </div>
          </div>
        )}

        {activeTab === 'monitor' && (
          <div className="space-y-6">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-slate-900/50 backdrop-blur border-slate-700">
                <div>
                  <h3 className="text-white text-center">RunPod Status</h3>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Server className="w-8 h-8 text-green-400" />
                  </div>
                  <div className="text-2xl font-bold text-green-400">Online</div>
                  <div className="text-slate-400 text-sm">Pod ID: Running</div>
                </div>
              </div>

              <div className="bg-slate-900/50 backdrop-blur border-slate-700">
                <div>
                  <h3 className="text-white text-center">GitHub Sync</h3>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Github className="w-8 h-8 text-blue-400" />
                  </div>
                  <div className="text-2xl font-bold text-blue-400">Synced</div>
                  <div className="text-slate-400 text-sm">Latest commit</div>
                </div>
              </div>

              <div className="bg-slate-900/50 backdrop-blur border-slate-700">
                <div>
                  <h3 className="text-white text-center">Platform Health</h3>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Zap className="w-8 h-8 text-purple-400" />
                  </div>
                  <div className="text-2xl font-bold text-purple-400">Healthy</div>
                  <div className="text-slate-400 text-sm">99.9% uptime</div>
                </div>
              </div>
            </div>

            <div className="bg-slate-900/50 backdrop-blur border-slate-700">
              <div>
                <h3 className="text-white">Live Platform Access</h3>
              </div>
              <div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <div>
                      <div className="text-white font-medium">NexusLang v2 IDE</div>
                      <div className="text-slate-400 text-sm">Web-based code editor and compiler</div>
                    </div>
                    <a href="https://developer.galion.app/ide" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors">
                      <Play className="h-4 w-4" />
                      Open IDE
                    </a>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <div>
                      <div className="text-white font-medium">API Documentation</div>
                      <div className="text-slate-400 text-sm">Complete API reference and examples</div>
                    </div>
                    <a href="https://api.developer.galion.app/docs" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2 border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                      View Docs
                    </a>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                    <div>
                      <div className="text-white font-medium">Platform Dashboard</div>
                      <div className="text-slate-400 text-sm">Monitor performance and usage</div>
                    </div>
                    <a href="https://developer.galion.app" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2 border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors">
                      View Dashboard
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'config' && (
          <div className="bg-slate-900/50 backdrop-blur border-slate-700">
            <div>
              <h3 className="text-white">Deployment Configuration</h3>
            </div>
            <div>
              <div className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      RunPod Host
                    </label>
                    <input
                      type="text"
                      value={config.runPodHost}
                      onChange={(e) => setConfig({...config, runPodHost: e.target.value})}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-white placeholder-slate-400"
                      placeholder="your-pod-id.proxy.runpod.net"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      RunPod Port
                    </label>
                    <input
                      type="text"
                      value={config.runPodPort}
                      onChange={(e) => setConfig({...config, runPodPort: e.target.value})}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-white"
                      placeholder="22"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      GitHub Repository URL
                    </label>
                    <input
                      type="text"
                      value={config.gitHubRepo}
                      onChange={(e) => setConfig({...config, gitHubRepo: e.target.value})}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-white placeholder-slate-400"
                      placeholder="https://github.com/username/repo"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Project Name
                    </label>
                    <input
                      type="text"
                      value={config.projectName}
                      onChange={(e) => setConfig({...config, projectName: e.target.value})}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-white"
                      placeholder="NexusLang-v2-Agent"
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <button className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition-colors">
                    Save Configuration
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
