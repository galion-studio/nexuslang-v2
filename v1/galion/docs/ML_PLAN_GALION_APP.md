# ML PLAN – GALION.APP

**Machine Learning & Knowledge Strategy**

**Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Alpha Phase

---

## MISSION

Train Nexus Core to understand and reason about:
- **Physics** (classical, quantum, relativity, thermodynamics)
- **Chemistry** (organic, inorganic, physical, computational)
- **Mathematics** (calculus, linear algebra, topology, statistics)
- **Materials Science** (properties, structures, synthesis)
- **3D Models** (spatial reasoning, mesh analysis, CAD)

**Goal:** Create a JARVIS-like AI that can answer complex scientific questions and reason about 3D spatial data.

---

## FIRST PRINCIPLES APPROACH

### Question Every Requirement

**Q:** Do we need to train an LLM from scratch?  
**A:** NO. Use Llama 3.1 8B Instruct (open, 8k context) with RAG over curated scientific corpora.

**Q:** Do we need a massive GPU cluster?  
**A:** NO. One g5.2xlarge (24GB VRAM) can run Llama 3.1 8B in int8 quantization.

**Q:** Do we need to index all of arXiv?  
**A:** NO. Start with 1000 high-quality papers in target domains; expand based on user queries.

**Q:** Do we need custom 3D neural networks?  
**A:** NO. Extract features offline (point clouds, surface descriptors) + text captions for RAG.

### Delete the Part

**DELETE:**
- Training LLMs from scratch (years + millions)
- Real-time 3D neural rendering (future feature)
- Multi-modal transformers (use simpler feature extraction)
- 100TB data lake (start with 1TB)

**KEEP:**
- RAG over curated corpora
- Light fine-tuning for domain style
- Offline 3D feature extraction
- Incremental data expansion

---

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                     ML PIPELINE                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Query                                                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  Query Understanding & Routing       │                 │
│  │  (Intent, entities, domain)          │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  Retrieval (RAG)                     │                 │
│  │  - Dense: bge-large embeddings       │                 │
│  │  - Sparse: BM25 keyword search       │                 │
│  │  - Hybrid fusion                     │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  Re-ranking                          │                 │
│  │  (bge-reranker-base)                 │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  Generation                          │                 │
│  │  (Llama 3.1 8B Instruct)             │                 │
│  │  + Retrieved context                 │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  Citation & Source Attribution       │                 │
│  │  (Link back to papers, 3D models)    │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  Response to User                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## DATA STRATEGY

### Knowledge Domains

#### 1. Physics
**Sources:**
- arXiv (physics, quant-ph, cond-mat, astro-ph)
- OpenStax Physics textbooks
- Feynman Lectures (public domain)
- Wikipedia physics articles (curated)

**Coverage:**
- Classical mechanics
- Quantum mechanics
- Electromagnetism
- Thermodynamics
- Relativity (special & general)
- Particle physics
- Astrophysics

**Alpha Target:** 300 papers + 5 textbooks

#### 2. Chemistry
**Sources:**
- PubChem (compound data)
- ChemSpider (structures)
- arXiv (chem-ph)
- OpenStax Chemistry
- Wikipedia chemistry (curated)

**Coverage:**
- Organic chemistry
- Inorganic chemistry
- Physical chemistry
- Computational chemistry
- Reaction mechanisms
- Spectroscopy

**Alpha Target:** 300 papers + 3 textbooks + 10k compounds

#### 3. Mathematics
**Sources:**
- arXiv (math)
- OpenStax Math textbooks
- ProofWiki (theorems + proofs)
- Wikipedia math (curated)

**Coverage:**
- Calculus
- Linear algebra
- Differential equations
- Topology
- Abstract algebra
- Statistics & probability

**Alpha Target:** 200 papers + 4 textbooks + 1k theorems

#### 4. Materials Science
**Sources:**
- Materials Project (computational data)
- arXiv (cond-mat.mtrl-sci)
- ASM Handbooks (licensed)
- Wikipedia materials (curated)

**Coverage:**
- Crystal structures
- Material properties (mechanical, thermal, electrical)
- Phase diagrams
- Synthesis methods
- Characterization techniques

**Alpha Target:** 200 papers + 5k materials

#### 5. 3D Models
**Sources:**
- Thingiverse (CC-licensed)
- NIH 3D Print Exchange (biological models)
- Sketchfab (CC-licensed)
- OpenSCAD models (open source)

