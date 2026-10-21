# Nirnay-X Research Project - Implementation Plan

## Context

The Nirnay-X project is an AI-powered legal intelligence platform designed to bridge the accessibility gap in the Indian legal ecosystem. The system implements a 11-step RAG (Retrieval-Augmented Generation) pipeline for legal document intelligence, supporting both common citizens and legal professionals. Current progress includes:
- Completed 11-step RAG pipeline architecture (PROJECT_SPEC.md)
- Implemented core components: document processing, embedding generation, vector database storage, semantic search, and LLM inference with grounding
- Preliminary evaluation shows Precision@K=0.78, Recall@K=0.82, MRR=0.71
- Research progress report created (research_progress_report.md)

## Phase 1: Initial Understanding (Completed)
- Read PROJECT_SPEC.md (technical architecture & specifications)
- Read FILES_CATALOG.md (directory structure & resource inventory)
- Analyzed system design: 11-functional modules (RAG Assistant, Document Processing, Simplified Explanations, Case Analysis, Provision/Precedent Retrieval, Summarization, Semantic Search, Timeline Tracking, Calendar Management, Case Organization, Conversational Interface)
- Identified evaluation framework: Precision@K, Recall@K, MRR, NDCG, Faithfulness, Answer Relevance, Context Utilization

## Phase 2: Design - Implementation Approach

### Recommended Approach
Build a production-ready Nirnay-X system with the following key components:

1. **Core RAG Pipeline** - End-to-end 11-stage workflow ensuring grounding at each stage
2. **Modular Service Architecture** - Separate services for document processing, embedding, retrieval, and generation
3. **Evaluation & Monitoring** - Automated metrics collection and user feedback integration
4. **Scalability Considerations** - Vector database optimization, caching, and horizontal scaling

### Critical Files to Modify
- `code/ingestion/` - PDF parsing and OCR modules
- `code/embeddings/` - Dense embedding generation pipelines
- `code/retrieval/` - Vector store indexing and top-K retrieval
- `code/retrieval/` - Semantic search engine with hybrid keyword+semantic retrieval
- `code/generation/` - LLM inference layer with citation generation
- `results/` - Evaluation scripts for Precision@K, Recall@K, MRR, NDCG
- `docs/` - Updated documentation with API specifications

### Technical Details
- **Embedding Strategy**: Dense vector embeddings for legal documents and queries
- **Retrieval Strategy**: Top-K (K=10) with cross-encoder re-ranking for legal relevance
- **Generation Approach**: Constrained decoding with mandatory citation tokens
- **Evaluation**: Automated benchmarking suite with human-aspect validation

## Phase 3: Review & Alignment

### Verification Steps
1. Validate that all 11 RAG stages are properly integrated
2. Confirm grounding mechanism (retrieved context + citations) is enforced
3. Ensure evaluation metrics are measurable and aligned with project goals
4. Check that documentation reflects current implementation state

### Risk Mitigation
- **Hallucination Risk**: Enforce citation tokens in all generated responses
- **Scalability**: Implement vector database caching and query batching
- **Coverage Gaps**: Expand training corpus with domain-specific legal texts

## Phase 4: Final Plan

### Timeline (Weeks 1-10)
- **Weeks 1-2**: Complete API integration of all 11 modules
- **Weeks 3-4**: Implement evaluation framework and benchmarking
- **Weeks 5-6**: Performance optimization (latency reduction, scalability)
- **Weeks 7-8**: Beta testing with legal partners, collect feedback
- **Weeks 9-10**: Final polish, documentation, and readiness for submission

### Deliverables
- Fully integrated Nirnay-X RAG system
- Comprehensive evaluation report with metrics
- API documentation and usage examples
- Deployment configuration (containerization, scaling)

## Phase 5: Execution

Once approved, proceed with:
1. Implementing the modular service architecture
2. Running unit and integration tests
3. Conducting beta testing with legal stakeholders
4. Finalizing documentation and preparing for submission

---
*Plan created for Nirnay-X viva preparation*
*Date: 2026-10-13*
