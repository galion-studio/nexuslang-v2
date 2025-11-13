#!/usr/bin/env python3
"""
Seed script for Grokopedia knowledge base.
Populates the database with initial knowledge entries.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_db, init_db
from ..models.knowledge import KnowledgeEntry, KnowledgeGraph, RelationshipType
from ..services.grokopedia.search import get_search_engine


# Sample knowledge entries
SEED_ENTRIES = [
    {
        "title": "Artificial Intelligence",
        "summary": "A field of computer science focused on creating systems capable of performing tasks that typically require human intelligence.",
        "content": """Artificial Intelligence (AI) is a multidisciplinary field that encompasses computer science, mathematics, psychology, linguistics, and neuroscience. It focuses on creating systems that can perform tasks requiring human-like intelligence such as visual perception, speech recognition, decision-making, and language translation.

## Key Concepts

### Machine Learning
A subset of AI that enables systems to automatically learn and improve from experience without being explicitly programmed. Machine learning algorithms build mathematical models based on training data to make predictions or decisions.

### Deep Learning
A subset of machine learning that uses artificial neural networks with multiple layers (deep neural networks) to model complex patterns in data. Deep learning has revolutionized fields like computer vision, natural language processing, and speech recognition.

### Natural Language Processing (NLP)
The ability of computers to understand, interpret, and generate human language. Modern NLP systems use transformer architectures and large language models to achieve human-like language understanding.

## Applications

- **Healthcare**: Diagnostic assistance, drug discovery, personalized medicine
- **Finance**: Fraud detection, algorithmic trading, risk assessment
- **Transportation**: Autonomous vehicles, route optimization, predictive maintenance
- **Entertainment**: Content recommendation, game AI, creative tools

## Ethical Considerations

As AI systems become more powerful, important ethical questions arise:
- Privacy and data protection
- Algorithmic bias and fairness
- Job displacement and economic impact
- Autonomous weapons and military applications
- AI safety and alignment with human values

## Future Directions

The field continues to evolve rapidly with advances in:
- Multimodal AI (combining vision, language, and other modalities)
- Explainable AI (making AI decisions interpretable)
- AI safety and robustness
- Human-AI collaboration and augmentation""",
        "tags": ["artificial-intelligence", "machine-learning", "technology", "computer-science"],
        "verified": True
    },
    {
        "title": "Quantum Computing",
        "summary": "A revolutionary computing paradigm that uses quantum mechanics principles to perform calculations impossible on classical computers.",
        "content": """Quantum computing represents a fundamental shift from classical computing by harnessing the principles of quantum mechanics to perform computations that would be impossible or impractical on traditional computers.

## Core Principles

### Quantum Bits (Qubits)
Unlike classical bits that exist in states of 0 or 1, qubits can exist in superposition - simultaneously representing both 0 and 1. This property allows quantum computers to process vast amounts of data in parallel.

### Entanglement
A quantum phenomenon where particles become correlated such that the state of one particle instantly influences the state of another, regardless of distance. This property enables quantum computers to perform complex correlations.

### Quantum Interference
The ability to constructively or destructively interfere quantum states, allowing quantum algorithms to amplify correct solutions while suppressing incorrect ones.

## Quantum Algorithms

### Shor's Algorithm
A quantum algorithm for integer factorization that runs in polynomial time, threatening current cryptographic systems based on the difficulty of factoring large numbers.

### Grover's Algorithm
Provides a quadratic speedup for unstructured search problems, finding items in an unsorted database of N items in √N steps instead of N/2.

### Quantum Fourier Transform
The quantum analog of the classical Fourier transform, fundamental to many quantum algorithms including Shor's algorithm.

## Hardware Platforms

### Superconducting Qubits
Used by companies like IBM and Google, these systems operate at extremely low temperatures and use superconducting circuits to create and manipulate qubits.

### Trapped Ions
Developed by companies like IonQ and Honeywell, this approach uses individual ions suspended in electromagnetic fields as qubits, offering high fidelity but slower gate operations.

### Photonic Quantum Computing
Uses photons as qubits, leveraging existing optical fiber infrastructure for quantum communication and potentially quantum computing.

## Challenges

