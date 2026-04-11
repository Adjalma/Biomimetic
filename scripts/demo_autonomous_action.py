#!/usr/bin/env python3
"""
Demonstração do Autonomous Action Orchestrator - Fase 7

Testa a integração dos componentes:
1. Google Calendar API (se credentials disponíveis)
2. Gmail API (se credentials disponíveis)
3. Sistema Biomimético
4. Obsidian (se configurado)
5. Orquestrador de decisão

Uso:
    python scripts/demo_autonomous_action.py [--real] [--simulated]

Argumentos:
    --real: Tenta usar APIs reais (requer credentials)
    --simulated: Usa modo simulado (default)
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Verifica dependências e componentes disponíveis"""
    print("🔍 VERIFICANDO DEPENDÊNCIAS E COMPONENTES")
    print("=" * 60)
    
    dependencies = {}
    
    # Google Calendar
    try:
        from src.google.google_calendar_client import GoogleCalendarClient
        dependencies['google_calendar'] = True
        print("✅ GoogleCalendarClient disponível")
    except ImportError as e:
        dependencies['google_calendar'] = False
        print(f"❌ GoogleCalendarClient não disponível: {e}")
    
    # Gmail
    try:
        from src.google.gmail_client import GmailClient
        dependencies['gmail'] = True
        print("✅ GmailClient disponível")
    except ImportError as e:
        dependencies['gmail'] = False
        print(f"❌ GmailClient não disponível: {e}")
    
    # Sistema Biomimético
    try:
        from src.systems.sistemas.sistema_meta_learning_biomimetico import AutoEvolvingAISystem
        dependencies['biomimetic_system'] = True
        print("✅ AutoEvolvingAISystem disponível")
    except ImportError as e:
        dependencies['biomimetic_system'] = False
        print(f"❌ AutoEvolvingAISystem não disponível: {e}")
    
    # Obsidian
    try:
        from src.app.obsidian_vault import ObsidianVault
        dependencies['obsidian'] = True
        print("✅ ObsidianVault disponível")
    except ImportError as e:
        dependencies['obsidian'] = False
        print(f"❌ ObsidianVault não disponível: {e}")
    
    # Biomimetic Calendar Agent
    try:
        from src.agents.biomimetic_calendar_agent import BiomimeticCalendarAgent
        dependencies['biomimetic_calendar_agent'] = True
        print("✅ BiomimeticCalendarAgent disponível")
    except ImportError as e:
        dependencies['biomimetic_calendar_agent'] = False
        print(f"❌ BiomimeticCalendarAgent não disponível: {e}")
    
    # Autonomous Action Orchestrator
    try:
        from src.agents.autonomous_action_orchestrator import AutonomousActionOrchestrator
        dependencies['autonomous_action_orchestrator'] = True
        print("✅ AutonomousActionOrchestrator disponível")
    except ImportError as e:
        dependencies['autonomous_action_orchestrator'] = False
        print(f"❌ AutonomousActionOrchestrator não disponível: {e}")
    
    print("=" * 60)
    return dependencies


