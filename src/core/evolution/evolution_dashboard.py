"""
EvolutionDashboard - Dashboard de Monitoramento Evolutivo
=========================================================

Monitora em tempo real as evoluções do sistema:
1. Mutações estruturais no genoma
2. Evoluções do cérebro (modelos)
3. Métricas de performance
4. Histórico de evoluções

Versão: 1.0.0
Data: 2026-04-15
Autor: Jarvis (OpenClaw)
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvolutionDashboard:
    """Dashboard para monitoramento evolutivo em tempo real"""
    
    def __init__(self, storage_path: str = "data/evolution_dashboard"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Estado do dashboard
        self.state = {
            'start_time': datetime.now().isoformat(),
            'total_mutations': 0,
            'total_evolutions': 0,
            'current_generation': 0,
            'performance_history': deque(maxlen=100),
            'structural_changes_history': deque(maxlen=50),
            'brain_evolution_history': deque(maxlen=50),
            'alerts': deque(maxlen=20),
            'metrics_snapshots': deque(maxlen=100)
        }
        
        # Componentes monitorados
        self.components = {
            'genome_mutator': {'status': 'disconnected', 'last_update': None},
            'brain_evolver': {'status': 'disconnected', 'last_update': None},
            'evolution_engine': {'status': 'disconnected', 'last_update': None}
        }
        
        logger.info("📊 EvolutionDashboard inicializado")
    
    def register_component(self, component_name: str, component_type: str = None):
        """Registra um componente para monitoramento"""
        if component_name not in self.components:
            self.components[component_name] = {
                'status': 'connected',
                'type': component_type or component_name,
                'last_update': datetime.now().isoformat(),
                'metrics': {}
            }
        else:
            self.components[component_name]['status'] = 'connected'
            self.components[component_name]['last_update'] = datetime.now().isoformat()
        
        logger.info(f"📋 Componente registrado: {component_name}")
    
    def update_component_metrics(self, component_name: str, metrics: Dict[str, Any]):
        """Atualiza métricas de um componente"""
        if component_name not in self.components:
            self.register_component(component_name)
        
        self.components[component_name]['metrics'] = metrics
        self.components[component_name]['last_update'] = datetime.now().isoformat()
        
        # Registrar snapshot
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'component': component_name,
            'metrics': metrics
        }
        self.state['metrics_snapshots'].append(snapshot)
    
    def record_mutation(self, mutation_data: Dict[str, Any]):
        """Registra uma mutação estrutural"""
        self.state['total_mutations'] += 1
        
        record = {
            'id': f"mutation_{self.state['total_mutations']}",
            'timestamp': datetime.now().isoformat(),
            'type': mutation_data.get('mutation_type', 'unknown'),
            'data': mutation_data
        }
        
        self.state['structural_changes_history'].append(record)
        
        # Verificar se é uma mutação significativa
        if mutation_data.get('structure_changed', False):
            self.add_alert('structural_change', 
                          f"📈 Mutação estrutural significativa detectada: {mutation_data.get('mutation_type')}")
        
        logger.info(f"📝 Mutação registrada: {mutation_data.get('mutation_type', 'unknown')}")
    
    def record_brain_evolution(self, evolution_data: Dict[str, Any]):
        """Registra uma evolução cerebral"""
        self.state['total_evolutions'] += 1
        
        record = {
            'id': f"evolution_{self.state['total_evolutions']}",
            'timestamp': datetime.now().isoformat(),
            'type': evolution_data.get('evolution_type', 'unknown'),
            'data': evolution_data
        }
        
        self.state['brain_evolution_history'].append(record)
        
        # Verificar se é uma evolução significativa
        if evolution_data.get('success', False):
            model_change = evolution_data.get('changes', [])
            if model_change:
                self.add_alert('brain_evolution', 
                              f"🧠 Evolução cerebral: {', '.join(model_change)}")
        
        logger.info(f"📝 Evolução cerebral registrada: {evolution_data.get('evolution_type', 'unknown')}")
    
    def record_performance(self, task_type: str, metrics: Dict[str, float]):
        """Registra performance de uma tarefa"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'metrics': metrics,
            'generation': self.state['current_generation']
        }
        
        self.state['performance_history'].append(record)
        
        # Análise de tendências
        if len(self.state['performance_history']) > 10:
            self._analyze_performance_trends()
    
    def increment_generation(self):
        """Incrementa a geração atual"""
        self.state['current_generation'] += 1
        
        # Registrar checkpoint a cada 10 gerações
        if self.state['current_generation'] % 10 == 0:
            self._save_checkpoint()
        
        logger.info(f"🔄 Geração {self.state['current_generation']}")
    
    def add_alert(self, alert_type: str, message: str, level: str = 'info'):
        """Adiciona alerta ao dashboard"""
        alert = {
            'id': f"alert_{len(self.state['alerts']) + 1}",
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'level': level,
            'message': message
        }
        
        self.state['alerts'].append(alert)
        
        if level in ['warning', 'error']:
            logger.warning(f"⚠️ Alerta {level}: {message}")
        else:
            logger.info(f"ℹ️ Alerta: {message}")
    
    def _analyze_performance_trends(self):
        """Analisa tendências de performance"""
        history = list(self.state['performance_history'])
        if len(history) < 5:
            return
        
        # Últimas 5 execuções
        recent = history[-5:]
        
        # Calcular média de accuracy
        accuracies = [r['metrics'].get('accuracy', 0) for r in recent]
        avg_accuracy = sum(accuracies) / len(accuracies)
        
        # Verificar degradação
        if len(history) >= 10:
            older = history[-10:-5]
            older_acc = [r['metrics'].get('accuracy', 0) for r in older]
            avg_older = sum(older_acc) / len(older_acc) if older_acc else 0
            
            if avg_accuracy < avg_older * 0.9:  # 10% de degradação
                self.add_alert('performance_degradation',
                              f"📉 Degradação de performance detectada: {avg_older:.2f} → {avg_accuracy:.2f}",
                              level='warning')
        
        # Verificar melhoria significativa
        if avg_accuracy > 0.8:
            self.add_alert('performance_improvement',
                          f"📈 Alta performance alcançada: {avg_accuracy:.2f}",
                          level='info')
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados completos do dashboard"""
        # Calcular estatísticas
        uptime = datetime.now() - datetime.fromisoformat(self.state['start_time'])
        
        # Status dos componentes
        component_status = {}
        for name, data in self.components.items():
            last_update = datetime.fromisoformat(data['last_update']) if data['last_update'] else None
            is_stale = last_update and (datetime.now() - last_update > timedelta(minutes=5))
            
            component_status[name] = {
                'status': 'stale' if is_stale else data['status'],
                'last_update': data['last_update'],
                'type': data.get('type', 'unknown'),
                'metrics': data.get('metrics', {})
            }
        
        # Resumo das mutações
        recent_mutations = list(self.state['structural_changes_history'])[-5:]
        recent_evolutions = list(self.state['brain_evolution_history'])[-5:]
        recent_alerts = list(self.state['alerts'])[-10:]
        
        return {
            'status': {
                'uptime_seconds': uptime.total_seconds(),
                'total_mutations': self.state['total_mutations'],
                'total_evolutions': self.state['total_evolutions'],
                'current_generation': self.state['current_generation'],
                'performance_history_count': len(self.state['performance_history']),
                'component_count': len(self.components)
            },
            'components': component_status,
            'recent_activity': {
                'mutations': recent_mutations,
                'evolutions': recent_evolutions,
                'alerts': recent_alerts
            },
            'statistics': self._calculate_statistics(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calcula estatísticas do sistema evolutivo"""
        mutations = list(self.state['structural_changes_history'])
        evolutions = list(self.state['brain_evolution_history'])
        performance = list(self.state['performance_history'])
        
        # Contar tipos de mutação
        mutation_types = {}
        for mut in mutations:
            mtype = mut['data'].get('mutation_type', 'unknown')
            mutation_types[mtype] = mutation_types.get(mtype, 0) + 1
        
        # Contar tipos de evolução
        evolution_types = {}
        for evo in evolutions:
            etype = evo['data'].get('evolution_type', 'unknown')
            evolution_types[etype] = evolution_types.get(etype, 0) + 1
        
        # Calcular performance média
        avg_performance = {}
        if performance:
            # Agregar métricas por tipo de tarefa
            task_metrics = {}
            for perf in performance:
                task_type = perf['task_type']
                if task_type not in task_metrics:
                    task_metrics[task_type] = []
                task_metrics[task_type].append(perf['metrics'])
            
            # Calcular médias
            for task_type, metrics_list in task_metrics.items():
                if metrics_list:
                    avg = {}
                    for key in metrics_list[0].keys():
                        values = [m.get(key, 0) for m in metrics_list]
                        avg[key] = sum(values) / len(values)
                    avg_performance[task_type] = avg
        
        return {
            'mutation_types': mutation_types,
            'evolution_types': evolution_types,
            'avg_performance': avg_performance,
            'success_rate': self._calculate_success_rate(),
            'innovation_rate': len(mutations) / max(1, self.state['current_generation'])
        }
    
    def _calculate_success_rate(self) -> float:
        """Calcula taxa de sucesso das evoluções"""
        evolutions = list(self.state['brain_evolution_history'])
        if not evolutions:
            return 0.0
        
        successful = sum(1 for evo in evolutions if evo['data'].get('success', False))
        return successful / len(evolutions)
    
    def _save_checkpoint(self):
        """Salva checkpoint do dashboard"""
        checkpoint_file = self.storage_path / f"checkpoint_gen_{self.state['current_generation']}.json"
        data = {
            'state': self.state,
            'components': self.components,
            'timestamp': datetime.now().isoformat(),
            'generation': self.state['current_generation']
        }
        
        # Converter deque para list para serialização
        data['state'] = self._deque_to_dict(data['state'])
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"💾 Checkpoint salvo: {checkpoint_file}")
    
    def _deque_to_dict(self, obj):
        """Converte deques em listas para serialização JSON"""
        if isinstance(obj, dict):
            return {k: self._deque_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, deque):
            return list(obj)
        elif isinstance(obj, (list, tuple)):
            return [self._deque_to_dict(item) for item in obj]
        else:
            return obj
    
    def save_dashboard(self):
        """Salva estado completo do dashboard"""
        dashboard_file = self.storage_path / "dashboard_state.json"
        data = self.get_dashboard_data()
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"💾 Dashboard salvo: {dashboard_file}")
        return str(dashboard_file)
    
    def generate_html_report(self) -> str:
        """Gera relatório HTML do dashboard"""
        data = self.get_dashboard_data()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Evolution Dashboard - IA Biomimética</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat {{ text-align: center; padding: 15px; border-radius: 8px; }}
                .stat.mutations {{ background: #e3f2fd; }}
                .stat.evolutions {{ background: #f3e5f5; }}
                .stat.performance {{ background: #e8f5e8; }}
                .stat.generation {{ background: #fff3e0; }}
                .alert {{ padding: 10px; margin: 10px 0; border-left: 4px solid; border-radius: 4px; }}
                .alert.info {{ background: #e3f2fd; border-color: #2196f3; }}
                .alert.warning {{ background: #fff3cd; border-color: #ffc107; }}
                .alert.error {{ background: #f8d7da; border-color: #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f8f9fa; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧬 Evolution Dashboard - IA Biomimética</h1>
                    <p>Monitoramento em tempo real do sistema evolutivo</p>
                    <p class="timestamp">Atualizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="card">
                    <h2>📊 Estatísticas Gerais</h2>
                    <div class="stats-grid">
                        <div class="stat mutations">
                            <h3>Mutações</h3>
                            <p style="font-size: 24px; font-weight: bold;">{data['status']['total_mutations']}</p>
                        </div>
                        <div class="stat evolutions">
                            <h3>Evoluções</h3>
                            <p style="font-size: 24px; font-weight: bold;">{data['status']['total_evolutions']}</p>
                        </div>
                        <div class="stat generation">
                            <h3>Geração</h3>
                            <p style="font-size: 24px; font-weight: bold;">{data['status']['current_generation']}</p>
                        </div>
                        <div class="stat performance">
                            <h3>Uptime</h3>
                            <p style="font-size: 24px; font-weight: bold;">{int(data['status']['uptime_seconds'] / 3600)}h</p>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🔧 Componentes do Sistema</h2>
                    <table>
                        <tr>
                            <th>Componente</th>
                            <th>Status</th>
                            <th>Última Atualização</th>
                            <th>Métricas</th>
                        </tr>
        """
        
        for name, comp in data['components'].items():
            metrics_str = ', '.join([f"{k}: {v}" for k, v in comp['metrics'].items()][:2])
            html += f"""
                        <tr>
                            <td>{name}</td>
                            <td><span style="color: {'green' if comp['status'] == 'connected' else 'orange'}">{comp['status']}</span></td>
                            <td>{comp['last_update'] or 'N/A'}</td>
                            <td>{metrics_str or 'N/A'}</td>
                        </tr>
            """
        
        html += """
                    </table>
                </div>
                
                <div class="card">
                    <h2>⚠️ Alertas Recentes</h2>
        """
        
        for alert in data['recent_activity']['alerts']:
            html += f"""
                    <div class="alert {alert['level']}">
                        <strong>[{alert['type']}]</strong> {alert['message']}
                        <div class="timestamp">{alert['timestamp']}</div>
                    </div>
            """
        
        html += """
                </div>
                
                <div class="card">
                    <h2>📈 Estatísticas Detalhadas</h2>
                    <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow: auto;">
        """
        
        html += json.dumps(data['statistics'], indent=2)
        
        html += """
                    </pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Salvar arquivo HTML
        html_file = self.storage_path / "dashboard.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"📄 Relatório HTML gerado: {html_file}")
        return str(html_file)


# Função de teste
def test_evolution_dashboard():
    """Testa o EvolutionDashboard"""
    try:
        dashboard = EvolutionDashboard()
        
        print("📊 TESTE EVOLUTION DASHBOARD")
        print("=" * 50)
        
        # Registrar componentes
        dashboard.register_component('genome_mutator', 'structural')
        dashboard.register_component('brain_evolver', 'cognitive')
        dashboard.register_component('evolution_engine', 'core')
        
        # Simular métricas
        dashboard.update_component_metrics('genome_mutator', {
            'node_count': 15,
            'mutation_rate': 0.05,
            'valid_structures': 12
        })
        
        dashboard.update_component_metrics('brain_evolver', {
            'current_model': 'llama3.1:8b',
            'ensemble_enabled': False,
            'parameter_count': 5
        })
        
        # Simular mutações
        for i in range(3):
            dashboard.record_mutation({
                'mutation_type': ['add_node', 'remove_node', 'rewire_connections'][i % 3],
                'structure_changed': True,
                'changes': [f'Change {i+1}']
            })
            time.sleep(0.1)
        
        # Simular evoluções
        for i in range(2):
            dashboard.record_brain_evolution({
                'evolution_type': ['mutate_model', 'optimize_parameters'][i % 2],
                'success': True,
                'changes': [f'Evolution {i+1}']
            })
            time.sleep(0.1)
        
        # Simular performance
        for i in range(5):
            dashboard.record_performance(f'task_{i}', {
                'accuracy': random.uniform(0.7, 0.95),
                'latency': random.uniform(0.1, 2.0),
                'tokens': random.randint(100, 1000)
            })
            dashboard.increment_generation()
            time.sleep(0.1)
        
        # Adicionar alertas
        dashboard.add_alert('structural_change', 'Nova camada neural adicionada', 'info')
        dashboard.add_alert('performance_improvement', 'Accuracy aumentou 15%', 'info')
        dashboard.add_alert('resource_warning', 'Uso de memória alto', 'warning')
        
        # Obter dados do dashboard
        data = dashboard.get_dashboard_data()
        print(f"\n✅ Dashboard criado com sucesso")
        print(f"   Total mutações: {data['status']['total_mutations']}")
        print(f"   Total evoluções: {data['status']['total_evolutions']}")
        print(f"   Geração atual: {data['status']['current_generation']}")
        print(f"   Componentes: {len(data['components'])}")
        
        # Salvar dashboard
        saved_path = dashboard.save_dashboard()
        print(f"💾 Dashboard salvo em: {saved_path}")
        
        # Gerar relatório HTML
        html_path = dashboard.generate_html_report()
        print(f"📄 Relatório HTML gerado em: {html_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_evolution_dashboard()