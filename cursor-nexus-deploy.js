#!/usr/bin/env node

/**
 * Cursor NexusLang v2 Deployment Launcher
 *
 * Launches the NexusLang v2 coding agent deployment interface
 * Can be integrated into Cursor workflows and new chat initialization
 */

const { exec } = require('child_process')
const path = require('path')
const fs = require('fs')

console.log('🚀 NexusLang v2 Coding Agent Deployment Launcher')
console.log('===============================================')
console.log('')

// Check if we're in the project directory
const projectRoot = path.join(__dirname, 'galion-studio')

if (!fs.existsSync(projectRoot)) {
  console.error('❌ Error: galion-studio directory not found')
  console.error('Please run this script from the project-nexus root directory')
  process.exit(1)
}

// Check if Node.js and npm are available
exec('node --version', (error, stdout) => {
  if (error) {
    console.error('❌ Error: Node.js not found')
    console.error('Please install Node.js to run the deployment interface')
    process.exit(1)
  }

  console.log('✅ Node.js found:', stdout.trim())

  // Check if npm is available
  exec('npm --version', (error, stdout) => {
    if (error) {
      console.error('❌ Error: npm not found')
      console.error('Please install npm to run the deployment interface')
      process.exit(1)
    }

    console.log('✅ npm found:', stdout.trim())

    // Change to galion-studio directory
    process.chdir(projectRoot)

    console.log('')
    console.log('📁 Changed to galion-studio directory')
    console.log('🌐 Starting NexusLang v2 Coding Agent...')

    // Check if dependencies are installed
    if (!fs.existsSync('node_modules')) {
      console.log('')
      console.log('📦 Installing dependencies...')
      console.log('This may take a few minutes...')

      exec('npm install', (error, stdout, stderr) => {
        if (error) {
          console.error('❌ Error installing dependencies:', error.message)
          process.exit(1)
        }

        console.log('✅ Dependencies installed')
        startDeploymentInterface()
      })
    } else {
      console.log('✅ Dependencies already installed')
      startDeploymentInterface()
    }
  })
})

function startDeploymentInterface() {
  console.log('')
  console.log('🚀 Starting deployment interface...')
  console.log('📱 Opening NexusLang v2 Coding Agent at: http://localhost:3001/nexuslang-agent')
  console.log('')
  console.log('Features available:')
  console.log('  • Enhanced deployment with progress bars')
  console.log('  • GitHub integration')
  console.log('  • RunPod deployment automation')
  console.log('  • Real-time monitoring')
  console.log('  • Live platform access')
  console.log('')
  console.log('Press Ctrl+C to stop the server')
  console.log('')

  // Start the development server
  const server = exec('npm run dev', (error, stdout, stderr) => {
    if (error) {
      console.error('❌ Error starting server:', error.message)
      process.exit(1)
    }
  })

  // Pipe output to console
  server.stdout.pipe(process.stdout)
  server.stderr.pipe(process.stderr)

  // Handle process termination
  process.on('SIGINT', () => {
    console.log('')
    console.log('🛑 Shutting down NexusLang v2 Coding Agent...')
    server.kill('SIGINT')
    process.exit(0)
  })

  // Open browser after a short delay
  setTimeout(() => {
    const open = require('open') || null
    if (open) {
      open('http://localhost:3001/nexuslang-agent')
    } else {
      console.log('💡 Please open http://localhost:3001/nexuslang-agent in your browser')
    }
  }, 3000)
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught exception:', error.message)
  process.exit(1)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled rejection:', reason)
  process.exit(1)
})