### Decoherence
Quantum states are extremely fragile and easily disrupted by environmental noise, requiring sophisticated error correction techniques.

### Scalability
Building large-scale quantum computers with thousands of qubits while maintaining coherence remains a significant engineering challenge.

### Error Correction
Quantum error correction codes are necessary to protect quantum information, but they require significant overhead in terms of physical qubits.

## Applications

- **Cryptography**: Breaking current encryption, enabling quantum-safe cryptography
- **Drug Discovery**: Simulating molecular interactions at quantum level
- **Optimization**: Solving complex optimization problems in logistics, finance, and materials science
- **Machine Learning**: Quantum machine learning algorithms with potential exponential speedups

## Current Status

While quantum computing is still in its early stages, significant progress has been made:
- Quantum supremacy demonstrations (performing tasks impossible on classical computers)
- Increasing qubit counts and coherence times
- Development of quantum software tools and programming languages
- Growing ecosystem of quantum hardware and software companies

The timeline for practical quantum advantage remains uncertain, but the field continues to advance rapidly with both academic and commercial investment.""",
        "tags": ["quantum-computing", "physics", "technology", "cryptography"],
        "verified": True
    },
    {
        "title": "Machine Learning",
        "summary": "A subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
        "content": """Machine Learning (ML) is a powerful approach to artificial intelligence that allows systems to automatically learn patterns and make decisions from data, without being explicitly programmed for each specific task.

## Learning Paradigms

### Supervised Learning
The most common ML approach where algorithms learn from labeled training data. The system is provided with input-output pairs and learns to map inputs to correct outputs.

**Common Algorithms:**
- Linear Regression: Predicting continuous values
- Logistic Regression: Binary classification
- Decision Trees: Hierarchical decision-making models
- Random Forests: Ensemble of decision trees
- Support Vector Machines: Maximum margin classifiers
- Neural Networks: Complex pattern recognition

### Unsupervised Learning
Algorithms discover hidden patterns in data without labeled examples. The system finds structure and relationships in the data itself.

**Common Techniques:**
- Clustering: Grouping similar data points (K-means, Hierarchical clustering)
- Dimensionality Reduction: Reducing data complexity (PCA, t-SNE)
- Association Rule Mining: Finding relationships between variables
- Anomaly Detection: Identifying unusual patterns

### Reinforcement Learning
Learning through interaction with an environment, receiving rewards or penalties for actions. The system learns optimal behavior through trial and error.

**Key Concepts:**
- Agent: The learning system
- Environment: The world the agent interacts with
- State: Current situation representation
- Action: Available choices
- Reward: Feedback signal
- Policy: Strategy for choosing actions

## Deep Learning

A subset of machine learning using artificial neural networks with multiple layers. Deep learning has revolutionized many fields due to its ability to automatically learn hierarchical features.

### Neural Network Components

- **Neurons**: Basic computational units that receive inputs, apply weights, and produce outputs
- **Layers**: Organized groups of neurons (input, hidden, output layers)
- **Activation Functions**: Non-linear transformations (ReLU, sigmoid, tanh)
- **Loss Functions**: Measures of prediction error
- **Optimizers**: Algorithms for updating network weights (SGD, Adam, RMSprop)

### Popular Architectures

- **Convolutional Neural Networks (CNNs)**: Excellent for image processing and computer vision
- **Recurrent Neural Networks (RNNs)**: Designed for sequential data like time series and text
- **Transformers**: Attention-based models revolutionizing natural language processing
- **Generative Adversarial Networks (GANs)**: Framework for generative modeling

## Model Evaluation

### Metrics
- **Accuracy**: Overall correctness of predictions
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under the receiver operating characteristic curve

### Validation Techniques
- **Train/Test Split**: Simple division of data
- **Cross-Validation**: Multiple train/test splits for robust evaluation
- **Holdout Validation**: Separate validation set for hyperparameter tuning

## Challenges and Best Practices

### Overfitting
When a model performs well on training data but poorly on new data. Solutions include:
- Regularization techniques (L1, L2)
- Dropout layers
- Early stopping
- Data augmentation

