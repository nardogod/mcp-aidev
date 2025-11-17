# API Documentation

> Documentação da API do MCP Orchestrator

## Endpoints

### Health Check

```
GET /health
```

Retorna o status do servidor.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## MCP Tools

### 1. create_project

Cria um novo projeto no orquestrador.

**Input:**
```json
{
  "name": "string",
  "description": "string (opcional)"
}
```

**Output:**
```json
{
  "project_id": "uuid",
  "name": "string",
  "status": "active",
  "message": "Project created successfully"
}
```

---

### 2. save_phase

Salva especificações de uma fase do projeto.

**Input:**
```json
{
  "project_id": "string",
  "phase_number": "integer",
  "title": "string",
  "specs": {
    "files_to_create": ["array"],
    "tests_to_write": ["array"],
    "dependencies": ["array"],
    "instructions": "string"
  }
}
```

**Output:**
```json
{
  "phase_id": "uuid",
  "project_id": "uuid",
  "phase_number": 1,
  "status": "planned",
  "message": "Phase saved successfully"
}
```

---

### 3. get_phase

Recupera especificações de uma fase para implementação.

**Input:**
```json
{
  "project_id": "string",
  "phase_number": "integer"
}
```

**Output:**
```json
{
  "phase_id": "uuid",
  "project_id": "uuid",
  "phase_number": 1,
  "title": "string",
  "status": "planned",
  "specs": {
    "files_to_create": ["array"],
    "tests_to_write": ["array"],
    "dependencies": ["array"],
    "instructions": "string"
  }
}
```

---

### 4. update_progress

Atualiza o progresso de uma fase após implementação.

**Input:**
```json
{
  "project_id": "string",
  "phase_number": "integer",
  "status": "in_progress|completed",
  "progress_data": {
    "files_created": ["array"],
    "tests_passed": "integer",
    "tests_failed": "integer",
    "notes": "string"
  }
}
```

**Output:**
```json
{
  "phase_id": "uuid",
  "status": "completed",
  "message": "Progress updated successfully"
}
```

---

## Status Codes

- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

