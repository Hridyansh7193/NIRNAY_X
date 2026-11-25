import React, { useState, useRef, useEffect } from 'react'
import {
  Send,
  Bot,
  User,
  Sparkles,
  FileText,
  Bookmark,
  ChevronDown,
  ChevronUp,
  Clock,
  ShieldAlert,
  Copy,
  Check,
  RotateCcw,
  BookOpen,
  Scale,
  ExternalLink,
  Layers,
  PieChart,
  Table as TableIcon,
  LayoutGrid,
} from 'lucide-react'
import {
  ModulesView,
  VennDiagramView,
  ChartsView,
  TablesView,
  MarkdownRenderer,
} from './VisualArtifacts'

const SUGGESTIONS = [
  {
    title: 'Wrong-Lane Collision & FIR',
    query: 'A truck hit my car on the wrong lane. Can I press charges and claim compensation?',
    persona: 'citizen',
  },
  {
    title: 'Statutory Offence Formulation',
    query: 'Identify the applicable BNS, BNSS, and Motor Vehicles Act provisions and penal concordance.',
    persona: 'advocate',
  },
  {
    title: 'Anticipatory Bail & Section 482 BNSS',
    query: 'What are the procedural requirements and landmark grounds for seeking anticipatory bail under BNSS / CrPC?',
    persona: 'advocate',
  },
  {
    title: 'Mandatory FIR & Lalita Kumari',
    query: 'What are my legal remedies if the police refuse to register my FIR for a cognizable offence?',
    persona: 'citizen',
  },
]