**Coverage:**
- Mechanical parts
- Biological structures (proteins, cells)
- Architectural models
- Scientific visualizations

**Alpha Target:** 100 models with metadata

---

## DATA LAKE STRUCTURE (S3)

```
s3://galion-app-data-{eu,us}/
├── raw/
│   ├── text/
│   │   ├── papers/
│   │   │   ├── physics/
│   │   │   ├── chemistry/
│   │   │   ├── math/
│   │   │   └── materials/
│   │   ├── textbooks/
│   │   └── wikipedia/
│   ├── audio/
│   │   └── voice_captures/
│   │       ├── YYYY-MM-DD/
│   │       └── metadata.json
│   └── 3d/
│       ├── models/
│       │   ├── stl/
│       │   ├── obj/
│       │   └── gltf/
│       └── metadata/
│           └── {model_id}.json
├── bronze/  # Raw ingested, validated
├── silver/  # Cleaned, normalized
└── gold/    # Enriched, indexed, ready for RAG
    ├── embeddings/
    │   ├── text_chunks/
    │   └── 3d_features/
    └── metadata/
        └── glue_catalog/
```

**Lifecycle:**
- Raw: 30 days Standard → 90 days IA → Glacier
- Bronze/Silver: 90 days Standard → IA
- Gold: Standard (hot access)
- Voice audio: 30 days Standard → 90 days IA → Glacier (with consent)

---

## INGESTION PIPELINE

### Text (Papers, Textbooks)

1. **Crawl/Download:**
   - arXiv: Use arXiv API (bulk download)
   - OpenStax: Download PDFs
   - Wikipedia: Use Wikipedia API

2. **Parse:**
   - PDFs → text via PyMuPDF or pdfplumber
   - Extract sections, equations (LaTeX), figures
   - Store metadata (title, authors, date, DOI, license)

3. **Chunk:**
   - Semantic chunking (512-1024 tokens)
   - Preserve context (section headers, equations)
   - Overlap 50 tokens between chunks

4. **Embed:**
   - bge-large-en-v1.5 (1024 dim)
   - Batch process on GPU
   - Store in pgvector or Qdrant

5. **Index:**
   - Dense: vector similarity
   - Sparse: BM25 (Elasticsearch or Tantivy)
   - Metadata: Postgres (title, authors, date, domain)

**Frequency:** Weekly batch job (AWS Glue or Lambda)

### 3D Models

1. **Download:**
   - Thingiverse API
   - NIH 3D Print Exchange
   - Manual curation

2. **Parse:**
   - Load mesh (trimesh library)
   - Extract features:
     - Bounding box, volume, surface area
     - Vertex/face counts
     - Material properties (if available)
   - Generate thumbnails (3 angles)

3. **Caption:**
   - Use BLIP-2 or LLaVA to generate text captions from thumbnails
   - Manual annotation for complex models

4. **Embed:**
   - Embed captions with bge-large
   - Store mesh features separately

5. **Index:**
   - Text search on captions
   - Metadata search (size, material, category)

**Frequency:** Monthly batch job

---

## MODELS

### Embeddings: bge-large-en-v1.5
- **Size:** 335M parameters
- **Dimensions:** 1024
- **Context:** 512 tokens
- **Performance:** MTEB #1 open model
- **Inference:** ~10ms on GPU, ~50ms on CPU
- **Hosting:** Self-hosted on g5.2xlarge

### Re-ranker: bge-reranker-base
- **Size:** 278M parameters
- **Input:** Query + document pairs
- **Performance:** Improves retrieval precision by 20-30%
- **Inference:** ~20ms per pair on GPU
- **Hosting:** Self-hosted on g5.2xlarge

### LLM: Llama 3.1 8B Instruct
- **Size:** 8B parameters
- **Context:** 8k tokens (expandable to 16k)
- **Quantization:** int8 (fits in 24GB VRAM)
- **Inference:** ~500ms for 100 tokens on g5.2xlarge
- **Hosting:** Self-hosted via vLLM or TGI

**Why Llama 3.1 8B?**
- Open weights (Llama 3 license)
- Strong reasoning abilities
- Fits in single GPU
- Fast inference with quantization
- Good instruction following

### Fine-tuning Strategy

**Phase 1 (Alpha):** No fine-tuning, use base models

