"""
Setup script for the Guardian API Client package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="guardian-api-client",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A client for retrieving articles from the Guardian API and publishing to message brokers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/guardian-api-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "boto3>=1.18.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "flake8>=3.0.0",
            "mypy>=0.800",
            "black>=22.0.0",
        ],
    },
)