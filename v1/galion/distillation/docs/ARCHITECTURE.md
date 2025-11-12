# Nexus Core Model Architecture

## Overview

This document describes the architectural differences between the base Nexus Core model and its distilled versions.

---

## Base Model Architecture (500GB)

### Transformer Configuration

```yaml
Model: Nexus-Core-500GB
Architecture: Transformer (Decoder-only)
Total Parameters: 405 Billion
Model Size: 500GB (FP32)

Layers: 96
Hidden Size: 8192
Attention Heads: 128
Head Dimension: 64
Intermediate Size (FFN): 32768
Vocabulary Size: 128000
Max Sequence Length: 128000 tokens
Position Embeddings: RoPE (Rotary Position Embedding)
Activation Function: SwiGLU
Normalization: RMSNorm
```

### Layer Structure

```
Input → Token Embedding → Position Embedding
  ↓
[Repeat 96 times:]
  ↓
  RMSNorm
  ↓
  Multi-Head Attention (128 heads)
    - Query, Key, Value projections
    - Rotary Position Embeddings
    - Grouped Query Attention (GQA)
    - Causal masking
  ↓
  Residual Connection
  ↓
  RMSNorm
  ↓
  Feed-Forward Network (SwiGLU)
    - Gate projection (8192 → 32768)
    - Up projection (8192 → 32768)
    - Down projection (32768 → 8192)
  ↓
  Residual Connection
  ↓
[End Repeat]
  ↓
  RMSNorm
  ↓
  Output Projection (8192 → 128000)
  ↓
Output Logits
```

### Memory Breakdown

```
Token Embeddings:     128000 × 8192 × 4 bytes  = 4.2 GB
Positional Encoding:  Computed on-the-fly      = 0 GB
96 Transformer Layers:                         = 486 GB
  - Attention weights:  96 × 100 MB            = 9.6 GB per layer
  - FFN weights:        96 × 400 MB            = 38.4 GB per layer
Output Layer:         128000 × 8192 × 4 bytes  = 4.2 GB
Optimizer States:     2× parameters            = 500 GB
Total Training:       ~1.5 TB
Total Inference:      ~500 GB
```

---

## Standard Model Architecture (16GB)

### Transformer Configuration

```yaml
Model: Nexus-Core-Standard-16GB
Architecture: Transformer (Decoder-only)
Total Parameters: 13 Billion
Model Size: 16GB (INT8 Mixed)

Layers: 32 (Reduced from 96)
Hidden Size: 2048 (Reduced from 8192)
Attention Heads: 32 (Reduced from 128)
Head Dimension: 64 (Same)
Intermediate Size (FFN): 8192 (Reduced from 32768)
Vocabulary Size: 50000 (Reduced from 128000)
Max Sequence Length: 8192 tokens (Reduced from 128K)
Position Embeddings: RoPE (Same)
Activation Function: SwiGLU (Same)
Normalization: RMSNorm (Same)
```

### Distillation Strategy

#### Layer Reduction
```python
# Base model: 96 layers → Standard: 32 layers
# Strategy: Keep every 3rd layer from base model

selected_layers = []
for i in range(0, 96, 3):
    layer = base_model.layers[i]
    selected_layers.append(layer)
    
# Further compress from 32 layers to final 32
# by merging adjacent layers
```

#### Hidden Dimension Reduction
```python
# 8192 → 2048 (75% reduction)
# Use PCA or learned projection

projection_matrix = learn_projection(
    input_dim=8192,
    output_dim=2048,
    data=training_data
)

new_weights = old_weights @ projection_matrix
```

#### Attention Head Pruning
```python
# 128 → 32 heads (75% reduction)
# Keep most important heads based on attention entropy

head_importance = calculate_head_importance(
    model=base_model,
    data=validation_data
)

top_heads = select_top_k_heads(head_importance, k=32)
pruned_attention = prune_heads(base_model.attention, top_heads)
```

### Memory Optimization

```
Token Embeddings:     50000 × 2048 × 1 byte   = 100 MB
Positional Encoding:  Computed on-the-fly     = 0 MB
32 Transformer Layers:                        = 14.8 GB
  - Attention (INT8):   32 × 150 MB           = 4.8 GB
  - FFN (INT8):         32 × 300 MB           = 9.6 GB
  - LayerNorm (FP16):   32 × 8 MB             = 256 MB
Output Layer:         50000 × 2048 × 1 byte   = 100 MB
KV Cache (8K ctx):    32 × 2048 × 8192 × 2    = 1 GB
Total Inference:      ~16 GB
```