### Data Quality
- Garbage in, garbage out: ML models are only as good as their training data
- Data cleaning and preprocessing are crucial
- Bias in training data leads to biased models

### Computational Requirements
- Modern deep learning requires significant computational resources
- GPU acceleration is often necessary for training large models
- Cloud computing platforms provide accessible ML infrastructure

## Applications

### Computer Vision
- Image classification and object detection
- Facial recognition
- Medical image analysis
- Autonomous vehicles

### Natural Language Processing
- Text classification and sentiment analysis
- Machine translation
- Chatbots and virtual assistants
- Content generation

### Recommendation Systems
- Product recommendations
- Content personalization
- Social network suggestions

### Predictive Analytics
- Financial forecasting
- Demand prediction
- Risk assessment
- Healthcare diagnostics

## Future Directions

The field continues to evolve with:
- **AutoML**: Automated machine learning pipeline creation
- **Federated Learning**: Privacy-preserving distributed learning
- **Explainable AI**: Making ML models more interpretable
- **Edge ML**: Running ML models on resource-constrained devices
- **Multimodal Learning**: Combining different data types (text, images, audio)""",
        "tags": ["machine-learning", "artificial-intelligence", "data-science", "algorithms"],
        "verified": True
    },
    {
        "title": "Neural Networks",
        "summary": "Computing systems inspired by biological neural networks, capable of learning complex patterns through interconnected nodes.",
        "content": """Neural networks are computational models inspired by the structure and function of biological neural networks in the human brain. They form the foundation of deep learning and have revolutionized artificial intelligence.

## Biological Inspiration

### Neurons
The basic computational units that receive inputs from other neurons, process them, and produce outputs. Biological neurons communicate through electrical and chemical signals.

### Synapses
Connections between neurons that can be strengthened or weakened, forming the basis of learning and memory in biological systems.

### Neural Plasticity
The ability of neural connections to change strength over time, enabling learning and adaptation.

## Artificial Neural Networks

### Basic Structure
- **Input Layer**: Receives raw data
- **Hidden Layers**: Process and transform data through learned representations
- **Output Layer**: Produces final predictions or classifications

### Neuron Model
Each artificial neuron:
1. Receives inputs from previous layer neurons
2. Applies weights to each input
3. Sums weighted inputs
4. Applies activation function
5. Produces output for next layer

### Activation Functions
- **Sigmoid**: Maps to (0,1), used for binary classification
- **Tanh**: Maps to (-1,1), zero-centered alternative to sigmoid
- **ReLU**: Rectified Linear Unit, most popular for hidden layers
- **Softmax**: Converts to probability distribution for multi-class classification

## Training Process

### Forward Propagation
Data flows from input to output layer, producing predictions.

### Loss Function
Measures the difference between predictions and actual targets:
- Mean Squared Error (MSE) for regression
- Cross-Entropy Loss for classification

### Backpropagation
Algorithm for computing gradients of the loss function with respect to network weights, enabling weight updates.

### Gradient Descent
Optimization algorithm that updates weights to minimize loss:
- **Stochastic Gradient Descent (SGD)**: Updates weights using single examples
- **Mini-batch Gradient Descent**: Balances efficiency and stability
- **Adam**: Adaptive optimization combining momentum and RMSprop

## Network Architectures

### Feedforward Networks
Simplest architecture where information flows only forward, no cycles.

### Convolutional Neural Networks (CNNs)
Designed for grid-like data (images, time series):
- **Convolutional Layers**: Extract local features using filters
- **Pooling Layers**: Reduce spatial dimensions
- **Fully Connected Layers**: Classification from extracted features

### Recurrent Neural Networks (RNNs)
Process sequential data with internal memory:
- **Vanilla RNNs**: Basic recurrent connections
- **Long Short-Term Memory (LSTM)**: Addresses vanishing gradients
- **Gated Recurrent Units (GRUs)**: Simplified LSTM variant

### Transformer Networks
Attention-based architectures revolutionizing NLP:
- **Self-Attention**: Computes relationships between all positions
- **Multi-Head Attention**: Parallel attention computations
- **Positional Encoding**: Injects sequence order information

## Advanced Concepts

