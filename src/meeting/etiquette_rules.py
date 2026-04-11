"""
Protocolos de Etiqueta para Participação em Reuniões
Fase 8: Participação em Reuniões - Comportamento Adequado da IA

Autor: Jarvis (OpenClaw)
Data: 2026-04-11

Objetivo:
- Definir regras de comportamento para IA em reuniões empresariais
- Determinar quando a IA deve falar, quando deve ficar quieta
- Estabelecer tom, formalidade e nível de participação
- Considerar hierarquia, contexto cultural e tipo de reunião

Regras Baseadas Em:
1. Hierarquia organizacional
2. Tipo de reunião (brainstorming, decisão, status update)
3. Contexto cultural da organização
4. Papel da IA na reunião (participante, assistente, observador)
5. Sensibilidade do tópico
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MeetingType(Enum):
    """Tipos de reunião empresarial"""
    BRAINSTORMING = "brainstorming"
    DECISION_MAKING = "decision_making"
    STATUS_UPDATE = "status_update"
    PLANNING = "planning"
    RETROSPECTIVE = "retrospective"
    ONE_ON_ONE = "one_on_one"
    CLIENT_MEETING = "client_meeting"
    EXECUTIVE = "executive"
    ALL_HANDS = "all_hands"
    TRAINING = "training"

class IARole(Enum):
    """Papel da IA na reunião"""
    PARTICIPANT = "participant"      # Participa ativamente
    ASSISTANT = "assistant"         # Auxilia moderador/participantes
    OBSERVER = "observer"           # Apenas observa e toma notas
    FACILITATOR = "facilitator"     # Facilita a reunião
    TRANSCRIBER = "transcriber"     # Apenas transcreve

class CulturalContext(Enum):
    """Contexto cultural da organização"""
    FORMAL_HIERARCHICAL = "formal_hierarchical"    # Empresa tradicional, hierárquica
    INFORMAL_FLAT = "informal_flat"               # Startup, estrutura plana
    TECHNICAL_FOCUSED = "technical_focused"       # Foco técnico, dados
    SALES_DRIVEN = "sales_driven"                # Foco em vendas, relacionamento
    CREATIVE = "creative"                         # Agência criativa, publicidade

class EtiquetteRule:
    """Regra individual de etiqueta"""
    
    def __init__(self, 
                 name: str,
                 description: str,
                 condition: Dict[str, Any],
                 action: str,
                 priority: int = 1):
        """
        Args:
            name: Nome da regra
            description: Descrição da regra
            condition: Condição para aplicar a regra
            action: Ação a ser tomada ('speak', 'listen', 'ask_permission', 'defer')
            priority: Prioridade (1-10, 10 é mais alta)
        """
        self.name = name
        self.description = description
        self.condition = condition
        self.action = action
        self.priority = priority
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Avalia se a regra se aplica ao contexto"""
        try:
            # Verificar tipo de reunião
            if 'meeting_type' in self.condition:
                if context.get('meeting_type') != self.condition['meeting_type']:
                    return False
            
            # Verificar papel da IA
            if 'ia_role' in self.condition:
                if context.get('ia_role') != self.condition['ia_role']:
                    return False
            
            # Verificar contexto cultural
            if 'cultural_context' in self.condition:
                if context.get('cultural_context') != self.condition['cultural_context']:
                    return False
            
            # Verificar se há hierarquia presente
            if 'has_executives' in self.condition:
                has_executives = context.get('participants', {}).get('executives', 0) > 0
                if self.condition['has_executives'] != has_executives:
                    return False
            
            # Verificar se é tópico sensível
            if 'sensitive_topic' in self.condition:
                is_sensitive = context.get('sensitive_topic', False)
                if self.condition['sensitive_topic'] != is_sensitive:
                    return False
            
            # Verificar se a IA foi diretamente mencionada
            if 'mentioned_ia' in self.condition:
                mentioned = context.get('mentioned_ia', False)
                if self.condition['mentioned_ia'] != mentioned:
                    return False
            
            # Verificar se há pergunta direta
            if 'direct_question' in self.condition:
                direct_question = context.get('direct_question', False)
                if self.condition['direct_question'] != direct_question:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao avaliar regra {self.name}: {e}")
            return False

