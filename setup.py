from setuptools import setup, find_packages

setup(
    name="chapa-cli",
    version="2.0.0",
    description="Command-line tool for the Chapa Payment API v2",
    packages=find_packages(),
    install_requires=[
        "click>=8.1",
        "requests>=2.31",
        "rich>=13.0",
        "flask>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "chapa=chapa_cli.main:cli",
        ],
    },
)
