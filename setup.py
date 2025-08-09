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
        "click>=8.1.7",
        "pydantic>=2.6.0",
        "PyYAML>=6.0.0",
        "watchdog>=4.0.0",
        "faiss-cpu>=1.7.4; platform_system != 'Windows'",
        "pypdf>=4.0.0",
        "beautifulsoup4>=4.12.0",
        "markdown-it-py>=3.0.0",
        "sentence-transformers>=3.0.0",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "vectormancer=vectormancer.cli:main",
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
        "Source": "https://github.com/you/vectormancer",
        "Issues": "https://github.com/you/vectormancer/issues",
    },
)