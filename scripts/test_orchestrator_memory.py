#!/usr/bin/env python3
"""
Teste rápido do orquestrador com integração do Memory Agent
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.autonomous_action_orchestrator import AutonomousActionOrchestrator

print("🧪 TESTE RÁPIDO DO ORQUESTRADOR COM MEMORY AGENT")
print("=" * 60)

# Criar orquestrador
orchestrator = AutonomousActionOrchestrator(
    use_biomimetic=False,
    require_human_approval=False
)

print("\n1. 📊 STATUS:")
status = orchestrator.get_status()
print(f"   • Componentes disponíveis:")
for component, available in status["components"].items():
    print(f"     - {component}: {'✅' if available else '❌'}")
print(f"   • Ações registradas: {len(status['available_actions'])}")

print("\n2. 🎯 AÇÕES DISPONÍVEIS:")
for action in status["available_actions"]:
    print(f"   • {action['type']}: {action['description']}")
    print(f"     Requisitos: {action['requirements']}")

print("\n3. 🧠 VERIFICAÇÃO DE MEMORY AGENT:")
if status["components"]["memory_agent"]:
    print("   ✅ Memory Agent disponível no sistema")
    # Verificar se o executor tem memory_agent
    if hasattr(orchestrator.executor, 'memory_agent') and orchestrator.executor.memory_agent:
        print("   ✅ Memory Agent inicializado no executor")
    else:
        print("   ⚠️ Memory Agent não inicializado no executor")
else:
    print("   ❌ Memory Agent não disponível (dependência não instalada)")

print("\n4. 🚀 SITUAÇÃO DE EXEMPLO (Consulta de Memória):")
situation = {
    "description": "Preciso consultar o contexto do projeto",
    "type": "memory_query",
    "urgency": "low",
    "action_parameters": {
        "query": "Qual é o estado atual do projeto AI-Biomimetica?",
        "question": "O que já foi implementado?"
    }
}

print(f"   📝 Situação: {situation['description']}")
result = orchestrator.process_situation(situation)
if result:
    print(f"   • Ação decidida: {result.action_type.value}")
    print(f"   • Status: {result.status}")
    if result.result:
        print(f"   • Resultado: {result.result}")
else:
    print("   • Nenhuma ação possível (componentes não disponíveis)")

print("\n" + "=" * 60)
print("✅ TESTE CONCLUÍDO")