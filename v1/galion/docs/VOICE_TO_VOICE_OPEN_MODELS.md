# VOICE-TO-VOICE – OPEN MODELS STRATEGY

**Ship Now, Fine-tune Later**

**Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Alpha Phase

---

## STRATEGY

**Ship with open models NOW → Collect real user data → Fine-tune in 6-12 weeks**

**Why this approach?**
- Get to market fast (weeks vs months)
- Collect real-world voice data with user consent
- Learn actual use patterns before investing in custom training
- Reduce upfront costs ($1k/month vs $50k+ for custom training)

---

## PIPELINE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                  VOICE-TO-VOICE PIPELINE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Mic → WebSocket → Voice Service                      │
│                                                             │
│  ┌──────────────────────────────────────┐                 │
│  │  1. Speech-to-Text (STT)             │                 │
│  │     Faster-Whisper medium.en         │                 │
│  │     Latency: 300-500ms               │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  2. Natural Language Understanding   │                 │
│  │     Llama 3.1 8B Instruct            │                 │
│  │     Intent + Entity extraction       │                 │
│  │     Latency: 200-400ms               │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  3. Action Routing                   │                 │
│  │     Query RAG, call APIs, etc.       │                 │
│  │     Latency: 300-800ms               │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  4. Response Generation              │                 │
│  │     Llama 3.1 8B Instruct            │                 │
│  │     Latency: 500-1000ms              │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  ┌──────────────────────────────────────┐                 │
│  │  5. Text-to-Speech (TTS)             │                 │
│  │     XTTS v2 or OpenVoice             │                 │
│  │     Latency: 400-800ms               │                 │
│  └──────────────────────────────────────┘                 │
│      ↓                                                      │
│  WebSocket → User Speakers                                 │
│                                                             │
│  Total P50: 1.5s | P95: 2.5s | P99: 4.0s                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## MODELS

### 1. Speech-to-Text: Faster-Whisper

**Model:** Faster-Whisper medium.en  
**Size:** 769M parameters  
**Quantization:** int8 (CTranslate2)  
**VRAM:** ~2 GB  
**Latency:** 300-500ms for 10s audio on g5.2xlarge  
**WER:** ~5-8% on LibriSpeech test-clean

**Why Faster-Whisper?**
- 4x faster than OpenAI Whisper
- Same accuracy as original Whisper
- Lower VRAM usage (int8 quantization)
- Open source (MIT license)
- Easy to fine-tune later

**Alternatives Considered:**
- OpenAI Whisper API: $0.006/min (expensive at scale)
- Wav2Vec2: Lower accuracy on scientific terms
- Conformer: Harder to fine-tune

**Deployment:**
- Self-hosted on g5.2xlarge GPU
- Docker container with CTranslate2
- Batch size 1 for low latency
- Streaming support (partial transcripts)

### 2. Text-to-Speech: XTTS v2

**Model:** XTTS v2 (Coqui TTS)  
**Size:** 400M parameters  
**VRAM:** ~4 GB  
**Latency:** 400-800ms for 20 words on g5.2xlarge  
**MOS:** ~4.0 (human-like quality)

**Why XTTS v2?**
- Multi-language support (17 languages)
- Voice cloning (1-shot from 6s audio)
- Emotional control (pitch, speed, energy)
- Open source (MPL 2.0)
- Easy to fine-tune

**Alternatives Considered:**
- OpenAI TTS API: $15/1M chars (expensive)
- ElevenLabs: $0.30/1k chars (expensive + closed)
- Bark: Slower, less controllable
- OpenVoice: Good alternative, similar quality

**Deployment:**
- Self-hosted on g5.2xlarge GPU
- Docker container with PyTorch
- Streaming audio output (chunks)
- 3 pre-configured voices (professional, friendly, technical)

### 3. NLU & Generation: Llama 3.1 8B Instruct

**Model:** Llama 3.1 8B Instruct  
**Size:** 8B parameters  
**Quantization:** int8 (bitsandbytes)  
**VRAM:** ~10 GB  
**Latency:** 500-1000ms for 100 tokens on g5.2xlarge  
**Context:** 8k tokens

**Why Llama 3.1 8B?**
- Strong reasoning and instruction following
- Fits in single GPU with STT + TTS
- Fast inference with quantization
- Open weights (Llama 3 license)
- Good for scientific domains

**Deployment:**
- Self-hosted via vLLM or TGI
- Shared GPU with STT + TTS
- KV cache for faster repeated queries

---

## LATENCY OPTIMIZATION

