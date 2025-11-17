# Comandos para Testar o Servidor MCP

## ✅ Comandos Disponíveis

### 1. Testar Servidor MCP (Simula Cursor)
```bash
python testar_mcp_cursor.py
```
**O que faz:** Inicia o servidor MCP como subprocesso e testa a comunicação stdio, simulando exatamente como o Cursor faria.

**Resultado esperado:** 
- Servidor inicia corretamente
- Responde ao comando `initialize`
- Lista ferramentas disponíveis
- Executa `health_check`

---

### 2. Testar Servidor MCP (Teste Interno)
```bash
python testar_mcp_server.py
```
**O que faz:** Testa o servidor MCP internamente, sem subprocesso.

**Resultado esperado:**
- Importa módulos corretamente
- Cria handler e servidor
- Executa métodos MCP
- Lista 5 ferramentas disponíveis

---

### 3. Ver Configuração Atual
```bash
python configurar_mcp_cursor.py --show
```
**O que faz:** Mostra a configuração atual do MCP no Cursor.

**Resultado esperado:**
- Mostra o caminho do arquivo de configuração
- Exibe o JSON completo da configuração

---

### 4. Reconfigurar Servidor MCP
```bash
python configurar_mcp_cursor.py
```
**O que faz:** Atualiza a configuração do servidor MCP no Cursor.

---

### 5. Testar Servidor Manualmente (stdio)
```bash
python -m mcp_client.server
```
**O que faz:** Inicia o servidor MCP em modo interativo. Você pode digitar comandos JSON-RPC manualmente.

**Como usar:**
1. Execute o comando
2. Digite um JSON-RPC request, por exemplo:
```json
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}
```
3. Pressione Enter
4. Veja a resposta

**Para sair:** Ctrl+C

---

### 6. Verificar se Python está no PATH
```bash
python --version
where python
```
**O que faz:** Verifica se o Python está acessível e mostra o caminho.

**Importante:** O Cursor precisa conseguir executar `python` diretamente.

---

### 7. Verificar Dependências
```bash
pip list | findstr groq
pip list | findstr langchain
```
**O que faz:** Verifica se as dependências necessárias estão instaladas.

---

### 8. Instalar/Atualizar Dependências
```bash
pip install -r requirements.txt
```
**O que faz:** Instala todas as dependências necessárias do projeto.

---

## 🔍 Como Verificar se Está Funcionando no Cursor

### Opção 1: Verificar Logs do Cursor
1. Abra o Cursor
2. Pressione `Ctrl+Shift+P` (paleta de comandos)
3. Digite: `MCP` ou `Model Context Protocol`
4. Procure por logs do servidor `mcp-aidev`

### Opção 2: Verificar Output Panel
1. No Cursor, vá em `View` → `Output`
2. Selecione `MCP` ou `mcp-aidev` no dropdown
3. Veja se há mensagens de inicialização

### Opção 3: Verificar Configurações
1. No Cursor, vá em `File` → `Preferences` → `Settings`
2. Procure por `mcp` nas configurações
3. Ou abra diretamente: `Ctrl+Shift+P` → `Preferences: Open User Settings (JSON)`
4. Procure por `mcpServers`

### Opção 4: Testar Ferramentas MCP
1. No chat do Cursor, tente usar uma ferramenta MCP
2. Por exemplo, digite algo como: "Listar projetos usando MCP"
3. O Cursor deve tentar usar a ferramenta `list_projects`

---

## 🐛 Solução de Problemas

### Problema: "Python não encontrado"
**Solução:**
```bash
# Verificar onde está o Python
where python

# Se não encontrar, adicionar ao PATH ou usar caminho completo na config
python configurar_mcp_cursor.py
# Edite o arquivo e use o caminho completo do Python
```

### Problema: "Module not found: mcp_client"
**Solução:**
```bash
# Certifique-se de estar no diretório do projeto
cd C:\LMM-proj\proj_mcp-aidev

# Verifique se o módulo existe
python -c "import mcp_client; print('OK')"
```

### Problema: Servidor não inicia no Cursor
**Solução:**
1. Verifique os logs do Cursor (Ctrl+Shift+P → MCP)
2. Teste manualmente: `python testar_mcp_cursor.py`
3. Verifique se o caminho `cwd` está correto na configuração
4. Tente usar caminho absoluto do Python na configuração

### Problema: Ferramentas não aparecem
**Solução:**
1. Reinicie o Cursor completamente
2. Verifique se o servidor está rodando nos logs
3. Teste: `python testar_mcp_server.py` (deve mostrar 5 ferramentas)
4. Verifique se há erros nos logs do Cursor

---

## 📝 Comandos Rápidos (Copiar e Colar)

```bash
# Teste completo
python testar_mcp_cursor.py

# Ver configuração
python configurar_mcp_cursor.py --show

# Teste interno
python testar_mcp_server.py

# Verificar Python
python --version

# Instalar dependências
pip install -r requirements.txt
```

---

## 💡 Dica

Se o servidor funciona nos testes mas não aparece no Cursor:
1. O problema geralmente é o PATH do Python
2. Tente usar o caminho completo do Python na configuração
3. Ou configure o Python no PATH do sistema Windows

