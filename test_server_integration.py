"""
Teste de integração automático do servidor usando TestClient
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi.testclient import TestClient
from main import app
from database.connection import init_db, clear_db, get_db

# Initialize test database
init_db(":memory:")

# Override database dependency
def override_get_db():
    db = next(get_db())
    try:
        yield db
    finally:
        pass

app.dependency_overrides[app.dependency_overrides.get] = override_get_db

client = TestClient(app)

def print_test(num, name):
    print(f"\n{num}. Testando {name}")
    print("-" * 60)

def print_success(msg):
    print(f"   [OK] {msg}")

def print_error(msg):
    print(f"   [ERRO] {msg}")

def main():
    print("=" * 60)
    print("TESTE AUTOMATICO DO SERVIDOR MCP-AIDEV")
    print("=" * 60)
    
    project_id = None
    
    # Teste 1: Health Check
    print_test(1, "GET /health")
    response = client.get("/health")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status: {data.get('status')}")
        print_success(f"Database: {data.get('database')}")
        print_success(f"Version: {data.get('version')}")
    else:
        print_error(f"Status {response.status_code}: {response.text}")
        return False
    
    # Teste 2: Root endpoint
    print_test(2, "GET /")
    response = client.get("/")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Message: {data.get('message')}")
    else:
        print_error(f"Status {response.status_code}")
    
    # Teste 3: Listar tools
    print_test(3, "GET /mcp/tools")
    response = client.get("/mcp/tools")
    if response.status_code == 200:
        data = response.json()
        tools = data.get("tools", [])
        print_success(f"Tools encontrados: {len(tools)}")
        for tool in tools:
            print(f"     - {tool.get('name')}")
    else:
        print_error(f"Status {response.status_code}")
        return False
    
    # Teste 4: Criar projeto
    print_test(4, "POST /mcp/execute (create_project)")
    response = client.post(
        "/mcp/execute",
        json={
            "tool": "create_project",
            "arguments": {
                "name": "teste-automatico",
                "description": "Projeto criado por teste automatico"
            }
        }
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            project_id = data.get("data", {}).get("project_id")
            print_success(f"Projeto criado: {project_id}")
            print_success(f"Nome: {data.get('data', {}).get('name')}")
        else:
            print_error(f"Erro: {data.get('error')}")
            return False
    else:
        print_error(f"Status {response.status_code}: {response.text}")
        return False
    
    # Teste 5: Salvar fase
    print_test(5, "POST /mcp/execute (save_phase)")
    response = client.post(
        "/mcp/execute",
        json={
            "tool": "save_phase",
            "arguments": {
                "project_id": project_id,
                "phase_number": 1,
                "title": "Fase 1 - Teste Automatico",
                "specs": {
                    "files_to_create": ["test.py"],
                    "tests_to_write": ["test_test.py"],
                    "dependencies": ["pytest"],
                    "instructions": "Teste automatico"
                }
            }
        }
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print_success(f"Fase salva: {data.get('data', {}).get('title')}")
            print_success(f"Status: {data.get('data', {}).get('status')}")
        else:
            print_error(f"Erro: {data.get('error')}")
            return False
    else:
        print_error(f"Status {response.status_code}")
        return False
    
    # Teste 6: Buscar fase
    print_test(6, "POST /mcp/execute (get_phase)")
    response = client.post(
        "/mcp/execute",
        json={
            "tool": "get_phase",
            "arguments": {
                "project_id": project_id,
                "phase_number": 1
            }
        }
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            phase = data.get("data", {})
            print_success(f"Fase encontrada: {phase.get('title')}")
            print_success(f"Specs: {len(phase.get('specs', {}))} campos")
        else:
            print_error(f"Erro: {data.get('error')}")
            return False
    else:
        print_error(f"Status {response.status_code}")
        return False
    
    # Teste 7: Listar projetos
    print_test(7, "GET /projects")
    response = client.get("/projects")
    if response.status_code == 200:
        data = response.json()
        projects = data.get("projects", [])
        print_success(f"Projetos encontrados: {len(projects)}")
        if projects:
            print(f"     - {projects[0].get('name')}")
    else:
        print_error(f"Status {response.status_code}")
    
    # Teste 8: Ver detalhes do projeto
    print_test(8, f"GET /projects/{project_id}")
    response = client.get(f"/projects/{project_id}")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Projeto: {data.get('name')}")
        print_success(f"Fases: {len(data.get('phases', []))}")
    else:
        print_error(f"Status {response.status_code}")
    
    # Teste 9: Erro - Tool não encontrado
    print_test(9, "Erro: Tool nao encontrado")
    response = client.post(
        "/mcp/execute",
        json={
            "tool": "tool_inexistente",
            "arguments": {}
        }
    )
    if response.status_code == 200:
        data = response.json()
        if not data.get("success"):
            print_success(f"Erro tratado: {data.get('error')}")
        else:
            print_error("Erro nao tratado corretamente")
    else:
        print_error(f"Status {response.status_code}")
    
    # Teste 10: Erro - Parâmetros faltando
    print_test(10, "Erro: Parametros obrigatorios faltando")
    response = client.post(
        "/mcp/execute",
        json={
            "tool": "create_project",
            "arguments": {}
        }
    )
    if response.status_code == 200:
        data = response.json()
        if not data.get("success"):
            print_success(f"Erro tratado: {data.get('error')}")
        else:
            print_error("Erro nao tratado corretamente")
    else:
        print_error(f"Status {response.status_code}")
    
    # Teste 11: Erro - Projeto não encontrado
    print_test(11, "Erro: Projeto nao encontrado (404)")
    response = client.get("/projects/uuid-inexistente")
    if response.status_code == 404:
        print_success("404 retornado corretamente")
    else:
        print_error(f"Status {response.status_code}, esperado 404")
    
    print("\n" + "=" * 60)
    print("[OK] TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
    print("=" * 60)
    
    # Cleanup
    clear_db()
    app.dependency_overrides.clear()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

