"""
Executor Automático Completo de Projetos

Este script executa um projeto completo do início ao fim:
1. Planeja todas as fases
2. Implementa cada fase automaticamente
3. Executa testes
4. Atualiza progresso
5. Continua até completar todas as fases

SEM INTERAÇÃO HUMANA!
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.graph_auto import create_auto_agent_graph
from agent.state import AgentState
from agent.config import config
from agent.tools import MCPTools
from agent.prp import PRPCollector, ProjectPreferences


def executar_projeto_completo(
    project_name: str,
    project_description: str,
    max_phases: int = None,
    project_path: str = None,
    auto_mode: bool = True
):
    """
    Executa um projeto completo automaticamente.
    
    Args:
        project_name: Nome do projeto
        project_description: Descrição do projeto
        max_phases: Número máximo de fases (padrão: 3)
        project_path: Caminho base para criar arquivos (padrão: ./projects/{project_name})
        auto_mode: Se True, implementa automaticamente. Se False, apenas planeja.
    """
    print("=" * 70)
    print("EXECUTOR AUTOMATICO COMPLETO DE PROJETOS")
    print("=" * 70)
    print()
    print(f"Projeto: {project_name}")
    print(f"Descricao: {project_description}")
    print(f"Modo: {'AUTOMATICO (implementa tudo)' if auto_mode else 'PLANEJAMENTO APENAS'}")
    print()
    
    # Configurar
    if max_phases:
        config.max_phases = max_phases
    else:
        config.max_phases = 3  # Padrão
    
    if project_path:
        config.project_base_path = project_path
    else:
        # Criar diretório do projeto
        project_dir = Path.cwd() / "projects" / project_name.lower().replace(" ", "_")
        project_dir.mkdir(parents=True, exist_ok=True)
        config.project_base_path = str(project_dir)
    
    print(f"Diretorio do projeto: {config.project_base_path}")
    print(f"Max fases: {config.max_phases}")
    print()
    print("-" * 70)
    print()
    
    # Verificar saúde do servidor MCP
    mcp = MCPTools(config.mcp_server_url)
    if not mcp.health_check():
        print(f"⚠️  AVISO: Servidor MCP em {config.mcp_server_url} nao esta respondendo")
        print("   Continuando mesmo assim...")
        print()
    
    # Coletar PRP (Product Requirements Planning)
    print("📋 Coletando preferencias do projeto (PRP)...")
    print("   (Usando padroes de mercado se nao especificado)")
    print()
    
    # Modo interativo: perguntar preferências
    # Modo não-interativo: auto-detectar ou usar padrões
    try:
        prefs = PRPCollector.collect_preferences_interactive(project_name, project_description)
    except (EOFError, KeyboardInterrupt):
        # Se não for interativo, usar auto-detecção
        print("   Usando auto-deteccao e padroes de mercado...")
        prefs = PRPCollector.collect_preferences_auto(project_name, project_description)
    
    # Criar estado inicial com preferências
    initial_state = AgentState(
        project_name=project_name,
        project_description=project_description,
        project_preferences=prefs.to_dict() if isinstance(prefs, ProjectPreferences) else prefs
    )
    
    # Criar e executar o grafo
    if auto_mode:
        print("🚀 INICIANDO EXECUCAO AUTOMATICA COMPLETA...")
        print()
        graph = create_auto_agent_graph()
    else:
        print("📋 INICIANDO PLANEJAMENTO APENAS...")
        print()
        from agent.graph import create_agent_graph
        graph = create_agent_graph()
    
    # Executar
    try:
        result = graph.invoke(initial_state)
        
        # Converter resultado para AgentState se necessário
        if isinstance(result, dict):
            final_state = AgentState.from_dict(result)
        else:
            final_state = result
        
        # Resumo final
        print()
        print("=" * 70)
        print("RESUMO FINAL")
        print("=" * 70)
        print()
        print(f"✅ Projeto ID: {final_state.project_id}")
        print(f"✅ Fases planejadas: {len(final_state.phases)}")
        print()
        
        # Estatísticas de implementação
        completed = sum(1 for p in final_state.phases if p.status == "completed")
        saved = sum(1 for p in final_state.phases if p.status == "saved")
        planned = sum(1 for p in final_state.phases if p.status == "planned")
        
        print("Status das fases:")
        print(f"  ✅ Completadas: {completed}")
        print(f"  💾 Salvas (não implementadas): {saved}")
        print(f"  📋 Planejadas: {planned}")
        print()
        
        print("Detalhes das fases:")
        for phase in final_state.phases:
            status_icon = {
                "completed": "✅",
                "saved": "💾",
                "planned": "📋",
                "failed": "❌"
            }.get(phase.status, "❓")
            
            print(f"  {status_icon} Fase {phase.number}: {phase.title} [{phase.status}]")
        
        print()
        
        if final_state.error:
            print(f"⚠️  Erros encontrados: {final_state.error}")
            print()
        
        print(f"📁 Arquivos criados em: {config.project_base_path}")
        print()
        print("=" * 70)
        
        return final_state
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO NA EXECUCAO")
        print("=" * 70)
        print(f"Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        raise


def modo_interativo():
    """Modo interativo para configurar o projeto"""
    print("=" * 70)
    print("EXECUTOR AUTOMATICO COMPLETO DE PROJETOS")
    print("=" * 70)
    print()
    
    project_name = input("Nome do projeto: ").strip()
    if not project_name:
        print("❌ Nome do projeto e obrigatorio!")
        return
    
    project_description = input("Descricao do projeto: ").strip()
    
    max_phases_input = input("Numero maximo de fases (padrao 3): ").strip()
    max_phases = int(max_phases_input) if max_phases_input else 3
    
    project_path_input = input("Caminho do projeto (Enter para usar padrao): ").strip()
    project_path = project_path_input if project_path_input else None
    
    modo_input = input("Modo automatico? (s/N): ").strip().lower()
    auto_mode = modo_input == "s"
    
    print()
    print("=" * 70)
    print("CONFIRMACAO")
    print("=" * 70)
    print(f"Projeto: {project_name}")
    print(f"Descricao: {project_description}")
    print(f"Max fases: {max_phases}")
    print(f"Modo: {'AUTOMATICO' if auto_mode else 'PLANEJAMENTO APENAS'}")
    print()
    
    confirm = input("Confirmar execucao? (s/N): ").strip().lower()
    if confirm != "s":
        print("Cancelado.")
        return
    
    print()
    executar_projeto_completo(
        project_name=project_name,
        project_description=project_description,
        max_phases=max_phases,
        project_path=project_path,
        auto_mode=auto_mode
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo não-interativo com argumentos
        project_name = sys.argv[1]
        project_description = sys.argv[2] if len(sys.argv) > 2 else ""
        max_phases = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        auto_mode = sys.argv[4].lower() == "true" if len(sys.argv) > 4 else True
        
        executar_projeto_completo(
            project_name=project_name,
            project_description=project_description,
            max_phases=max_phases,
            auto_mode=auto_mode
        )
    else:
        # Modo interativo
        modo_interativo()

