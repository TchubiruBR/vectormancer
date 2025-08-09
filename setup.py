from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vectormancer",
    version="0.1.0",
    description="Local-first vector search for your files, notes, and code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Zhafira Elham",
    license="MIT",
    packages=find_packages(exclude=("tests", "examples", "docs")),
    python_requires=">=3.9",
    install_requires=[
        "numpy<2",                    # avoid NumPy 2.x breakage
        "click>=8.1.7",
        "pydantic>=2.6.0",
        "PyYAML>=6.0.0",
        "watchdog>=4.0.0",
        "faiss-cpu>=1.7.4; platform_system != 'Windows'",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",               # faster/safer HTML parsing for bs4
        "markdown-it-py>=3.0.0",
        "requests>=2.31.0",          # fetch <URL>
        "pdfplumber>=0.11.0",        # PDF text extraction
        "sentence-transformers>=3.0.0",
        "rich>=13.7.0",
    ],
    extras_require={
        "web": ["fastapi>=0.110.0", "uvicorn>=0.27.0", "python-multipart>=0.0.9"],
        "ocr": ["pdf2image>=1.17.0", "pytesseract>=0.3.10"],
    }, 
    entry_points={
        "console_scripts": [
            "vectormancer=vectormancer.cli.main:main",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Intended Audience :: Developers",
    ],
    project_urls={
        "Source": "https://github.com/ikanberjalandidarat/vectormancer",
        "Issues": "https://github.com/ikanberjalandidarat/vectormancer/issues",
    },
)
