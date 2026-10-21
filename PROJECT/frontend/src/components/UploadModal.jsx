import React, { useState } from 'react'
import {
  UploadCloud,
  FileText,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Layers,
  ShieldCheck,
} from 'lucide-react'

export default function UploadModal({ onClose, onUploadComplete }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [progressStage, setProgressStage] = useState('')
  const [error, setError] = useState(null)
  const [successData, setSuccessData] = useState(null)

  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (selected) {
      if (!selected.name.toLowerCase().endsWith('.pdf')) {
        setError('Only PDF files are currently supported.')
        return
      }
      if (selected.size > 25 * 1024 * 1024) {
        setError('File size exceeds the 25MB limit.')
        return
      }
      setFile(selected)
      setError(null)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0]
      if (!dropped.name.toLowerCase().endsWith('.pdf')) {
        setError('Only PDF documents are supported.')
        return
      }
      setFile(dropped)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file || uploading) return

    setUploading(true)
    setError(null)
    setProgressStage('Step 1/5: Transferring PDF to secure ingestion buffer...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      // Simulate pipeline stage feedback
      const stageTimer1 = setTimeout(() => {
        setProgressStage('Step 2/5: Extracting text & running OCR analysis...')
      }, 700)
      const stageTimer2 = setTimeout(() => {
        setProgressStage('Step 3/5: Applying legally-coherent chunking & role detection...')
      }, 1500)
      const stageTimer3 = setTimeout(() => {
        setProgressStage('Step 4/5: Generating dense semantic vector embeddings...')
      }, 2300)
      const stageTimer4 = setTimeout(() => {
        setProgressStage('Step 5/5: Indexing chunks in ChromaDB vector store...')
      }, 3100)

      const res = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        body: formData,
      })

      clearTimeout(stageTimer1)
      clearTimeout(stageTimer2)
      clearTimeout(stageTimer3)
      clearTimeout(stageTimer4)

      const data = await res.json()

      if (res.ok && data.status === 'success') {
        setSuccessData(data.data)
        setTimeout(() => {
          onUploadComplete(data.data)
        }, 1600)
      } else {
        setError(data.detail || 'Document ingestion failed.')
        setUploading(false)
      }
    } catch (err) {
      console.error(err)
      setError('Network error connecting to http://localhost:8000. Is the backend running?')
      setUploading(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content upload-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <UploadCloud size={22} className="modal-icon" />
            <div>
              <h3>Ingest Legal Document</h3>
              <span className="modal-subtitle">11-Step RAG Ingestion Pipeline</span>
            </div>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose} disabled={uploading}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body upload-modal-body">
          {error && (
            <div className="upload-alert error">
              <AlertCircle size={16} /> <span>{error}</span>
            </div>
          )}

          {successData ? (
            <div className="upload-success-state">
              <CheckCircle2 size={48} className="success-icon-large" />
              <h4>Document Successfully Ingested!</h4>
              <p>
                <strong>{successData.filename}</strong> has been parsed and indexed.
              </p>
              <div className="success-stats-box">
                <div className="stat-item">
                  <span>Indexed Chunks:</span>
                  <strong>{successData.chunks_count || 'Complete'}</strong>
                </div>
                <div className="stat-item">
                  <span>Detected Category:</span>
                  <strong>{successData.category || 'General Legal Document'}</strong>
                </div>
              </div>
              <small>Closing window and updating active corpora...</small>
            </div>
          ) : (
            <>
              {/* Dropzone */}
              <div
                className={`dropzone-box ${file ? 'has-file' : ''}`}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  id="pdf-file-input"
                  accept=".pdf"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                  disabled={uploading}
                />
                <label htmlFor="pdf-file-input" className="dropzone-label">
                  <div className="dropzone-icon-circle">
                    {file ? <FileText size={28} /> : <UploadCloud size={28} />}
                  </div>
                  {file ? (
                    <div className="selected-file-info">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                      <span className="change-hint">Click or drop to replace</span>
                    </div>
                  ) : (
                    <div className="dropzone-prompt">
                      <strong>Click to upload</strong> or drag and drop PDF
                      <span className="file-types-hint">Supreme Court judgments, FIRs, Petitions, Contracts (Max 25MB)</span>
                    </div>
                  )}
                </label>
              </div>

              {uploading && (
                <div className="upload-progress-container">
                  <div className="progress-spinner-row">
                    <Loader2 size={18} className="spinner-icon" />
                    <span className="progress-text">{progressStage}</span>
                  </div>
                  <div className="animated-progress-line"></div>
                </div>
              )}

              <div className="ingestion-info-box">
                <ShieldCheck size={16} className="info-icon" />
                <p>
                  Documents are parsed with legal clause awareness (preserving provisos & statutory section numbers) and stored as private local vector embeddings in ChromaDB.
                </p>
              </div>
            </>
          )}
        </div>

        {!successData && (
          <div className="modal-footer">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={handleUpload}
              disabled={!file || uploading}
            >
              {uploading ? 'Processing Pipeline...' : 'Start Ingestion'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
