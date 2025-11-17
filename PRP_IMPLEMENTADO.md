# ✅ PRP (Product Requirements Planning) - IMPLEMENTADO

## 📋 O Que É PRP?

**PRP (Product Requirements Planning)** é um sistema que:
1. **Pergunta preferências** ao criar um novo projeto
2. **Registra essas preferências** no banco de dados para aquele projeto específico
3. **Usa padrões de mercado** quando não especificado (melhores práticas)

---

## 🎯 Funcionalidades Implementadas

### 1. **Coleta de Preferências**

O sistema pergunta sobre:
- ✅ Linguagem de programação
- ✅ Framework preferido
- ✅ Padrão de arquitetura
- ✅ Framework de testes
- ✅ Banco de dados
- ✅ Nível de segurança
- ✅ Type hints
- ✅ Cobertura de testes mínima
- ✅ Linting e formatação
- ✅ Plataforma de deploy

### 2. **Padrões de Mercado**

Quando não especificado, usa:
- **Python:** Python 3.11, pytest, PEP 8, type hints
- **JavaScript/TypeScript:** Jest/Vitest, Airbnb style
- **Arquitetura:** MVC para FastAPI/Django, Component-based para React/Vue
- **Banco de dados:** SQLite para desenvolvimento
- **Segurança:** Nível standard
- **Testes:** 80% de cobertura mínima
- **Linting/Formatação:** Ativado por padrão

### 3. **Armazenamento**

Preferências são salvas no banco de dados:
- Campo `preferences` (JSON) no modelo `Project`
- Persistido para cada projeto
- Usado em todas as fases do projeto

---

## 🔄 Como Funciona

### Fluxo Completo:

```
1. Criar Projeto
   ↓
2. Coletar PRP (preferências)
   ├─ Modo Interativo: Pergunta ao usuário
   └─ Modo Auto: Auto-detecta ou usa padrões
   ↓
3. Salvar Preferências no Banco
   ↓
4. Usar Preferências no Planejamento
   ├─ Contexto para LLM
   ├─ Especificações de fases
   └─ Implementação automática
```

---

## 📝 Exemplo de Uso

### Modo Interativo:

```bash
$ python executar_projeto_completo.py

============================================================
EXECUTOR AUTOMATICO COMPLETO DE PROJETOS
============================================================

Projeto: calculadora
Descricao: Calculadora simples em Python

📋 Coletando preferencias do projeto (PRP)...
   (Usando padroes de mercado se nao especificado)

======================================================================
PRP - PRODUCT REQUIREMENTS PLANNING
======================================================================

Vamos coletar suas preferencias para este projeto.
Pressione Enter para usar padroes de mercado (recomendado).

----------------------------------------------------------------------
1. LINGUAGEM DE PROGRAMACAO
----------------------------------------------------------------------
Opcoes: python, javascript, typescript, java, go, rust
(Enter para auto-detectar baseado na descricao)
Linguagem: python

2. FRAMEWORK PYTHON
Opcoes: fastapi, django, flask, none
(Enter para usar: fastapi - padrao mercado)
Framework: [Enter]  # Usa fastapi

3. PADRAO DE ARQUITETURA
(Enter para usar padrao baseado no framework)
Arquitetura: [Enter]  # Usa MVC

... (outras perguntas)

======================================================================
RESUMO DAS PREFERENCIAS
======================================================================
Linguagem: python
Framework: fastapi
Arquitetura: mvc
Testes: pytest
Banco de dados: sqlite
Seguranca: standard
Type hints: Sim
Cobertura testes: 80%
Linting: Sim
Formatacao: Sim
======================================================================
```

### Modo Auto (Não-Interativo):

```python
from agent.prp import PRPCollector

# Auto-detecta baseado na descrição
prefs = PRPCollector.collect_preferences_auto(
    "api-rest",
    "API REST em FastAPI com autenticação"
)

# Resultado:
# - Linguagem: python (detectado)
# - Framework: fastapi (detectado)
# - Outros: padrões de mercado aplicados
```

