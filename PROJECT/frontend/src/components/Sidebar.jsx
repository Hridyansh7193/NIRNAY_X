import React, { useEffect } from 'react'
import {
  MessageSquareText,
  FileText,
  Search,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  FolderOpen,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  FileBox,
} from 'lucide-react'

export default function Sidebar({
  activeView,
  onViewChange,
  collapsed,
  onToggle,
  documents,
  selectedDocId,
  onSelectDoc,
  onRefreshDocs,
}) {
  useEffect(() => {
    onRefreshDocs()
  }, [onRefreshDocs])

  const navItems = [
    { id: 'chat', label: 'RAG Legal Assistant', icon: MessageSquareText },
    { id: 'documents', label: 'Case Materials & OCR', icon: FileText, badge: documents.length },
    { id: 'search', label: 'Semantic Provision Search', icon: Search },
    { id: 'stats', label: 'System Analytics & SDG', icon: BarChart3 },
  ]

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {!collapsed && <span className="sidebar-title">MODULES</span>}
        <button
          type="button"
          className="sidebar-toggle-btn"
          onClick={onToggle}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeView === item.id
          return (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onViewChange(item.id)}
              title={item.label}
            >
              <Icon size={18} className="nav-icon" />
              {!collapsed && (
                <div className="nav-label-group">
                  <span className="nav-label">{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="nav-badge">{item.badge}</span>
                  )}
                </div>
              )}
            </button>
          )
        })}
      </nav>

      {!collapsed && (
        <div className="sidebar-docs-section">
          <div className="sidebar-docs-header">
            <span className="docs-header-title">
              <FolderOpen size={14} /> ACTIVE CORPORA
            </span>
            <button
              type="button"
              className="refresh-btn"
              onClick={onRefreshDocs}
              title="Refresh document list"
            >
              <RefreshCw size={13} />
            </button>
          </div>

          <div className="doc-filter-indicator">
            {selectedDocId ? (
              <div className="filtered-doc-chip">
                <span>Filtered: </span>
                <strong>{documents.find((d) => d.id === selectedDocId)?.filename || 'Document'}</strong>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    onSelectDoc(null)
                  }}
                  title="Clear document filter (search all corpora)"
                >
                  ×
                </button>
              </div>
            ) : (
              <span className="all-docs-indicator">Grounding: All Corpus ({documents.length} files)</span>
            )}
          </div>

          <div className="sidebar-doc-list">
            {documents.length === 0 ? (
              <div className="sidebar-empty-docs">
                <FileBox size={22} className="empty-icon" />
                <p>No documents ingested yet.</p>
                <small>Upload an FIR, Judgment or Petition</small>
              </div>
            ) : (
              documents.map((doc) => {
                const isSelected = selectedDocId === doc.id
                return (
                  <div
                    key={doc.id}
                    className={`sidebar-doc-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => onSelectDoc(isSelected ? null : doc.id)}
                    title={`Click to ${isSelected ? 'unfilter' : 'filter queries to this document'}`}
                  >
                    <div className="doc-item-title-row">
                      <FileText size={14} className="doc-mini-icon" />
                      <span className="doc-item-name">{doc.filename}</span>
                    </div>
                    <div className="doc-item-meta">
                      <span>{doc.chunks_count || 0} chunks</span>
                      {doc.category && <span className="category-pill">{doc.category}</span>}
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      )}

      <div className="sidebar-footer">
        {!collapsed ? (
          <div className="system-status-indicator">
            <span className="status-dot online"></span>
            <span className="status-text">RAG Pipeline Ready</span>
          </div>
        ) : (
          <div className="system-status-indicator" title="RAG Pipeline Ready">
            <span className="status-dot online"></span>
          </div>
        )}
      </div>
    </aside>
  )
}
