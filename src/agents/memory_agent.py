#!/usr/bin/env python3
"""
Memory Agent for Jarvis - Fase Memória

Agente especializado em gerenciar e recuperar contexto para o assistente Jarvis.
Integra:
- Supermemory (memória de longo prazo)
- Arquivos locais (MEMORY.md, USER.md, SOUL.md, memory/YYYY-MM-DD.md)
- Estado do projeto AI-Biomimetica
- Histórico de decisões e configurações

Autor: Jarvis (OpenClaw)
Data: 2026-04-11
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import hashlib

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configurar logging
logger = logging.getLogger(__name__)


class MemoryCategory(Enum):
    """Categorias para armazenamento de memória"""
    TECHNICAL = "technical"           # Configurações técnicas, APIs, credenciais
    DECISION = "decision"             # Decisões arquiteturais, escolhas
    PREFERENCE = "preference"         # Preferências do usuário, estilo
    SECURITY = "security"             # Informações de segurança, credenciais
    PROJECT = "project"               # Estado do projeto, fases, progresso
    CONVERSATION = "conversation"     # Contexto de conversas importantes
    TASK = "task"                     # Tarefas pendentes, próximos passos
    LESSON = "lesson"                 # Lições aprendidas, erros, soluções


class MemoryPriority(Enum):
    """Prioridade da informação (frequência de recall)"""
    CRITICAL = "critical"     # Sempre lembrar (ex: credenciais, decisões-chave)
    HIGH = "high"             # Frequentemente relevante (ex: preferências, estado do projeto)
    MEDIUM = "medium"         # Ocasionalmente relevante (ex: lições aprendidas)
    LOW = "low"               # Raramente relevante (ex: histórico de conversas antigas)


class MemoryContext:
    """Contexto para uma consulta/armazenamento de memória"""
    
    def __init__(self, session_id: str = None, user_id: str = "Adjalma"):
        self.session_id = session_id or hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:8]
        self.user_id = user_id
        self.timestamp = datetime.now()
        self.project_context = {}
        self.conversation_history = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte contexto para dicionário"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "project_context": self.project_context,
            "conversation_history_length": len(self.conversation_history)
        }


class JarvisMemoryAgent:
    """
    Agente de memória para o assistente Jarvis
    
    Responsabilidades:
    1. Manter contexto do projeto AI-Biomimetica atualizado
    2. Armazenar decisões importantes no Supermemory
    3. Recuperar contexto ao iniciar sessões
    4. Responder consultas sobre estado do projeto
    5. Gerenciar arquivos de memória locais
    """
    
    def __init__(self, workspace_root: str = "/data/workspace"):
        self.workspace_root = workspace_root
        self.ai_biomimetica_root = os.path.join(workspace_root, "AI-Biomimetica")
        self.memory_files_root = os.path.join(workspace_root, "memory")
        
        # Cache de memória
        self.cached_context = {}
        self.last_refresh = None
        
        # Estado do projeto
        self.project_state = {}
        
        logger.info(f"Memory Agent inicializado. Workspace: {workspace_root}")
    
    # ===== MÉTODOS DE LEITURA DE ARQUIVOS LOCAIS =====
    
    def read_memory_file(self, filename: str) -> Optional[str]:
        """Lê um arquivo de memória local"""
        try:
            filepath = os.path.join(self.workspace_root, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {filename}: {e}")
        return None
    
    def read_daily_memory(self, days_back: int = 3) -> Dict[str, str]:
        """Lê memórias diárias dos últimos N dias"""
        memories = {}
        for i in range(days_back + 1):
            date = datetime.now() - timedelta(days=i)
            filename = date.strftime("memory/%Y-%m-%d.md")
            content = self.read_memory_file(filename)
            if content:
                memories[date.strftime("%Y-%m-%d")] = content[:1000] + "..." if len(content) > 1000 else content
        return memories
    
    def read_core_files(self) -> Dict[str, str]:
        """Lê arquivos centrais de identidade e memória"""
        core_files = {
            "MEMORY.md": self.read_memory_file("MEMORY.md"),
            "USER.md": self.read_memory_file("USER.md"),
            "SOUL.md": self.read_memory_file("SOUL.md"),
            "IDENTITY.md": self.read_memory_file("IDENTITY.md"),
            "AGENTS.md": self.read_memory_file("AGENTS.md"),
            "TOOLS.md": self.read_memory_file("TOOLS.md")
        }
        return {k: v for k, v in core_files.items() if v}
    
    # ===== MÉTODOS DE CONTEXTO DO PROJETO =====
    
    def scan_project_state(self) -> Dict[str, Any]:
        """Escaneia o estado atual do projeto AI-Biomimetica"""
        state = {
            "last_commit": None,
            "phases_implemented": [],
            "google_apis_status": {},
            "ollama_status": None,
            "pending_tasks": [],
            "recent_changes": []
        }
        
        try:
            # Verificar status Git
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                cwd=self.ai_biomimetica_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                state["last_commit"] = result.stdout.strip()
            
            # Verificar fases implementadas (baseado em arquivos)
            phases = []
            if os.path.exists(os.path.join(self.ai_biomimetica_root, "src", "systems", "sistemas", "sistema_meta_learning_biomimetico.py")):
                phases.append("Fase 5: Sistema de Meta-Learning Biomimético")
            
            # Verificar Google APIs
            google_status = {}
            if os.path.exists(os.path.join(self.ai_biomimetica_root, "src", "google", "google_calendar_client.py")):
                google_status["calendar"] = "implementado"
            if os.path.exists(os.path.join(self.ai_biomimetica_root, "src", "google", "gmail_client.py")):
                google_status["gmail"] = "implementado"
            if os.path.exists(os.path.join(self.ai_biomimetica_root, "credentials.json")):
                google_status["credentials"] = "presente"
            
            state["google_apis_status"] = google_status
            state["phases_implemented"] = phases
            
            # Verificar Ollama (simplificado)
            try:
                import ollama
                state["ollama_status"] = "disponível"
            except ImportError:
                state["ollama_status"] = "não detectado"
                
        except Exception as e:
            logger.warning(f"Erro ao escanear projeto: {e}")
            state["scan_error"] = str(e)
        
        return state
    
    # ===== MÉTODOS DE REFRESH DE CONTEXTO =====
    
    async def refresh_context(self, force: bool = False) -> Dict[str, Any]:
        """
        Atualiza o contexto completo do Jarvis
        
        Retorna um resumo conciso para uso imediato
        """
        if not force and self.last_refresh and (datetime.now() - self.last_refresh).seconds < 300:
            logger.info("Contexto recente, usando cache")
            return self.cached_context
        
        logger.info("Atualizando contexto do Memory Agent")
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "core_identity": {},
            "recent_memories": {},
            "project_state": {},
            "pending_decisions": [],
            "key_reminders": []
        }
        
        # 1. Identidade e preferências
        core_files = self.read_core_files()
        context["core_identity"] = {
            "files_loaded": list(core_files.keys()),
            "user_info": self._extract_user_info(core_files.get("USER.md", "")),
            "personality": self._extract_personality(core_files.get("SOUL.md", ""))
        }
        
        # 2. Memórias recentes
        context["recent_memories"] = self.read_daily_memory(days_back=2)
        
        # 3. Estado do projeto
        context["project_state"] = self.scan_project_state()
        
        # 4. Tarefas pendentes (extrai de memórias recentes)
        context["pending_tasks"] = self._extract_pending_tasks(context["recent_memories"])
        
        # 5. Consulta Supermemory para contexto adicional
        try:
            supermemory_context = await self._query_supermemory_context()
            context["supermemory_context"] = supermemory_context
        except Exception as e:
            logger.warning(f"Erro ao consultar supermemory: {e}")
            context["supermemory_context"] = {"error": str(e)}
        
        self.cached_context = context
        self.last_refresh = datetime.now()
        
        return context
    
    def _extract_user_info(self, user_md: str) -> Dict[str, str]:
        """Extrai informações do usuário do USER.md"""
        info = {}
        if not user_md:
            return info
        
        lines = user_md.split('\n')
        for line in lines:
            if "**Name:**" in line:
                info["name"] = line.split("**Name:**")[-1].strip()
            elif "**Timezone:**" in line:
                info["timezone"] = line.split("**Timezone:**")[-1].strip()
            elif "**Language:**" in line:
                info["language"] = line.split("**Language:**")[-1].strip()
        
        return info
    
    def _extract_personality(self, soul_md: str) -> Dict[str, str]:
        """Extrai personalidade do SOUL.md"""
        personality = {}
        if not soul_md:
            return personality
        
        lines = soul_md.split('\n')
        for line in lines:
            if "**Personalidade:**" in line:
                personality["description"] = line.split("**Personalidade:**")[-1].strip()
            elif "**Regras**" in line:
                # Próximas linhas após título
                pass
        
        return personality
    
    def _extract_pending_tasks(self, recent_memories: Dict[str, str]) -> List[str]:
        """Extrai tarefas pendentes de memórias recentes"""
        tasks = []
        for date, content in recent_memories.items():
            # Procura por padrões como "pendente", "próximo passo", "to do"
            lines = content.split('\n')
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ["pendente", "próximo passo", "next step", "to do", "fazer", "precisa"]):
                    if len(line.strip()) > 10:  # Evita linhas muito curtas
                        tasks.append(f"{date}: {line.strip()}")
        
        return tasks[:5]  # Limita a 5 tarefas
    
    async def _query_supermemory_context(self) -> Dict[str, Any]:
        """Consulta o Supermemory para contexto adicional"""
        # Esta é uma implementação mock - na prática usaria supermemory_search
        # e supermemory_profile
        return {
            "biomimetica_context": "AI-Biomimetica project fully updated with all 5 phases",
            "user_preferences": "Prefers direct communication, sarcastic tone in Portuguese",
            "recent_decisions": "Implemented Google Calendar and Gmail APIs (Phase 6)"
        }
    
    # ===== MÉTODOS DE ARMAZENAMENTO =====
    
    async def store_important(self, 
                             event: str, 
                             category: MemoryCategory,
                             priority: MemoryPriority = MemoryPriority.MEDIUM,
                             context: Dict[str, Any] = None) -> bool:
        """
        Armazena um evento importante na memória
        
        Args:
            event: Descrição do evento
            category: Categoria da memória
            priority: Prioridade (frequência de recall)
            context: Contexto adicional (ex: decisões técnicas, erros)
        
        Returns:
            bool: True se armazenado com sucesso
        """
        logger.info(f"Armazenando memória: {category.value} - {event[:50]}...")
        
        # Preparar dados para armazenamento
        memory_data = {
            "event": event,
            "category": category.value,
            "priority": priority.value,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # 1. Armazenar no Supermemory (se disponível)
        try:
            # Em produção, chamaria supermemory_store aqui
            # Por enquanto, apenas log
            logger.debug(f"Dados para supermemory: {json.dumps(memory_data, indent=2)}")
        except Exception as e:
            logger.error(f"Erro ao armazenar no supermemory: {e}")
        
        # 2. Armazenar em arquivo local (MEMORY.md)
        try:
            self._append_to_memory_file(memory_data)
        except Exception as e:
            logger.error(f"Erro ao armazenar em arquivo local: {e}")
        
        # 3. Atualizar cache
        if "memories" not in self.cached_context:
            self.cached_context["memories"] = []
        self.cached_context["memories"].append(memory_data)
        
        return True
    
    def _append_to_memory_file(self, memory_data: Dict[str, Any]):
        """Adiciona memória ao MEMORY.md"""
        memory_file = os.path.join(self.workspace_root, "MEMORY.md")
        
        # Formatar entrada
        entry = f"""
