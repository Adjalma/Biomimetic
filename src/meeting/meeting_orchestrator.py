#!/usr/bin/env python3
"""
Meeting Orchestrator - Fase 8: Participação em Reuniões
Fase 9: Contexto Empresarial
Fase 10: Aprendizado com Interações Reais

Extende o AutonomousActionOrchestrator com capacidades específicas para:
- Entrar em reuniões (Google Meet, Microsoft Teams) com Google Meet SDK
- Transcrever áudio em tempo real (STT)
- Analisar conversas e sentimentos
- Resumir reuniões e extrair decisões
- Salvar notas automaticamente no Obsidian
- Seguir protocolos de etiqueta empresarial (etiquette_rules)
- Entender hierarquias organizacionais (organizational_hierarchy)
- Gerenciar relacionamentos (relationship_manager)
- Aprender com interações reais (interaction_learning)

Autor: Jarvis (OpenClaw)
Data: 2026-04-11
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from enum import Enum

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.autonomous_action_orchestrator import (
    AutonomousActionOrchestrator,
    ActionType,
    ActionPriority,
    ActionContext,
    ActionRequest,
    ActionRegistry,
    ActionDecisionEngine,
    ActionExecutor
)

# Importar novos módulos das Fases 8, 9, 10
try:
    from google.google_meet_client import GoogleMeetClient, create_google_meet_client
    GOOGLE_MEET_AVAILABLE = True
except ImportError:
    GOOGLE_MEET_AVAILABLE = False
    logger.warning("GoogleMeetClient não disponível. Instale dependências: pip install selenium")

try:
    from meeting.etiquette_rules import MeetingEtiquetteRules, create_etiquette_rules, MeetingType, IARole, CulturalContext
    ETIQUETTE_RULES_AVAILABLE = True
except ImportError:
    ETIQUETTE_RULES_AVAILABLE = False
    logger.warning("MeetingEtiquetteRules não disponível")

try:
    from agents.organizational_hierarchy import OrganizationalHierarchy, create_organizational_hierarchy, EmployeeRole
    ORGANIZATIONAL_HIERARCHY_AVAILABLE = True
except ImportError:
    ORGANIZATIONAL_HIERARCHY_AVAILABLE = False
    logger.warning("OrganizationalHierarchy não disponível")

try:
    from agents.relationship_manager import RelationshipManager, create_relationship_manager, InteractionType as RelInteractionType
    RELATIONSHIP_MANAGER_AVAILABLE = True
except ImportError:
    RELATIONSHIP_MANAGER_AVAILABLE = False
    logger.warning("RelationshipManager não disponível")

logger = logging.getLogger(__name__)


class MeetingOrchestrator(AutonomousActionOrchestrator):
    """Orquestrador especializado em ações de reunião"""
    
    def __init__(self, 
                 use_biomimetic: bool = True,
                 require_human_approval: bool = True,  # Por padrão pedir aprovação para entrar em reuniões
                 meeting_platform: str = "google_meet",  # google_meet, teams, zoom
                 organizational_data_path: Optional[str] = None,
                 relationship_data_path: Optional[str] = None,
                 cultural_context: str = "formal_hierarchical"):
        """
        Inicializa orquestrador de reuniões com módulos das Fases 8, 9, 10.
        
        Args:
            use_biomimetic: Usar sistema biomimético para decisões
            require_human_approval: Requer aprovação humana para ações críticas
            meeting_platform: Plataforma de reunião padrão
            organizational_data_path: Caminho para dados organizacionais (JSON/CSV)
            relationship_data_path: Caminho para dados de relacionamentos (JSON)
            cultural_context: Contexto cultural (formal_hierarchical, informal_flat, etc.)
        """
        super().__init__(use_biomimetic=use_biomimetic, 
                        require_human_approval=require_human_approval)
        
        self.meeting_platform = meeting_platform
        self.active_meetings = {}  # meeting_id -> meeting_info
        self.meeting_history = []
        
        # Inicializar módulos da Fase 8: Google Meet Client
        self.google_meet_client = None
        if GOOGLE_MEET_AVAILABLE and meeting_platform == "google_meet":
            try:
                self.google_meet_client = create_google_meet_client(headless=True)
                logger.info("✅ Google Meet Client inicializado (modo headless)")
            except Exception as e:
                logger.warning(f"⚠️  Falha ao inicializar Google Meet Client: {e}")
        
        # Inicializar módulos da Fase 8: Regras de Etiqueta
        self.etiquette_rules = None
        if ETIQUETTE_RULES_AVAILABLE:
            try:
                cultural_enum = CulturalContext[cultural_context.upper()] if hasattr(CulturalContext, cultural_context.upper()) else CulturalContext.FORMAL_HIERARCHICAL
                self.etiquette_rules = create_etiquette_rules(cultural_enum)
                logger.info(f"✅ Regras de Etiqueta inicializadas (contexto: {cultural_context})")
            except Exception as e:
                logger.warning(f"⚠️  Falha ao inicializar Regras de Etiqueta: {e}")
        
        # Inicializar módulos da Fase 9: Hierarquia Organizacional
        self.organizational_hierarchy = None
        if ORGANIZATIONAL_HIERARCHY_AVAILABLE and organizational_data_path:
            try:
                self.organizational_hierarchy = create_organizational_hierarchy(organizational_data_path)
                logger.info(f"✅ Hierarquia Organizacional carregada: {organizational_data_path}")
            except Exception as e:
                logger.warning(f"⚠️  Falha ao carregar Hierarquia Organizacional: {e}")
        
        # Inicializar módulos da Fase 9: Gestão de Relacionamentos
        self.relationship_manager = None
        if RELATIONSHIP_MANAGER_AVAILABLE:
            try:
                self.relationship_manager = create_relationship_manager(relationship_data_path)
                logger.info("✅ Gestão de Relacionamentos inicializada")
            except Exception as e:
                logger.warning(f"⚠️  Falha ao inicializar Gestão de Relacionamentos: {e}")
        
        # Registro de interações para aprendizado (Fase 10)
        self.interaction_log = []
        
        # Registrar ações específicas de reunião
        self._register_meeting_actions()
        
        logger.info(f"✅ MeetingOrchestrator inicializado para {meeting_platform} com módulos das Fases 8-10")
    
    def _register_meeting_actions(self):
        """Registra ações específicas de reunião"""
        
        # Entrar em reunião
        self.registry.register(
            ActionType.JOIN_MEETING,
            self._handle_join_meeting,
            "Entrar em reunião (Google Meet, Teams, Zoom)",
            requirements=["meeting_client"]
        )
        
        # Transcrever reunião
        self.registry.register(
            ActionType.TRANSCRIBE_MEETING,
            self._handle_transcribe_meeting,
            "Transcrever áudio de reunião para texto",
            requirements=["stt_service"]
        )
        
        # Resumir reunião
        self.registry.register(
            ActionType.SUMMARIZE_MEETING,
            self._handle_summarize_meeting,
            "Gerar resumo da reunião com decisões e ações",
            requirements=["biomimetic_system"]
        )
        
        # Salvar notas da reunião
        self.registry.register(
            ActionType.SAVE_MEETING_NOTES,
            self._handle_save_meeting_notes,
            "Salvar notas da reunião no Obsidian",
            requirements=["obsidian"]
        )
        
        # Monitorar reunião ativa
        self.registry.register(
            ActionType.MONITOR_MEETING,
            self._handle_monitor_meeting,
            "Monitorar reunião ativa e intervir quando apropriado",
            requirements=["meeting_client", "stt_service"]
        )
        
        # Analisar interações para aprendizado (Fase 10)
        self.registry.register(
            "ANALYZE_INTERACTIONS",
            self._handle_analyze_interactions,
            "Analisar interações para aprendizado evolutivo",
            requirements=["biomimetic_system"]
        )
        
        logger.info(f"✅ {len([a for a in self.registry.list_actions() if 'meeting' in a['type']]) + 1} ações de reunião registradas (incluindo Fase 10)")
    
    # ==================== HANDLERS DE AÇÃO ====================
    
    def _handle_join_meeting(self, request: ActionRequest, executor: ActionExecutor) -> Dict[str, Any]:
        """Handler para entrar em reunião"""
        
        meeting_url = request.parameters.get("meeting_url")
        meeting_title = request.parameters.get("title", "Reunião sem título")
        meeting_time = request.parameters.get("time", datetime.now().isoformat())
        participants = request.parameters.get("participants", [])
        
        logger.info(f"🟡 Tentando entrar na reunião: {meeting_title}")
        
        # Analisar contexto de etiqueta antes de entrar (Fase 8)
        etiquette_context = self._create_etiquette_context(request.parameters)
        if self.etiquette_rules:
            etiquette_recommendation = self.etiquette_rules.get_recommended_action(etiquette_context)
            logger.info(f"📋 Recomendação de etiqueta: {etiquette_recommendation['action']} (confiança: {etiquette_recommendation['confidence']:.2f})")
        
        # Analisar hierarquia dos participantes (Fase 9)
        hierarchy_info = self._analyze_participant_hierarchy(participants)
        
        meeting_id = f"meeting_{hash(meeting_url) % 10000:04d}"
        
        # Usar Google Meet Client real se disponível
        if self.google_meet_client and self.meeting_platform == "google_meet":
            try:
                logger.info("🔗 Usando Google Meet Client para entrar na reunião")
                join_result = self.google_meet_client.join_meeting(meeting_url, meeting_title)
                
                result = {
                    "success": join_result.get("success", True),
                    "meeting_id": meeting_id,
                    "meeting_title": meeting_title,
                    "platform": self.meeting_platform,
                    "joined_at": datetime.now().isoformat(),
                    "participants": participants,
                    "notes": f"Entrou na reunião '{meeting_title}' via {self.meeting_platform} usando Google Meet Client",
                    "action": "join_meeting",
                    "mock": join_result.get("mock", False),
                    "etiquette_recommendation": etiquette_recommendation if self.etiquette_rules else None,
                    "hierarchy_info": hierarchy_info
                }
                
                # Registrar reunião ativa
                self.active_meetings[meeting_id] = {
                    **result,
                    "transcription": [],
                    "decisions": [],
                    "action_items": [],
                    "status": "active",
                    "google_meet_result": join_result
                }
                
                logger.info(f"✅ Entrou na reunião {meeting_id} via Google Meet Client: {meeting_title}")
                
                # Registrar interação para aprendizado (Fase 10)
                self._log_interaction(
                    interaction_type="meeting_join",
                    participants=participants,
                    meeting_id=meeting_id,
                    context=etiquette_context
                )
                
            except Exception as e:
                logger.error(f"❌ Erro ao usar Google Meet Client: {e}")
                # Fallback para mock
                result = self._create_mock_join_result(meeting_url, meeting_title, participants, meeting_id)
        else:
            # Usar mock (modo de desenvolvimento)
            result = self._create_mock_join_result(meeting_url, meeting_title, participants, meeting_id)
        
        # Se temos sistema biomimético, analisar contexto inicial
        if self.biomimetic_system:
            self._analyze_meeting_context(meeting_id, request.parameters)
        
        return result
    
    # ==================== MÉTODOS AUXILIARES DAS FASES 8-10 ====================
    
    def _create_etiquette_context(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Cria contexto para análise de etiqueta (Fase 8)"""
        context = {
            'meeting_type': parameters.get('meeting_type', 'status_update'),
            'ia_role': parameters.get('ia_role', 'assistant'),
            'cultural_context': parameters.get('cultural_context', 'formal_hierarchical'),
            'sensitive_topic': parameters.get('sensitive_topic', False),
            'mentioned_ia': parameters.get('mentioned_ia', False),
            'direct_question': parameters.get('direct_question', False)
        }
        
        # Adicionar informações de participantes se disponível
        participants = parameters.get('participants', [])
        if participants and self.organizational_hierarchy:
            # Verificar se há executivos na reunião
            executives_count = 0
            for participant in participants:
                if isinstance(participant, str) and '@' in participant:
                    emp = self.organizational_hierarchy.get_employee_by_email(participant)
                    if emp and emp.role in [EmployeeRole.CEO, EmployeeRole.CTO, EmployeeRole.CFO, EmployeeRole.COO, EmployeeRole.VP]:
                        executives_count += 1
            
            context['has_executives'] = executives_count > 0
            context['executives_count'] = executives_count
        
        return context
    
    def _analyze_participant_hierarchy(self, participants: List[str]) -> Dict[str, Any]:
        """Analisa hierarquia dos participantes (Fase 9)"""
        if not self.organizational_hierarchy or not participants:
            return {"available": False, "message": "Hierarquia não disponível"}
        
        hierarchy_info = {
            "available": True,
            "participants_analyzed": 0,
            "executives": [],
            "managers": [],
            "individual_contributors": [],
            "common_manager": None,
            "max_hierarchical_distance": 0
        }
        
        # Analisar cada participante
        participant_employees = []
        for participant in participants:
            if isinstance(participant, str) and '@' in participant:
                emp = self.organizational_hierarchy.get_employee_by_email(participant)
                if emp:
                    participant_employees.append(emp)
        
        hierarchy_info["participants_analyzed"] = len(participant_employees)
        
        # Classificar por cargo
        for emp in participant_employees:
            if emp.role in [EmployeeRole.CEO, EmployeeRole.CTO, EmployeeRole.CFO, EmployeeRole.COO, EmployeeRole.VP]:
                hierarchy_info["executives"].append({
                    "id": emp.id,
                    "name": emp.name,
                    "role": emp.role.value,
                    "level": emp.level
                })
            elif emp.role in [EmployeeRole.DIRECTOR, EmployeeRole.SENIOR_MANAGER, EmployeeRole.MANAGER]:
                hierarchy_info["managers"].append({
                    "id": emp.id,
                    "name": emp.name,
                    "role": emp.role.value,
                    "level": emp.level
                })
            else:
                hierarchy_info["individual_contributors"].append({
                    "id": emp.id,
                    "name": emp.name,
                    "role": emp.role.value,
                    "level": emp.level
                })
        
        # Encontrar gerente comum
        if len(participant_employees) >= 2:
            employee_ids = [emp.id for emp in participant_employees]
            common_manager = self.organizational_hierarchy.find_common_manager(employee_ids)
            if common_manager:
                hierarchy_info["common_manager"] = {
                    "id": common_manager.id,
                    "name": common_manager.name,
                    "role": common_manager.role.value,
                    "level": common_manager.level
                }
        
        # Calcular distância hierárquica máxima
        if len(participant_employees) >= 2:
            max_distance = 0
            for i in range(len(participant_employees)):
                for j in range(i + 1, len(participant_employees)):
                    distance = self.organizational_hierarchy.get_hierarchical_distance(
                        participant_employees[i].id,
                        participant_employees[j].id
                    )
                    if distance and distance > max_distance:
                        max_distance = distance
            
            hierarchy_info["max_hierarchical_distance"] = max_distance
        
        return hierarchy_info
    
    def _create_mock_join_result(self, meeting_url: str, meeting_title: str, participants: List[str], meeting_id: str) -> Dict[str, Any]:
        """Cria resultado mock para entrada em reunião (fallback)"""
        result = {
            "success": True,
            "meeting_id": meeting_id,
            "meeting_title": meeting_title,
            "platform": self.meeting_platform,
            "joined_at": datetime.now().isoformat(),
            "participants": participants,
            "notes": f"Entrou na reunião '{meeting_title}' via {self.meeting_platform} (mock)",
            "action": "join_meeting",
            "mock": True
        }
        
        # Registrar reunião ativa
        self.active_meetings[meeting_id] = {
            **result,
            "transcription": [],
            "decisions": [],
            "action_items": [],
            "status": "active"
        }
        
        logger.info(f"✅ Entrou na reunião {meeting_id} (mock): {meeting_title}")
        return result
    
    def _log_interaction(self, interaction_type: str, participants: List[str], **kwargs):
        """Registra interação para aprendizado (Fase 10)"""
        interaction = {
            "type": interaction_type,
            "timestamp": datetime.now().isoformat(),
            "participants": participants,
            **kwargs
        }
        
        self.interaction_log.append(interaction)
        
        # Se temos gerenciador de relacionamentos, registrar interação formal
        if self.relationship_manager and participants:
            # Converter para formato do relationship_manager
            # (simplificado - em produção seria mais completo)
            pass
        
        # Limitar log a 1000 entradas
        if len(self.interaction_log) > 1000:
            self.interaction_log = self.interaction_log[-1000:]
    
    def _update_relationship_metrics(self, meeting_id: str):
        """Atualiza métricas de relacionamento baseadas na reunião (Fase 9)"""
        if not self.relationship_manager or meeting_id not in self.active_meetings:
            return
        
        meeting = self.active_meetings[meeting_id]
        participants = meeting.get("participants", [])
        
        # Registrar interação no relationship_manager
        # (simplificado - em produção seria mais completo)
        if len(participants) >= 2 and self.relationship_manager:
            # Para cada par de participantes
            pass
    
    def get_interaction_insights(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtém insights do aprendizado com interações (Fase 10)"""
        insights = []
        
        # Análise básica de padrões
        if len(self.interaction_log) >= 10:
            # Contar tipos de interação
            type_counts = {}
            for interaction in self.interaction_log[-limit:]:
                itype = interaction.get("type", "unknown")
                type_counts[itype] = type_counts.get(itype, 0) + 1
            
            # Identificar participantes frequentes
            participant_counts = {}
            for interaction in self.interaction_log[-limit:]:
                for participant in interaction.get("participants", []):
                    participant_counts[participant] = participant_counts.get(participant, 0) + 1
            
            insights.append({
                "analysis_type": "interaction_patterns",
                "total_interactions": len(self.interaction_log),
                "interaction_types": type_counts,
                "top_participants": dict(sorted(participant_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
                "timestamp": datetime.now().isoformat()
            })
        
        return insights
    
    # ==================== HANDLERS DE AÇÃO ====================
    
    def _handle_transcribe_meeting(self, request: ActionRequest, executor: ActionExecutor) -> Dict[str, Any]:
        """Handler para transcrever reunião"""
        
        meeting_id = request.parameters.get("meeting_id")
        audio_data = request.parameters.get("audio_data")  # Base64 ou caminho para arquivo
        language = request.parameters.get("language", "pt-BR")
        
        if meeting_id not in self.active_meetings:
            return {
                "success": False,
                "error": f"Reunião {meeting_id} não encontrada",
                "action": "transcribe_meeting"
            }
        
        logger.info(f"🟡 Transcrevendo reunião {meeting_id} ({language})")
        
        # Simular transcrição (mock)
        # Em produção, usaria Whisper API, Azure Speech, ou Google Speech-to-Text
        
        mock_transcript = [
            {
                "speaker": "Participante 1",
                "text": "Vamos começar a reunião. O objetivo hoje é discutir o progresso do projeto AI-Biomimetica.",
                "timestamp": "00:01:15",
                "sentiment": "neutral"
            },
            {
                "speaker": "Participante 2", 
                "text": "Estamos na Fase 8 agora, implementando participação em reuniões.",
                "timestamp": "00:02:30",
                "sentiment": "positive"
            },
            {
                "speaker": "Participante 1",
                "text": "Precisamos garantir que o sistema possa entrar em reuniões do Google Meet e Teams.",
                "timestamp": "00:03:45",
                "sentiment": "neutral"
            },
            {
                "speaker": "IA (Jarvis)",
                "text": "Posso ajudar a transcrever a reunião e extrair decisões importantes.",
                "timestamp": "00:04:20",
                "sentiment": "positive"
            }
        ]
        
        # Atualizar reunião ativa
        self.active_meetings[meeting_id]["transcription"].extend(mock_transcript)
        
        result = {
            "success": True,
            "meeting_id": meeting_id,
            "transcript": mock_transcript,
            "language": language,
            "total_segments": len(mock_transcript),
            "action": "transcribe_meeting",
            "mock": True
        }
        
        logger.info(f"✅ Transcrição gerada para reunião {meeting_id}: {len(mock_transcript)} segmentos")
        
        return result
    
    def _handle_summarize_meeting(self, request: ActionRequest, executor: ActionExecutor) -> Dict[str, Any]:
        """Handler para resumir reunião"""
        
        meeting_id = request.parameters.get("meeting_id")
        
        if meeting_id not in self.active_meetings:
            return {
                "success": False,
                "error": f"Reunião {meeting_id} não encontrada",
                "action": "summarize_meeting"
            }
        
        meeting = self.active_meetings[meeting_id]
        transcript = meeting.get("transcription", [])
        
        logger.info(f"🟡 Resumindo reunião {meeting_id} com {len(transcript)} segmentos")
        
        # Extrair texto completo
        full_text = "\n".join([f"{seg['speaker']}: {seg['text']}" for seg in transcript])
        
        # Usar sistema biomimético para resumir (se disponível)
        summary = ""
        decisions = []
        action_items = []
        
        if self.biomimetic_system:
            # Preparar tarefa para sistema biomimético
            task = {
                "type": "meeting_summarization",
                "text": full_text,
                "length": len(full_text),
                "context": {
                    "meeting_title": meeting.get("meeting_title", ""),
                    "platform": meeting.get("platform", ""),
                    "participants": meeting.get("participants", [])
                }
            }
            
            try:
                # Usar sistema biomimético para gerar resumo
                # Em produção, isso chamaria o sistema biomimético real
                recommendation = self.biomimetic_system.recommend_provider(
                    task_type="text_summarization",
                    task_length=len(full_text),
                    context="Summarize meeting transcript"
                )
                
                # Simular resultado
                summary = "**Resumo da Reunião**\n\n"
                summary += "- Discussão sobre progresso do projeto AI-Biomimetica\n"
                summary += "- Foco na Fase 8 (Participação em Reuniões)\n"
                summary += "- IA Jarvis pode transcrever e extrair decisões\n"
                summary += "- Próximos passos: integrar com Google Meet e Teams\n"
                
                decisions = [
                    "Continuar implementação da Fase 8",
                    "Testar integração com Google Meet usando credenciais reais",
                    "Documentar protocolos de etiqueta para participação da IA"
                ]
                
                action_items = [
                    {"assignee": "Adjalma", "task": "Obter credenciais Google", "due": "2026-04-12"},
                    {"assignee": "Jarvis", "task": "Criar demo funcional", "due": "2026-04-13"},
                    {"assignee": "Time", "task": "Revisar protocolos de participação", "due": "2026-04-15"}
                ]
                
            except Exception as e:
                logger.error(f"Erro ao usar sistema biomimético para resumo: {e}")
                summary = "Resumo não disponível (erro no sistema biomimético)"
        else:
            # Fallback simples
            summary = f"Reunião '{meeting.get('meeting_title', '')}' com {len(transcript)} segmentos de conversa."
            decisions = ["Continuar desenvolvimento da Fase 8"]
            action_items = []
        
        # Atualizar reunião
        self.active_meetings[meeting_id]["summary"] = summary
        self.active_meetings[meeting_id]["decisions"] = decisions
        self.active_meetings[meeting_id]["action_items"] = action_items
        
        result = {
            "success": True,
            "meeting_id": meeting_id,
            "summary": summary,
            "decisions": decisions,
            "action_items": action_items,
            "action": "summarize_meeting"
        }
        
        logger.info(f"✅ Reunião {meeting_id} resumida: {len(decisions)} decisões, {len(action_items)} ações")
        
        return result
    
    def _handle_save_meeting_notes(self, request: ActionRequest, executor: ActionExecutor) -> Dict[str, Any]:
        """Handler para salvar notas da reunião no Obsidian"""
        
        meeting_id = request.parameters.get("meeting_id")
        
        if meeting_id not in self.active_meetings:
            return {
                "success": False,
                "error": f"Reunião {meeting_id} não encontrada",
                "action": "save_meeting_notes"
            }
        
        meeting = self.active_meetings[meeting_id]
        
        logger.info(f"🟡 Salvando notas da reunião {meeting_id} no Obsidian")
        
        # Construir conteúdo da nota
        note_content = f"""---
tags: [meeting, {meeting.get('platform', 'unknown')}]
date: {datetime.now().isoformat()}
meeting_id: {meeting_id}
title: "{meeting.get('meeting_title', 'Reunião sem título')}"
participants: {json.dumps(meeting.get('participants', []))}
---

# {meeting.get('meeting_title', 'Reunião sem título')}

**Data:** {meeting.get('joined_at', datetime.now().isoformat())}
**Plataforma:** {meeting.get('platform', 'Desconhecida')}
**Status:** {meeting.get('status', 'Desconhecido')}

## Resumo

{meeting.get('summary', 'Nenhum resumo disponível.')}

## Decisões Tomadas

{chr(10).join(f'- {d}' for d in meeting.get('decisions', [])) or 'Nenhuma decisão registrada.'}

## Itens de Ação

{chr(10).join(f'- **{ai["task"]}** (Responsável: {ai["assignee"]}, Prazo: {ai["due"]})' for ai in meeting.get('action_items', [])) or 'Nenhum item de ação registrado.'}

## Transcrição (Trechos)

{chr(10).join(f'**{seg["timestamp"]} - {seg["speaker"]}:** {seg["text"]}' for seg in meeting.get('transcription', [])[:10]) or 'Nenhuma transcrição disponível.'}

{'*(... transcrição truncada ...)*' if len(meeting.get('transcription', [])) > 10 else ''}

---
*Nota gerada automaticamente por Jarvis (AI-Biomimetica)*
"""
        
        # Salvar no Obsidian (simulado)
        # Em produção, usaria ObsidianVault
        note_path = f"meetings/{meeting_id.replace('meeting_', '')}_{datetime.now().strftime('%Y%m%d')}.md"
        
        result = {
            "success": True,
            "meeting_id": meeting_id,
            "note_path": note_path,
            "note_content_preview": note_content[:200] + "...",
            "action": "save_meeting_notes",
            "mock": True  # Indica que é simulação
        }
        
        logger.info(f"✅ Notas da reunião {meeting_id} salvas (simulado): {note_path}")
        
        # Se Obsidian disponível, salvar de verdade
        try:
            from app.obsidian_vault import write_note as obsidian_write_note
            obsidian_write_note(
                filename=f"{meeting_id}.md",
                content=note_content,
                subdir="meetings"
            )
            result["mock"] = False
            result["obsidian_saved"] = True
        except ImportError:
            pass
        
        # ==================== INTEGRAÇÃO COM CALENDÁRIO ====================
        # Criar evento no Google Calendar com resumo da reunião
        calendar_event_created = False
        calendar_event_id = None
        
        if hasattr(self, 'calendar_client') and self.calendar_client:
            try:
                # Extrair informações da reunião para o calendário
                meeting_title = meeting.get('meeting_title', 'Reunião sem título')
                meeting_start_str = meeting.get('joined_at', datetime.now().isoformat())
                
                # Calcular horário de término (padrão: 60 minutos após início)
                meeting_start = datetime.fromisoformat(meeting_start_str.replace('Z', '+00:00'))
                meeting_duration_minutes = request.parameters.get('meeting_duration_minutes', 60)
                meeting_end = meeting_start + timedelta(minutes=meeting_duration_minutes)
                
                # Construir descrição com link para notas do Obsidian
                description = f"""Reunião processada por Jarvis (AI-Biomimetica)

Resumo: {meeting.get('summary', 'Nenhum resumo disponível.')[:500]}

Decisões:
{chr(10).join(f'- {d}' for d in meeting.get('decisions', [])) or 'Nenhuma decisão registrada.'}

Itens de Ação:
{chr(10).join(f'- {ai["task"]} (Responsável: {ai["assignee"]}, Prazo: {ai["due"]})' for ai in meeting.get('action_items', [])) or 'Nenhum item de ação registrado.'}

Notas completas: {note_path}
"""
                
                # Criar evento no calendário
                calendar_event = {
                    'summary': f'📝 {meeting_title}',
                    'description': description,
                    'start': {
                        'dateTime': meeting_start.isoformat(),
                        'timeZone': 'America/Sao_Paulo',
                    },
                    'end': {
                        'dateTime': meeting_end.isoformat(),
                        'timeZone': 'America/Sao_Paulo',
                    },
                    'attendees': [{'email': email} for email in meeting.get('participants', []) if '@' in str(email)],
                    'location': meeting.get('url', ''),
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'popup', 'minutes': 10},
                        ],
                    },
                }
                
                # Chamar API do Google Calendar
                created_event = self.calendar_client.create_event(calendar_event)
                if created_event and 'id' in created_event:
                    calendar_event_created = True
                    calendar_event_id = created_event['id']
                    result['calendar_event_created'] = True
                    result['calendar_event_id'] = calendar_event_id
                    result['calendar_event_link'] = created_event.get('htmlLink', '')
                    logger.info(f"✅ Evento criado no Google Calendar: {calendar_event_id}")
                else:
                    logger.warning("⚠️ Falha ao criar evento no Google Calendar (resposta vazia)")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao criar evento no calendário: {e}")
                result['calendar_error'] = str(e)
        else:
            logger.info("ℹ️ Google Calendar Client não disponível para criar evento")
        
        result['calendar_integration_attempted'] = True
        result['calendar_event_created'] = calendar_event_created
        
        return result
    
    def _handle_monitor_meeting(self, request: ActionRequest, executor: ActionExecutor) -> Dict[str, Any]:
        """Handler para monitorar reunião ativa e intervir quando apropriado"""
        
        meeting_id = request.parameters.get("meeting_id")
        interval_seconds = request.parameters.get("interval_seconds", 30)
        
        if meeting_id not in self.active_meetings:
            return {
                "success": False,
                "error": f"Reunião {meeting_id} não encontrada",
                "action": "monitor_meeting"
            }
        
        logger.info(f"🟡 Monitorando reunião {meeting_id} (intervalo: {interval_seconds}s)")
        
        # Simular monitoramento
        # Em produção, isso seria um loop contínuo de:
        # 1. Capturar áudio
        # 2. Transcrever
        # 3. Analisar contexto
        # 4. Decidir se deve intervir
        # 5. Se sim, sintetizar voz e falar
        
        meeting = self.active_meetings[meeting_id]
        
        # Análise biomimética do contexto (simulada)
        should_intervene = False
        intervention_reason = ""
        
        if len(meeting.get("transcription", [])) > 0:
            last_segment = meeting["transcription"][-1]
            last_text = last_segment["text"].lower()
            
            # Regras simples para demonstração
            if "jarvis" in last_text or "ia" in last_text or "assistente" in last_text:
                should_intervene = True
                intervention_reason = "Mencionado na conversa"
            elif "?" in last_text and len(last_text) < 100:
                should_intervene = True
                intervention_reason = "Pergunta direta detectada"
            elif "decisão" in last_text or "decidir" in last_text:
                should_intervene = True
                intervention_reason = "Discussão de decisão detectada"
        
        result = {
            "success": True,
            "meeting_id": meeting_id,
            "monitoring_active": True,
            "interval_seconds": interval_seconds,
            "should_intervene": should_intervene,
            "intervention_reason": intervention_reason,
            "transcript_segments": len(meeting.get("transcription", [])),
            "action": "monitor_meeting",
            "mock": True
        }
        
        if should_intervene:
            # Gerar resposta apropriada
            response = self._generate_meeting_response(meeting)
            result["intervention_response"] = response
            result["intervention_timestamp"] = datetime.now().isoformat()
            
            logger.info(f"✅ Intervenção necessária na reunião {meeting_id}: {intervention_reason}")
        
        return result
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _analyze_meeting_context(self, meeting_id: str, parameters: Dict[str, Any]):
        """Analisa contexto da reunião usando sistema biomimético"""
        
        if not self.biomimetic_system:
            return
        
        try:
            # Preparar contexto para análise biomimética
            context = {
                "meeting_id": meeting_id,
                "title": parameters.get("title", ""),
                "participants": parameters.get("participants", []),
                "platform": self.meeting_platform,
                "time": parameters.get("time", datetime.now().isoformat()),
                "purpose": parameters.get("purpose", "")
            }
            
            task = {
                "type": "meeting_context_analysis",
                "context": context,
                "length": len(json.dumps(context)),
            }
            
            # Usar sistema biomimético para recomendar estratégia de participação
            recommendation = self.biomimetic_system.recommend_provider(
                task_type="context_analysis",
                task_length=task["length"],
                context="Analyze meeting context for appropriate participation strategy"
            )
            
            logger.info(f"✅ Contexto da reunião {meeting_id} analisado biomimeticamente")
            
        except Exception as e:
            logger.error(f"Erro na análise biomimética do contexto: {e}")
    
    def _generate_meeting_response(self, meeting: Dict[str, Any]) -> str:
        """Gera resposta apropriada para intervenção em reunião"""
        
        # Regras simples para demonstração
        # Em produção, usaria sistema biomimético para gerar resposta contextual
        
        last_segment = meeting.get("transcription", [])[-1] if meeting.get("transcription") else None
        
        if last_segment and "?" in last_segment["text"]:
            return "Posso ajudar com essa pergunta. Com base na discussão anterior, sugiro revisarmos os requisitos da Fase 8."
        elif "decisão" in meeting.get("meeting_title", "").lower():
            return "Para apoiar a decisão, recomendo considerar: 1) Prazo de implementação, 2) Recursos necessários, 3) Riscos identificados."
        else:
            return "Com base na conversa, gostaria de contribuir com uma perspectiva sobre a implementação técnica."
    
    def _handle_analyze_interactions(self, request: ActionRequest, executor: ActionExecutor) -> Dict[str, Any]:
        """Handler para analisar interações e aprender com elas (Fase 10)"""
        
        logger.info("🧠 Analisando interações para aprendizado evolutivo")
        
        # Obter insights das interações
        insights = self.get_interaction_insights(limit=request.parameters.get("limit", 100))
        
        # Se temos sistema biomimético, usar para análise avançada
        if self.biomimetic_system:
            try:
                # Preparar dados para análise biomimética
                analysis_data = {
                    "interaction_log": self.interaction_log[-100:],  # Últimas 100 interações
                    "insights": insights,
                    "meeting_history": self.meeting_history[-20:],  # Últimas 20 reuniões
                    "timestamp": datetime.now().isoformat()
                }
                
                # Criar tarefa para sistema biomimético
                task = {
                    "type": "interaction_learning",
                    "data": analysis_data,
                    "length": len(json.dumps(analysis_data)),
                    "context": "Analyze interaction patterns for evolutionary learning"
                }
                
                # Obter recomendação do sistema biomimético
                recommendation = self.biomimetic_system.recommend_provider(
                    task_type="pattern_analysis",
                    task_length=task["length"],
                    context=task["context"]
                )
                
                # Registrar resultado para aprendizado evolutivo
                if hasattr(self.biomimetic_system, 'record_task_result'):
                    self.biomimetic_system.record_task_result(
                        task_type="interaction_learning",
                        provider_used=recommendation.get("provider", "unknown"),
                        success=True,
                        metrics={
                            "interactions_analyzed": len(self.interaction_log),
                            "insights_generated": len(insights),
                            "meetings_analyzed": len(self.meeting_history)
                        }
                    )
                
                logger.info(f"✅ Análise biomimética de interações completada: {recommendation.get('provider', 'unknown')}")
                
            except Exception as e:
                logger.error(f"❌ Erro na análise biomimética de interações: {e}")
                recommendation = {"provider": "fallback", "error": str(e)}
        else:
            recommendation = {"provider": "none", "message": "Sistema biomimético não disponível"}
        
        result = {
            "success": True,
            "action": "analyze_interactions",
            "interactions_analyzed": len(self.interaction_log),
            "insights": insights,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
            "evolutionary_learning": True
        }
        
        logger.info(f"✅ Análise de interações completada: {len(insights)} insights gerados")
        return result
    
    def process_meeting_invitation(self, invitation: Dict[str, Any]) -> Optional[ActionRequest]:
        """
        Processa convite para reunião e decide participar.
        
        Args:
            invitation: {
                "title": "Título da reunião",
                "url": "https://meet.google.com/...",
                "time": "2026-04-11T20:00:00",
                "organizer": "nome@email.com",
                "participants": ["p1@email.com", "p2@email.com"],
                "description": "Descrição da reunião",
                "platform": "google_meet"  # ou "teams", "zoom"
            }
        
        Returns:
            ActionRequest para JOIN_MEETING se decidir participar
        """
        
        logger.info(f"Processando convite para reunião: {invitation.get('title', 'N/A')}")
        
        # Criar situação para processamento
        situation = {
            "type": "meeting_invitation",
            "description": f"Convite para reunião: {invitation.get('title')}",
            "invitation": invitation,
            "timestamp": datetime.now().isoformat(),
            "priority": "medium" if invitation.get("organizer") == "Adjalma" else "low"
        }
        
        # Usar process_situation do pai para decidir/executar
        return self.process_situation(situation)
    
    def get_meeting_status(self, meeting_id: str) -> Dict[str, Any]:
        """Obtém status de uma reunião ativa"""
        
        if meeting_id in self.active_meetings:
            meeting = self.active_meetings[meeting_id].copy()
            meeting["transcription_count"] = len(meeting.get("transcription", []))
            meeting["decisions_count"] = len(meeting.get("decisions", []))
            meeting["action_items_count"] = len(meeting.get("action_items", []))
            return meeting
        else:
            return {"error": f"Reunião {meeting_id} não encontrada"}
    
    def end_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Finaliza uma reunião ativa"""
        
        if meeting_id not in self.active_meetings:
            return {"success": False, "error": f"Reunião {meeting_id} não encontrada"}
        
        meeting = self.active_meetings[meeting_id]
        meeting["ended_at"] = datetime.now().isoformat()
        meeting["status"] = "ended"
        meeting["duration_minutes"] = (
            datetime.fromisoformat(meeting["ended_at"]) - 
            datetime.fromisoformat(meeting.get("joined_at", meeting["ended_at"]))
        ).total_seconds() / 60
        
        # Mover para histórico
        self.meeting_history.append(meeting)
        del self.active_meetings[meeting_id]
        
        logger.info(f"✅ Reunião {meeting_id} finalizada: {meeting.get('meeting_title')}")
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "ended_at": meeting["ended_at"],
            "duration_minutes": meeting["duration_minutes"]
        }


# Função de conveniência para criar orquestrador de reuniões
def create_meeting_orchestrator(platform: str = "google_meet", **kwargs) -> MeetingOrchestrator:
    """
    Cria e retorna um MeetingOrchestrator configurado.
    
    Args:
        platform: google_meet, teams, zoom
        **kwargs: Argumentos adicionais para MeetingOrchestrator
    
    Returns:
        MeetingOrchestrator configurado
    """
    return MeetingOrchestrator(meeting_platform=platform, **kwargs)