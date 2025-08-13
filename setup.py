from setuptools import setup, find_packages

setup(
    name="chapa-cli",
    version="0.0.4",
    author="Israel Goytom",
    author_email="israel@chapa.co",
    description="A CLI tool for integrating with Chapa API.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Chapa-Et/chapa-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    
    install_requires=[
        "requests",        # For making HTTP requests
        "click",           # For creating CLI commands
        "flask",           # For webhook listener (optional)
        "pyngrok",         # For ngrok integration (optional)
        "rich",            # For beautiful terminal output 
        "pydantic>=2.0.0", # Data validation and parsing
        "email-validator>=2.0.0", # Email validation
        "phonenumbers>=8.13.0",    # Phone number validation
        "validators>=0.20.0",      # URL and other validators
        "tenacity>=8.2.0",         # Retry logic with backoff
        "python-dotenv>=1.0.0",    # Environment variable loading
    ],
    extras_require={
        "dev": [
            "requests-mock",   # For mocking HTTP requests in tests
            "pytest",          # Testing framework
            "pytest-cov",      # Coverage reporting
        ]
    },
    entry_points={
        "console_scripts": [
            "chapa=chapa_cli.main:cli",
        ],
    },
)




