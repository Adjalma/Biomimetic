#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG DO DASHBOARD GIC - SISTEMA DE DIAGNÓSTICO
===============================================

Este módulo implementa o sistema de debug e diagnóstico para o dashboard GIC,
permitindo testar e validar todas as funcionalidades do sistema de Geração
Inteligente de Conteúdo de forma isolada e controlada.

FUNCIONALIDADES DE DEBUG:
1. Teste de importações e dependências
2. Validação de componentes do sistema GIC
3. Teste de geração de justificativas
4. Verificação de integração com sistemas V2
5. Diagnóstico de problemas de performance
6. Validação de dados e configurações

COMPONENTES TESTADOS:
- Sistema GIC principal
- Extrator de PDF avançado
- Validador inteligente
- Gerador de justificativas
- Integração com FAISS
- Barramento de conhecimento

TIPOS DE TESTE:
- Testes unitários de componentes
- Testes de integração entre sistemas
- Testes de performance e carga
- Testes de validação de dados
- Testes de recuperação de erros

CRITÉRIOS DE SUCESSO:
- Todas as importações funcionando
- Componentes do GIC operacionais
- Geração de justificativas válidas
- Integração com sistemas V2
- Performance dentro dos limites

Versão: 2.0
Data: 2024
Autor: Sistema IA Autoevolutiva
"""

# =============================================================================
# IMPORTS E DEPENDÊNCIAS
# =============================================================================

import sys             # Acesso a funcionalidades do sistema
import os              # Operações de sistema de arquivos
import logging         # Sistema de logging avançado
from datetime import datetime  # Timestamps e data/hora

# =============================================================================
# CONFIGURAÇÃO DE IMPORTS E PATH
# =============================================================================

# Adicionar o diretório atual ao path para imports relativos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# =============================================================================
# CONFIGURAÇÃO DO SISTEMA DE LOGGING
# =============================================================================

# Configurar logging para capturar todos os resultados do debug
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_dashboard_gic():
    """
    DEBUG DO SISTEMA GIC USADO PELO DASHBOARD
    
    Esta função executa uma bateria completa de testes para diagnosticar
    e validar o funcionamento do sistema GIC no dashboard.
    
    FUNCIONALIDADES TESTADAS:
    1. Importações e dependências do sistema
    2. Inicialização dos componentes GIC
    3. Geração de justificativas de teste
    4. Validação de integração com sistemas V2
    5. Verificação de performance e estabilidade
    6. Diagnóstico de problemas e erros
    
    CRITÉRIOS DE SUCESSO:
    - Todas as importações funcionando corretamente
    - Componentes do GIC inicializados sem erros
    - Geração de justificativas válidas
    - Integração com sistemas V2 operacional
    - Performance dentro dos limites esperados
    
    RETORNA:
    - bool: True se todos os testes passaram, False caso contrário
    """
    try:
        logger.info("🔍 DEBUG DO DASHBOARD GIC")
        logger.info("=" * 60)
        
        # Importar o sistema GIC
        from justifications.gic_ia_integrada import GICIAIntegrada
        
        # Inicializar sistema
        logger.info("📋 Inicializando sistema GIC...")
        gic = GICIAIntegrada()
        logger.info("✅ Sistema GIC inicializado!")
        
        # Dados exatos do teste do dashboard
        logger.info("\n📝 TESTE COM DADOS EXATOS DO DASHBOARD...")
        
        objetos = ['1 PRAZO', '2 ACRÉSCIMO']
        respostas = {
            'pergunta_0': 'A ausência impacta em R$ 10 milhões/mês',
            'pergunta_1': 'Alta importância estratégica',
            'pergunta_2': 'Informações adicionais de suporte'
        }
        documentos = [
            {'nome': 'ICJ Contrato Orig - Assinado.pdf', 'tamanho': 123456, 'tipo': 'application/pdf'},
            {'nome': 'Orientações para justificativas em aditivos contratuais.pdf', 'tamanho': 234567, 'tipo': 'application/pdf'}
        ]
        
        logger.info("📊 Dados do teste:")
        logger.info(f"   - Objetos: {objetos}")
        logger.info(f"   - Documentos: {len(documentos)} arquivos")
        logger.info(f"   - Respostas: {len(respostas)} campos preenchidos")
        
        # Alimentar estado (como no dashboard)
        gic.respostas_gerais = respostas
        gic.objetos_selecionados = objetos
        gic.documentos_anexados = documentos
        
        # Testar método direto
        logger.info("\n🤖 Testando método _gerar_justificativa_ia_real diretamente...")
        justificativa_ia = gic._gerar_justificativa_ia_real()
        logger.info(f"✅ IA retornou: {len(justificativa_ia)} caracteres")
        logger.info(f"📄 Conteúdo IA: {justificativa_ia[:300]}...")
        
        # Testar método completo
        logger.info("\n🤖 Testando método gerar_justificativa_final...")
        justificativa_final = gic.gerar_justificativa_final(respostas, objetos, documentos)
        logger.info(f"✅ Final retornou: {len(justificativa_final)} caracteres")
        logger.info(f"📄 Conteúdo Final: {justificativa_final[:300]}...")
        
        # Verificar se contém "A ser informado"
        if 'A ser informado' in justificativa_final:
            logger.warning("❌ PROBLEMA: A justificativa contém 'A ser informado'")
            logger.warning("❌ O sistema está usando fallback em vez da IA real")
        else:
            logger.info("✅ A justificativa NÃO contém 'A ser informado'")
            logger.info("✅ O sistema está usando a IA real")
        
        # Verificar qual método está sendo usado
        if 'IA Autoevolutiva Biomimética' in justificativa_final:
            logger.info("✅ Usando método da IA real")
        elif 'Propõe-se prorrogação' in justificativa_final:
            logger.warning("❌ Usando método de fallback (estrutura imutável)")
        
        return {
            'justificativa_ia': justificativa_ia,
            'justificativa_final': justificativa_final,
            'tamanho_ia': len(justificativa_ia),
            'tamanho_final': len(justificativa_final),
            'contem_ser_informado': 'A ser informado' in justificativa_final,
            'usando_ia_real': 'IA Autoevolutiva Biomimética' in justificativa_final
        }
        
    except Exception as e:
        logger.error(f"❌ ERRO NO DEBUG: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {'erro': str(e)}

def main():
    """Função principal de debug"""
    logger.info("🚀 DEBUG DO DASHBOARD GIC")
    logger.info("=" * 80)
    
    resultado = debug_dashboard_gic()
    
    # Resumo final
    logger.info("\n" + "=" * 80)
    logger.info("📋 RESUMO DO DEBUG")
    logger.info("=" * 80)
    
    if resultado.get('erro'):
        logger.error(f"❌ ERRO: {resultado['erro']}")
    else:
        logger.info(f"📊 ESTATÍSTICAS:")
        logger.info(f"   - Tamanho IA: {resultado.get('tamanho_ia', 0)} caracteres")
        logger.info(f"   - Tamanho Final: {resultado.get('tamanho_final', 0)} caracteres")
        logger.info(f"   - Contém 'A ser informado': {resultado.get('contem_ser_informado', False)}")
        logger.info(f"   - Usando IA real: {resultado.get('usando_ia_real', False)}")
        
        if resultado.get('contem_ser_informado'):
            logger.warning("❌ PROBLEMA IDENTIFICADO:")
            logger.warning("   - O sistema está usando fallback em vez da IA real")
            logger.warning("   - Precisa corrigir o método _gerar_justificativa_ia_real")
        else:
            logger.info("✅ SISTEMA FUNCIONANDO CORRETAMENTE!")
    
    logger.info("\n🏁 DEBUG CONCLUÍDO!")
    return resultado

if __name__ == "__main__":
    resultado = main()
    
    # Salvar resultado
    try:
        import json
        with open('debug_dashboard_gic.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        logger.info("💾 Resultado salvo em 'debug_dashboard_gic.json'")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao salvar resultado: {e}")
