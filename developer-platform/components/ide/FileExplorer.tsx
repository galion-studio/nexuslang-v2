'use client'

import { useState } from 'react'
import { File, Folder, FolderOpen, FileText, Code, Image, Settings } from 'lucide-react'

interface FileItem {
  name: string
  type: 'file' | 'folder'
  extension?: string
  children?: FileItem[]
}

const mockFiles: FileItem[] = [
  {
    name: 'src',
    type: 'folder',
    children: [
      { name: 'main.nx', type: 'file', extension: 'nx' },
      { name: 'utils.nx', type: 'file', extension: 'nx' },
      { name: 'types.nx', type: 'file', extension: 'nx' }
    ]
  },
  {
    name: 'tests',
    type: 'folder',
    children: [
      { name: 'main.test.nx', type: 'file', extension: 'nx' },
      { name: 'utils.test.nx', type: 'file', extension: 'nx' }
    ]
  },
  {
    name: 'docs',
    type: 'folder',
    children: [
      { name: 'README.md', type: 'file', extension: 'md' },
      { name: 'API.md', type: 'file', extension: 'md' }
    ]
  },
  { name: 'package.json', type: 'file', extension: 'json' },
  { name: 'galion.config.js', type: 'file', extension: 'js' }
]

interface FileExplorerProps {
  onFileSelect?: (fileName: string) => void
  currentFile?: string
  className?: string
}

export function FileExplorer({ onFileSelect, currentFile, className = '' }: FileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['src', 'tests']))

  const toggleFolder = (folderName: string) => {
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(folderName)) {
      newExpanded.delete(folderName)
    } else {
      newExpanded.add(folderName)
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

  const renderFileTree = (items: FileItem[], level = 0) => {
    return items.map((item) => {
      const isExpanded = expandedFolders.has(item.name)
      const isSelected = currentFile === item.name

      return (
        <div key={item.name}>
          <button
            onClick={() => {
              if (item.type === 'folder') {
                toggleFolder(item.name)
              } else {
                onFileSelect?.(item.name)
              }
            }}
            className={`w-full text-left px-3 py-1.5 text-sm hover:bg-surface-hover transition-colors flex items-center space-x-2 ${
              isSelected ? 'bg-primary/10 text-primary' : 'text-foreground'
            }`}
            style={{ paddingLeft: `${12 + level * 16}px` }}
          >
            {item.type === 'folder' ? (
              isExpanded ? (
                <FolderOpen className="w-4 h-4 text-blue-500" />
              ) : (
                <Folder className="w-4 h-4 text-blue-500" />
              )
            ) : (
              getFileIcon(item.extension)
            )}
            <span className="truncate">{item.name}</span>
          </button>

          {item.type === 'folder' && isExpanded && item.children && (
            <div>
              {renderFileTree(item.children, level + 1)}
            </div>
          )}
        </div>
      )
    })
  }

  return (
    <div className={`text-sm ${className}`}>
      {renderFileTree(mockFiles)}
    </div>
  )
}

export default FileExplorer