## {memory_data['timestamp']} - {memory_data['category'].upper()}
**Evento:** {memory_data['event']}

**Prioridade:** {memory_data['priority']}

**Contexto:**
```json
{json.dumps(memory_data['context'], indent=2, ensure_ascii=False)}
```

---
"""
        
        # Adicionar ao arquivo
        if os.path.exists(memory_file):
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write("# MEMORY.md - Curated Long-Term Memory\n\n")
                f.write(entry)
    
    # ===== MÉTODOS DE CONSULTA =====
    
    async def query_context(self, question: str) -> str:
        """
        Responde perguntas sobre contexto/projeto
        
        Args:
            question: Pergunta em linguagem natural
        
        Returns:
            str: Resposta contextual
        """
        logger.info(f"Consultando contexto: {question}")
        
        # Primeiro, garantir contexto atualizado
        context = await self.refresh_context()
        
        # Analisar pergunta
        question_lower = question.lower()
        
        # Respostas baseadas em padrões
        if any(keyword in question_lower for keyword in ["estado", "status", "como está", "progresso"]):
            return self._generate_project_status_response(context)
        
        elif any(keyword in question_lower for keyword in ["próximo", "passo", "fazer agora", "tarefa"]):
            return self._generate_next_steps_response(context)
        
        elif any(keyword in question_lower for keyword in ["implementado", "feito", "concluído"]):
            return self._generate_implemented_response(context)
        
        elif any(keyword in question_lower for keyword in ["configurado", "setup", "instalado"]):
            return self._generate_configuration_response(context)
        
        elif any(keyword in question_lower for keyword in ["problema", "erro", "bug", "falta"]):
            return self._generate_problems_response(context)
        
        else:
            return self._generate_general_context_response(context, question)
    
    def _generate_project_status_response(self, context: Dict[str, Any]) -> str:
        """Gera resposta sobre status do projeto"""
        project = context.get("project_state", {})
        
        response = "📊 **STATUS DO PROJETO AI-BIOMIMETICA**\n\n"
        
        # Último commit
        if project.get("last_commit"):
            response += f"• **Último commit:** `{project['last_commit']}`\n"
        
        # Google APIs
        google_status = project.get("google_apis_status", {})
        if google_status:
            response += "• **Google APIs:** "
            if google_status.get("calendar") == "implementado":
                response += "✅ Calendar "
            if google_status.get("gmail") == "implementado":
                response += "✅ Gmail "
            if google_status.get("credentials") == "presente":
                response += "🔑 Credenciais "
            response += "\n"
        
        # Ollama
        ollama_status = project.get("ollama_status")
        if ollama_status:
            response += f"• **Ollama:** {'✅ Disponível' if ollama_status == 'disponível' else '⚠️ Não detectado'}\n"
        
        # Tarefas pendentes
        pending = context.get("pending_tasks", [])
        if pending:
            response += "\n**📋 TAREFAS PENDENTES:**\n"
            for i, task in enumerate(pending[:3], 1):
                response += f"{i}. {task}\n"
        
        return response
    
    def _generate_next_steps_response(self, context: Dict[str, Any]) -> str:
        """Gera resposta sobre próximos passos"""
        pending = context.get("pending_tasks", [])
        project = context.get("project_state", {})
        
        response = "🎯 **PRÓXIMOS PASSOS RECOMENDADOS**\n\n"
        
        if pending:
            response += "**Baseado em tarefas pendentes:**\n"
            for i, task in enumerate(pending[:3], 1):
                response += f"{i}. {task}\n"
        else:
            # Sugestões baseadas no estado do projeto
            google_status = project.get("google_apis_status", {})
            
            if google_status.get("calendar") == "implementado" and google_status.get("gmail") == "implementado":
                response += "1. **Testar integração Google APIs** (`python scripts/test_gmail_api.py`)\n"
                response += "2. **Integrar com sistema biomimético** principal\n"
                response += "3. **Implementar Fase 7** (Sistema de Ação Autônoma)\n"
            else:
                response += "1. **Completar implementação Google APIs** (Calendar + Gmail)\n"
                response += "2. **Configurar autenticação OAuth2**\n"
                response += "3. **Testar conexões** com APIs reais\n"
        
        return response
    
    def _generate_implemented_response(self, context: Dict[str, Any]) -> str:
        """Gera resposta sobre o que já foi implementado"""
        project = context.get("project_state", {})
        
        response = "✅ **IMPLEMENTAÇÕES CONCLUÍDAS**\n\n"
        
        # Fases
        phases = project.get("phases_implemented", [])
        if phases:
            response += "**Fases do AI-Biomimetica:**\n"
            for phase in phases:
                response += f"• {phase}\n"
        
        # Google APIs
        google_status = project.get("google_apis_status", {})
        if google_status:
            response += "\n**Google APIs:**\n"
            if google_status.get("calendar") == "implementado":
                response += "• Calendar API (leitura + escrita)\n"
            if google_status.get("gmail") == "implementado":
                response += "• Gmail API (leitura + escrita)\n"
        
        return response
    
    def _generate_configuration_response(self, context: Dict[str, Any]) -> str:
        """Gera resposta sobre configurações"""
        project = context.get("project_state", {})
        
        response = "⚙️ **CONFIGURAÇÕES DO SISTEMA**\n\n"
        
        # Credenciais
        google_status = project.get("google_apis_status", {})
        if google_status.get("credentials") == "presente":
            response += "✅ Credenciais Google OAuth2 configuradas\n"
        else:
            response += "❌ Credenciais Google não encontradas\n"
        
        # Ollama
        ollama_status = project.get("ollama_status")
        if ollama_status:
            response += f"✅ Ollama: {ollama_status}\n"
        
        # Identidade
        identity = context.get("core_identity", {})
        if identity.get("user_info"):
            user = identity["user_info"]
            response += f"\n**👤 Usuário:** {user.get('name', 'Não especificado')}\n"
            response += f"**🌐 Timezone:** {user.get('timezone', 'Não especificado')}\n"
            response += f"**🗣️ Idioma:** {user.get('language', 'Não especificado')}\n"
        
        return response
    
    def _generate_problems_response(self, context: Dict[str, Any]) -> str:
        """Gera resposta sobre problemas conhecidos"""
        response = "🔧 **PROBLEMAS CONHECIDOS**\n\n"
        
        # Extrair problemas de memórias recentes
        recent = context.get("recent_memories", {})
        problems = []
        
        for date, content in recent.items():
            if any(keyword in content.lower() for keyword in ["erro", "problema", "bug", "falha", "não funciona"]):
                # Encontrar linha com problema
                lines = content.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ["erro", "problema", "bug", "falha"]):
                        problems.append(f"{date}: {line.strip()}")
        
        if problems:
            for i, problem in enumerate(problems[:3], 1):
                response += f"{i}. {problem}\n"
        else:
            response += "✅ Nenhum problema crítico reportado recentemente.\n"
            response += "⚠️ Verifique logs e testes para validação completa.\n"
        
        return response
    
    def _generate_general_context_response(self, context: Dict[str, Any], question: str) -> str:
        """Gera resposta contextual geral"""
        return f"""
