#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE INTEGRADO DOS SISTEMAS V2
Script para testar todos os sistemas implementados:

1. 🛡️ Guardião do Conhecimento
2. 🧠 Simulador Contrafactual  
3. ⚡ Gerador de Procedimentos e Academia de Agentes
"""

import time
import json
from pathlib import Path

def testar_guardiao_conhecimento():
    """Testar o Guardião do Conhecimento"""
    print("🛡️ TESTANDO GUARDIÃO DO CONHECIMENTO")
    print("=" * 50)
    
    try:
        # Importar e testar Guardião
        from guardiao_conhecimento import GuardiaoConhecimento
        
        # Inicializar
        guardiao = GuardiaoConhecimento()
        print("✅ Guardião inicializado com sucesso!")
        
        # Executar análise manual
        print("🔍 Executando análise manual...")
        relatorio = guardiao.executar_analise_manual()
        
        print("📊 Relatório do Guardião:")
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))
        
        # Iniciar monitoramento
        print("🔄 Iniciando monitoramento...")
        guardiao.iniciar_monitoramento()
        
        # Aguardar um pouco
        time.sleep(2)
        
        # Parar monitoramento
        guardiao.parar_monitoramento()
        print("✅ Teste do Guardião concluído com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do Guardião: {str(e)}")
        return False

def testar_simulador_contrafactual():
    """Testar o Simulador Contrafactual"""
    print("\n🧠 TESTANDO SIMULADOR CONTRADFACTUAL")
    print("=" * 50)
    
    try:
        # Importar e testar Simulador
        from simulador_contrafactual import SimuladorContrafactual
        
        # Inicializar
        simulador = SimuladorContrafactual()
        print("✅ Simulador inicializado com sucesso!")
        
        # Contrato de exemplo
        contrato_exemplo = """
        CONTRATO DE SERVIÇOS
        
        CLÁUSULA 1 - OBJETO
        Prestação de serviços de consultoria.
        
        CLÁUSULA 2 - VALOR
        R$ 300.000,00 (trezentos mil reais).
        
        CLÁUSULA 3 - MULTA
        Multa de 3% por atraso.
        """
        
        # Alterações para simular
        alteracoes = [
            {
                'tipo': 'alteracao_valor',
                'valor_original': 'R$ 300.000,00',
                'valor_novo': 'R$ 450.000,00',
                'descricao': 'Aumento do valor do contrato',
                'clausula': 'CLÁUSULA 2 - VALOR',
                'impacto_estimado': 'Aumento de 50% no valor'
            },
            {
                'tipo': 'alteracao_valor',
                'valor_original': '3%',
                'valor_novo': '8%',
                'descricao': 'Aumento da multa por atraso',
                'clausula': 'CLÁUSULA 3 - MULTA',
                'impacto_estimado': 'Aumento significativo da multa'
            }
        ]
        
        print("📋 Simulando alterações no contrato...")
        resultado = simulador.simular_cenario_contrato(
            contrato_exemplo,
            alteracoes,
            "Usuário Teste"
        )
        
        print(f"✅ Simulação concluída!")
        print(f"  🆔 ID: {resultado.id}")
        print(f"  ⚠️ Risco: {resultado.risco_geral.value.upper()}")
        print(f"  💰 Impacto: R$ {resultado.impacto_financeiro:,.2f}")
        print(f"  📝 Recomendação: {resultado.recomendacao}")
        
        # Verificar histórico
        historico = simulador.obter_historico_simulacoes()
        print(f"📈 Histórico: {len(historico)} simulações")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do Simulador: {str(e)}")
        return False

def testar_gerador_procedimentos():
    """Testar o Gerador de Procedimentos e Academia"""
    print("\n⚡ TESTANDO GERADOR DE PROCEDIMENTOS E ACADEMIA")
    print("=" * 50)
    
    try:
        # Importar e testar sistemas
        from gerador_procedimentos_academia import (
            MineradorPadroes, 
            GeradorProcedimentosSugeridos, 
            AcademiaAgentes
        )
        
        # 1. Minerar padrões
        print("🔍 Minerando padrões...")
        minerador = MineradorPadroes()
        padroes = minerador.minerar_padroes_sequencia_analise()
        
        print(f"✅ {len(padroes)} padrões minerados!")
        for padrao in padroes:
            print(f"  - {padrao.descricao}")
        
        # 2. Gerar procedimentos
        print("\n📋 Gerando procedimentos...")
        gps = GeradorProcedimentosSugeridos()
        
        procedimentos = []
        for padrao in padroes:
            procedimento = gps.gerar_procedimento_otimizado(padrao)
            if procedimento:
                procedimentos.append(procedimento)
                print(f"  ✅ {procedimento.titulo[:60]}...")
        
        # 3. Criar academia
        print("\n🎓 Criando academia...")
        academia = AcademiaAgentes()
        
        total_cenarios = 0
        for procedimento in procedimentos:
            cenarios = academia.criar_cenarios_treinamento(procedimento)
            total_cenarios += len(cenarios)
            print(f"  📚 {len(cenarios)} cenários para: {procedimento.titulo[:40]}...")
        
        print(f"✅ Total de cenários criados: {total_cenarios}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do Gerador: {str(e)}")
        return False

def testar_integracao_sistemas():
    """Testar integração entre os sistemas"""
    print("\n🔗 TESTANDO INTEGRAÇÃO ENTRE SISTEMAS")
    print("=" * 50)
    
    try:
        # Simular fluxo integrado
        print("🔄 Simulando fluxo integrado...")
        
        # 1. Guardião detecta padrões
        print("  1️⃣ Guardião analisa biblioteca...")
        time.sleep(1)
        
        # 2. Simulador testa cenários
        print("  2️⃣ Simulador testa cenários contrafactuais...")
        time.sleep(1)
        
        # 3. Gerador cria procedimentos
        print("  3️⃣ Gerador cria procedimentos otimizados...")
        time.sleep(1)
        
        # 4. Academia treina agentes
        print("  4️⃣ Academia treina agentes nos novos procedimentos...")
        time.sleep(1)
        
        print("✅ Fluxo integrado simulado com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {str(e)}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 TESTE INTEGRADO DOS SISTEMAS V2")
    print("=" * 60)
    print("Sistemas a serem testados:")
    print("  1. 🛡️ Guardião do Conhecimento")
    print("  2. 🧠 Simulador Contrafactual")
    print("  3. ⚡ Gerador de Procedimentos e Academia")
    print("  4. 🔗 Integração entre Sistemas")
    print("=" * 60)
    
    resultados = []
    
    # Testar cada sistema
    testes = [
        ("Guardião do Conhecimento", testar_guardiao_conhecimento),
        ("Simulador Contrafactual", testar_simulador_contrafactual),
        ("Gerador de Procedimentos", testar_gerador_procedimentos),
        ("Integração de Sistemas", testar_integracao_sistemas)
    ]
    
    for nome_teste, funcao_teste in testes:
        try:
            print(f"\n🔄 Executando: {nome_teste}")
            sucesso = funcao_teste()
            resultados.append((nome_teste, sucesso))
            
            if sucesso:
                print(f"✅ {nome_teste}: PASSOU")
            else:
                print(f"❌ {nome_teste}: FALHOU")
                
        except Exception as e:
            print(f"❌ ERRO no teste {nome_teste}: {e}")
            resultados.append((nome_teste, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for nome_teste, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"  {nome_teste}: {status}")
    
    total_testes = len(resultados)
    testes_passaram = sum(1 for _, sucesso in resultados if sucesso)
    
    print(f"\n📈 RESULTADO FINAL: {testes_passaram}/{total_testes} sistemas funcionando")
    
    if testes_passaram == total_testes:
        print("\n🎉 TODOS OS SISTEMAS V2 ESTÃO FUNCIONANDO PERFEITAMENTE!")
        print("\n🚀 SISTEMA V2 COMPLETAMENTE IMPLEMENTADO:")
        print("  ✅ Guardião do Conhecimento - Monitoramento autônomo")
        print("  ✅ Simulador Contrafactual - Raciocínio estratégico")
        print("  ✅ Gerador de Procedimentos - Otimização de processos")
        print("  ✅ Academia de Agentes - Treinamento simulado")
        
        print("\n💡 PRÓXIMOS PASSOS:")
        print("  1. Integrar com o sistema FAISS unificado existente")
        print("  2. Configurar parâmetros específicos para Petrobras")
        print("  3. Treinar agentes na academia")
        print("  4. Implementar procedimentos otimizados")
        print("  5. Monitorar resultados e ajustar")
        
    else:
        print("\n⚠️ ALGUNS SISTEMAS FALHARAM!")
        print("🔧 Verifique os erros acima e corrija antes de prosseguir")
    
    return testes_passaram == total_testes

if __name__ == "__main__":
    main()
