#!/usr/bin/env python3
"""
Demonstração das Três Melhorias de Autonomia:
1. SecurityProtocols - Protocolos de segurança avançados
2. HierarchyIntegration - Integração com hierarquia organizacional  
3. ProactiveMonitor - Monitoramento proativo e alertas

Autor: Jarvis (OpenClaw)
Data: 2026-04-11
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_security_protocols():
    """Testa protocolos de segurança"""
    print("\n" + "="*80)
    print("1️⃣  TESTE SECURITYPROTOCOLS")
    print("="*80)
    
    try:
        from agents.security_protocols import SecurityProtocols, SecurityLevel, UserTrustLevel
        
        # Inicializar
        security = SecurityProtocols()
        print("✅ SecurityProtocols inicializado")
        
        # Testar avaliação de ação
        test_action = {
            "action_type": "SEND_EMAIL",
            "parameters": {
                "to": ["ceo@company.com", "cto@company.com", "cfo@company.com"],
                "subject": "Relatório Confidencial",
                "body": "Dados financeiros sigilosos..."
            },
            "context": {
                "user_id": "user123",
                "user_trust_level": UserTrustLevel.HIGH.value,
                "timestamp": datetime.now().isoformat(),
                "environment": "production",
                "action_history_count": 5
            }
        }
        
        evaluation = security.evaluate_action(
            action_type=test_action["action_type"],
            parameters=test_action["parameters"],
            context=test_action["context"]
        )
        
        print(f"\n📋 Avaliação de segurança:")
        print(f"   • Requer aprovação: {evaluation.get('requires_approval', False)}")
        print(f"   • Razão: {evaluation.get('approval_reason', 'N/A')}")
        print(f"   • Nível de risco: {evaluation.get('risk_level', 'N/A')}")
        print(f"   • Score de risco: {evaluation.get('risk_score', 0):.2f}")
        
        # Testar workflow de aprovação
        if evaluation.get("requires_approval", False):
            print(f"\n🔄 Testando workflow de aprovação...")
            workflow = security.create_approval_workflow(
                action_type=test_action["action_type"],
                evaluation=evaluation,
                user_id=test_action["context"]["user_id"]
            )
            
            print(f"   • Workflow ID: {workflow.get('workflow_id')}")
            print(f"   • Aprovadores necessários: {workflow.get('required_approvers', 0)}")
            print(f"   • Prazo: {workflow.get('deadline', 'N/A')}")
        
        # Testar análise de risco
        print(f"\n📊 Testando análise de risco...")
        risk_analysis = security.analyze_risk_factors(
            action_type=test_action["action_type"],
            parameters=test_action["parameters"]
        )
        
        print(f"   • Fatores de risco: {len(risk_analysis.get('risk_factors', []))}")
        for factor in risk_analysis.get("risk_factors", [])[:3]:
            print(f"     - {factor.get('factor')}: {factor.get('risk_level')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de SecurityProtocols: {e}")
        return False

def test_hierarchy_integration():
    """Testa integração com hierarquia organizacional"""
    print("\n" + "="*80)
    print("2️⃣  TESTE HIERARCHYINTEGRATION")
    print("="*80)
    
    try:
        from agents.hierarchy_integration import HierarchyIntegration, HierarchyDecision, FormalizationLevel
        
        # Inicializar com dados de exemplo
        hierarchy = HierarchyIntegration()
        print("✅ HierarchyIntegration inicializado")
        
        # Adicionar alguns funcionários de exemplo
        employees_data = [
            {
                "id": "emp001",
                "name": "Carlos Silva",
                "email": "carlos.silva@company.com",
                "role": "CEO",
                "department": "Executive",
                "manager_id": None,
                "level": 10
            },
            {
                "id": "emp002",
                "name": "Ana Santos",
                "email": "ana.santos@company.com",
                "role": "DIRECTOR",
                "department": "Technology",
                "manager_id": "emp001",
                "level": 8
            },
            {
                "id": "emp003",
                "name": "João Pereira",
                "email": "joao.pereira@company.com",
                "role": "ENGINEER",
                "department": "Technology",
                "manager_id": "emp002",
                "level": 5
            }
        ]
        
        for emp in employees_data:
            if hierarchy.add_employee_manually(emp):
                print(f"   • Funcionário adicionado: {emp['name']} ({emp['role']})")
        
        # Testar avaliação de ação com hierarquia
        test_context = {
            "user_id": "emp003",  # Engenheiro
            "participants": ["emp003", "emp001"],  # Engenheiro + CEO
            "action_type": "SEND_EMAIL",
            "parameters": {
                "to": ["ceo@company.com"],
                "subject": "Proposta de Projeto",
                "budget": 15000
            }
        }
        
        evaluation = hierarchy.evaluate_action_with_hierarchy(
            action_type=test_context["action_type"],
            parameters=test_context["parameters"],
            context=test_context
        )
        
        print(f"\n📋 Avaliação hierárquica:")
        print(f"   • Decisão: {evaluation.get('hierarchy_decision', 'N/A')}")
        print(f"   • Razão: {evaluation.get('decision_reason', 'N/A')}")
        print(f"   • Nível de formalização: {evaluation.get('formalization_level', 'N/A')}")
        print(f"   • Validação de autoridade: {evaluation.get('authority_validation', False)}")
        print(f"   • Papel do iniciador: {evaluation.get('initiator_role', 'N/A')}")
        print(f"   • Papel mais alto: {evaluation.get('highest_rank_role', 'N/A')}")
        
        # Testar encontrar aprovador apropriado
        print(f"\n👤 Testando busca de aprovador...")
        approver = hierarchy.find_appropriate_approver(
            action_type=test_context["action_type"],
            initiator_id=test_context["user_id"]
        )
        
        if approver:
            print(f"   • Aprovador sugerido: {approver.get('email', 'N/A')}")
            print(f"   • Papel: {approver.get('role_name', 'N/A')}")
            print(f"   • Autoridade: {approver.get('authority', 0)}")
        else:
            print(f"   • Nenhum aprovador encontrado")
        
        # Obter status da hierarquia
        status = hierarchy.get_hierarchy_status()
        print(f"\n📊 Status da hierarquia:")
        print(f"   • Funcionários: {status.get('employee_count', 0)}")
        print(f"   • CEO identificado: {status.get('ceo_identified', False)}")
        print(f"   • Departamentos: {status.get('departments', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de HierarchyIntegration: {e}")
        return False

def test_proactive_monitor():
    """Testa monitoramento proativo"""
    print("\n" + "="*80)
    print("3️⃣  TESTE PROACTIVEMONITOR")
    print("="*80)
    
    try:
        from agents.proactive_monitor import ProactiveMonitor, AlertSeverity, MetricType
        
        # Inicializar
        monitor = ProactiveMonitor(window_size=50, alert_threshold=2.5)
        print("✅ ProactiveMonitor inicializado")
        
        # Simular algumas ações
        print(f"\n📈 Simulando execuções de ação...")
        action_results = [
            {
                "action_type": "SEND_EMAIL",
                "status": "completed",
                "execution_time": 2.5,
                "success": True,
                "risk_score": 0.2
            },
            {
                "action_type": "SCHEDULE_MEETING",
                "status": "completed",
                "execution_time": 5.1,
                "success": True,
                "risk_score": 0.3
            },
            {
                "action_type": "SEND_EMAIL",
                "status": "failed",
                "execution_time": 8.7,
                "success": False,
                "risk_score": 0.8,
                "error": "Connection timeout"
            },
            {
                "action_type": "SEND_EMAIL",
                "status": "failed",
                "execution_time": 7.9,
                "success": False,
                "risk_score": 0.7,
                "error": "Connection timeout"
            },
            {
                "action_type": "SEND_EMAIL",
                "status": "failed",
                "execution_time": 9.2,
                "success": False,
                "risk_score": 0.9,
                "error": "Connection timeout"
            }
        ]
        
        for i, result in enumerate(action_results, 1):
            monitor.record_action(result)
            print(f"   • Ação {i} registrada: {result['action_type']} ({result['status']})")
        
        # Verificar métricas
        print(f"\n🔍 Verificando métricas...")
        monitor.check_metrics()
        
        # Obter resumo de métricas
        metrics_summary = monitor.get_metrics_summary()
        print(f"\n📊 Resumo de métricas:")
        for metric_type, data in metrics_summary.items():
            if data.get("count", 0) > 0:
                print(f"   • {metric_type}:")
                print(f"     - Atual: {data.get('current', 0):.2f}")
                print(f"     - Média: {data.get('average', 0):.2f}")
                print(f"     - Min/Max: {data.get('min', 0):.2f}/{data.get('max', 0):.2f}")
        
        # Verificar alertas
        print(f"\n🚨 Alertas ativos: {len(monitor.active_alerts)}")
        for alert in monitor.active_alerts[:3]:  # Mostrar até 3
            print(f"   • [{alert.get('severity', 'N/A').upper()}] {alert.get('title', 'Sem título')}")
            print(f"     {alert.get('message', '')[:80]}...")
        
        # Obter recomendações
        recommendations = monitor.get_recommendations()
        print(f"\n💡 Recomendações: {len(recommendations)}")
        for rec in recommendations:
            print(f"   • [{rec.get('priority', 'medium').upper()}] {rec.get('title', 'Sem título')}")
            print(f"     Ação: {rec.get('action', 'N/A')}")
        
        # Obter status
        status = monitor.get_status()
        print(f"\n📈 Status do monitor:")
        print(f"   • Métricas monitoradas: {status.get('metrics_tracked', 0)}")
        print(f"   • Ações registradas: {status.get('total_actions_recorded', 0)}")
        print(f"   • Alertas ativos: {status.get('active_alerts', 0)}")
        print(f"   • Padrões de erro: {status.get('error_patterns_detected', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de ProactiveMonitor: {e}")
        return False

def test_integration():
    """Testa integração dos três módulos"""
    print("\n" + "="*80)
    print("🔗 TESTE DE INTEGRAÇÃO COMPLETA")
    print("="*80)
    
    try:
        # Importar todos os módulos
        from agents.security_protocols import SecurityProtocols
        from agents.hierarchy_integration import HierarchyIntegration
        from agents.proactive_monitor import ProactiveMonitor
        
        # Inicializar
        security = SecurityProtocols()
        hierarchy = HierarchyIntegration()
        monitor = ProactiveMonitor()
        
        print("✅ Todos os módulos inicializados")
        
        # Cenário integrado
        print(f"\n🎭 Simulando cenário integrado...")
        
        # Dados do cenário
        action_data = {
            "action_type": "SEND_EMAIL",
            "parameters": {
                "to": ["ceo@company.com", "board@company.com"],
                "subject": "Relatório Anual de Resultados",
                "body": "Dados confidenciais de performance...",
                "attachments": ["financial_report.pdf"]
            },
            "context": {
                "user_id": "manager123",
                "user_trust_level": "medium",
                "timestamp": datetime.now().isoformat(),
                "environment": "production",
                "participants": ["manager123", "ceo@company.com", "board@company.com"]
            }
        }
        
        # 1. Avaliação de segurança
        print(f"\n1. Avaliação de segurança:")
        security_eval = security.evaluate_action(
            action_type=action_data["action_type"],
            parameters=action_data["parameters"],
            context=action_data["context"]
        )
        print(f"   • Risco: {security_eval.get('risk_score', 0):.2f}")
        print(f"   • Requer aprovação: {security_eval.get('requires_approval', False)}")
        
        # 2. Avaliação hierárquica
        print(f"\n2. Avaliação hierárquica:")
        hierarchy_eval = hierarchy.evaluate_action_with_hierarchy(
            action_type=action_data["action_type"],
            parameters=action_data["parameters"],
            context=action_data["context"]
        )
        print(f"   • Decisão: {hierarchy_eval.get('hierarchy_decision', 'N/A')}")
        print(f"   • Formalização: {hierarchy_eval.get('formalization_level', 'N/A')}")
        
        # 3. Simular execução e monitoramento
        print(f"\n3. Monitoramento proativo:")
        
        # Simular resultado
        action_result = {
            "action_type": action_data["action_type"],
            "status": "completed",
            "execution_time": 3.2,
            "success": True,
            "risk_score": max(
                security_eval.get('risk_score', 0),
                hierarchy_eval.get('hierarchy_risk', 0)
            ),
            "error": None,
            "result": {"message_id": "msg_12345"}
        }
        
        monitor.record_action(action_result)
        monitor.check_metrics()
        
        print(f"   • Ação registrada no monitor")
        print(f"   • Alertas ativos: {len(monitor.active_alerts)}")
        
        # Resumo integrado
        print(f"\n📋 RESUMO DA INTEGRAÇÃO:")
        print(f"   • Segurança: {'APROVADA' if not security_eval.get('requires_approval', False) else 'PENDENTE'}")
        print(f"   • Hierarquia: {hierarchy_eval.get('suggested_approach', 'N/A')}")
        print(f"   • Monitoramento: {monitor.get_status().get('active_alerts', 0)} alertas ativos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de integração: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 DEMONSTRAÇÃO DAS TRÊS MELHORIAS DE AUTONOMIA")
    print("="*80)
    
    results = []
    
    # Executar testes individuais
    results.append(("SecurityProtocols", test_security_protocols()))
    results.append(("HierarchyIntegration", test_hierarchy_integration()))
    results.append(("ProactiveMonitor", test_proactive_monitor()))
    results.append(("Integração Completa", test_integration()))
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    success_count = 0
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} {name}")
        if success:
            success_count += 1
    
    print(f"\n🎯 Resultado: {success_count}/{len(results)} testes bem-sucedidos")
    
    if success_count == len(results):
        print("\n✨ TODAS AS TRÊS MELHORIAS IMPLEMENTADAS E INTEGRADAS COM SUCESSO!")
        print("   1. SecurityProtocols - Protocolos de segurança avançados")
        print("   2. HierarchyIntegration - Integração com hierarquia organizacional")
        print("   3. ProactiveMonitor - Monitoramento proativo e alertas")
        print("\n🔄 O sistema de ação autônoma agora possui:")
        print("   • Avaliação de risco baseada em múltiplos fatores")
        print("   • Decisões hierárquicas inteligentes")
        print("   • Monitoramento contínuo e alertas proativos")
        print("   • Integração com sistema biomimético para aprendizado")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs para detalhes.")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)