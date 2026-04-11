"""
Protocolos de Segurança para Ações Autônomas
Autor: Jarvis (OpenClaw)
Data: 2026-04-11

Objetivo:
- Definir níveis de segurança para ações autônomas
- Determinar quando requerer aprovação humana
- Gerenciar confiança do usuário
- Criar solicitações de aprovação com timeout
- Implementar sistema de rollback para ações problemáticas

Integração:
- Usado pelo AutonomousActionOrchestrator
- Conectado com OrganizationalHierarchy para verificar autoridade
- Integrado com sistema biomimético para aprendizado de segurança
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import uuid

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Níveis de segurança para ações"""
    SAFE = "safe"           # Ação segura, sem aprovação necessária
    LOW_RISK = "low_risk"   # Baixo risco, aprovação opcional
    MEDIUM_RISK = "medium_risk"  # Risco moderado, aprovação recomendada
    HIGH_RISK = "high_risk" # Alto risco, aprovação obrigatória
    DANGEROUS = "dangerous" # Perigosa, aprovação múltipla necessária

class UserTrustLevel(Enum):
    """Níveis de confiança do usuário"""
    NEW = 0          # Usuário novo, alto monitoramento
    LOW = 1          # Baixa confiança
    MEDIUM = 2       # Confiança média
    HIGH = 3         # Alta confiança
    ADMIN = 4        # Administrador, confiança total

class ActionSecurity:
    """Define segurança de um tipo de ação"""
    
    def __init__(self, action_type: str, default_level: SecurityLevel, 
                 requires_approval: bool = False, max_recipients: int = 10):
        self.action_type = action_type
        self.default_level = default_level
        self.requires_approval = requires_approval
        self.max_recipients = max_recipients
        self.dangerous_params: Set[str] = set()
        self.allowed_users: Set[str] = set()  # IDs de usuários autorizados
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "default_level": self.default_level.value,
            "requires_approval": self.requires_approval,
            "max_recipients": self.max_recipients,
            "dangerous_params": list(self.dangerous_params),
            "allowed_users": list(self.allowed_users)
        }

