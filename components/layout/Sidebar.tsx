'use client'

import { useState } from 'react'
import { useUser } from '@clerk/nextjs'
import { 
  MessageSquare, 
  FileText, 
  Search, 
  FileEdit, 
  Settings,
  Plus,
  Trash2,
  User
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useChatStore } from '@/hooks/useChatStore'

interface SidebarProps {
  onItemClick?: () => void
}

export function Sidebar({ onItemClick }: SidebarProps) {
  const { user } = useUser()
  const { sessions, currentSession, createSession, deleteSession, setCurrentSession } = useChatStore()
  const [activeTab, setActiveTab] = useState('chat')

  const tabs = [
    { id: 'chat', label: 'AI Chat Assistant', icon: MessageSquare, href: '/' },
    { id: 'documents', label: 'Document Management', icon: FileText, href: '/documents' },
    { id: 'search', label: 'Legal Law Search', icon: Search, href: '/search' },
    { id: 'templates', label: 'Legal Template Builder', icon: FileEdit, href: '/templates' },
  ]

  const handleNewChat = () => {
    createSession(`Chat ${sessions.length + 1}`)
    onItemClick?.()
  }

  const handleDeleteSession = (sessionId: string) => {
    deleteSession(sessionId)
  }

  const handleSessionClick = (sessionId: string) => {
    setCurrentSession(sessionId)
    onItemClick?.()
  }

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId)
    onItemClick?.()
  }

  return (
    <div className="w-64 h-full bg-[#181818] border-r border-border flex flex-col">
      {/* User Info */}
      <div className="p-4 border-b border-border flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
            <User className="w-4 h-4 text-primary-foreground" />
          </div>
          <div>
            <div className="text-sm font-medium">{user?.fullName}</div>
            <div className="text-xs text-muted-foreground">{user?.emailAddresses[0]?.emailAddress}</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="p-4 flex-shrink-0">
        <nav className="space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <a
                key={tab.id}
                href={tab.href}
                onClick={() => handleTabClick(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </a>
            )
          })}
        </nav>
      </div>

      {/* Chat Sessions (only show for chat tab) */}
      {activeTab === 'chat' && (
        <div className="flex-1 p-4 space-y-4 overflow-y-auto">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Chat Sessions</h3>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleNewChat}
              className="h-6 w-6"
            >
              <Plus className="h-3 w-3" />
            </Button>
          </div>
          
          <div className="space-y-1">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`flex items-center justify-between p-2 rounded-md text-sm cursor-pointer transition-colors group ${
                  currentSession?.id === session.id
                    ? 'bg-accent text-accent-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                <button
                  onClick={() => handleSessionClick(session.id)}
                  className="flex-1 text-left truncate"
                >
                  {session.title}
                </button>
                {currentSession?.id === session.id && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteSession(session.id)}
                    className="h-4 w-4 opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="p-4 border-t border-border flex-shrink-0">
        <div className="text-center">
          <p className="text-xs text-muted-foreground mb-1">Beta Release</p>
          <p className="text-xs text-muted-foreground">
            © Techxos Digital Solutions 2025
          </p>
          <a
            href="https://www.techxos.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-primary hover:underline"
          >
            www.techxos.com
          </a>
        </div>
      </div>
    </div>
  )
}
