# 🎤 Ditado de Voz - IMPLEMENTADO

## ✅ Funcionalidade Implementada

Sistema de **ditado de voz para escrever no Cursor** usando MCP.

---

## 🎯 Como Funciona

### 1. **Ferramenta MCP `dictate_text`**

Ferramenta disponível globalmente no Cursor que:
- Captura áudio do microfone
- Converte para texto usando speech-to-text
- Retorna texto para inserção no editor

### 2. **Métodos de Reconhecimento**

Suporta múltiplos métodos (com fallback):
- ✅ **OpenAI Whisper API** (melhor qualidade, requer API key)
- ✅ **Google Speech Recognition** (gratuito, requer internet)
- ✅ **Whisper Local** (offline, requer instalação)

---

## 🚀 Como Usar

### No Cursor IDE:

```
Chat do Cursor:
"Escreva usando voz" ou "dictate text" ou "usar ditado"
```

**Parâmetros opcionais:**
- `duration`: Duração da gravação em segundos (padrão: 5)
- `language`: Idioma (padrão: pt-BR)
- `insert_mode`: Como inserir (insert, append, replace)

### Exemplo:

```
Usuário: "dictate_text usando MCP, duração 10 segundos"
→ Sistema grava 10 segundos
→ Converte para texto
→ Texto aparece no editor do Cursor
```

---

## 📋 Instalação de Dependências

### Opção 1: Google Speech Recognition (Mais Simples)

```bash
pip install SpeechRecognition pyaudio
```

### Opção 2: OpenAI Whisper (Melhor Qualidade)

```bash
pip install SpeechRecognition pyaudio openai
# Configure OPENAI_API_KEY
```

### Opção 3: Whisper Local (Offline)

```bash
pip install SpeechRecognition pyaudio whisper torch
```

---

## 🔧 Configuração

### Variáveis de Ambiente (Opcional):

```bash
# Para usar OpenAI Whisper
OPENAI_API_KEY=your-openai-key

# Idioma padrão (opcional)
VOICE_LANGUAGE=pt-BR
```

---

## 📝 Arquivos Criados

- ✅ `mcp_client/voice_handler.py` - Handler de voz
- ✅ `mcp_client/handlers.py` - Integração da ferramenta
- ✅ `requirements_voice.txt` - Dependências

---

## 🎯 Funcionalidades

### ✅ Captura de Áudio
- Grava do microfone padrão
- Duração configurável
- Suporte a múltiplos idiomas

### ✅ Conversão para Texto
- Múltiplos métodos (fallback automático)
- Alta qualidade com Whisper
- Gratuito com Google Speech

### ✅ Integração com Cursor
- Ferramenta MCP global
- Disponível em todas as abas
- Texto retornado para inserção

---

## 💡 Exemplos de Uso

### Uso Básico:
```
"dictate_text usando MCP"
→ Grava 5 segundos (padrão)
→ Converte para texto
→ Insere no cursor
```

### Uso Avançado:
```
"dictate_text usando MCP, duração 15 segundos, idioma en-US"
→ Grava 15 segundos em inglês
→ Converte para texto
→ Insere no cursor
```

---

## ⚠️ Requisitos

### Windows:
- Microfone funcionando
- Python com acesso ao microfone
- Bibliotecas instaladas (SpeechRecognition, pyaudio)

### Linux:
- `portaudio19-dev` instalado
- Microfone configurado

### macOS:
- Microfone com permissões
- Bibliotecas instaladas

---

## 🔍 Troubleshooting

### Erro: "No speech recognition methods available"
**Solução:** Instale dependências:
```bash
pip install SpeechRecognition pyaudio
```

### Erro: "Failed to record audio"
**Solução:** 
- Verifique se o microfone está funcionando
- Verifique permissões do sistema
- Teste com outro aplicativo

### Erro: "Não foi possível entender o áudio"
**Solução:**
- Fale mais claro
- Reduza ruído ambiente
- Aumente duração da gravação

---

## 📊 Status

- ✅ **Ferramenta MCP criada** (`dictate_text`)
- ✅ **Handler de voz implementado**
- ✅ **Múltiplos métodos de reconhecimento**
- ✅ **Integração com Cursor**
- ✅ **Disponível globalmente**

---

## 🎓 Próximos Passos (Opcional)

1. Adicionar preview do texto antes de inserir
2. Suporte a correção de texto ditado
3. Comandos de voz para formatação
4. Histórico de ditados

---

**Status:** ✅ DITADO DE VOZ IMPLEMENTADO  
**Versão:** 1.0.0  
**Disponível em:** Todas as abas do Cursor (global)

