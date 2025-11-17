# Comandos MCP Rápidos

## 📋 Listar Projetos
```bash
python listar_projetos_mcp.py
```
**O que faz:** Lista todos os projetos cadastrados no servidor MCP usando a ferramenta `list_projects`.

---

## 🆕 Criar Projeto
```bash
python criar_projeto_mcp.py
```
**O que faz:** Cria um novo projeto usando a ferramenta `run_agent` do MCP. O script pedirá:
- Nome do projeto
- Descrição do projeto  
- Número máximo de fases

**Exemplo de uso:**
```bash
python criar_projeto_mcp.py
# Digite: "meu-projeto"
# Digite: "Descrição do projeto"
# Digite: "3" (ou Enter para padrão)
```

---

## 🔍 Buscar Fase Específica
```bash
python get_phase_script.py
```
**O que faz:** Busca uma fase específica de um projeto usando `get_phase`.

**Nota:** Você precisa editar o script para definir o `project_id` e `phase_number`.

---

## ✅ Testar Servidor MCP
```bash
python testar_mcp_server.py
```
**O que faz:** Testa se o servidor MCP está funcionando corretamente.

---

## 🔧 Ver Configuração
```bash
python configurar_mcp_cursor.py --show
```
**O que faz:** Mostra a configuração atual do MCP no Cursor.

---

## 💡 Uso no Chat do Cursor

Depois de reiniciar o Cursor, você pode usar diretamente no chat:

- **"Listar projetos usando MCP"**
- **"Criar um projeto chamado 'teste' usando MCP"**
- **"Fazer health check do servidor MCP"**
- **"Buscar fase 1 do projeto [project-id] usando MCP"**

---

## 📝 Fluxo Completo

1. **Criar projeto:**
   ```bash
   python criar_projeto_mcp.py
   ```

2. **Listar projetos:**
   ```bash
   python listar_projetos_mcp.py
   ```

3. **Buscar fase:**
   ```bash
   python get_phase_script.py
   ```
   (Edite o script com o project_id retornado)

---

## 🎯 Resumo

| Ação | Comando |
|------|---------|
| Listar projetos | `python listar_projetos_mcp.py` |
| Criar projeto | `python criar_projeto_mcp.py` |
| Buscar fase | `python get_phase_script.py` |
| Testar servidor | `python testar_mcp_server.py` |
| Ver config | `python configurar_mcp_cursor.py --show` |