class MeetingEtiquetteRules:
    """Sistema de regras de etiqueta para reuniões"""
    
    def __init__(self, cultural_context: CulturalContext = CulturalContext.FORMAL_HIERARCHICAL):
        self.cultural_context = cultural_context
        self.rules = []
        self._initialize_default_rules()
        logger.info(f"✅ MeetingEtiquetteRules inicializado (contexto: {cultural_context.value})")
    
    def _initialize_default_rules(self):
        """Inicializa regras padrão de etiqueta"""
        
        # Regra 1: Não interromper executivos
        self.rules.append(EtiquetteRule(
            name="nao_interromper_executivos",
            description="Não falar quando executivos de alto nível estão falando",
            condition={
                'has_executives': True,
                'meeting_type': MeetingType.EXECUTIVE.value
            },
            action="listen",
            priority=10
        ))
        
        # Regra 2: Responder quando mencionado diretamente
        self.rules.append(EtiquetteRule(
            name="responder_quando_mencionado",
            description="Responder quando a IA é mencionada pelo nome",
            condition={
                'mentioned_ia': True
            },
            action="speak",
            priority=9
        ))
        
        # Regra 3: Pedir permissão para intervir
        self.rules.append(EtiquetteRule(
            name="pedir_permissao_para_intervir",
            description="Pedir permissão antes de intervir em reuniões formais",
            condition={
                'cultural_context': CulturalContext.FORMAL_HIERARCHICAL.value,
                'direct_question': False,
                'mentioned_ia': False
            },
            action="ask_permission",
            priority=8
        ))
        
        # Regra 4: Participar ativamente em brainstorming
        self.rules.append(EtiquetteRule(
            name="participar_ativamente_brainstorming",
            description="Participar ativamente em sessões de brainstorming",
            condition={
                'meeting_type': MeetingType.BRAINSTORMING.value,
                'cultural_context': CulturalContext.CREATIVE.value
            },
            action="speak",
            priority=7
        ))
        
        # Regra 5: Manter silêncio em reuniões de clientes
        self.rules.append(EtiquetteRule(
            name="silencioso_em_reunioes_cliente",
            description="Manter-se principalmente em modo de escuta em reuniões com clientes",
            condition={
                'meeting_type': MeetingType.CLIENT_MEETING.value,
                'sensitive_topic': True
            },
            action="listen",
            priority=9
        ))
        
        # Regra 6: Oferecer ajuda quando apropriado
        self.rules.append(EtiquetteRule(
            name="oferecer_ajuda_quando_apropriado",
            description="Oferecer ajuda quando detecta dificuldade ou pergunta técnica",
            condition={
                'ia_role': IARole.ASSISTANT.value,
                'direct_question': False,
                'mentioned_ia': False
            },
            action="offer_help",
            priority=6
        ))
        
        # Regra 7: Deferir para humanos em decisões sensíveis
        self.rules.append(EtiquetteRule(
            name="deferir_decisoes_sensiveis",
            description="Deferir para humanos em decisões sensíveis ou éticas",
            condition={
                'sensitive_topic': True,
                'meeting_type': MeetingType.DECISION_MAKING.value
            },
            action="defer",
            priority=10
        ))
        
        # Regra 8: Usar tom formal em contextos hierárquicos
        self.rules.append(EtiquetteRule(
            name="tom_formal_hierarquico",
            description="Usar tom formal e respeitoso em organizações hierárquicas",
            condition={
                'cultural_context': CulturalContext.FORMAL_HIERARCHICAL.value
            },
            action="formal_tone",
            priority=8
        ))
        
        # Regra 9: Tom casual em startups
        self.rules.append(EtiquetteRule(
            name="tom_casual_startup",
            description="Usar tom mais casual e direto em startups",
            condition={
                'cultural_context': CulturalContext.INFORMAL_FLAT.value
            },
            action="casual_tone",
            priority=7
        ))
        
        # Regra 10: Focar em dados em contextos técnicos
        self.rules.append(EtiquetteRule(
            name="foco_dados_contexto_tecnico",
            description="Focar em dados e fatos em organizações técnicas",
            condition={
                'cultural_context': CulturalContext.TECHNICAL_FOCUSED.value
            },
            action="data_focused",
            priority=7
        ))
        
        logger.info(f"✅ {len(self.rules)} regras de etiqueta inicializadas")
    
    def evaluate_context(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Avalia o contexto da reunião e retorna regras aplicáveis.
        
        Args:
            context: Dicionário com contexto da reunião
            
        Returns:
            Lista de regras aplicáveis ordenadas por prioridade
        """
        applicable_rules = []
        
        # Adicionar contexto cultural padrão se não especificado
        if 'cultural_context' not in context:
            context['cultural_context'] = self.cultural_context.value
        
        for rule in self.rules:
            if rule.evaluate(context):
                applicable_rules.append({
                    'name': rule.name,
                    'description': rule.description,
                    'action': rule.action,
                    'priority': rule.priority
                })
        
        # Ordenar por prioridade (maior primeiro)
        applicable_rules.sort(key=lambda x: x['priority'], reverse=True)
        
        logger.info(f"✅ {len(applicable_rules)} regras aplicáveis ao contexto")
        return applicable_rules
    
    def get_recommended_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtém a ação recomendada com base nas regras aplicáveis.
        
        Args:
            context: Contexto da reunião
            
        Returns:
            Dicionário com ação recomendada e justificativa
        """
        applicable_rules = self.evaluate_context(context)
        
        if not applicable_rules:
            # Default: ouvir e observar
            return {
                'action': 'listen',
                'confidence': 0.7,
                'reasoning': 'Nenhuma regra específica aplicável. Modo padrão: observar.',
                'applied_rules': []
            }
        
        # Pegar a regra de maior prioridade
        top_rule = applicable_rules[0]
        
        # Se houver múltiplas regras de alta prioridade, considerar combinações
        high_priority_rules = [r for r in applicable_rules if r['priority'] >= 8]
        
        if len(high_priority_rules) > 1:
            # Regras conflitantes de alta prioridade
            actions = set(r['action'] for r in high_priority_rules)
            
            # Resolver conflitos: preferir 'listen' sobre 'speak' em caso de dúvida
            if 'listen' in actions and 'speak' in actions:
                action = 'listen'  # Quando em dúvida, ouvir
                reasoning = f"Conflito entre regras de alta prioridade. Preferindo 'listen' por segurança."
            else:
                action = top_rule['action']
                reasoning = f"Ação baseada na regra de maior prioridade: {top_rule['name']}"
        else:
            action = top_rule['action']
            reasoning = f"Ação baseada na regra: {top_rule['name']}"
        
        return {
            'action': action,
            'confidence': min(0.9, 0.5 + (top_rule['priority'] / 20)),  # 0.5-0.9
            'reasoning': reasoning,
            'applied_rules': [r['name'] for r in applicable_rules],
            'top_rule': top_rule['name'],
            'rule_description': top_rule['description']
        }
    
    def should_speak(self, context: Dict[str, Any]) -> bool:
        """
        Determina se a IA deve falar no contexto atual.
        
        Args:
            context: Contexto da reunião
            
        Returns:
            True se a IA deve falar
        """
        recommendation = self.get_recommended_action(context)
        
        speak_actions = ['speak', 'ask_permission', 'offer_help']
        return recommendation['action'] in speak_actions
    
    def get_speech_guidelines(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtém diretrizes para fala da IA com base no contexto.
        
        Args:
            context: Contexto da reunião
            
        Returns:
            Diretrizes para fala (tom, formalidade, conteúdo)
        """
        applicable_rules = self.evaluate_context(context)
        
        guidelines = {
            'tone': 'neutral',
            'formality': 'medium',
            'content_focus': 'balanced',
            'max_duration_seconds': 30,
            'allow_humor': False,
            'allow_opinions': False,
            'require_data_backup': False
        }
        
        # Aplicar regras de tom
        for rule in applicable_rules:
            if rule['action'] == 'formal_tone':
                guidelines['tone'] = 'formal'
                guidelines['formality'] = 'high'
                guidelines['allow_humor'] = False
            elif rule['action'] == 'casual_tone':
                guidelines['tone'] = 'casual'
                guidelines['formality'] = 'low'
                guidelines['allow_humor'] = True
            elif rule['action'] == 'data_focused':
                guidelines['content_focus'] = 'data'
                guidelines['require_data_backup'] = True
                guidelines['allow_opinions'] = False
        
        # Ajustar baseado no tipo de reunião
        meeting_type = context.get('meeting_type')
        if meeting_type == MeetingType.BRAINSTORMING.value:
            guidelines['allow_opinions'] = True
            guidelines['allow_humor'] = True
            guidelines['max_duration_seconds'] = 60
        elif meeting_type == MeetingType.EXECUTIVE.value:
            guidelines['tone'] = 'formal'
            guidelines['formality'] = 'high'
            guidelines['max_duration_seconds'] = 15
            guidelines['require_data_backup'] = True
        
        return guidelines

def create_etiquette_rules(cultural_context: CulturalContext = None) -> MeetingEtiquetteRules:
    """
    Factory function para criar sistema de regras de etiqueta.
    
    Args:
        cultural_context: Contexto cultural (opcional)
        
    Returns:
        Instância do MeetingEtiquetteRules
    """
    if cultural_context is None:
        cultural_context = CulturalContext.FORMAL_HIERARCHICAL
    
    return MeetingEtiquetteRules(cultural_context)