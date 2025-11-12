"use client"

import { DashboardLayout } from '@/components/layout'
import { useRequireAuth } from '@/lib/hooks'

export default function DashboardLayoutWrapper({
  children,
}: {
  children: React.ReactNode
}) {
  // Ensure user is authenticated
  useRequireAuth()

  return <DashboardLayout>{children}</DashboardLayout>
}

