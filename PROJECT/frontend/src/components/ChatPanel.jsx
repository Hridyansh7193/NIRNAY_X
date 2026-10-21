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
} from 'lucide-react'

const SUGGESTIONS = [
  {
    title: 'Statutory Provisions',
    query: 'Identify the applicable IPC, BNS, or CrPC sections mentioned in the case materials and their elements.',
    persona: 'advocate',
  },
  {
    title: 'Plain Language Explanation',
    query: 'Explain the core dispute and allegations in simple words without complex legal jargon.',
    persona: 'citizen',
  },
  {
    title: 'Procedural Timeline & Facts',
    query: 'Extract the chronological facts, filing dates, and procedural posture of this matter.',
    persona: 'advocate',
  },
  {
    title: 'Legal Remedies & Relief',
    query: 'What legal remedies, bail provisions, or defensive steps are available to the aggrieved party?',
    persona: 'citizen',
  },
]

export default function ChatPanel({ persona, selectedDocId, onPersonaChange }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        `Welcome to **NirnayX** — AI-Powered Legal Intelligence & Decision-Support System.\n\n` +
        `I operate via an **11-step RAG pipeline** deterministically grounded in authoritative statutes, FIRs, petitions, and case laws. Every generated insight includes verifiable source citations.\n\n` +
        `Current Persona: **${persona === 'citizen' ? 'Citizen (Plain Language & Remedies)' : 'Advocate (Statutory Rigor & Precedents)'}**.\n\n` +
        `Ask any legal question, or click one of the suggested prompts below to begin.`,
      sources: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [copiedId, setCopiedId] = useState(null)
  const [expandedSources, setExpandedSources] = useState({})
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
          sources: (data.sources || []).map((s) => ({
            ...s,
            text: s.text || s.text_preview || s.content,
            score: s.relevance_score !== undefined ? s.relevance_score : s.score,
          })),
          retrievalMetrics: {
            retrievedCount: data.retrieval_count ?? data.retrieved_count ?? 0,
            elapsedSeconds: data.latency_sec ?? data.elapsed_seconds ?? 0,
            provider: data.model_info?.model || data.model_provider || 'Simulated RAG Engine',
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
      {/* Top Banner / Context Info */}
      <div className="chat-top-banner">
        <div className="banner-left">
          <span className={`persona-badge ${persona}`}>
            {persona === 'citizen' ? <ShieldAlert size={14} /> : <BookOpen size={14} />}
            {persona === 'citizen' ? 'Citizen Mode' : 'Advocate Mode'}
          </span>
          <span className="banner-desc">
            {persona === 'citizen'
              ? 'Plain language explanations, practical remedies, simplified summaries'
              : 'Statutory citations (IPC/BNS), case precedents, strict evidentiary reasoning'}
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
        {messages.map((msg) => (
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

              <div className="message-content">
                <p style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</p>
              </div>

              {/* Citations & Grounding Sources */}
              {msg.sources && msg.sources.length > 0 && (
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
                              {src.metadata?.page && (
                                <div className="excerpt-meta">
                                  <span>Page {src.metadata.page}</span>
                                  {src.metadata.clause && <span>Clause: {src.metadata.clause}</span>}
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
                  <span>🔍 {msg.retrievalMetrics.retrievedCount} chunks evaluated</span>
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
        ))}

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
                  Executing 11-step RAG pipeline: Embedding query → Vector similarity search → Reranking → Grounded synthesis...
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
                ? "Describe your legal situation, notice, or ask for simple explanations..."
                : "Enter statutory query, legal proposition, IPC/BNS section inquiry, or precedent search..."
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
            ⚠️ NirnayX provides informational decision support grounded in uploaded corpora. Not a substitute for licensed legal counsel.
          </span>
        </div>
      </div>
    </div>
  )
}