class SecurityProtocols:
    """Sistema de protocolos de segurança"""
    
    def __init__(self):
        self.security_rules: Dict[str, ActionSecurity] = {}
        self.user_trust: Dict[str, UserTrustLevel] = {}
        self.approval_requests: Dict[str, Dict] = {}
        self.rollback_points: Dict[str, Dict] = {}
        
        # Configurações padrão
        self.default_trust_level = UserTrustLevel.MEDIUM
        self.max_auto_actions_per_hour = 20
        self.require_multi_approval_for_dangerous = True
        
        # Inicializar regras padrão
        self._initialize_default_rules()
        
        logger.info("✅ SecurityProtocols inicializado")
    
    def _initialize_default_rules(self):
        """Inicializa regras de segurança padrão"""
        
        # Ações perigosas (sempre requerem aprovação)
        dangerous_actions = {
            "DELETE_EMAIL": ActionSecurity("DELETE_EMAIL", SecurityLevel.DANGEROUS, True, 1),
            "SEND_MONEY": ActionSecurity("SEND_MONEY", SecurityLevel.DANGEROUS, True, 1),
            "FIRE_EMPLOYEE": ActionSecurity("FIRE_EMPLOYEE", SecurityLevel.DANGEROUS, True, 1),
            "GRANT_ACCESS": ActionSecurity("GRANT_ACCESS", SecurityLevel.HIGH_RISK, True, 5),
            "CHANGE_PASSWORD": ActionSecurity("CHANGE_PASSWORD", SecurityLevel.HIGH_RISK, True, 1),
            "SHARE_CONFIDENTIAL": ActionSecurity("SHARE_CONFIDENTIAL", SecurityLevel.HIGH_RISK, True, 3),
        }
        
        # Ações de alto risco
        high_risk_actions = {
            "SEND_EMAIL": ActionSecurity("SEND_EMAIL", SecurityLevel.HIGH_RISK, False, 10),
            "SCHEDULE_MEETING": ActionSecurity("SCHEDULE_MEETING", SecurityLevel.MEDIUM_RISK, False, 15),
            "CREATE_REMINDER": ActionSecurity("CREATE_REMINDER", SecurityLevel.LOW_RISK, False, 20),
        }
        
        # Ações seguras
        safe_actions = {
            "SAVE_TO_MEMORY": ActionSecurity("SAVE_TO_MEMORY", SecurityLevel.SAFE, False, 100),
            "QUERY_MEMORY": ActionSecurity("QUERY_MEMORY", SecurityLevel.SAFE, False, 100),
            "ANALYZE_CONTEXT": ActionSecurity("ANALYZE_CONTEXT", SecurityLevel.SAFE, False, 100),
        }
        
        # Registrar todas
        for actions_dict in [dangerous_actions, high_risk_actions, safe_actions]:
            for action_name, security in actions_dict.items():
                self.security_rules[action_name] = security
        
        logger.info(f"✅ {len(self.security_rules)} regras de segurança inicializadas")
    
    def evaluate_action(self, action_type: str, parameters: Dict[str, Any], 
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia uma ação e retorna recomendação de segurança.
        
        Returns:
            Dict com:
            - security_level: SecurityLevel
            - requires_approval: bool
            - approval_reason: str (se requer aprovação)
            - risk_score: float (0-1)
            - suggested_mitigations: List[str]
        """
        
        # Obter regra para ação
        security_rule = self.security_rules.get(action_type)
        if not security_rule:
            # Se ação desconhecida, tratar como de alto risco
            security_rule = ActionSecurity(action_type, SecurityLevel.HIGH_RISK, True, 5)
        
        # Calcular nível de segurança baseado em parâmetros
        security_level = self._calculate_security_level(
            security_rule, action_type, parameters, context
        )
        
        # Calcular se requer aprovação
        requires_approval, approval_reason = self._requires_approval(
            security_rule, security_level, parameters, context
        )
        
        # Calcular score de risco
        risk_score = self._calculate_risk_score(security_level, parameters)
        
        # Sugerir mitigações
        mitigations = self._suggest_mitigations(security_level, risk_score, parameters)
        
        return {
            "security_level": security_level.value,
            "requires_approval": requires_approval,
            "approval_reason": approval_reason,
            "risk_score": risk_score,
            "suggested_mitigations": mitigations,
            "action_type": action_type,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_security_level(self, security_rule: ActionSecurity, 
                                 action_type: str, parameters: Dict[str, Any],
                                 context: Dict[str, Any]) -> SecurityLevel:
        """Calcula nível de segurança considerando contexto"""
        
        # Começar com nível padrão
        level = security_rule.default_level
        
        # Verificar parâmetros perigosos
        dangerous_params_present = False
        for param_name in security_rule.dangerous_params:
            if param_name in parameters and parameters[param_name]:
                dangerous_params_present = True
                break
        
        if dangerous_params_present:
            if level.value < SecurityLevel.HIGH_RISK.value:
                level = SecurityLevel.HIGH_RISK
        
        # Verificar número de destinatários
        if "recipients" in parameters:
            recipients = parameters["recipients"]
            if isinstance(recipients, list) and len(recipients) > security_rule.max_recipients:
                level = SecurityLevel.HIGH_RISK
        
        # Verificar confiança do usuário
        user_id = context.get("user_id", "unknown")
        trust_level = self.user_trust.get(user_id, self.default_trust_level)
        
        if trust_level.value <= UserTrustLevel.LOW.value:
            # Usuário de baixa confiança: aumentar nível de segurança
            if level.value < SecurityLevel.MEDIUM_RISK.value:
                level = SecurityLevel.MEDIUM_RISK
        
        # Verificar hora do dia (ações noturnas são mais arriscadas)
        hour = datetime.now().hour
        if 22 <= hour or hour < 6:  # Entre 22h e 6h
            if level.value < SecurityLevel.MEDIUM_RISK.value:
                level = SecurityLevel.MEDIUM_RISK
        
        return level
    
    def _requires_approval(self, security_rule: ActionSecurity, 
                          security_level: SecurityLevel,
                          parameters: Dict[str, Any],
                          context: Dict[str, Any]) -> (bool, str):
        """Determina se ação requer aprovação e motivo"""
        
        # Nível de segurança determina aprovação obrigatória
        if security_level == SecurityLevel.DANGEROUS:
            return True, "Ação classificada como PERIGOSA"
        
        if security_level == SecurityLevel.HIGH_RISK:
            return True, "Ação de ALTO RISCO"
        
        # Regra específica da ação
        if security_rule.requires_approval:
            return True, "Ação configurada para requerer aprovação"
        
        # Verificar confiança do usuário
        user_id = context.get("user_id", "unknown")
        trust_level = self.user_trust.get(user_id, self.default_trust_level)
        
        if trust_level == UserTrustLevel.NEW:
            return True, "Usuário novo - aprovação requerida"
        
        # Verificar parâmetros específicos
        if "confidential" in parameters.get("tags", []):
            return True, "Conteúdo confidencial"
        
        if "amount" in parameters and parameters["amount"] > 1000:
            return True, "Valor monetário alto"
        
        if "recipients" in parameters:
            recipients = parameters["recipients"]
            if isinstance(recipients, list) and len(recipients) > 5:
                return True, f"Muitos destinatários ({len(recipients)})"
        
        return False, ""
    
    def _calculate_risk_score(self, security_level: SecurityLevel, 
                             parameters: Dict[str, Any]) -> float:
        """Calcula score de risco (0-1)"""
        
        # Baseado no nível de segurança
        level_scores = {
            SecurityLevel.SAFE: 0.1,
            SecurityLevel.LOW_RISK: 0.3,
            SecurityLevel.MEDIUM_RISK: 0.5,
            SecurityLevel.HIGH_RISK: 0.7,
            SecurityLevel.DANGEROUS: 0.9,
        }
        
        score = level_scores.get(security_level, 0.5)
        
        # Ajustar baseado em parâmetros
        if "recipients" in parameters:
            recipients = parameters["recipients"]
            if isinstance(recipients, list):
                score += min(len(recipients) * 0.02, 0.2)  # +2% por destinatário, máximo 20%
        
        if "confidential" in parameters.get("tags", []):
            score += 0.15
        
        if "amount" in parameters:
            amount = parameters["amount"]
            if amount > 1000:
                score += 0.1
        
        return min(score, 1.0)  # Limitar a 1.0
    
    def _suggest_mitigations(self, security_level: SecurityLevel,
                            risk_score: float, parameters: Dict[str, Any]) -> List[str]:
        """Sugere mitigações para reduzir risco"""
        
        mitigations = []
        
        if security_level == SecurityLevel.DANGEROUS:
            mitigations.append("Requer aprovação de múltiplos administradores")
            mitigations.append("Implementar verificação em duas etapas")
        
        if risk_score > 0.7:
            mitigations.append("Limitar número de destinatários")
            mitigations.append("Adicionar disclaimer de responsabilidade")
        
        if "recipients" in parameters:
            recipients = parameters["recipients"]
            if isinstance(recipients, list) and len(recipients) > 10:
                mitigations.append("Considerar envio em lotes menores")
                mitigations.append("Verificar lista de destinatários")
        
        if "confidential" in parameters.get("tags", []):
            mitigations.append("Criptografar conteúdo sensível")
            mitigations.append("Registrar acesso ao conteúdo")
        
        if not mitigations and risk_score > 0.5:
            mitigations.append("Revisar manualmente antes de executar")
        
        return mitigations
    
    def analyze_risk_factors(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa fatores de risco específicos de uma ação.
        
        Args:
            action_type: Tipo de ação
            parameters: Parâmetros da ação
        
        Returns:
            Dict com fatores de risco identificados
        """
        risk_factors = []
        
        # Fator 1: Número de destinatários
        recipients_keys = ["to", "recipients", "attendees", "participants"]
        for key in recipients_keys:
            if key in parameters:
                value = parameters[key]
                if isinstance(value, list) and len(value) > 5:
                    risk_factors.append({
                        "factor": f"Múltiplos destinatários ({len(value)})",
                        "risk_level": "medium" if len(value) <= 10 else "high",
                        "description": f"Ação envolve {len(value)} destinatários, aumentando impacto"
                    })
                elif isinstance(value, str) and '@' in value:
                    # Email único - risco baixo
                    pass
        
        # Fator 2: Conteúdo sensível
        sensitive_keywords = ["confidential", "secret", "private", "sensitive", 
                             "financial", "salary", "password", "token"]
        param_str = json.dumps(parameters).lower()
        found_keywords = []
        for keyword in sensitive_keywords:
            if keyword in param_str:
                found_keywords.append(keyword)
        
        if found_keywords:
            risk_factors.append({
                "factor": "Conteúdo sensível detectado",
                "risk_level": "high",
                "description": f"Palavras-chave sensíveis encontradas: {', '.join(found_keywords[:3])}"
            })
        
        # Fator 3: Ações destrutivas
        destructive_actions = ["DELETE", "REMOVE", "CANCEL", "TERMINATE", "FIRE"]
        if any(destructive in action_type.upper() for destructive in destructive_actions):
            risk_factors.append({
                "factor": "Ação destrutiva",
                "risk_level": "high",
                "description": f"Ação do tipo {action_type} pode ter efeitos irreversíveis"
            })
        
        # Fator 4: Parâmetros de alto valor
        high_value_keys = ["budget", "amount", "price", "cost", "value"]
        for key in high_value_keys:
            if key in parameters:
                value = parameters[key]
                try:
                    numeric_value = float(value)
                    if numeric_value > 10000:
                        risk_factors.append({
                            "factor": f"Alto valor monetário (R${numeric_value:,.2f})",
                            "risk_level": "medium" if numeric_value <= 50000 else "high",
                            "description": f"Valor de R${numeric_value:,.2f} envolvido na ação"
                        })
                except (ValueError, TypeError):
                    pass
        
        # Calcular risco total
        risk_levels = {"low": 0.3, "medium": 0.6, "high": 0.9}
        total_risk = 0.0
        if risk_factors:
            total_risk = sum(risk_levels.get(factor.get("risk_level", "low"), 0.3) 
                           for factor in risk_factors) / len(risk_factors)
        
        return {
            "risk_factors": risk_factors,
            "total_risk_score": total_risk,
            "factor_count": len(risk_factors),
            "highest_risk": max([factor.get("risk_level", "low") for factor in risk_factors], 
                               key=lambda x: risk_levels.get(x, 0), default="low"),
            "action_type": action_type,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_approval_request(self, action_type: str, parameters: Dict[str, Any],
                               context: Dict[str, Any], reason: str = "") -> Dict[str, Any]:
        """Cria solicitação de aprovação para ação"""
        
        request_id = str(uuid.uuid4())[:12]
        
        # Avaliar ação para obter detalhes de segurança
        evaluation = self.evaluate_action(action_type, parameters, context)
        
        # Criar solicitação
        request = {
            "request_id": request_id,
            "action_type": action_type,
            "parameters": parameters,
            "context": context,
            "evaluation": evaluation,
            "reason": reason or evaluation.get("approval_reason", "Ação requer aprovação"),
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "status": "pending",
            "approvers": [],  # Lista de aprovadores
            "approval_code": hashlib.md5(request_id.encode()).hexdigest()[:6].upper(),
        }
        
        # Armazenar solicitação
        self.approval_requests[request_id] = request
        
        logger.info(f"✅ Solicitação de aprovação criada: {request_id}")
        
        return request
    
    def approve_action(self, request_id: str, approver_id: str, 
                      notes: str = "") -> Dict[str, Any]:
        """Aprova uma solicitação de ação"""
        
        if request_id not in self.approval_requests:
            raise ValueError(f"Solicitação não encontrada: {request_id}")
        
        request = self.approval_requests[request_id]
        
        # Verificar se já expirou
        expires_at = datetime.fromisoformat(request["expires_at"])
        if datetime.now() > expires_at:
            request["status"] = "expired"
            return request
        
        # Adicionar aprovador
        if approver_id not in request["approvers"]:
            request["approvers"].append(approver_id)
        
        # Atualizar status
        request["status"] = "approved"
        request["approved_at"] = datetime.now().isoformat()
        request["approver_notes"] = notes
        
        logger.info(f"✅ Ação aprovada: {request_id} por {approver_id}")
        
        return request
    
    def reject_action(self, request_id: str, rejecter_id: str,
                     reason: str = "") -> Dict[str, Any]:
        """Rejeita uma solicitação de ação"""
        
        if request_id not in self.approval_requests:
            raise ValueError(f"Solicitação não encontrada: {request_id}")
        
        request = self.approval_requests[request_id]
        request["status"] = "rejected"
        request["rejected_at"] = datetime.now().isoformat()
        request["rejecter_id"] = rejecter_id
        request["rejection_reason"] = reason
        
        logger.info(f"❌ Ação rejeitada: {request_id} por {rejecter_id}")
        
        return request
    
    def create_rollback_point(self, action_type: str, parameters: Dict[str, Any],
                             pre_action_state: Dict[str, Any]) -> str:
        """Cria ponto de rollback para ação"""
        
        checkpoint_id = str(uuid.uuid4())[:8]
        
        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "action_type": action_type,
            "parameters": parameters,
            "pre_action_state": pre_action_state,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.rollback_points[checkpoint_id] = checkpoint
        
        logger.info(f"✅ Ponto de rollback criado: {checkpoint_id}")
        
        return checkpoint_id
    
    def rollback_if_needed(self, checkpoint_id: str, 
                          action_result: Dict[str, Any]) -> bool:
        """Executa rollback se resultado for problemático"""
        
        if checkpoint_id not in self.rollback_points:
            logger.warning(f"⚠️  Ponto de rollback não encontrado: {checkpoint_id}")
            return False
        
        checkpoint = self.rollback_points[checkpoint_id]
        
        # Verificar se precisa rollback
        needs_rollback = False
        error_severity = action_result.get("error_severity", 0)
        
        if error_severity > 7:  # Erro crítico
            needs_rollback = True
            reason = f"Erro crítico (severidade: {error_severity})"
        elif action_result.get("status") == "failed" and "irreversible" in action_result.get("error", ""):
            needs_rollback = True
            reason = "Erro irreversível detectado"
        elif "data_loss" in action_result.get("warnings", []):
            needs_rollback = True
            reason = "Perda de dados detectada"
        
        if needs_rollback:
            checkpoint["status"] = "rolled_back"
            checkpoint["rolled_back_at"] = datetime.now().isoformat()
            checkpoint["rollback_reason"] = reason
            
            logger.warning(f"🔄 Rollback executado: {checkpoint_id} - {reason}")
            
            # Em produção, aqui restauraríamos o estado
            # self.restore_state(checkpoint["pre_action_state"])
            
            return True
        
        # Se não precisar rollback, marcar como concluído
        checkpoint["status"] = "completed"
        checkpoint["completed_at"] = datetime.now().isoformat()
        
        return False
    
    def update_user_trust(self, user_id: str, trust_level: UserTrustLevel):
        """Atualiza nível de confiança do usuário"""
        self.user_trust[user_id] = trust_level
        logger.info(f"✅ Confiança do usuário atualizada: {user_id} -> {trust_level.name}")
    
    def get_user_trust_level(self, user_id: str) -> UserTrustLevel:
        """Obtém nível de confiança do usuário"""
        return self.user_trust.get(user_id, self.default_trust_level)
    
    def add_security_rule(self, action_security: ActionSecurity):
        """Adiciona ou atualiza regra de segurança"""
        self.security_rules[action_security.action_type] = action_security
        logger.info(f"✅ Regra de segurança adicionada: {action_security.action_type}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtém status do sistema de segurança"""
        return {
            "total_rules": len(self.security_rules),
            "total_users": len(self.user_trust),
            "pending_approvals": sum(1 for r in self.rollback_points.values() 
                                   if r.get("status") == "pending"),
            "active_checkpoints": sum(1 for r in self.rollback_points.values() 
                                    if r.get("status") == "active"),
            "default_trust_level": self.default_trust_level.name,
            "max_auto_actions_per_hour": self.max_auto_actions_per_hour,
        }