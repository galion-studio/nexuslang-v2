"""
Setup configuration for NexusLang v2.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="nexuslang",
    version="2.0.0-beta",
    author="NexusLang Team",
    author_email="team@nexuslang.dev",
    description="AI-Native Programming Language for the 22nd Century",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/project-nexus",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Compilers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "numpy>=1.26.0",
        "rich>=13.7.0",
        "httpx>=0.25.0",
        "openai>=1.3.0",
        "openai-whisper>=20231117",
        "TTS>=0.20.0",
        "pyaudio>=0.2.13",
        "pydub>=0.25.1",
    ],
    entry_points={
        "console_scripts": [
            "nexuslang=nexuslang.cli.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nexuslang": ["examples/*.nx"],
    },
)

