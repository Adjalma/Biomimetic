#!/usr/bin/env python3
"""
Analisador de Inteligência Emocional para Conversação
=====================================================

Sistema que detecta estados emocionais em texto em português e adapta respostas.
Integração com sistema biomimético para aprendizado contínuo.

Emoções detectadas:
- Frustração: irritação, impaciência, problemas técnicos
- Urgência: pressa, necessidade imediata, deadlines
- Curiosidade: interesse, exploração, aprendizado
- Cansaço: fadiga, desânimo, sobrecarga
- Satisfação: contentamento, aprovação, sucesso
- Neutro: estado emocional normal

Autor: Jarvis (OpenClaw)
Data: 2026-04-12
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter
import json

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """Estados emocionais detectáveis"""
    FRUSTRATED = "frustrated"
    URGENT = "urgent"
    CURIOUS = "curious"
    TIRED = "tired"
    SATISFIED = "satisfied"
    NEUTRAL = "neutral"


@dataclass
class EmotionalAnalysis:
    """Resultado da análise emocional"""
    primary_emotion: EmotionalState
    secondary_emotions: List[Tuple[EmotionalState, float]]
    intensity: float  # 0.0 a 1.0
    confidence: float  # 0.0 a 1.0
    detected_triggers: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "primary_emotion": self.primary_emotion.value,
            "secondary_emotions": [(e.value, score) for e, score in self.secondary_emotions],
            "intensity": self.intensity,
            "confidence": self.confidence,
            "detected_triggers": self.detected_triggers,
            "metadata": self.metadata
        }


class EmotionalAnalyzer:
    """
    Analisador de estados emocionais baseado em léxico e padrões
    """
    
    def __init__(self):
        # Dicionários de palavras-chave para cada emoção
        self.lexicons = {
            EmotionalState.FRUSTRATED: {
                "palavras": [
                    "frustrado", "irritado", "chateado", "nervoso", "estressado",
                    "cansado disso", "já chega", "não funciona", "problema", "bug",
                    "erro", "falha", "lento", "travando", "complexo", "difícil",
                    "complicado", "confuso", "desanimado", "desistir", "desisto"
                ],
                "padrões_regex": [
                    r"não consigo",
                    r"não está funcionando",
                    r"que droga",
                    r"que merda",
                    r"que saco",
                    r"já tentei",
                    r"sem sucesso",
                    r"não aguento mais",
                    r"estou perdendo a paciência"
                ]
            },
            EmotionalState.URGENT: {
                "palavras": [
                    "urgente", "rápido", "agora", "imediatamente", "preciso já",
                    "deadline", "prazo", "pressa", "corre", "depressa",
                    "hoje", "amanhã", "asap", "urgência", "importante",
                    "crítico", "prioridade", "imediatamente"
                ],
                "padrões_regex": [
                    r"preciso (agora|já|hoje)",
                    r"tem que ser (hoje|amanhã)",
                    r"o mais rápido possível",
                    r"sem tempo",
                    r"estou atrasado",
                    r"preciso urgente",
                    r"deadline (amanhã|hoje)"
                ]
            },
            EmotionalState.CURIOUS: {
                "palavras": [
                    "curioso", "interessante", "gostaria de saber", "como funciona",
                    "explique", "detalhes", "profundidade", "aprender", "entender",
                    "pesquisar", "estudar", "explorar", "novidade", "inovador",
                    "revolucionário", "surpreenda-me", "me surpreenda", "criativo"
                ],
                "padrões_regex": [
                    r"como (funciona|é que)",
                    r"me explique",
                    r"gostaria de saber",
                    r"quero aprender",
                    r"mostre (mais|detalhes)",
                    r"surpreenda-me",
                    r"me surpreenda"
                ]
            },
            EmotionalState.TIRED: {
                "palavras": [
                    "cansado", "exausto", "fatigado", "desanimado", "sem energia",
                    "esgotado", "sobrecarregado", "muito trabalho", "sem tempo",
                    "preciso descansar", "exaustão", "burnout", "estourendo",
                    "sobrevivendo", "apenas sobrevivendo"
                ],
                "padrões_regex": [
                    r"estou cansado",
                    r"sem energia",
                    r"preciso dormir",
                    r"muito trabalho",
                    r"sobrecarregado",
                    r"estou esgotado"
                ]
            },
            EmotionalState.SATISFIED: {
                "palavras": [
                    "bom", "ótimo", "excelente", "maravilhoso", "perfeito",
                    "funcionou", "sucesso", "consegui", "finalmente", "feliz",
                    "contento", "satisfeito", "gostei", "incrível", "fantástico",
                    "espetacular", "obrigado", "valeu", "show", "top"
                ],
                "padrões_regex": [
                    r"muito bom",
                    r"funcionou perfeitamente",
                    r"finalmente consegui",
                    r"estou feliz",
                    r"obrigado pela ajuda",
                    r"valeu (mesmo|demais)"
                ]
            }
        }
        
        # Intensificadores (aumentam intensidade)
        self.intensifiers = {
            "muito": 1.5,
            "extremamente": 2.0,
            "totalmente": 1.8,
            "completamente": 1.8,
            "absolutamente": 2.0,
            "realmente": 1.3,
            "demais": 1.5,
            "tão": 1.4,
            "tanto": 1.4
        }
        
        # Atenuadores (diminuem intensidade)
        self.attenuators = {
            "pouco": 0.5,
            "levemente": 0.6,
            "um pouco": 0.6,
            "ligeiramente": 0.7,
            "mais ou menos": 0.5,
            "meio": 0.5,
            "quase": 0.8
        }
        
        # Histórico para aprendizado
        self.history = []
        self.user_profiles = {}
        
        logger.info("Analisador emocional inicializado")
    
    def analyze(self, text: str, user_id: str = "default") -> EmotionalAnalysis:
        """
        Analisa texto e detecta estado emocional
        
        Args:
            text: Texto para análise
            user_id: Identificador do usuário para personalização
            
        Returns:
            EmotionalAnalysis com resultados
        """
        text_lower = text.lower()
        
        # Contagem de detecções por emoção
        emotion_scores = {}
        detected_triggers = []
        
        # 1. Análise por léxico e padrões regex
        for emotion, data in self.lexicons.items():
            score = 0.0
            triggers = []
            
            # Palavras-chave
            for palavra in data["palavras"]:
                if palavra in text_lower:
                    score += 1.0
                    triggers.append(palavra)
            
            # Padrões regex
            for pattern in data["padrões_regex"]:
                if re.search(pattern, text_lower):
                    score += 2.0  # Padrões são mais significativos
                    triggers.append(f"padrão:{pattern}")
            
            if score > 0:
                emotion_scores[emotion] = score
                detected_triggers.extend(triggers)
        
        # 2. Análise de pontuação e estilo
        punctuation_score = self._analyze_punctuation(text)
        if punctuation_score > 0.7:
            emotion_scores[EmotionalState.URGENT] = emotion_scores.get(EmotionalState.URGENT, 0) + 1.5
            detected_triggers.append("pontuação_intensa")
        
        # 3. Análise de intensificadores/atenuadores
        intensity_multiplier = self._calculate_intensity_modifier(text_lower)
        
        # 4. Determinar emoção primária
        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            total_score = sum(emotion_scores.values())
            
            # Normalizar scores para 0-1
            normalized_scores = {}
            for emotion, score in emotion_scores.items():
                normalized_scores[emotion] = score / total_score
            
            # Calcular intensidade baseada no score e modificadores
            base_intensity = min(1.0, total_score / 10.0)  # Normalizar
            intensity = min(1.0, base_intensity * intensity_multiplier)
            
            # Emoções secundárias (top 3)
            secondary_items = sorted(
                [(e, s) for e, s in normalized_scores.items() if e != primary_emotion],
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            confidence = min(1.0, total_score / 15.0)  # Confiança baseada em evidências
        else:
            # Sem emoções detectadas → neutro
            primary_emotion = EmotionalState.NEUTRAL
            normalized_scores = {EmotionalState.NEUTRAL: 1.0}
            secondary_items = []
            intensity = 0.3
            confidence = 0.5
        
        # 5. Aplicar aprendizado do perfil do usuário
        if user_id in self.user_profiles:
            profile_adjustment = self._apply_user_profile(user_id, primary_emotion, intensity)
            if profile_adjustment:
                primary_emotion, intensity = profile_adjustment
        
        # 6. Criar resultado
        analysis = EmotionalAnalysis(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_items,
            intensity=intensity,
            confidence=confidence,
            detected_triggers=detected_triggers,
            metadata={
                "text_length": len(text),
                "has_questions": "?" in text,
                "has_exclamations": "!" in text,
                "normalized_scores": {e.value: s for e, s in normalized_scores.items()},
                "intensity_multiplier": intensity_multiplier
            }
        )
        
        # 7. Registrar no histórico
        self.history.append({
            "timestamp": self._get_timestamp(),
            "user_id": user_id,
            "text": text[:500],  # Limitar tamanho
            "analysis": analysis.to_dict()
        })
        
        # Manter histórico limitado
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        logger.debug(f"Análise emocional: {primary_emotion.value} (intensidade: {intensity:.2f})")
        return analysis
    
    def _analyze_punctuation(self, text: str) -> float:
        """Analisa pontuação para detectar urgência/frustração"""
        score = 0.0
        
        # Múltiplos pontos de exclamação/interrogação
        if "!!" in text or "??" in text or "?!" in text or "!?" in text:
            score += 0.5
        
        # Muitas exclamações
        excl_count = text.count("!")
        if excl_count > 1:
            score += min(0.5, excl_count * 0.1)
        
        # TUDO EM MAIÚSCULAS (possível frustração/urgência)
        if len(text) > 10:
            upper_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if upper_ratio > 0.7:
                score += 0.8
        
        return min(1.0, score)
    
    def _calculate_intensity_modifier(self, text_lower: str) -> float:
        """Calcula modificador de intensidade baseado em intensificadores/atenuadores"""
        words = text_lower.split()
        modifier = 1.0
        
        for i, word in enumerate(words):
            if word in self.intensifiers:
                modifier *= self.intensifiers[word]
            elif word in self.attenuators:
                modifier *= self.attenuators[word]
            # Combinações como "muito bom"
            if i < len(words) - 1:
                bigram = f"{word} {words[i+1]}"
                if bigram in self.intensifiers:
                    modifier *= self.intensifiers[bigram]
                elif bigram in self.attenuators:
                    modifier *= self.attenuators[bigram]
        
        return modifier
    
    def _apply_user_profile(self, user_id: str, emotion: EmotionalState, intensity: float) -> Optional[Tuple[EmotionalState, float]]:
        """Aplica ajustes baseados no perfil do usuário"""
        profile = self.user_profiles[user_id]
        
        # Verificar se há padrões de falsos positivos
        false_positives = profile.get("false_positives", {})
        if emotion.value in false_positives:
            # Se este usuário frequentemente tem falsos positivos para esta emoção
            false_rate = false_positives[emotion.value]
            if false_rate > 0.7:  # Mais de 70% de falsos positivos
                # Reduzir intensidade ou mudar para neutro
                return EmotionalState.NEUTRAL, intensity * 0.5
        
        # Verificar padrões de subestimação
        underestimations = profile.get("underestimations", {})
        if emotion.value in underestimations:
            under_rate = underestimations[emotion.value]
            if under_rate > 0.6:  # Frequentemente subestimamos esta emoção
                return emotion, intensity * 1.5
        
        return None
    
    def update_user_profile(self, user_id: str, feedback: Dict[str, Any]):
        """
        Atualiza perfil do usuário com feedback
        
        Args:
            user_id: Identificador do usuário
            feedback: {
                "expected_emotion": "frustrated",  # Emoção que o usuário realmente sentia
                "detected_emotion": "frustrated",  # Emoção que detectamos
                "intensity_match": 0.8,  # Quão perto a intensidade estava (0-1)
                "context": "texto original ou contexto"
            }
        """
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "total_feedbacks": 0,
                "false_positives": {},
                "underestimations": {},
                "common_emotions": Counter(),
                "accuracy_history": []
            }
        
        profile = self.user_profiles[user_id]
        profile["total_feedbacks"] += 1
        
        expected = feedback.get("expected_emotion")
        detected = feedback.get("detected_emotion")
        
        if expected and detected:
            # Acerto/erro
            if expected == detected:
                # Acerto
                if "accuracy_history" in profile:
                    profile["accuracy_history"].append(1.0)
            else:
                # Erro - falso positivo para a emoção detectada
                profile["false_positives"][detected] = profile["false_positives"].get(detected, 0) + 1
            
            # Subestimação/superestimação da intensidade
            intensity_match = feedback.get("intensity_match", 0.5)
            if intensity_match < 0.3:  # Muito diferente
                profile["underestimations"][expected] = profile["underestimations"].get(expected, 0) + 1
        
        # Limitar histórico
        if "accuracy_history" in profile and len(profile["accuracy_history"]) > 100:
            profile["accuracy_history"] = profile["accuracy_history"][-100:]
        
        logger.info(f"Perfil do usuário {user_id} atualizado com feedback")
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Obtém perfil do usuário"""
        return self.user_profiles.get(user_id, {}).copy()
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual como string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save_state(self, filepath: str = "emotional_analyzer_state.json"):
        """Salva estado do analisador"""
        state = {
            "history": self.history[-500:],  # Salvar apenas os últimos 500
            "user_profiles": self.user_profiles,
            "metadata": {
                "total_analyses": len(self.history),
                "unique_users": len(self.user_profiles)
            }
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.info(f"Estado salvo em {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    def load_state(self, filepath: str = "emotional_analyzer_state.json"):
        """Carrega estado do analisador"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.history = state.get("history", [])
            self.user_profiles = state.get("user_profiles", {})
            logger.info(f"Estado carregado de {filepath}")
        except FileNotFoundError:
            logger.info(f"Arquivo de estado {filepath} não encontrado, começando do zero")
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")


# Função de conveniência para uso rápido
def analyze_text(text: str) -> Dict[str, Any]:
    """Função simples para análise de texto"""
    analyzer = EmotionalAnalyzer()
    analysis = analyzer.analyze(text)
    return analysis.to_dict()


if __name__ == "__main__":
    # Testes básicos
    test_cases = [
        "Estou frustrado com esse código que não funciona!",
        "Preciso disso urgente para amanhã!",
        "Como funciona o sistema biomimético? Gostaria de aprender mais.",
        "Estou cansado, trabalhei o dia todo.",
        "Funcionou perfeitamente, obrigado!",
        "Tudo bem, só queria saber o status."
    ]
    
    analyzer = EmotionalAnalyzer()
    
    print("🧪 Testes do Analisador Emocional")
    print("=" * 50)
    
    for i, text in enumerate(test_cases):
        analysis = analyzer.analyze(text)
        print(f"\nTeste {i+1}:")
        print(f"Texto: {text}")
        print(f"Emoção primária: {analysis.primary_emotion.value}")
        print(f"Intensidade: {analysis.intensity:.2f}")
        print(f"Confiança: {analysis.confidence:.2f}")
        print(f"Triggers: {analysis.detected_triggers[:3]}")
    
    print("\n" + "=" * 50)
    print("✅ Testes completos")