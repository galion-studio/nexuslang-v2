'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Users,
  Search,
  Filter,
  UserPlus,
  MoreHorizontal,
  Shield,
  Crown,
  User,
  Mail,
  Calendar,
  Activity,
  Ban,
  Edit,
  Trash2
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface User {
  id: string
  username: string
  email: string
  fullName: string
  role: 'user' | 'premium' | 'admin'
  status: 'active' | 'inactive' | 'suspended'
  createdAt: Date
  lastLogin: Date
  credits: number
  totalUsage: number
  avatar?: string
}

interface UserStats {
  total: number
  active: number
  premium: number
  admin: number
  suspended: number
}

export default function AdminUsers() {
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterRole, setFilterRole] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [selectedUsers, setSelectedUsers] = useState<string[]>([])

  useEffect(() => {
    loadUsers()
  }, [])

  useEffect(() => {
    filterUsers()
  }, [users, searchTerm, filterRole, filterStatus])

  const loadUsers = async () => {
    try {
      // Mock data - in production, this would fetch from your backend
      const mockUsers: User[] = [
        {
          id: '1',
          username: 'johndoe',
          email: 'john@example.com',
          fullName: 'John Doe',
          role: 'premium',
          status: 'active',
          createdAt: new Date('2024-01-15'),
          lastLogin: new Date('2024-11-13'),
          credits: 2500,
          totalUsage: 1247,
          avatar: '/avatars/john.jpg'
        },
        {
          id: '2',
          username: 'sarahsmith',
          email: 'sarah@example.com',
          fullName: 'Sarah Smith',
          role: 'user',
          status: 'active',
          createdAt: new Date('2024-02-20'),
          lastLogin: new Date('2024-11-12'),
          credits: 500,
          totalUsage: 387
        },
        {
          id: '3',
          username: 'admin',
          email: 'admin@galion.app',
          fullName: 'System Admin',
          role: 'admin',
          status: 'active',
          createdAt: new Date('2023-12-01'),
          lastLogin: new Date('2024-11-13'),
          credits: 99999,
          totalUsage: 0
        }
      ]

      setUsers(mockUsers)

      const userStats: UserStats = {
        total: mockUsers.length,
        active: mockUsers.filter(u => u.status === 'active').length,
        premium: mockUsers.filter(u => u.role === 'premium').length,
        admin: mockUsers.filter(u => u.role === 'admin').length,
        suspended: mockUsers.filter(u => u.status === 'suspended').length
      }

      setStats(userStats)
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterUsers = () => {
    let filtered = users

    if (searchTerm) {
      filtered = filtered.filter(user =>
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.fullName.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (filterRole !== 'all') {
      filtered = filtered.filter(user => user.role === filterRole)
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(user => user.status === filterStatus)
    }

    setFilteredUsers(filtered)
  }

  const handleUserAction = async (action: string, userId: string) => {
    // Mock actions - in production, these would call your backend API
    console.log(`Performing ${action} on user ${userId}`)

    switch (action) {
      case 'suspend':
        setUsers(users.map(u =>
          u.id === userId ? { ...u, status: 'suspended' } : u
        ))
        break
      case 'activate':
        setUsers(users.map(u =>
          u.id === userId ? { ...u, status: 'active' } : u
        ))
        break
      case 'promote':
        setUsers(users.map(u =>
          u.id === userId ? { ...u, role: 'premium' } : u
        ))
        break
      case 'demote':
        setUsers(users.map(u =>
          u.id === userId ? { ...u, role: 'user' } : u
        ))
        break
      case 'delete':
        setUsers(users.filter(u => u.id !== userId))
        break
    }
  }

  const bulkAction = async (action: string) => {
    for (const userId of selectedUsers) {
      await handleUserAction(action, userId)
    }
    setSelectedUsers([])
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return <Crown className="h-4 w-4 text-red-600" />
      case 'premium': return <Shield className="h-4 w-4 text-blue-600" />
      default: return <User className="h-4 w-4 text-gray-600" />
    }
  }

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'admin': return 'destructive'
      case 'premium': return 'default'
      default: return 'secondary'
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'active': return 'default'
      case 'inactive': return 'secondary'
      case 'suspended': return 'destructive'
      default: return 'secondary'
    }
  }

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Users className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-muted-foreground">Loading user management...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
          <p className="text-muted-foreground">
            Manage users, permissions, and account status
          </p>
        </div>
        <Button>
          <UserPlus className="h-4 w-4 mr-2" />
          Add User
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Users</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active</p>
                <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              </div>
              <Activity className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Premium</p>
                <p className="text-2xl font-bold text-blue-600">{stats.premium}</p>
              </div>
              <Shield className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Admins</p>
                <p className="text-2xl font-bold text-red-600">{stats.admin}</p>
              </div>
              <Crown className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Suspended</p>
                <p className="text-2xl font-bold text-orange-600">{stats.suspended}</p>
              </div>
              <Ban className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>User Directory</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search users by name, email, or username..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>

            <div className="flex gap-2">
              <select
                value={filterRole}
                onChange={(e) => setFilterRole(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md bg-white"
              >
                <option value="all">All Roles</option>
                <option value="user">Users</option>
                <option value="premium">Premium</option>
                <option value="admin">Admins</option>
              </select>

              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md bg-white"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
          </div>

          {/* Bulk Actions */}
          {selectedUsers.length > 0 && (
            <div className="flex items-center gap-2 mb-4 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <span className="text-sm font-medium">
                {selectedUsers.length} user{selectedUsers.length !== 1 ? 's' : ''} selected
              </span>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => bulkAction('activate')}>
                  Activate
                </Button>
                <Button size="sm" variant="outline" onClick={() => bulkAction('suspend')}>
                  Suspend
                </Button>
                <Button size="sm" variant="outline" onClick={() => bulkAction('promote')}>
                  Promote
                </Button>
                <Button size="sm" variant="outline" onClick={() => bulkAction('demote')}>
                  Demote
                </Button>
              </div>
            </div>
          )}

          {/* User Table */}
          <div className="space-y-4">
            {filteredUsers.map((user) => (
              <motion.div
                key={user.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-4">
                  <input
                    type="checkbox"
                    checked={selectedUsers.includes(user.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedUsers([...selectedUsers, user.id])
                      } else {
                        setSelectedUsers(selectedUsers.filter(id => id !== user.id))
                      }
                    }}
                    className="w-4 h-4"
                  />

                  <Avatar>
                    <AvatarFallback>
                      {user.fullName.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>

                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium">{user.fullName}</h3>
                      {getRoleIcon(user.role)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        @{user.username}
                      </span>
                      <span className="flex items-center gap-1">
                        <Mail className="h-3 w-3" />
                        {user.email}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-sm font-medium">{user.credits.toLocaleString()} credits</div>
                    <div className="text-xs text-muted-foreground">
                      {user.totalUsage.toLocaleString()} total usage
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge variant={getRoleBadgeVariant(user.role)}>
                      {user.role}
                    </Badge>
                    <Badge variant={getStatusBadgeVariant(user.status)}>
                      {user.status}
                    </Badge>
                  </div>

                  <div className="text-right text-xs text-muted-foreground">
                    <div>Last login: {user.lastLogin.toLocaleDateString()}</div>
                    <div>Joined: {user.createdAt.toLocaleDateString()}</div>
                  </div>

                  <div className="flex items-center gap-1">
                    <Button variant="ghost" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleUserAction(user.status === 'active' ? 'suspend' : 'activate', user.id)}
                    >
                      {user.status === 'active' ? <Ban className="h-4 w-4" /> : <Activity className="h-4 w-4" />}
                    </Button>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </motion.div>
            ))}

            {filteredUsers.length === 0 && (
              <div className="text-center py-12">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No users found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your search or filter criteria.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