**Phase 2 (Beta):** Light fine-tuning on domain style
- Dataset: 1k Q&A pairs from user interactions
- Method: LoRA (rank 16, alpha 32)
- Training: 1 epoch on g5.12xlarge (~4 hours)
- Cost: ~$20

**Phase 3 (1.0):** Task-specific adapters
- Separate LoRA adapters for physics, chemistry, math
- Switch adapter based on query domain
- Training: 2k examples per domain (~$100)

---

## RETRIEVAL (RAG)

### Hybrid Search

**Dense Retrieval (Vector Similarity):**
- Embed query with bge-large
- Cosine similarity search in pgvector/Qdrant
- Top 20 candidates

**Sparse Retrieval (BM25):**
- Keyword search with BM25
- Top 20 candidates

**Fusion:**
- Reciprocal Rank Fusion (RRF)
- Combine dense + sparse scores
- Top 10 after fusion

### Re-ranking

- Pass top 10 through bge-reranker-base
- Score each (query, document) pair
- Select top 5 for context

### Context Window Management

- Llama 3.1 8B: 8k tokens
- Reserve 2k for query + instructions
- Reserve 2k for response
- Use 4k for retrieved context (~5 chunks × 800 tokens)

---

## EVALUATION

### Retrieval Metrics

**Precision@k:**
- Measure: % of top-k results that are relevant
- Target: P@5 > 80%, P@10 > 70%
- Eval set: 500 hand-labeled query-document pairs

**Recall@k:**
- Measure: % of relevant docs in top-k
- Target: R@10 > 90%

**MRR (Mean Reciprocal Rank):**
- Measure: Average 1/rank of first relevant result
- Target: MRR > 0.85

### Generation Metrics

**Groundedness:**
- Measure: % of claims supported by retrieved context
- Method: NLI model (deberta-v3-large-mnli)
- Target: > 90%

**Faithfulness:**
- Measure: No hallucinations
- Method: Human eval (weekly sample of 50 responses)
- Target: < 5% hallucination rate

**Relevance:**
- Measure: Response answers the question
- Method: Human eval + LLM-as-judge
- Target: > 85% relevant

**Citation Accuracy:**
- Measure: Citations link to correct sources
- Method: Automated check + human spot check
- Target: 100% accurate citations

### Latency SLOs

- **P50:** < 1.5s (query → response start)
- **P95:** < 2.5s
- **P99:** < 4.0s

**Breakdown:**
- Retrieval: 200-400ms
- Re-ranking: 100-200ms
- Generation: 500-1500ms
- Overhead: 100-200ms

---

## 3D MODEL PROCESSING

### Feature Extraction

**Geometric Features:**
- Bounding box (min/max x, y, z)
- Volume (m³)
- Surface area (m²)
- Centroid
- Principal axes (PCA)

**Topological Features:**
- Vertex count
- Face count
- Edge count
- Euler characteristic
- Genus (holes)

**Material Properties (if available):**
- Density
- Young's modulus
- Tensile strength
- Thermal conductivity

### Text Generation

**Caption Generation:**
- Use BLIP-2 or LLaVA on 3 thumbnail views
- Combine captions: "A {object} with {features}"
- Manual refinement for complex models

**Descriptive Text:**
- Template: "{Category} model with {dimensions}, {material}, {features}"
- Example: "Mechanical gear model with 50mm diameter, steel, 20 teeth"

### Spatial Reasoning

**Query Types:**
- "Show me models similar to this gear"
- "Find models with volume < 100 cm³"
- "What's the surface area of this part?"
- "Compare these two structures"

**Implementation:**
- Metadata search for size/material
- Vector search on captions for similarity
- Compute metrics on-demand for comparisons

---

## DATA QUALITY

### Curation

**Inclusion Criteria:**
- Peer-reviewed papers (arXiv, journals)
- Open-access or licensed content
- High-quality 3D models (manifold, clean mesh)
- Accurate metadata

**Exclusion Criteria:**
- Paywalled content (unless licensed)
- Low-quality scans or models
- Duplicate content
- Offensive or harmful content

### Validation

**Text:**
- Check for OCR errors (papers)
- Validate LaTeX equations
- Verify DOI/citation accuracy

**3D Models:**
- Validate mesh (manifold, no self-intersections)
- Check file integrity
- Verify license (CC-BY, CC0, etc.)

### Metadata

**Required Fields:**
- Title, authors, date, source, license
- Domain/category (physics, chemistry, etc.)
- Language (default: English)

**Optional Fields:**
- DOI, arXiv ID, PubMed ID
- Keywords, abstract
- Figures, equations