### Target SLOs
- **P50:** < 1.5s (end-to-end)
- **P95:** < 2.5s
- **P99:** < 4.0s

### Optimization Strategies

#### 1. Streaming
- **STT:** Stream partial transcripts every 1s
- **TTS:** Stream audio chunks every 200ms
- **LLM:** Stream tokens as generated

**Impact:** User hears response start in ~1s instead of waiting for full generation

#### 2. Model Quantization
- **STT:** int8 (4x faster, minimal accuracy loss)
- **LLM:** int8 (2x faster, <1% accuracy loss)
- **TTS:** fp16 (2x faster, no quality loss)

**Impact:** 2-4x latency reduction

#### 3. Batching (Future)
- Batch multiple user requests when traffic increases
- Trade latency for throughput
- Only enable when >10 concurrent users

**Impact:** 50% cost reduction at scale

#### 4. Caching
- Cache common queries (e.g., "What can you do?")
- Cache TTS for repeated phrases
- Redis with 1-hour TTL

**Impact:** 90% latency reduction for cached queries

#### 5. GPU Optimization
- Use Flash Attention 2 for LLM
- Use CTranslate2 for STT
- Use TorchScript for TTS

**Impact:** 20-30% latency reduction

---

## DATA CAPTURE STRATEGY

### User Consent

**Opt-in by default:**
- Clear consent dialog on first voice interaction
- Explain data usage (improve voice quality)
- Allow opt-out anytime
- Show data retention policy (90 days)

**Consent UI:**
```
┌────────────────────────────────────────┐
│  Help Improve Voice Quality            │
├────────────────────────────────────────┤
│                                        │
│  We'd like to record your voice       │
│  interactions to improve accuracy.     │
│                                        │
│  Your data will be:                    │
│  ✓ Stored securely (encrypted)        │
│  ✓ Used only for training             │
│  ✓ Deleted after 90 days              │
│  ✓ Never shared with third parties    │
│                                        │
│  [Allow]  [Deny]  [Learn More]        │
│                                        │
└────────────────────────────────────────┘
```

### What We Capture

**Audio:**
- Format: FLAC (lossless compression)
- Sample rate: 16 kHz mono
- Storage: S3 with encryption at rest
- Lifecycle: 30 days Standard → 60 days IA → Glacier

**Metadata:**
- Timestamp, user_id (anonymized), session_id
- Transcript (STT output)
- Intent (NLU output)
- Response (LLM output)
- Latency metrics (STT, NLU, TTS)
- User feedback (thumbs up/down)

**PII Redaction:**
- Automatic: Credit cards, SSNs, phone numbers
- Manual review: Names, addresses (weekly batch)

### Storage Layout

```
s3://galion-app-data-{eu,us}/raw/audio/voice_captures/
├── YYYY-MM-DD/
│   ├── {session_id}/
│   │   ├── audio.flac
│   │   ├── metadata.json
│   │   └── transcript.txt
│   └── ...
└── ...
```

**Metadata JSON:**
```json
{
  "session_id": "uuid",
  "user_id": "hashed_user_id",
  "timestamp": "2025-11-09T10:30:00Z",
  "duration_ms": 3500,
  "transcript": "What is the speed of light?",
  "intent": "scientific_query",
  "domain": "physics",
  "response": "The speed of light in vacuum is...",
  "latency": {
    "stt_ms": 320,
    "nlu_ms": 180,
    "rag_ms": 450,
    "llm_ms": 680,
    "tts_ms": 520,
    "total_ms": 2150
  },
  "feedback": "thumbs_up",
  "consent": true,
  "region": "us"
}
```

---

## FINE-TUNING ROADMAP

### Phase 1: Data Collection (Weeks 1-6)

**Goal:** Collect 200 hours of labeled voice data

**Activities:**
- Launch alpha with 50 beta testers
- Capture voice interactions (with consent)
- Manual labeling (correct transcripts, mark errors)
- Augment data (speed, noise, reverb)

**Metrics:**
- 200 hours raw audio
- 150 hours after filtering (quality check)
- 50k utterances labeled

**Cost:** ~$5k (labeling @ $10/hour)

### Phase 2: STT Fine-tuning (Weeks 7-8)

**Goal:** Reduce WER on scientific terms

**Dataset:**
- 150 hours labeled audio
- Focus on physics, chemistry, math terminology
- Augment with synthetic data (TTS → STT loop)

**Method:**
- Fine-tune Whisper medium.en
- LoRA adapters (rank 32)
- Train on g5.12xlarge (4x A10G)
- 3 epochs (~20 hours training)

