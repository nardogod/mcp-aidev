# MCP Orchestrator - mcp-aidev

> MCP Server web para orquestrar workflows de desenvolvimento entre Claude Web e Cursor

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Sobre o Projeto

O **mcp-aidev** é um servidor MCP (Model Context Protocol) que permite orquestrar workflows de desenvolvimento entre Claude Web e Cursor, facilitando o gerenciamento de projetos e fases de desenvolvimento.

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd mcp-aidev

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### Executar Localmente

```bash
# Execute o servidor
uvicorn src.main:app --reload --port 8000
```

O servidor estará disponível em `http://localhost:8000`

## 📚 Documentação

- [API Documentation](docs/API.md) - Documentação completa da API
- [MCP Protocol](https://modelcontextprotocol.io/) - Especificação do protocolo MCP

## 🏗️ Arquitetura

```
mcp-orchestrator/
├── src/
│   ├── main.py                 # FastAPI app + MCP endpoints
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── protocol.py         # MCP protocol implementation
│   │   └── tools.py            # Tool definitions
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py           # SQLAlchemy models
│   │   └── connection.py       # DB connection
│   └── services/
│       ├── __init__.py
│       └── project_service.py  # Business logic
├── tests/
│   ├── test_tools.py           # Testes dos 4 tools
│   ├── test_database.py        # Testes de persistência
│   └── test_mcp_protocol.py    # Testes do protocolo
├── docs/
│   └── API.md                  # Documentação da API
└── README.md
```

## 🛠️ MCP Tools

O servidor expõe 4 tools principais:

1. **create_project** - Cria novo projeto com metadata
2. **save_phase** - Salva especificação de uma fase
3. **get_phase** - Busca specs de fase para implementação
4. **update_progress** - Atualiza status após implementação

## 🧪 Testes

```bash
# Execute todos os testes
pytest

# Execute com coverage
pytest --cov=src tests/
```

## 📦 Deployment

### Railway (Recommended)

1. Fork this repository
2. Connect to [Railway](https://railway.app)
3. Create new project from GitHub repo
4. Railway will automatically detect Dockerfile
5. Deploy!

### Environment Variables

- `DATABASE_URL` - SQLite database path (default: `sqlite:///./data/mcp_aidev.db`)
- `ALLOWED_ORIGINS` - CORS origins, comma-separated (default: `*`)
- `PORT` - Server port (Railway sets this automatically)

### Manual Docker Deployment

```bash
# Build image
docker build -t mcp-aidev .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data mcp-aidev

# Test
curl http://localhost:8000/health
```

### Health Check

```bash
curl https://your-app.railway.app/health
```

## 📝 Licença

MIT License

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue antes de fazer mudanças significativas.

---

**Status:** 🚧 Em desenvolvimento (MVP)