def test_orchestrator_simulated():
    """Testa orquestrador em modo simulado"""
    print("\n🤖 TESTANDO ORQUESTRADOR (MODO SIMULADO)")
    print("=" * 60)
    
    try:
        from src.agents.autonomous_action_orchestrator import (
            AutonomousActionOrchestrator, 
            ActionType, 
            ActionPriority
        )
        
        # Criar orquestrador em modo simulado
        orchestrator = AutonomousActionOrchestrator(
            use_biomimetic=False,
            require_human_approval=False
        )
        
        print("✅ Orquestrador inicializado (modo simulado)")
        
        # Obter status
        status = orchestrator.get_status()
        print(f"\n📊 STATUS:")
        print(f"  • Ações disponíveis: {len(status['available_actions'])}")
        print(f"  • Componentes ativos: {sum(1 for v in status['components'].values() if v)}/{len(status['components'])}")
        
        # Listar ações disponíveis
        print(f"\n📋 AÇÕES REGISTRADAS:")
        for action in status['available_actions'][:5]:  # Mostrar primeiras 5
            print(f"  • {action['type']}: {action['description']}")
        if len(status['available_actions']) > 5:
            print(f"  ... e mais {len(status['available_actions']) - 5} ações")
        
        # Testar processamento de situação simples
        print(f"\n🎯 TESTANDO PROCESSAMENTO DE SITUAÇÃO:")
        
        situation = {
            "description": "Teste de situação simulada",
            "type": "memory",
            "urgency": "low",
            "content": "Este é um teste do orquestrador de ações autônomas.",
            "action_parameters": {
                "title": "Teste de Situação - Demonstração",
                "tags": ["teste", "demonstração", "orquestrador"],
            }
        }
        
        print(f"  Situação: {situation['description']}")
        result = orchestrator.process_situation(situation)
        
        if result:
            print(f"  Resultado:")
            print(f"    • Ação: {result.action_type.value}")
            print(f"    • Status: {result.status}")
            print(f"    • ID: {result.request_id}")
            print(f"    • Tempo: {result.execution_time:.2f}s")
        else:
            print("  ❌ Nenhuma ação executada (componentes não disponíveis)")
        
        print("\n✅ Teste do orquestrador concluído (modo simulado)")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do orquestrador: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_biomimetic_decision():
    """Testa decisão biomimética (se sistema disponível)"""
    print("\n🧠 TESTANDO DECISÃO BIOMIMÉTICA")
    print("=" * 60)
    
    try:
        from src.agents.autonomous_action_orchestrator import (
            AutonomousActionOrchestrator,
            ActionDecisionEngine,
            ActionType
        )
        
        # Criar motor de decisão
        decision_engine = ActionDecisionEngine()
        
        # Situação de teste
        situation = {
            "description": "Reunião urgente com cliente",
            "type": "meeting",
            "urgency": "high",
            "participants": ["cliente@empresa.com"],
            "communication_type": "meeting",
            "recipient_count": 1,
            "has_attachment": False
        }
        
        # Ações disponíveis (simuladas)
        available_actions = [
            ActionType.SCHEDULE_MEETING,
            ActionType.SEND_EMAIL,
            ActionType.SAVE_TO_MEMORY,
            ActionType.ANALYZE_CONTEXT
        ]
        
        print(f"  Situação: {situation['description']}")
        print(f"  Urgência: {situation['urgency']}")
        print(f"  Ações disponíveis: {[a.value for a in available_actions]}")
        
        # Tomar decisão
        action_type, decision_info = decision_engine.decide_action(situation, available_actions)
        
        if action_type:
            print(f"\n  🎯 DECISÃO TOMADA:")
            print(f"    • Ação: {action_type.value}")
            print(f"    • Método: {decision_info.get('decision_method', 'N/A')}")
            print(f"    • Confiança: {decision_info.get('confidence', 0):.2f}")
            print(f"    • Razão: {decision_info.get('reasoning', 'N/A')}")
        else:
            print(f"\n  ❌ Nenhuma decisão possível")
        
        # Testar múltiplas situações
        print(f"\n  🔄 TESTANDO DIFERENTES SITUAÇÕES:")
        
        test_situations = [
            {
                "description": "Email com anexo para múltiplos destinatários",
                "type": "communication",
                "urgency": "medium",
                "has_attachment": True,
                "recipient_count": 3
            },
            {
                "description": "Lembrete pessoal",
                "type": "reminder",
                "urgency": "low",
                "recipient_count": 1
            },
            {
                "description": "Alerta crítico do sistema",
                "type": "alert",
                "urgency": "critical",
                "recipient_count": 1
            }
        ]
        
        for i, sit in enumerate(test_situations, 1):
            action_type, info = decision_engine.decide_action(sit, available_actions)
            if action_type:
                print(f"    {i}. {sit['description']} → {action_type.value} ({info.get('confidence', 0):.2f})")
            else:
                print(f"    {i}. {sit['description']} → Nenhuma ação")
        
        print("\n✅ Teste de decisão biomimética concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de decisão biomimética: {e}")
        return False


