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
        "rich"             # For beautiful terminal output 
        
    ],
    entry_points={
        "console_scripts": [
            "chapa=chapa_cli.main:cli",
        ],
    },
)