---

## TRAINING INTERFACES

### Data Annotation Tool

**Purpose:** Label query-document relevance for eval

**Features:**
- Show query + top 10 retrieved docs
- Binary label: relevant / not relevant
- Optionally rank by relevance
- Track inter-annotator agreement

**Tech Stack:**
- Simple web UI (React)
- Backend: FastAPI
- Storage: Postgres

**Target:** 500 labeled queries for alpha eval

### Model Monitoring Dashboard

**Purpose:** Track ML metrics in production

**Metrics:**
- Retrieval latency (P50, P95, P99)
- Generation latency
- Cache hit rate
- Error rate
- User feedback (thumbs up/down)

**Tech Stack:**
- Grafana dashboard
- Prometheus metrics
- CloudWatch Logs Insights

### Fine-tuning Pipeline

**Purpose:** Automate fine-tuning experiments

**Steps:**
1. Collect user interactions (with consent)
2. Filter for high-quality Q&A pairs
3. Format as instruction-following dataset
4. Launch SageMaker training job
5. Evaluate on held-out set
6. Deploy if metrics improve

**Tech Stack:**
- AWS SageMaker (ad-hoc)
- Hugging Face Transformers
- Weights & Biases (experiment tracking)

---

## COST ESTIMATES

### Storage (Alpha)

- **Text:** 10 GB (1k papers + textbooks)
- **3D Models:** 5 GB (100 models)
- **Embeddings:** 1 GB (1M chunks × 1KB)
- **Voice:** 15 GB/month (5k min × 3 MB/min)
- **Total:** ~30 GB + 15 GB/month
- **Cost:** ~$1/month S3 Standard + $5/month IA

### Compute (Alpha)

- **Embedding:** 1 hour/week on GPU (~$1.50/week)
- **Inference:** g5.2xlarge 24/7 (~$1,050/month)
- **Batch jobs:** 10 hours/month on m7i.large (~$5/month)
- **Total:** ~$1,060/month

### Scaling (Beta → 1.0)

- **Storage:** 1 TB (50k papers + 20k models) → ~$25/month
- **Compute:** 2x g5.2xlarge + auto-scaling → ~$2,500/month
- **Fine-tuning:** 100 GPU hours/quarter → ~$500/quarter

---

## TIMELINE

### Week 1-2 (Alpha)
- Set up S3 data lake structure
- Ingest 1k papers (300 physics, 300 chem, 200 math, 200 materials)
- Deploy bge-large + Llama 3.1 8B on g5.2xlarge
- Implement RAG baseline with pgvector

### Week 3-4
- Add 100 3D models with captions
- Implement hybrid search (dense + sparse)
- Add re-ranker
- Build eval harness

### Week 5-6
- Collect user feedback
- Improve retrieval (tune hyperparams)
- Add citation tracking
- Expand to 5k papers

### Week 7-8 (Beta)
- Fine-tune Llama 3.1 8B on domain style
- Add 5k 3D models
- Implement spatial reasoning queries
- Scale to 10k papers

---

## SUCCESS CRITERIA

### Alpha
- ✅ 1k papers indexed and searchable
- ✅ 100 3D models with captions
- ✅ P@5 > 70% on eval set
- ✅ P95 latency < 2.5s
- ✅ < 10% hallucination rate

### Beta
- ✅ 10k papers indexed
- ✅ 5k 3D models
- ✅ P@5 > 80%
- ✅ P95 latency < 2.0s
- ✅ < 5% hallucination rate
- ✅ Fine-tuned model deployed

### 1.0
- ✅ 50k papers indexed
- ✅ 20k 3D models
- ✅ P@5 > 85%
- ✅ P95 latency < 1.5s
- ✅ < 3% hallucination rate
- ✅ Multi-domain adapters

---

## NEXT STEPS

1. **Immediate:**
   - Set up S3 buckets with lifecycle policies
   - Write ingestion scripts (arXiv, OpenStax)
   - Deploy bge-large + Llama 3.1 8B

2. **This Week:**
   - Ingest first 100 papers
   - Test RAG pipeline end-to-end
   - Build simple eval set (50 queries)

3. **Next 2 Weeks:**
   - Scale to 1k papers
   - Add 3D model processing
   - Launch alpha with beta testers

---

**Built with First Principles**  
**Status:** Ready to Implement  
**Let's train Nexus Core.** 🧠

