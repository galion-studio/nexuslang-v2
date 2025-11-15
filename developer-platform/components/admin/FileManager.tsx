'use client'

import { useState } from 'react'
import { File, Folder, FolderOpen, FileText, Code, Image, Settings, Plus, Search, MoreVertical } from 'lucide-react'

interface FileNode {
  name: string
  type: 'file' | 'folder'
  extension?: string
  children?: FileNode[]
  size?: number
  modified?: Date
}

const mockFileTree: FileNode[] = [
  {
    name: 'src',
    type: 'folder',
    children: [
      { name: 'main.nx', type: 'file', extension: 'nx', size: 2048, modified: new Date() },
      { name: 'utils.nx', type: 'file', extension: 'nx', size: 1536, modified: new Date() },
      { name: 'components', type: 'folder', children: [
        { name: 'Button.nx', type: 'file', extension: 'nx', size: 512, modified: new Date() },
        { name: 'Modal.nx', type: 'file', extension: 'nx', size: 1024, modified: new Date() }
      ]}
    ]
  },
  {
    name: 'tests',
    type: 'folder',
    children: [
      { name: 'main.test.nx', type: 'file', extension: 'nx', size: 768, modified: new Date() },
      { name: 'utils.test.nx', type: 'file', extension: 'nx', size: 512, modified: new Date() }
    ]
  },
  {
    name: 'docs',
    type: 'folder',
    children: [
      { name: 'README.md', type: 'file', extension: 'md', size: 4096, modified: new Date() },
      { name: 'API.md', type: 'file', extension: 'md', size: 2048, modified: new Date() }
    ]
  },
  { name: 'package.json', type: 'file', extension: 'json', size: 1024, modified: new Date() },
  { name: 'galion.config.js', type: 'file', extension: 'js', size: 512, modified: new Date() }
]

interface FileManagerProps {
  onFileSelect?: (filePath: string) => void
  currentFile?: string | null
  className?: string
}

export function FileManager({ onFileSelect, currentFile, className = '' }: FileManagerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['src']))
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  const toggleFolder = (folderPath: string) => {
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(folderPath)) {
      newExpanded.delete(folderPath)
    } else {
      newExpanded.add(folderPath)
    }
    setExpandedFolders(newExpanded)
  }

  const getFileIcon = (extension?: string) => {
    switch (extension) {
      case 'nx':
        return <Code className="w-4 h-4 text-blue-500" />
      case 'md':
        return <FileText className="w-4 h-4 text-gray-500" />
      case 'json':
        return <Settings className="w-4 h-4 text-yellow-500" />
      case 'js':
        return <Code className="w-4 h-4 text-yellow-600" />
      default:
        return <File className="w-4 h-4 text-gray-400" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const handleFileClick = (filePath: string, node: FileNode) => {
    if (node.type === 'folder') {
      toggleFolder(filePath)
    } else {
      setSelectedFile(filePath)
      onFileSelect?.(filePath)
    }
  }

  const renderFileTree = (nodes: FileNode[], currentPath = '', level = 0): JSX.Element[] => {
    return nodes.flatMap((node) => {
      const fullPath = currentPath ? `${currentPath}/${node.name}` : node.name
      const isExpanded = expandedFolders.has(fullPath)
      const isSelected = selectedFile === fullPath || currentFile === fullPath

      // Filter by search query
      if (searchQuery && !node.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return []
      }

      const elements = [
        <div key={fullPath}>
          <button
            onClick={() => handleFileClick(fullPath, node)}
            className={`w-full text-left px-2 py-1 text-sm hover:bg-surface-hover transition-colors flex items-center space-x-2 ${
              isSelected ? 'bg-primary/10 text-primary' : 'text-foreground'
            }`}
            style={{ paddingLeft: `${8 + level * 12}px` }}
          >
            {node.type === 'folder' ? (
              isExpanded ? (
                <FolderOpen className="w-4 h-4 text-blue-500 flex-shrink-0" />
              ) : (
                <Folder className="w-4 h-4 text-blue-500 flex-shrink-0" />
              )
            ) : (
              <div className="flex-shrink-0">
                {getFileIcon(node.extension)}
              </div>
            )}
            <span className="truncate flex-1">{node.name}</span>
            {node.type === 'file' && node.size && (
              <span className="text-xs text-foreground-muted flex-shrink-0">
                {formatFileSize(node.size)}
              </span>
            )}
            <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-surface-active rounded">
              <MoreVertical className="w-3 h-3" />
            </button>
          </button>
        </div>
      ]

      // Render children if expanded
      if (node.type === 'folder' && isExpanded && node.children) {
        elements.push(...renderFileTree(node.children, fullPath, level + 1))
      }

      return elements
    })
  }

  return (
    <div className={`text-sm ${className}`}>
      {/* Search Bar */}
      <div className="p-3 border-b border-border">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-foreground-muted" />
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      {/* File Tree */}
      <div className="overflow-y-auto max-h-[400px]">
        {renderFileTree(mockFileTree)}
      </div>

      {/* Actions */}
      <div className="p-3 border-t border-border space-y-2">
        <button className="w-full flex items-center space-x-2 px-3 py-2 text-sm bg-surface-hover hover:bg-surface-active rounded-md transition-colors">
          <Plus className="w-4 h-4" />
          <span>New File</span>
        </button>
        <button className="w-full flex items-center space-x-2 px-3 py-2 text-sm bg-surface-hover hover:bg-surface-active rounded-md transition-colors">
          <Folder className="w-4 h-4" />
          <span>New Folder</span>
        </button>
      </div>
    </div>
  )
}

export default FileManager
