# Uso Rápido do MCP Agent

## 🚀 Executar pelo Cursor (Recomendado)

Você pode executar o agente diretamente pelo Cursor usando as ferramentas MCP, **sem precisar mudar de diretório**:

### 1. Usando a ferramenta `run_agent` (já disponível)

```
Use a ferramenta MCP: run_agent
- project_name: "Meu Projeto"
- project_description: "Descrição do projeto"
- max_phases: 3
```

### 2. Usando a nova ferramenta `execute_agent_command`

```
Use a ferramenta MCP: execute_agent_command
- command: "agent"
- project_name: "Meu Projeto"
- project_description: "Descrição"
- max_phases: 3
```

## 💻 Executar pelo Terminal

### Opção 1: Script Batch (Windows)

```bash
# De qualquer diretório:
C:\LMM-proj\proj_mcp-aidev\mcp-agent.bat agent "Meu Projeto" "Descrição" 3

# Ou adicione ao PATH e use:
mcp-agent.bat agent "Meu Projeto"
```

### Opção 2: Script Python

```bash
# De qualquer diretório:
python C:\LMM-proj\proj_mcp-aidev\mcp_agent.py agent "Meu Projeto" "Descrição" 3
```

### Opção 3: Diretamente (precisa estar no diretório)

```bash
cd C:\LMM-proj\proj_mcp-aidev
python -m agent.main
```

## 📝 Adicionar ao PATH (Opcional)

Para usar `mcp-agent` de qualquer lugar:

1. Adicione `C:\LMM-proj\proj_mcp-aidev` ao PATH do Windows
2. Ou crie um alias/symlink

Depois você pode usar:

```bash
mcp-agent.bat agent "Meu Projeto"
```

## ✅ Vantagens

- ✅ **Pelo Cursor**: Use as ferramentas MCP - funciona de qualquer projeto
- ✅ **Pelo Terminal**: Use os scripts wrapper - não precisa mudar de diretório
- ✅ **Automático**: Os scripts encontram automaticamente o diretório do projeto
