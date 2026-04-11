"""
Gestão de Relacionamentos
Fase 9: Contexto Empresarial - Gestão de Relacionamentos

Autor: Jarvis (OpenClaw)
Data: 2026-04-11

Objetivo:
- Rastrear histórico de interações entre indivíduos
- Calcular rapport (nível de conexão/confiança)
- Identificar padrões de comunicação
- Sugerir abordagens personalizadas baseadas no relacionamento
- Integrar com hierarquia organizacional e etiqueta

Funcionalidades:
- Registrar interações (reuniões, emails, mensagens)
- Calcular métricas de relacionamento (frequência, sentimento, reciprocidade)
- Prever estilos de comunicação preferidos
- Sugerir tópicos de conversa baseados em histórico
- Detectar mudanças no relacionamento
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """Tipos de interação"""
    MEETING = "meeting"
    EMAIL = "email"
    CHAT = "chat"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"
    COLLABORATION = "collaboration"
    FEEDBACK = "feedback"
    SOCIAL = "social"

class Sentiment(Enum):
    """Sentimento da interação"""
    VERY_POSITIVE = 2
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1
    VERY_NEGATIVE = -2

@dataclass
class Interaction:
    """Registro de uma interação"""
    id: str
    participant_ids: List[str]  # IDs dos participantes
    interaction_type: InteractionType
    timestamp: datetime
    duration_minutes: float
    topic: str
    sentiment: Sentiment = Sentiment.NEUTRAL
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'participant_ids': self.participant_ids,
            'interaction_type': self.interaction_type.value,
            'timestamp': self.timestamp.isoformat(),
            'duration_minutes': self.duration_minutes,
            'topic': self.topic,
            'sentiment': self.sentiment.value,
            'notes': self.notes,
            'metadata': self.metadata
        }

@dataclass
class RelationshipMetrics:
    """Métricas de relacionamento entre dois indivíduos"""
    person_a_id: str
    person_b_id: str
    
    # Frequência
    total_interactions: int = 0
    interactions_last_30_days: int = 0
    average_days_between: float = 0.0
    
    # Sentimento
    average_sentiment: float = 0.0
    sentiment_trend: float = 0.0  # -1 a 1 (negativo para positivo)
    
    # Reciprocidade
    reciprocity_score: float = 0.0  # 0-1 (1 = perfeitamente recíproco)
    
    # Tópicos
    common_topics: List[str] = field(default_factory=list)
    topic_overlap_score: float = 0.0  # 0-1
    
    # Rapport
    rapport_score: float = 0.0  # 0-100
    trust_level: float = 0.0  # 0-1
    
    # Comunicação
    preferred_communication_type: Optional[InteractionType] = None
    response_time_hours_avg: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'person_a_id': self.person_a_id,
            'person_b_id': self.person_b_id,
            'total_interactions': self.total_interactions,
            'interactions_last_30_days': self.interactions_last_30_days,
            'average_days_between': self.average_days_between,
            'average_sentiment': self.average_sentiment,
            'sentiment_trend': self.sentiment_trend,
            'reciprocity_score': self.reciprocity_score,
            'common_topics': self.common_topics,
            'topic_overlap_score': self.topic_overlap_score,
            'rapport_score': self.rapport_score,
            'trust_level': self.trust_level,
            'preferred_communication_type': self.preferred_communication_type.value if self.preferred_communication_type else None,
            'response_time_hours_avg': self.response_time_hours_avg
        }

class RelationshipManager:
    """Gerenciador de relacionamentos"""
    
    def __init__(self, data_source: Optional[str] = None):
        """
        Inicializa gerenciador de relacionamentos.
        
        Args:
            data_source: Caminho para arquivo de dados (JSON) ou None para vazio
        """
        self.interactions: Dict[str, Interaction] = {}
        self.relationships: Dict[Tuple[str, str], RelationshipMetrics] = {}
        self.person_interactions: Dict[str, List[str]] = {}  # person_id -> list of interaction_ids
        
        if data_source:
            self.load_from_source(data_source)
        
        logger.info(f"✅ RelationshipManager inicializado com {len(self.interactions)} interações")
    
    def load_from_source(self, data_source: str):
        """
        Carrega dados de relacionamento de uma fonte.
        
        Args:
            data_source: Caminho para arquivo JSON
        """
        try:
            path = Path(data_source)
            if not path.exists():
                logger.warning(f"⚠️  Arquivo de dados não encontrado: {data_source}")
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Carregar interações
            if 'interactions' in data:
                for int_data in data['interactions']:
                    try:
                        interaction = Interaction(
                            id=int_data['id'],
                            participant_ids=int_data['participant_ids'],
                            interaction_type=InteractionType(int_data['interaction_type']),
                            timestamp=datetime.fromisoformat(int_data['timestamp'].replace('Z', '+00:00')),
                            duration_minutes=int_data['duration_minutes'],
                            topic=int_data['topic'],
                            sentiment=Sentiment(int_data['sentiment']),
                            notes=int_data.get('notes'),
                            metadata=int_data.get('metadata', {})
                        )
                        self.interactions[interaction.id] = interaction
                        
                        # Atualizar índices
                        for person_id in interaction.participant_ids:
                            if person_id not in self.person_interactions:
                                self.person_interactions[person_id] = []
                            self.person_interactions[person_id].append(interaction.id)
                        
                    except Exception as e:
                        logger.warning(f"⚠️  Erro ao carregar interação {int_data.get('id')}: {e}")
            
            # Carregar métricas de relacionamento (se existirem)
            if 'relationships' in data:
                for rel_data in data['relationships']:
                    try:
                        key = (rel_data['person_a_id'], rel_data['person_b_id'])
                        metrics = RelationshipMetrics(
                            person_a_id=rel_data['person_a_id'],
                            person_b_id=rel_data['person_b_id'],
                            total_interactions=rel_data['total_interactions'],
                            interactions_last_30_days=rel_data['interactions_last_30_days'],
                            average_days_between=rel_data['average_days_between'],
                            average_sentiment=rel_data['average_sentiment'],
                            sentiment_trend=rel_data['sentiment_trend'],
                            reciprocity_score=rel_data['reciprocity_score'],
                            common_topics=rel_data['common_topics'],
                            topic_overlap_score=rel_data['topic_overlap_score'],
                            rapport_score=rel_data['rapport_score'],
                            trust_level=rel_data['trust_level'],
                            preferred_communication_type=InteractionType(rel_data['preferred_communication_type']) if rel_data['preferred_communication_type'] else None,
                            response_time_hours_avg=rel_data.get('response_time_hours_avg')
                        )
                        self.relationships[key] = metrics
                    except Exception as e:
                        logger.warning(f"⚠️  Erro ao carregar relacionamento: {e}")
            
            # Se não houver métricas pré-calculadas, calcular agora
            if not self.relationships and self.interactions:
                self._calculate_all_relationships()
            
            logger.info(f"✅ Dados carregados: {len(self.interactions)} interações, {len(self.relationships)} relacionamentos")
        
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {e}")
    
    def add_interaction(self, interaction: Interaction):
        """Adiciona uma nova interação"""
        self.interactions[interaction.id] = interaction
        
        # Atualizar índices
        for person_id in interaction.participant_ids:
            if person_id not in self.person_interactions:
                self.person_interactions[person_id] = []
            self.person_interactions[person_id].append(interaction.id)
        
        # Atualizar métricas de relacionamento para todos os pares
        self._update_relationships_for_interaction(interaction)
        
        logger.info(f"✅ Interação registrada: {interaction.interaction_type.value} entre {len(interaction.participant_ids)} pessoas")
    
    def _update_relationships_for_interaction(self, interaction: Interaction):
        """Atualiza métricas de relacionamento para uma interação"""
        participants = interaction.participant_ids
        
        # Para cada par de participantes
        for i in range(len(participants)):
            for j in range(i + 1, len(participants)):
                person_a = participants[i]
                person_b = participants[j]
                
                # Garantir ordem consistente
                if person_a > person_b:
                    person_a, person_b = person_b, person_a
                
                key = (person_a, person_b)
                
                if key not in self.relationships:
                    self.relationships[key] = RelationshipMetrics(person_a, person_b)
                
                # Recalcular métricas para este par
                self._calculate_relationship_metrics(person_a, person_b)
    
    def _calculate_all_relationships(self):
        """Calcula métricas para todos os relacionamentos"""
        # Coletar todos os pares únicos que têm interações
        pairs = set()
        
        for interaction in self.interactions.values():
            participants = interaction.participant_ids
            for i in range(len(participants)):
                for j in range(i + 1, len(participants)):
                    person_a = participants[i]
                    person_b = participants[j]
                    
                    # Ordem consistente
                    if person_a > person_b:
                        person_a, person_b = person_b, person_a
                    
                    pairs.add((person_a, person_b))
        
        # Calcular métricas para cada par
        for person_a, person_b in pairs:
            self._calculate_relationship_metrics(person_a, person_b)
    
    def _calculate_relationship_metrics(self, person_a: str, person_b: str):
        """Calcula métricas de relacionamento para um par específico"""
        # Obter interações envolvendo este par
        pair_interactions = []
        
        for interaction in self.interactions.values():
            if person_a in interaction.participant_ids and person_b in interaction.participant_ids:
                pair_interactions.append(interaction)
        
        if not pair_interactions:
            return
        
        # Ordenar por timestamp
        pair_interactions.sort(key=lambda x: x.timestamp)
        
        # Criar ou obter métricas
        key = (person_a, person_b) if person_a < person_b else (person_b, person_a)
        if key not in self.relationships:
            self.relationships[key] = RelationshipMetrics(person_a, person_b)
        
        metrics = self.relationships[key]
        
        # Atualizar métricas básicas
        metrics.total_interactions = len(pair_interactions)
        
        # Interações nos últimos 30 dias
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_interactions = [i for i in pair_interactions if i.timestamp >= thirty_days_ago]
        metrics.interactions_last_30_days = len(recent_interactions)
        
        # Tempo médio entre interações
        if len(pair_interactions) > 1:
            time_diffs = []
            for i in range(1, len(pair_interactions)):
                diff = (pair_interactions[i].timestamp - pair_interactions[i-1].timestamp).total_seconds() / 86400  # dias
                time_diffs.append(diff)
            
            if time_diffs:
                metrics.average_days_between = statistics.mean(time_diffs)
        
        # Sentimento médio
        sentiments = [i.sentiment.value for i in pair_interactions]
        metrics.average_sentiment = statistics.mean(sentiments) if sentiments else 0.0
        
        # Tendência de sentimento (últimas 5 interações vs anteriores)
        if len(pair_interactions) >= 5:
            recent = pair_interactions[-5:]
            older = pair_interactions[:-5] if len(pair_interactions) > 5 else []
            
            recent_sentiment = statistics.mean([i.sentiment.value for i in recent]) if recent else 0.0
            older_sentiment = statistics.mean([i.sentiment.value for i in older]) if older else 0.0
            
            if older_sentiment != 0:
                metrics.sentiment_trend = (recent_sentiment - older_sentiment) / abs(older_sentiment)
            else:
                metrics.sentiment_trend = 0.0
        else:
            metrics.sentiment_trend = 0.0
        
        # Tópicos comuns
        all_topics = {}
        for interaction in pair_interactions:
            topic = interaction.topic.lower()
            all_topics[topic] = all_topics.get(topic, 0) + 1
        
        # Top 5 tópicos mais frequentes
        common_topics = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)[:5]
        metrics.common_topics = [topic for topic, count in common_topics]
        
        # Score de sobreposição de tópicos
        total_interactions_both = metrics.total_interactions
        if total_interactions_both > 0:
            metrics.topic_overlap_score = len(metrics.common_topics) / min(10, total_interactions_both)
        
        # Tipo de comunicação preferido
        type_counts = {}
        for interaction in pair_interactions:
            itype = interaction.interaction_type
            type_counts[itype] = type_counts.get(itype, 0) + 1
        
        if type_counts:
            metrics.preferred_communication_type = max(type_counts.items(), key=lambda x: x[1])[0]
        
        # Calcular rapport score (0-100)
        rapport = 0.0
        
        # Baseado na frequência (max 40 pontos)
        if metrics.average_days_between > 0:
            freq_score = min(40, 40 * (30 / metrics.average_days_between))
            rapport += freq_score
        
        # Baseado no sentimento (max 30 pontos)
        sentiment_score = min(30, 15 * (metrics.average_sentiment + 2))  # -2 a 2 -> 0 a 30
        rapport += sentiment_score
        
        # Baseado na consistência (max 20 pontos)
        if metrics.total_interactions >= 5:
            consistency_score = min(20, metrics.total_interactions)
            rapport += consistency_score
        
        # Baseado na reciprocidade (max 10 pontos)
        # (simplificado - em produção calcularia baseado em iniciativas)
        rapport += min(10, metrics.total_interactions * 0.5)
        
        metrics.rapport_score = min(100, rapport)
        
        # Nível de confiança (0-1 baseado no rapport)
        metrics.trust_level = metrics.rapport_score / 100
    
    def get_relationship(self, person_a_id: str, person_b_id: str) -> Optional[RelationshipMetrics]:
        """
        Obtém métricas de relacionamento entre duas pessoas.
        
        Args:
            person_a_id: ID da primeira pessoa
            person_b_id: ID da segunda pessoa
            
        Returns:
            RelationshipMetrics ou None se não houver interações
        """
        key = (person_a_id, person_b_id) if person_a_id < person_b_id else (person_b_id, person_a_id)
        return self.relationships.get(key)
    
    def get_person_interactions(self, person_id: str, limit: int = 50) -> List[Interaction]:
        """
        Obtém interações de uma pessoa.
        
        Args:
            person_id: ID da pessoa
            limit: Número máximo de interações a retornar
            
        Returns:
            Lista de interações ordenadas por data (mais recente primeiro)
        """
        if person_id not in self.person_interactions:
            return []
        
        interaction_ids = self.person_interactions[person_id]
        interactions = [self.interactions[iid] for iid in interaction_ids if iid in self.interactions]
        
        # Ordenar por timestamp (mais recente primeiro)
        interactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return interactions[:limit]
    
    def get_communication_recommendation(self, from_person_id: str, to_person_id: str, context: str = "general") -> Dict[str, Any]:
        """
        Obtém recomendações de comunicação para uma interação.
        
        Args:
            from_person_id: ID do remetente
            to_person_id: ID do destinatário
            context: Contexto da comunicação ('general', 'urgent', 'sensitive', 'collaborative')
            
        Returns:
            Recomendações de comunicação
        """
        metrics = self.get_relationship(from_person_id, to_person_id)
        
        recommendations = {
            'preferred_channel': None,
            'formality_level': 'medium',
            'suggested_topics': [],
            'avoid_topics': [],
            'timing_recommendation': 'anytime',
            'warm_up_needed': False,
            'estimated_response_time_hours': 24,
            'confidence': 0.5
        }
        
        if metrics:
            # Canal preferido
            if metrics.preferred_communication_type:
                recommendations['preferred_channel'] = metrics.preferred_communication_type.value
            
            # Nível de formalidade baseado no rapport
            if metrics.rapport_score > 70:
                recommendations['formality_level'] = 'low'
                recommendations['warm_up_needed'] = False
            elif metrics.rapport_score > 30:
                recommendations['formality_level'] = 'medium'
                recommendations['warm_up_needed'] = metrics.interactions_last_30_days == 0
            else:
                recommendations['formality_level'] = 'high'
                recommendations['warm_up_needed'] = True
            
            # Tópicos sugeridos (baseado em histórico)
            if metrics.common_topics:
                recommendations['suggested_topics'] = metrics.common_topics[:3]
            
            # Timing baseado em padrões históricos
            if metrics.average_days_between > 7:
                recommendations['timing_recommendation'] = 'schedule_in_advance'
            elif metrics.interactions_last_30_days > 5:
                recommendations['timing_recommendation'] = 'anytime'
            
            # Tempo estimado de resposta
            if metrics.response_time_hours_avg:
                recommendations['estimated_response_time_hours'] = metrics.response_time_hours_avg
            
            recommendations['confidence'] = min(0.9, metrics.rapport_score / 100)
        
        # Ajustar baseado no contexto
        if context == 'urgent':
            recommendations['preferred_channel'] = 'chat' if not recommendations['preferred_channel'] else recommendations['preferred_channel']
            recommendations['timing_recommendation'] = 'immediate'
        elif context == 'sensitive':
            recommendations['formality_level'] = 'high'
            recommendations['preferred_channel'] = 'in_person' if not recommendations['preferred_channel'] else recommendations['preferred_channel']
        
        return recommendations
    
    def export_to_json(self, filepath: str):
        """Exporta dados para arquivo JSON"""
        data = {
            'interactions': [interaction.to_dict() for interaction in self.interactions.values()],
            'relationships': [metrics.to_dict() for metrics in self.relationships.values()]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Dados de relacionamento exportados para {filepath}")

def create_relationship_manager(data_source: Optional[str] = None) -> RelationshipManager:
    """
    Factory function para criar gerenciador de relacionamentos.
    
    Args:
        data_source: Caminho para arquivo de dados (opcional)
        
    Returns:
        Instância do RelationshipManager
    """
    return RelationshipManager(data_source)