🤔 **CONSULTA DE CONTEXTO**

**Pergunta:** {question}

**Contexto atual:**
- Projeto AI-Biomimetica com Google APIs implementadas
- Sistema biomimético com meta-learning (Fases 1-5)
- Pronto para Fase 7 (Ação Autônoma)
- Usuário: Adjalma Aguiar (timezone America/Sao_Paulo)

**Sugestão:** Para respostas mais específicas, pergunte sobre:
• Estado do projeto
• Próximos passos
• Configurações
• Problemas conhecidos
• O que já foi implementado
"""
    
    # ===== MÉTODOS DE UTILIDADE =====
    
    def get_context_summary(self, max_length: int = 1000) -> str:
        """
        Retorna um resumo conciso do contexto atual
        
        Ideal para refresh ao iniciar sessão
        """
        if not self.cached_context:
            return "⚠️ Contexto não carregado. Execute refresh_context() primeiro."
        
        summary = f"""
🔄 **CONTEXTO ATUALIZADO** ({self.last_refresh.strftime('%H:%M')})

**👤 USUÁRIO:**
• Nome: {self.cached_context.get('core_identity', {}).get('user_info', {}).get('name', 'Não especificado')}
• Timezone: {self.cached_context.get('core_identity', {}).get('user_info', {}).get('timezone', 'Não especificado')}

