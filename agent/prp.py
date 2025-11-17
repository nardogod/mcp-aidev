"""
PRP (Product Requirements Planning) Module

Coleta e gerencia preferências e requisitos por projeto.
Se não especificado, usa padrões de mercado e melhores práticas.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json


@dataclass
class ProjectPreferences:
    """
    Preferências e requisitos do projeto.
    Se não especificado, usa padrões de mercado.
    """
    # Linguagem e Framework
    programming_language: Optional[str] = None  # python, javascript, typescript, etc.
    framework: Optional[str] = None  # fastapi, django, react, vue, etc.
    python_version: Optional[str] = None  # 3.11, 3.12, etc.
    node_version: Optional[str] = None  # 18, 20, etc.
    
    # Arquitetura e Padrões
    architecture_pattern: Optional[str] = None  # mvc, mvp, clean-architecture, etc.
    code_style: Optional[str] = None  # pep8, airbnb, google, etc.
    use_type_hints: Optional[bool] = None  # True/False
    use_async: Optional[bool] = None  # True/False
    
    # Testes e Qualidade
    testing_framework: Optional[str] = None  # pytest, unittest, jest, vitest, etc.
    test_coverage_min: Optional[int] = None  # 80, 90, etc.
    use_linting: Optional[bool] = None  # True/False
    use_formatting: Optional[bool] = None  # True/False
    
    # Banco de Dados
    database_type: Optional[str] = None  # sqlite, postgresql, mongodb, etc.
    use_orm: Optional[str] = None  # sqlalchemy, django-orm, prisma, etc.
    
    # Segurança
    security_level: Optional[str] = None  # basic, standard, high
    use_authentication: Optional[bool] = None  # True/False
    use_authorization: Optional[bool] = None  # True/False
    
    # Deploy e DevOps
    deployment_platform: Optional[str] = None  # render, railway, vercel, docker, etc.
    use_ci_cd: Optional[bool] = None  # True/False
    use_docker: Optional[bool] = None  # True/False
    
    # Bibliotecas e Dependências
    preferred_libraries: Optional[List[str]] = None  # Lista de bibliotecas preferidas
    
    # Outros
    documentation_style: Optional[str] = None  # sphinx, mkdocs, jsdoc, etc.
    api_style: Optional[str] = None  # rest, graphql, grpc, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectPreferences':
        """Create from dictionary"""
        if not data:
            return cls()
        # Filter only valid fields and handle None values
        valid_data = {}
        for k, v in data.items():
            if hasattr(cls, k):
                valid_data[k] = v
        return cls(**valid_data)
    
    def apply_market_standards(self):
        """
        Aplica padrões de mercado quando não especificado.
        Usa melhores práticas da indústria.
        """
        # Python padrões
        if self.programming_language == "python" or not self.programming_language:
            if not self.python_version:
                self.python_version = "3.11"  # Padrão mercado
            if not self.testing_framework:
                self.testing_framework = "pytest"  # Padrão mercado
            if not self.code_style:
                self.code_style = "pep8"  # Padrão mercado
            if self.use_type_hints is None:
                self.use_type_hints = True  # Melhor prática
            if not self.use_linting:
                self.use_linting = True  # Melhor prática
            if not self.use_formatting:
                self.use_formatting = True  # Melhor prática
        
        # JavaScript/TypeScript padrões
        if self.programming_language in ["javascript", "typescript"]:
            if not self.testing_framework:
                self.testing_framework = "jest" if self.programming_language == "javascript" else "vitest"
            if not self.code_style:
                self.code_style = "airbnb"  # Padrão mercado
            if self.use_type_hints is None and self.programming_language == "typescript":
                self.use_type_hints = True
        
        # Arquitetura padrão
        if not self.architecture_pattern:
            if self.framework == "fastapi":
                self.architecture_pattern = "mvc"
            elif self.framework == "django":
                self.architecture_pattern = "mvc"
            elif self.framework in ["react", "vue"]:
                self.architecture_pattern = "component-based"
            else:
                self.architecture_pattern = "layered"  # Padrão genérico
        
        # Banco de dados padrão
        if not self.database_type:
            self.database_type = "sqlite"  # Padrão para desenvolvimento
        
        # Segurança padrão
        if not self.security_level:
            self.security_level = "standard"  # Padrão mercado
        
        # Testes padrão
        if not self.test_coverage_min:
            self.test_coverage_min = 80  # Padrão mercado
        
        # Documentação padrão
        if not self.documentation_style:
            if self.programming_language == "python":
                self.documentation_style = "sphinx"
            else:
                self.documentation_style = "markdown"
        
        # API padrão
        if not self.api_style:
            self.api_style = "rest"  # Padrão mercado


class PRPCollector:
    """
    Coletor de PRP (Product Requirements Planning).
    Pergunta preferências ao usuário e aplica padrões quando não especificado.
    """
    
    @staticmethod
    def collect_preferences_interactive(project_name: str, project_description: str) -> ProjectPreferences:
        """
        Coleta preferências interativamente do usuário.
        Se não especificado, usa padrões de mercado.
        
        Args:
            project_name: Nome do projeto
            project_description: Descrição do projeto
            
        Returns:
            ProjectPreferences com preferências coletadas
        """
        print("\n" + "=" * 70)
        print("PRP - PRODUCT REQUIREMENTS PLANNING")
        print("=" * 70)
        print()
        print("Vamos coletar suas preferencias para este projeto.")
        print("Pressione Enter para usar padroes de mercado (recomendado).")
        print()
        
        prefs = ProjectPreferences()
        
        # 1. Linguagem de Programação
        print("-" * 70)
        print("1. LINGUAGEM DE PROGRAMACAO")
        print("-" * 70)
        print("Opcoes: python, javascript, typescript, java, go, rust")
        print("(Enter para auto-detectar baseado na descricao)")
        lang = input("Linguagem: ").strip().lower()
        if lang:
            prefs.programming_language = lang
        
        # 2. Framework (se aplicável)
        if prefs.programming_language == "python":
            print("\n2. FRAMEWORK PYTHON")
            print("Opcoes: fastapi, django, flask, none")
            print("(Enter para usar: fastapi - padrao mercado)")
            framework = input("Framework: ").strip().lower()
            if framework:
                prefs.framework = framework
            else:
                prefs.framework = "fastapi"  # Padrão mercado
        
        elif prefs.programming_language in ["javascript", "typescript"]:
            print("\n2. FRAMEWORK FRONTEND/BACKEND")
            print("Opcoes: react, vue, angular, express, nestjs, none")
            print("(Enter para auto-detectar)")
            framework = input("Framework: ").strip().lower()
            if framework:
                prefs.framework = framework
        
        # 3. Arquitetura
        print("\n3. PADRAO DE ARQUITETURA")
        print("Opcoes: mvc, mvp, clean-architecture, layered, component-based")
        print("(Enter para usar padrao baseado no framework)")
        arch = input("Arquitetura: ").strip().lower()
        if arch:
            prefs.architecture_pattern = arch
        
        # 4. Testes
        print("\n4. FRAMEWORK DE TESTES")
        print("(Enter para usar padrao da linguagem)")
        test_fw = input("Framework de testes: ").strip().lower()
        if test_fw:
            prefs.testing_framework = test_fw
        
        # 5. Banco de Dados
        print("\n5. BANCO DE DADOS")
        print("Opcoes: sqlite, postgresql, mongodb, mysql, none")
        print("(Enter para usar: sqlite - padrao desenvolvimento)")
        db = input("Banco de dados: ").strip().lower()
        if db:
            prefs.database_type = db
        else:
            prefs.database_type = "sqlite"  # Padrão mercado
        
        # 6. Segurança
        print("\n6. NIVEL DE SEGURANCA")
        print("Opcoes: basic, standard, high")
        print("(Enter para usar: standard - padrao mercado)")
        security = input("Nivel de seguranca: ").strip().lower()
        if security:
            prefs.security_level = security
        else:
            prefs.security_level = "standard"  # Padrão mercado
        
        # 7. Type Hints / TypeScript
        if prefs.programming_language == "python":
            print("\n7. TYPE HINTS")
            print("(Enter para usar: sim - melhor pratica)")
            use_types = input("Usar type hints? (s/n): ").strip().lower()
            prefs.use_type_hints = use_types in ['s', 'sim', 'y', 'yes', '']
        
        # 8. Cobertura de Testes
        print("\n8. COBERTURA DE TESTES MINIMA")
        print("(Enter para usar: 80% - padrao mercado)")
        coverage = input("Cobertura minima (%): ").strip()
        if coverage:
            try:
                prefs.test_coverage_min = int(coverage)
            except:
                prefs.test_coverage_min = 80
        else:
            prefs.test_coverage_min = 80  # Padrão mercado
        
        # 9. Linting e Formatação
        print("\n9. LINTING E FORMATACAO")
        print("(Enter para usar: sim - melhor pratica)")
        linting = input("Usar linting? (s/n): ").strip().lower()
        prefs.use_linting = linting in ['s', 'sim', 'y', 'yes', '']
        
        formatting = input("Usar formatacao automatica? (s/n): ").strip().lower()
        prefs.use_formatting = formatting in ['s', 'sim', 'y', 'yes', '']
        
        # 10. Deploy
        print("\n10. PLATAFORMA DE DEPLOY")
        print("Opcoes: render, railway, vercel, docker, none")
        print("(Enter para deixar em branco)")
        deploy = input("Plataforma de deploy: ").strip().lower()
        if deploy:
            prefs.deployment_platform = deploy
        
        # Aplicar padrões de mercado para campos não especificados
        prefs.apply_market_standards()
        
        # Resumo
        print("\n" + "=" * 70)
        print("RESUMO DAS PREFERENCIAS")
        print("=" * 70)
        print(f"Linguagem: {prefs.programming_language or 'Auto-detectar'}")
        print(f"Framework: {prefs.framework or 'Nenhum'}")
        print(f"Arquitetura: {prefs.architecture_pattern or 'Padrao'}")
        print(f"Testes: {prefs.testing_framework or 'Padrao'}")
        print(f"Banco de dados: {prefs.database_type or 'Nenhum'}")
        print(f"Seguranca: {prefs.security_level or 'Padrao'}")
        print(f"Type hints: {'Sim' if prefs.use_type_hints else 'Nao'}")
        print(f"Cobertura testes: {prefs.test_coverage_min}%")
        print(f"Linting: {'Sim' if prefs.use_linting else 'Nao'}")
        print(f"Formatacao: {'Sim' if prefs.use_formatting else 'Nao'}")
        print("=" * 70)
        print()
        
        return prefs
    
    @staticmethod
    def collect_preferences_auto(project_name: str, project_description: str) -> ProjectPreferences:
        """
        Coleta preferências automaticamente baseado na descrição.
        Usa padrões de mercado quando não pode detectar.
        
        Args:
            project_name: Nome do projeto
            project_description: Descrição do projeto
            
        Returns:
            ProjectPreferences com preferências detectadas/padrão
        """
        prefs = ProjectPreferences()
        
        # Auto-detectar linguagem baseado na descrição
        desc_lower = project_description.lower()
        
        if "python" in desc_lower or "fastapi" in desc_lower or "django" in desc_lower:
            prefs.programming_language = "python"
            if "fastapi" in desc_lower:
                prefs.framework = "fastapi"
            elif "django" in desc_lower:
                prefs.framework = "django"
        elif "javascript" in desc_lower or "node" in desc_lower:
            prefs.programming_language = "javascript"
        elif "typescript" in desc_lower:
            prefs.programming_language = "typescript"
        elif "react" in desc_lower:
            prefs.programming_language = "typescript"
            prefs.framework = "react"
        elif "vue" in desc_lower:
            prefs.programming_language = "typescript"
            prefs.framework = "vue"
        
        # Aplicar padrões de mercado
        prefs.apply_market_standards()
        
        return prefs
    
    @staticmethod
    def preferences_to_prompt_context(prefs) -> str:
        """
        Converte preferências em contexto para prompts do LLM.
        
        Args:
            prefs: Preferências do projeto (ProjectPreferences ou dict)
            
        Returns:
            String com contexto formatado
        """
        # Convert dict to ProjectPreferences if needed
        if isinstance(prefs, dict):
            prefs = ProjectPreferences.from_dict(prefs)
        elif not isinstance(prefs, ProjectPreferences):
            return "Using market standard best practices"
        
        context_parts = []
        
        if prefs.programming_language:
            context_parts.append(f"Programming Language: {prefs.programming_language}")
        
        if prefs.framework:
            context_parts.append(f"Framework: {prefs.framework}")
        
        if prefs.architecture_pattern:
            context_parts.append(f"Architecture Pattern: {prefs.architecture_pattern}")
        
        if prefs.testing_framework:
            context_parts.append(f"Testing Framework: {prefs.testing_framework}")
        
        if prefs.database_type:
            context_parts.append(f"Database: {prefs.database_type}")
        
        if prefs.security_level:
            context_parts.append(f"Security Level: {prefs.security_level}")
        
        if prefs.use_type_hints:
            context_parts.append("Use Type Hints: Yes")
        
        if prefs.test_coverage_min:
            context_parts.append(f"Minimum Test Coverage: {prefs.test_coverage_min}%")
        
        if prefs.use_linting:
            context_parts.append("Use Linting: Yes")
        
        if prefs.use_formatting:
            context_parts.append("Use Code Formatting: Yes")
        
        if context_parts:
            return "\n".join(context_parts)
        else:
            return "Using market standard best practices"

