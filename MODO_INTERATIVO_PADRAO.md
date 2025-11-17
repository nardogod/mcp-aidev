# Modo Interativo como Padrão

## ✅ Implementado

O modo interativo agora é o **padrão** para todos os scripts que executam o `run_agent`, independente do projeto.

## 📝 Scripts Atualizados

### 1. `executar_run_agent.py`
- **ANTES:** Usava valores hardcoded
- **AGORA:** Modo interativo por padrão
- Pergunta cada informação e aguarda resposta

### 2. `criar_projeto_mcp.py`
- **ANTES:** Tinha valores padrão com Enter
- **AGORA:** Modo interativo completo
- Pergunta cada informação e aguarda resposta
- Inclui confirmação antes de executar

## 🎯 Como Funciona

Quando você executar qualquer um desses scripts:

```bash
python executar_run_agent.py
# ou
python criar_projeto_mcp.py
```

O script vai:

1. **Perguntar o nome do projeto** (obrigatório)
   - Aguarda sua resposta
   - Valida se não está vazio

2. **Perguntar a descrição** (opcional)
   - Aguarda sua resposta
   - Aceita vazio

3. **Perguntar número máximo de fases** (opcional)
   - Aguarda sua resposta
   - Usa padrão 3 se vazio ou inválido

4. **Mostrar resumo** da configuração

5. **Pedir confirmação** antes de executar

6. **Executar** o `run_agent` com os parâmetros fornecidos

## 💡 Exemplo de Uso

```bash
$ python executar_run_agent.py

============================================================
EXECUTAR run_agent - MODO INTERATIVO (PADRAO)
============================================================

Este script vai perguntar cada informacao e aguardar sua resposta.
Pressione Enter apos cada resposta.

============================================================
PERGUNTA 1: Nome do Projeto
============================================================
Digite o nome do projeto: meu-projeto
[OK] Nome do projeto: meu-projeto

============================================================
PERGUNTA 2: Descricao do Projeto
============================================================
(Pressione Enter para deixar vazio)
Digite a descricao do projeto: Um projeto incrível
[OK] Descricao: Um projeto incrível

... e assim por diante
```

## 🔄 Compatibilidade

- ✅ Todos os scripts mantêm compatibilidade com chamadas programáticas
- ✅ O modo interativo é apenas para execução direta via terminal
- ✅ APIs e chamadas MCP continuam funcionando normalmente

## 📌 Notas

- O modo interativo só funciona quando executado diretamente no terminal
- Para automação, continue usando os parâmetros diretamente nas funções
- Todos os scripts agora têm o mesmo comportamento interativo consistente

