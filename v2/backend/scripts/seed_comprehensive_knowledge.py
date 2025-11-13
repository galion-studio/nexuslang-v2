#!/usr/bin/env python3
"""
Comprehensive Human Knowledge Seeding Script for Grokopedia
Seeds the knowledge base with extensive foundational human knowledge across all domains
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select

from core.database import get_db
from models.knowledge import KnowledgeEntry
from services.grokopedia.search import SemanticSearch
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive knowledge base covering all major domains of human knowledge
COMPREHENSIVE_KNOWLEDGE = [
    # MATHEMATICS
    {
        "title": "Mathematics",
        "content": """Mathematics is the abstract science of number, quantity, and space, either as abstract concepts or as applied to other disciplines such as physics and engineering. It involves the study of such topics as quantity (number theory), structure (algebra), space (geometry), and change (mathematical analysis).

The development of mathematics can be divided into several periods:
1. Ancient mathematics (before 500 BCE)
2. Classical mathematics (500 BCE - 500 CE)
3. Medieval mathematics (500 - 1500 CE)
4. Early modern mathematics (1500 - 1800 CE)
5. Modern mathematics (1800 CE - present)

Key branches include:
- Arithmetic: Study of numbers and basic operations
- Algebra: Study of mathematical symbols and rules for manipulating them
- Geometry: Study of shapes, sizes, and positions
- Calculus: Study of rates of change and accumulation
- Statistics: Study of data collection, analysis, and interpretation
- Topology: Study of spatial properties that are preserved under continuous deformations
- Number Theory: Study of integers and their properties

Mathematics serves as the foundation for all scientific disciplines and many areas of modern technology.""",
        "tags": ["mathematics", "science", "logic", "abstract", "quantitative"],
        "verified": True
    },
    {
        "title": "Calculus",
        "content": """Calculus is a branch of mathematics focused on limits, functions, derivatives, integrals, and infinite series. It was independently developed by Isaac Newton and Gottfried Wilhelm Leibniz in the late 17th century.

**Differential Calculus:**
- Studies rates of change and slopes of curves
- Introduces the concept of derivatives
- Applications: velocity, acceleration, optimization

**Integral Calculus:**
- Studies accumulation of quantities
- Introduces the concept of integrals
- Applications: areas, volumes, work done

**Fundamental Theorem of Calculus:**
Establishes the relationship between differentiation and integration, showing that they are inverse operations.

**Key Concepts:**
- Limits: Foundation of calculus, describe behavior near a point
- Continuity: Function values approach each other as inputs approach each other
- Derivatives: Instantaneous rate of change
- Integrals: Accumulation of infinitesimal quantities

**Applications:**
- Physics: motion, forces, energy
- Engineering: design optimization, signal processing
- Economics: marginal analysis, growth models
- Biology: population dynamics, drug concentration""",
        "tags": ["calculus", "mathematics", "derivatives", "integrals", "analysis"],
        "verified": True
    },
    {
        "title": "Number Theory",
        "content": """Number Theory is a branch of pure mathematics devoted to the study of integers and integer-valued functions. It studies properties of integers such as divisibility, prime numbers, and Diophantine equations.

**Prime Numbers:**
- Integers greater than 1 with no positive divisors other than 1 and themselves
- Fundamental building blocks of all integers
- Distribution described by the Prime Number Theorem

**Modular Arithmetic:**
- Arithmetic modulo n (remainder when divided by n)
- Forms a finite field when n is prime
- Applications in cryptography and computer science

**Diophantine Equations:**
- Polynomial equations with integer solutions
- Famous examples: Fermat's Last Theorem, Pell equations

**Key Theorems:**
- Euclid's Theorem: Infinitely many prime numbers
- Fundamental Theorem of Arithmetic: Unique prime factorization
- Chinese Remainder Theorem: Solving systems of congruences

**Modern Applications:**
- Cryptography: RSA algorithm, elliptic curve cryptography
- Computer Science: Hash functions, error-correcting codes
- Internet Security: SSL/TLS protocols""",
        "tags": ["number theory", "mathematics", "primes", "cryptography", "pure mathematics"],
        "verified": True
    },

    # PHYSICS
    {
        "title": "Physics",
        "content": """Physics is the natural science that studies matter, its motion and behavior through space and time, and the related entities of energy and force. It is the foundation of all other natural sciences and engineering disciplines.

**Classical Physics:**
- Mechanics: Study of motion and forces
- Thermodynamics: Study of heat and energy transfer
- Electromagnetism: Study of electric and magnetic fields
- Optics: Study of light and its interactions

**Modern Physics:**
- Quantum Mechanics: Study of matter at atomic and subatomic scales
- Relativity: Study of space, time, and gravity
- Particle Physics: Study of fundamental particles and forces
- Condensed Matter Physics: Study of macroscopic physical properties

**Fundamental Forces:**
1. Gravity: Attractive force between masses
2. Electromagnetism: Force between charged particles
3. Strong Nuclear Force: Binds protons and neutrons in nuclei
4. Weak Nuclear Force: Responsible for radioactive decay

**Key Principles:**
- Conservation Laws: Energy, momentum, angular momentum, charge
- Symmetry Principles: Underlie conservation laws
- Uncertainty Principle: Fundamental limit on measurement precision
- Equivalence Principle: Gravity and acceleration are indistinguishable

**Applications:**
- Technology: Computers, lasers, medical imaging
- Engineering: Structural analysis, materials science
- Astronomy: Understanding celestial bodies and phenomena
- Medicine: Radiation therapy, diagnostic imaging""",
        "tags": ["physics", "science", "natural science", "matter", "energy", "forces"],
        "verified": True
    },
    {
        "title": "Quantum Mechanics",
        "content": """Quantum Mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles. It forms the foundation of modern physics and quantum chemistry.

**Wave-Particle Duality:**
- Particles exhibit both particle-like and wave-like behavior
- Demonstrated by the double-slit experiment
- Matter waves described by the de Broglie wavelength

**Uncertainty Principle:**
- Impossible to simultaneously know position and momentum precisely
- Fundamental limit on measurement accuracy
- Heisenberg's uncertainty relations

**Quantum States and Superposition:**
- Quantum systems exist in superposition of multiple states
- Wave function describes probability amplitudes
- Measurement causes wave function collapse

**Key Phenomena:**
- Tunneling: Particles can pass through potential barriers
- Entanglement: Quantum states of particles become correlated
- Quantization: Energy levels are discrete, not continuous
- Spin: Intrinsic angular momentum of particles

**Mathematical Framework:**
- Hilbert spaces for quantum states
- Operators representing physical observables
- Commutators and non-commuting observables
- Schrödinger equation for time evolution

**Applications:**
- Semiconductors and transistors
- Lasers and quantum optics
- Magnetic resonance imaging (MRI)
- Quantum computing and cryptography""",
        "tags": ["quantum mechanics", "physics", "modern physics", "uncertainty principle", "superposition"],
        "verified": True
    },
    {
        "title": "General Relativity",
        "content": """General Relativity is Einstein's theory of gravity, published in 1915. It describes gravity as the curvature of spacetime caused by mass and energy, replacing Newton's theory of universal gravitation.

**Equivalence Principle:**
- Gravitational and inertial mass are equivalent
- Free fall and inertial motion are indistinguishable
- Basis for the geometric interpretation of gravity

**Spacetime Curvature:**
- Mass and energy curve the fabric of spacetime
- Motion follows geodesics (straight lines in curved space)
- Gravity is not a force but geometry

**Key Predictions:**
- Time dilation: Moving clocks run slow, gravitational time dilation
- Length contraction: Space contraction in moving frames
- Black holes: Regions where gravity is so strong that nothing can escape
- Gravitational waves: Ripples in spacetime propagating at light speed

**Experimental Verification:**
- Perihelion precession of Mercury
- Gravitational redshift of light
- Deflection of light by massive objects
- Time dilation measurements with atomic clocks

