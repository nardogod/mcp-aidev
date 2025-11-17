"""
Script para listar projetos usando a ferramenta MCP list_projects
"""
import sys
import json
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("LISTAR PROJETOS USANDO MCP")
print("=" * 60)
print()

try:
    from mcp_client.handlers import MCPHandler
    
    # Criar handler
    handler = MCPHandler()
    
    # Inicializar (necessário antes de usar ferramentas)
    print("1. Inicializando servidor MCP...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "list-projects-client",
                "version": "1.0.0"
            }
        }
    }
    
    init_response = handler.handle_request(init_request)
    print(f"   [OK] Servidor inicializado: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'N/A')}")
    print()
    
    # Enviar notificação initialized
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    handler.handle_request(initialized_notification)
    
    # Chamar ferramenta list_projects
    print("2. Chamando ferramenta 'list_projects'...")
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_projects",
            "arguments": {}
        }
    }
    
    response = handler.handle_request(list_request)
    
    # Processar resposta
    result = response.get("result", {})
    content = result.get("content", [])
    
    if content:
        # O conteúdo geralmente vem como texto JSON
        text_content = content[0].get("text", "{}")
        try:
            projects_data = json.loads(text_content)
            projects = projects_data.get("projects", [])
            
            print(f"   [OK] Resposta recebida")
            print()
            print("=" * 60)
            print(f"PROJETOS ENCONTRADOS: {len(projects)}")
            print("=" * 60)
            
            if projects:
                for i, project in enumerate(projects, 1):
                    print(f"\n{i}. {project.get('name', 'Sem nome')}")
                    print(f"   ID: {project.get('project_id', 'N/A')}")
                    print(f"   Status: {project.get('status', 'N/A')}")
                    if project.get('description'):
                        print(f"   Descricao: {project.get('description', '')[:80]}...")
                    if project.get('created_at'):
                        print(f"   Criado em: {project.get('created_at', 'N/A')}")
                    
                    # Mostrar estatisticas de fases (se disponivel)
                    if 'phases_count' in project:
                        print(f"\n   ESTATISTICAS DE FASES:")
                        print(f"     Total de fases: {project.get('phases_count', 0)}")
                        print(f"     Completadas: {project.get('phases_completed', 0)}")
                        print(f"     Em progresso: {project.get('phases_in_progress', 0)}")
                        print(f"     Planejadas: {project.get('phases_planned', 0)}")
                        print(f"     Progresso: {project.get('progress_percentage', 0)}%")
                        
                        if project.get('current_phase'):
                            cp = project['current_phase']
                            print(f"\n   FASE ATUAL:")
                            print(f"     Fase {cp.get('phase_number')}: {cp.get('title')}")
                            print(f"     Status: {cp.get('status')}")
            else:
                print("\nNenhum projeto encontrado no banco de dados.")
                print("\nPara criar um projeto, use:")
                print("  python -c \"from agent.main import run_agent; run_agent('meu-projeto', 'Descricao')\"")
            
            print("\n" + "=" * 60)
            
        except json.JSONDecodeError:
            print("   [AVISO] Resposta nao e JSON valido")
            print(f"   Conteudo: {text_content[:200]}")
    else:
        print("   [AVISO] Nenhum conteudo na resposta")
        print(f"   Resposta completa: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
except Exception as e:
    print(f"[ERRO] Erro ao listar projetos: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

