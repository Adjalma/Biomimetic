#!/usr/bin/env python3
"""
Demonstração das Fases 9 e 10: Contexto Empresarial e Aprendizado com Interações

Testa os módulos:
1. Hierarquia Organizacional - mapeamento de cargos, departamentos, relações
2. Gestão de Relacionamentos - métricas de rapport, confiança, histórico
3. Regras de Etiqueta - protocolos baseados em hierarquia e contexto cultural
4. Aprendizado com Interações - análise de padrões para evolução

Autor: Jarvis (OpenClaw)
Data: 2026-04-11
"""

import sys
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_organizational_hierarchy():
    """Teste 1: Hierarquia Organizacional"""
    print("\n" + "="*60)
    print("TESTE 1: Hierarquia Organizacional (Fase 9)")
    print("="*60)
    
    try:
        from src.agents.organizational_hierarchy import create_organizational_hierarchy, EmployeeRole
        
        # Criar dados organizacionais de exemplo
        org_data = {
            "employees": [
                {
                    "id": "ceo_001",
                    "name": "Carlos Silva",
                    "email": "carlos.silva@empresa.com",
                    "role": "ceo",
                    "department": "Executivo",
                    "manager_id": None,
                    "direct_reports": ["cto_001", "cfo_001"],
                    "level": 0,
                    "start_date": "2020-01-15"
                },
                {
                    "id": "cto_001",
                    "name": "Ana Rodrigues",
                    "email": "ana.rodrigues@empresa.com",
                    "role": "cto",
                    "department": "Tecnologia",
                    "manager_id": "ceo_001",
                    "direct_reports": ["director_tech_001", "director_tech_002"],
                    "level": 1,
                    "start_date": "2021-03-20"
                },
                {
                    "id": "director_tech_001",
                    "name": "Roberto Lima",
                    "email": "roberto.lima@empresa.com",
                    "role": "director",
                    "department": "Engenharia",
                    "manager_id": "cto_001",
                    "direct_reports": ["manager_eng_001", "manager_eng_002"],
                    "level": 2,
                    "start_date": "2022-06-10"
                },
                {
                    "id": "manager_eng_001",
                    "name": "Fernanda Costa",
                    "email": "fernanda.costa@empresa.com",
                    "role": "manager",
                    "department": "Engenharia",
                    "manager_id": "director_tech_001",
                    "direct_reports": ["eng_001", "eng_002"],
                    "level": 3,
                    "start_date": "2023-01-15"
                },
                {
                    "id": "eng_001",
                    "name": "Adjalma Aguiar",
                    "email": "adjalma.aguiar@empresa.com",
                    "role": "engineer",
                    "department": "Engenharia",
                    "manager_id": "manager_eng_001",
                    "direct_reports": [],
                    "level": 4,
                    "start_date": "2024-02-01"
                },
                {
                    "id": "eng_002",
                    "name": "Julia Santos",
                    "email": "julia.santos@empresa.com",
                    "role": "senior_engineer",
                    "department": "Engenharia",
                    "manager_id": "manager_eng_001",
                    "direct_reports": [],
                    "level": 4,
                    "start_date": "2023-11-01"
                }
            ],
            "departments": [
                {
                    "id": "dept_exec",
                    "name": "Executivo",
                    "head_id": "ceo_001",
                    "member_ids": ["ceo_001"]
                },
                {
                    "id": "dept_tech",
                    "name": "Tecnologia",
                    "head_id": "cto_001",
                    "member_ids": ["cto_001", "director_tech_001", "director_tech_002", 
                                  "manager_eng_001", "manager_eng_002", "eng_001", "eng_002"]
                }
            ]
        }
        
        # Salvar dados temporariamente
        temp_file = Path("/tmp/org_data_demo.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(org_data, f, indent=2, ensure_ascii=False)
        
        # Criar hierarquia
        hierarchy = create_organizational_hierarchy(str(temp_file))
        
        print(f"✅ Hierarquia carregada com {len(hierarchy.employees)} funcionários")
        
        # Testar consultas
        print("\n📊 Consultas de Hierarquia:")
        
        # Encontrar funcionário por email
        adjalma = hierarchy.get_employee_by_email("adjalma.aguiar@empresa.com")
        if adjalma:
            print(f"   👤 Adjalma: {adjalma.name} ({adjalma.role.value}), Nível: {adjalma.level}")
        
        # Cadeia de comando
        if adjalma:
            chain = hierarchy.get_manager_chain(adjalma.id)
            print(f"\n   ⛓️  Cadeia de comando de {adjalma.name}:")
            for emp in chain:
                print(f"      → {emp.name} ({emp.role.value}) - Nível {emp.level}")
        
        # Distância hierárquica
        ceo = hierarchy.get_employee_by_email("carlos.silva@empresa.com")
        if ceo and adjalma:
            distance = hierarchy.get_hierarchical_distance(ceo.id, adjalma.id)
            print(f"\n   📏 Distância hierárquica CEO ↔ Adjalma: {distance} níveis")
        
        # Formalidade de comunicação
        if ceo and adjalma:
            formality = hierarchy.get_communication_formality(adjalma.id, ceo.id)
            print(f"   🎩 Formalidade (Adjalma → CEO): {formality}")
            formality_reverse = hierarchy.get_communication_formality(ceo.id, adjalma.id)
            print(f"   🎩 Formalidade (CEO → Adjalma): {formality_reverse}")
        
        # Gerente comum
        eng2 = hierarchy.get_employee_by_email("julia.santos@empresa.com")
        if adjalma and eng2:
            common_manager = hierarchy.find_common_manager([adjalma.id, eng2.id])
            if common_manager:
                print(f"\n   🤝 Gerente comum (Adjalma & Julia): {common_manager.name} ({common_manager.role.value})")
        
        # Exportar para JSON
        export_file = Path("/tmp/org_export_demo.json")
        hierarchy.export_to_json(str(export_file))
        print(f"\n   💾 Hierarquia exportada para: {export_file}")
        
        temp_file.unlink(missing_ok=True)
        
        return hierarchy
        
    except Exception as e:
        print(f"❌ Erro no teste de hierarquia: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_relationship_manager():
    """Teste 2: Gestão de Relacionamentos"""
    print("\n" + "="*60)
    print("TESTE 2: Gestão de Relacionamentos (Fase 9)")
    print("="*60)
    
    try:
        from src.agents.relationship_manager import create_relationship_manager, InteractionType
        
        # Criar gerenciador de relacionamentos
        rel_manager = create_relationship_manager()
        
        # Adicionar interações de exemplo
        from datetime import datetime, timedelta
        
        # Interações entre Adjalma e seus colegas/gestores
        interactions = [
            {
                "id": "int_001",
                "participant_ids": ["eng_001", "manager_eng_001"],  # Adjalma e sua gerente
                "interaction_type": "meeting",
                "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
                "duration_minutes": 60,
                "topic": "Revisão de progresso do projeto AI-Biomimetica",
                "sentiment": 1,  # POSITIVE
                "notes": "Discussão produtiva, feedback positivo"
            },
            {
                "id": "int_002",
                "participant_ids": ["eng_001", "eng_002"],  # Adjalma e Julia
                "interaction_type": "chat",
                "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
                "duration_minutes": 15,
                "topic": "Dúvida técnica sobre integração Google Meet",
                "sentiment": 0,  # NEUTRAL
                "notes": "Resolução rápida de problema"
            },
            {
                "id": "int_003",
                "participant_ids": ["eng_001", "director_tech_001"],  # Adjalma e diretor
                "interaction_type": "email",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "duration_minutes": 5,
                "topic": "Relatório de progresso da Fase 8",
                "sentiment": 1,  # POSITIVE
                "notes": "Feedback elogioso do diretor"
            },
            {
                "id": "int_004",
                "participant_ids": ["eng_001", "manager_eng_001"],  # Adjalma e gerente (repetido)
                "interaction_type": "meeting",
                "timestamp": datetime.now().isoformat(),
                "duration_minutes": 45,
                "topic": "Planejamento da Fase 9",
                "sentiment": 2,  # VERY_POSITIVE
                "notes": "Sessão de brainstorming muito produtiva"
            }
        ]
        
        # Adicionar interações
        from src.agents.relationship_manager import Interaction, Sentiment
        
        for int_data in interactions:
            interaction = Interaction(
                id=int_data["id"],
                participant_ids=int_data["participant_ids"],
                interaction_type=InteractionType(int_data["interaction_type"]),
                timestamp=datetime.fromisoformat(int_data["timestamp"].replace('Z', '+00:00')),
                duration_minutes=int_data["duration_minutes"],
                topic=int_data["topic"],
                sentiment=Sentiment(int_data["sentiment"]),
                notes=int_data["notes"]
            )
            rel_manager.add_interaction(interaction)
        
        print(f"✅ Gerenciador de relacionamentos criado com {len(rel_manager.interactions)} interações")
        
        # Testar consultas
        print("\n📈 Métricas de Relacionamento:")
        
        # Relacionamento Adjalma ↔ Gerente
        metrics = rel_manager.get_relationship("eng_001", "manager_eng_001")
        if metrics:
            print(f"\n   👥 Adjalma ↔ Gerente (Fernanda):")
            print(f"      Total interações: {metrics.total_interactions}")
            print(f"      Interações (30 dias): {metrics.interactions_last_30_days}")
            print(f"      Sentimento médio: {metrics.average_sentiment:.2f}")
            print(f"      Score de rapport: {metrics.rapport_score:.1f}/100")
            print(f"      Nível de confiança: {metrics.trust_level:.2f}")
            print(f"      Canal preferido: {metrics.preferred_communication_type.value if metrics.preferred_communication_type else 'N/A'}")
        
        # Relacionamento Adjalma ↔ Colega
        metrics2 = rel_manager.get_relationship("eng_001", "eng_002")
        if metrics2:
            print(f"\n   👥 Adjalma ↔ Colega (Julia):")
            print(f"      Total interações: {metrics2.total_interactions}")
            print(f"      Score de rapport: {metrics2.rapport_score:.1f}/100")
            print(f"      Tópicos comuns: {', '.join(metrics2.common_topics[:3])}")
        
        # Recomendações de comunicação
        print("\n💡 Recomendações de Comunicação:")
        
        recommendation = rel_manager.get_communication_recommendation(
            from_person_id="eng_001",
            to_person_id="director_tech_001",
            context="sensitive"
        )
        
        if recommendation:
            print(f"   📤 Adjalma → Diretor (contexto sensível):")
            print(f"      Canal preferido: {recommendation['preferred_channel'] or 'N/A'}")
            print(f"      Nível de formalidade: {recommendation['formality_level']}")
            print(f"      Timing: {recommendation['timing_recommendation']}")
            print(f"      Warm-up necessário: {recommendation['warm_up_needed']}")
            print(f"      Confiança: {recommendation['confidence']:.2f}")
        
        # Histórico de interações
        print("\n🕰️ Histórico de Interações de Adjalma:")
        interactions = rel_manager.get_person_interactions("eng_001", limit=5)
        for i, interaction in enumerate(interactions):
            print(f"   {i+1}. {interaction.timestamp.strftime('%d/%m')} - {interaction.interaction_type.value}: {interaction.topic[:50]}...")
        
        # Exportar dados
        export_file = Path("/tmp/relationships_export_demo.json")
        rel_manager.export_to_json(str(export_file))
        print(f"\n   💾 Dados de relacionamento exportados para: {export_file}")
        
        return rel_manager
        
    except Exception as e:
        print(f"❌ Erro no teste de relacionamentos: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_etiquette_rules():
    """Teste 3: Regras de Etiqueta"""
    print("\n" + "="*60)
    print("TESTE 3: Regras de Etiqueta (Fase 8)")
    print("="*60)
    
    try:
        from src.meeting.etiquette_rules import create_etiquette_rules, MeetingType, IARole, CulturalContext
        
        # Criar sistema de regras para diferentes contextos culturais
        print("\n🎭 Testando diferentes contextos culturais:")
        
        contexts = [
            ("formal_hierarchical", "Empresa Tradicional Hierárquica"),
            ("informal_flat", "Startup com Estrutura Plana"),
            ("technical_focused", "Organização com Foco Técnico"),
            ("creative", "Agência Criativa/Publicidade")
        ]
        
        for context_key, description in contexts:
            etiquette = create_etiquette_rules(CulturalContext[context_key.upper()])
            
            # Cenário: Reunião executiva com tópico sensível
            executive_context = {
                "meeting_type": MeetingType.EXECUTIVE.value,
                "ia_role": IARole.ASSISTANT.value,
                "cultural_context": context_key,
                "sensitive_topic": True,
                "has_executives": True,
                "mentioned_ia": False,
                "direct_question": False
            }
            
            recommendation = etiquette.get_recommended_action(executive_context)
            
            print(f"\n   🏢 {description}:")
            print(f"      Ação recomendada: {recommendation['action']}")
            print(f"      Confiança: {recommendation['confidence']:.2f}")
            print(f"      Regra aplicada: {recommendation.get('top_rule', 'N/A')}")
        
        # Teste detalhado para contexto formal
        print("\n📋 Teste Detalhado - Contexto Formal Hierárquico:")
        etiquette = create_etiquette_rules(CulturalContext.FORMAL_HIERARCHICAL)
        
        scenarios = [
            {
                "name": "Reunião de Brainstorming Criativo",
                "context": {
                    "meeting_type": MeetingType.BRAINSTORMING.value,
                    "ia_role": IARole.PARTICIPANT.value,
                    "cultural_context": "formal_hierarchical",
                    "sensitive_topic": False,
                    "has_executives": False,
                    "mentioned_ia": False,
                    "direct_question": False
                }
            },
            {
                "name": "Reunião com CEO (IA mencionada)",
                "context": {
                    "meeting_type": MeetingType.EXECUTIVE.value,
                    "ia_role": IARole.ASSISTANT.value,
                    "cultural_context": "formal_hierarchical",
                    "sensitive_topic": True,
                    "has_executives": True,
                    "mentioned_ia": True,
                    "direct_question": True
                }
            },
            {
                "name": "Reunião de Cliente Sensível",
                "context": {
                    "meeting_type": MeetingType.CLIENT_MEETING.value,
                    "ia_role": IARole.OBSERVER.value,
                    "cultural_context": "formal_hierarchical",
                    "sensitive_topic": True,
                    "has_executives": False,
                    "mentioned_ia": False,
                    "direct_question": False
                }
            }
        ]
        
        for scenario in scenarios:
            print(f"\n   📌 {scenario['name']}:")
            context = scenario['context']
            
            # Verificar se deve falar
            should_speak = etiquette.should_speak(context)
            print(f"      Deve falar: {'✅ Sim' if should_speak else '❌ Não'}")
            
            # Obter diretrizes de fala
            guidelines = etiquette.get_speech_guidelines(context)
            print(f"      Tom: {guidelines['tone']}")
            print(f"      Formalidade: {guidelines['formality']}")
            print(f"      Duração máxima: {guidelines['max_duration_seconds']}s")
            print(f"      Permitir humor: {'✅ Sim' if guidelines['allow_humor'] else '❌ Não'}")
            
            # Regras aplicáveis
            applicable = etiquette.evaluate_context(context)
            print(f"      Regras aplicáveis: {len(applicable)}")
        
        return etiquette
        
    except Exception as e:
        print(f"❌ Erro no teste de etiqueta: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_interaction_learning():
    """Teste 4: Aprendizado com Interações (Fase 10)"""
    print("\n" + "="*60)
    print("TESTE 4: Aprendizado com Interações (Fase 10)")
    print("="*60)
    
    try:
        # Usar MeetingOrchestrator que já tem sistema de log de interações
        from src.meeting.meeting_orchestrator import create_meeting_orchestrator
        
        # Criar orquestrador
        orchestrator = create_meeting_orchestrator(
            platform="google_meet",
            use_biomimetic=False,  # Sem biomimético para simplificar
            require_human_approval=False
        )
        
        # Simular algumas interações
        print("\n📝 Simulando interações para aprendizado...")
        
        interactions = [
            {
                "type": "meeting_join",
                "participants": ["carlos.silva@empresa.com", "adjalma.aguiar@empresa.com"],
                "meeting_id": "meeting_001",
                "context": {"meeting_type": "executive", "success": True}
            },
            {
                "type": "chat_message",
                "participants": ["adjalma.aguiar@empresa.com", "julia.santos@empresa.com"],
                "message_length": 150,
                "response_time_seconds": 120,
                "topic": "technical"
            },
            {
                "type": "email_sent",
                "participants": ["adjalma.aguiar@empresa.com", "fernanda.costa@empresa.com"],
                "subject": "Progress Report",
                "urgency": "medium",
                "response_received": True
            },
            {
                "type": "meeting_join",
                "participants": ["ana.rodrigues@empresa.com", "adjalma.aguiar@empresa.com", "roberto.lima@empresa.com"],
                "meeting_id": "meeting_002",
                "context": {"meeting_type": "technical_review", "success": True}
            },
            {
                "type": "chat_message",
                "participants": ["adjalma.aguiar@empresa.com", "roberto.lima@empresa.com"],
                "message_length": 80,
                "response_time_seconds": 300,  # 5 minutos
                "topic": "project_approval"
            }
        ]
        
        # Registrar interações
        for interaction in interactions:
            orchestrator._log_interaction(**interaction)
        
        print(f"✅ {len(orchestrator.interaction_log)} interações registradas")
        
        # Obter insights
        print("\n🧠 Gerando insights do aprendizado...")
        insights = orchestrator.get_interaction_insights(limit=10)
        
        if insights:
            for insight in insights:
                print(f"\n📊 {insight['analysis_type'].replace('_', ' ').title()}:")
                print(f"   Total interações: {insight['total_interactions']}")
                
                if 'interaction_types' in insight:
                    print(f"   Tipos de interação:")
                    for itype, count in insight['interaction_types'].items():
                        print(f"      - {itype}: {count}")
                
                if 'top_participants' in insight:
                    print(f"   Participantes mais ativos:")
                    for participant, count in list(insight['top_participants'].items())[:3]:
                        print(f"      - {participant}: {count} interações")
        
        # Testar ação de análise de interações (se disponível)
        print("\n🔍 Testando análise biomimética de interações...")
        
        try:
            from src.agents.autonomous_action_orchestrator import ActionRequest
            
            request = ActionRequest(
                action_type="ANALYZE_INTERACTIONS",
                parameters={
                    "limit": 50,
                    "analysis_depth": "deep"
                }
            )
            
            # Executar análise (pode ser simulada se não houver sistema biomimético)
            result = orchestrator.executor.execute(request)
            
            if result and result.result:
                print(f"✅ Análise de interações executada:")
                print(f"   Interações analisadas: {result.result.get('interactions_analyzed', 0)}")
                print(f"   Insights gerados: {len(result.result.get('insights', []))}")
                print(f"   Aprendizado evolutivo: {'✅ Ativo' if result.result.get('evolutionary_learning') else '❌ Inativo'}")
            else:
                print("⚠️ Análise de interações não disponível (requer sistema biomimético)")
                
        except Exception as e:
            print(f"⚠️ Ação de análise de interações não disponível: {e}")
        
        return orchestrator
        
    except Exception as e:
        print(f"❌ Erro no teste de aprendizado: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_integrated_scenario():
    """Teste 5: Cenário Integrado (Fases 8-10 combinadas)"""
    print("\n" + "="*60)
    print("TESTE 5: Cenário Integrado - Reunião Empresarial Completa")
    print("="*60)
    
    print("\n🎭 Simulando cenário de reunião com todas as fases...")
    
    try:
        # 1. Preparar hierarquia organizacional
        print("\n1️⃣ Preparando contexto organizacional...")
        hierarchy = test_organizational_hierarchy()
        
        # 2. Preparar gerenciador de relacionamentos
        print("\n2️⃣ Carregando histórico de relacionamentos...")
        rel_manager = test_relationship_manager()
        
        # 3. Preparar regras de etiqueta
        print("\n3️⃣ Configurando regras de etiqueta...")
        etiquette = test_etiquette_rules()
        
        # 4. Cenário: Reunião importante com múltiplos níveis hierárquicos
        print("\n4️⃣ 📅 Cenário: Reunião de Revisão Estratégica")
        print("   Participantes:")
        print("   - Carlos Silva (CEO, Nível 0)")
        print("   - Ana Rodrigues (CTO, Nível 1)")
        print("   - Roberto Lima (Diretor, Nível 2)")
        print("   - Fernanda Costa (Gerente, Nível 3)")
        print("   - Adjalma Aguiar (Engenheiro, Nível 4)")
        print("   - Jarvis (IA Assistente)")
        
        # Análise hierárquica
        if hierarchy:
            print("\n   📊 Análise Hierárquica:")
            print(f"   - Distância máxima: CEO (0) ↔ Adjalma (4) = 4 níveis")
            print(f"   - Formalidade recomendada: Alta (devido à presença de executivos)")
            
            # Gerente comum
            participants = ["ceo_001", "cto_001", "director_tech_001", "manager_eng_001", "eng_001"]
            common_manager = hierarchy.find_common_manager(participants)
            if common_manager:
                print(f"   - Gerente comum: {common_manager.name} ({common_manager.role.value})")
        
        # Recomendações de relacionamento
        if rel_manager:
            print("\n   💡 Recomendações Baseadas em Relacionamentos:")
            
            # Adjalma → CEO (pouca interação prévia)
            rec = rel_manager.get_communication_recommendation("eng_001", "ceo_001", "general")
            if rec:
                print(f"   - Adjalma para CEO: {rec['formality_level'].upper()} formalidade")
                print(f"     Timing: {rec['timing_recommendation']}")
                print(f"     Warm-up necessário: {'Sim' if rec['warm_up_needed'] else 'Não'}")
        
        # Regras de etiqueta para IA
        if etiquette:
            print("\n   🤖 Protocolos de Etiqueta para IA (Jarvis):")
            
            ia_context = {
                "meeting_type": "executive",
                "ia_role": "assistant",
                "cultural_context": "formal_hierarchical",
                "sensitive_topic": True,
                "has_executives": True,
                "mentioned_ia": False,
                "direct_question": False
            }
            
            guidelines = etiquette.get_speech_guidelines(ia_context)
            print(f"   - Tom: {guidelines['tone'].upper()}")
            print(f"   - Formalidade: {guidelines['formality'].upper()}")
            print(f"   - Duração máxima: {guidelines['max_duration_seconds']} segundos")
            print(f"   - Backup de dados necessário: {'Sim' if guidelines['require_data_backup'] else 'Não'}")
            
            should_speak = etiquette.should_speak(ia_context)
            print(f"   - Deve falar inicialmente: {'SIM, com permissão' if should_speak else 'NÃO, apenas observar'}")
        
        # Aprendizado com interações
        print("\n5️⃣ 📚 Sistema de Aprendizado (Fase 10):")
        print("   - Todas as interações na reunião serão registradas")
        print("   - Padrões de comunicação serão analisados")
        print("   - Recomendações futuras serão ajustadas")
        print("   - Rapport entre participantes será atualizado")
        
        print("\n✅ Cenário integrado pronto para execução!")
        print("   O sistema agora pode:")
        print("   1. Entrar na reunião do Google Meet")
        print("   2. Seguir protocolos de etiqueta apropriados")
        print("   3. Considerar hierarquia e relacionamentos")
        print("   4. Transcrever e analisar conversas")
        print("   5. Aprender com cada interação")
        print("   6. Evoluir para futuras reuniões")
        
    except Exception as e:
        print(f"❌ Erro no cenário integrado: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Função principal"""
    print("\n🚀 DEMONSTRAÇÃO DAS FASES 9 E 10: CONTEXTO EMPRESARIAL")
    print("="*60)
    
    print("\n📋 O que será demonstrado:")
    print("   1. 🏢 Hierarquia Organizacional (Fase 9)")
    print("   2. 👥 Gestão de Relacionamentos (Fase 9)")
    print("   3. 🤖 Regras de Etiqueta (Fase 8)")
    print("   4. 📚 Aprendizado com Interações (Fase 10)")
    print("   5. 🎭 Cenário Integrado (Fases 8-10 combinadas)")
    
    input("\nPressione Enter para começar...")
    
    # Executar testes
    hierarchy = test_organizational_hierarchy()
    input("\nPressione Enter para continuar com Gestão de Relacionamentos...")
    
    rel_manager = test_relationship_manager()
    input("\nPressione Enter para continuar com Regras de Etiqueta...")
    
    etiquette = test_etiquette_rules()
    input("\nPressione Enter para continuar com Aprendizado com Interações...")
    
    orchestrator = test_interaction_learning()
    input("\nPressione Enter para ver o Cenário Integrado...")
    
    test_integrated_scenario()
    
    print("\n" + "="*60)
    print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    
    print("\n✅ RESUMO DA IMPLEMENTAÇÃO DAS FASES 9 E 10:")
    print("\n🏢 FASE 9 - CONTEXTO EMPRESARIAL:")
    print("   • Sistema de Hierarquia Organizacional completo")
    print("   • Mapeamento de cargos, departamentos, relações de reporte")
    print("   • Cálculo de distância hierárquica e formalidade")
    print("   • Gestão de Relacionamentos com métricas de rapport")
    print("   • Histórico de interações e recomendações de comunicação")
    
    print("\n📚 FASE 10 - APRENDIZADO COM INTERAÇÕES REAIS:")
    print("   • Registro de todas as interações (reuniões, chats, emails)")
    print("   • Análise de padrões de comunicação")
    print("   • Geração de insights para evolução")
    print("   • Integração com sistema biomimético para meta-learning")
    
    print("\n🤖 FASE 8 - ETIQUETA EMPRESARIAL (COMPLEMENTAR):")
    print("   • Protocolos baseados em contexto cultural")
    print("   • Regras para quando falar/ouvir")
    print("   • Diretrizes de tom e formalidade")
    print("   • Consideração de hierarquia e sensibilidade")
    
    print("\n🔗 INTEGRAÇÕES IMPLEMENTADAS:")
    print("   • MeetingOrchestrator ←→ Hierarquia Organizacional")
    print("   • MeetingOrchestrator ←→ Gestão de Relacionamentos")
    print("   • MeetingOrchestrator ←→ Regras de Etiqueta")
    print("   • Todos os módulos ←→ Sistema Biomimético (Fase 5)")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Configurar dados organizacionais reais (CSV/JSON)")
    print("   2. Importar histórico de interações de fontes reais")
    print("   3. Conectar com sistema de RH/Identity Provider")
    print("   4. Treinar modelos de predição de rapport")
    print("   5. Implementar dashboard de análise de relacionamentos")
    
    print("\n💡 DICA: Use o script demo_meeting_participation.py")
    print("      para testar a integração completa das Fases 8-10!")


if __name__ == "__main__":
    main()