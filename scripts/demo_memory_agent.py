#!/usr/bin/env python3
"""
Demonstração do Memory Agent para Jarvis

Testa as funcionalidades principais do agente de memória:
1. Atualização de contexto
2. Consultas sobre projeto
3. Armazenamento de memórias
4. Integração com workspace

Uso:
    python scripts/demo_memory_agent.py
"""

import sys
import os
import asyncio
import logging

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')


async def main():
    print("🧠 DEMONSTRAÇÃO DO MEMORY AGENT")
    print("=" * 60)
    
    try:
        from src.agents.memory_agent import JarvisMemoryAgent, MemoryCategory, MemoryPriority
        
        print("\n1. 🚀 INICIALIZANDO AGENTE...")
        agent = JarvisMemoryAgent(workspace_root="/data/workspace")
        print("   ✅ Agente inicializado")
        
        print("\n2. 🔄 ATUALIZANDO CONTEXTO...")
        context = await agent.refresh_context(force=True)
        print(f"   ✅ Contexto atualizado ({len(context)} elementos)")
        
        print("\n3. 📋 RESUMO DO CONTEXTO:")
        summary = agent.get_context_summary()
        print(summary)
        
        print("\n4. ❓ CONSULTAS DE CONTEXTO:")
        
        questions = [
            "Como está o projeto AI-Biomimetica?",
            "O que fazer agora?",
            "O que já foi implementado?",
            "O que está configurado no sistema?",
            "Tem algum problema conhecido?"
        ]
        
        for question in questions:
            print(f"\n   Q: {question}")
            answer = await agent.query_context(question)
            # Limitar resposta para demonstração
            lines = answer.split('\n')
            for line in lines[:8]:  # Primeiras 8 linhas
                print(f"      {line}")
            if len(lines) > 8:
                print(f"      ... ({len(lines) - 8} linhas omitidas)")
        
        print("\n5. 💾 ARMAZENANDO MEMÓRIA DE TESTE...")
        await agent.store_important(
            event="Memory Agent testado com sucesso",
            category=MemoryCategory.TECHNICAL,
            priority=MemoryPriority.HIGH,
            context={
                "test_type": "demonstração",
                "result": "sucesso",
                "features_tested": ["context_refresh", "queries", "memory_storage"]
            }
        )
        print("   ✅ Memória armazenada")
        
        print("\n6. 🎯 PRÓXIMOS PASSOS IDENTIFICADOS:")
        pending_tasks = context.get("pending_tasks", [])
        if pending_tasks:
            for i, task in enumerate(pending_tasks[:3], 1):
                print(f"   {i}. {task}")
        else:
            print("   ℹ️ Nenhuma tarefa pendente identificada")
        
        print("\n" + "=" * 60)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\nO Memory Agent está funcionando e pode:")
        print("• Manter contexto atualizado do projeto")
        print("• Responder perguntas sobre estado do sistema")
        print("• Armazenar memórias importantes")
        print("• Identificar próximos passos")
        print("\nPronto para integração com Jarvis!")
        
    except Exception as e:
        print(f"\n❌ ERRO NA DEMONSTRAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)