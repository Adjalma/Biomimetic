#!/usr/bin/env python3
"""
Script de Teste para Integração dos Sistemas V2 ao FAISS
========================================================

Este script testa se os Sistemas V2 foram integrados corretamente aos arquivos principais da IA:
- main.py
- core/main.py  
- Integração ao FAISS existente (sem bancos separados)
- genome_master.yaml
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_importacoes_v2():
    """Testa se os Sistemas V2 podem ser importados"""
    logger.info("🧪 Testando importações dos Sistemas V2...")
    
    try:
        from guardiao_conhecimento import GuardiaoConhecimento
        logger.info("✅ GuardiaoConhecimento importado com sucesso")
        
        from simulador_contrafactual import SimuladorContrafactual
        logger.info("✅ SimuladorContrafactual importado com sucesso")
        
        from gerador_procedimentos_academia import (
            MineradorPadroes, 
            GeradorProcedimentosSugeridos, 
            AcademiaAgentes
        )
        logger.info("✅ GeradorProcedimentosAcademia importado com sucesso")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Erro ao importar Sistemas V2: {e}")
        return False

def testar_main_py():
    """Testa se o main.py foi atualizado com Sistemas V2 integrados ao FAISS"""
    logger.info("🧪 Testando main.py...")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se contém importações dos Sistemas V2
        if 'from guardiao_conhecimento import GuardiaoConhecimento' in content:
            logger.info("✅ Importação GuardiaoConhecimento encontrada")
        else:
            logger.error("❌ Importação GuardiaoConhecimento NÃO encontrada")
            return False
        
        if 'from simulador_contrafactual import SimuladorContrafactual' in content:
            logger.info("✅ Importação SimuladorContrafactual encontrada")
        else:
            logger.error("❌ Importação SimuladorContrafactual NÃO encontrada")
            return False
        
        if 'from gerador_procedimentos_academia import' in content:
            logger.info("✅ Importação GeradorProcedimentosAcademia encontrada")
        else:
            logger.error("❌ Importação GeradorProcedimentosAcademia NÃO encontrada")
            return False
        
        # Verificar se contém métodos dos Sistemas V2
        if 'def _inicializar_sistemas_v2(self):' in content:
            logger.info("✅ Método _inicializar_sistemas_v2 encontrado")
        else:
            logger.error("❌ Método _inicializar_sistemas_v2 NÃO encontrado")
            return False
        
        if 'def executar_analise_guardiao(self)' in content:
            logger.info("✅ Método executar_analise_guardiao encontrado")
        else:
            logger.error("❌ Método executar_analise_guardiao NÃO encontrado")
            return False
        
        # Verificar se está integrado ao FAISS (sem bancos separados)
        if 'usar_banco_separado=False' in content:
            logger.info("✅ Configuração sem bancos separados encontrada")
        else:
            logger.error("❌ Configuração sem bancos separados NÃO encontrada")
            return False
        
        if 'faiss_path="faiss_biblioteca_central"' in content:
            logger.info("✅ Integração ao FAISS encontrada")
        else:
            logger.error("❌ Integração ao FAISS NÃO encontrada")
            return False
        
        logger.info("✅ main.py está integrado com Sistemas V2 ao FAISS")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar main.py: {e}")
        return False

def testar_core_main_py():
    """Testa se o core/main.py foi atualizado com Sistemas V2 integrados ao FAISS"""
    logger.info("🧪 Testando core/main.py...")
    
    try:
        with open('core/main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se contém importações dos Sistemas V2
        if 'from guardiao_conhecimento import GuardiaoConhecimento' in content:
            logger.info("✅ Importação GuardiaoConhecimento encontrada")
        else:
            logger.error("❌ Importação GuardiaoConhecimento NÃO encontrada")
            return False
        
        if 'from simulador_contrafactual import SimuladorContrafactual' in content:
            logger.info("✅ Importação SimuladorContrafactual encontrada")
        else:
            logger.error("❌ Importação SimuladorContrafactual NÃO encontrada")
            return False
        
        # Verificar se contém métodos dos Sistemas V2
        if 'def _inicializar_sistemas_v2(self):' in content:
            logger.info("✅ Método _inicializar_sistemas_v2 encontrado")
        else:
            logger.error("❌ Método _inicializar_sistemas_v2 NÃO encontrado")
            return False
        
        if 'def executar_analise_guardiao(self)' in content:
            logger.info("✅ Método executar_analise_guardiao encontrado")
        else:
            logger.error("❌ Método executar_analise_guardiao NÃO encontrado")
            return False
        
        # Verificar se está integrado ao FAISS (sem bancos separados)
        if 'usar_banco_separado=False' in content:
            logger.info("✅ Configuração sem bancos separados encontrada")
        else:
            logger.error("❌ Configuração sem bancos separados NÃO encontrada")
            return False
        
        logger.info("✅ core/main.py está integrado com Sistemas V2 ao FAISS")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar core/main.py: {e}")
        return False

def testar_barramento_conhecimento():
    """Testa se o barramento_conhecimento_unificado.py foi limpo de Sistemas V2"""
    logger.info("🧪 Testando barramento_conhecimento_unificado.py...")
    
    try:
        with open('barramento_conhecimento_unificado.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se NÃO contém importações dos Sistemas V2
        if 'from guardiao_conhecimento import GuardiaoConhecimento' in content:
            logger.error("❌ Importação GuardiaoConhecimento ainda presente (deveria ter sido removida)")
            return False
        else:
            logger.info("✅ Importação GuardiaoConhecimento removida corretamente")
        
        if 'from simulador_contrafactual import SimuladorContrafactual' in content:
            logger.error("❌ Importação SimuladorContrafactual ainda presente (deveria ter sido removida)")
            return False
        else:
            logger.info("✅ Importação SimuladorContrafactual removida corretamente")
        
        # Verificar se contém nota sobre Sistemas V2 movidos
        if 'Sistemas V2 foram movidos para integração direta com FAISS' in content:
            logger.info("✅ Nota sobre Sistemas V2 movidos encontrada")
        else:
            logger.error("❌ Nota sobre Sistemas V2 movidos NÃO encontrada")
            return False
        
        logger.info("✅ barramento_conhecimento_unificado.py foi limpo corretamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar barramento_conhecimento_unificado.py: {e}")
        return False

def testar_genome_master():
    """Testa se o genome_master.yaml foi atualizado com o 8º agente"""
    logger.info("🧪 Testando genome_master.yaml...")
    
    try:
        with open('genome_master.yaml', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se contém o 8º agente (guardião)
        if 'guardiao:' in content:
            logger.info("✅ Agente guardiao encontrado")
        else:
            logger.error("❌ Agente guardiao NÃO encontrado")
            return False
        
        if 'Guardião do Conhecimento' in content:
            logger.info("✅ Descrição do Guardião encontrada")
        else:
            logger.error("❌ Descrição do Guardião NÃO encontrada")
            return False
        
        # Verificar se contém as ferramentas V2
        if 'knowledge_guardian_system' in content:
            logger.info("✅ Ferramenta knowledge_guardian_system encontrada")
        else:
            logger.error("❌ Ferramenta knowledge_guardian_system NÃO encontrada")
            return False
        
        if 'counterfactual_simulator' in content:
            logger.info("✅ Ferramenta counterfactual_simulator encontrada")
        else:
            logger.error("❌ Ferramenta counterfactual_simulator NÃO encontrada")
            return False
        
        if 'procedure_generator_academy' in content:
            logger.info("✅ Ferramenta procedure_generator_academy encontrada")
        else:
            logger.error("❌ Ferramenta procedure_generator_academy NÃO encontrada")
            return False
        
        logger.info("✅ genome_master.yaml está atualizado com o 8º agente e ferramentas V2")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar genome_master.yaml: {e}")
        return False

def testar_instanciacao_sistemas():
    """Testa se os Sistemas V2 podem ser instanciados sem bancos separados"""
    logger.info("🧪 Testando instanciação dos Sistemas V2 sem bancos separados...")
    
    try:
        # Testar Guardião do Conhecimento (sem banco separado)
        from guardiao_conhecimento import GuardiaoConhecimento
        guardiao = GuardiaoConhecimento(usar_banco_separado=False, faiss_path="faiss_biblioteca_central")
        logger.info("✅ GuardiaoConhecimento instanciado com sucesso (sem banco separado)")
        
        # Testar Simulador Contrafactual (sem banco separado)
        from simulador_contrafactual import SimuladorContrafactual
        simulador = SimuladorContrafactual(usar_banco_separado=False, faiss_path="faiss_biblioteca_central")
        logger.info("✅ SimuladorContrafactual instanciado com sucesso (sem banco separado)")
        
        # Testar Gerador de Procedimentos (sem bancos separados)
        from gerador_procedimentos_academia import (
            MineradorPadroes, 
            GeradorProcedimentosSugeridos, 
            AcademiaAgentes
        )
        minerador = MineradorPadroes(usar_banco_separado=False, faiss_path="faiss_biblioteca_central")
        gerador = GeradorProcedimentosSugeridos(usar_banco_separado=False, faiss_path="faiss_biblioteca_central")
        academia = AcademiaAgentes(usar_banco_separado=False, faiss_path="faiss_biblioteca_central")
        logger.info("✅ Todos os sistemas V2 instanciados com sucesso (sem bancos separados)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao instanciar Sistemas V2: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DE INTEGRAÇÃO DOS SISTEMAS V2 AO FAISS")
    print("=" * 50)
    
    resultados = {}
    
    # Executar todos os testes
    resultados['importacoes_v2'] = testar_importacoes_v2()
    resultados['main_py'] = testar_main_py()
    resultados['core_main_py'] = testar_core_main_py()
    resultados['barramento_conhecimento'] = testar_barramento_conhecimento()
    resultados['genome_master'] = testar_genome_master()
    resultados['instanciacao_sistemas'] = testar_instanciacao_sistemas()
    
    # Resumo dos resultados
    print("\n📊 RESULTADOS DOS TESTES:")
    print("=" * 30)
    
    total_testes = len(resultados)
    testes_aprovados = sum(resultados.values())
    
    for teste, resultado in resultados.items():
        status = "✅ APROVADO" if resultado else "❌ REPROVADO"
        print(f"  {teste}: {status}")
    
    print(f"\n📈 RESUMO: {testes_aprovados}/{total_testes} testes aprovados")
    
    if testes_aprovados == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM! Sistemas V2 integrados ao FAISS com sucesso!")
        print("\n🚀 A IA agora está ciente dos novos sistemas e capacidades:")
        print("  • Guardião do Conhecimento (8º agente especialista) - integrado ao FAISS")
        print("  • Simulador Contrafactual para análise de cenários - integrado ao FAISS")
        print("  • Gerador de Procedimentos e Academia de Agentes - integrado ao FAISS")
        print("  • Genoma atualizado com novas ferramentas")
        print("  • Arquivos principais integrados (sem bancos separados)")
        print("  • Integração direta ao FAISS unificado existente")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM. Verifique os erros acima.")
    
    return resultados

if __name__ == "__main__":
    main()
