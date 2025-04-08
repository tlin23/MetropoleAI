"""
Setup script for the metropole_crawler package.
"""

from setuptools import setup, find_packages

setup(
    name="metropole_crawler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
        "html2text>=2024.2.26",
        "tqdm>=4.66.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "requests-mock>=1.11.0",
        ],
    },
    python_requires=">=3.6",
    description="A structured webcrawler for the Metropole Ballard website",
    author="Metropole Team",
)