---

## Nano Model Architecture (4GB)

### Transformer Configuration

```yaml
Model: Nexus-Core-Nano-4GB
Architecture: Transformer (Decoder-only)
Total Parameters: 1.5 Billion
Model Size: 4GB (INT8)

Layers: 12 (Reduced from 96)
Hidden Size: 768 (Reduced from 8192)
Attention Heads: 12 (Reduced from 128)
Head Dimension: 64 (Same)
Intermediate Size (FFN): 3072 (Reduced from 32768)
Vocabulary Size: 32000 (Reduced from 128000)
Max Sequence Length: 2048 tokens (Reduced from 128K)
Position Embeddings: RoPE (Same)
Activation Function: SwiGLU (Same)
Normalization: RMSNorm (Same)
```

### Distillation Strategy

#### Aggressive Layer Reduction
```python
# Base model: 96 layers → Nano: 12 layers
# Strategy: Keep every 8th layer

selected_layers = [base_model.layers[i] for i in range(0, 96, 8)]
```

#### Extreme Dimension Reduction
```python
# 8192 → 768 (90% reduction)
# Use knowledge distillation + autoencoder

autoencoder = train_autoencoder(
    encoder_input=8192,
    latent_dim=768,
    decoder_output=8192,
    data=training_data
)

compressed_weights = autoencoder.encoder(original_weights)
```

#### Vocabulary Reduction
```python
# 128K → 32K tokens
# Keep most frequent tokens + subword merging

token_freq = count_token_frequency(training_data)
top_tokens = select_top_k_tokens(token_freq, k=32000)

# Merge rare tokens using BPE
bpe_merges = learn_bpe_merges(top_tokens, num_merges=5000)
```

### Memory Optimization

```
Token Embeddings:     32000 × 768 × 1 byte    = 25 MB
Positional Encoding:  Computed on-the-fly     = 0 MB
12 Transformer Layers:                        = 3.8 GB
  - Attention (INT8):   12 × 100 MB           = 1.2 GB
  - FFN (INT8):         12 × 200 MB           = 2.4 GB
  - LayerNorm (FP16):   12 × 6 MB             = 72 MB
Output Layer:         32000 × 768 × 1 byte    = 25 MB
KV Cache (2K ctx):    12 × 768 × 2048 × 2     = 150 MB
Total Inference:      ~4 GB
```

---

## Architectural Comparisons

### Parameter Count Comparison

| Component | Base (500GB) | Standard (16GB) | Nano (4GB) |
|-----------|--------------|-----------------|------------|
| Layers | 96 | 32 | 12 |
| Hidden Size | 8192 | 2048 | 768 |
| Attention Heads | 128 | 32 | 12 |
| FFN Size | 32768 | 8192 | 3072 |
| Vocab Size | 128K | 50K | 32K |
| **Total Params** | **405B** | **13B** | **1.5B** |
| **Reduction** | **0%** | **96.8%** | **99.6%** |

### Context Length Comparison

| Model | Max Context | KV Cache Size | Use Case |
|-------|-------------|---------------|----------|
| Base | 128K tokens | ~100 GB | Long documents, books |
| Standard | 8K tokens | ~1 GB | Articles, conversations |
| Nano | 2K tokens | ~150 MB | Chatbots, quick Q&A |

### Inference Speed Comparison

| Model | Hardware | Tokens/Sec | Latency (128 tok) | Throughput |
|-------|----------|------------|-------------------|------------|
| Base | 8× A100 80GB | 20 | 6400ms | 10 req/min |
| Standard | 1× A100 40GB | 100 | 1280ms | 100 req/min |
| Nano | 1× RTX 3060 | 50 | 2560ms | 500 req/min |

---

## Key Design Decisions

### 1. Decoder-Only Architecture
**Why?** Simpler than encoder-decoder, better for generation tasks.

### 2. Rotary Position Embeddings (RoPE)
**Why?** Better extrapolation to longer sequences than learned embeddings.

### 3. SwiGLU Activation
**Why?** Better performance than ReLU/GELU in language models.

### 4. RMSNorm Instead of LayerNorm
**Why?** Faster computation, similar performance.

### 5. Grouped Query Attention (GQA)
**Why?** Reduces KV cache size while maintaining quality.

