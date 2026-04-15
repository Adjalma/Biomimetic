#!/usr/bin/env python3
"""
Gerenciador de Conversação Inteligente
======================================

Sistema unificado que integra:
1. Análise emocional em tempo real
2. Otimização biomimética de estilo de resposta
3. Aprendizado contínuo com feedback
4. Integração com sistema de memória e perfil do usuário

Ponto de entrada principal para conversação avançada do assistente.

Autor: Jarvis (OpenClaw)
Data: 2026-04-12
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
import json
from datetime import datetime
import uuid

# Importar módulos internos
try:
    from .emotional_analyzer import EmotionalAnalyzer, EmotionalAnalysis
    EMOTIONAL_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ EmotionalAnalyzer não disponível: {e}")
    EMOTIONAL_ANALYZER_AVAILABLE = False

try:
    from .conversation_optimizer import ConversationOptimizer, ResponseStyle, ResponseParameter
    CONVERSATION_OPTIMIZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ ConversationOptimizer não disponível: {e}")
    CONVERSATION_OPTIMIZER_AVAILABLE = False

try:
    from .memory_agent import JarvisMemoryAgent
    MEMORY_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MemoryAgent não disponível: {e}")
    MEMORY_AGENT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Contexto completo de uma conversação"""
    conversation_id: str
    user_id: str
    history: List[Dict[str, Any]] = field(default_factory=list)
    context_tags: List[str] = field(default_factory=list)
    emotional_trend: List[EmotionalAnalysis] = field(default_factory=list)
    style_history: List[ResponseStyle] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, style: Optional[ResponseStyle] = None):
        """Adiciona mensagem ao histórico"""
        message_id = str(uuid.uuid4())[:8]
        message = {
            "id": message_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "style": style.to_dict() if style else None
        }
        self.history.append(message)
        
        # Manter histórico limitado
        if len(self.history) > 50:
            self.history = self.history[-50:]
    
    def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """Obtém mensagens recentes"""
        return self.history[-count:] if self.history else []
    
    def get_emotional_trend(self) -> Optional[str]:
        """Obtém tendência emocional recente"""
        if not self.emotional_trend:
            return None
        
        # Analisar últimas 5 análises emocionais
        recent = self.emotional_trend[-5:]
        emotions = [analysis.primary_emotion.value for analysis in recent]
        
        from collections import Counter
        if emotions:
            most_common = Counter(emotions).most_common(1)[0][0]
            return most_common
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "history_length": len(self.history),
            "context_tags": self.context_tags,
            "emotional_trend": self.get_emotional_trend(),
            "metadata": self.metadata
        }


