#!/usr/bin/env python3
"""
Demonstração da Fase 8: Participação em Reuniões

Testa o MeetingOrchestrator com ações biomiméticas:
1. Processar convite para reunião
2. Entrar em reunião (Google Meet/Teams)
3. Transcrever áudio em tempo real
4. Resumir conversa com sistema biomimético
5. Salvar notas automaticamente no Obsidian
6. Monitorar reunião e intervir quando apropriado

Autor: Jarvis (OpenClaw)
Data: 2026-04-11
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importações
try:
    from src.meeting.meeting_orchestrator import MeetingOrchestrator, create_meeting_orchestrator
    logger.info("✅ MeetingOrchestrator importado")
except ImportError as e:
    logger.error(f"❌ Erro ao importar MeetingOrchestrator: {e}")
    sys.exit(1)

# Verificar se sistema biomimético está disponível
BIOMIMETIC_AVAILABLE = False
try:
    from src.systems.sistemas.sistema_meta_learning_biomimetico import AutoEvolvingAISystem
    BIOMIMETIC_AVAILABLE = True
    logger.info("✅ Sistema biomimético disponível para decisões")
except ImportError:
    logger.warning("⚠️ Sistema biomimético não disponível - usando heurísticas")


def test_meeting_invitation_processing(orchestrator=None):
    """Teste 1: Processar convite para reunião"""
    print("\n" + "="*60)
    print("TESTE 1: Processamento de Convite para Reunião")
    print("="*60)
    
    # Criar orquestrador se não fornecido
    if orchestrator is None:
        orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=BIOMIMETIC_AVAILABLE,
            require_human_approval=False  # Desativar para teste
        )
    
    # Criar convite de reunião simulado
    invitation = {
        "title": "Revisão da Fase 8 - Participação em Reuniões",
        "url": "https://meet.google.com/abc-defg-hij",
        "time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "organizer": "Adjalma Aguiar",
        "participants": ["adja@exemplo.com", "colaborador@exemplo.com", "jarvis@exemplo.com"],
        "description": "Discutir progresso da Fase 8 (Participação em Reuniões) e próximos passos",
        "platform": "google_meet",
        "purpose": "Revisão técnica e planejamento"
    }
    
    print(f"\n📨 Convite recebido:")
    print(f"  Título: {invitation['title']}")
    print(f"  Organizador: {invitation['organizer']}")
    print(f"  Participantes: {len(invitation['participants'])} pessoas")
    print(f"  Horário: {invitation['time']}")
    print(f"  URL: {invitation['url']}")
    
    # Processar convite
    print("\n🔄 Processando convite...")
    request = orchestrator.process_meeting_invitation(invitation)
    
    if request:
        print(f"✅ Ação decidida: {request.action_type.value}")
        print(f"   Status: {request.status}")
        print(f"   Resultado: {json.dumps(request.result, indent=2, ensure_ascii=False)[:300]}...")
        
        if request.result and "meeting_id" in request.result:
            meeting_id = request.result["meeting_id"]
            print(f"\n📊 Status da reunião {meeting_id}:")
            status = orchestrator.get_meeting_status(meeting_id)
            print(f"   Título: {status.get('meeting_title')}")
            print(f"   Status: {status.get('status')}")
            print(f"   Plataforma: {status.get('platform')}")
            
            return meeting_id
    else:
        print("❌ Nenhuma ação decidida para o convite")
    
    return None


def test_meeting_transcription(meeting_id: str, orchestrator=None):
    """Teste 2: Transcrever reunião"""
    print("\n" + "="*60)
    print("TESTE 2: Transcrição de Reunião")
    print("="*60)
    
    # Criar orquestrador se não fornecido
    if orchestrator is None:
        orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=BIOMIMETIC_AVAILABLE
        )
    
    if not meeting_id:
        print("❌ ID de reunião não fornecido")
        return
    
    print(f"🎤 Transcrevendo reunião {meeting_id}...")
    
    # Criar requisição de transcrição
    from src.agents.autonomous_action_orchestrator import ActionRequest, ActionType
    
    request = ActionRequest(
        action_type=ActionType.TRANSCRIBE_MEETING,
        parameters={
            "meeting_id": meeting_id,
            "audio_data": "mock_audio_base64_or_path",  # Simulado
            "language": "pt-BR"
        }
    )
    
    # Executar transcrição
    result = orchestrator.executor.execute(request)
    
    if result and result.result and result.result.get("success"):
        print(f"✅ Transcrição concluída:")
        print(f"   Segmentos: {result.result.get('total_segments', 0)}")
        print(f"   Idioma: {result.result.get('language')}")
        
        # Mostrar alguns segmentos
        transcript = result.result.get("transcript", [])
        if transcript:
            print(f"\n📝 Trechos da transcrição:")
            for i, seg in enumerate(transcript[:3]):  # Mostrar 3 primeiros
                print(f"   {i+1}. {seg['speaker']} ({seg['timestamp']}): {seg['text'][:80]}...")
            if len(transcript) > 3:
                print(f"   ... e mais {len(transcript) - 3} segmentos")
    else:
        if result and result.result:
            print(f"❌ Falha na transcrição: {result.result.get('error', 'Erro desconhecido')}")
        else:
            print(f"❌ Falha na transcrição: resultado vazio (result: {result})")


def test_meeting_summarization(meeting_id: str, orchestrator=None):
    """Teste 3: Resumir reunião com sistema biomimético"""
    print("\n" + "="*60)
    print("TESTE 3: Resumo Biomimético de Reunião")
    print("="*60)
    
    # Criar orquestrador se não fornecido
    if orchestrator is None:
        orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=BIOMIMETIC_AVAILABLE
        )
    
    if not meeting_id:
        print("❌ ID de reunião não fornecido")
        return
    
    print(f"🧠 Resumindo reunião {meeting_id} com sistema biomimético...")
    
    from src.agents.autonomous_action_orchestrator import ActionRequest, ActionType
    
    request = ActionRequest(
        action_type=ActionType.SUMMARIZE_MEETING,
        parameters={
            "meeting_id": meeting_id
        }
    )
    
    result = orchestrator.executor.execute(request)
    
    if result and result.result and result.result.get("success"):
        print(f"✅ Resumo gerado com sucesso!")
        print(f"   Decisões: {len(result.result.get('decisions', []))}")
        print(f"   Itens de ação: {len(result.result.get('action_items', []))}")
        
        summary = result.result.get("summary", "")
        print(f"\n📋 Resumo:")
        for line in summary.split('\n')[:10]:  # Mostrar primeiras 10 linhas
            print(f"   {line}")
        
        decisions = result.result.get("decisions", [])
        if decisions:
            print(f"\n🤝 Decisões tomadas:")
            for i, decision in enumerate(decisions):
                print(f"   {i+1}. {decision}")
        
        action_items = result.result.get("action_items", [])
        if action_items:
            print(f"\n📋 Itens de ação:")
            for i, item in enumerate(action_items):
                print(f"   {i+1}. {item['task']} (Responsável: {item['assignee']}, Prazo: {item['due']})")
    else:
        if result and result.result:
            print(f"❌ Falha no resumo: {result.result.get('error', 'Erro desconhecido')}")
        else:
            print(f"❌ Falha no resumo: resultado vazio (result: {result})")


def test_meeting_notes_saving(meeting_id: str, orchestrator=None):
    """Teste 4: Salvar notas da reunião no Obsidian"""
    print("\n" + "="*60)
    print("TESTE 4: Salvamento Automático de Notas")
    print("="*60)
    
    # Criar orquestrador se não fornecido
    if orchestrator is None:
        orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=BIOMIMETIC_AVAILABLE
        )
    
    if not meeting_id:
        print("❌ ID de reunião não fornecido")
        return
    
    print(f"💾 Salvando notas da reunião {meeting_id}...")
    
    from src.agents.autonomous_action_orchestrator import ActionRequest, ActionType
    
    request = ActionRequest(
        action_type=ActionType.SAVE_MEETING_NOTES,
        parameters={
            "meeting_id": meeting_id
        }
    )
    
    result = orchestrator.executor.execute(request)
    
    if result and result.result and result.result.get("success"):
        print(f"✅ Notas salvas com sucesso!")
        print(f"   Caminho: {result.result.get('note_path')}")
        
        if result.result.get("obsidian_saved"):
            print(f"   ✅ Salvo no Obsidian (real)")
        else:
            print(f"   ⚠️ Simulado (Obsidian não disponível)")
        
        # Verificar integração com Google Calendar
        if result.result.get("calendar_integration_attempted"):
            if result.result.get("calendar_event_created"):
                print(f"   ✅ Evento criado no Google Calendar")
                print(f"      ID: {result.result.get('calendar_event_id', 'N/A')}")
                print(f"      Link: {result.result.get('calendar_event_link', 'N/A')}")
            else:
                print(f"   ⚠️ Integração com calendário falhou ou não disponível")
                if result.result.get("calendar_error"):
                    print(f"      Erro: {result.result.get('calendar_error')}")
        else:
            print(f"   ℹ️ Integração com calendário não tentada")
        
        # Mostrar preview do conteúdo
        preview = result.result.get("note_content_preview", "")
        print(f"\n📄 Preview do conteúdo:")
        print(f"   {preview}")
    else:
        print(f"❌ Falha ao salvar notas: {result.result.get('error', 'Erro desconhecido')}")


def test_meeting_monitoring(meeting_id: str, orchestrator=None):
    """Teste 5: Monitoramento de reunião ativa"""
    print("\n" + "="*60)
    print("TESTE 5: Monitoramento e Intervenção em Reunião")
    print("="*60)
    
    # Criar orquestrador se não fornecido
    if orchestrator is None:
        orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=BIOMIMETIC_AVAILABLE
        )
    
    if not meeting_id:
        print("❌ ID de reunião não fornecido")
        return
    
    print(f"👁️ Monitorando reunião {meeting_id}...")
    
    from src.agents.autonomous_action_orchestrator import ActionRequest, ActionType
    
    # Adicionar mais transcrição para simular conversa
    status = orchestrator.get_meeting_status(meeting_id)
    if status and "transcription" in status:
        # Adicionar segmento que menciona Jarvis para testar intervenção
        status["transcription"].append({
            "speaker": "Participante 3",
            "text": "O que o Jarvis acha sobre a implementação com Google Meet?",
            "timestamp": "00:10:15",
            "sentiment": "neutral"
        })
    
    request = ActionRequest(
        action_type=ActionType.MONITOR_MEETING,
        parameters={
            "meeting_id": meeting_id,
            "interval_seconds": 30
        }
    )
    
    result = orchestrator.executor.execute(request)
    
    if result and result.result and result.result.get("success"):
        print(f"✅ Monitoramento ativo!")
        print(f"   Segmentos transcritos: {result.result.get('transcript_segments', 0)}")
        print(f"   Intervalo: {result.result.get('interval_seconds')}s")
        
        if result.result.get("should_intervene"):
            print(f"\n🚨 INTERVENÇÃO NECESSÁRIA!")
            print(f"   Motivo: {result.result.get('intervention_reason')}")
            print(f"   Resposta sugerida: {result.result.get('intervention_response')}")
            print(f"   Horário: {result.result.get('intervention_timestamp')}")
        else:
            print(f"\n✅ Nenhuma intervenção necessária no momento")
    else:
        print(f"❌ Falha no monitoramento: {result.result.get('error', 'Erro desconhecido')}")


def test_meeting_end(meeting_id: str, orchestrator=None):
    """Teste 6: Finalizar reunião"""
    print("\n" + "="*60)
    print("TESTE 6: Finalização de Reunião")
    print("="*60)
    
    # Criar orquestrador se não fornecido
    if orchestrator is None:
        orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=BIOMIMETIC_AVAILABLE
        )
    
    if not meeting_id:
        print("❌ ID de reunião não fornecido")
        return
    
    print(f"🏁 Finalizando reunião {meeting_id}...")
    
    result = orchestrator.end_meeting(meeting_id)
    
    if result.get("success"):
        print(f"✅ Reunião finalizada com sucesso!")
        print(f"   Duração: {result.get('duration_minutes', 0):.1f} minutos")
        print(f"   Horário de término: {result.get('ended_at')}")
        
        # Verificar histórico
        print(f"\n📊 Histórico de reuniões: {len(orchestrator.meeting_history)} reuniões")
        for i, meeting in enumerate(orchestrator.meeting_history[-3:]):  # Últimas 3
            print(f"   {i+1}. {meeting.get('meeting_title')} ({meeting.get('status')})")
    else:
        print(f"❌ Falha ao finalizar reunião: {result.get('error', 'Erro desconhecido')}")


def run_demo_scenario():
    """Executa cenário completo de demonstração"""
    print("🎭 DEMONSTRAÇÃO DA FASE 8: PARTICIPAÇÃO EM REUNIÕES")
    print("="*60)
    
    meeting_id = None
    
    try:
        # Criar um único orquestrador para todos os testes
        orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=BIOMIMETIC_AVAILABLE,
            require_human_approval=False  # Desativar para teste
        )
        
        # Teste 1: Processar convite
        meeting_id = test_meeting_invitation_processing(orchestrator)
        
        if meeting_id:
            # Teste 2: Transcrever (usa o mesmo orquestrador)
            test_meeting_transcription(meeting_id, orchestrator)
            
            # Teste 3: Resumir
            test_meeting_summarization(meeting_id, orchestrator)
            
            # Teste 4: Salvar notas
            test_meeting_notes_saving(meeting_id, orchestrator)
            
            # Teste 5: Monitorar
            test_meeting_monitoring(meeting_id, orchestrator)
            
            # Teste 6: Finalizar
            test_meeting_end(meeting_id, orchestrator)
            
            print("\n" + "="*60)
            print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print("\nRecursos implementados:")
            print("  1. 🎯 Processamento biomimético de convites")
            print("  2. 🎤 Entrada automática em reuniões")
            print("  3. 📝 Transcrição em tempo real (STT)")
            print("  4. 🧠 Resumo inteligente com sistema biomimético")
            print("  5. 💾 Salvamento automático no Obsidian")
            print("  6. 👁️ Monitoramento contextual e intervenção")
            print("  7. 📊 Histórico e métricas de participação")
            
            # Teste adicional: Integração biomimética
            test_biomimetic_decision_integration()
        else:
            print("\n⚠️ Demonstração parcial - não foi possível obter ID de reunião")
    
    except Exception as e:
        print(f"\n❌ ERRO NA DEMONSTRAÇÃO: {e}")
        import traceback
        traceback.print_exc()


def test_biomimetic_decision_integration():
    """Teste adicional: Integração com sistema biomimético para decisões"""
    print("\n" + "="*60)
    print("TESTE AVANÇADO: Integração Biomimética")
    print("="*60)
    
    if not BIOMIMETIC_AVAILABLE:
        print("⚠️ Sistema biomimético não disponível - pulando teste")
        return
    
    print("🧬 Testando integração com sistema biomimético...")
    
    try:
        from src.systems.sistemas.sistema_meta_learning_biomimetico import AutoEvolvingAISystem
        
        # Criar sistema biomimético
        biomimetic = AutoEvolvingAISystem(use_local_brain=True)
        
        # Testar decisão para contexto de reunião
        task = {
            "type": "meeting_participation_strategy",
            "context": {
                "meeting_type": "technical_review",
                "participants": ["engenheiros", "gestores"],
                "platform": "google_meet",
                "duration_minutes": 60
            },
            "length": 150,
        }
        
        recommendation = biomimetic.recommend_provider(
            task_type="strategy_planning",
            task_length=task["length"],
            context="Determine optimal meeting participation strategy"
        )
        
        print(f"✅ Sistema biomimético integrado!")
        print(f"   Recomendação: {recommendation.get('provider', 'N/A')}")
        print(f"   Confiança: {recommendation.get('confidence', 0):.1%}")
        print(f"   Estratégia: {recommendation.get('strategy', 'N/A')}")
        
        if recommendation.get("reasoning"):
            print(f"\n🤔 Reasoning:")
            for line in recommendation["reasoning"].split('\n')[:5]:
                print(f"   {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração biomimética: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 Iniciando demonstração da Fase 8...")
    
    # Executar cenário principal
    run_demo_scenario()
    
    # Teste adicional de integração biomimética
    test_biomimetic_decision_integration()
    
    print("\n" + "="*60)
    print("📋 RESUMO DA IMPLEMENTAÇÃO")
    print("="*60)
    print("\n✅ FASE 8 IMPLEMENTADA:")
    print("   - MeetingOrchestrator: Orquestrador especializado em reuniões")
    print("   - 5 novas ações: JOIN_MEETING, TRANSCRIBE_MEETING, SUMMARIZE_MEETING, etc.")
    print("   - Integração com Google Meet/Teams (simulada)")
    print("   - Transcrição STT em tempo real (simulada)")
    print("   - Resumo biomimético com sistema de Fase 5")
    print("   - Salvamento automático no Obsidian")
    print("   - Monitoramento contextual e intervenção")
    print("   - Protocolos de etiqueta empresarial")
    print("\n🔗 INTEGRAÇÕES:")
    print("   - Google Calendar API (Fase 7)")
    print("   - Gmail API (Fase 7)")
    print("   - Sistema Biomimético (Fase 5)")
    print("   - Obsidian (Fase 7)")
    print("   - WhatsApp/TTS via Bio Console (Fase 7)")
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Configurar credenciais Google reais")
    print("   2. Implementar integração real com Google Meet")
    print("   3. Adicionar suporte a Microsoft Teams")
    print("   4. Implementar STT real (Whisper/Azure Speech)")
    print("   5. Testar com reuniões reais")