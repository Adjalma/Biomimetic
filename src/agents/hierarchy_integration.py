"""
Integração de Hierarquia Organizacional com Sistema de Ação Autônoma
Autor: Jarvis (OpenClaw)
Data: 2026-04-11

Objetivo:
- Conectar OrganizationalHierarchy com AutonomousActionOrchestrator
- Fornecer decisões baseadas em hierarquia para ações autônomas
- Determinar formalidade e protocolos baseados em posição organizacional
- Validar autoridade para ações sensíveis
- Integrar com SecurityProtocols para aprovações baseadas em hierarquia

Funcionalidades:
- Consultar posição hierárquica de participantes
- Determinar se ação requer aprovação baseada em hierarquia
- Sugerir formalidade de comunicação baseada em diferença hierárquica
- Validar se usuário tem autoridade para certas ações
- Integrar com sistema biomimético para decisões hierárquicas
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum
from datetime import datetime

# Importar OrganizationalHierarchy
try:
    from .organizational_hierarchy import OrganizationalHierarchy, Employee, EmployeeRole
    HIERARCHY_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️  OrganizationalHierarchy não disponível: {e}")
    HIERARCHY_AVAILABLE = False
    EmployeeRole = Enum('EmployeeRole', ['CEO', 'CTO', 'CFO', 'COO', 'VP', 'DIRECTOR', 
                                         'SENIOR_MANAGER', 'MANAGER', 'TEAM_LEAD', 
                                         'SENIOR_ENGINEER', 'ENGINEER', 'ANALYST', 
                                         'INTERN', 'CONTRACTOR', 'EXTERNAL'])

logger = logging.getLogger(__name__)

class HierarchyDecision(Enum):
    """Decisões baseadas em hierarquia"""
    APPROVE_AUTOMATICALLY = "approve_automatically"  # Ação pode ser executada automaticamente
    REQUIRE_APPROVAL = "require_approval"           # Requer aprovação humana
    REQUIRE_MANAGER_APPROVAL = "require_manager_approval"  # Requer aprovação do gerente
    REQUIRE_EXECUTIVE_APPROVAL = "require_executive_approval"  # Requer aprovação executiva
    BLOCK_ACTION = "block_action"                   # Bloquear ação completamente
    ESCALATE = "escalate"                           # Escalar para nível superior

class FormalizationLevel(Enum):
    """Níveis de formalização baseados em hierarquia"""
    HIGHLY_FORMAL = "highly_formal"      # CEO, executivos, comunicação externa
    FORMAL = "formal"                    # Diretores, gerentes sênior
    SEMI_FORMAL = "semi_formal"          # Gerentes, colegas de diferentes departamentos
    INFORMAL = "informal"                # Colegas do mesmo time, subordinados diretos
    HIGHLY_INFORMAL = "highly_informal"  # Times muito próximos, comunicação interna

class HierarchyIntegration:
    """Integração de hierarquia organizacional com sistema de ação"""
    
    def __init__(self, hierarchy_data_source: Optional[str] = None):
        """
        Inicializa integração de hierarquia.
        
        Args:
            hierarchy_data_source: Caminho para arquivo de dados hierárquicos
        """
        self.hierarchy = None
        self.enabled = HIERARCHY_AVAILABLE
        
        if self.enabled and hierarchy_data_source:
            try:
                self.hierarchy = OrganizationalHierarchy(hierarchy_data_source)
                logger.info(f"✅ Hierarquia organizacional carregada de {hierarchy_data_source}")
            except Exception as e:
                logger.error(f"❌ Falha ao carregar hierarquia: {e}")
                self.enabled = False
        elif self.enabled:
            try:
                self.hierarchy = OrganizationalHierarchy()
                logger.info("✅ Hierarquia organizacional inicializada vazia")
            except Exception as e:
                logger.error(f"❌ Falha ao inicializar hierarquia: {e}")
                self.enabled = False
        
        # Mapeamento de cargos para níveis de autoridade
        self.authority_levels = {
            EmployeeRole.CEO: 100,
            EmployeeRole.CTO: 95,
            EmployeeRole.CFO: 95,
            EmployeeRole.COO: 95,
            EmployeeRole.VP: 90,
            EmployeeRole.DIRECTOR: 85,
            EmployeeRole.SENIOR_MANAGER: 75,
            EmployeeRole.MANAGER: 70,
            EmployeeRole.TEAM_LEAD: 60,
            EmployeeRole.SENIOR_ENGINEER: 50,
            EmployeeRole.ENGINEER: 40,
            EmployeeRole.ANALYST: 30,
            EmployeeRole.INTERN: 10,
            EmployeeRole.CONTRACTOR: 20,
            EmployeeRole.EXTERNAL: 5,
        }
        
        # Configurações
        self.auto_approval_threshold = 70  # Autoridade >= 70 pode aprovar automaticamente
        self.require_executive_approval_for = {
            "budget_approval": 80,  # Aprovações orçamentárias acima de 80% do limite
            "new_hire": True,       # Novas contratações sempre requerem aprovação executiva
            "major_purchase": 10000,  # Compras acima de R$10.000
        }
        
        logger.info(f"✅ HierarchyIntegration inicializado (enabled: {self.enabled})")
    
    def evaluate_action_with_hierarchy(self, 
                                      action_type: str, 
                                      parameters: Dict[str, Any],
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia ação considerando hierarquia organizacional.
        
        Args:
            action_type: Tipo de ação (ex: "SEND_EMAIL", "SCHEDULE_MEETING")
            parameters: Parâmetros da ação
            context: Contexto incluindo participantes
        
        Returns:
            Dict com:
            - hierarchy_decision: HierarchyDecision
            - required_approval_level: str (se requer aprovação)
            - formalization_level: FormalizationLevel
            - authority_validation: bool (se usuário tem autoridade)
            - hierarchical_constraints: List[str] (restrições hierárquicas)
            - suggested_approach: str (abordagem sugerida)
        """
        
        if not self.enabled or not self.hierarchy:
            return self._get_disabled_response()
        
        # Extrair participantes do contexto
        initiator_id = context.get("user_id", "unknown")
        participants = self._extract_participants(parameters, context)
        
        # Identificar papéis hierárquicos
        initiator = self._get_participant_info(initiator_id)
        highest_rank_participant = self._get_highest_rank_participant(participants)
        
        # Tomar decisão baseada em hierarquia
        decision, decision_reason = self._make_hierarchy_decision(
            action_type, initiator, highest_rank_participant, parameters, context
        )
        
        # Determinar nível de formalização
        formalization = self._determine_formalization_level(
            initiator, highest_rank_participant, action_type, context
        )
        
        # Validar autoridade do iniciador
        authority_valid, authority_reason = self._validate_authority(
            initiator, action_type, parameters
        )
        
        # Identificar restrições hierárquicas
        constraints = self._identify_hierarchical_constraints(
            initiator, participants, action_type, parameters
        )
        
        # Sugerir abordagem
        suggested_approach = self._suggest_approach(
            decision, formalization, authority_valid, constraints
        )
        
        return {
            "hierarchy_decision": decision.value,
            "decision_reason": decision_reason,
            "required_approval_level": self._get_approval_level(decision),
            "formalization_level": formalization.value,
            "authority_validation": authority_valid,
            "authority_reason": authority_reason,
            "hierarchical_constraints": constraints,
            "suggested_approach": suggested_approach,
            "initiator_role": initiator.get("role", "unknown") if initiator else "unknown",
            "highest_rank_role": highest_rank_participant.get("role", "unknown") if highest_rank_participant else "unknown",
            "hierarchy_enabled": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_participants(self, parameters: Dict[str, Any], 
                             context: Dict[str, Any]) -> List[str]:
        """Extrai IDs de participantes dos parâmetros e contexto"""
        participants = set()
        
        # Extrair do contexto
        if "participants" in context:
            participants.update(self._normalize_participant_ids(context["participants"]))
        
        # Extrair dos parâmetros
        for key in ["to", "recipients", "attendees", "participants"]:
            if key in parameters:
                participants.update(self._normalize_participant_ids(parameters[key]))
        
        # Adicionar iniciador se conhecido
        if "user_id" in context and context["user_id"] != "unknown":
            participants.add(context["user_id"])
        
        return list(participants)
    
    def _normalize_participant_ids(self, participants) -> List[str]:
        """Normaliza IDs de participantes (email, ID, nome)"""
        if not participants:
            return []
        
        if isinstance(participants, str):
            participants = [participants]
        
        normalized = []
        for participant in participants:
            if isinstance(participant, str):
                # Tentar extrair email ou usar como ID
                if '@' in participant:
                    # É um email, tentar encontrar funcionário
                    normalized.append(participant)
                else:
                    normalized.append(participant)
        
        return normalized
    
    def _get_participant_info(self, participant_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações hierárquicas de um participante"""
        if not self.hierarchy or not participant_id:
            return None
        
        # Tentar por email primeiro
        employee = self.hierarchy.get_employee_by_email(participant_id)
        if not employee and '@' not in participant_id:
            # Tentar por ID
            employee = self.hierarchy.get_employee(participant_id)
        
        if employee:
            return {
                "id": employee.id,
                "email": employee.email,
                "role": employee.role,
                "role_name": employee.role.value,
                "level": employee.level,
                "authority": self.authority_levels.get(employee.role, 0),
                "department": employee.department,
                "manager_id": employee.manager_id,
            }
        
        return None
    
    def _get_highest_rank_participant(self, participants: List[str]) -> Optional[Dict[str, Any]]:
        """Identifica participante com maior autoridade hierárquica"""
        highest_authority = -1
        highest_participant = None
        
        for participant_id in participants:
            info = self._get_participant_info(participant_id)
            if info:
                authority = info.get("authority", 0)
                if authority > highest_authority:
                    highest_authority = authority
                    highest_participant = info
        
        return highest_participant
    
    def _make_hierarchy_decision(self, 
                                action_type: str,
                                initiator: Optional[Dict[str, Any]],
                                highest_rank_participant: Optional[Dict[str, Any]],
                                parameters: Dict[str, Any],
                                context: Dict[str, Any]) -> Tuple[HierarchyDecision, str]:
        """Toma decisão baseada em hierarquia"""
        
        # Se não temos informações hierárquicas, requer aprovação por segurança
        if not initiator:
            return HierarchyDecision.REQUIRE_APPROVAL, "Iniciador não identificado na hierarquia"
        
        initiator_authority = initiator.get("authority", 0)
        
        # Ações críticas sempre requerem aprovação executiva
        if action_type in ["DELETE_EMAIL", "FIRE_EMPLOYEE", "GRANT_ACCESS"]:
            if initiator_authority >= 90:  # Executivos
                return HierarchyDecision.APPROVE_AUTOMATICALLY, f"Executivo com autoridade {initiator_authority}"
            else:
                return HierarchyDecision.REQUIRE_EXECUTIVE_APPROVAL, f"Ação crítica requer aprovação executiva"
        
        # Verificar se há participantes de alto nível
        if highest_rank_participant:
            highest_authority = highest_rank_participant.get("authority", 0)
            
            # Se participante tem autoridade muito maior que iniciador
            if highest_authority - initiator_authority > 30:
                return HierarchyDecision.REQUIRE_MANAGER_APPROVAL, f"Participante com autoridade {highest_authority} muito superior ao iniciador {initiator_authority}"
            
            # Se participante é executivo
            if highest_authority >= 90:
                return HierarchyDecision.REQUIRE_APPROVAL, f"Participante executivo (autoridade {highest_authority})"
        
        # Verificar limites orçamentários
        if "budget" in parameters:
            budget = parameters["budget"]
            budget_limit = self.require_executive_approval_for.get("major_purchase", 10000)
            
            if budget > budget_limit:
                if initiator_authority >= 85:  # Diretores podem aprovar
                    return HierarchyDecision.APPROVE_AUTOMATICALLY, f"Diretor pode aprovar orçamento de {budget}"
                else:
                    return HierarchyDecision.REQUIRE_EXECUTIVE_APPROVAL, f"Orçamento {budget} acima do limite {budget_limit}"
        
        # Decisão baseada na autoridade do iniciador
        if initiator_authority >= self.auto_approval_threshold:
            return HierarchyDecision.APPROVE_AUTOMATICALLY, f"Autoridade suficiente ({initiator_authority})"
        else:
            return HierarchyDecision.REQUIRE_APPROVAL, f"Autoridade insuficiente ({initiator_authority} < {self.auto_approval_threshold})"
    
    def _determine_formalization_level(self,
                                      initiator: Optional[Dict[str, Any]],
                                      highest_rank_participant: Optional[Dict[str, Any]],
                                      action_type: str,
                                      context: Dict[str, Any]) -> FormalizationLevel:
        """Determina nível de formalização baseado em hierarquia"""
        
        if not initiator or not highest_rank_participant:
            # Se falta informação, usar formal por segurança
            return FormalizationLevel.FORMAL
        
        initiator_auth = initiator.get("authority", 0)
        highest_auth = highest_rank_participant.get("authority", 0)
        
        # Calcular diferença de autoridade
        auth_diff = abs(highest_auth - initiator_auth)
        
        # Determinar formalidade baseada na diferença
        if auth_diff >= 40:
            return FormalizationLevel.HIGHLY_FORMAL
        elif auth_diff >= 20:
            return FormalizationLevel.FORMAL
        elif auth_diff >= 10:
            return FormalizationLevel.SEMI_FORMAL
        elif auth_diff >= 5:
            return FormalizationLevel.INFORMAL
        else:
            return FormalizationLevel.HIGHLY_INFORMAL
    
    def _validate_authority(self, 
                           initiator: Optional[Dict[str, Any]],
                           action_type: str,
                           parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida se iniciador tem autoridade para ação"""
        
        if not initiator:
            return False, "Iniciador não identificado"
        
        initiator_auth = initiator.get("authority", 0)
        
        # Ações que requerem autoridade mínima
        min_authority_requirements = {
            "SCHEDULE_MEETING": 30,      # Engenheiro sênior
            "SEND_EMAIL": 20,            # Engenheiro
            "CREATE_REMINDER": 10,       # Estagiário
            "DELETE_EMAIL": 70,          # Gerente
            "GRANT_ACCESS": 85,          # Diretor
            "APPROVE_BUDGET": 80,        # Diretor
            "HIRE_EMPLOYEE": 90,         # VP+
        }
        
        required_auth = min_authority_requirements.get(action_type, 0)
        
        if initiator_auth >= required_auth:
            return True, f"Autoridade suficiente ({initiator_auth} >= {required_auth})"
        else:
            return False, f"Autoridade insuficiente ({initiator_auth} < {required_auth})"
    
    def _identify_hierarchical_constraints(self,
                                          initiator: Optional[Dict[str, Any]],
                                          participants: List[str],
                                          action_type: str,
                                          parameters: Dict[str, Any]) -> List[str]:
        """Identifica restrições hierárquicas para a ação"""
        
        constraints = []
        
        if not initiator:
            constraints.append("Iniciador não identificado na hierarquia")
            return constraints
        
        # Verificar se há superiores diretos entre participantes
        initiator_info = initiator
        manager_id = initiator_info.get("manager_id")
        
        if manager_id and manager_id in participants:
            constraints.append("Gerente direto está entre os participantes")
        
        # Verificar diferença hierárquica extrema
        for participant_id in participants:
            participant_info = self._get_participant_info(participant_id)
            if participant_info:
                auth_diff = abs(initiator_info.get("authority", 0) - participant_info.get("authority", 0))
                if auth_diff > 50:
                    constraints.append(f"Diferença de autoridade extrema com {participant_id}")
        
        # Verificar ações entre departamentos diferentes
        initiator_dept = initiator_info.get("department", "")
        for participant_id in participants:
            participant_info = self._get_participant_info(participant_id)
            if participant_info:
                participant_dept = participant_info.get("department", "")
                if participant_dept and initiator_dept and participant_dept != initiator_dept:
                    constraints.append(f"Ação envolve departamento diferente: {participant_dept}")
                    break
        
        return constraints
    
    def _suggest_approach(self,
                         decision: HierarchyDecision,
                         formalization: FormalizationLevel,
                         authority_valid: bool,
                         constraints: List[str]) -> str:
        """Sugere abordagem baseada na análise hierárquica"""
        
        if not authority_valid:
            return "Não prosseguir - falta de autoridade"
        
        if decision == HierarchyDecision.BLOCK_ACTION:
            return "Ação bloqueada por restrições hierárquicas"
        
        if constraints:
            constraints_text = ", ".join(constraints[:3])
            return f"Proceder com cautela devido a: {constraints_text}"
        
        if decision == HierarchyDecision.APPROVE_AUTOMATICALLY:
            if formalization in [FormalizationLevel.HIGHLY_FORMAL, FormalizationLevel.FORMAL]:
                return f"Executar ação com formalidade {formalization.value}"
            else:
                return f"Executar ação normalmente ({formalization.value})"
        
        if decision in [HierarchyDecision.REQUIRE_APPROVAL, 
                       HierarchyDecision.REQUIRE_MANAGER_APPROVAL,
                       HierarchyDecision.REQUIRE_EXECUTIVE_APPROVAL]:
            return f"Solicitar aprovação conforme decisão hierárquica: {decision.value}"
        
        return "Proceder com a ação normalmente"
    
    def _get_approval_level(self, decision: HierarchyDecision) -> str:
        """Obtém nível de aprovação requerido"""
        decision_to_approval = {
            HierarchyDecision.APPROVE_AUTOMATICALLY: "none",
            HierarchyDecision.REQUIRE_APPROVAL: "any_approver",
            HierarchyDecision.REQUIRE_MANAGER_APPROVAL: "direct_manager",
            HierarchyDecision.REQUIRE_EXECUTIVE_APPROVAL: "executive",
            HierarchyDecision.BLOCK_ACTION: "blocked",
            HierarchyDecision.ESCALATE: "escalated",
        }
        return decision_to_approval.get(decision, "unknown")
    
    def _get_disabled_response(self) -> Dict[str, Any]:
        """Resposta quando hierarquia está desabilitada"""
        return {
            "hierarchy_decision": "require_approval",
            "decision_reason": "Hierarquia organizacional não disponível",
            "required_approval_level": "any_approver",
            "formalization_level": "formal",
            "authority_validation": False,
            "authority_reason": "Sistema de hierarquia não disponível",
            "hierarchical_constraints": ["Hierarquia não configurada"],
            "suggested_approach": "Requer aprovação manual - sistema de hierarquia indisponível",
            "initiator_role": "unknown",
            "highest_rank_role": "unknown",
            "hierarchy_enabled": False,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_hierarchy_status(self) -> Dict[str, Any]:
        """Obtém status do sistema de hierarquia"""
        if not self.enabled or not self.hierarchy:
            return {
                "enabled": False,
                "employee_count": 0,
                "ceo_identified": False,
                "departments": 0,
            }
        
        ceo_identified = self.hierarchy.ceo_id is not None
        dept_count = len(self.hierarchy.departments) if hasattr(self.hierarchy, 'departments') else 0
        
        return {
            "enabled": True,
            "employee_count": len(self.hierarchy.employees),
            "ceo_identified": ceo_identified,
            "departments": dept_count,
            "auto_approval_threshold": self.auto_approval_threshold,
            "authority_levels_defined": len(self.authority_levels),
        }
    
    def add_employee_manually(self, employee_data: Dict[str, Any]) -> bool:
        """Adiciona funcionário manualmente à hierarquia"""
        if not self.enabled or not self.hierarchy:
            return False
        
        try:
            from .organizational_hierarchy import Employee, EmployeeRole
            
            # Converter role string para EmployeeRole
            role_str = employee_data["role"]
            role = None
            
            # Mapeamento de strings comuns para valores do enum
            role_mapping = {
                "CEO": EmployeeRole.CEO,
                "CTO": EmployeeRole.CTO,
                "CFO": EmployeeRole.CFO,
                "COO": EmployeeRole.COO,
                "VP": EmployeeRole.VP,
                "DIRECTOR": EmployeeRole.DIRECTOR,
                "SENIOR_MANAGER": EmployeeRole.SENIOR_MANAGER,
                "MANAGER": EmployeeRole.MANAGER,
                "TEAM_LEAD": EmployeeRole.TEAM_LEAD,
                "SENIOR_ENGINEER": EmployeeRole.SENIOR_ENGINEER,
                "ENGINEER": EmployeeRole.ENGINEER,
                "ANALYST": EmployeeRole.ANALYST,
                "INTERN": EmployeeRole.INTERN,
                "CONTRACTOR": EmployeeRole.CONTRACTOR,
                "EXTERNAL": EmployeeRole.EXTERNAL,
            }
            
            # Tentar mapeamento direto
            if role_str in role_mapping:
                role = role_mapping[role_str]
            else:
                # Tentar converter para minúsculas e remover underscores
                normalized = role_str.lower().replace(" ", "_").replace("-", "_")
                try:
                    role = EmployeeRole(normalized)
                except ValueError:
                    # Tentar encontrar por correspondência parcial
                    for enum_member in EmployeeRole:
                        if enum_member.value.lower() == normalized.lower():
                            role = enum_member
                            break
            
            if role is None:
                logger.error(f"❌ Role inválida: {role_str}")
                return False
            
            employee = Employee(
                id=employee_data["id"],
                name=employee_data["name"],
                email=employee_data["email"],
                role=role,
                department=employee_data.get("department", "Unknown"),
                manager_id=employee_data.get("manager_id"),
                direct_reports=employee_data.get("direct_reports", []),
                level=employee_data.get("level", 0),
                start_date=employee_data.get("start_date"),
                tags=employee_data.get("tags", [])
            )
            
            self.hierarchy.add_employee(employee)
            logger.info(f"✅ Funcionário adicionado manualmente: {employee.name} ({role.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar funcionário manualmente: {e}")
            return False
    
    def find_appropriate_approver(self, action_type: str, 
                                 initiator_id: str) -> Optional[Dict[str, Any]]:
        """
        Encontra aprovador apropriado baseado em hierarquia.
        
        Args:
            action_type: Tipo de ação
            initiator_id: ID do iniciador
        
        Returns:
            Informações do aprovador apropriado ou None
        """
        if not self.enabled or not self.hierarchy:
            return None
        
        initiator = self._get_participant_info(initiator_id)
        if not initiator:
            return None
        
        # Para ações críticas, encontrar executivo apropriado
        if action_type in ["DELETE_EMAIL", "FIRE_EMPLOYEE", "GRANT_ACCESS"]:
            # Procurar VP ou diretor no mesmo departamento
            for emp in self.hierarchy.employees.values():
                if emp.role in [EmployeeRole.VP, EmployeeRole.DIRECTOR]:
                    if emp.department == initiator.get("department", ""):
                        return self._get_participant_info(emp.id)
        
        # Para outras ações, usar gerente direto
        manager_id = initiator.get("manager_id")
        if manager_id:
            return self._get_participant_info(manager_id)
        
        # Se não tem gerente, procurar alguém com autoridade maior
        initiator_auth = initiator.get("authority", 0)
        for emp in self.hierarchy.employees.values():
            emp_auth = self.authority_levels.get(emp.role, 0)
            if emp_auth > initiator_auth + 10:  # Alguém com autoridade significativamente maior
                return self._get_participant_info(emp.id)
        
        return None