### Regularization
Techniques to prevent overfitting:
- **Dropout**: Randomly deactivates neurons during training
- **Batch Normalization**: Normalizes layer inputs
- **Weight Decay**: Penalizes large weights

### Transfer Learning
Using pre-trained models for new tasks, significantly reducing training time and data requirements.

### Generative Models
- **Autoencoders**: Learn efficient data representations
- **Variational Autoencoders (VAEs)**: Generate new data samples
- **Generative Adversarial Networks (GANs)**: Framework for generative modeling

## Implementation Considerations

### Hardware Acceleration
- **GPUs**: Parallel processing ideal for matrix operations
- **TPUs**: Specialized for neural network computations
- **Edge Devices**: Optimized for mobile and IoT applications

### Frameworks and Libraries
- **TensorFlow**: Comprehensive ML platform
- **PyTorch**: Dynamic computational graphs
- **JAX**: High-performance numerical computing
- **Keras**: High-level neural network API

## Applications

### Computer Vision
- Image classification and segmentation
- Object detection and recognition
- Facial recognition systems
- Medical image analysis

### Natural Language Processing
- Text classification and sentiment analysis
- Machine translation
- Question answering systems
- Language generation

### Speech Recognition
- Automatic speech recognition
- Speaker identification
- Speech synthesis
- Voice assistants

### Game Playing
- Game strategy and decision making
- Procedural content generation
- NPC behavior simulation

## Challenges and Limitations

### Interpretability
Neural networks often act as "black boxes," making it difficult to understand their decision-making processes.

### Data Requirements
Deep networks typically require large amounts of training data to achieve good performance.

### Computational Cost
Training large networks requires significant computational resources and energy.

### Adversarial Examples
Carefully crafted inputs can fool neural networks into making incorrect predictions.

## Future Directions

The field continues to advance with:
- **Neural Architecture Search**: Automated design of network architectures
- **Neural Symbolic Integration**: Combining neural networks with symbolic reasoning
- **Energy-Efficient Networks**: Reducing computational requirements
- **Brain-Inspired Computing**: Neuromorphic hardware and algorithms
- **Federated Learning**: Privacy-preserving distributed training""",
        "tags": ["neural-networks", "deep-learning", "artificial-intelligence", "machine-learning"],
        "verified": True
    },
    {
        "title": "Blockchain Technology",
        "summary": "A decentralized, distributed ledger technology that maintains a continuously growing list of records secured by cryptography.",
        "content": """Blockchain technology is a decentralized, distributed ledger system that maintains a continuously growing list of records (blocks) that are cryptographically linked and secured. It enables secure, transparent, and immutable transactions without requiring a central authority.

## Core Components

### Blocks
Containers that hold batches of valid transactions. Each block contains:
- **Block Header**: Metadata including previous block hash, timestamp, nonce
- **Transaction List**: Valid transactions included in the block
- **Merkle Root**: Cryptographic hash of all transactions in the block

### Chain Structure
Blocks are linked together in chronological order, forming an immutable chain. Each block references the hash of the previous block, creating a secure chronological sequence.

### Consensus Mechanisms
Protocols that ensure all network participants agree on the state of the blockchain:

#### Proof-of-Work (PoW)
- Used by Bitcoin and many other cryptocurrencies
- Miners compete to solve computational puzzles
- First to solve gets to add the next block
- Energy-intensive but proven security

#### Proof-of-Stake (PoS)
- Validators are chosen based on cryptocurrency holdings
- More energy-efficient than PoW
- Used by Ethereum 2.0, Cardano, and others

#### Other Mechanisms
- **Delegated Proof-of-Stake (DPoS)**: Stakeholders elect delegates
- **Proof-of-Authority (PoA)**: Approved validators create blocks
- **Proof-of-History (PoH)**: Uses verifiable delay functions

## Cryptographic Foundations

### Hash Functions
One-way mathematical functions that convert input data into fixed-size strings:
- **SHA-256**: Used by Bitcoin
- **Keccak-256**: Used by Ethereum
- Properties: Deterministic, quick to compute, computationally infeasible to reverse

### Public-Key Cryptography
Asymmetric encryption enabling secure transactions:
- **Public Keys**: Freely shared addresses
- **Private Keys**: Secret keys for signing transactions
- **Digital Signatures**: Prove transaction authenticity

