from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="deepexec-sdk",
    version="0.1.0",
    author="DeepGeek Team",
    author_email="info@deepgeek.com",
    description="Python SDK for interacting with the DeepExec service using the MCP protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deepgeek/deepexec-sdk",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-asyncio>=0.21.0,<0.22.0",
            "pytest-cov>=4.1.0,<5.0.0",
            "mypy>=1.0.0,<2.0.0",
            "flake8>=6.0.0,<7.0.0",
            "black>=23.0.0,<24.0.0",
            "isort>=5.12.0,<6.0.0",
            "coverage>=7.2.0,<8.0.0",
            "tox>=4.0.0,<5.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0,<8.0.0",
            "sphinx-rtd-theme>=1.2.0,<2.0.0",
            "sphinx-autodoc-typehints>=1.23.0,<2.0.0",
            "m2r2>=0.3.2,<0.4.0",
        ],
    },
)