### 6. INT8 Quantization
**Why?** 4× memory reduction with minimal accuracy loss.

---

## Advanced Features

### 1. Flash Attention
```python
# Optimized attention implementation
# O(N) memory instead of O(N²)

def flash_attention(Q, K, V, block_size=1024):
    seq_len = Q.shape[1]
    output = torch.zeros_like(Q)
    
    for i in range(0, seq_len, block_size):
        q_block = Q[:, i:i+block_size]
        
        for j in range(0, seq_len, block_size):
            k_block = K[:, j:j+block_size]
            v_block = V[:, j:j+block_size]
            
            scores = q_block @ k_block.transpose(-2, -1)
            attn = F.softmax(scores / sqrt(d_k), dim=-1)
            output[:, i:i+block_size] += attn @ v_block
    
    return output
```

### 2. Gradient Checkpointing
```python
# Trade compute for memory
# Recompute activations during backward pass

class TransformerLayer(nn.Module):
    def forward(self, x):
        if self.training and self.gradient_checkpointing:
            return checkpoint(self._forward, x)
        else:
            return self._forward(x)
    
    def _forward(self, x):
        x = x + self.attention(self.norm1(x))
        x = x + self.ffn(self.norm2(x))
        return x
```

### 3. Dynamic Batching
```python
# Batch requests of similar length for efficiency

def dynamic_batch(requests, max_batch_size=32):
    # Sort by sequence length
    requests.sort(key=lambda r: len(r.tokens))
    
    batches = []
    current_batch = []
    current_length = 0
    
    for req in requests:
        if len(current_batch) >= max_batch_size or \
           (current_length > 0 and req.length > current_length * 1.2):
            batches.append(current_batch)
            current_batch = []
            current_length = 0
        
        current_batch.append(req)
        current_length = max(current_length, req.length)
    
    if current_batch:
        batches.append(current_batch)
    
    return batches
```

### 4. Speculative Decoding
```python
# Use small model to draft, large model to verify

def speculative_decode(prompt, draft_model, target_model, k=5):
    # Draft k tokens with small model
    draft_tokens = draft_model.generate(prompt, max_tokens=k)
    
    # Verify in parallel with large model
    verified_tokens = []
    for i, token in enumerate(draft_tokens):
        prob = target_model.get_prob(prompt + draft_tokens[:i], token)
        if prob > threshold:
            verified_tokens.append(token)
        else:
            # Reject and resample
            corrected = target_model.sample(prompt + verified_tokens)
            verified_tokens.append(corrected)
            break
    
    return verified_tokens
```

---

## Implementation Details

### Initialization

```python
# Xavier/Glorot initialization for stability
def init_weights(module):
    if isinstance(module, nn.Linear):
        torch.nn.init.xavier_uniform_(module.weight)
        if module.bias is not None:
            torch.nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Embedding):
        torch.nn.init.normal_(module.weight, mean=0, std=0.02)
```

### Training Stability

```python
# Gradient clipping
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# Warmup learning rate
def get_lr(step, warmup_steps, max_lr):
    if step < warmup_steps:
        return max_lr * step / warmup_steps
    else:
        return max_lr * 0.5 * (1 + cos(pi * (step - warmup_steps) / 
                                        (total_steps - warmup_steps)))
```

### Memory Management

```python
# Clear cache between batches
torch.cuda.empty_cache()

# Use gradient accumulation
for i, batch in enumerate(dataloader):
    loss = model(batch) / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

---

## Future Improvements

### Planned Features

1. **Mixture of Experts (MoE)**
   - Sparse activation for efficiency
   - 8 experts, activate top-2 per token
   - Target: 4× model capacity with same compute

2. **Multi-Query Attention (MQA)**
   - Share K/V across heads
   - Reduce KV cache by 32×
   - Target: 8× faster generation

3. **Sliding Window Attention**
   - Local + global attention
   - Process 32K context in 4GB
   - Target: 4× longer context

4. **4-bit Quantization (NF4)**
   - Further compression
   - Target: 2GB nano model
   - Maintain 80%+ accuracy

---

## References

- **Attention Is All You Need**: Original Transformer paper
- **LLaMA**: Architecture inspiration
- **DistilBERT**: Knowledge distillation techniques
- **GPT-3**: Scaling laws and architecture
- **FlashAttention**: Optimized attention implementation

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Maintained By**: Nexus Core Team

