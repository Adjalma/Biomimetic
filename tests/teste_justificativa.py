#!/usr/bin/env python3
"""
Teste de Geração de Justificativa - GIC IA
==========================================

Script para testar se a IA consegue gerar justificativas adequadas
"""

import sys
import os
import json
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

try:
    from gic_ia_integrada import GICIAIntegrada
    print("✅ GICIAIntegrada importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar GICIAIntegrada: {e}")
    sys.exit(1)

def testar_geracao_justificativa():
    """Testa se a IA consegue gerar uma justificativa"""
    print("\n🧪 TESTE DE GERAÇÃO DE JUSTIFICATIVA")
    print("=" * 50)
    
    try:
        # Inicializar o GIC
        print("1. Inicializando GIC...")
        gic = GICIAIntegrada()
        print("✅ GIC inicializado com sucesso")
        
        # Dados de teste
        objetos_selecionados = ["1 PRAZO", "2 ACRÉSCIMO"]
        respostas_objetos = {
            "1 PRAZO": {
                "fato_superveniente": "Necessidade de prorrogação devido a atrasos na contratação de novos fornecedores",
                "demanda_continuada": "sim",
                "aporte_proporcional": "sim",
                "motivo_prorrogacao": "1.1 ATRASO NA NOVA CONTRAÇÃO",
                "atraso_motivo": "Problemas na documentação dos fornecedores",
                "atraso_sup": "SUP 2025/4433, Oportunidade 70004455"
            },
            "2 ACRÉSCIMO": {
                "fato_superveniente": "Mudanças na legislação vigente exigem novos itens",
                "tipo_acrescimo": "Inclusão de novo item na PPU",
                "supera_25": "sim",
                "parecer_juridico": "não"
            }
        }
        respostas_gerais = {
            "pergunta_0": "Impacto financeiro de 50 milhões por mês",
            "pergunta_1": "Estratégico para a região",
            "pergunta_2": "Não há informações adicionais"
        }
        documentos_anexados = [
            {"nome": "ICJ_Contrato_Teste.pdf", "tipo": "application/pdf", "tamanho": 1000000},
            {"nome": "Aditivo_Anterior.pdf", "tipo": "application/pdf", "tamanho": 500000}
        ]
        
        print("2. Dados de teste preparados")
        print(f"   - Objetos: {objetos_selecionados}")
        print(f"   - Documentos: {len(documentos_anexados)}")
        
        # Testar geração da justificativa
        print("3. Gerando justificativa...")
        justificativa = gic.gerar_justificativa_final(
            objetos_selecionados=objetos_selecionados,
            respostas_objetos=respostas_objetos,
            respostas_gerais=respostas_gerais,
            documentos_anexados=documentos_anexados
        )
        
        print("✅ Justificativa gerada com sucesso!")
        print("\n" + "="*80)
        print("JUSTIFICATIVA GERADA:")
        print("="*80)
        print(justificativa)
        print("="*80)
        
        # Analisar qualidade da justificativa
        print("\n4. Analisando qualidade da justificativa...")
        analisar_qualidade(justificativa)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def analisar_qualidade(justificativa):
    """Analisa a qualidade da justificativa gerada"""
    print("\n📊 ANÁLISE DE QUALIDADE:")
    
    # Verificar se contém seções essenciais
    secoes_essenciais = [
        "JUSTIFICATIVA PARA ADITIVO CONTRATUAL",
        "ANÁLISE INTELIGENTE DOS DOCUMENTOS",
        "1 PRAZO:",
        "2 ACRÉSCIMO:",
        "ANÁLISE DE IMPACTOS E RISCOS",
        "CONCLUSÃO INTELIGENTE",
        "Solicitações de Melhorias, críticas e/ou elogios"
    ]
    
    secoes_encontradas = 0
    for secao in secoes_essenciais:
        if secao in justificativa:
            print(f"✅ {secao}")
            secoes_encontradas += 1
        else:
            print(f"❌ {secao}")
    
    # Verificar se contém dados dos sistemas especialistas
    sistemas_especialistas = [
        "Barramento de Conhecimento Unificado",
        "Sistema FAISS Integrado",
        "Leis Imutáveis",
        "Guardião do Conhecimento",
        "Simulador Contrafactual",
        "Academia de Agentes",
        "Agente de Metalearning"
    ]
    
    sistemas_encontrados = 0
    print(f"\n🔧 SISTEMAS ESPECIALISTAS:")
    for sistema in sistemas_especialistas:
        if sistema in justificativa:
            print(f"✅ {sistema}")
            sistemas_encontrados += 1
        else:
            print(f"❌ {sistema}")
    
    # Verificar se contém dados reais das respostas
    dados_reais = [
        "Necessidade de prorrogação",
        "Mudanças na legislação",
        "50 milhões por mês",
        "Estratégico para a região"
    ]
    
    dados_encontrados = 0
    print(f"\n📝 DADOS REAIS DAS RESPOSTAS:")
    for dado in dados_reais:
        if dado in justificativa:
            print(f"✅ {dado}")
            dados_encontrados += 1
        else:
            print(f"❌ {dado}")
    
    # Calcular score de qualidade
    total_verificacoes = len(secoes_essenciais) + len(sistemas_especialistas) + len(dados_reais)
    verificacoes_ok = secoes_encontradas + sistemas_encontrados + dados_encontrados
    score_qualidade = (verificacoes_ok / total_verificacoes) * 100
    
    print(f"\n📈 SCORE DE QUALIDADE: {score_qualidade:.1f}%")
    
    if score_qualidade >= 80:
        print("🎉 EXCELENTE! A IA está gerando justificativas de alta qualidade!")
    elif score_qualidade >= 60:
        print("👍 BOM! A IA está gerando justificativas adequadas.")
    elif score_qualidade >= 40:
        print("⚠️ REGULAR. A IA precisa de melhorias.")
    else:
        print("❌ RUIM. A IA não está gerando justificativas adequadas.")
    
    return score_qualidade

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE DE GERAÇÃO DE JUSTIFICATIVA")
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    sucesso = testar_geracao_justificativa()
    
    if sucesso:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU!")
        sys.exit(1)
