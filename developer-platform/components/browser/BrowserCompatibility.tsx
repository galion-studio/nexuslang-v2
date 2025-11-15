'use client'

import { useEffect, useState } from 'react'
import { AlertTriangle, X, Chrome, Firefox, Safari, Edge } from 'lucide-react'

interface BrowserInfo {
  name: string
  version: string
  isSupported: boolean
  isMobile: boolean
  userAgent: string
}

const BrowserCompatibility: React.FC = () => {
  const [browserInfo, setBrowserInfo] = useState<BrowserInfo | null>(null)
  const [showWarning, setShowWarning] = useState(false)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    const detectBrowser = () => {
      const ua = navigator.userAgent
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)

      let browserName = 'Unknown'
      let version = 'Unknown'
      let isSupported = true

      // Chrome detection
      if (ua.includes('Chrome') && !ua.includes('Edg')) {
        browserName = 'Chrome'
        const match = ua.match(/Chrome\/(\d+)/)
        version = match ? match[1] : 'Unknown'
        isSupported = parseInt(version) >= 80
      }
      // Edge detection
      else if (ua.includes('Edg')) {
        browserName = 'Edge'
        const match = ua.match(/Edg\/(\d+)/)
        version = match ? match[1] : 'Unknown'
        isSupported = parseInt(version) >= 80
      }
      // Firefox detection
      else if (ua.includes('Firefox')) {
        browserName = 'Firefox'
        const match = ua.match(/Firefox\/(\d+)/)
        version = match ? match[1] : 'Unknown'
        isSupported = parseInt(version) >= 78
      }
      // Safari detection
      else if (ua.includes('Safari') && !ua.includes('Chrome')) {
        browserName = 'Safari'
        const match = ua.match(/Version\/(\d+)/)
        version = match ? match[1] : 'Unknown'
        isSupported = parseInt(version) >= 14
      }
      // Internet Explorer detection
      else if (ua.includes('MSIE') || ua.includes('Trident')) {
        browserName = 'Internet Explorer'
        version = 'Legacy'
        isSupported = false
      }
      // Older browsers
      else if (ua.includes('Opera')) {
        browserName = 'Opera'
        const match = ua.match(/Opera\/(\d+)/) || ua.match(/OPR\/(\d+)/)
        version = match ? match[1] : 'Unknown'
        isSupported = parseInt(version) >= 60
      }

      const info: BrowserInfo = {
        name: browserName,
        version,
        isSupported,
        isMobile,
        userAgent: ua
      }

      setBrowserInfo(info)
      setShowWarning(!isSupported && !dismissed)
    }

    detectBrowser()
  }, [dismissed])

  const getBrowserIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case 'chrome': return <Chrome className="h-5 w-5" />
      case 'firefox': return <Firefox className="h-5 w-5" />
      case 'safari': return <Safari className="h-5 w-5" />
      case 'edge': return <Edge className="h-5 w-5" />
      default: return <AlertTriangle className="h-5 w-5" />
    }
  }

  const getRecommendedBrowsers = () => [
    { name: 'Chrome', version: '80+', url: 'https://chrome.google.com', icon: <Chrome className="h-4 w-4" /> },
    { name: 'Firefox', version: '78+', url: 'https://firefox.com', icon: <Firefox className="h-4 w-4" /> },
    { name: 'Safari', version: '14+', url: 'https://apple.com/safari', icon: <Safari className="h-4 w-4" /> },
    { name: 'Edge', version: '80+', url: 'https://microsoft.com/edge', icon: <Edge className="h-4 w-4" /> }
  ]

  if (!showWarning || !browserInfo) return null

  return (
    <div className="fixed top-4 left-4 right-4 z-50 max-w-2xl mx-auto">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 shadow-lg">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-yellow-800 mb-1">
              Browser Compatibility Warning
            </h3>
            <p className="text-sm text-yellow-700 mb-3">
              You're using {browserInfo.name} {browserInfo.version}, which may not fully support all features of Galion.app.
              For the best experience, please use one of the following supported browsers:
            </p>

            <div className="grid grid-cols-2 gap-2 mb-3">
              {getRecommendedBrowsers().map((browser) => (
                <a
                  key={browser.name}
                  href={browser.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-xs text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded transition-colors"
                >
                  {browser.icon}
                  <span>{browser.name} {browser.version}</span>
                </a>
              ))}
            </div>

            <p className="text-xs text-yellow-600">
              Some features may work with limited functionality in your current browser.
            </p>
          </div>

          <button
            onClick={() => setDismissed(true)}
            className="text-yellow-600 hover:text-yellow-800 transition-colors"
            aria-label="Dismiss warning"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default BrowserCompatibility
