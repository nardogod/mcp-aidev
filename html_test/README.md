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
mcp-aidev/
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
├── agent/
│   ├── __init__.py
│   ├── main.py                 # LangGraph Agent entry point
│   ├── config.py               # Agent configuration
│   ├── llm.py                  # LLM abstraction (Groq/Claude/Ollama)
│   ├── state.py                # Agent state management
│   ├── tools.py                # MCP server integration
│   ├── nodes.py                # LangGraph nodes (plan/execute/review)
│   └── graph.py                # LangGraph workflow
├── mcp_client/
│   ├── __init__.py
│   ├── server.py               # MCP stdio server for Cursor
│   └── handlers.py             # MCP protocol handlers
├── tests/
│   ├── test_tools.py           # Testes dos 4 tools
│   ├── test_database.py        # Testes de persistência
│   ├── test_mcp_protocol.py    # Testes do protocolo
│   ├── test_agent.py           # Testes do LangGraph Agent
│   └── test_mcp_client.py      # Testes do MCP Client
├── docs/
│   └── API.md                  # Documentação da API
└── README.md
```

## 🛠️ MCP Tools

### Web Server (FastAPI)

O servidor web expõe 4 tools principais:

1. **create_project** - Cria novo projeto com metadata
2. **save_phase** - Salva especificação de uma fase
3. **get_phase** - Busca specs de fase para implementação
4. **update_progress** - Atualiza status após implementação

### Cursor MCP Client (stdio)

O cliente MCP para Cursor expõe 5 tools:

1. **run_agent** - Executa o LangGraph Agent para planejar fases do projeto
2. **get_phase** - Busca especificação de uma fase do servidor MCP
3. **list_projects** - Lista todos os projetos
4. **update_progress** - Atualiza progresso de uma fase
5. **health_check** - Verifica saúde do servidor MCP

## 🤖 LangGraph Agent

O projeto inclui um agente LangGraph que:

- **Planeja** fases de desenvolvimento usando LLM (Groq/Claude/Ollama)
- **Executa** salvando fases no servidor MCP
- **Revisa** e decide se continua para próxima fase
- **Loop** automático até completar todas as fases planejadas

### Uso do Agent

```bash
# Modo interativo
python -m agent.main

# Modo programático
python -c "from agent.main import run_agent; run_agent('meu-projeto', 'Descrição', max_phases=3)"
```

### Configuração do Agent

Configure no `.env`:

```bash
LLM_PROVIDER=groq  # ou anthropic, ollama
GROQ_API_KEY=your-key-here
MCP_SERVER_URL=https://mcp-aidev.onrender.com
LLM_MODEL=llama-3.3-70b-versatile  # opcional
```

## 🔌 Integração com Cursor

Para usar o MCP Client no Cursor:

1. Copie `cursor_config.json` para `~/.cursor/mcp.json` (ou equivalente no Windows)
2. Ajuste o caminho `cwd` e variáveis de ambiente
3. Reinicie o Cursor
4. O servidor MCP será iniciado automaticamente

As tools estarão disponíveis no Cursor para:
- Planejar projetos automaticamente
- Buscar especificações de fases
- Atualizar progresso

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