---

## 🗄️ Estrutura no Banco de Dados

### Modelo Project Atualizado:

```python
class Project(Base):
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    preferences = Column(JSON, nullable=True)  # ⭐ NOVO: PRP
    status = Column(String(50), default="active")
    ...
```

### Exemplo de JSON Salvo:

```json
{
  "programming_language": "python",
  "framework": "fastapi",
  "architecture_pattern": "mvc",
  "testing_framework": "pytest",
  "database_type": "sqlite",
  "security_level": "standard",
  "use_type_hints": true,
  "test_coverage_min": 80,
  "use_linting": true,
  "use_formatting": true
}
```

---

## 🎯 Uso no Planejamento de Fases

As preferências são usadas como contexto para o LLM:

```python
# No plan_node (agent/nodes.py)
if state.project_preferences:
    prp_context = PRPCollector.preferences_to_prompt_context(prefs)
    context += f"\n\nProject Requirements (PRP):\n{prp_context}\n"
```

**Resultado:** O LLM planeja fases seguindo as preferências do projeto!

---

## 📊 Padrões de Mercado Aplicados

### Python:
- ✅ Python 3.11+
- ✅ pytest para testes
- ✅ PEP 8 para estilo
- ✅ Type hints habilitado
- ✅ Linting e formatação ativados

### JavaScript/TypeScript:
- ✅ Jest/Vitest para testes
- ✅ Airbnb style guide
- ✅ TypeScript com type checking

### Arquitetura:
- ✅ MVC para FastAPI/Django
- ✅ Component-based para React/Vue
- ✅ Layered para projetos genéricos

### Qualidade:
- ✅ 80% cobertura de testes mínima
- ✅ Linting ativado
- ✅ Formatação automática
- ✅ Segurança nível standard

---

## 🔧 Integração com Sistema Existente

### 1. **executar_projeto_completo.py**
- ✅ Coleta PRP antes de criar projeto
- ✅ Salva preferências no estado
- ✅ Usa preferências no planejamento

### 2. **agent/nodes.py**
- ✅ Usa preferências como contexto para LLM
- ✅ Planeja fases seguindo preferências

### 3. **agent/implementer.py**
- ✅ Pode usar preferências na implementação
- ✅ Segue padrões definidos

### 4. **src/database/models.py**
- ✅ Campo `preferences` adicionado
- ✅ Persistência no banco

---

## 🎓 Benefícios

1. **Consistência:** Todos os projetos seguem padrões definidos
2. **Flexibilidade:** Pode customizar por projeto
3. **Padrões de Mercado:** Usa melhores práticas quando não especificado
4. **Rastreabilidade:** Preferências salvas para referência futura
5. **Automação:** Menos decisões manuais, mais automação

---

## 📝 Exemplo Completo

```python
# 1. Coletar preferências
prefs = PRPCollector.collect_preferences_interactive(
    "api-rest",
    "API REST em FastAPI"
)

# 2. Criar projeto com preferências
state = AgentState(
    project_name="api-rest",
    project_description="API REST em FastAPI",
    project_preferences=prefs.to_dict()
)

# 3. Planejar fases (usa preferências)
graph = create_auto_agent_graph()
result = graph.invoke(state)

# 4. Preferências são usadas em todas as fases!
```

---

## ✅ Status

- ✅ **PRP Module criado** (`agent/prp.py`)
- ✅ **Coleta interativa implementada**
- ✅ **Coleta automática implementada**
- ✅ **Padrões de mercado aplicados**
- ✅ **Integração com banco de dados**
- ✅ **Uso no planejamento de fases**
- ✅ **Documentação completa**

---

**Status:** ✅ PRP IMPLEMENTADO E FUNCIONAL  
**Versão:** 1.0.0  
**Data:** Agora