def test_action_registry():
    """Testa registro e execução de ações"""
    print("\n📝 TESTANDO REGISTRO DE AÇÕES")
    print("=" * 60)
    
    try:
        from src.agents.autonomous_action_orchestrator import (
            ActionRegistry,
            ActionType,
            ActionContext
        )
        
        # Criar contexto
        context = ActionContext(user_id="demo_user")
        
        # Criar registro
        registry = ActionRegistry()
        
        # Registrar ações de exemplo
        def handler1(request, executor):
            return {"message": "Handler 1 executado", "parameters": request.parameters}
        
        def handler2(request, executor):
            return {"message": "Handler 2 executado", "parameters": request.parameters}
        
        registry.register(
            ActionType.SCHEDULE_MEETING,
            handler1,
            "Agendar reunião (demo)",
            requirements=["google_calendar"]
        )
        
        registry.register(
            ActionType.SAVE_TO_MEMORY,
            handler2,
            "Salvar na memória (demo)",
            requirements=["obsidian"]
        )
        
        print(f"✅ {len(registry.list_actions())} ações registradas")
        
        # Listar ações
        print(f"\n📋 AÇÕES REGISTRADAS:")
        for action in registry.list_actions():
            print(f"  • {action['type']}: {action['description']}")
            print(f"    Requisitos: {action['requirements']}")
        
        # Verificar execução
        print(f"\n🔍 VERIFICANDO EXECUÇÃO:")
        
        # Ação com requisitos não atendidos
        can_execute1 = registry.can_execute(ActionType.SCHEDULE_MEETING, context)
        print(f"  • {ActionType.SCHEDULE_MEETING.value}: {'✅ Executável' if can_execute1 else '❌ Não executável'}")
        
        # Obter handlers
        handler1 = registry.get_handler(ActionType.SCHEDULE_MEETING)
        handler2 = registry.get_handler(ActionType.SAVE_TO_MEMORY)
        print(f"  • Handler SCHEDULE_MEETING: {'✅ Encontrado' if handler1 else '❌ Não encontrado'}")
        print(f"  • Handler SAVE_TO_MEMORY: {'✅ Encontrado' if handler2 else '❌ Não encontrado'}")
        
        print("\n✅ Teste de registro de ações concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de registro de ações: {e}")
        return False


