#!/usr/bin/env python3
"""
Otimizador de Conversação Biomimético
=====================================

Sistema que adapta estilo de resposta baseado em:
1. Análise emocional do usuário
2. Contexto da conversa
3. Preferências aprendidas do usuário
4. Sistema biomimético de auto-evolução

Integra com AutoEvolvingAISystem para aprendizado contínuo e otimização.

Autor: Jarvis (OpenClaw)
Data: 2026-04-12
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

# Importar analisador emocional
try:
    from .emotional_analyzer import EmotionalAnalyzer, EmotionalState, EmotionalAnalysis
    EMOTIONAL_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ EmotionalAnalyzer não disponível: {e}")
    EMOTIONAL_ANALYZER_AVAILABLE = False
    # Placeholders para desenvolvimento
    class EmotionalState(Enum):
        NEUTRAL = "neutral"
        FRUSTRATED = "frustrated"
        URGENT = "urgent"
        CURIOUS = "curious"
        TIRED = "tired"
        SATISFIED = "satisfied"
    
    class EmotionalAnalysis:
        def __init__(self):
            self.primary_emotion = EmotionalState.NEUTRAL
            self.intensity = 0.5
            self.confidence = 0.5

# Importar sistema biomimético
try:
    from ..systems.sistemas.sistema_meta_learning_biomimetico import AutoEvolvingAISystem
    BIOMIMETIC_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AutoEvolvingAISystem não disponível: {e}")
    BIOMIMETIC_SYSTEM_AVAILABLE = False

logger = logging.getLogger(__name__)


class ResponseParameter(Enum):
    """Parâmetros de resposta que podem ser otimizados"""
    VERBOSITY = "verbosity"           # 0.0-1.0: conciso ↔ detalhado
    FORMALITY = "formality"           # 0.0-1.0: casual ↔ formal
    WARMTH = "warmth"                 # 0.0-1.0: frio/neutro ↔ caloroso/empático
    SOLUTION_BIAS = "solution_bias"   # 0.0-1.0: explicativo ↔ focado em solução
    TECHNICAL_DEPTH = "technical_depth"  # 0.0-1.0: leigo ↔ técnico
    SURPRISE_FACTOR = "surprise_factor"  # 0.0-1.0: convencional ↔ surpreendente
    STRUCTURE = "structure"           # 0.0-1.0: narrativa ↔ estruturado (listas, bullets)
    HUMOR_LEVEL = "humor_level"       # 0.0-1.0: sério ↔ humorístico


@dataclass
class ResponseStyle:
    """Estilo de resposta com parâmetros otimizados"""
    parameters: Dict[ResponseParameter, float]
    emotional_context: Optional[EmotionalAnalysis] = None
    user_id: str = "default"
    context_tags: List[str] = field(default_factory=list)
    reasoning: str = ""
    
    def get_parameter(self, param: ResponseParameter, default: float = 0.5) -> float:
        """Obtém valor do parâmetro com fallback"""
        return self.parameters.get(param, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "parameters": {p.value: v for p, v in self.parameters.items()},
            "emotional_context": self.emotional_context.to_dict() if self.emotional_context else None,
            "user_id": self.user_id,
            "context_tags": self.context_tags,
            "reasoning": self.reasoning
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseStyle':
        """Cria a partir de dicionário"""
        # Converter strings para ResponseParameter
        parameters = {}
        for param_str, value in data.get("parameters", {}).items():
            try:
                param = ResponseParameter(param_str)
                parameters[param] = float(value)
            except (ValueError, KeyError):
                continue
        
        # Criar instância
        return cls(
            parameters=parameters,
            user_id=data.get("user_id", "default"),
            context_tags=data.get("context_tags", []),
            reasoning=data.get("reasoning", "")
        )


class ConversationOptimizer:
    """
    Otimizador de conversação que adapta estilo baseado em múltiplos fatores
    """
    
    def __init__(self, use_biomimetic: bool = True):
        # Componentes
        self.emotional_analyzer = None
        self.biomimetic_system = None
        
        # Inicializar componentes
        if EMOTIONAL_ANALYZER_AVAILABLE:
            self.emotional_analyzer = EmotionalAnalyzer()
            logger.info("✅ Analisador emocional inicializado")
        else:
            logger.warning("⚠️ Analisador emocional não disponível")
        
        if use_biomimetic and BIOMIMETIC_SYSTEM_AVAILABLE:
            try:
                self.biomimetic_system = AutoEvolvingAISystem(use_local_brain=False)
                logger.info("✅ Sistema biomimético inicializado para otimização de conversação")
            except Exception as e:
                logger.error(f"Erro ao inicializar sistema biomimético: {e}")
                self.biomimetic_system = None
        
        # Histórico de otimizações para aprendizado
        self.optimization_history = []
        
        # Perfis de usuário para estilo
        self.user_style_profiles = {}
        
        # Regras baseadas em emoção (baseline)
        self.emotion_based_rules = self._create_emotion_rules()
        
        # Contadores para aprendizado
        self.feedback_history = []
        
        logger.info("Otimizador de conversação inicializado")
    
    def _create_emotion_rules(self) -> Dict[EmotionalState, Dict[ResponseParameter, float]]:
        """Cria regras baseadas em emoção para baseline"""
        return {
            EmotionalState.FRUSTRATED: {
                ResponseParameter.VERBOSITY: 0.3,      # Conciso
                ResponseParameter.SOLUTION_BIAS: 0.9,  # Foco em solução
                ResponseParameter.WARMTH: 0.6,         # Moderadamente caloroso
                ResponseParameter.FORMALITY: 0.4,      # Casual
                ResponseParameter.TECHNICAL_DEPTH: 0.3, # Evitar detalhes técnicos
                ResponseParameter.STRUCTURE: 0.8,      # Estruturado (passo a passo)
            },
            EmotionalState.URGENT: {
                ResponseParameter.VERBOSITY: 0.2,      # Muito conciso
                ResponseParameter.SOLUTION_BIAS: 0.95, # Máximo foco em solução
                ResponseParameter.FORMALITY: 0.3,      # Casual rápido
                ResponseParameter.STRUCTURE: 0.9,      # Altamente estruturado
                ResponseParameter.TECHNICAL_DEPTH: 0.2, # Mínimo técnico
            },
            EmotionalState.CURIOUS: {
                ResponseParameter.VERBOSITY: 0.8,      # Detalhado
                ResponseParameter.TECHNICAL_DEPTH: 0.7, # Técnico moderado
                ResponseParameter.SOLUTION_BIAS: 0.4,  # Balanceado explicação/solução
                ResponseParameter.SURPRISE_FACTOR: 0.6, # Incluir insights surpreendentes
                ResponseParameter.STRUCTURE: 0.6,      # Semi-estruturado
            },
            EmotionalState.TIRED: {
                ResponseParameter.VERBOSITY: 0.3,      # Conciso
                ResponseParameter.WARMTH: 0.8,         # Caloroso/empático
                ResponseParameter.FORMALITY: 0.2,      # Muito casual
                ResponseParameter.STRUCTURE: 0.9,      # Estruturado simples
                ResponseParameter.TECHNICAL_DEPTH: 0.1, # Mínimo técnico
            },
            EmotionalState.SATISFIED: {
                ResponseParameter.WARMTH: 0.9,         # Muito caloroso
                ResponseParameter.HUMOR_LEVEL: 0.5,    # Leve humor
                ResponseParameter.VERBOSITY: 0.5,      # Balanceado
                ResponseParameter.FORMALITY: 0.3,      # Casual
            },
            EmotionalState.NEUTRAL: {
                ResponseParameter.VERBOSITY: 0.5,      # Balanceado
                ResponseParameter.FORMALITY: 0.5,      # Neutro
                ResponseParameter.WARMTH: 0.5,         # Neutro
                ResponseParameter.SOLUTION_BIAS: 0.5,  # Balanceado
                ResponseParameter.TECHNICAL_DEPTH: 0.5, # Moderado
            }
        }
    
    def optimize_response_style(
        self,
        user_message: str,
        user_id: str = "default",
        context_tags: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> ResponseStyle:
        """
        Otimiza estilo de resposta baseado em múltiplos fatores
        
        Args:
            user_message: Mensagem do usuário
            user_id: Identificador do usuário
            context_tags: Tags de contexto (ex: ["technical", "urgent", "debug"])
            conversation_history: Histórico da conversa
            
        Returns:
            ResponseStyle otimizado
        """
        # 1. Análise emocional
        emotional_analysis = None
        if self.emotional_analyzer:
            emotional_analysis = self.emotional_analyzer.analyze(user_message, user_id)
            primary_emotion = emotional_analysis.primary_emotion
            intensity = emotional_analysis.intensity
        else:
            # Fallback
            primary_emotion = EmotionalState.NEUTRAL
            intensity = 0.5
        
        # 2. Obter baseline baseada em emoção
        baseline_style = self._get_emotion_baseline(primary_emotion, intensity)
        
        # 3. Ajustar baseado no perfil do usuário
        user_adjusted_style = self._apply_user_profile(
            baseline_style, user_id, primary_emotion, context_tags or []
        )
        
        # 4. Ajustar baseado no contexto da conversa
        context_adjusted_style = self._apply_conversation_context(
            user_adjusted_style, conversation_history, context_tags or []
        )
        
        # 5. Usar sistema biomimético para otimização (se disponível)
        final_style = self._apply_biomimetic_optimization(
            context_adjusted_style, 
            user_message, 
            user_id,
            emotional_analysis
        )
        
        # 6. Adicionar contexto emocional e reasoning
        final_style.emotional_context = emotional_analysis
        final_style.user_id = user_id
        final_style.context_tags = context_tags or []
        
        # Gerar reasoning explicativo
        reasoning_parts = [
            f"Emoção detectada: {primary_emotion.value} (intensidade: {intensity:.2f})",
            f"Perfil do usuário aplicado: {len(self.user_style_profiles.get(user_id, {}))} ajustes"
        ]
        
        if self.biomimetic_system:
            reasoning_parts.append("Otimização biomimética aplicada")
        
        final_style.reasoning = "; ".join(reasoning_parts)
        
        # 7. Registrar no histórico
        self.optimization_history.append({
            "timestamp": self._get_timestamp(),
            "user_id": user_id,
            "message": user_message[:200],
            "style": final_style.to_dict(),
            "emotional_analysis": emotional_analysis.to_dict() if emotional_analysis else None
        })
        
        # Manter histórico limitado
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-1000:]
        
        logger.debug(f"Estilo otimizado para {user_id}: {primary_emotion.value}")
        return final_style
    
    def _get_emotion_baseline(self, emotion: EmotionalState, intensity: float) -> Dict[ResponseParameter, float]:
        """Obtém baseline de estilo baseado em emoção, ajustado por intensidade"""
        baseline = {}
        
        # Obter regras para a emoção (com fallback para neutro)
        emotion_rules = self.emotion_based_rules.get(
            emotion, 
            self.emotion_based_rules[EmotionalState.NEUTRAL]
        )
        
        # Aplicar intensidade como multiplicador para alguns parâmetros
        intensity_multiplier = 0.5 + (intensity * 0.5)  # Mapear 0.0-1.0 para 0.5-1.0
        
        for param, base_value in emotion_rules.items():
            # Alguns parâmetros são mais afetados pela intensidade
            if param in [ResponseParameter.VERBOSITY, ResponseParameter.WARMTH, 
                        ResponseParameter.SOLUTION_BIAS, ResponseParameter.SURPRISE_FACTOR]:
                adjusted_value = base_value * intensity_multiplier
            else:
                adjusted_value = base_value
            
            # Garantir dentro dos limites 0.0-1.0
            baseline[param] = max(0.0, min(1.0, adjusted_value))
        
        return baseline
    
    def _apply_user_profile(
        self, 
        baseline_style: Dict[ResponseParameter, float], 
        user_id: str,
        current_emotion: EmotionalState,
        context_tags: List[str]
    ) -> Dict[ResponseParameter, float]:
        """Ajusta estilo baseado no perfil do usuário"""
        adjusted_style = baseline_style.copy()
        
        if user_id not in self.user_style_profiles:
            return adjusted_style
        
        profile = self.user_style_profiles[user_id]
        
        # Aplicar ajustes gerais do usuário
        if "preferred_parameters" in profile:
            for param_str, preferred_value in profile["preferred_parameters"].items():
                try:
                    param = ResponseParameter(param_str)
                    # Misturar baseline com preferência (70% preferência, 30% baseline)
                    current = adjusted_style.get(param, 0.5)
                    adjusted = (preferred_value * 0.7) + (current * 0.3)
                    adjusted_style[param] = max(0.0, min(1.0, adjusted))
                except (ValueError, KeyError):
                    continue
        
        # Aplicar ajustes específicos por emoção
        emotion_key = current_emotion.value
        if "emotion_specific_adjustments" in profile and emotion_key in profile["emotion_specific_adjustments"]:
            adjustments = profile["emotion_specific_adjustments"][emotion_key]
            for param_str, adjustment in adjustments.items():
                try:
                    param = ResponseParameter(param_str)
                    current = adjusted_style.get(param, 0.5)
                    adjusted = current + adjustment
                    adjusted_style[param] = max(0.0, min(1.0, adjusted))
                except (ValueError, KeyError):
                    continue
        
        # Aplicar ajustes por contexto
        for tag in context_tags:
            tag_key = f"context_{tag}"
            if "context_adjustments" in profile and tag_key in profile["context_adjustments"]:
                adjustments = profile["context_adjustments"][tag_key]
                for param_str, adjustment in adjustments.items():
                    try:
                        param = ResponseParameter(param_str)
                        current = adjusted_style.get(param, 0.5)
                        adjusted = current + adjustment
                        adjusted_style[param] = max(0.0, min(1.0, adjusted))
                    except (ValueError, KeyError):
                        continue
        
        return adjusted_style
    
    def _apply_conversation_context(
        self,
        style: Dict[ResponseParameter, float],
        conversation_history: Optional[List[Dict[str, Any]]],
        context_tags: List[str]
    ) -> Dict[ResponseParameter, float]:
        """Ajusta estilo baseado no contexto da conversa"""
        adjusted_style = style.copy()
        
        if not conversation_history or len(conversation_history) == 0:
            return adjusted_style
        
        # Analisar histórico recente (últimas 5 mensagens)
        recent_history = conversation_history[-5:]
        
        # Detectar padrões
        has_technical_questions = any(
            msg.get("content", "").lower() in ["como funciona", "explique", "detalhes"]
            for msg in recent_history
        )
        
        has_repeated_questions = len(recent_history) >= 2 and any(
            recent_history[i].get("content") == recent_history[i+1].get("content")
            for i in range(len(recent_history)-1)
        )
        
        # Ajustes baseados em padrões
        if has_technical_questions:
            adjusted_style[ResponseParameter.TECHNICAL_DEPTH] = min(
                1.0, adjusted_style.get(ResponseParameter.TECHNICAL_DEPTH, 0.5) + 0.2
            )
            adjusted_style[ResponseParameter.VERBOSITY] = min(
                1.0, adjusted_style.get(ResponseParameter.VERBOSITY, 0.5) + 0.1
            )
        
        if has_repeated_questions:
            # Usuário não entendeu → ser mais claro, estruturado
            adjusted_style[ResponseParameter.STRUCTURE] = min(
                1.0, adjusted_style.get(ResponseParameter.STRUCTURE, 0.5) + 0.3
            )
            adjusted_style[ResponseParameter.VERBOSITY] = min(
                1.0, adjusted_style.get(ResponseParameter.VERBOSITY, 0.5) + 0.2
            )
        
        return adjusted_style
    
    def _apply_biomimetic_optimization(
        self,
        style: Dict[ResponseParameter, float],
        user_message: str,
        user_id: str,
        emotional_analysis: Optional[EmotionalAnalysis]
    ) -> Dict[ResponseParameter, float]:
        """Usa sistema biomimético para otimização avançada"""
        if not self.biomimetic_system:
            return style
        
        try:
            # Preparar dados para o sistema biomimético
            task_data = {
                "task_type": "conversation_optimization",
                "user_message": user_message[:500],  # Limitar tamanho
                "current_style": {p.value: v for p, v in style.items()},
                "user_id": user_id,
                "emotional_state": emotional_analysis.primary_emotion.value if emotional_analysis else "neutral",
                "emotional_intensity": emotional_analysis.intensity if emotional_analysis else 0.5
            }
            
            # Usar sistema biomimético para recomendar otimizações
            recommendation = self.biomimetic_system.recommend_provider(task_data)
            
            # Extrair insights da recommendation (se disponível)
            if recommendation and "reasoning" in recommendation:
                reasoning = recommendation["reasoning"]
                
                # Extrair sugestões do reasoning (simplificado)
                # Em implementação real, isso seria mais sofisticado
                if "mais conciso" in reasoning.lower():
                    style[ResponseParameter.VERBOSITY] = max(0.1, style.get(ResponseParameter.VERBOSITY, 0.5) - 0.2)
                
                if "mais técnico" in reasoning.lower():
                    style[ResponseParameter.TECHNICAL_DEPTH] = min(1.0, style.get(ResponseParameter.TECHNICAL_DEPTH, 0.5) + 0.2)
                
                if "mais caloroso" in reasoning.lower():
                    style[ResponseParameter.WARMTH] = min(1.0, style.get(ResponseParameter.WARMTH, 0.5) + 0.3)
            
            logger.debug("Otimização biomimética aplicada")
            
        except Exception as e:
            logger.error(f"Erro na otimização biomimética: {e}")
        
        return style
    
    def update_user_profile_from_feedback(
        self,
        user_id: str,
        feedback: Dict[str, Any]
    ):
        """
        Atualiza perfil do usuário com feedback sobre qualidade da resposta
        
        Args:
            user_id: Identificador do usuário
            feedback: {
                "message_id": "id da mensagem",
                "user_satisfaction": 0.0-1.0,  # Satisfação do usuário
                "engagement_metrics": {},       # Métricas de engajamento
                "explicit_feedback": "texto do usuário",
                "response_style_used": ResponseStyle.to_dict(),
                "suggested_improvements": ["mais conciso", "mais técnico", etc.]
            }
        """
        if user_id not in self.user_style_profiles:
            self.user_style_profiles[user_id] = {
                "preferred_parameters": {},
                "emotion_specific_adjustments": {},
                "context_adjustments": {},
                "feedback_history": [],
                "average_satisfaction": 0.5,
                "total_feedbacks": 0
            }
        
        profile = self.user_style_profiles[user_id]
        profile["total_feedbacks"] += 1
        
        # Adicionar ao histórico
        feedback_entry = {
            "timestamp": self._get_timestamp(),
            **feedback
        }
        profile["feedback_history"].append(feedback_entry)
        
        # Limitar histórico
        if len(profile["feedback_history"]) > 100:
            profile["feedback_history"] = profile["feedback_history"][-100:]
        
        # Atualizar satisfação média
        satisfaction = feedback.get("user_satisfaction", 0.5)
        current_avg = profile.get("average_satisfaction", 0.5)
        total = profile["total_feedbacks"]
        
        # Média móvel
        profile["average_satisfaction"] = ((current_avg * (total - 1)) + satisfaction) / total
        
        # Processar sugestões de melhoria
        suggested_improvements = feedback.get("suggested_improvements", [])
        if suggested_improvements:
            self._process_improvement_suggestions(user_id, suggested_improvements, feedback)
        
        logger.info(f"Perfil do usuário {user_id} atualizado com feedback")
    
    def _process_improvement_suggestions(
        self,
        user_id: str,
        suggestions: List[str],
        feedback: Dict[str, Any]
    ):
        """Processa sugestões de melhoria para ajustar perfil"""
        profile = self.user_style_profiles[user_id]
        style_used = feedback.get("response_style_used")
        
        if not style_used:
            return
        
        # Mapear sugestões para parâmetros
        suggestion_to_param = {
            "mais conciso": (ResponseParameter.VERBOSITY, -0.2),
            "mais detalhado": (ResponseParameter.VERBOSITY, 0.2),
            "mais técnico": (ResponseParameter.TECHNICAL_DEPTH, 0.2),
            "menos técnico": (ResponseParameter.TECHNICAL_DEPTH, -0.2),
            "mais formal": (ResponseParameter.FORMALITY, 0.2),
            "mais casual": (ResponseParameter.FORMALITY, -0.2),
            "mais direto": (ResponseParameter.SOLUTION_BIAS, 0.2),
            "mais caloroso": (ResponseParameter.WARMTH, 0.3),
            "mais humor": (ResponseParameter.HUMOR_LEVEL, 0.3),
        }
        
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            
            for pattern, (param, adjustment) in suggestion_to_param.items():
                if pattern in suggestion_lower:
                    # Atualizar preferência geral
                    current_pref = profile["preferred_parameters"].get(param.value, 0.5)
                    new_pref = max(0.0, min(1.0, current_pref + adjustment))
                    profile["preferred_parameters"][param.value] = new_pref
                    
                    logger.debug(f"Ajustado {param.value} para {user_id}: {current_pref:.2f} → {new_pref:.2f}")
                    break
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Obtém perfil do usuário"""
        return self.user_style_profiles.get(user_id, {}).copy()
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        return datetime.now().isoformat()
    
    def save_state(self, filepath: str = "conversation_optimizer_state.json"):
        """Salva estado do otimizador"""
        state = {
            "user_style_profiles": self.user_style_profiles,
            "optimization_history": self.optimization_history[-500:],  # Últimas 500
            "metadata": {
                "total_users": len(self.user_style_profiles),
                "total_optimizations": len(self.optimization_history)
            }
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info(f"Estado salvo em {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    def load_state(self, filepath: str = "conversation_optimizer_state.json"):
        """Carrega estado do otimizador"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.user_style_profiles = state.get("user_style_profiles", {})
            self.optimization_history = state.get("optimization_history", [])
            logger.info(f"Estado carregado de {filepath}")
        except FileNotFoundError:
            logger.info(f"Arquivo de estado {filepath} não encontrado, começando do zero")
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")


# Função de conveniência para uso rápido
def optimize_response(
    user_message: str,
    user_id: str = "default",
    context_tags: Optional[List[str]] = None
) -> ResponseStyle:
    """Função simples para otimização de resposta"""
    optimizer = ConversationOptimizer(use_biomimetic=True)
    return optimizer.optimize_response_style(user_message, user_id, context_tags)


if __name__ == "__main__":
    # Testes básicos
    print("🧪 Testes do Otimizador de Conversação")
    print("=" * 50)
    
    optimizer = ConversationOptimizer(use_biomimetic=False)
    
    test_cases = [
        ("Estou frustrado com esse erro no código!", ["technical", "debug"], "user1"),
        ("Como funciona o sistema biomimético? Explique detalhes.", ["learning", "technical"], "user1"),
        ("Preciso resolver isso urgente para amanhã!", ["urgent", "business"], "user2"),
        ("Estou cansado, só quero uma solução simples.", ["tired", "simple"], "user3"),
    ]
    
    for i, (message, tags, user_id) in enumerate(test_cases):
        style = optimizer.optimize_response_style(
            user_message=message,
            user_id=user_id,
            context_tags=tags
        )
        
        print(f"\nTeste {i+1} - Usuário: {user_id}")
        print(f"Mensagem: {message}")
        print(f"Tags: {tags}")
        print(f"Parâmetros otimizados:")
        
        for param, value in style.parameters.items():
            print(f"  {param.value}: {value:.2f}")
        
        print(f"Reasoning: {style.reasoning}")
    
    print("\n" + "=" * 50)
    print("✅ Testes completos")