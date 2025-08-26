'use client'

import { useUser } from '@clerk/nextjs'
import { redirect } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Menu, X } from 'lucide-react'
import { ChatInterface } from '@/components/chat/ChatInterface'
import { Sidebar } from '@/components/layout/Sidebar'
import { CountrySelector } from '@/components/ui/CountrySelector'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Button } from '@/components/ui/Button'
import { useChatStore } from '@/hooks/useChatStore'

export default function HomePage() {
  const { user, isLoaded } = useUser()
  const { initializeChat } = useChatStore()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (user) {
      initializeChat(user.id)
    }
  }, [user, initializeChat])

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)
  const closeSidebar = () => setSidebarOpen(false)

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    redirect('/sign-in')
  }

  return (
    <div className="flex h-screen bg-[#212121] overflow-hidden">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-card border-r border-border flex flex-col transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <Sidebar onItemClick={closeSidebar} />
      </div>

      {/* Main content */}
      <main className="flex-1 flex flex-col lg:ml-0 min-h-0">
        <header className="flex items-center sticky top-0 z-30 justify-between p-4 border-b bg-[#212121] border-border">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleSidebar}
              className="lg:hidden"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <h1 className="text-xl lg:text-2xl font-bold text-foreground">
              JuristAI - Nigerian Legal Assistant
            </h1>
          </div>
          <CountrySelector />
        </header>
        <div className="flex-1 min-h-0">
          <ChatInterface />
        </div>
      </main>
    </div>
  )
}