export default function ChatPanel({ persona, selectedDocId, onPersonaChange }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        `## Welcome to **NirnayX** — AI-Powered Legal Intelligence & Decision-Support System\n\n` +
        `Operating via a deterministic **11-step RAG pipeline** with dense vector retrieval, **Cross-Scoring Legal Reranking**, and **Multi-Modal Visual Decision Synthesis** (Modules, Venn Diagrams, Charts, and Tabular Matrices).\n\n` +
        `Current Persona: **${persona === 'citizen' ? 'Citizen (Plain Language & Actionable Remedies)' : 'Advocate (Statutory Rigor, BNS/BNSS Concordance & Precedents)'}**.\n\n` +
        `Ask any legal question below, or select a suggested research inquiry to view the visual decision modules.`,
      sources: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [copiedId, setCopiedId] = useState(null)
  const [expandedSources, setExpandedSources] = useState({})
  const [activeTabs, setActiveTabs] = useState({}) // { [msgId]: 'comprehensive' | 'modules' | 'venn' | 'charts' | 'tables' | 'sources' }
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const toggleSource = (msgId, index) => {
    const key = `${msgId}-${index}`
    setExpandedSources((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const setTabForMessage = (msgId, tab) => {
    setActiveTabs((prev) => ({ ...prev, [msgId]: tab }))
  }

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleClearChat = () => {
    setMessages([
      {
        id: 'reset',
        role: 'assistant',
        content: `Session cleared. Ready for your legal inquiries under **${persona === 'citizen' ? 'Citizen' : 'Advocate'}** mode.`,
        sources: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ])
  }

  const handleSend = async (queryText = null) => {
    const text = (queryText || inputValue).trim()
    if (!text || loading) return

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      // Build previous chat history for multi-turn RAG context
      const chatHistory = messages
        .filter((m) => m.id !== 'welcome' && m.id !== 'reset')
        .slice(-6)
        .map((m) => ({
          role: m.role,
          content: m.content,
        }))

      const payload = {
        query: text,
        persona: persona,
        doc_id: selectedDocId || null,
        chat_history: chatHistory,
      }

      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (res.ok && data.status === 'ok') {
        const botMessage = {
          id: `bot-${Date.now()}`,
          role: 'assistant',
          content: data.answer || data.response || 'No response generated.',
          structuredData: data.structured_data || null,
          sources: (data.sources || []).map((s) => ({
            ...s,
            text: s.text || s.text_preview || s.content,
            score: s.relevance_score !== undefined ? s.relevance_score : s.score,
          })),
          retrievalMetrics: {
            retrievedCount: data.retrieval_count ?? data.retrieved_count ?? 0,
            elapsedSeconds: data.latency_sec ?? data.elapsed_seconds ?? 0,
            provider: data.model_info?.model || data.model_provider || 'NirnayX RAG Engine',
          },
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setMessages((prev) => [...prev, botMessage])
      } else {
        const errorMessage = {
          id: `error-${Date.now()}`,
          role: 'assistant',
          isError: true,
          content: `⚠️ **Pipeline Error:** ${data.detail || data.message || 'Unable to retrieve grounded answer. Please ensure the backend server is running on port 8000.'}`,
          sources: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setMessages((prev) => [...prev, errorMessage])
      }
    } catch (err) {
      const networkError = {
        id: `net-error-${Date.now()}`,
        role: 'assistant',
        isError: true,
        content: `⚠️ **Connection Error:** Could not reach the NirnayX backend at \`http://localhost:8000\`. Please ensure the FastAPI server is active.`,
        sources: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      setMessages((prev) => [...prev, networkError])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-panel">
      {/* Top Banner */}
      <div className="chat-top-banner">
        <div className="banner-left">
          <span className={`persona-badge ${persona}`}>
            {persona === 'citizen' ? <ShieldAlert size={14} /> : <BookOpen size={14} />}
            {persona === 'citizen' ? 'Citizen Mode' : 'Advocate Mode'}
          </span>
          <span className="banner-desc">
            {persona === 'citizen'
              ? 'Plain language explanations, practical remedies, simplified summaries'
              : 'Statutory citations (BNS/BNSS/IPC), case precedents, strict evidentiary reasoning'}
          </span>
        </div>
        <div className="banner-right">
          <button
            type="button"
            className="btn-ghost clear-btn"
            onClick={handleClearChat}
            title="Reset conversation"
          >
            <RotateCcw size={14} />
            <span>Reset Chat</span>
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="chat-messages-container">
        {messages.map((msg) => {
          const currentTab = activeTabs[msg.id] || 'comprehensive'
          const sData = msg.structuredData

          return (
            <div
              key={msg.id}
              className={`message-row ${msg.role === 'user' ? 'user-row' : 'bot-row'} ${
                msg.isError ? 'error-row' : ''
              }`}
            >
              <div className="message-avatar">
                {msg.role === 'user' ? <User size={18} /> : <Scale size={18} />}
              </div>

              <div className="message-bubble-wrapper">
                <div className="message-header-row">
                  <span className="sender-name">
                    {msg.role === 'user' ? 'You' : 'NirnayX Intelligence'}
                  </span>
                  <span className="message-time">{msg.timestamp}</span>
                </div>

                {/* Visual View-Mode Tabs for Assistant Messages with Structured Data */}
                {msg.role === 'assistant' && sData && (
                  <div className="result-view-tabs-bar">
                    <button
                      type="button"
                      className={`view-tab-btn ${currentTab === 'comprehensive' ? 'active' : ''}`}
                      onClick={() => setTabForMessage(msg.id, 'comprehensive')}
                    >
                      <LayoutGrid size={13} />
                      <span>Comprehensive</span>
                    </button>

                    {sData.modules && sData.modules.length > 0 && (
                      <button
                        type="button"
                        className={`view-tab-btn ${currentTab === 'modules' ? 'active' : ''}`}
                        onClick={() => setTabForMessage(msg.id, 'modules')}
                      >
                        <Layers size={13} />
                        <span>Modules ({sData.modules.length})</span>
                      </button>
                    )}

                    {sData.venn_diagram && (
                      <button
                        type="button"
                        className={`view-tab-btn ${currentTab === 'venn' ? 'active' : ''}`}
                        onClick={() => setTabForMessage(msg.id, 'venn')}
                      >
                        <PieChart size={13} />
                        <span>Venn Diagram</span>
                      </button>
                    )}

                    {sData.charts && sData.charts.length > 0 && (
                      <button
                        type="button"
                        className={`view-tab-btn ${currentTab === 'charts' ? 'active' : ''}`}
                        onClick={() => setTabForMessage(msg.id, 'charts')}
                      >
                        <Clock size={13} />
                        <span>Charts & Timeline</span>
                      </button>
                    )}

                    {sData.tables && sData.tables.length > 0 && (
                      <button
                        type="button"
                        className={`view-tab-btn ${currentTab === 'tables' ? 'active' : ''}`}
                        onClick={() => setTabForMessage(msg.id, 'tables')}
                      >
                        <TableIcon size={13} />
                        <span>Statutory Tables</span>
                      </button>
                    )}

                    {msg.sources && msg.sources.length > 0 && (
                      <button
                        type="button"
                        className={`view-tab-btn ${currentTab === 'sources' ? 'active' : ''}`}
                        onClick={() => setTabForMessage(msg.id, 'sources')}
                      >
                        <Bookmark size={13} />
                        <span>Sources ({msg.sources.length})</span>
                      </button>
                    )}
                  </div>
                )}

                {/* ── Active View Rendering ── */}
                <div className="message-content">
                  {/* Default / Plain text for user or simple messages */}
                  {(!sData || msg.role === 'user') && (
                    <MarkdownRenderer content={msg.content} />
                  )}

                  {/* Comprehensive View: renders Modules, Venn, Charts, Tables, and Prose */}
                  {sData && currentTab === 'comprehensive' && (
                    <div className="comprehensive-display-stack">
                      <ModulesView modules={sData.modules} />
                      <VennDiagramView vennData={sData.venn_diagram} />
                      <ChartsView charts={sData.charts} />
                      <TablesView tables={sData.tables} />
                      <div className="mt-4 pt-4 border-t border-[var(--card-border)]">
                        <MarkdownRenderer content={msg.content} />
                      </div>
                    </div>
                  )}

                  {/* Tab 1: Modules Only */}
                  {sData && currentTab === 'modules' && (
                    <ModulesView modules={sData.modules} />
                  )}

                  {/* Tab 2: Venn Diagram Only */}
                  {sData && currentTab === 'venn' && (
                    <VennDiagramView vennData={sData.venn_diagram} />
                  )}

                  {/* Tab 3: Charts & Timeline Only */}
                  {sData && currentTab === 'charts' && (
                    <ChartsView charts={sData.charts} />
                  )}

                  {/* Tab 4: Statutory Tables Only */}
                  {sData && currentTab === 'tables' && (
                    <TablesView tables={sData.tables} />
                  )}

                  {/* Tab 5: Sources Focused View */}
                  {sData && currentTab === 'sources' && (
                    <div className="focused-sources-view">
                      <div className="mb-3 text-xs text-[var(--muted-foreground)]">
                        Indexed statutory authorities & precedents evaluated by the Stage-2 Reranker:
                      </div>
                    </div>
                  )}
                </div>

                {/* Grounding Source Citations (Shown in Comprehensive or Sources tab) */}
                {msg.sources && msg.sources.length > 0 && (currentTab === 'comprehensive' || currentTab === 'sources') && (
                  <div className="citations-container">
                    <div className="citations-header">
                      <Bookmark size={14} className="cite-icon" />
                      <span>Authoritative Grounding Sources ({msg.sources.length} Retrieved Chunks)</span>
                    </div>
                    <div className="citations-grid">
                      {msg.sources.map((src, idx) => {
                        const sourceKey = `${msg.id}-${idx}`
                        const isExpanded = !!expandedSources[sourceKey]
                        return (
                          <div key={idx} className="citation-card">
                            <div
                              className="citation-card-header"
                              onClick={() => toggleSource(msg.id, idx)}
                            >
                              <div className="citation-title-group">
                                <FileText size={14} className="cite-doc-icon" />
                                <span className="cite-doc-title">
                                  {src.metadata?.filename || src.doc_id || 'Corpus Source'}
                                </span>
                                {src.metadata?.rhetorical_role && (
                                  <span className={`role-badge ${src.metadata.rhetorical_role.toLowerCase()}`}>
                                    {src.metadata.rhetorical_role}
                                  </span>
                                )}
                              </div>
                              <div className="citation-score-group">
                                {src.score !== undefined && (
                                  <span className="score-badge">
                                    {(src.score * 100).toFixed(0)}% match
                                  </span>
                                )}
                                {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                              </div>
                            </div>

                            {isExpanded && (
                              <div className="citation-excerpt">
                                <p className="excerpt-text">"{src.text || src.content}"</p>
                                {src.metadata?.doc_type && (
                                  <div className="excerpt-meta">
                                    <span>Type: {src.metadata.doc_type}</span>
                                    {src.metadata?.chunk_index !== undefined && (
                                      <span>Chunk #{src.metadata.chunk_index}</span>
                                    )}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* Retrieval Telemetry Footer */}
                {msg.retrievalMetrics && (
                  <div className="retrieval-telemetry">
                    <span>⏱ {msg.retrievalMetrics.elapsedSeconds}s</span>
                    <span>•</span>
                    <span>🔍 {msg.retrievalMetrics.retrievedCount} chunks evaluated & reranked</span>
                    <span>•</span>
                    <span>⚡ {msg.retrievalMetrics.provider}</span>
                  </div>
                )}

                {/* Action Toolbar */}
                <div className="message-toolbar">
                  <button
                    type="button"
                    className="msg-tool-btn"
                    onClick={() => handleCopy(msg.id, msg.content)}
                    title="Copy response"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check size={13} className="success-icon" /> <span>Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy size={13} /> <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )
        })}

        {loading && (
          <div className="message-row bot-row">
            <div className="message-avatar">
              <Scale size={18} />
            </div>
            <div className="message-bubble-wrapper">
              <div className="thinking-loader">
                <div className="pulse-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="loader-text">
                  Executing 11-step RAG pipeline: Query Vectorization → Dense Search → Legal Reranking → Multi-Modal Synthesis (Modules, Venn, Charts, Tables)...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Inquiries (Show when few messages) */}
      {messages.length <= 2 && !loading && (
        <div className="suggestions-section">
          <div className="suggestions-label">
            <Sparkles size={14} /> Suggested Research Inquiries
          </div>
          <div className="suggestions-grid">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                type="button"
                className="suggestion-chip"
                onClick={() => {
                  if (s.persona !== persona) {
                    onPersonaChange(s.persona)
                  }
                  handleSend(s.query)
                }}
              >
                <span className="chip-title">{s.title}</span>
                <span className="chip-query">{s.query}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Composer Box */}
      <div className="chat-composer-container">
        <div className="composer-wrapper">
          <textarea
            ref={inputRef}
            className="composer-textarea"
            rows="2"
            placeholder={
              persona === 'citizen'
                ? "Describe your legal situation, notice, accident details, or ask for simple remedies..."
                : "Enter statutory query, legal proposition, IPC/BNS cross-mapping, or precedent search..."
            }
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            type="button"
            className="composer-send-btn"
            disabled={!inputValue.trim() || loading}
            onClick={() => handleSend()}
            title="Send query"
          >
            <Send size={18} />
          </button>
        </div>
        <div className="composer-footer-note">
          <span>
            ⚠️ NirnayX provides informational decision support grounded in authoritative corpora. Not a substitute for licensed legal counsel.
          </span>
        </div>
      </div>
    </div>
  )
}
