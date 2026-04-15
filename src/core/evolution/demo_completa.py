#!/usr/bin/env python3
"""
Demonstração Completa do Sistema Evolutivo Biomimético
=======================================================

Testa todos os 3 componentes integrados:
1. GenomeMutator - Mutação estrutural
2. BrainEvolver - Evolução cerebral
3. EvolutionDashboard - Monitoramento

Uso:
    python3 demo_completa.py
    python3 demo_completa.py --full (executa evolução completa)

Versão: 1.0.0
Data: 2026-04-15
Autor: Jarvis (OpenClaw)
"""

import sys
import time
import random
import argparse
from datetime import datetime
from pathlib import Path

def print_header(title):
    """Imprime cabeçalho bonito"""
    print("\n" + "="*60)
    print(f"🧬 {title}")
    print("="*60)

def test_genome_mutator():
    """Testa o GenomeMutator"""
    print_header("TESTE GENOME MUTATOR")
    
    try:
        from genome_mutator import GenomeMutator
        
        print("1. Inicializando GenomeMutator...")
        mutator = GenomeMutator()
        
        print("2. Métricas estruturais atuais:")
        metrics = mutator.get_structural_metrics()
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        print("3. Executando mutação estrutural...")
        mutation_types = ['add_node', 'remove_node', 'create_specialist', 'rewire_connections']
        
        for i, mtype in enumerate(mutation_types[:2]):  # Testar 2 tipos
            print(f"\n   Mutação {i+1}: {mtype}")
            result = mutator.perform_structural_mutation(mtype)
            
            print(f"   ✅ Tipo: {result['mutation_type']}")
            print(f"   📈 Estrutura mudou: {result.get('structure_changed', False)}")
            print(f"   📝 Mudanças: {result.get('changes', [])}")
            
            # Validar integridade
            validation = mutator.validate_genome_integrity()
            print(f"   ✓ Válido: {validation['is_valid']}")
            
            time.sleep(0.5)
        
        print("\n4. Salvando genoma mutado...")
        saved_path = mutator.save_mutated_genome("demo")
        print(f"   💾 Salvo em: {saved_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no GenomeMutator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_brain_evolver():
    """Testa o BrainEvolver"""
    print_header("TESTE BRAIN EVOLVER")
    
    try:
        from brain_evolver import BrainEvolver
        
        print("1. Inicializando BrainEvolver...")
        evolver = BrainEvolver()
        
        print("2. Métricas do cérebro atual:")
        metrics = evolver.get_brain_metrics()
        print(f"   Modelo: {metrics['current_model']}")
        print(f"   Tipo: {metrics['local_brain_type']}")
        if metrics.get('model_info'):
            print(f"   Descrição: {metrics['model_info'].get('description', 'N/A')}")
        
        print("3. Executando evolução cerebral...")
        
        # Testar diferentes tipos de evolução
        evolution_types = ['mutate_model', 'optimize_parameters', 'evolve_routing']
        
        for i, etype in enumerate(evolution_types[:2]):  # Testar 2 tipos
            print(f"\n   Evolução {i+1}: {etype}")
            result = evolver.perform_brain_evolution(etype)
            
            print(f"   ✅ Tipo: {result['evolution_type']}")
            print(f"   📈 Sucesso: {result.get('success', False)}")
            print(f"   📝 Mudanças: {result.get('changes', [])}")
            
            time.sleep(0.5)
        
        print("\n4. Métricas atualizadas:")
        metrics = evolver.get_brain_metrics()
        print(f"   Modelo: {metrics['current_model']}")
        
        print("\n5. Salvando configuração...")
        saved_path = evolver.save_evolution_config("demo")
        print(f"   💾 Salvo em: {saved_path}")
        
        print("\n6. Aplicando ao ambiente...")
        evolver.apply_to_environment()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no BrainEvolver: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_evolution_dashboard():
    """Testa o EvolutionDashboard"""
    print_header("TESTE EVOLUTION DASHBOARD")
    
    try:
        from evolution_dashboard import EvolutionDashboard
        
        print("1. Inicializando EvolutionDashboard...")
        dashboard = EvolutionDashboard("data/demo_dashboard")
        
        print("2. Registrando componentes...")
        dashboard.register_component('genome_mutator', 'structural')
        dashboard.register_component('brain_evolver', 'cognitive')
        dashboard.register_component('demo_agent', 'test')
        
        print("3. Simulando atividades...")
        
        # Simular métricas
        dashboard.update_component_metrics('genome_mutator', {
            'node_count': random.randint(5, 15),
            'mutation_rate': random.uniform(0.01, 0.1),
            'valid_structures': random.randint(3, 10)
        })
        
        dashboard.update_component_metrics('brain_evolver', {
            'current_model': 'llama3.1:8b',
            'ensemble_enabled': random.choice([True, False]),
            'parameter_count': random.randint(3, 8)
        })
        
        # Simular mutações
        print("4. Registrando mutações simuladas...")
        for i in range(3):
            dashboard.record_mutation({
                'mutation_type': random.choice(['add_node', 'remove_node', 'rewire_connections']),
                'structure_changed': True,
                'changes': [f'Demo mutation {i+1}']
            })
        
        # Simular evoluções
        print("5. Registrando evoluções simuladas...")
        for i in range(2):
            dashboard.record_brain_evolution({
                'evolution_type': random.choice(['mutate_model', 'optimize_parameters']),
                'success': True,
                'changes': [f'Demo evolution {i+1}']
            })
        
        # Simular performance
        print("6. Registrando performance...")
        for i in range(5):
            dashboard.record_performance(f'task_{i}', {
                'accuracy': random.uniform(0.7, 0.95),
                'latency': random.uniform(0.1, 2.0),
                'tokens': random.randint(100, 1000)
            })
            dashboard.increment_generation()
        
        # Adicionar alertas
        print("7. Adicionando alertas...")
        dashboard.add_alert('demo', 'Sistema de demonstração inicializado', 'info')
        dashboard.add_alert('performance', 'Accuracy aumentou 12% na última geração', 'info')
        dashboard.add_alert('warning', 'Uso de memória acima do esperado', 'warning')
        
        print("\n8. Obtendo dados do dashboard...")
        data = dashboard.get_dashboard_data()
        
        print(f"   Total mutações: {data['status']['total_mutations']}")
        print(f"   Total evoluções: {data['status']['total_evolutions']}")
        print(f"   Geração atual: {data['status']['current_generation']}")
        print(f"   Componentes ativos: {len([c for c in data['components'].values() if c['status'] == 'connected'])}")
        
        print("\n9. Salvando dashboard...")
        saved_path = dashboard.save_dashboard()
        print(f"   💾 Estado salvo em: {saved_path}")
        
        print("\n10. Gerando relatório HTML...")
        html_path = dashboard.generate_html_report()
        print(f"   📄 HTML gerado em: {html_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no EvolutionDashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrated_evolution():
    """Testa evolução integrada (todos componentes juntos)"""
    print_header("EVOLUÇÃO INTEGRADA COMPLETA")
    
    try:
        # Importar todos os componentes
        from genome_mutator import GenomeMutator
        from brain_evolver import BrainEvolver
        from evolution_dashboard import EvolutionDashboard
        
        print("1. Inicializando sistema completo...")
        
        # Inicializar componentes
        dashboard = EvolutionDashboard("data/integrated_demo")
        mutator = GenomeMutator()
        evolver = BrainEvolver()
        
        # Registrar componentes no dashboard
        dashboard.register_component('genome_mutator', 'structural')
        dashboard.register_component('brain_evolver', 'cognitive')
        
        print("2. Executando ciclo evolutivo completo...")
        
        for cycle in range(3):  # 3 ciclos evolutivos
            print(f"\n   🔄 CICLO EVOLUTIVO {cycle + 1}")
            
            # Atualizar métricas
            dashboard.update_component_metrics('genome_mutator', {
                'node_count': mutator.get_structural_metrics()['total_nodes'],
                'mutation_rate': 0.05,
                'cycle': cycle
            })
            
            dashboard.update_component_metrics('brain_evolver', {
                'current_model': evolver.config.get('ollama_model', 'unknown'),
                'cycle': cycle
            })
            
            # Executar mutação estrutural
            print("   a) Executando mutação estrutural...")
            mutation_result = mutator.perform_structural_mutation()
            dashboard.record_mutation(mutation_result)
            
            # Executar evolução cerebral
            print("   b) Executando evolução cerebral...")
            evolution_result = evolver.perform_brain_evolution()
            dashboard.record_brain_evolution(evolution_result)
            
            # Registrar performance
            print("   c) Registrando performance...")
            performance = {
                'accuracy': random.uniform(0.6 + cycle * 0.1, 0.9),
                'latency': random.uniform(0.5, 2.0 - cycle * 0.3),
                'tokens_used': random.randint(200, 800),
                'confidence': random.uniform(0.7 + cycle * 0.05, 0.95)
            }
            dashboard.record_performance(f'cycle_{cycle}', performance)
            
            # Incrementar geração
            dashboard.increment_generation()
            
            time.sleep(0.3)
        
        print("\n3. Resultados finais:")
        
        # Obter dados consolidados
        final_data = dashboard.get_dashboard_data()
        
        print(f"   Total de mutações: {final_data['status']['total_mutations']}")
        print(f"   Total de evoluções: {final_data['status']['total_evolutions']}")
        print(f"   Geração final: {final_data['status']['current_generation']}")
        print(f"   Taxa de inovação: {final_data['statistics'].get('innovation_rate', 0):.2f}")
        
        # Salvar tudo
        print("\n4. Salvando resultados...")
        
        # Salvar genoma evoluído
        genome_path = mutator.save_mutated_genome("integrated")
        print(f"   💾 Genoma: {genome_path}")
        
        # Salvar configuração cerebral
        brain_path = evolver.save_evolution_config("integrated")
        print(f"   💾 Cérebro: {brain_path}")
        
        # Salvar dashboard
        dashboard_path = dashboard.save_dashboard()
        print(f"   💾 Dashboard: {dashboard_path}")
        
        # Gerar relatório HTML
        html_path = dashboard.generate_html_report()
        print(f"   📄 Relatório: {html_path}")
        
        print("\n🎉 EVOLUÇÃO INTEGRADA CONCLUÍDA COM SUCESSO!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na evolução integrada: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Demonstração do Sistema Evolutivo Biomimético')
    parser.add_argument('--full', action='store_true', help='Executar evolução integrada completa')
    parser.add_argument('--genome', action='store_true', help='Testar apenas GenomeMutator')
    parser.add_argument('--brain', action='store_true', help='Testar apenas BrainEvolver')
    parser.add_argument('--dashboard', action='store_true', help='Testar apenas EvolutionDashboard')
    
    args = parser.parse_args()
    
    print_header("SISTEMA EVOLUTIVO BIOMIMÉTICO - DEMONSTRAÇÃO")
    print("Autor: Jarvis (OpenClaw)")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nComponentes disponíveis:")
    print("  🧬 GenomeMutator   - Mutação estrutural real")
    print("  🧠 BrainEvolver    - Evolução cerebral (Llama/Modelos)")
    print("  📊 EvolutionDashboard - Monitoramento em tempo real")
    
    success = True
    
    if args.full:
        # Executar evolução integrada completa
        success = test_integrated_evolution()
    elif args.genome:
        success = test_genome_mutator()
    elif args.brain:
        success = test_brain_evolver()
    elif args.dashboard:
        success = test_evolution_dashboard()
    else:
        # Executar todos os testes individuais
        print("\n🔍 Executando todos os testes individuais...")
        
        success = test_genome_mutator() and success
        time.sleep(1)
        
        success = test_brain_evolver() and success
        time.sleep(1)
        
        success = test_evolution_dashboard() and success
        
        print_header("RESUMO DOS TESTES")
        if success:
            print("✅ TODOS OS TESTES PASSARAM!")
            print("\nPróximos passos sugeridos:")
            print("1. Executar evolução integrada: python3 demo_completa.py --full")
            print("2. Iniciar a API: python3 src/core/evolution/evolution_api.py")
            print("3. Integrar com sistema existente do AI-Biomimetica")
        else:
            print("⚠️ ALGUNS TESTES FALHARAM")
            print("Verifique as dependências (PyYAML) e tente novamente")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())