### Merkle Trees
Binary tree structures for efficient data verification:
- Leaves contain transaction hashes
- Parent nodes contain hashes of child nodes
- Root hash represents entire transaction set
- Enables efficient verification of transaction inclusion

## Smart Contracts

Self-executing contracts with terms directly written into code:
- **Ethereum Virtual Machine (EVM)**: Runtime environment for smart contracts
- **Turing Complete**: Can execute any computable function
- **Decentralized Applications (dApps)**: Applications built on blockchain networks

### Programming Languages
- **Solidity**: Primary language for Ethereum smart contracts
- **Vyper**: Python-like language for Ethereum
- **Rust**: Used by Polkadot and other Substrate-based chains
- **Move**: Used by Diem (formerly Libra)

## Applications Beyond Cryptocurrency

### Decentralized Finance (DeFi)
- **Decentralized Exchanges (DEXs)**: Peer-to-peer trading without intermediaries
- **Lending Protocols**: Algorithmic lending and borrowing
- **Stablecoins**: Cryptocurrencies pegged to stable assets
- **Yield Farming**: Earning rewards by providing liquidity

### Supply Chain Management
- **Product Tracking**: End-to-end supply chain visibility
- **Authenticity Verification**: Preventing counterfeiting
- **Quality Control**: Automated compliance checking

### Healthcare
- **Medical Records**: Secure, interoperable patient data
- **Drug Traceability**: Preventing counterfeit medications
- **Clinical Trials**: Transparent, tamper-proof trial data

### Identity Management
- **Self-Sovereign Identity**: User-controlled digital identities
- **Decentralized Identifiers (DIDs)**: Blockchain-based identity systems
- **Verifiable Credentials**: Cryptographically verifiable claims

### Voting Systems
- **Election Integrity**: Transparent, tamper-proof voting
- **Voter Privacy**: Maintaining anonymity while ensuring validity
- **Cross-Border Voting**: Enabling secure international elections

## Scalability Challenges

### Transaction Throughput
Current blockchain networks process fewer transactions per second than traditional systems:
- **Bitcoin**: ~7 TPS
- **Ethereum**: ~15-45 TPS (depending on network conditions)
- **Traditional Systems**: Thousands to millions TPS

### Solutions
- **Layer 2 Scaling**: Off-chain transaction processing
- **Sharding**: Parallel processing of transactions
- **Sidechains**: Independent chains pegged to main chain
- **State Channels**: Off-chain transaction channels

## Privacy and Security

### Privacy Concerns
- **Public Ledgers**: All transactions are visible to everyone
- **Address Linking**: Transaction patterns can reveal identities
- **Metadata Leakage**: Information leaked through transaction details

### Privacy Solutions
- **Zero-Knowledge Proofs**: Prove statements without revealing data
- **Mixing Services**: Break transaction linkability
- **Confidential Transactions**: Hide transaction amounts
- **Privacy Coins**: Built-in privacy features (Monero, Zcash)

### Security Considerations
- **51% Attacks**: Controlling majority of network hash power
- **Smart Contract Vulnerabilities**: Code exploits and bugs
- **Private Key Security**: Protecting access to funds
- **Oracle Problems**: Secure integration with external data

## Interoperability

### Cross-Chain Communication
- **Atomic Swaps**: Trustless exchange between different blockchains
- **Wrapped Tokens**: Assets from one chain represented on another
- **Blockchain Bridges**: Connect disparate blockchain networks

### Standards and Protocols
- **Inter-Blockchain Communication (IBC)**: Cosmos ecosystem standard
- **Polkadot Parachains**: Interconnected parallel chains
- **Cross-Chain Transaction Protocol**: Standardized interoperability

## Regulatory Landscape

### Current Status
- **United States**: Securities and Exchange Commission (SEC) oversight
- **European Union**: Markets in Crypto-Assets (MiCA) regulation
- **China**: Strict cryptocurrency mining and trading restrictions
- **El Salvador**: Bitcoin as legal tender

