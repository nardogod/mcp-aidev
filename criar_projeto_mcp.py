"""
Script para criar um projeto usando a ferramenta MCP run_agent
"""
import sys
import json
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("CRIAR PROJETO USANDO MCP (run_agent) - MODO INTERATIVO")
print("=" * 60)
print()
print("Este script vai perguntar cada informacao e aguardar sua resposta.")
print("Pressione Enter apos cada resposta.")
print()

# Pergunta 1: Nome do projeto
print("=" * 60)
print("PERGUNTA 1: Nome do Projeto")
print("=" * 60)
project_name = input("Digite o nome do projeto: ").strip()

if not project_name:
    print("[ERRO] Nome do projeto e obrigatorio!")
    sys.exit(1)

print(f"\n[OK] Nome do projeto: {project_name}")
print()

# Pergunta 2: Descrição
print("=" * 60)
print("PERGUNTA 2: Descricao do Projeto")
print("=" * 60)
print("(Pressione Enter para deixar vazio)")
project_description = input("Digite a descricao do projeto: ").strip()

if project_description:
    print(f"\n[OK] Descricao: {project_description}")
else:
    print("\n[OK] Descricao: (vazio)")
print()

# Pergunta 3: Número máximo de fases
print("=" * 60)
print("PERGUNTA 3: Numero Maximo de Fases")
print("=" * 60)
print("(Pressione Enter para usar o padrao: 3)")
max_phases_input = input("Digite o numero maximo de fases: ").strip()

if max_phases_input:
    try:
        max_phases = int(max_phases_input)
        if max_phases < 1:
            print("[AVISO] Numero invalido. Usando padrao: 3")
            max_phases = 3
        else:
            print(f"\n[OK] Max fases: {max_phases}")
    except ValueError:
        print("[AVISO] Numero invalido. Usando padrao: 3")
        max_phases = 3
else:
    max_phases = 3
    print(f"\n[OK] Max fases: {max_phases} (padrao)")
print()

# Resumo
print("=" * 60)
print("RESUMO DA CONFIGURACAO")
print("=" * 60)
print(f"Projeto: {project_name}")
print(f"Descricao: {project_description or '(sem descricao)'}")
print(f"Max Fases: {max_phases}")
print()

# Confirmação
print("=" * 60)
print("CONFIRMACAO")
print("=" * 60)
confirmacao = input("Deseja continuar? (s/n): ").strip().lower()

if confirmacao not in ['s', 'sim', 'y', 'yes', '']:
    print("\nOperacao cancelada pelo usuario.")
    sys.exit(0)

print()
print("=" * 60)
print("CRIANDO PROJETO...")
print("=" * 60)
print("(Isso pode levar alguns segundos)")
print()

try:
    from mcp_client.handlers import MCPHandler
    
    # Criar handler
    handler = MCPHandler()
    
    # Inicializar
    print("1. Inicializando servidor MCP...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "create-project-client",
                "version": "1.0.0"
            }
        }
    }
    
    init_response = handler.handle_request(init_request)
    print(f"   [OK] Servidor inicializado")
    
    # Enviar notificação initialized
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    handler.handle_request(initialized_notification)
    print()
    
    # Chamar ferramenta run_agent
    print("2. Chamando ferramenta 'run_agent'...")
    print("   (Isso pode levar alguns segundos...)")
    print()
    
    run_agent_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "run_agent",
            "arguments": {
                "project_name": project_name,
                "project_description": project_description,
                "max_phases": max_phases
            }
        }
    }
    
    response = handler.handle_request(run_agent_request)
    
    # Processar resposta
    result = response.get("result", {})
    content = result.get("content", [])
    
    if content:
        text_content = content[0].get("text", "{}")
        try:
            agent_result = json.loads(text_content)
            
            print("=" * 60)
            print("PROJETO CRIADO COM SUCESSO!")
            print("=" * 60)
            print()
            print(f"Project ID: {agent_result.get('project_id', 'N/A')}")
            print(f"Project Name: {agent_result.get('project_name', 'N/A')}")
            print(f"Phases Planejadas: {agent_result.get('phases_planned', 0)}")
            print()
            
            phases = agent_result.get("phases", [])
            if phases:
                print("Fases criadas:")
                for phase in phases:
                    print(f"  - Fase {phase.get('number', 'N/A')}: {phase.get('title', 'N/A')} [{phase.get('status', 'N/A')}]")
            
            print()
            print("=" * 60)
            print("\nAgora voce pode listar os projetos:")
            print("  python listar_projetos_mcp.py")
            print("=" * 60)
            
        except json.JSONDecodeError:
            print("[AVISO] Resposta nao e JSON valido")
            print(f"Conteudo: {text_content[:500]}")
    else:
        print("[ERRO] Nenhum conteudo na resposta")
        print(f"Resposta completa: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
except Exception as e:
    print(f"[ERRO] Erro ao criar projeto: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