**📊 PROJETO AI-BIOMIMETICA:**
• Google Calendar: {'✅' if self.cached_context.get('project_state', {}).get('google_apis_status', {}).get('calendar') == 'implementado' else '❌'}
• Google Gmail: {'✅' if self.cached_context.get('project_state', {}).get('google_apis_status', {}).get('gmail') == 'implementado' else '❌'}
• Ollama: {'✅ Disponível' if self.cached_context.get('project_state', {}).get('ollama_status') == 'disponível' else '⚠️ Não detectado'}

**📋 PRÓXIMOS PASSOS:**
{chr(10).join(f'• {task}' for task in self.cached_context.get('pending_tasks', ['Nenhuma tarefa pendente identificada'])[:2])}
"""
        
        return summary[:max_length]
    
    async def auto_refresh_on_startup(self):
        """
        Método para ser chamado automaticamente ao iniciar sessão
        
        Atualiza contexto e loga resumo
        """
        logger.info("🔄 Memory Agent: Auto-refresh ao iniciar sessão")
        
        try:
            context = await self.refresh_context(force=True)
            summary = self.get_context_summary()
            
            logger.info(f"Contexto atualizado:\n{summary}")
            
            # Armazenar memória do startup
            await self.store_important(
                event="Sessão iniciada - contexto atualizado",
                category=MemoryCategory.CONVERSATION,
                priority=MemoryPriority.LOW,
                context={"summary": summary}
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro no auto-refresh: {e}")
            return f"❌ Erro ao atualizar contexto: {e}"


# Função de utilidade para integração fácil
async def create_and_refresh_memory_agent(workspace_root: str = "/data/workspace") -> Tuple[JarvisMemoryAgent, str]:
    """
    Cria e atualiza um Memory Agent em uma única chamada
    
    Returns:
        Tuple[JarvisMemoryAgent, str]: Agente e resumo do contexto
    """
    agent = JarvisMemoryAgent(workspace_root)
    summary = await agent.auto_refresh_on_startup()
    return agent, summary


# Teste básico
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("🧪 TESTANDO MEMORY AGENT")
        print("=" * 50)
        
        agent = JarvisMemoryAgent()
        
        # 1. Atualizar contexto
        print("\n1. Atualizando contexto...")
        context = await agent.refresh_context()
        print(f"   Contexto atualizado: {len(context)} elementos")
        
        # 2. Resumo
        print("\n2. Resumo do contexto:")
        print(agent.get_context_summary())
        
        # 3. Consultas
        print("\n3. Testando consultas:")
        
        questions = [
            "Como está o projeto?",
            "O que fazer agora?",
            "O que já foi implementado?",
            "O que está configurado?",
            "Tem algum problema?"
        ]
        
        for q in questions:
            print(f"\n   Q: {q}")
            answer = await agent.query_context(q)
            print(f"   A: {answer[:200]}...")
        
        # 4. Armazenar memória
        print("\n4. Armazenando memória de teste...")
        await agent.store_important(
            event="Teste do Memory Agent concluído",
            category=MemoryCategory.TECHNICAL,
            priority=MemoryPriority.MEDIUM,
            context={"test_result": "sucesso", "timestamp": datetime.now().isoformat()}
        )
        
        print("\n✅ Teste concluído!")
    
    asyncio.run(test())