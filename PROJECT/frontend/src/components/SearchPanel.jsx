import React, { useState } from 'react'
import {
  Search,
  Filter,
  SlidersHorizontal,
  Bookmark,
  FileText,
  ExternalLink,
  ChevronDown,
  Sparkles,
  Info,
} from 'lucide-react'

export default function SearchPanel({ selectedDocId }) {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(6)
  const [roleFilter, setRoleFilter] = useState('ALL')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [error, setError] = useState(null)

  const roles = [
    { id: 'ALL', label: 'All Rhetorical Roles' },
    { id: 'statute', label: 'Statute / Provisions' },
    { id: 'ruling', label: 'Judicial Rulings' },
    { id: 'facts', label: 'Case Facts & Allegations' },
    { id: 'argument', label: 'Counsel Arguments' },
    { id: 'procedure', label: 'Procedural Orders' },
  ]

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!query.trim() || loading) return

    setLoading(true)
    setError(null)
    setSearched(true)

    try {
      const payload = {
        query: query.trim(),
        top_k: Number(topK),
        doc_id: selectedDocId || null,
        role_filter: roleFilter === 'ALL' ? null : roleFilter,
      }

      const res = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()
      if (res.ok && data.status === 'ok') {
        setResults(data.results || [])
      } else {
        setError(data.detail || 'Search failed on backend')
      }
    } catch (err) {
      setError('Could not connect to backend server at http://localhost:8000')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="search-panel">
      {/* Top Banner */}
      <div className="search-panel-header">
        <div>
          <h2>Semantic Provision & Precedent Search</h2>
          <p>
            Concept-driven dense vector retrieval across statutory corpora without generative hallucination.
          </p>
        </div>
      </div>

      {/* Query Bar & Filters */}
      <div className="search-form-card">
        <form onSubmit={handleSearch} className="search-input-group">
          <div className="search-bar-inner">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="e.g., Anticipatory bail requirements under Section 438 CrPC / 482 BNSS..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button
              type="submit"
              className="btn-primary search-submit-btn"
              disabled={!query.trim() || loading}
            >
              {loading ? 'Searching...' : 'Search Corpora'}
            </button>
          </div>

          <div className="search-filters-row">
            <div className="filter-item">
              <SlidersHorizontal size={14} />
              <label>Top-K Retrieval:</label>
              <select value={topK} onChange={(e) => setTopK(e.target.value)}>
                <option value={3}>3 chunks</option>
                <option value={6}>6 chunks</option>
                <option value={10}>10 chunks</option>
                <option value={15}>15 chunks</option>
              </select>
            </div>

            <div className="filter-item">
              <Filter size={14} />
              <label>Rhetorical Role:</label>
              <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>

            {selectedDocId && (
              <div className="active-doc-badge">
                <span>Filtering to active document ID: {selectedDocId.slice(0, 8)}...</span>
              </div>
            )}
          </div>
        </form>
      </div>

      {/* Search Results Area */}
      <div className="search-results-section">
        {error && (
          <div className="search-error-alert">
            <Info size={16} /> <span>{error}</span>
          </div>
        )}

        {searched && !loading && results.length === 0 && !error && (
          <div className="search-empty-state">
            <Bookmark size={40} className="empty-icon" />
            <h4>No semantic matches found</h4>
            <p>Try rephrasing your search query or uploading additional case materials.</p>
          </div>
        )}

        {results.length > 0 && (
          <div className="results-list">
            <div className="results-header-count">
              <span>Retrieved {results.length} ranked segments (Cosine Distance Ranked)</span>
            </div>

            <div className="results-cards-stack">
              {results.map((res, idx) => (
                <div key={idx} className="result-card">
                  <div className="result-card-header">
                    <div className="result-source-meta">
                      <span className="rank-badge">#{idx + 1}</span>
                      <FileText size={15} />
                      <span className="source-title">
                        {res.metadata?.filename || res.doc_id || 'Corpus Document'}
                      </span>
                      {res.metadata?.rhetorical_role && (
                        <span className={`role-badge ${res.metadata.rhetorical_role.toLowerCase()}`}>
                          {res.metadata.rhetorical_role}
                        </span>
                      )}
                    </div>

                    <div className="result-score">
                      {res.score !== undefined && (
                        <span className="similarity-score">
                          {((res.score || 0.85) * 100).toFixed(1)}% match
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="result-card-body">
                    <p className="chunk-text">"{res.text || res.content}"</p>
                  </div>

                  <div className="result-card-footer">
                    <div className="footer-meta-tags">
                      {res.metadata?.page && <span className="meta-tag">Page {res.metadata.page}</span>}
                      {res.metadata?.chunk_index !== undefined && (
                        <span className="meta-tag">Chunk #{res.metadata.chunk_index}</span>
                      )}
                      {res.metadata?.category && (
                        <span className="meta-tag">{res.metadata.category}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
