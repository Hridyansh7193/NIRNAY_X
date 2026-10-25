import React, { useState } from 'react'
import {
  FileText,
  UploadCloud,
  Trash2,
  Filter,
  Search,
  ExternalLink,
  Layers,
  Calendar,
  UserCheck,
  BookmarkCheck,
  AlertCircle,
  FileCheck2,
} from 'lucide-react'

export default function DocumentPanel({ documents, onRefresh, onUpload, onSelectDoc }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('ALL')
  const [viewingDoc, setViewingDoc] = useState(null)
  const [deletingId, setDeletingId] = useState(null)

  const categories = ['ALL', ...new Set(documents.map((d) => d.category || d.doc_type || 'General').filter(Boolean))]

  const filteredDocs = documents.filter((doc) => {
    const docCat = doc.category || doc.doc_type || 'General'
    const matchesSearch =
      doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      docCat.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCat = selectedCategory === 'ALL' || docCat === selectedCategory
    return matchesSearch && matchesCat
  })

  const handleDelete = async (docId, e) => {
    e.stopPropagation()
    if (!confirm('Are you sure you want to delete this document and all its indexed vector embeddings?')) {
      return
    }

    setDeletingId(docId)
    try {
      const res = await fetch(`http://localhost:8000/api/documents/${docId}`, {
        method: 'DELETE',
      })
      if (res.ok) {
        onRefresh()
      } else {
        alert('Failed to delete document')
      }
    } catch (err) {
      console.error(err)
      alert('Network error deleting document')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="document-panel">
      {/* Top action header */}
      <div className="doc-panel-header">
        <div className="doc-panel-title-area">
          <h2>Case Materials & Corpus Repository</h2>
          <p>
            Manage indexed legal documents, review automated OCR parsing, chunk extractions, and statutory tagging.
          </p>
        </div>
        <button type="button" className="btn-primary" onClick={onUpload}>
          <UploadCloud size={16} />
          <span>Upload Document (PDF)</span>
        </button>
      </div>

      {/* Controls Bar: Search & Category filter */}
      <div className="doc-controls-bar">
        <div className="doc-search-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search by case title, FIR number, or category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="category-pills-row">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              className={`cat-pill ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Documents Grid / Table */}
      {filteredDocs.length === 0 ? (
        <div className="doc-empty-state">
          <FileCheck2 size={48} className="empty-state-icon" />
          <h3>No Legal Documents Found</h3>
          <p>Upload a judgment, FIR, petition, or statutory code to index it into the NirnayX vector store.</p>
          <button type="button" className="btn-primary" onClick={onUpload} style={{ marginTop: '1rem' }}>
            <UploadCloud size={16} /> Ingest Your First Document
          </button>
        </div>
      ) : (
        <div className="docs-card-grid">
          {filteredDocs.map((doc) => {
            const docKey = doc.doc_id || doc.id
            const docCategory = doc.category || doc.doc_type || 'Legal Document'
            const sections = doc.sections_cited || doc.metadata?.sections || []
            return (
              <div key={docKey} className="doc-card" onClick={() => setViewingDoc(doc)}>
                <div className="doc-card-top">
                  <div className="doc-type-icon">
                    <FileText size={20} />
                  </div>
                  <div className="doc-card-header-info">
                    <h4 className="doc-title" title={doc.filename}>
                      {doc.filename}
                    </h4>
                    <span className="doc-cat-tag">{docCategory}</span>
                  </div>
                </div>

                <div className="doc-metrics-row">
                  <div className="doc-metric">
                    <Layers size={13} />
                    <span>{doc.chunks_count || 0} Chunks</span>
                  </div>
                  <div className="doc-metric">
                    <Calendar size={13} />
                    <span>{doc.created_at || doc.extracted_at ? new Date(doc.created_at || doc.extracted_at).toLocaleDateString() : 'Active'}</span>
                  </div>
                </div>

                {/* Detected Statutory sections pill */}
                {sections.length > 0 && (
                  <div className="extracted-sections-preview">
                    <span className="sections-label">Sections:</span>
                    <div className="sections-tag-list">
                      {sections.slice(0, 3).map((sec, i) => (
                        <span key={i} className="section-pill">
                          {sec}
                        </span>
                      ))}
                      {sections.length > 3 && (
                        <span className="section-pill more">+{sections.length - 3}</span>
                      )}
                    </div>
                  </div>
                )}

                <div className="doc-card-actions">
                  <button
                    type="button"
                    className="btn-outline-sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onSelectDoc(docKey)
                    }}
                    title="Query this document specifically in RAG assistant"
                  >
                    <Filter size={13} /> Query This
                  </button>
                  <button
                    type="button"
                    className="btn-danger-sm"
                    disabled={deletingId === docKey}
                    onClick={(e) => handleDelete(docKey, e)}
                    title="Delete document and remove embeddings"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Document Detail Inspection Modal */}
      {viewingDoc && (
        <div className="modal-backdrop" onClick={() => setViewingDoc(null)}>
          <div className="modal-content doc-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-group">
                <FileText size={22} className="modal-icon" />
                <div>
                  <h3>{viewingDoc.filename}</h3>
                  <span className="modal-subtitle">Document ID: {viewingDoc.doc_id || viewingDoc.id}</span>
                </div>
              </div>
              <button type="button" className="modal-close-btn" onClick={() => setViewingDoc(null)}>
                ×
              </button>
            </div>

            <div className="modal-body doc-inspect-body">
              <div className="inspect-section">
                <h4>Document Metadata</h4>
                <div className="metadata-table">
                  <div className="meta-row">
                    <span className="meta-key">Category:</span>
                    <span className="meta-val">{viewingDoc.category || viewingDoc.doc_type || 'General Legal Document'}</span>
                  </div>
                  <div className="meta-row">
                    <span className="meta-key">Total Chunks:</span>
                    <span className="meta-val">{viewingDoc.chunks_count || 'N/A'}</span>
                  </div>
                  <div className="meta-row">
                    <span className="meta-key">Ingestion Date:</span>
                    <span className="meta-val">{viewingDoc.created_at || viewingDoc.extracted_at || 'Just now'}</span>
                  </div>
                </div>
              </div>

              {(viewingDoc.sections_cited || viewingDoc.dates || viewingDoc.parties || viewingDoc.metadata) && (
                <div className="inspect-section">
                  <h4>Automated Legal Entity Extraction</h4>
                  <div className="entities-block">
                    {(viewingDoc.sections_cited || viewingDoc.metadata?.sections) && (
                      <div className="entity-group">
                        <strong>Statutory Sections:</strong>
                        <div className="tag-cloud">
                          {(viewingDoc.sections_cited || viewingDoc.metadata?.sections || []).map((s, i) => (
                            <span key={i} className="statute-tag">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {(viewingDoc.dates || viewingDoc.metadata?.dates) && (
                      <div className="entity-group">
                        <strong>Identified Dates:</strong>
                        <div className="tag-cloud">
                          {(viewingDoc.dates || viewingDoc.metadata?.dates || []).map((d, i) => (
                            <span key={i} className="date-tag">
                              {d}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {(viewingDoc.parties || viewingDoc.metadata?.parties) && (
                      <div className="entity-group">
                        <strong>Identified Parties:</strong>
                        <div className="tag-cloud">
                          {(viewingDoc.parties || viewingDoc.metadata?.parties || []).map((p, i) => (
                            <span key={i} className="party-tag">
                              {p}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn-primary"
                onClick={() => {
                  onSelectDoc(viewingDoc.doc_id || viewingDoc.id)
                  setViewingDoc(null)
                }}
              >
                Set As Active RAG Filter
              </button>
              <button type="button" className="btn-secondary" onClick={() => setViewingDoc(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
