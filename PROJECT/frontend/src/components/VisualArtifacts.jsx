import React, { useState } from 'react'
import {
  Shield,
  Scale,
  BookOpen,
  Activity,
  Layers,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowRight,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'

// ── 1. MODULES COMPONENT ─────────────────────────────────
export function ModulesView({ modules }) {
  if (!modules || modules.length === 0) return null

  const getModuleIcon = (iconName) => {
    switch (iconName) {
      case 'shield':
        return <Shield size={18} className="text-emerald-400" />
      case 'scale':
        return <Scale size={18} className="text-indigo-400" />
      case 'book-open':
        return <BookOpen size={18} className="text-amber-400" />
      case 'activity':
      default:
        return <Activity size={18} className="text-cyan-400" />
    }
  }

  return (
    <div className="modules-container">
      <div className="modules-section-title">
        <Layers size={16} />
        <span>Analytical Decision Modules ({modules.length})</span>
      </div>
      <div className="modules-grid">
        {modules.map((mod, idx) => (
          <div key={mod.id || idx} className="module-card">
            <div className="module-header">
              <div className="module-icon-wrap">
                {getModuleIcon(mod.icon)}
              </div>
              <div className="module-title-group">
                <span className="module-badge">{mod.badge || `Module ${idx + 1}`}</span>
                <h4 className="module-title">{mod.title}</h4>
              </div>
            </div>

            {mod.summary && (
              <p className="module-summary">{mod.summary}</p>
            )}

            {mod.points && mod.points.length > 0 && (
              <ul className="module-points-list">
                {mod.points.map((pt, pIdx) => (
                  <li key={pIdx} className="module-point-item">
                    <span className="point-bullet">•</span>
                    <span className="point-text">{pt}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// ── 2. VENN DIAGRAM COMPONENT ─────────────────────────────
export function VennDiagramView({ vennData }) {
  if (!vennData) return null

  const left = vennData.left_set || {}
  const right = vennData.right_set || {}
  const center = vennData.intersection || {}

  const [activeSegment, setActiveSegment] = useState('intersection')

  return (
    <div className="venn-container">
      <div className="venn-header">
        <div>
          <h4 className="venn-title">🔵 {vennData.title || 'Jurisprudential Venn Analysis'}</h4>
          {vennData.subtitle && <p className="venn-subtitle">{vennData.subtitle}</p>}
        </div>
      </div>

      {/* Interactive SVG Venn Diagram */}
      <div className="venn-svg-wrapper">
        <svg viewBox="0 0 540 260" className="venn-svg">
          <defs>
            {/* Left Circle Glow */}
            <radialGradient id="leftGlow" cx="40%" cy="50%" r="60%">
              <stop offset="0%" stopColor={left.color || '#ef4444'} stopOpacity="0.55" />
              <stop offset="100%" stopColor={left.color || '#ef4444'} stopOpacity="0.12" />
            </radialGradient>
            {/* Right Circle Glow */}
            <radialGradient id="rightGlow" cx="60%" cy="50%" r="60%">
              <stop offset="0%" stopColor={right.color || '#10b981'} stopOpacity="0.55" />
              <stop offset="100%" stopColor={right.color || '#10b981'} stopOpacity="0.12" />
            </radialGradient>
            {/* Center Blend */}
            <linearGradient id="centerBlend" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={left.color || '#ef4444'} stopOpacity="0.45" />
              <stop offset="50%" stopColor="#818cf8" stopOpacity="0.7" />
              <stop offset="100%" stopColor={right.color || '#10b981'} stopOpacity="0.45" />
            </linearGradient>
          </defs>

          {/* Left Circle */}
          <circle
            cx="210"
            cy="130"
            r="115"
            fill="url(#leftGlow)"
            stroke={left.color || '#ef4444'}
            strokeWidth={activeSegment === 'left' ? '3' : '1.5'}
            className="cursor-pointer transition-all duration-300"
            onClick={() => setActiveSegment('left')}
          />

          {/* Right Circle */}
          <circle
            cx="330"
            cy="130"
            r="115"
            fill="url(#rightGlow)"
            stroke={right.color || '#10b981'}
            strokeWidth={activeSegment === 'right' ? '3' : '1.5'}
            className="cursor-pointer transition-all duration-300"
            onClick={() => setActiveSegment('right')}
          />

          {/* Intersection Clip Area Highlighting */}
          <ellipse
            cx="270"
            cy="130"
            rx="55"
            ry="90"
            fill="url(#centerBlend)"
            stroke="#a5b4fc"
            strokeWidth={activeSegment === 'intersection' ? '2.5' : '1'}
            strokeDasharray={activeSegment === 'intersection' ? 'none' : '4,2'}
            className="cursor-pointer transition-all duration-300"
            onClick={() => setActiveSegment('intersection')}
          />

          {/* Labels on SVG */}
          <text x="145" y="85" textAnchor="middle" className="venn-svg-text-title" fill="#fca5a5">
            {left.name ? left.name.split('(')[0].trim() : 'Left Domain'}
          </text>
          <text x="145" y="105" textAnchor="middle" className="venn-svg-text-count" fill="#cbd5e1">
            {left.items ? `${left.items.length} Elements` : ''}
          </text>

          <text x="395" y="85" textAnchor="middle" className="venn-svg-text-title" fill="#6ee7b7">
            {right.name ? right.name.split('(')[0].trim() : 'Right Domain'}
          </text>
          <text x="395" y="105" textAnchor="middle" className="venn-svg-text-count" fill="#cbd5e1">
            {right.items ? `${right.items.length} Elements` : ''}
          </text>

          <text x="270" y="125" textAnchor="middle" className="venn-svg-text-shared" fill="#ffffff" fontWeight="bold">
            SHARED CORE
          </text>
          <text x="270" y="145" textAnchor="middle" className="venn-svg-text-count" fill="#e0e7ff">
            {center.items ? `${center.items.length} Principles` : ''}
          </text>
        </svg>
      </div>

      {/* Segment Selector Pills */}
      <div className="venn-pill-row">
        <button
          type="button"
          className={`venn-pill-btn ${activeSegment === 'left' ? 'active-left' : ''}`}
          onClick={() => setActiveSegment('left')}
        >
          <span className="dot" style={{ background: left.color || '#ef4444' }}></span>
          <span>{left.name || 'Left Set'}</span>
          <span className="count-tag">{left.items?.length || 0}</span>
        </button>

        <button
          type="button"
          className={`venn-pill-btn ${activeSegment === 'intersection' ? 'active-center' : ''}`}
          onClick={() => setActiveSegment('intersection')}
        >
          <span className="dot" style={{ background: '#818cf8' }}></span>
          <span>{center.name || 'Harmonized Intersection'}</span>
          <span className="count-tag">{center.items?.length || 0}</span>
        </button>

        <button
          type="button"
          className={`venn-pill-btn ${activeSegment === 'right' ? 'active-right' : ''}`}
          onClick={() => setActiveSegment('right')}
        >
          <span className="dot" style={{ background: right.color || '#10b981' }}></span>
          <span>{right.name || 'Right Set'}</span>
          <span className="count-tag">{right.items?.length || 0}</span>
        </button>
      </div>

      {/* Active Segment Detail Card */}
      <div className="venn-active-card">
        {activeSegment === 'left' && (
          <div className="segment-detail left-detail">
            <h5>{left.name}</h5>
            <ul className="segment-items-list">
              {(left.items || []).map((item, i) => (
                <li key={i}><CheckCircle2 size={13} className="text-rose-400" /> {item}</li>
              ))}
            </ul>
          </div>
        )}

        {activeSegment === 'intersection' && (
          <div className="segment-detail center-detail">
            <h5>⚡ {center.name}</h5>
            <ul className="segment-items-list">
              {(center.items || []).map((item, i) => (
                <li key={i}><CheckCircle2 size={13} className="text-indigo-400" /> {item}</li>
              ))}
            </ul>
          </div>
        )}

        {activeSegment === 'right' && (
          <div className="segment-detail right-detail">
            <h5>{right.name}</h5>
            <ul className="segment-items-list">
              {(right.items || []).map((item, i) => (
                <li key={i}><CheckCircle2 size={13} className="text-emerald-400" /> {item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {vennData.commentary && (
        <div className="venn-commentary">
          <strong>Strategic Takeaway:</strong> {vennData.commentary}
        </div>
      )}
    </div>
  )
}

// ── 3. CHARTS & TIMELINES COMPONENT ────────────────────────
export function ChartsView({ charts }) {
  if (!charts || charts.length === 0) return null

  return (
    <div className="charts-container">
      {charts.map((chart, idx) => {
        if (chart.type === 'timeline') {
          return (
            <div key={chart.id || idx} className="chart-card timeline-chart-card">
              <div className="chart-header">
                <div>
                  <h4 className="chart-title">⏱️ {chart.title}</h4>
                  {chart.description && <p className="chart-desc">{chart.description}</p>}
                </div>
              </div>

              <div className="timeline-stepper">
                {(chart.stages || []).map((stg, sIdx) => (
                  <div key={sIdx} className={`timeline-step-node ${stg.status || 'pending'}`}>
                    <div className="step-marker">
                      <span className="step-number">{sIdx + 1}</span>
                      {sIdx < chart.stages.length - 1 && <div className="step-connector"></div>}
                    </div>
                    <div className="step-content">
                      <div className="step-header-row">
                        <span className="step-stage-name">{stg.step || `Stage ${sIdx + 1}`}</span>
                        {stg.provision && <span className="step-provision-pill">{stg.provision}</span>}
                        {stg.timeframe && (
                          <span className="step-time-pill">
                            <Clock size={11} /> {stg.timeframe}
                          </span>
                        )}
                      </div>
                      <h5 className="step-title">{stg.title}</h5>
                      <p className="step-action">{stg.action}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        }

        // Horizontal Bar Chart
        const maxVal = Math.max(...(chart.items || []).map((i) => i.value || 1), 1)

        return (
          <div key={chart.id || idx} className="chart-card bar-chart-card">
            <div className="chart-header">
              <div>
                <h4 className="chart-title">📊 {chart.title}</h4>
                {chart.description && <p className="chart-desc">{chart.description}</p>}
              </div>
              {chart.unit && <span className="chart-unit-badge">{chart.unit}</span>}
            </div>

            <div className="bar-chart-body">
              {(chart.items || []).map((item, iIdx) => {
                const pct = Math.min(100, Math.max(12, ((item.value || 0) / maxVal) * 100))
                return (
                  <div key={iIdx} className="bar-row-item">
                    <div className="bar-meta-row">
                      <span className="bar-label">{item.label}</span>
                      <div className="bar-right-info">
                        <span className="bar-val-display">{item.display || `${item.value} yrs`}</span>
                        {item.badge && (
                          <span className={`bar-badge ${item.badge.toLowerCase().includes('non') ? 'badge-rose' : 'badge-emerald'}`}>
                            {item.badge}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{
                          width: `${pct}%`,
                          background: item.color || '#6366f1',
                        }}
                      ></div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ── 4. STATUTORY TABLES COMPONENT ─────────────────────────
export function TablesView({ tables }) {
  if (!tables || tables.length === 0) return null

  return (
    <div className="tables-container">
      {tables.map((table, tIdx) => (
        <div key={tIdx} className="legal-table-card">
          <div className="table-card-header">
            <div className="table-title-group">
              <Scale size={16} className="text-indigo-400" />
              <h4>{table.title}</h4>
            </div>
            {table.caption && <span className="table-caption-badge">{table.caption}</span>}
          </div>

          <div className="table-responsive-wrapper">
            <table className="nirnay-data-table">
              <thead>
                <tr>
                  {(table.headers || []).map((h, hIdx) => (
                    <th key={hIdx}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(table.rows || []).map((row, rIdx) => (
                  <tr key={rIdx}>
                    {(row || []).map((cell, cIdx) => {
                      const strCell = String(cell)
                      let pillClass = null

                      if (strCell.includes('Non-Bailable') || strCell.includes('Heinous')) {
                        pillClass = 'pill-rose'
                      } else if (strCell.includes('Bailable') || strCell.includes('Routine')) {
                        pillClass = 'pill-emerald'
                      } else if (strCell.includes('Cognizable')) {
                        pillClass = 'pill-amber'
                      } else if (strCell.includes('Section') || strCell.includes('Article')) {
                        pillClass = 'pill-indigo'
                      }

                      return (
                        <td key={cIdx}>
                          {pillClass ? (
                            <span className={`table-cell-pill ${pillClass}`}>{strCell}</span>
                          ) : (
                            strCell
                          )}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  )
}

// ── 5. CLEAN MARKDOWN PROSE RENDERER ──────────────────────
export function MarkdownRenderer({ content }) {
  if (!content) return null

  const lines = content.split('\n')
  const elements = []
  let tableBuffer = []
  let inTable = false

  const flushTable = (key) => {
    if (tableBuffer.length < 2) {
      tableBuffer = []
      inTable = false
      return null
    }

    const headerLine = tableBuffer[0]
    const rowLines = tableBuffer.slice(2) // Skip separator line

    const headers = headerLine
      .split('|')
      .map((c) => c.trim())
      .filter(Boolean)

    const rows = rowLines.map((line) =>
      line
        .split('|')
        .map((c) => c.trim())
        .filter(Boolean)
    )

    tableBuffer = []
    inTable = false

    return (
      <div key={key} className="embedded-md-table-wrap">
        <table className="nirnay-data-table">
          <thead>
            <tr>
              {headers.map((h, i) => (
                <th key={i}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rIdx) => (
              <tr key={rIdx}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx]

    // Table Detection
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      inTable = true
      tableBuffer.push(line)
      continue
    } else if (inTable) {
      const tblElem = flushTable(`tbl-${idx}`)
      if (tblElem) elements.push(tblElem)
    }

    if (!line.trim()) {
      elements.push(<div key={`sp-${idx}`} className="h-2" />)
      continue
    }

    // Headings
    if (line.startsWith('## ')) {
      elements.push(
        <h2 key={idx} className="md-h2">
          {line.replace('## ', '')}
        </h2>
      )
    } else if (line.startsWith('### ')) {
      elements.push(
        <h3 key={idx} className="md-h3">
          {line.replace('### ', '')}
        </h3>
      )
    } else if (line.startsWith('#### ')) {
      elements.push(
        <h4 key={idx} className="md-h4">
          {line.replace('#### ', '')}
        </h4>
      )
    } else if (line.startsWith('> ')) {
      // Blockquotes
      elements.push(
        <blockquote key={idx} className="md-quote">
          {line.replace('> ', '')}
        </blockquote>
      )
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      // Bullet items
      elements.push(
        <div key={idx} className="md-bullet-item">
          <span className="bullet-dot">▪</span>
          <span>{renderFormattedText(line.slice(2))}</span>
        </div>
      )
    } else if (/^\d+\.\s/.test(line)) {
      // Numbered lists
      const numMatch = line.match(/^(\d+)\.\s(.*)/)
      elements.push(
        <div key={idx} className="md-numbered-item">
          <span className="num-badge">{numMatch[1]}</span>
          <span>{renderFormattedText(numMatch[2])}</span>
        </div>
      )
    } else if (line.startsWith('---')) {
      elements.push(<hr key={idx} className="md-hr" />)
    } else {
      elements.push(
        <p key={idx} className="md-p">
          {renderFormattedText(line)}
        </p>
      )
    }
  }

  if (inTable) {
    const tblElem = flushTable(`tbl-end`)
    if (tblElem) elements.push(tblElem)
  }

  return <div className="markdown-body">{elements}</div>
}

function renderFormattedText(text) {
  if (!text) return ''

  // Split on **bold** formatting
  const parts = text.split(/(\*\*.*?\*\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-semibold text-indigo-300">
          {part.slice(2, -2)}
        </strong>
      )
    }
    return part
  })
}
