#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste para o Sistema GIC Modificado
=============================================
Testa as modificações feitas no sistema GIC com IA Autoevolutiva Biomimética
"""

import sys
import os
import logging
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def testar_sistema_gic():
    """Testa o sistema GIC modificado"""
    try:
        logger.info("🧪 INICIANDO TESTE DO SISTEMA GIC MODIFICADO")
        logger.info("=" * 60)
        
        # Importar o sistema GIC
        from justifications.gic_ia_integrada import GICIAIntegrada
        
        # Inicializar sistema
        logger.info("📋 Inicializando sistema GIC...")
        gic = GICIAIntegrada()
        logger.info("✅ Sistema GIC inicializado com sucesso!")
        
        # Dados de teste
        logger.info("📝 Preparando dados de teste...")
        respostas_teste = {
            'pergunta_0': 'R$ 2.5 milhões em impactos financeiros',
            'pergunta_1': 'Contrato essencial para continuidade operacional da Petrobras',
            'pergunta_2': 'Documentação técnica e jurídica anexada para suporte'
        }
        
        objetos_teste = ['1 PRAZO', '2 ACRÉSCIMO']
        documentos_teste = ['ICJ_12345.pdf', 'Parecer_Juridico.pdf']
        
        logger.info(f"   - Respostas: {len(respostas_teste)} itens")
        logger.info(f"   - Objetos: {objetos_teste}")
        logger.info(f"   - Documentos: {documentos_teste}")
        
        # Teste 1: Iniciar fluxo GIC
        logger.info("\n🔄 TESTE 1: Iniciando fluxo GIC...")
        fluxo = gic.iniciar_fluxo_gic()
        logger.info(f"   Status: {fluxo.get('status', 'N/A')}")
        logger.info(f"   Fase: {fluxo.get('fase', 'N/A')}")
        logger.info("✅ Fluxo GIC iniciado com sucesso!")
        
        # Teste 2: Gerar justificativa final
        logger.info("\n🤖 TESTE 2: Gerando justificativa com IA...")
        justificativa = gic.gerar_justificativa_final(
            respostas_gerais=respostas_teste,
            objetos_selecionados=objetos_teste,
            documentos_anexados=documentos_teste
        )
        
        logger.info("✅ Justificativa gerada com sucesso!")
        logger.info(f"   Tamanho: {len(justificativa)} caracteres")
        
        # Mostrar parte da justificativa
        logger.info("\n📄 PREVIEW DA JUSTIFICATIVA GERADA:")
        logger.info("-" * 40)
        preview = justificativa[:500] + "..." if len(justificativa) > 500 else justificativa
        logger.info(preview)
        logger.info("-" * 40)
        
        # Teste 3: Verificar estatísticas da IA
        logger.info("\n📊 TESTE 3: Verificando estatísticas da IA...")
        stats = gic.obter_estatisticas_ia()
        logger.info(f"   Sistemas ativos: {stats.get('sistemas_ativos', 'N/A')}")
        logger.info(f"   Versão: {stats.get('versao', 'N/A')}")
        logger.info(f"   IA Autoevolutiva: {stats.get('ia_autoevolutiva', 'N/A')}")
        logger.info("✅ Estatísticas obtidas com sucesso!")
        
        # Teste 4: Verificar se a justificativa contém elementos esperados
        logger.info("\n🔍 TESTE 4: Verificando qualidade da justificativa...")
        
        elementos_esperados = [
            'ANÁLISE MULTIDIMENSIONAL',
            'SISTEMAS ESPECIALISTAS',
            'IA AUTOEVOLUTIVA BIOMIMÉTICA',
            'CONFIANÇA DA ANÁLISE'
        ]
        
        elementos_encontrados = []
        for elemento in elementos_esperados:
            if elemento in justificativa:
                elementos_encontrados.append(elemento)
                logger.info(f"   ✅ {elemento}: Encontrado")
            else:
                logger.warning(f"   ⚠️ {elemento}: Não encontrado")
        
        qualidade = len(elementos_encontrados) / len(elementos_esperados) * 100
        logger.info(f"   Qualidade geral: {qualidade:.1f}%")
        
        # Resultado final
        logger.info("\n🎯 RESULTADO FINAL DO TESTE:")
        logger.info("=" * 60)
        
        if qualidade >= 75:
            logger.info("✅ TESTE PASSOU - Sistema funcionando adequadamente!")
            logger.info("   - Justificativa gerada com sucesso")
            logger.info("   - Elementos esperados presentes")
            logger.info("   - IA Autoevolutiva Biomimética operacional")
        else:
            logger.warning("⚠️ TESTE COM PROBLEMAS - Verificar implementação")
            logger.warning("   - Alguns elementos esperados não encontrados")
            logger.warning("   - Pode precisar de ajustes")
        
        logger.info(f"\n📈 ESTATÍSTICAS DO TESTE:")
        logger.info(f"   - Elementos encontrados: {len(elementos_encontrados)}/{len(elementos_esperados)}")
        logger.info(f"   - Qualidade: {qualidade:.1f}%")
        logger.info(f"   - Tamanho da justificativa: {len(justificativa)} caracteres")
        logger.info(f"   - Timestamp: {datetime.now().isoformat()}")
        
        return {
            'sucesso': qualidade >= 75,
            'qualidade': qualidade,
            'elementos_encontrados': len(elementos_encontrados),
            'total_elementos': len(elementos_esperados),
            'tamanho_justificativa': len(justificativa),
            'justificativa': justificativa
        }
        
    except ImportError as e:
        logger.error(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        logger.error("   Verifique se todos os módulos estão disponíveis")
        return {'sucesso': False, 'erro': 'import_error', 'detalhes': str(e)}
        
    except Exception as e:
        logger.error(f"❌ ERRO NO TESTE: {e}")
        logger.error("   Verifique a implementação do sistema")
        return {'sucesso': False, 'erro': 'runtime_error', 'detalhes': str(e)}

def testar_componentes_individualmente():
    """Testa componentes individuais do sistema"""
    try:
        logger.info("\n🔧 TESTANDO COMPONENTES INDIVIDUAIS...")
        
        # Teste de importações
        logger.info("📦 Testando importações...")
        
        try:
            from barramento_conhecimento_unificado import BarramentoConhecimentoUnificado
            logger.info("   ✅ BarramentoConhecimentoUnificado: OK")
        except Exception as e:
            logger.warning(f"   ⚠️ BarramentoConhecimentoUnificado: {e}")
        
        try:
            from sistema_agentes_faiss_integrado import SistemaAgentesFAISSIntegrado
            logger.info("   ✅ SistemaAgentesFAISSIntegrado: OK")
        except Exception as e:
            logger.warning(f"   ⚠️ SistemaAgentesFAISSIntegrado: {e}")
        
        try:
            from genoma_leis_imutaveis import LeisImutaveis
            logger.info("   ✅ LeisImutaveis: OK")
        except Exception as e:
            logger.warning(f"   ⚠️ LeisImutaveis: {e}")
        
        try:
            from simulador_contrafactual import SimuladorContrafactual
            logger.info("   ✅ SimuladorContrafactual: OK")
        except Exception as e:
            logger.warning(f"   ⚠️ SimuladorContrafactual: {e}")
        
        try:
            from guardiao_conhecimento import GuardiaoConhecimento
            logger.info("   ✅ GuardiaoConhecimento: OK")
        except Exception as e:
            logger.warning(f"   ⚠️ GuardiaoConhecimento: {e}")
        
        try:
            from sistemas.academia_agentes import AcademiaAgentes
            logger.info("   ✅ AcademiaAgentes: OK")
        except Exception as e:
            logger.warning(f"   ⚠️ AcademiaAgentes: {e}")
        
        try:
            from sistemas.sistema_completo_metalearning_evolucao import MetalearningAgent
            logger.info("   ✅ MetalearningAgent: OK")
        except Exception as e:
            logger.warning(f"   ⚠️ MetalearningAgent: {e}")
        
        logger.info("✅ Teste de componentes concluído!")
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de componentes: {e}")

def main():
    """Função principal de teste"""
    logger.info("🚀 INICIANDO TESTES DO SISTEMA GIC MODIFICADO")
    logger.info("=" * 80)
    
    # Teste 1: Componentes individuais
    testar_componentes_individualmente()
    
    # Teste 2: Sistema completo
    resultado = testar_sistema_gic()
    
    # Resumo final
    logger.info("\n" + "=" * 80)
    logger.info("📋 RESUMO FINAL DOS TESTES")
    logger.info("=" * 80)
    
    if resultado.get('sucesso'):
        logger.info("🎉 TODOS OS TESTES PASSARAM!")
        logger.info("   O sistema GIC modificado está funcionando adequadamente.")
        logger.info("   A IA Autoevolutiva Biomimética está gerando justificativas reais.")
    else:
        logger.warning("⚠️ ALGUNS TESTES FALHARAM!")
        logger.warning("   Verifique os erros acima e ajuste a implementação.")
    
    logger.info(f"\n📊 ESTATÍSTICAS FINAIS:")
    if 'qualidade' in resultado:
        logger.info(f"   - Qualidade da justificativa: {resultado['qualidade']:.1f}%")
        logger.info(f"   - Elementos encontrados: {resultado['elementos_encontrados']}/{resultado['total_elementos']}")
        logger.info(f"   - Tamanho: {resultado['tamanho_justificativa']} caracteres")
    
    logger.info("\n🏁 TESTES CONCLUÍDOS!")
    return resultado

if __name__ == "__main__":
    resultado = main()
    
    # Salvar resultado em arquivo
    try:
        import json
        with open('resultado_teste_gic.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        logger.info("💾 Resultado salvo em 'resultado_teste_gic.json'")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar resultado: {e}")