class ConversationManager:
    """
    Gerenciador principal de conversação inteligente
    """
    
    def __init__(
        self,
        use_emotional_analysis: bool = True,
        use_style_optimization: bool = True,
        use_memory_integration: bool = True,
        use_biomimetic_learning: bool = True
    ):
        # Configurações
        self.use_emotional_analysis = use_emotional_analysis and EMOTIONAL_ANALYZER_AVAILABLE
        self.use_style_optimization = use_style_optimization and CONVERSATION_OPTIMIZER_AVAILABLE
        self.use_memory_integration = use_memory_integration and MEMORY_AGENT_AVAILABLE
        self.use_biomimetic_learning = use_biomimetic_learning
        
        # Componentes
        self.emotional_analyzer = None
        self.conversation_optimizer = None
        self.memory_agent = None
        
        # Inicializar componentes
        if self.use_emotional_analysis:
            try:
                self.emotional_analyzer = EmotionalAnalyzer()
                logger.info("✅ Analisador emocional inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar analisador emocional: {e}")
                self.use_emotional_analysis = False
        
        if self.use_style_optimization:
            try:
                self.conversation_optimizer = ConversationOptimizer(
                    use_biomimetic=use_biomimetic_learning
                )
                logger.info("✅ Otimizador de conversação inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar otimizador de conversação: {e}")
                self.use_style_optimization = False
        
        if self.use_memory_integration:
            try:
                self.memory_agent = JarvisMemoryAgent()
                logger.info("✅ Agente de memória inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar agente de memória: {e}")
                self.use_memory_integration = False
        
        # Contextos de conversação ativos
        self.active_conversations: Dict[str, ConversationContext] = {}
        
        # Callbacks para feedback
        self.feedback_callbacks = []
        
        # Estatísticas
        self.stats = {
            "total_messages_processed": 0,
            "conversations_started": 0,
            "emotional_analyses_performed": 0,
            "style_optimizations_performed": 0
        }
        
        logger.info("Gerenciador de conversação inicializado")
    
    def process_user_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        context_tags: Optional[List[str]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa mensagem do usuário e retorna análise + estilo otimizado
        
        Args:
            user_id: Identificador do usuário
            message: Mensagem do usuário
            conversation_id: ID da conversação (opcional, cria nova se não existir)
            context_tags: Tags de contexto (ex: ["technical", "urgent"])
            additional_context: Contexto adicional (ex: plataforma, hora, etc.)
            
        Returns:
            Dicionário com:
            {
                "conversation_id": str,
                "emotional_analysis": EmotionalAnalysis.to_dict(),
                "response_style": ResponseStyle.to_dict(),
                "conversation_context": ConversationContext.to_dict(),
                "recommendations": List[str],
                "processing_metadata": {...}
            }
        """
        # 1. Gerenciar contexto da conversação
        conv_context = self._get_or_create_conversation(
            user_id, conversation_id, context_tags, additional_context
        )
        
        # Adicionar mensagem do usuário ao histórico
        conv_context.add_message("user", message)
        
        # 2. Análise emocional
        emotional_analysis = None
        if self.use_emotional_analysis and self.emotional_analyzer:
            try:
                emotional_analysis = self.emotional_analyzer.analyze(message, user_id)
                conv_context.emotional_trend.append(emotional_analysis)
                self.stats["emotional_analyses_performed"] += 1
                
                # Limitar histórico emocional
                if len(conv_context.emotional_trend) > 10:
                    conv_context.emotional_trend = conv_context.emotional_trend[-10:]
            except Exception as e:
                logger.error(f"Erro na análise emocional: {e}")
        
        # 3. Otimização de estilo
        response_style = None
        if self.use_style_optimization and self.conversation_optimizer:
            try:
                response_style = self.conversation_optimizer.optimize_response_style(
                    user_message=message,
                    user_id=user_id,
                    context_tags=conv_context.context_tags,
                    conversation_history=conv_context.get_recent_messages(10)
                )
                conv_context.style_history.append(response_style)
                self.stats["style_optimizations_performed"] += 1
                
                # Limitar histórico de estilos
                if len(conv_context.style_history) > 10:
                    conv_context.style_history = conv_context.style_history[-10:]
            except Exception as e:
                logger.error(f"Erro na otimização de estilo: {e}")
        
        # 4. Integração com memória (obter contexto adicional)
        memory_context = None
        if self.use_memory_integration and self.memory_agent:
            try:
                memory_context = self._get_memory_context(user_id, message, conv_context)
            except Exception as e:
                logger.error(f"Erro na integração com memória: {e}")
        
        # 5. Gerar recomendações baseadas na análise
        recommendations = self._generate_recommendations(
            emotional_analysis, response_style, memory_context
        )
        
        # 6. Atualizar estatísticas
        self.stats["total_messages_processed"] += 1
        
        # 7. Preparar resultado
        result = {
            "conversation_id": conv_context.conversation_id,
            "emotional_analysis": emotional_analysis.to_dict() if emotional_analysis else None,
            "response_style": response_style.to_dict() if response_style else None,
            "conversation_context": conv_context.to_dict(),
            "recommendations": recommendations,
            "processing_metadata": {
                "components_used": {
                    "emotional_analysis": bool(emotional_analysis),
                    "style_optimization": bool(response_style),
                    "memory_integration": bool(memory_context)
                },
                "processing_timestamp": datetime.now().isoformat()
            }
        }
        
        # Adicionar contexto de memória se disponível
        if memory_context:
            result["memory_context"] = memory_context
        
        logger.debug(f"Mensagem processada para {user_id} (conversação: {conv_context.conversation_id})")
        return result
    
    def _get_or_create_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str],
        context_tags: Optional[List[str]],
        additional_context: Optional[Dict[str, Any]]
    ) -> ConversationContext:
        """Obtém ou cria contexto de conversação"""
        if conversation_id and conversation_id in self.active_conversations:
            conv = self.active_conversations[conversation_id]
            
            # Atualizar tags de contexto se fornecidas
            if context_tags:
                # Adicionar novas tags sem duplicatas
                existing_tags = set(conv.context_tags)
                new_tags = [tag for tag in context_tags if tag not in existing_tags]
                conv.context_tags.extend(new_tags)
            
            # Atualizar metadados
            if additional_context:
                conv.metadata.update(additional_context)
            
            return conv
        
        # Criar nova conversação
        new_conv_id = conversation_id or str(uuid.uuid4())[:12]
        
        conv = ConversationContext(
            conversation_id=new_conv_id,
            user_id=user_id,
            context_tags=context_tags or [],
            metadata=additional_context or {}
        )
        
        self.active_conversations[new_conv_id] = conv
        self.stats["conversations_started"] += 1
        
        logger.info(f"Nova conversação iniciada: {new_conv_id} para {user_id}")
        return conv
    
    def _get_memory_context(
        self,
        user_id: str,
        message: str,
        conversation_context: ConversationContext
    ) -> Dict[str, Any]:
        """Obtém contexto relevante da memória"""
        memory_context = {
            "user_preferences": {},
            "relevant_history": [],
            "project_context": None
        }
        
        try:
            # 1. Obter preferências do usuário do perfil
            if self.conversation_optimizer:
                user_profile = self.conversation_optimizer.get_user_profile(user_id)
                memory_context["user_preferences"] = user_profile
            
            # 2. Obter contexto do projeto AI-Biomimetica
            project_state = self.memory_agent.scan_project_state()
            memory_context["project_context"] = {
                "phases_implemented": project_state.get("phases_implemented", []),
                "pending_tasks": project_state.get("pending_tasks", []),
                "recent_changes": project_state.get("recent_changes", [])
            }
            
            # 3. Verificar histórico relevante
            # (implementação simplificada - em produção seria mais sofisticada)
            daily_memories = self.memory_agent.read_daily_memory(days_back=3)
            memory_context["recent_memories"] = list(daily_memories.keys())
            
        except Exception as e:
            logger.error(f"Erro ao obter contexto de memória: {e}")
        
        return memory_context
    
    def _generate_recommendations(
        self,
        emotional_analysis: Optional[EmotionalAnalysis],
        response_style: Optional[ResponseStyle],
        memory_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Recomendações baseadas em emoção
        if emotional_analysis:
            emotion = emotional_analysis.primary_emotion
            intensity = emotional_analysis.intensity
            
            if emotion.value == "frustrated" and intensity > 0.7:
                recommendations.append("Focar em soluções práticas e imediatas")
                recommendations.append("Evitar detalhes técnicos extensos")
                recommendations.append("Usar linguagem direta e empática")
            
            elif emotion.value == "urgent" and intensity > 0.6:
                recommendations.append("Ser conciso e direto ao ponto")
                recommendations.append("Priorizar ações imediatas")
                recommendations.append("Evitar digressões ou histórias")
            
            elif emotion.value == "curious" and intensity > 0.6:
                recommendations.append("Fornecer explicações detalhadas")
                recommendations.append("Incluir exemplos práticos")
                recommendations.append("Sugerir recursos para aprendizado adicional")
            
            elif emotion.value == "tired" and intensity > 0.5:
                recommendations.append("Simplificar linguagem")
                recommendations.append("Dividir informações em partes pequenas")
                recommendations.append("Oferecer resumos executivos")
        
        # Recomendações baseadas em estilo
        if response_style:
            params = response_style.parameters
            
            # Verificar parâmetros extremos
            if params.get(ResponseParameter.VERBOSITY, 0.5) < 0.3:
                recommendations.append("Manter respostas muito concisas")
            
            if params.get(ResponseParameter.TECHNICAL_DEPTH, 0.5) > 0.7:
                recommendations.append("Incluir explicações técnicas detalhadas")
            
            if params.get(ResponseParameter.WARMTH, 0.5) > 0.7:
                recommendations.append("Usar linguagem calorosa e empática")
        
        # Recomendações baseadas em contexto de memória
        if memory_context:
            pending_tasks = memory_context.get("project_context", {}).get("pending_tasks", [])
            if pending_tasks:
                recommendations.append(f"Considerar {len(pending_tasks)} tarefas pendentes do projeto")
        
        return recommendations[:5]  # Limitar a 5 recomendações
    
    def apply_style_to_response(
        self,
        response_text: str,
        response_style: ResponseStyle,
        format_for_platform: str = "telegram"
    ) -> str:
        """
        Aplica estilo otimizado a uma resposta de texto
        
        Args:
            response_text: Texto da resposta (gerado pelo assistente)
            response_style: Estilo otimizado
            format_for_platform: Plataforma de destino (telegram, whatsapp, discord, etc.)
            
        Returns:
            Texto ajustado conforme o estilo
        """
        if not response_style:
            return response_text
        
        # Obter parâmetros
        params = response_style.parameters
        
        # 1. Ajustar verbosidade (comprimento)
        target_verbosity = params.get(ResponseParameter.VERBOSITY, 0.5)
        current_length = len(response_text)
        
        # Alvo de comprimento baseado em verbosidade (500-2000 caracteres)
        target_length = 500 + int(target_verbosity * 1500)
        
        if current_length > target_length * 1.5 and target_verbosity < 0.7:
            # Texto muito longo para verbosidade desejada → resumir
            response_text = self._summarize_text(response_text, target_length)
        elif current_length < target_length * 0.5 and target_verbosity > 0.6:
            # Texto muito curto para verbosidade desejada → expandir
            response_text = self._expand_text(response_text, target_length)
        
        # 2. Ajustar estrutura baseada no parâmetro STRUCTURE
        structure_level = params.get(ResponseParameter.STRUCTURE, 0.5)
        if structure_level > 0.7:
            # Alta estruturação → adicionar formatação
            response_text = self._add_structure(response_text, format_for_platform)
        
        # 3. Ajustar nível técnico (simplificado)
        technical_depth = params.get(ResponseParameter.TECHNICAL_DEPTH, 0.5)
        if technical_depth < 0.3:
            # Baixo nível técnico → simplificar termos técnicos
            response_text = self._simplify_technical_terms(response_text)
        
        # 4. Adicionar calor/empatia baseado em WARMTH
        warmth = params.get(ResponseParameter.WARMTH, 0.5)
        if warmth > 0.7:
            response_text = self._add_warmth(response_text)
        
        # 5. Adicionar humor baseado em HUMOR_LEVEL
        humor_level = params.get(ResponseParameter.HUMOR_LEVEL, 0.0)
        if humor_level > 0.5 and format_for_platform in ["telegram", "whatsapp", "discord"]:
            response_text = self._add_humorous_touch(response_text)
        
        return response_text
    
    def _summarize_text(self, text: str, target_length: int) -> str:
        """Resume texto para comprimento alvo (implementação simplificada)"""
        if len(text) <= target_length:
            return text
        
        # Encontrar ponto de quebra natural próximo ao alvo
        sentences = text.split('. ')
        
        if len(sentences) <= 2:
            # Texto já curto ou sem muitas frases
            return text[:target_length] + "..."
        
        # Construir resumo com frases mais importantes
        summary = []
        current_length = 0
        
        # Priorizar primeiras frases (geralmente mais importantes)
        for sentence in sentences:
            if current_length + len(sentence) < target_length:
                summary.append(sentence)
                current_length += len(sentence) + 2  # +2 para ". "
            else:
                break
        
        if summary:
            result = '. '.join(summary) + '.'
            
            # Adicionar indicador de resumo se cortamos muito
            if len(result) < len(text) * 0.7:
                result += "\n\n(Resumido para ser mais conciso)"
            
            return result
        
        return text[:target_length] + "..."
    
    def _expand_text(self, text: str, target_length: int) -> str:
        """Expande texto para comprimento alvo (implementação simplificada)"""
        if len(text) >= target_length:
            return text
        
        # Adicionar explicações adicionais se o texto for muito curto
        expansions = [
            "\n\nDeseja que eu detalhe algum aspecto específico?",
            "\n\nPosso fornecer exemplos práticos se ajudar.",
            "\n\nExistem considerações adicionais relevantes para seu contexto.",
            "\n\nHá mais detalhes técnicos que posso compartilhar se for útil."
        ]
        
        # Escolher expansão baseada em comprimento necessário
        needed_length = target_length - len(text)
        
        if needed_length > 100 and len(text) < 300:
            # Texto muito curto, adicionar oferta de detalhamento
            return text + expansions[0]
        elif needed_length > 50:
            # Adicionar oferta de exemplos
            return text + expansions[1]
        
        return text
    
    def _add_structure(self, text: str, platform: str) -> str:
        """Adiciona estrutura ao texto (listas, títulos, etc.)"""
        # Simplificado: detectar se já tem estrutura
        if '\n- ' in text or '\n* ' in text or '\n1. ' in text:
            return text  # Já tem alguma estrutura
        
        # Para plataformas que suportam markdown
        if platform in ["telegram", "discord", "slack"]:
            # Adicionar formatação básica
            lines = text.split('\n')
            if len(lines) > 3:
                # Adicionar título principal
                if not lines[0].startswith('**'):
                    lines[0] = f"**{lines[0]}**"
                
                # Adicionar bullets para listas implícitas
                for i in range(1, len(lines)):
                    if len(lines[i]) > 20 and not lines[i].startswith(('-', '*', '•')):
                        lines[i] = f"• {lines[i]}"
                
                return '\n'.join(lines)
        
        return text
    
    def _simplify_technical_terms(self, text: str) -> str:
        """Simplifica termos técnicos (implementação simplificada)"""
        replacements = {
            "algoritmo": "método",
            "arquitetura": "estrutura",
            "biomimético": "inspirado na natureza",
            "orquestração": "coordenação",
            "otimização": "melhoria",
            "parâmetros": "configurações",
            "módulo": "parte",
            "integração": "conexão",
            "implementação": "aplicação",
            "funcionalidade": "funcionamento"
        }
        
        result = text
        for technical, simple in replacements.items():
            result = result.replace(technical, simple)
        
        return result
    
    def _add_warmth(self, text: str) -> str:
        """Adiciona calor/empatia ao texto"""
        # Evitar duplicar calor se já tiver
        warm_phrases = ["fico feliz", "entendo", "compreendo", "imagino", "sinto muito"]
        if any(phrase in text.lower() for phrase in warm_phrases):
            return text
        
        # Adicionar frase calorosa no início ou fim
        warm_openings = [
            "Entendo sua situação. ",
            "Compreendo o que você precisa. ",
            "Vamos resolver isso juntos. ",
            "Fico feliz em ajudar. "
        ]
        
        warm_closings = [
            "\n\nEspero que isso ajude!",
            "\n\nEstou aqui se precisar de mais alguma coisa.",
            "\n\nFico à disposição para qualquer dúvida.",
            "\n\nConte comigo para o que precisar."
        ]
        
        import random
        if len(text) > 100:
            # Adicionar no início se texto for longo
            text = random.choice(warm_openings) + text
        
        # Sempre adicionar no final
        text = text + random.choice(warm_closings)
        
        return text
    
    def _add_humorous_touch(self, text: str) -> str:
        """Adiciona toque humorístico (leve)"""
        humorous_additions = [
            "\n\n(Prometo que não é magia negra, só código bem escrito! 😄)",
            "\n\n(A IA não dorme, então estou sempre disponível! 🤖)",
            "\n\n(Isso foi mais fácil do que explicar o sistema tributário brasileiro! 😅)",
            "\n\n(Se fosse mais simples, já estaria obsoleto! 🚀)"
        ]
        
        import random
        # Adicionar humor apenas em 30% das vezes, mesmo com nível alto
        import random
        if random.random() < 0.3:
            return text + random.choice(humorous_additions)
        
        return text
    
    def register_feedback_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Registra callback para receber feedback"""
        self.feedback_callbacks.append(callback)
    
    def submit_feedback(
        self,
        conversation_id: str,
        feedback_data: Dict[str, Any]
    ):
        """
        Submete feedback sobre uma resposta
        
        Args:
            conversation_id: ID da conversação
            feedback_data: {
                "user_satisfaction": 0.0-1.0,
                "message_id": "id da mensagem respondida",
                "explicit_feedback": "texto do usuário",
                "engagement_metrics": {...},
                "response_effectiveness": 0.0-1.0
            }
        """
        # Atualizar otimizador com feedback
        if self.use_style_optimization and self.conversation_optimizer:
            try:
                # Obter contexto da conversação
                conv = self.active_conversations.get(conversation_id)
                if conv:
                    self.conversation_optimizer.update_user_profile_from_feedback(
                        user_id=conv.user_id,
                        feedback=feedback_data
                    )
            except Exception as e:
                logger.error(f"Erro ao atualizar perfil com feedback: {e}")
        
        # Atualizar analisador emocional com feedback
        if self.use_emotional_analysis and self.emotional_analyzer:
            try:
                # Extrair feedback emocional implícito
                if "explicit_feedback" in feedback_data:
                    explicit = feedback_data["explicit_feedback"]
                    
                    # Analisar feedback para detectar emoção real vs detectada
                    # (implementação simplificada)
                    feedback_analysis = self.emotional_analyzer.analyze(explicit)
                    
                    # Criar estrutura de feedback para aprendizado
                    emotion_feedback = {
                        "expected_emotion": feedback_analysis.primary_emotion.value,
                        "detected_emotion": "unknown",  # Precisaríamos do original
                        "intensity_match": 0.5,  # Assumir médio
                        "context": explicit[:200]
                    }
                    
                    if conv:
                        self.emotional_analyzer.update_user_profile(
                            user_id=conv.user_id,
                            feedback=emotion_feedback
                        )
            except Exception as e:
                logger.error(f"Erro ao atualizar analisador emocional com feedback: {e}")
        
        # Chamar callbacks registrados
        for callback in self.feedback_callbacks:
            try:
                callback({
                    "conversation_id": conversation_id,
                    "feedback": feedback_data,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Erro em callback de feedback: {e}")
        
        logger.info(f"Feedback processado para conversação {conversation_id}")
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Obtém contexto de conversação pelo ID"""
        return self.active_conversations.get(conversation_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do gerenciador"""
        return {
            **self.stats,
            "active_conversations": len(self.active_conversations),
            "components_active": {
                "emotional_analysis": self.use_emotional_analysis,
                "style_optimization": self.use_style_optimization,
                "memory_integration": self.use_memory_integration,
                "biomimetic_learning": self.use_biomimetic_learning
            }
        }
    
    def save_state(self, filepath: str = "conversation_manager_state.json"):
        """Salva estado do gerenciador"""
        state = {
            "active_conversations": {
                conv_id: {
                    "conversation_id": conv.conversation_id,
                    "user_id": conv.user_id,
                    "context_tags": conv.context_tags,
                    "history_length": len(conv.history),
                    "metadata": conv.metadata
                }
                for conv_id, conv in self.active_conversations.items()
            },
            "stats": self.stats,
            "metadata": {
                "save_timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info(f"Estado salvo em {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Limpa conversações antigas"""
        current_time = datetime.now()
        removed_count = 0
        
        conv_ids_to_remove = []
        
        for conv_id, conv in self.active_conversations.items():
            # Verificar última atividade (simplificado)
            if conv.history:
                last_message = conv.history[-1]
                last_timestamp = datetime.fromisoformat(last_message["timestamp"])
                age_hours = (current_time - last_timestamp).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    conv_ids_to_remove.append(conv_id)
        
        for conv_id in conv_ids_to_remove:
            del self.active_conversations[conv_id]
            removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Removidas {removed_count} conversações antigas")


# Função de conveniência para uso rápido
def create_conversation_manager() -> ConversationManager:
    """Cria gerenciador de conversação com configurações padrão"""
    return ConversationManager(
        use_emotional_analysis=True,
        use_style_optimization=True,
        use_memory_integration=True,
        use_biomimetic_learning=True
    )


if __name__ == "__main__":
    print("🧪 Testes do Gerenciador de Conversação")
    print("=" * 50)
    
    # Criar gerenciador simplificado (sem dependências opcionais)
    manager = ConversationManager(
        use_emotional_analysis=False,
        use_style_optimization=False,
        use_memory_integration=False,
        use_biomimetic_learning=False
    )
    
    # Testar processamento básico
    result = manager.process_user_message(
        user_id="test_user",
        message="Estou com problemas no sistema biomimético, pode ajudar?",
        context_tags=["technical", "urgent"]
    )
    
    print(f"Conversação criada: {result['conversation_id']}")
    print(f"Recomendações: {result['recommendations']}")
    print(f"Estatísticas: {manager.get_stats()}")
    
    print("\n" + "=" * 50)
    print("✅ Testes básicos completos")