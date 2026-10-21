/*
 * NirnayX — AI-Powered Legal Intelligence Platform
 * Main Application Component
 */

import { useState, useCallback } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'
import DocumentPanel from './components/DocumentPanel'
import SearchPanel from './components/SearchPanel'
import StatsPanel from './components/StatsPanel'
import UploadModal from './components/UploadModal'
import './App.css'

function App() {
  const [activeView, setActiveView] = useState('chat')
  const [persona, setPersona] = useState('citizen')
  const [documents, setDocuments] = useState([])
  const [selectedDocId, setSelectedDocId] = useState(null)
  const [showUpload, setShowUpload] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const refreshDocuments = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8000/api/documents')
      const data = await res.json()
      if (data.status === 'ok') {
        setDocuments(data.documents || [])
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    }
  }, [])

  const handleUploadComplete = useCallback((newDoc) => {
    setShowUpload(false)
    refreshDocuments()
  }, [refreshDocuments])

  const renderActiveView = () => {
    switch (activeView) {
      case 'chat':
        return (
          <ChatPanel
            persona={persona}
            selectedDocId={selectedDocId}
            onPersonaChange={setPersona}
          />
        )
      case 'documents':
        return (
          <DocumentPanel
            documents={documents}
            onRefresh={refreshDocuments}
            onUpload={() => setShowUpload(true)}
            onSelectDoc={setSelectedDocId}
          />
        )
      case 'search':
        return <SearchPanel selectedDocId={selectedDocId} />
      case 'stats':
        return <StatsPanel />
      default:
        return <ChatPanel persona={persona} selectedDocId={selectedDocId} onPersonaChange={setPersona} />
    }
  }

  return (
    <div className="app">
      <Header
        persona={persona}
        onPersonaChange={setPersona}
        onUpload={() => setShowUpload(true)}
      />
      <div className="app-body">
        <Sidebar
          activeView={activeView}
          onViewChange={setActiveView}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          documents={documents}
          selectedDocId={selectedDocId}
          onSelectDoc={(id) => {
            setSelectedDocId(id)
            setActiveView('chat')
          }}
          onRefreshDocs={refreshDocuments}
        />
        <main className={`main-content ${sidebarCollapsed ? 'expanded' : ''}`}>
          {renderActiveView()}
        </main>
      </div>

      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUploadComplete={handleUploadComplete}
        />
      )}
    </div>
  )
}

export default App
