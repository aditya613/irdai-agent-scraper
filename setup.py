from setuptools import setup, find_packages

setup(
    name="irdai-agent-locator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "xmltodict",
        "pandas",
        "python-dotenv",
        "tqdm",
        "tenacity"
    ],
    author="Aditya Gupta",
    description="Python client and scraper for IRDAI public agent locator APIs",
    python_requires=">=3.9",
)