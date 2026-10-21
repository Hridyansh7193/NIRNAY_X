import React from 'react'
import { Scale, UploadCloud, Shield, BookOpen, Sparkles, Terminal } from 'lucide-react'

export default function Header({ persona, onPersonaChange, onUpload }) {
  return (
    <header className="header">
      <div className="header-brand">
        <div className="brand-logo-container">
          <Scale className="brand-icon" size={24} />
        </div>
        <div className="brand-titles">
          <div className="brand-name-row">
            <h1 className="brand-title">Nirnay<span>X</span></h1>
            <span className="brand-tag">v1.0 RAG</span>
          </div>
          <p className="brand-subtitle">AI-Powered Legal Intelligence & Decision-Support System</p>
        </div>
      </div>

      <div className="header-actions">
        {/* Persona Switcher */}
        <div className="persona-toggle-container">
          <span className="persona-label">Persona Mode:</span>
          <div className="persona-switch">
            <button
              type="button"
              className={`persona-btn ${persona === 'citizen' ? 'active' : ''}`}
              onClick={() => onPersonaChange('citizen')}
              title="Plain language explanations, practical remedies, simplified summaries"
            >
              <Shield size={14} className="persona-btn-icon" />
              <span>Citizen</span>
            </button>
            <button
              type="button"
              className={`persona-btn ${persona === 'advocate' ? 'active' : ''}`}
              onClick={() => onPersonaChange('advocate')}
              title="Statutory rigor, IPC/CrPC/BNS provisions, case law precedents, procedural posture"
            >
              <BookOpen size={14} className="persona-btn-icon" />
              <span>Advocate</span>
            </button>
          </div>
        </div>

        {/* Upload Document Button */}
        <button
          type="button"
          className="btn-primary upload-btn"
          onClick={onUpload}
        >
          <UploadCloud size={16} />
          <span>Upload Legal Doc</span>
        </button>
      </div>
    </header>
  )
}