**Cosmological Implications:**
- Expanding universe (Hubble's law)
- Big Bang theory of cosmic origins
- Cosmic microwave background radiation
- Dark matter and dark energy

**Applications:**
- GPS satellite corrections for time dilation
- Gravitational wave detection (LIGO)
- Black hole imaging (Event Horizon Telescope)
- Cosmological models and predictions""",
        "tags": ["general relativity", "physics", "einstein", "gravity", "spacetime", "cosmology"],
        "verified": True
    },

    # COMPUTER SCIENCE
    {
        "title": "Computer Science",
        "content": """Computer Science is the study of computation, automation, and information. It encompasses both theoretical and practical aspects of computing, including algorithms, data structures, programming languages, and computer systems.

**Theoretical Computer Science:**
- Algorithms: Step-by-step procedures for calculations
- Computational complexity: Study of algorithm efficiency
- Automata theory: Abstract machines and computation models
- Formal languages: Mathematical models of programming languages

**Computer Systems:**
- Computer architecture: Hardware design and organization
- Operating systems: Software that manages computer resources
- Networks: Communication protocols and distributed systems
- Databases: Data storage, retrieval, and management

**Software Engineering:**
- Software development methodologies (Agile, Waterfall)
- Programming paradigms (object-oriented, functional, procedural)
- Code quality and testing
- Software architecture and design patterns

**Artificial Intelligence and Machine Learning:**
- Neural networks and deep learning
- Natural language processing
- Computer vision and image recognition
- Robotics and autonomous systems

**Key Concepts:**
- Abstraction: Managing complexity through layered design
- Modularity: Breaking systems into manageable components
- Algorithms: Efficient solutions to computational problems
- Data structures: Organization of data for efficient access
- Parallel computing: Simultaneous execution of computations

**Applications:**
- Internet and web technologies
- Mobile computing and apps
- Cloud computing and distributed systems
- Cybersecurity and information protection
- Scientific computing and simulation""",
        "tags": ["computer science", "computing", "algorithms", "programming", "software"],
        "verified": True
    },
    {
        "title": "Artificial Intelligence",
        "content": """Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, problem-solving, perception, and language understanding.

**Machine Learning:**
- Supervised learning: Training with labeled data
- Unsupervised learning: Finding patterns in unlabeled data
- Reinforcement learning: Learning through interaction and rewards
- Deep learning: Neural networks with multiple layers

**Natural Language Processing (NLP):**
- Text analysis and understanding
- Machine translation
- Sentiment analysis
- Conversational AI and chatbots

**Computer Vision:**
- Image recognition and classification
- Object detection and tracking
- Image generation and manipulation
- Medical image analysis

**Expert Systems:**
- Knowledge representation and reasoning
- Rule-based systems
- Decision support systems
- Diagnostic and recommendation systems

**AI Ethics and Safety:**
- Bias and fairness in AI systems
- Transparency and explainability
- Privacy and data protection
- AI alignment with human values

**Applications:**
- Autonomous vehicles and robotics
- Healthcare diagnostics and treatment
- Financial trading and risk assessment
- Recommendation systems and personalization
- Scientific research and discovery

**Current Challenges:**
- General AI (AGI) development
- AI safety and alignment
- Computational resource requirements
- Interpretability and trust
- Societal impact and regulation""",
        "tags": ["artificial intelligence", "AI", "machine learning", "neural networks", "automation"],
        "verified": True
    },
    {
        "title": "Algorithms",
        "content": """Algorithms are finite sequences of well-defined instructions for solving computational problems or performing calculations. They form the foundation of computer science and software development.

**Algorithm Analysis:**
- Time complexity: How execution time scales with input size
- Space complexity: Memory usage as function of input size
- Big O notation: Asymptotic upper bounds
- Best, worst, and average case analysis

**Fundamental Algorithms:**
- Sorting: Bubble sort, quicksort, mergesort, heapsort
- Searching: Binary search, linear search, hash tables
- Graph algorithms: Dijkstra, Bellman-Ford, Floyd-Warshall
- Dynamic programming: Knapsack, longest common subsequence
- Greedy algorithms: Minimum spanning tree, Huffman coding

**Data Structures:**
- Arrays: Fixed-size, contiguous memory
- Linked lists: Dynamic, node-based structures
- Stacks and queues: LIFO and FIFO structures
- Trees: Hierarchical data organization
- Hash tables: Key-value mapping with O(1) average access
- Heaps: Priority queue implementations

**Algorithm Design Paradigms:**
- Divide and conquer: Break problems into subproblems
- Dynamic programming: Optimal substructure and overlapping subproblems
- Greedy algorithms: Locally optimal choices
- Backtracking: Systematic search with pruning
- Branch and bound: Optimization with bounds

**Computational Complexity:**
- P vs NP problem: Fundamental unsolved question
- NP-complete problems: Computationally difficult
- Approximation algorithms: Near-optimal solutions
- Randomized algorithms: Using probability for efficiency

**Applications:**
- Database query optimization
- Network routing protocols
- Cryptographic systems
- Machine learning model training
- Real-time system scheduling""",
        "tags": ["algorithms", "computer science", "complexity", "data structures", "efficiency"],
        "verified": True
    },

    # BIOLOGY
    {
        "title": "Biology",
        "content": """Biology is the scientific study of life and living organisms. It encompasses everything from molecular processes within cells to interactions between organisms and their environment.

**Molecular Biology:**
- DNA, RNA, and protein synthesis
- Gene expression and regulation
- Cellular metabolism and energy production
- Molecular genetics and heredity

**Cellular Biology:**
- Cell structure and organelles
- Membrane transport and signaling
- Cell division and reproduction
- Cellular respiration and photosynthesis

**Genetics:**
- Mendelian inheritance patterns
- Chromosomal theory of inheritance
- Population genetics and evolution
- Genetic engineering and biotechnology

**Ecology:**
- Ecosystem dynamics and energy flow
- Population ecology and species interactions
- Community structure and biodiversity
- Conservation biology and sustainability

**Evolutionary Biology:**
- Natural selection and adaptation
- Speciation and macroevolution
- Phylogenetic relationships
- Human evolution and origins

**Physiology:**
- Organ system functions
- Homeostasis and regulation
- Neural and hormonal control
- Reproductive biology

**Key Principles:**
- Cell theory: All living things are composed of cells
- Evolution by natural selection: Mechanism of biological change
- Homeostasis: Maintenance of internal stability
- Emergent properties: Complex behaviors from simple interactions

**Applications:**
- Medicine and healthcare
- Agriculture and food production
- Environmental conservation
- Biotechnology and pharmaceuticals
- Forensic science and investigation""",
        "tags": ["biology", "life science", "cells", "genetics", "evolution", "ecology"],
        "verified": True
    },
    {
        "title": "DNA and Genetics",
        "content": """DNA (Deoxyribonucleic Acid) is the molecule that carries genetic information in all living organisms. Genetics is the study of genes, genetic variation, and heredity.

**DNA Structure:**
- Double helix structure discovered by Watson and Crick
- Composed of nucleotides: adenine, thymine, guanine, cytosine
- Base pairing: A-T, G-C hydrogen bonds
- Antiparallel strands with 5' to 3' orientation

**DNA Replication:**
- Semi-conservative process ensuring genetic continuity
- Helicase unwinds the double helix
- DNA polymerase synthesizes new strands
- Proofreading and repair mechanisms

**Gene Expression:**
- Transcription: DNA to mRNA in the nucleus
- Translation: mRNA to protein in ribosomes
- Regulatory elements control gene activity
- Epigenetic modifications affect expression

**Genetic Inheritance:**
- Mendel's laws: segregation, independent assortment, dominance
- Chromosomal inheritance patterns
- Sex-linked traits and genetic linkage
- Polygenic inheritance for quantitative traits

**Genetic Variation:**
- Mutations: Point mutations, insertions, deletions
- Recombination during meiosis
- Genetic drift and natural selection
- Gene flow between populations

**Molecular Genetics:**
- PCR amplification of DNA sequences
- DNA sequencing technologies
- CRISPR gene editing
- Genetic engineering and GMOs

**Human Genetics:**
- 23 pairs of chromosomes (22 autosomes + X/Y)
- Genetic diseases and disorders
- Pharmacogenetics and personalized medicine
- Forensic DNA analysis

**Applications:**
- Medical diagnostics and genetic testing
- Agricultural crop improvement
- Biotechnology and drug development
- Evolutionary biology research
- Forensic science and paternity testing""",
        "tags": ["DNA", "genetics", "molecular biology", "inheritance", "genes", "mutations"],
        "verified": True
    },
    {
        "title": "Evolution",
        "content": """Evolution is the process by which species of organisms change over time through genetic variation and natural selection. It is the fundamental mechanism underlying the diversity of life on Earth.

**Darwin's Theory of Evolution:**
- Descent with modification from common ancestors
- Natural selection as the primary mechanism
- Variation within populations provides raw material
- Adaptation to local environments drives change

**Evidence for Evolution:**
- Fossil record showing transitional forms
- Comparative anatomy and homologous structures
- Molecular biology and genetic similarities
- Biogeography and species distribution patterns
- Observed evolutionary change in contemporary populations

**Mechanisms of Evolution:**
- Natural selection: Differential survival and reproduction
- Genetic drift: Random changes in allele frequencies
- Gene flow: Movement of genes between populations
- Mutation: Source of new genetic variation
- Sexual selection: Mating preferences drive evolution

**Speciation:**
- Allopatric speciation: Geographic isolation
- Sympatric speciation: Reproductive isolation without geography
- Parapatric speciation: Partial geographic barriers
- Adaptive radiation: Rapid diversification from single ancestor

**Macroevolution:**
- Major evolutionary transitions
- Mass extinctions and recoveries
- Long-term trends in complexity
- Co-evolution between species

**Human Evolution:**
- Bipedalism and brain expansion
- Tool use and cultural evolution
- Migration out of Africa
- Recent human genetic diversity

**Applications:**
- Medicine: Antibiotic resistance, viral evolution
- Agriculture: Crop and livestock improvement
- Conservation: Endangered species management
- Public health: Disease prevention and control""",
        "tags": ["evolution", "biology", "natural selection", "darwin", "adaptation", "speciation"],
        "verified": True
    },

    # CHEMISTRY
    {
        "title": "Chemistry",
        "content": """Chemistry is the scientific study of matter, its properties, composition, and transformations. It encompasses the study of atoms, molecules, and their interactions through chemical reactions.

**Atomic Theory:**
- Matter composed of atoms (Dalton's atomic theory)
- Atoms are indivisible and indestructible
- Atoms of same element are identical
- Compounds form from combination of atoms in fixed ratios

**Chemical Bonding:**
- Ionic bonds: Transfer of electrons between atoms
- Covalent bonds: Sharing of electrons between atoms
- Metallic bonds: Delocalized electrons in metals
- Intermolecular forces: Attractions between molecules

**Chemical Reactions:**
- Synthesis: A + B → AB
- Decomposition: AB → A + B
- Single replacement: A + BC → AC + B
- Double replacement: AB + CD → AD + CB
- Combustion: Hydrocarbon + O₂ → CO₂ + H₂O

**States of Matter:**
- Solid: Fixed volume and shape, particles in fixed positions
- Liquid: Fixed volume, variable shape, particles mobile
- Gas: Variable volume and shape, particles highly mobile
- Plasma: Ionized gas with free electrons

**Thermodynamics:**
- First law: Energy conservation
- Second law: Entropy increases in isolated systems
- Third law: Absolute zero unattainable
- Gibbs free energy: Determines reaction spontaneity

**Chemical Kinetics:**
- Reaction rates and rate laws
- Activation energy and reaction mechanisms
- Catalysts and enzyme kinetics
- Temperature and concentration effects

**Quantum Chemistry:**
- Electronic structure of atoms and molecules
- Molecular orbital theory
- Spectroscopy and energy level transitions

**Applications:**
- Pharmaceuticals and drug development
- Materials science and nanotechnology
- Environmental chemistry and pollution control
- Food science and nutrition
- Forensic chemistry and criminal investigation""",
        "tags": ["chemistry", "matter", "atoms", "molecules", "reactions", "thermodynamics"],
        "verified": True
    },
    {
        "title": "Organic Chemistry",
        "content": """Organic Chemistry is the study of carbon-containing compounds and their properties, reactions, and synthesis. Carbon's unique ability to form stable bonds makes it the basis of life and many industrial materials.

**Carbon Bonding:**
- Tetravalent: Forms 4 bonds in most compounds
- Catenation: Ability to form chains and rings
- Isomerism: Same formula, different structures
- Functional groups determine chemical properties

**Hydrocarbons:**
- Alkanes: Saturated hydrocarbons (CₙH₂ₙ₊₂)
- Alkenes: Unsaturated with double bonds (CₙH₂ₙ)
- Alkynes: Unsaturated with triple bonds (CₙH₂ₙ₋₂)
- Aromatic: Benzene ring structures

**Functional Groups:**
- Alcohols: -OH (polar, hydrogen bonding)
- Aldehydes/Ketones: -CHO, >C=O
- Carboxylic acids: -COOH (acidic)
- Amines: -NH₂, -NHR, -NR₂ (basic)
- Esters: -COOR (fragrant compounds)

**Reaction Mechanisms:**
- Nucleophilic substitution (SN1, SN2)
- Elimination reactions (E1, E2)
- Addition reactions to alkenes
- Electrophilic aromatic substitution

**Stereochemistry:**
- Chirality and enantiomers
- R/S configuration designation
- Diastereomers and meso compounds
- Optical activity and polarization

**Polymer Chemistry:**
- Addition polymerization: Monomers add without byproducts
- Condensation polymerization: Water or other small molecules eliminated
- Natural polymers: Proteins, nucleic acids, polysaccharides
- Synthetic polymers: Plastics, fibers, elastomers

**Biochemistry:**
- Carbohydrates: Energy storage and structural molecules
- Lipids: Membrane components and energy reserves
- Proteins: Enzymes, antibodies, structural elements
- Nucleic acids: DNA and RNA for genetic information

**Applications:**
- Drug discovery and pharmaceutical development
- Materials science and polymer engineering
- Petrochemical industry and fuel production
- Food chemistry and nutrition science
- Agricultural chemistry and pesticides""",
        "tags": ["organic chemistry", "carbon", "molecules", "synthesis", "polymers", "biochemistry"],
        "verified": True
    },

    # PHILOSOPHY
    {
        "title": "Philosophy",
        "content": """Philosophy is the systematic study of fundamental questions about existence, knowledge, values, reason, mind, and language. It seeks to understand the nature of reality and our place within it.

**Metaphysics:**
- Ontology: Study of being and existence
- Cosmology: Origin and structure of the universe
- Philosophy of mind: Consciousness and mental states
- Free will vs determinism debate

**Epistemology:**
- Theory of knowledge and belief
- Sources of knowledge (empiricism vs rationalism)
- Justification and warrant
- Skepticism and certainty

**Ethics:**
- Moral philosophy and value theory
- Virtue ethics (Aristotle)
- Deontological ethics (Kant)
- Utilitarianism (Mill, Bentham)
- Metaethics and moral psychology

**Political Philosophy:**
- Justice and rights
- Social contract theory (Hobbes, Locke, Rousseau)
- Democracy and governance
- Liberty and equality

**Aesthetics:**
- Philosophy of art and beauty
- Artistic value and interpretation
- Taste and aesthetic judgment
- Cultural and historical contexts

**Philosophy of Language:**
- Meaning and reference
- Truth and proposition theory
- Language games (Wittgenstein)
- Analytic philosophy traditions

**Existentialism:**
- Individual freedom and responsibility
- Authenticity and bad faith
- Absurdity and meaning-making
- Death and finitude

**Eastern Philosophy:**
- Confucianism: Social harmony and ritual
- Taoism: Natural order and wu wei
- Buddhism: Suffering, enlightenment, impermanence
- Hinduism: Dharma, karma, reincarnation

**Modern Philosophy:**
- Phenomenology (Husserl, Heidegger)
- Existentialism (Sartre, Camus)
- Postmodernism (Derrida, Foucault)
- Analytic philosophy (Russell, Wittgenstein)

**Philosophy of Science:**
- Scientific method and demarcation
- Theory change and paradigm shifts
- Realism vs anti-realism
- Values in scientific inquiry""",
        "tags": ["philosophy", "metaphysics", "epistemology", "ethics", "existence", "knowledge"],
        "verified": True
    },
    {
        "title": "Ethics",
        "content": """Ethics is the branch of philosophy that involves systematizing, defending, and recommending concepts of right and wrong conduct. It examines moral principles and values that guide human behavior.

**Normative Ethics:**
- Virtue Ethics: Focus on character and virtues (Aristotle)
- Deontological Ethics: Duty-based morality (Kant)
- Consequentialism: Outcomes determine morality
- Utilitarianism: Greatest happiness for greatest number

**Metaethics:**
- Moral realism: Moral facts exist objectively
- Moral relativism: Morality is culturally determined
- Moral subjectivism: Morality is personal opinion
- Moral nihilism: No objective moral truths

**Applied Ethics:**
- Bioethics: Medical and biological issues
- Environmental ethics: Human relationship to nature
- Business ethics: Corporate responsibility
- Professional ethics: Codes of conduct

**Moral Psychology:**
- Moral reasoning and development (Kohlberg)
- Emotional aspects of morality
- Moral intuition and reasoning
- Cultural influences on moral judgment

**Key Concepts:**
- Moral obligation and duty
- Rights and responsibilities
- Justice and fairness
- Virtue and character
- Happiness and well-being

**Ethical Theories:**

**Utilitarianism:**
- Actions are right if they maximize overall happiness
- Jeremy Bentham: "Greatest happiness principle"
- John Stuart Mill: Quality of pleasure matters
- Criticisms: Ignores individual rights, difficult to calculate

**Deontology:**
- Immanuel Kant: Categorical imperative
- Universal moral laws
- Treat people as ends, not means
- Criticisms: Too rigid, ignores consequences

**Virtue Ethics:**
- Aristotle: Golden mean between extremes
- Focus on character development
- Intellectual and moral virtues
- Criticisms: Vague application to specific situations

**Contemporary Issues:**
- Artificial intelligence ethics
- Climate change responsibility
- Genetic engineering and human enhancement
- Global justice and poverty
- Animal rights and welfare""",
        "tags": ["ethics", "morality", "philosophy", "values", "moral theory", "virtue"],
        "verified": True
    },

    # HISTORY
    {
        "title": "World History",
        "content": """World History encompasses the study of human civilization from prehistoric times to the present, examining the development of societies, cultures, technologies, and global interactions.

**Ancient Civilizations:**
- Mesopotamia (Sumerians, Akkadians, Babylonians)
- Ancient Egypt (pharaonic dynasties)
- Indus Valley Civilization
- Ancient China (Shang, Zhou, Qin dynasties)
- Mesoamerican civilizations (Olmecs, Maya, Aztecs)
- Ancient Greece and Hellenistic period
- Roman Republic and Empire

**Middle Ages (500-1500 CE):**
- Fall of Western Roman Empire
- Rise of Islam and Islamic Golden Age
- Byzantine Empire and Eastern Christianity
- Medieval Europe (feudalism, Crusades, Black Death)
- Mongol Empire and Silk Road trade
- Mali Empire and Mansa Musa
- Aztec and Inca empires

**Early Modern Period (1500-1800):**
- Age of Exploration and European colonization
- Scientific Revolution (Copernicus, Galileo, Newton)
- Enlightenment and democratic revolutions
- Industrial Revolution beginnings
- Atlantic slave trade and triangular trade

**Modern Era (1800-Present):**
- Industrial Revolution and urbanization
- World Wars and Cold War
- Decolonization and independence movements
- Technological revolution (computers, internet)
- Globalization and economic integration

**Key Historical Processes:**
- Agricultural Revolution: Transition to farming societies
- Urban Revolution: Rise of cities and civilizations
- Axial Age: Major philosophical and religious developments
- Commercial Revolution: Long-distance trade networks
- Industrial Revolution: Mechanization and factories
- Digital Revolution: Information technology era

**Historiography:**
- Different approaches: political, economic, social, cultural
- Primary vs secondary sources
- Historical interpretation and bias
- Role of archaeology and material evidence

**Contemporary Issues:**
- Climate change and environmental history
- Digital history and big data approaches
- Global inequality and development
- Cultural heritage preservation
- Historical memory and collective identity""",
        "tags": ["history", "civilization", "culture", "societies", "chronology", "development"],
        "verified": True
    },
    {
        "title": "Scientific Revolution",
        "content": """The Scientific Revolution (1543-1687) was a period of transformative change in European thought, when scientific ideas and methods replaced traditional beliefs about the natural world. It laid the foundation for modern science.

**Key Figures and Discoveries:**

**Copernican Revolution:**
- Nicolaus Copernicus: Heliocentric model (1543)
- Replaced geocentric worldview
- Earth orbits the Sun, not vice versa

**Scientific Method:**
- Francis Bacon: Empirical method and inductive reasoning
- René Descartes: Deductive mathematical approach
- Emphasis on observation, experimentation, and mathematics

**Physics and Astronomy:**
- Galileo Galilei: Telescope observations, laws of motion
- Johannes Kepler: Laws of planetary motion
- Isaac Newton: Universal gravitation and classical mechanics

**Medicine and Biology:**
- Andreas Vesalius: Modern human anatomy
- William Harvey: Circulation of blood
- Anton van Leeuwenhoek: Microscopic observations

**Chemistry and Matter:**
- Robert Boyle: Experimental chemistry, gas laws
- Alchemy to modern chemistry transition
- Corpuscular theory of matter

**Mathematics:**
- René Descartes: Analytic geometry
- Pierre de Fermat: Number theory foundations
- Blaise Pascal: Probability theory

**Institutional Changes:**
- Royal Society of London (1660)
- Académie des Sciences (1666)
- Scientific journals and peer review
- International scientific communication

**Philosophical Foundations:**
- Rejection of Aristotelian physics
- Mechanical philosophy and clockwork universe
- Empiricism vs rationalism debate
- Separation of science from theology

**Impact on Society:**
- Technological innovation and engineering
- Medical advances and public health
- Navigation and exploration capabilities
- Educational reforms and scientific literacy

**Legacy:**
- Foundation of modern scientific disciplines
- Enlightenment and Age of Reason
- Industrial Revolution technological base
- Contemporary scientific methodology""",
        "tags": ["scientific revolution", "science", "history", "renaissance", "discovery", "methodology"],
        "verified": True
    },

    # ECONOMICS
    {
        "title": "Economics",
        "content": """Economics is the social science that studies how individuals, businesses, governments, and societies allocate scarce resources to satisfy unlimited wants and needs.

**Microeconomics:**
- Individual and firm behavior
- Supply and demand analysis
- Market structures (perfect competition, monopoly, oligopoly)
- Consumer theory and utility maximization
- Production theory and cost analysis

**Macroeconomics:**
- National income and GDP measurement
- Inflation and unemployment analysis
- Monetary and fiscal policy
- Business cycles and economic growth
- International trade and finance

**Key Economic Concepts:**
- Scarcity: Limited resources, unlimited wants
- Opportunity cost: Value of next best alternative
- Marginal analysis: Additional benefits vs costs
- Incentives: Rewards and punishments affecting behavior
- Markets: Mechanisms for resource allocation

**Economic Systems:**
- Capitalism: Private ownership, market allocation
- Socialism: Government ownership, planned allocation
- Mixed economies: Combination of market and government
- Traditional economies: Customs and habits guide allocation

**Market Failures:**
- Externalities: Costs/benefits not reflected in prices
- Public goods: Non-excludable, non-rivalrous goods
- Information asymmetry: Unequal information between parties
- Market power: Ability to influence prices

**Government Intervention:**
- Regulation and antitrust laws
- Taxation and redistribution
- Public goods provision
- Stabilization policies (monetary, fiscal)

**International Economics:**
- Comparative advantage and trade theory
- Balance of payments and exchange rates
- International organizations (WTO, IMF, World Bank)
- Globalization and economic integration

**Development Economics:**
- Economic growth and poverty reduction
- Human capital and education
- Institutions and governance
- Sustainable development goals

**Behavioral Economics:**
- Psychological factors in economic decisions
- Cognitive biases and heuristics
- Prospect theory and loss aversion
- Nudge theory and choice architecture

**Applications:**
- Business strategy and management
- Public policy and government
- Environmental economics and sustainability
- Health economics and insurance markets""",
        "tags": ["economics", "finance", "markets", "resources", "policy", "growth"],
        "verified": True
    },
    {
        "title": "Supply and Demand",
        "content": """Supply and Demand are fundamental concepts in economics that explain how prices are determined in markets and how resources are allocated.

**Demand:**
- Quantity demanded: Amount consumers want at a given price
- Law of demand: Inverse relationship between price and quantity
- Demand curve: Downward sloping (higher prices, lower quantity)
- Determinants: Income, prices of related goods, tastes, expectations

**Supply:**
- Quantity supplied: Amount producers offer at a given price
- Law of supply: Direct relationship between price and quantity
- Supply curve: Upward sloping (higher prices, higher quantity)
- Determinants: Input prices, technology, expectations, number of sellers

**Market Equilibrium:**
- Equilibrium price: Where supply equals demand
- Equilibrium quantity: Amount traded at equilibrium price
- Surplus: Excess supply (price above equilibrium)
- Shortage: Excess demand (price below equilibrium)

**Price Elasticity:**
- Elastic demand: Quantity changes greatly with price changes
- Inelastic demand: Quantity changes little with price changes
- Elasticity formula: % change in quantity / % change in price
- Factors affecting elasticity: Substitutes, necessity vs luxury, time horizon

**Shifts vs Movements:**
- Demand shift: Change in quantity demanded at every price
- Demand movement: Change in quantity at same price
- Supply shift: Change in quantity supplied at every price
- Supply movement: Change in quantity at same price

**Applications:**
- Price controls and government intervention
- Tax incidence and burden distribution
- Agricultural price supports
- Minimum wage and labor markets
- International trade and tariffs

**Market Efficiency:**
- Allocative efficiency: Resources go to highest-valued uses
- Pareto efficiency: No one can be made better off without making someone worse off
- Market failures: Externalities, public goods, information problems
- Government role in correcting market failures

**Real-World Examples:**
- Oil price shocks and supply disruptions
- Housing market bubbles and demand shifts
- Technology improvements and supply increases
- Seasonal demand patterns and pricing strategies""",
        "tags": ["supply and demand", "economics", "markets", "equilibrium", "elasticity", "pricing"],
        "verified": True
    },

    # LITERATURE AND ARTS
    {
        "title": "Literature",
        "content": """Literature encompasses written works of fiction, poetry, drama, and nonfiction that are considered to have artistic or intellectual value. It reflects human experience, culture, and imagination.

**Literary Genres:**
- Fiction: Novels, short stories, novellas
- Poetry: Verse forms, rhythm, imagery
- Drama: Plays, screenplays, performance scripts
- Nonfiction: Essays, biographies, memoirs, journalism

**Literary Devices:**
- Metaphor and simile: Figurative language
- Symbolism: Objects representing abstract ideas
- Irony: Contrast between expectation and reality
- Foreshadowing: Hints of future events
- Alliteration: Repetition of initial sounds

**Literary Periods:**
- Classical literature (ancient Greece and Rome)
- Medieval literature (epic poems, romance)
- Renaissance literature (Shakespeare, humanism)
- Romanticism (emotion, nature, individualism)
- Modernism (stream of consciousness, fragmentation)
- Postmodernism (metafiction, irony, pastiche)

**Literary Criticism:**
- Formalism: Focus on literary elements and structure
- Structuralism: Underlying patterns and systems
- Reader-response theory: Reader's role in creating meaning
- Feminist criticism: Gender roles and patriarchy
- Marxist criticism: Class struggle and economic factors
- Postcolonial criticism: Colonialism and cultural identity

**World Literature:**
- Western canon: Greek, Roman, European traditions
- Eastern literature: Chinese, Japanese, Indian classics
- African literature: Oral traditions, postcolonial writing
- Latin American literature: Magical realism, political themes
- Indigenous literatures: Oral traditions, cultural preservation

**Digital Literature:**
- Hypertext fiction and interactive narratives
- Electronic literature and digital poetry
- Fan fiction and participatory writing
- Social media literature and micro-fiction

**Literary Theory:**
- Hermeneutics: Interpretation and understanding
- Semiotics: Signs and symbols in literature
- Narratology: Study of narrative structures
- Deconstruction: Challenging fixed meanings

**Cultural Impact:**
- Social commentary and critique
- Preservation of cultural heritage
- Language development and evolution
- Empathy building and perspective taking
- Entertainment and emotional catharsis""",
        "tags": ["literature", "writing", "fiction", "poetry", "drama", "narrative"],
        "verified": True
    },
    {
        "title": "Shakespeare",
        "content": """William Shakespeare (1564-1616) was an English playwright, poet, and actor widely regarded as the greatest writer in the English language and the world's greatest dramatist.

**Life and Career:**
- Born in Stratford-upon-Avon, England
- Married Anne Hathaway at age 18
- Moved to London, became actor and playwright
- Member of the Lord Chamberlain's Men (later King's Men)
- Wrote 39 plays, 154 sonnets, and several narrative poems

**Literary Works:**

**Tragedies:**
- Hamlet: Prince's revenge and existential crisis
- Macbeth: Ambition, guilt, and supernatural elements
- Othello: Jealousy and manipulation
- King Lear: Power, family, madness
- Romeo and Juliet: Love, fate, feud

**Comedies:**
- A Midsummer Night's Dream: Love, magic, mistaken identities
- The Taming of the Shrew: Marriage, gender roles, transformation
- Twelfth Night: Love triangle, disguise, celebration
- As You Like It: Pastoral romance, gender disguise
- Much Ado About Nothing: Wit, deception, reconciliation

**Histories:**
- Henry V: Leadership, nationalism, St. Crispin's Day speech
- Richard III: Villainy, power, deformity
- Henry IV Part 1 & 2: Rebellion, honor, friendship

**Sonnets:**
- 154 sonnets exploring love, beauty, time, mortality
- Fair Youth sequence and Dark Lady poems
- Themes of immortality through poetry
- Iambic pentameter with ABAB CDCD EFEF GG rhyme scheme

**Literary Techniques:**
- Blank verse (unrhymed iambic pentameter)
- Soliloquies and asides for character revelation
- Dramatic irony and foreshadowing
- Wordplay: puns, metaphors, malapropisms
- Subversion of social hierarchies

**Themes:**
- Love and romance (courtly vs genuine)
- Power and ambition (corruption of authority)
- Identity and transformation (gender disguise)
- Fate vs free will (providence and choice)
- Madness and sanity (Hamlet, Lear, Ophelia)
- Appearance vs reality (deception, illusion)

**Cultural Impact:**
- English language: 1,700+ words and phrases
- Theater: Foundation of modern drama
- Psychology: Character depth and complexity
- Education: Required reading worldwide
- Adaptations: Films, novels, modern retellings

**Shakespearean Criticism:**
- Authorship debates and collaboration theories
- Textual authenticity and First Folio (1623)
- Historical context and Elizabethan/Jacobean England
- Feminist readings and gender politics
- Postcolonial interpretations

**Legacy:**
- Universal themes still relevant today
- Influence on Western literature and culture
- Ongoing scholarly research and performance
- Global theater tradition and Shakespeare festivals""",
        "tags": ["shakespeare", "literature", "drama", "poetry", "renaissance", "theater"],
        "verified": True
    },

    # PSYCHOLOGY
    {
        "title": "Psychology",
        "content": """Psychology is the scientific study of mind and behavior. It encompasses the biological, cognitive, emotional, and social aspects of human functioning and development.

**Major Branches:**
- Clinical Psychology: Assessment and treatment of mental disorders
- Cognitive Psychology: Mental processes (thinking, memory, perception)
- Developmental Psychology: Growth and change across lifespan
- Social Psychology: Social behavior and interpersonal relationships
- Personality Psychology: Individual differences and traits
- Neuropsychology: Brain-behavior relationships

**Research Methods:**
- Experimental design: Controlled manipulation of variables
- Observational studies: Natural behavior in real settings
- Surveys and questionnaires: Self-report measures
- Case studies: In-depth analysis of individuals
- Neuroimaging: fMRI, EEG, PET scans
- Statistical analysis: Hypothesis testing and data interpretation

**Key Theories:**
- Psychoanalytic Theory (Freud): Unconscious mind, psychosexual development
- Behaviorism (Watson, Skinner): Learning through conditioning
- Humanistic Psychology (Rogers, Maslow): Self-actualization, personal growth
- Cognitive Theory (Piaget, Beck): Mental processes and information processing
- Evolutionary Psychology: Adaptive psychological mechanisms

**Biological Psychology:**
- Nervous system structure and function
- Neurotransmitters and brain chemistry
- Genetics and heritability
- Brain plasticity and neuroplasticity
- Hormonal influences on behavior

**Cognitive Processes:**
- Attention and perception
- Memory systems (sensory, short-term, long-term)
- Language acquisition and processing
- Problem-solving and decision-making
- Intelligence and cognitive abilities

**Emotional Psychology:**
- Emotional intelligence and regulation
- Mood disorders and affective states
- Stress and coping mechanisms
- Positive psychology and well-being
- Emotional development across lifespan

**Social Psychology:**
- Attitudes and persuasion
- Group dynamics and conformity
- Interpersonal attraction and relationships
- Prejudice and stereotyping
- Self and identity formation

**Developmental Psychology:**
- Prenatal development and infancy
- Childhood cognitive and social development
- Adolescent identity formation
- Adult development and aging
- Lifespan developmental theories

**Abnormal Psychology:**
- Classification of mental disorders (DSM-5)
- Anxiety and mood disorders
- Personality disorders and schizophrenia
- Trauma and stress-related disorders
- Treatment approaches and therapies

**Applications:**
- Clinical treatment and psychotherapy
- Educational psychology and learning
- Industrial-organizational psychology
- Forensic psychology and law
- Sports psychology and performance
- Health psychology and wellness""",
        "tags": ["psychology", "mind", "behavior", "cognitive", "development", "mental health"],
        "verified": True
    },
    {
        "title": "Cognitive Psychology",
        "content": """Cognitive Psychology studies mental processes including how people think, feel, remember, and learn. It focuses on internal mental states and processes rather than observable behavior.

**Core Topics:**
- Attention: Selective focus and information processing
- Perception: Sensory input interpretation and organization
- Memory: Encoding, storage, and retrieval processes
- Language: Comprehension, production, and acquisition
- Thinking: Problem-solving, reasoning, and decision-making
- Consciousness: Awareness, metacognition, and self-reflection

**Memory Systems:**
- Sensory memory: Brief storage of sensory information
- Short-term memory (working memory): Limited capacity (7±2 items)
- Long-term memory: Relatively permanent storage
- Episodic memory: Personal experiences and events
- Semantic memory: Factual knowledge and concepts
- Procedural memory: Skills and motor sequences

**Learning Theories:**
- Behaviorism: Classical and operant conditioning
- Cognitive learning: Insight and understanding
- Social learning: Observation and modeling
- Constructivism: Active knowledge construction

**Problem-Solving:**
- Algorithms: Step-by-step procedures
- Heuristics: Mental shortcuts and rules of thumb
- Insight: Sudden understanding of solutions
- Creativity: Novel and useful idea generation

**Decision-Making:**
- Rational choice theory: Optimal decision strategies
- Bounded rationality: Limitations in information processing
- Prospect theory: Risk perception and loss aversion
- Cognitive biases: Systematic thinking errors

**Language Processing:**
- Phonological processing: Sound-based language analysis
- Syntactic processing: Grammatical structure parsing
- Semantic processing: Meaning extraction
- Pragmatic processing: Context and social use

**Cognitive Development:**
- Piaget's stages: Sensorimotor, preoperational, concrete operational, formal operational
- Information processing approach: Attention, memory, strategy development
- Social cognition: Theory of mind and perspective-taking
- Metacognition: Thinking about thinking

**Neurocognitive Foundations:**
- Neural networks and brain regions
- Cognitive neuroscience methods (fMRI, ERP)
- Plasticity and brain reorganization
- Neurotransmitter systems and cognition

**Applications:**
- Educational psychology and learning design
- Human-computer interaction and UX design
- Clinical psychology and cognitive therapy
- Artificial intelligence and machine learning
- Memory enhancement and cognitive training
- Expert performance and skill acquisition""",
        "tags": ["cognitive psychology", "cognition", "memory", "thinking", "learning", "perception"],
        "verified": True
    },

    # ENVIRONMENTAL SCIENCE
    {
        "title": "Environmental Science",
        "content": """Environmental Science studies the interactions between physical, chemical, and biological components of the environment, with particular emphasis on human impacts and sustainability.

**Ecosystems:**
- Structure and function of natural systems
- Energy flow and nutrient cycling
- Biodiversity and species interactions
- Succession and ecosystem development
- Carrying capacity and limiting factors

**Climate Systems:**
- Atmospheric composition and greenhouse gases
- Ocean currents and heat distribution
- Weather patterns and climate zones
- Climate change and global warming
- Extreme weather events and impacts

**Water Resources:**
- Hydrologic cycle and water distribution
- Groundwater and surface water systems
- Water quality and pollution
- Water scarcity and conservation
- Watershed management and restoration

**Soil Systems:**
- Soil formation and classification
- Soil erosion and conservation
- Soil fertility and nutrient management
- Land degradation and desertification
- Sustainable agriculture practices

**Air Quality:**
- Atmospheric pollutants and sources
- Acid rain and photochemical smog
- Ozone depletion and UV radiation
- Indoor air quality and health impacts
- Air pollution control technologies

**Waste Management:**
- Solid waste generation and composition
- Recycling and resource recovery
- Hazardous waste handling and disposal
- Circular economy principles
- Waste-to-energy technologies

**Conservation Biology:**
- Endangered species protection
- Habitat preservation and restoration
- Invasive species management
- Wildlife corridors and connectivity
- Population viability analysis

**Environmental Policy:**
- Environmental impact assessment
- Regulatory frameworks and standards
- International agreements (Paris Accord, CBD)
- Environmental justice and equity
- Sustainable development goals

**Human Impacts:**
- Deforestation and land use change
- Overfishing and marine ecosystem decline
- Urban sprawl and habitat fragmentation
- Pollution and contamination
- Resource depletion and overconsumption

**Sustainable Solutions:**
- Renewable energy transition
- Green technology and innovation
- Ecosystem-based management
- Environmental education and awareness
- Corporate sustainability practices""",
        "tags": ["environmental science", "ecology", "sustainability", "climate", "conservation", "pollution"],
        "verified": True
    },
    {
        "title": "Climate Change",
        "content": """Climate Change refers to long-term shifts in global weather patterns and temperatures, primarily driven by human activities that increase greenhouse gas concentrations in the atmosphere.

**Greenhouse Effect:**
- Natural greenhouse gases: CO₂, CH₄, H₂O, N₂O
- Enhanced greenhouse effect from human emissions
- Atmospheric warming and heat trapping
- Global average temperature increase

**Causes of Climate Change:**
- Fossil fuel combustion (CO₂ emissions)
- Deforestation and land use change
- Industrial processes and chemical emissions
- Agricultural practices (methane from livestock)
- Waste management and landfill emissions

**Evidence and Observations:**
- Global temperature records (1880-present)
- Sea level rise and thermal expansion
- Glacier retreat and Arctic sea ice decline
- Ocean heat content increase
- Extreme weather frequency and intensity

**Impacts of Climate Change:**
- Ecosystems: Species migration, coral bleaching, forest fires
- Agriculture: Crop yield changes, drought impacts
- Water resources: Flooding, drought, water scarcity
- Human health: Heat-related illness, disease vectors
- Coastal communities: Sea level rise, storm surges
- Infrastructure: Extreme weather damage

**Climate Science:**
- Climate models and projections
- Paleoclimate records and proxy data
- Carbon cycle and feedback mechanisms
- Tipping points and abrupt changes
- Regional climate variability

**Mitigation Strategies:**
- Renewable energy transition (solar, wind, hydro)
- Energy efficiency and conservation
- Carbon capture and storage technologies
- Reforestation and afforestation
- Sustainable transportation systems

**Adaptation Measures:**
- Infrastructure resilience planning
- Agricultural adaptation strategies
- Water resource management
- Coastal protection and retreat planning
- Health system preparedness

**International Framework:**
- United Nations Framework Convention on Climate Change (UNFCCC)
- Paris Agreement targets (1.5°C warming limit)
- Nationally Determined Contributions (NDCs)
- Kyoto Protocol and emission trading
- Intergovernmental Panel on Climate Change (IPCC)

**Policy and Economics:**
- Carbon pricing (taxes, cap-and-trade)
- Green finance and sustainable investing
- International climate finance
- Just transition for affected communities
- Environmental justice considerations

**Future Scenarios:**
- Representative Concentration Pathways (RCPs)
- Shared Socioeconomic Pathways (SSPs)
- Climate sensitivity and uncertainty
- Geoengineering proposals and risks
- Long-term climate stabilization goals""",
        "tags": ["climate change", "global warming", "environment", "greenhouse gases", "sustainability", "carbon"],
        "verified": True
    },

    # SOCIOLOGY AND ANTHROPOLOGY
    {
        "title": "Sociology",
        "content": """Sociology is the scientific study of society, social institutions, and social relationships. It examines how individuals interact within social structures and how societies develop and change.

**Social Theory:**
- Functionalism: Society as interconnected parts working together
- Conflict theory: Society shaped by inequality and power struggles
- Symbolic interactionism: Social life through symbols and interactions
- Structuralism: Underlying social structures and patterns
- Postmodernism: Fragmentation of social narratives

**Social Institutions:**
- Family: Marriage, kinship, child-rearing patterns
- Education: Socialization, knowledge transmission, stratification
- Religion: Beliefs, rituals, social cohesion
- Economy: Production, distribution, consumption patterns
- Government: Political systems, power distribution, law

**Social Stratification:**
- Class systems: Economic inequality and mobility
- Status and prestige hierarchies
- Power and authority structures
- Social mobility patterns
- Intersectionality: Multiple identity dimensions

**Culture and Society:**
- Cultural norms and values
- Socialization processes
- Deviance and social control
- Cultural relativism vs ethnocentrism
- Globalization and cultural diffusion

**Group Dynamics:**
- Primary and secondary groups
- Reference groups and social comparison
- Group conformity and obedience
- Leadership styles and effectiveness
- Intergroup relations and conflict

**Social Change:**
- Theories of social evolution
- Revolution and reform movements
- Technological impacts on society
- Demographic transitions
- Globalization and modernization

**Research Methods:**
- Quantitative methods: Surveys, statistical analysis
- Qualitative methods: Ethnography, interviews, participant observation
- Mixed methods approaches
- Comparative sociology: Cross-cultural analysis
- Historical sociology: Long-term social change

**Applied Sociology:**
- Criminology and criminal justice
- Urban sociology and community studies
- Sociology of education and learning
- Sociology of religion and spirituality
- Environmental sociology and sustainability

**Contemporary Issues:**
- Inequality and social justice
- Immigration and multiculturalism
- Technology and digital society
- Aging populations and demographics
- Gender roles and identity
- Race and ethnic relations
- Mental health and well-being""",
        "tags": ["sociology", "society", "social institutions", "culture", "inequality", "social change"],
        "verified": True
    },
    {
        "title": "Anthropology",
        "content": """Anthropology is the holistic study of humanity, encompassing biological, cultural, linguistic, and archaeological dimensions of human existence across time and space.

**Cultural Anthropology:**
- Ethnography: In-depth study of cultures
- Cultural relativism: Understanding cultures on their own terms
- Participant observation: Immersive fieldwork method
- Cross-cultural comparison and analysis

**Biological Anthropology:**
- Human evolution and paleoanthropology
- Primatology: Study of primates and human origins
- Human variation and adaptation
- Forensic anthropology and osteology

**Archaeology:**
- Material culture and artifacts
- Excavation techniques and stratigraphy
- Dating methods (radiocarbon, dendrochronology)
- Cultural reconstruction from material remains

**Linguistic Anthropology:**
- Language and culture relationships
- Ethnography of communication
- Sociolinguistics and language variation
- Endangered languages and preservation

**Key Concepts:**
- Holism: Integrated approach to human study
- Cultural relativism: Non-judgmental cultural understanding
- Emic vs etic perspectives: Insider vs outsider viewpoints
- Participant observation: Primary research method
- Thick description: Detailed cultural analysis

**Theoretical Approaches:**
- Functionalism: Cultural elements serve social functions
- Structuralism: Underlying patterns in culture
- Symbolic anthropology: Meaning and symbolism
- Postmodern anthropology: Power, representation, reflexivity
- Feminist anthropology: Gender and power dynamics

**Research Methods:**
- Ethnographic fieldwork and immersion
- Participant observation techniques
- Interview and oral history methods
- Archival research and document analysis
- Quantitative methods and surveys

**Major Subfields:**
- Urban anthropology: Cities and urbanization
- Medical anthropology: Health, illness, healing
- Economic anthropology: Production and exchange
- Political anthropology: Power and governance
- Psychological anthropology: Culture and personality

**Applied Anthropology:**
- Development anthropology and aid projects
- Cultural resource management
- Human rights advocacy
- Corporate anthropology and business applications
- Public policy and social impact assessment

**Contemporary Issues:**
- Globalization and cultural change
- Indigenous rights and sovereignty
- Migration and transnationalism
- Environmental anthropology and climate change
- Digital anthropology and online cultures
- Bioethics and new reproductive technologies
- Cultural heritage preservation

**Ethical Considerations:**
- Informed consent in research
- Cultural sensitivity and respect
- Representation and voice of studied communities
- Researcher positionality and reflexivity
- Collaborative and participatory research methods""",
        "tags": ["anthropology", "culture", "humanity", "ethnography", "archaeology", "linguistics"],
        "verified": True
    },

    # MEDICINE AND HEALTH
    {
        "title": "Medicine",
        "content": """Medicine is the science and practice of diagnosing, treating, and preventing disease. It encompasses medical knowledge, clinical practice, research, and healthcare systems.

**Medical Specialties:**
- Internal Medicine: Adult medical conditions
- Surgery: Operative treatment of diseases
- Pediatrics: Medical care of children
- Obstetrics/Gynecology: Women's health and childbirth
- Psychiatry: Mental health and behavioral disorders
- Radiology: Medical imaging and diagnosis
- Pathology: Disease diagnosis through laboratory analysis
- Emergency Medicine: Acute care and trauma

**Basic Medical Sciences:**
- Anatomy: Structure of the human body
- Physiology: Function of body systems
- Biochemistry: Chemical processes in living organisms
- Pharmacology: Drug actions and therapeutic uses
- Microbiology: Microorganisms and infectious diseases
- Immunology: Immune system and defense mechanisms
- Pathology: Disease processes and mechanisms

**Clinical Practice:**
- History taking and physical examination
- Differential diagnosis and clinical reasoning
- Treatment planning and patient management
- Preventive medicine and health promotion
- Palliative care and end-of-life management
- Medical ethics and patient rights

**Medical Research:**
- Basic science research and discovery
- Clinical trials and evidence-based medicine
- Translational research from bench to bedside
- Epidemiological studies and population health
- Health services research and outcomes

**Healthcare Systems:**
- Primary, secondary, and tertiary care levels
- Public health and preventive services
- Health insurance and payment systems
- Healthcare policy and reform
- Global health and international medicine

**Diagnostic Methods:**
- Laboratory testing and biomarkers
- Medical imaging (X-ray, CT, MRI, ultrasound)
- Endoscopic procedures and biopsies
- Genetic testing and personalized medicine
- Point-of-care testing and rapid diagnostics

**Treatment Modalities:**
- Pharmacological therapy and drug development
- Surgical interventions and minimally invasive procedures
- Radiation therapy and oncology
- Physical therapy and rehabilitation
- Psychotherapy and behavioral interventions
- Alternative and complementary medicine

**Preventive Medicine:**
- Vaccination and immunization programs
- Screening and early detection
- Lifestyle modification and health education
- Environmental health and occupational medicine
- Health promotion and disease prevention

**Medical Ethics:**
- Patient autonomy and informed consent
- Beneficence and non-maleficence principles
- Justice in healthcare distribution
- Confidentiality and privacy protection
- End-of-life care decisions

**Global Health:**
- Infectious disease control and eradication
- Maternal and child health improvement
- Non-communicable disease prevention
- Health systems strengthening
- Humanitarian medicine and disaster response

**Future of Medicine:**
- Precision medicine and genomics
- Artificial intelligence in diagnosis
- Telemedicine and digital health
- Regenerative medicine and stem cells
- Nanotechnology and targeted therapies""",
        "tags": ["medicine", "healthcare", "diagnosis", "treatment", "prevention", "medical science"],
        "verified": True
    },
    {
        "title": "Public Health",
        "content": """Public Health focuses on protecting and improving the health of communities and populations through prevention, education, policy, and research. It addresses health issues at the population level rather than individual care.

**Core Functions:**
- Assessment: Monitoring community health status
- Policy Development: Creating health policies and regulations
- Assurance: Ensuring access to healthcare services

**Epidemiology:**
- Disease surveillance and outbreak investigation
- Risk factor identification and analysis
- Study design and statistical methods
- Causal inference and association studies

**Health Promotion:**
- Health education and communication
- Behavioral change interventions
- Community-based health programs
- Health literacy improvement

**Disease Prevention:**
- Immunization programs and vaccine distribution
- Screening and early detection programs
- Vector control and environmental interventions
- Health risk reduction strategies

**Environmental Health:**
- Water and air quality monitoring
- Food safety and sanitation
- Occupational health and workplace safety
- Hazardous waste management
- Climate change health impacts

**Global Health:**
- International health organizations (WHO, UNICEF)
- Global health security and pandemic preparedness
- Health equity and social determinants
- International development and aid
- Cross-border health threats

**Health Policy:**
- Healthcare financing and insurance systems
- Health system organization and delivery
- Regulatory frameworks and standards
- Health equity and access policies
- Quality assurance and performance measurement

**Biostatistics:**
- Study design and sampling methods
- Data analysis and interpretation
- Statistical modeling and inference
- Research methodology and validity

**Social Determinants of Health:**
- Socioeconomic status and income inequality
- Education and health literacy
- Housing and neighborhood conditions
- Social support networks
- Discrimination and social exclusion

**Population Health Management:**
- Risk stratification and targeted interventions
- Chronic disease management programs
- Health outcomes measurement
- Cost-effectiveness analysis
- Quality improvement initiatives

**Emergency Preparedness:**
- Disaster response and recovery
- Pandemic planning and response
- Bioterrorism preparedness
- Emergency medical services
- Public health emergency declarations

**Health Informatics:**
- Electronic health records and data systems
- Health information exchange
- Surveillance systems and monitoring
- Data privacy and security
- Big data analytics in health

**Maternal and Child Health:**
- Prenatal care and pregnancy outcomes
- Child development and immunization
- Family planning and reproductive health
- Adolescent health and risk behaviors
- Early childhood intervention programs

**Aging and Geriatric Health:**
- Elderly population health needs
- Long-term care and support services
- Age-related disease prevention
- Cognitive health and dementia care
- End-of-life care and palliative services

**Mental Health:**
- Mental health promotion and prevention
- Stigma reduction and awareness
- Community mental health services
- Crisis intervention and suicide prevention
- Integration with primary healthcare

**Injury Prevention:**
- Motor vehicle safety and traffic control
- Workplace safety and injury prevention
- Violence prevention and intervention
- Falls prevention in elderly populations
- Sports and recreation injury prevention""",
        "tags": ["public health", "epidemiology", "prevention", "health policy", "population health", "community health"],
        "verified": True
    },

    # POLITICAL SCIENCE
    {
        "title": "Political Science",
        "content": """Political Science studies government systems, political behavior, political institutions, and the distribution of power and resources within societies.

**Political Theory:**
- Classical political philosophy (Plato, Aristotle, Machiavelli)
- Liberal democracy and democratic theory
- Justice and rights (Rawls, Nozick)
- Power and authority (Weber, Foucault)
- Feminist political theory and gender

**Comparative Politics:**
- Political systems and regimes
- Democratization and authoritarianism
- Political parties and electoral systems
- Federalism and decentralization
- Political culture and civic engagement

**International Relations:**
- Realism, liberalism, constructivism theories
- International organizations and global governance
- Conflict and cooperation in world politics
- Globalization and interdependence
- Security studies and peace research

**Political Economy:**
- Capitalism, socialism, mixed economies
- Economic development and inequality
- International trade and finance
- Political business cycles
- Corruption and rent-seeking

**Public Administration:**
- Bureaucracy and organizational theory
- Public policy process and implementation
- Government budgeting and finance
- Administrative law and regulation
- Performance measurement and accountability

**Political Behavior:**
- Voting behavior and electoral participation
- Public opinion and political attitudes
- Political socialization and identity
- Interest groups and lobbying
- Social movements and protest

**Constitutional Law:**
- Constitutional design and amendment
- Separation of powers and checks and balances
- Federalism and intergovernmental relations
- Judicial review and constitutional interpretation
- Rights and liberties protection

**Research Methods:**
- Quantitative methods: Statistical analysis, modeling
- Qualitative methods: Case studies, interviews
- Comparative methods: Cross-national analysis
- Experimental design: Field and lab experiments
- Historical analysis and archival research

**Key Concepts:**
- Power: Ability to influence others and outcomes
- Authority: Legitimate exercise of power
- Legitimacy: Acceptance of political systems
- Sovereignty: Supreme authority within territory
- Citizenship: Rights and responsibilities in polity

**Contemporary Issues:**
- Democratic backsliding and populism
- Identity politics and polarization
- Climate change and environmental politics
- Technology and digital governance
- Migration and border politics
- Inequality and social justice
- Cybersecurity and information warfare

**Political Systems:**
- Presidential vs parliamentary systems
- Unitary vs federal states
- Majoritarian vs consensus democracies
- Authoritarian regimes and hybrid systems
- Political party systems and coalitions

**Global Politics:**
- United Nations and multilateralism
- Regional organizations (EU, ASEAN, NATO)
- Non-state actors and transnationalism
- Human rights and international law
- Development aid and foreign policy
- Conflict resolution and peacekeeping""",
        "tags": ["political science", "government", "politics", "power", "democracy", "international relations"],
        "verified": True
    },

    # EDUCATION
    {
        "title": "Education",
        "content": """Education encompasses the systematic process of facilitating learning, knowledge acquisition, skill development, and character formation. It includes formal schooling, informal learning, and lifelong education.

**Educational Philosophy:**
- Essentialism: Core knowledge and academic rigor
- Progressivism: Child-centered, experiential learning
- Constructivism: Active knowledge construction
- Critical pedagogy: Social justice and empowerment
- Humanism: Personal growth and self-actualization

**Learning Theories:**
- Behaviorism: Stimulus-response and conditioning
- Cognitivism: Information processing and mental structures
- Social learning: Observation and modeling
- Experiential learning: Reflection and application
- Multiple intelligences: Diverse learning styles

**Curriculum Development:**
- Content standards and learning objectives
- Scope and sequence planning
- Assessment and evaluation methods
- Differentiation for diverse learners
- Integration of technology and digital tools

**Teaching Methods:**
- Direct instruction and lecturing
- Inquiry-based and problem-solving approaches
- Collaborative and cooperative learning
- Project-based and experiential learning
- Personalized and adaptive instruction

**Educational Psychology:**
- Motivation and engagement strategies
- Memory and cognitive load theory
- Metacognition and self-regulated learning
- Emotional intelligence in education
- Learning disabilities and special education

**Assessment and Evaluation:**
- Formative vs summative assessment
- Standardized testing and accountability
- Performance-based assessment
- Portfolio assessment and authentic evaluation
- Grading systems and rubrics

**Educational Technology:**
- Learning management systems (LMS)
- Adaptive learning platforms
- Virtual and augmented reality
- Artificial intelligence tutoring systems
- Mobile learning and ubiquitous computing

**Inclusive Education:**
- Universal design for learning
- Multicultural education and diversity
- Gifted education and advanced learners
- English language learners support
- Students with disabilities accommodation

**Early Childhood Education:**
- Brain development and critical periods
- Play-based learning approaches
- Social-emotional development
- Language and literacy foundations
- Parent involvement and family engagement

**Higher Education:**
- Undergraduate and graduate education
- Research universities and liberal arts colleges
- Online and distance education
- Adult learning and continuing education
- Academic freedom and tenure

**Educational Policy:**
- Educational equity and access
- School funding and resource allocation
- Teacher quality and professional development
- Curriculum standards and accountability
- Education reform and innovation

**Global Education:**
- International education systems comparison
- UNESCO and global education goals
- Education for sustainable development
- Global citizenship education
- Cross-cultural understanding and exchange

**Lifelong Learning:**
- Adult education and workforce development
- Professional certification and credentialing
- Community education and enrichment
- Retirement learning and encore careers
- Personal development and self-directed learning

**Educational Research:**
- Evidence-based educational practices
- Program evaluation and effectiveness studies
- Educational neuroscience and brain-based learning
- Large-scale educational data analysis
- Action research and practitioner inquiry

**Contemporary Challenges:**
- Digital divide and educational technology access
- Student mental health and well-being
- Teacher shortages and retention
- School safety and crisis management
- Education during pandemics and disruptions
- Climate change education and environmental awareness
- Critical thinking and information literacy
- Social-emotional learning and character education""",
        "tags": ["education", "learning", "teaching", "curriculum", "assessment", "pedagogy"],
        "verified": True
    }
]


async def seed_comprehensive_knowledge():
    """
    Seed the Grokopedia database with comprehensive human knowledge entries
    """
    logger.info("Starting comprehensive knowledge seeding...")

    try:
        # Initialize the database
        from core.database import init_db
        await init_db()

        # Get database session
        async for db in get_db():
            # Initialize semantic search
            search_engine = SemanticSearch()

            entries_created = 0
            entries_skipped = 0

            for knowledge_entry in COMPREHENSIVE_KNOWLEDGE:
                try:
                    # Check if entry already exists
                    existing = await db.execute(
                        select(KnowledgeEntry).where(KnowledgeEntry.slug == knowledge_entry["title"].lower().replace(" ", "-"))
                    )
                    existing_entry = existing.scalar_one_or_none()

                    if existing_entry:
                        logger.info(f"Entry '{knowledge_entry['title']}' already exists, skipping...")
                        entries_skipped += 1
                        continue

                    # Create the knowledge entry
                    slug = knowledge_entry["title"].lower().replace(" ", "-").replace(",", "").replace("'", "")

                    # Generate embeddings for the entry
                    content_for_embedding = f"{knowledge_entry['title']}. {knowledge_entry['content']}"
                    embeddings = await search_engine.create_embedding(content_for_embedding)

                    # Create database entry
                    db_entry = KnowledgeEntry(
                        title=knowledge_entry["title"],
                        content=knowledge_entry["content"],
                        slug=slug,
                        tags=knowledge_entry["tags"],
                        verified=knowledge_entry["verified"],
                        embeddings=embeddings,
                        author_name="Galion AI Knowledge System",
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )

                    db.add(db_entry)
                    await db.commit()
                    await db.refresh(db_entry)

                    entries_created += 1
                    logger.info(f"Created entry: {knowledge_entry['title']}")

                except Exception as e:
                    logger.error(f"Failed to create entry '{knowledge_entry['title']}': {e}")
                    await db.rollback()
                    continue

            await db.close()

            logger.info(f"Comprehensive knowledge seeding completed!")
            logger.info(f"Entries created: {entries_created}")
            logger.info(f"Entries skipped: {entries_skipped}")
            logger.info(f"Total entries processed: {len(COMPREHENSIVE_KNOWLEDGE)}")

    except Exception as e:
        logger.error(f"Comprehensive knowledge seeding failed: {e}")
        raise


if __name__ == "__main__":
    # Run the seeding script
    asyncio.run(seed_comprehensive_knowledge())