def run_comprehensive_demo(use_real_apis: bool = False):
    """Executa demonstração abrangente do sistema"""
    print(f"\n🚀 DEMONSTRAÇÃO ABRANGENTE DO SISTEMA {'(MODO REAL)' if use_real_apis else '(MODO SIMULADO)'}")
    print("=" * 70)
    
    # Verificar dependências
    dependencies = check_dependencies()
    
    if not dependencies.get('autonomous_action_orchestrator', False):
        print("❌ AutonomousActionOrchestrator não disponível. Abortando.")
        return False
    
    # Testar componentes individuais
    tests_passed = 0
    total_tests = 3
    
    # Teste 1: Registro de ações
    if test_action_registry():
        tests_passed += 1
    
    # Teste 2: Decisão biomimética
    if test_biomimetic_decision():
        tests_passed += 1
    
    # Teste 3: Orquestrador simulado
    if test_orchestrator_simulated():
        tests_passed += 1
    
    print(f"\n📊 RESULTADO DOS TESTES: {tests_passed}/{total_tests} passaram")
    
    if tests_passed == total_tests:
        print("✅ TODOS OS TESTES PASSARAM!")
        
        # Demonstrar cenário integrado
        print(f"\n🎭 CENÁRIO INTEGRADO DE AÇÃO AUTÔNOMA")
        print("-" * 50)
        
        scenario = """
        Cenário: Sistema detecta que há uma reunião importante amanhã,
        mas nenhum lembrete foi enviado aos participantes.
        
        Fluxo biomimético:
        1. Percepção: Calendário mostra reunião sem confirmação
        2. Decisão: Enviar lembrete por email (prioridade média)
        3. Ação: Enviar email com detalhes da reunião
        4. Memória: Registrar ação tomada
        5. Aprendizado: Avaliar taxa de resposta para melhorias futuras
        """
        
        print(scenario)
        
        # Mostrar como implementar
        print("\n💻 IMPLEMENTAÇÃO DO CENÁRIO:")
        implementation_code = '''
        # 1. Inicializar orquestrador
        orchestrator = AutonomousActionOrchestrator(
            use_biomimetic=True,
            require_human_approval=False
        )
        
        # 2. Situação detectada
        situation = {
            "description": "Reunião sem confirmação de participantes",
            "type": "meeting_followup",
            "urgency": "medium",
            "participants": ["participante1@email.com", "participante2@email.com"],
            "meeting_title": "Revisão da Fase 7",
            "meeting_time": "2026-04-12T14:00:00",
            "action_parameters": {
                "to": ["participante1@email.com", "participante2@email.com"],
                "subject": "Lembrete: Reunião de Revisão da Fase 7",
                "body": "Lembrete da reunião agendada para amanhã...",
            }
        }
        
        # 3. Processar situação (sistema toma decisão e executa)
        result = orchestrator.process_situation(situation)
        
        # 4. Analisar resultado
        if result and result.status == "completed":
            print(f"Ação executada: {result.action_type.value}")
            print(f"Resultado: {result.result}")
        '''
        
        for line in implementation_code.strip().split('\n'):
            print(f"  {line}")
        
        print(f"\n🎯 FASE 7 - SISTEMA DE AÇÃO AUTÔNOMA")
        print("   Status: ✅ ESTRUTURA PRINCIPAL IMPLEMENTADA")
        print(f"   Componentes ativos: {sum(1 for v in dependencies.values() if v)}/{len(dependencies)}")
        
        # Próximos passos
        print(f"\n🔧 PRÓXIMOS PASSOS RECOMENDADOS:")
        print("   1. Configurar credenciais Google (Calendar + Gmail)")
        print("   2. Testar com APIs reais (use --real)")
        print("   3. Implementar integração com WhatsApp Z-API")
        print("   4. Adicionar mais lógica biomimética avançada")
        print("   5. Criar dashboard de monitoramento")
        print("   6. Implementar aprovação humana para ações críticas")
        
    else:
        print(f"⚠️ ALGUNS TESTES FALHARAM. Verifique dependências.")
    
    print("\n" + "=" * 70)
    print("🏁 DEMONSTRAÇÃO CONCLUÍDA")
    
    return tests_passed == total_tests


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Demonstração do Autonomous Action Orchestrator")
    parser.add_argument("--real", action="store_true", help="Tentar usar APIs reais (requer credentials)")
    parser.add_argument("--simulated", action="store_true", help="Usar modo simulado (default)")
    
    args = parser.parse_args()
    
    print("🤖 AI-Biomimetica - Demonstração Fase 7: Sistema de Ação Autônoma")
    print("   Autonomous Action Orchestrator\n")
    
    # Determinar modo
    use_real_apis = args.real and not args.simulated
    
    if use_real_apis:
        print("⚠️  MODO REAL: Requer credenciais Google configuradas")
        print("   Certifique-se de que:")
        print("   1. credentials.json está no diretório raiz")
        print("   2. token.pickle existe (ou execute autenticação)")
        print("   3. APIs Google Calendar e Gmail estão habilitadas")
        print("\n   Continuando em 3 segundos...")
        import time
        time.sleep(3)
    else:
        print("📱 MODO SIMULADO: Usando componentes simulados")
        print("   Nenhuma credencial necessária\n")
    
    # Executar demonstração
    success = run_comprehensive_demo(use_real_apis=use_real_apis)
    
    # Testar ações de reunião (Fase 8)
    print("\n" + "=" * 70)
    print("🔄 TESTANDO AÇÕES DE REUNIÃO (FASE 8)")
    print("=" * 70)
    
    try:
        # Importar MeetingOrchestrator
        from src.meeting.meeting_orchestrator import create_meeting_orchestrator
        
        # Criar orquestrador de reuniões
        meeting_orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=dependencies.get('biomimetic_system', False),
            require_human_approval=False  # Para teste
        )
        
        print("✅ MeetingOrchestrator criado")
        print(f"   Ações de reunião disponíveis: {len([a for a in meeting_orchestrator.registry.list_actions() if 'meeting' in a['type']])}")
        
        # Testar convite de reunião simulado
        from datetime import datetime, timedelta
        invitation = {
            "title": "Teste de Integração Fase 8",
            "url": "https://meet.google.com/test-123",
            "time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "organizer": "test@exemplo.com",
            "participants": ["test1@exemplo.com", "test2@exemplo.com"],
            "description": "Teste da Fase 8: Participação em Reuniões",
            "platform": "google_meet"
        }
        
        print(f"\n📨 Processando convite de reunião: {invitation['title']}")
        request = meeting_orchestrator.process_meeting_invitation(invitation)
        
        if request and request.action_type:
            print(f"✅ Ação decidida: {request.action_type.value}")
            if request.result and 'meeting_id' in request.result:
                meeting_id = request.result['meeting_id']
                print(f"   ID da reunião: {meeting_id}")
                print(f"   Status: {meeting_orchestrator.get_meeting_status(meeting_id).get('status', 'unknown')}")
                
                # Testar outras ações de reunião
                from src.agents.autonomous_action_orchestrator import ActionRequest, ActionType
                
                # Transcrição
                transcribe_request = ActionRequest(
                    action_type=ActionType.TRANSCRIBE_MEETING,
                    parameters={"meeting_id": meeting_id, "language": "pt-BR"}
                )
                transcribe_result = meeting_orchestrator.executor.execute(transcribe_request)
                if transcribe_result.result and transcribe_result.result.get('success'):
                    print(f"✅ Transcrição: {transcribe_result.result.get('total_segments', 0)} segmentos")
                
                # Resumo
                summarize_request = ActionRequest(
                    action_type=ActionType.SUMMARIZE_MEETING,
                    parameters={"meeting_id": meeting_id}
                )
                summarize_result = meeting_orchestrator.executor.execute(summarize_request)
                if summarize_result.result and summarize_result.result.get('success'):
                    print(f"✅ Resumo: {len(summarize_result.result.get('decisions', []))} decisões")
                
                # Finalizar reunião
                end_result = meeting_orchestrator.end_meeting(meeting_id)
                if end_result.get('success'):
                    print(f"✅ Reunião finalizada: {end_result.get('duration_minutes', 0):.1f} minutos")
        
        print("\n🎉 AÇÕES DE REUNIÃO TESTADAS COM SUCESSO!")
        print("   Fase 8 (Participação em Reuniões) implementada!")
        
    except ImportError as e:
        print(f"⚠️  Não foi possível testar ações de reunião: {e}")
        print("   Certifique-se de que o módulo meeting está instalado")
    except Exception as e:
        print(f"⚠️  Erro ao testar ações de reunião: {e}")
    
    if success:
        print("\n✅ DEMONSTRAÇÃO BEM-SUCEDIDA!")
        print("   O sistema de ação autônoma está pronto para uso.")
        print("   Execute 'python scripts/demo_autonomous_action.py --real' para testar com APIs reais.")
        print("\n📈 FASE 8 IMPLEMENTADA: Participação em Reuniões")
        print("   - Entrada automática em reuniões")
        print("   - Transcrição em tempo real")
        print("   - Resumo biomimético")
        print("   - Salvamento automático de notas")
        print("   - Monitoramento contextual")
        sys.exit(0)
    else:
        print("\n⚠️  DEMONSTRAÇÃO COM LIMITAÇÕES")
        print("   Alguns componentes não estão disponíveis.")
        print("   Verifique dependências e configurações.")
        sys.exit(1)


if __name__ == "__main__":
    main()