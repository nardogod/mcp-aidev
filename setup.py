"""Setup script for mcp-aidev."""

from setuptools import setup, find_packages

setup(
    name="mcp-aidev",
    version="0.1.0",
    description="MCP Server para orquestrar workflows de desenvolvimento",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "sqlalchemy>=2.0.23",
        "aiosqlite>=0.19.0",
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "httpx>=0.25.2",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.11",
)