**Expected Results:**
- WER: 5-8% → 3-5% on scientific terms
- Latency: Same (300-500ms)

**Cost:** ~$1,500 (GPU hours)

### Phase 3: TTS Fine-tuning (Weeks 9-10)

**Goal:** Create custom voices with personality

**Dataset:**
- 10 hours high-quality voice recordings (3 speakers)
- Professional voice actors (technical, friendly, authoritative)
- Scripted scientific content

**Method:**
- Fine-tune XTTS v2 on custom voices
- Train on g5.12xlarge
- 5 epochs per voice (~10 hours total)

**Expected Results:**
- MOS: 4.0 → 4.3 (more natural)
- Personality control (tone, pace, energy)
- Voice cloning from 6s samples

**Cost:** ~$2,000 (voice actors + GPU)

### Phase 4: Continuous Improvement (Weeks 11+)

**Goal:** Iterative refinement based on user feedback

**Activities:**
- Weekly model updates
- A/B testing (base vs fine-tuned)
- User feedback loop (thumbs up/down)
- Expand to new domains (biology, engineering)

**Metrics:**
- WER < 3% on all domains
- MOS > 4.5
- User satisfaction > 85%

---

## EVALUATION METRICS

### STT Quality: Word Error Rate (WER)

**Formula:** WER = (S + D + I) / N
- S: Substitutions
- D: Deletions
- I: Insertions
- N: Total words

**Targets:**
- Alpha: WER < 8%
- Beta: WER < 5%
- 1.0: WER < 3%

**Eval Set:** 1000 utterances (hand-labeled)

### TTS Quality: Mean Opinion Score (MOS)

**Method:** Human raters score 1-5
- 5: Excellent (natural, clear)
- 4: Good (minor artifacts)
- 3: Fair (noticeable issues)
- 2: Poor (hard to understand)
- 1: Bad (unintelligible)

**Targets:**
- Alpha: MOS > 3.5
- Beta: MOS > 4.0
- 1.0: MOS > 4.5

**Eval Set:** 100 generated samples

### Latency: P50, P95, P99

**Measurement:** End-to-end (mic → speaker)

**Targets:**
- Alpha: P50 < 2.0s, P95 < 3.0s
- Beta: P50 < 1.5s, P95 < 2.5s
- 1.0: P50 < 1.0s, P95 < 2.0s

**Monitoring:** CloudWatch + Prometheus

### User Satisfaction

**Method:** Thumbs up/down after each interaction

**Targets:**
- Alpha: > 70% thumbs up
- Beta: > 80% thumbs up
- 1.0: > 90% thumbs up

---

## DEPLOYMENT

### GPU Requirements

**Alpha (1 GPU):**
- Instance: g5.2xlarge (1x A10G, 24GB VRAM)
- Models: STT (2GB) + LLM (10GB) + TTS (4GB) = 16GB
- Headroom: 8GB for batch processing
- Cost: ~$1.05/hour = ~$750/month (on-demand)
- Spot: ~$0.40/hour = ~$290/month (62% savings)

**Beta (2 GPUs):**
- Instances: 2x g5.2xlarge
- Split: GPU1 (STT + TTS), GPU2 (LLM + RAG)
- Cost: ~$1,500/month (on-demand), ~$580/month (Spot)

### Docker Containers

**voice-service:**
```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python 3.11
RUN apt-get update && apt-get install -y python3.11 python3-pip

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Faster-Whisper (CTranslate2)
RUN pip install faster-whisper

# Install XTTS v2
RUN pip install TTS

# Install vLLM for Llama 3.1
RUN pip install vllm

# Copy application
COPY app/ /app/
WORKDIR /app

# Expose port
EXPOSE 8003

# Run
CMD ["python", "main.py"]
```

**requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
faster-whisper==0.10.0
TTS==0.20.0
vllm==0.2.6
torch==2.1.0
torchaudio==2.1.0
transformers==4.35.0
pydantic==2.5.0
python-multipart==0.0.6
```

### ECS Task Definition

```json
{
  "family": "voice-service",
  "requiresCompatibilities": ["EC2"],
  "networkMode": "bridge",
  "containerDefinitions": [
    {
      "name": "voice-service",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/voice-service:latest",
      "memory": 20480,
      "cpu": 4096,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8003,
          "hostPort": 8003,
          "protocol": "tcp"
        }
      ],
      "resourceRequirements": [
        {
          "type": "GPU",
          "value": "1"
        }
      ],
      "environment": [
        {"name": "MODEL_STT", "value": "medium.en"},
        {"name": "MODEL_TTS", "value": "xtts_v2"},
        {"name": "MODEL_LLM", "value": "meta-llama/Llama-3.1-8B-Instruct"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/voice-service",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

---

## COST BREAKDOWN

### Alpha (Month 1-2)

**Compute:**
- 1x g5.2xlarge (Spot): ~$290/month
- Data transfer: ~$10/month
- **Total:** ~$300/month

**Storage:**
- Voice audio: 5k min/month × 3 MB/min = 15 GB
- S3 Standard (30 days): ~$0.35/month
- S3 IA (60 days): ~$0.20/month
- **Total:** ~$1/month

**Inference:**
- 5k voice minutes/month
- Cost per minute: ~$0.06 (GPU amortized)
- **Total:** Covered by compute

**Grand Total:** ~$301/month

### Beta (Month 3-6)

**Compute:**
- 2x g5.2xlarge (Spot): ~$580/month
- **Total:** ~$580/month

**Storage:**
- Voice audio: 50k min/month × 3 MB/min = 150 GB
- S3: ~$5/month
- **Total:** ~$5/month

**Fine-tuning (one-time):**
- STT: ~$1,500
- TTS: ~$2,000
- **Total:** ~$3,500

**Grand Total:** ~$585/month + $3,500 one-time

### 1.0 (Month 7+)

**Compute:**
- 4x g5.2xlarge (Spot): ~$1,160/month
- Auto-scaling (peak): +$500/month
- **Total:** ~$1,660/month

**Storage:**
- Voice audio: 500k min/month × 3 MB/min = 1.5 TB
- S3: ~$50/month
- **Total:** ~$50/month

**Grand Total:** ~$1,710/month

---

## ALTERNATIVES CONSIDERED

### STT Alternatives

| Model | WER | Latency | Cost | License |
|-------|-----|---------|------|---------|
| Faster-Whisper | 5-8% | 300ms | Self-host | MIT ✅ |
| OpenAI Whisper API | 5-8% | 500ms | $0.006/min | Proprietary |
| Wav2Vec2 | 8-12% | 200ms | Self-host | Apache 2.0 |
| Conformer | 4-6% | 400ms | Self-host | Apache 2.0 |

**Winner:** Faster-Whisper (best balance of accuracy, speed, cost, license)

### TTS Alternatives

| Model | MOS | Latency | Cost | License |
|-------|-----|---------|------|---------|
| XTTS v2 | 4.0 | 500ms | Self-host | MPL 2.0 ✅ |
| OpenAI TTS | 4.5 | 800ms | $15/1M chars | Proprietary |
| ElevenLabs | 4.7 | 600ms | $0.30/1k chars | Proprietary |
| Bark | 3.8 | 2000ms | Self-host | MIT |
| OpenVoice | 4.0 | 500ms | Self-host | MIT ✅ |

**Winner:** XTTS v2 (best balance of quality, speed, cost, features)

---

## RISKS & MITIGATIONS

### Risk: Latency > 2.5s

**Mitigation:**
- Streaming (start response in 1s)
- Model quantization (int8)
- GPU optimization (Flash Attention)
- Caching common queries

### Risk: Poor WER on scientific terms

**Mitigation:**
- Fine-tune Whisper on domain data
- Add scientific vocabulary to language model
- User feedback loop (correct transcripts)

### Risk: TTS sounds robotic

**Mitigation:**
- Fine-tune XTTS on professional voice actors
- Emotional control (pitch, speed, energy)
- A/B test multiple voices

### Risk: GPU costs explode

**Mitigation:**
- Use Spot instances (60% savings)
- Model quantization (2x throughput)
- Batch inference when traffic allows
- Auto-scaling (scale to zero at night)

---

## NEXT STEPS

### Week 1
- Deploy Faster-Whisper medium.en on g5.2xlarge
- Deploy XTTS v2 with 3 pre-configured voices
- Deploy Llama 3.1 8B via vLLM
- Test end-to-end latency

### Week 2
- Integrate with existing voice-service
- Add consent UI for data capture
- Set up S3 buckets with lifecycle
- Launch alpha with 10 beta testers

### Week 3-6
- Collect 200 hours voice data
- Label and augment dataset
- Build eval harness (WER, MOS, latency)

### Week 7-8
- Fine-tune Whisper on collected data
- A/B test base vs fine-tuned
- Deploy fine-tuned model if metrics improve

---

**Built with First Principles**  
**Status:** Ready to Deploy  
**Let's ship voice-to-voice.** 🎤