### Key Regulatory Themes
- **Consumer Protection**: Preventing fraud and market manipulation
- **Anti-Money Laundering (AML)**: Combating illicit finance
- **Know Your Customer (KYC)**: Identity verification requirements
- **Tax Compliance**: Reporting and taxation of crypto transactions

## Environmental Impact

### Energy Consumption
- **Proof-of-Work Mining**: Significant electricity usage
- **Renewable Energy**: Growing adoption of green mining
- **Energy Efficiency**: Proof-of-Stake and other alternatives

### Carbon Footprint
- **Bitcoin Network**: Annual energy consumption comparable to countries
- **Sustainable Mining**: Transition to renewable energy sources
- **Hardware Efficiency**: More efficient mining equipment

## Future Developments

### Web3 Ecosystem
- **Decentralized Internet**: Moving beyond centralized web services
- **Token Economics**: Incentive mechanisms for network participation
- **Decentralized Autonomous Organizations (DAOs)**: Blockchain-based governance

### Enterprise Adoption
- **Private Blockchains**: Permissioned networks for businesses
- **Consortium Chains**: Multi-party governance models
- **Hybrid Solutions**: Combining public and private elements

### Technological Advancements
- **Layer 1 Improvements**: Enhanced base layer protocols
- **Quantum Resistance**: Preparing for quantum computing threats
- **Interoperability Standards**: Seamless cross-chain interactions
- **Sustainability**: Environmentally friendly consensus mechanisms

## Challenges and Limitations

### Technical Challenges
- **Scalability Trilemma**: Balancing decentralization, security, and scalability
- **User Experience**: Complex key management and transaction processes
- **Regulatory Uncertainty**: Evolving legal and compliance requirements

### Adoption Barriers
- **Volatility**: Cryptocurrency price fluctuations
- **Complexity**: Steep learning curve for users and developers
- **Integration**: Connecting blockchain with existing systems

### Social and Economic Factors
- **Inequality**: Concentration of wealth and power
- **Financial Inclusion**: Potential to democratize finance
- **Job Displacement**: Automation of traditional financial roles

Blockchain technology continues to evolve rapidly, with new applications and improvements emerging regularly. While challenges remain, the technology's potential to create more transparent, secure, and decentralized systems continues to drive innovation across industries.""",
        "tags": ["blockchain", "cryptocurrency", "distributed-systems", "cryptography"],
        "verified": True
    }
]


async def seed_knowledge_entries(db: AsyncSession):
    """Seed the knowledge base with initial entries."""
    search_engine = get_search_engine()

    for entry_data in SEED_ENTRIES:
        # Check if entry already exists
        result = await db.execute(
            select(KnowledgeEntry).where(KnowledgeEntry.title == entry_data["title"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Entry '{entry_data['title']}' already exists, skipping...")
            continue

        # Create embedding for the entry
        embedding_text = f"{entry_data['title']}\n\n{entry_data['summary']}\n\n{entry_data['content']}"
        try:
            embedding = await search_engine.create_embedding(embedding_text)
        except Exception as e:
            print(f"Failed to create embedding for '{entry_data['title']}': {e}")
            continue

        # Generate slug
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', entry_data['title'].lower()).strip('-')

        # Ensure unique slug
        counter = 1
        original_slug = slug
        while True:
            result = await db.execute(
                select(KnowledgeEntry).where(KnowledgeEntry.slug == slug)
            )
            if not result.scalar_one_or_none():
                break
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Create the entry
        entry = KnowledgeEntry(
            title=entry_data["title"],
            slug=slug,
            summary=entry_data["summary"],
            content=entry_data["content"],
            embeddings=embedding,
            tags=entry_data["tags"],
            verified=entry_data["verified"],
            views_count=0,
            upvotes_count=0
            # created_by will be None for seed data
        )

        db.add(entry)
        print(f"Created entry: {entry_data['title']}")

    await db.commit()
    print("Knowledge base seeding completed!")


async def main():
    """Main seeding function."""
    print("Initializing database...")
    await init_db()

    print("Seeding knowledge base...")
    async for db in get_db():
        try:
            await seed_knowledge_entries(db)
            break
        except Exception as e:
            print(f"Seeding failed: {e}")
            raise
        finally:
            await db.close()

    print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
