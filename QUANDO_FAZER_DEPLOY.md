# Quando Fazer Deploy?

## ✅ **SIM, precisa fazer deploy** se você modificou:

### 1. **Código do Servidor Web/API** (`src/`)
- ✅ `src/services/project_service.py` - **SIM, precisa deploy**
- ✅ `src/mcp/protocol.py` - **SIM, precisa deploy**
- ✅ `src/mcp/tools.py` - **SIM, precisa deploy**
- ✅ `src/main.py` - **SIM, precisa deploy**
- ✅ `src/database/models.py` - **SIM, precisa deploy**

**Por quê?** Essas mudanças afetam o servidor em `https://mcp-aidev.onrender.com`

### 2. **Novas Ferramentas MCP no Servidor Web**
- ✅ `get_project_status` - **SIM, precisa deploy**
- ✅ `list_project_phases` - **SIM, precisa deploy**
- ✅ `get_current_phase` - **SIM, precisa deploy**

**Por quê?** Essas ferramentas são expostas via API HTTP no servidor remoto

---

## ❌ **NÃO precisa fazer deploy** se você modificou:

### 1. **Scripts Locais** (raiz do projeto)
- ❌ `executar_run_agent.py` - **NÃO precisa deploy**
- ❌ `criar_projeto_mcp.py` - **NÃO precisa deploy**
- ❌ `listar_projetos_mcp.py` - **NÃO precisa deploy**
- ❌ `status_projeto_*.py` - **NÃO precisa deploy**
- ❌ Qualquer script `.py` na raiz - **NÃO precisa deploy**

**Por quê?** Esses scripts rodam localmente na sua máquina

### 2. **MCP Client para Cursor** (`mcp_client/`)
- ❌ `mcp_client/handlers.py` - **NÃO precisa deploy** (mas precisa reiniciar Cursor)
- ❌ `mcp_client/server.py` - **NÃO precisa deploy** (mas precisa reiniciar Cursor)

**Por quê?** O MCP Client roda localmente no Cursor, não no servidor remoto

### 3. **Agent** (`agent/`)
- ❌ `agent/main.py` - **NÃO precisa deploy** (só se usar localmente)
- ❌ `agent/nodes.py` - **NÃO precisa deploy**
- ❌ `agent/tools.py` - **NÃO precisa deploy** (só se chamar servidor remoto)

**Por quê?** O agent roda localmente, mas pode chamar o servidor remoto

---

## 🔍 **Mudanças Feitas Recentemente**

### ✅ **Precisam Deploy:**
1. ✅ `src/services/project_service.py` - Novos métodos (`get_project_status`, `list_project_phases`, `get_current_phase`)
2. ✅ `src/mcp/tools.py` - Novas ferramentas MCP
3. ✅ `src/mcp/protocol.py` - Novos handlers

### ❌ **NÃO Precisam Deploy:**
1. ❌ `executar_run_agent.py` - Script local interativo
2. ❌ `criar_projeto_mcp.py` - Script local interativo
3. ❌ `mcp_client/handlers.py` - Client local (mas precisa reiniciar Cursor)

---

## 🚀 **Como Fazer Deploy**

### Opção 1: Deploy Automático (Render.com)

Se você tem o repositório conectado ao Render com `autoDeploy: true`:

1. **Commit as mudanças:**
   ```bash
   git add .
   git commit -m "Adiciona novas funcionalidades de gestão de projetos"
   git push
   ```

2. **Render faz deploy automaticamente** (se `autoDeploy: true`)

### Opção 2: Deploy Manual (Render.com)

1. Acesse o dashboard do Render: https://dashboard.render.com
2. Vá para o serviço `mcp-aidev`
3. Clique em **"Manual Deploy"** → **"Deploy latest commit"**

### Opção 3: Deploy via Railway

Se estiver usando Railway:

1. **Commit e push:**
   ```bash
   git add .
   git commit -m "Adiciona novas funcionalidades"
   git push
   ```

2. Railway detecta automaticamente e faz deploy

---

## ⚠️ **Importante**

### Para usar as novas ferramentas no servidor remoto:

**SIM, precisa fazer deploy** porque:
- As novas ferramentas (`get_project_status`, `list_project_phases`, `get_current_phase`) estão no código do servidor
- O servidor remoto precisa ter essas mudanças para funcionar
- Scripts que chamam a API HTTP precisam que o servidor tenha essas ferramentas

### Para usar scripts locais:

**NÃO precisa fazer deploy** porque:
- Scripts locais rodam na sua máquina
- Podem usar o banco de dados local ou chamar a API remota
- Mudanças em scripts locais não afetam o servidor remoto

---

## 🧪 **Como Verificar se Precisa Deploy**

### Teste Local:
```bash
# Testar servidor local
uvicorn src.main:app --reload --port 8000

# Em outro terminal, testar
curl http://localhost:8000/mcp/tools
# Deve listar as novas ferramentas
```

### Teste Remoto:
```bash
# Testar servidor remoto
curl https://mcp-aidev.onrender.com/mcp/tools
# Se não listar as novas ferramentas, precisa deploy
```

---

## 📝 **Resumo**

| Mudança | Precisa Deploy? | Por quê? |
|---------|----------------|----------|
| `src/services/project_service.py` | ✅ SIM | Código do servidor web |
| `src/mcp/tools.py` | ✅ SIM | Ferramentas MCP do servidor |
| `src/mcp/protocol.py` | ✅ SIM | Handlers do servidor |
| `executar_run_agent.py` | ❌ NÃO | Script local |
| `mcp_client/handlers.py` | ❌ NÃO | Client local (mas reinicia Cursor) |
| Scripts na raiz | ❌ NÃO | Rodam localmente |

---

## 🎯 **Recomendação**

**SIM, faça deploy** porque você adicionou novas funcionalidades no servidor web que precisam estar disponíveis no servidor remoto para funcionar completamente.

**Depois do deploy:**
- As novas ferramentas estarão disponíveis via API HTTP
- Scripts que chamam a API remota funcionarão
- O Cursor poderá usar as novas ferramentas MCP (se configurado)

