#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Real da Geração de Justificativas
=======================================
Testa o sistema GIC com dados reais para verificar se está gerando justificativas adequadas
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

def testar_justificativa_real():
    """Testa a geração de justificativas com dados reais"""
    try:
        logger.info("🔍 TESTANDO GERAÇÃO DE JUSTIFICATIVAS REAIS")
        logger.info("=" * 60)
        
        # Importar o sistema GIC
        from justifications.gic_ia_integrada import GICIAIntegrada
        
        # Inicializar sistema
        logger.info("📋 Inicializando sistema GIC...")
        gic = GICIAIntegrada()
        logger.info("✅ Sistema GIC inicializado!")
        
        # Teste com dados reais de um aditivo
        logger.info("\n📝 TESTE COM DADOS REAIS DE ADITIVO...")
        
        # Dados reais de um aditivo de PRAZO
        respostas_reais = {
            'pergunta_0': 'R$ 2.5 milhões em impactos financeiros mensais',
            'pergunta_1': 'Contrato essencial para continuidade operacional da Refinaria',
            'pergunta_2': 'Documentação técnica e parecer jurídico anexados',
            'fato_superveniente': 'Atraso na nova contratação devido a mudanças regulatórias',
            'demanda_continuada': 'sim',
            'aporte_proporcional': 'sim',
            'motivo_prorrogacao': '1.1 ATRASO NA NOVA CONTRAÇÃO',
            'atraso_motivo': 'Mudanças na legislação ambiental exigiram revisão do projeto',
            'atraso_sup': 'SUP 2024/001 - Oportunidade 12345'
        }
        
        objetos_reais = ['1 PRAZO']
        documentos_reais = [
            'ICJ_Contrato_Refinaria_2024.pdf',
            'Parecer_Juridico_Aditivo.pdf',
            'Documentacao_Tecnica_Ambiental.pdf'
        ]
        
        logger.info("📊 Dados do teste:")
        logger.info(f"   - Objetos: {objetos_reais}")
        logger.info(f"   - Documentos: {len(documentos_reais)} arquivos")
        logger.info(f"   - Respostas: {len(respostas_reais)} campos preenchidos")
        
        # Gerar justificativa
        logger.info("\n🤖 Gerando justificativa com IA...")
        justificativa = gic.gerar_justificativa_final(
            respostas_gerais=respostas_reais,
            objetos_selecionados=objetos_reais,
            documentos_anexados=documentos_reais
        )
        
        logger.info("✅ Justificativa gerada!")
        logger.info(f"   Tamanho: {len(justificativa)} caracteres")
        
        # Análise da justificativa
        logger.info("\n🔍 ANÁLISE DA JUSTIFICATIVA:")
        logger.info("-" * 40)
        
        # Verificar se contém dados do ICJ
        if 'ICJ' in justificativa:
            logger.info("✅ Contém dados do ICJ")
        else:
            logger.warning("❌ NÃO contém dados do ICJ")
        
        # Verificar se contém empresa
        if 'empresa' in justificativa.lower():
            logger.info("✅ Menciona empresa")
        else:
            logger.warning("❌ NÃO menciona empresa")
        
        # Verificar se contém objeto
        if 'objetiva' in justificativa.lower() or 'objeto' in justificativa.lower() or 'para ' in justificativa.lower():
            logger.info("✅ Menciona objeto do contrato")
        else:
            logger.warning("❌ NÃO menciona objeto do contrato")
        
        # Verificar se contém data
        if any(termo in justificativa.lower() for termo in ['data', 'término', 'prazo', '2024', '2025']):
            logger.info("✅ Menciona data/prazo")
        else:
            logger.warning("❌ NÃO menciona data/prazo")
        
        # Verificar se contém valores financeiros
        if any(termo in justificativa.lower() for termo in ['milhões', 'milhares', 'r$', 'impacto']):
            logger.info("✅ Menciona valores financeiros")
        else:
            logger.warning("❌ NÃO menciona valores financeiros")
        
        # Verificar se contém análise específica
        if any(termo in justificativa.lower() for termo in ['prorrogação', 'atraso', 'continuidade']):
            logger.info("✅ Contém análise específica do PRAZO")
        else:
            logger.warning("❌ NÃO contém análise específica do PRAZO")
        
        # Mostrar a justificativa completa
        logger.info("\n📄 JUSTIFICATIVA GERADA:")
        logger.info("=" * 60)
        logger.info(justificativa)
        logger.info("=" * 60)
        
        # Avaliação final
        logger.info("\n🎯 AVALIAÇÃO FINAL:")
        logger.info("-" * 40)
        
        problemas = []
        if 'A ser informado' in justificativa:
            problemas.append("Contém 'A ser informado'")
        if 'ICJ' not in justificativa:
            problemas.append("Não extraiu dados do ICJ")
        if 'empresa' not in justificativa.lower():
            problemas.append("Não menciona empresa")
        if 'objetiva' not in justificativa.lower():
            problemas.append("Não menciona objeto")
        
        if problemas:
            logger.warning("❌ PROBLEMAS ENCONTRADOS:")
            for problema in problemas:
                logger.warning(f"   - {problema}")
            logger.warning("❌ A justificativa NÃO está adequada para o dashboard")
        else:
            logger.info("✅ A justificativa está adequada!")
            logger.info("✅ Pode ser usada no dashboard")
        
        return {
            'justificativa': justificativa,
            'tamanho': len(justificativa),
            'problemas': problemas,
            'adequada': len(problemas) == 0
        }
        
    except Exception as e:
        logger.error(f"❌ ERRO NO TESTE: {e}")
        return {'erro': str(e), 'adequada': False}

def main():
    """Função principal de teste"""
    logger.info("🚀 TESTANDO GERAÇÃO DE JUSTIFICATIVAS REAIS")
    logger.info("=" * 80)
    
    resultado = testar_justificativa_real()
    
    # Resumo final
    logger.info("\n" + "=" * 80)
    logger.info("📋 RESUMO FINAL")
    logger.info("=" * 80)
    
    if resultado.get('adequada'):
        logger.info("🎉 A JUSTIFICATIVA ESTÁ ADEQUADA!")
        logger.info("   ✅ Contém dados do ICJ")
        logger.info("   ✅ Menciona empresa e objeto")
        logger.info("   ✅ Análise específica do contexto")
        logger.info("   ✅ Pode ser usada no dashboard")
    else:
        logger.warning("⚠️ A JUSTIFICATIVA NÃO ESTÁ ADEQUADA")
        logger.warning("   - Problemas encontrados:")
        for problema in resultado.get('problemas', []):
            logger.warning(f"     * {problema}")
        logger.warning("   - Precisa ser corrigida")
    
    logger.info(f"\n📊 ESTATÍSTICAS:")
    logger.info(f"   - Tamanho: {resultado.get('tamanho', 0)} caracteres")
    logger.info(f"   - Adequada: {resultado.get('adequada', False)}")
    logger.info(f"   - Problemas: {len(resultado.get('problemas', []))}")
    
    logger.info("\n🏁 TESTE CONCLUÍDO!")
    return resultado

if __name__ == "__main__":
    resultado = main()
    
    # Salvar resultado
    try:
        import json
        with open('resultado_justificativa_real.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        logger.info("💾 Resultado salvo em 'resultado_justificativa_real.json'")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar resultado: {e}")
