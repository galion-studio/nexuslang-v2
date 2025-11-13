#!/usr/bin/env python3
"""
Populate Grokopedia knowledge base via API
Uses HTTP requests to populate the knowledge base through API endpoints
"""

import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"

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
    }
]


def create_knowledge_entry(entry_data):
    """Create a knowledge entry via API"""
    url = f"{API_BASE_URL}/api/v2/grokopedia/entries"

    payload = {
        "title": entry_data["title"],
        "content": entry_data["content"],
        "tags": entry_data["tags"],
        "verified": entry_data["verified"]
    }

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            logger.info(f"✅ Created entry: {entry_data['title']}")
            return True
        else:
            logger.error(f"❌ Failed to create entry '{entry_data['title']}': {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error creating entry '{entry_data['title']}': {e}")
        return False


def main():
    """Main function to populate knowledge base"""
    logger.info("🚀 Starting comprehensive knowledge population via API...")
    logger.info(f"📚 Total entries to create: {len(COMPREHENSIVE_KNOWLEDGE)}")

    # Test API connectivity
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            logger.error("❌ API not accessible")
            return
    except Exception as e:
        logger.error(f"❌ Cannot connect to API: {e}")
        return

    logger.info("✅ API connection successful")

    # Create knowledge entries
    created_count = 0
    failed_count = 0

    for entry in COMPREHENSIVE_KNOWLEDGE:
        if create_knowledge_entry(entry):
            created_count += 1
        else:
            failed_count += 1

    logger.info("📊 Population Summary:")
    logger.info(f"   ✅ Created: {created_count}")
    logger.info(f"   ❌ Failed: {failed_count}")
    logger.info(f"   📈 Success Rate: {(created_count / len(COMPREHENSIVE_KNOWLEDGE)) * 100:.1f}%")

    if created_count > 0:
        logger.info("🎉 Grokopedia knowledge base populated successfully!")
    else:
        logger.error("💥 Failed to populate knowledge base")


if __name__ == "__main__":
    main()
