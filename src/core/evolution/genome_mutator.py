"""
GenomeMutator - Mutação Estrutural Real
========================================

Implementa mutações estruturais profundas no genoma:
1. Adição/remoção de nós no agent_graph
2. Criação de novos tipos de especialistas  
3. Redesenho de conexões entre módulos
4. Validação de integridade estrutural

Versão: 1.0.0
Data: 2026-04-14
Autor: Jarvis (OpenClaw)
"""

import json
import random
import copy
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenomeMutator:
    """Realiza mutações estruturais profundas no genoma"""
    
    def __init__(self, genome_path: str = None, genome_data: Dict = None):
        """Inicializa mutator com genoma"""
        if genome_path:
            # Tentar carregar como JSON primeiro
            if genome_path.endswith('.yaml') or genome_path.endswith('.yml'):
                # Se for YAML, tentar usar alternativa
                try:
                    # Tentar carregar com yaml se disponível
                    import yaml
                    with open(genome_path, 'r', encoding='utf-8') as f:
                        self.genome = yaml.safe_load(f)
                except ImportError:
                    # Se não tiver yaml, usar arquivo JSON alternativo
                    json_path = genome_path.replace('.yaml', '.json').replace('.yml', '.json')
                    if Path(json_path).exists():
                        with open(json_path, 'r', encoding='utf-8') as f:
                            self.genome = json.load(f)
                    else:
                        # Criar genoma básico
                        self.genome = self._create_basic_genome()
                        logger.warning(f"⚠️ Usando genoma básico. Converta {genome_path} para JSON")
            else:
                # Assume que é JSON
                with open(genome_path, 'r', encoding='utf-8') as f:
                    self.genome = json.load(f)
        elif genome_data:
            self.genome = copy.deepcopy(genome_data)
        else:
            self.genome = self._create_basic_genome()
            logger.info("ℹ️ Usando genoma básico (nenhum fornecido)")
        
        self.original_genome = copy.deepcopy(self.genome)
        genome_name = self.genome.get('metadata', {}).get('name', 'Unknown')
        logger.info(f"🧬 GenomeMutator inicializado com genoma: {genome_name}")
    
    def _create_basic_genome(self) -> Dict[str, Any]:
        """Cria genoma básico para testes"""
        return {
            'metadata': {
                'name': 'BiomimeticEvolutionaryAI',
                'version': '1.0.0',
                'author': 'Specialist AI Adjalma Aguiar',
                'description': 'IA Biomimética com Meta-Learning e Evolução Coletiva'
            },
            'agent_graph': {
                'nodes': [
                    {'name': 'input_processor', 'type': 'input', 'specialist': 'maestro'},
                    {'name': 'legal_analysis', 'type': 'specialist', 'specialist': 'jurist', 'dependencies': ['input_processor']},
                    {'name': 'financial_analysis', 'type': 'specialist', 'specialist': 'financial', 'dependencies': ['input_processor']},
                    {'name': 'content_review', 'type': 'specialist', 'specialist': 'reviewer', 'dependencies': ['legal_analysis', 'financial_analysis']},
                    {'name': 'critical_review', 'type': 'specialist', 'specialist': 'skeptic', 'dependencies': ['content_review']},
                    {'name': 'knowledge_guardian', 'type': 'specialist', 'specialist': 'guardiao', 'dependencies': ['critical_review']},
                    {'name': 'final_synthesis', 'type': 'output', 'specialist': 'maestro', 'dependencies': ['knowledge_guardian']}
                ]
            },
            'specialists': {
                'maestro': {'name': 'Agente Maestro', 'confidence_threshold': 0.9, 'max_tokens': 3000},
                'jurist': {'name': 'Agente Jurista', 'confidence_threshold': 0.8, 'max_tokens': 2000},
                'financial': {'name': 'Agente Financeiro', 'confidence_threshold': 0.85, 'max_tokens': 1500},
                'reviewer': {'name': 'Agente Revisor', 'confidence_threshold': 0.75, 'max_tokens': 1000},
                'skeptic': {'name': 'Agente Cético', 'confidence_threshold': 0.7, 'max_tokens': 1200},
                'guardiao': {'name': 'Guardião do Conhecimento', 'confidence_threshold': 0.95, 'max_tokens': 2500}
            },
            'evolution': {
                'mutation_types': [
                    {'name': 'parameter_mutation', 'probability': 0.3, 'intensity': 0.05},
                    {'name': 'structural_mutation', 'probability': 0.1, 'intensity': 0.02},
                    {'name': 'behavioral_mutation', 'probability': 0.2, 'intensity': 0.03}
                ]
            }
        }
    
    def get_structural_metrics(self) -> Dict[str, Any]:
        """Retorna métricas da estrutura atual"""
        nodes = self.genome['agent_graph']['nodes']
        specialists = self.genome['specialists']
        
        # Calcular métricas de complexidade
        total_nodes = len(nodes)
        input_nodes = len([n for n in nodes if n.get('type') == 'input'])
        output_nodes = len([n for n in nodes if n.get('type') == 'output'])
        specialist_nodes = len([n for n in nodes if n.get('type') == 'specialist'])
        
        # Calcular densidade de conexões
        total_deps = sum(len(n.get('dependencies', [])) for n in nodes)
        max_possible_deps = total_nodes * (total_nodes - 1)
        connection_density = total_deps / max_possible_deps if max_possible_deps > 0 else 0
        
        return {
            'total_nodes': total_nodes,
            'input_nodes': input_nodes,
            'output_nodes': output_nodes,
            'specialist_nodes': specialist_nodes,
            'total_specialist_types': len(specialists),
            'total_dependencies': total_deps,
            'connection_density': round(connection_density, 3),
            'avg_dependencies_per_node': round(total_deps / total_nodes, 2) if total_nodes > 0 else 0
        }
    
    def add_node(self, node_type: str = "specialist", 
                specialist_type: str = None,
                dependencies: List[str] = None,
                name: str = None) -> str:
        """Adiciona novo nó ao agent_graph com dependências inteligentes"""
        
        nodes = self.genome['agent_graph']['nodes']
        specialists = self.genome['specialists']
        
        # Gerar nome se não fornecido
        if not name:
            existing_names = [n['name'] for n in nodes]
            base_name = f"{node_type}_node"
            counter = 1
            while f"{base_name}_{counter}" in existing_names:
                counter += 1
            name = f"{base_name}_{counter}"
        
        # Escolher especialista se não fornecido
        if node_type == "specialist" and not specialist_type:
            available_specialists = list(specialists.keys())
            specialist_type = random.choice(available_specialists)
        
        # Definir dependências inteligentes
        if dependencies is None:
            if node_type == "input":
                dependencies = []
            elif node_type == "output":
                # Output depende de todos os specialist nodes
                dependencies = [n['name'] for n in nodes if n.get('type') == 'specialist']
                if not dependencies:  # Fallback
                    dependencies = ['input_processor']
            else:  # specialist
                # Depender de input_processor ou de especialistas existentes
                input_nodes = [n['name'] for n in nodes if n.get('type') == 'input']
                if input_nodes:
                    dependencies = [random.choice(input_nodes)]
                else:
                    # Se não há input, depende de um especialista aleatório
                    specialist_nodes = [n['name'] for n in nodes if n.get('type') == 'specialist']
                    if specialist_nodes:
                        dependencies = [random.choice(specialist_nodes)]
                    else:
                        dependencies = []
        
        # Criar novo nó
        new_node = {
            'name': name,
            'type': node_type,
            'dependencies': dependencies
        }
        
        if node_type == "specialist":
            new_node['specialist'] = specialist_type
        
        # Adicionar ao grafo
        nodes.append(new_node)
        logger.info(f"➕ Nó adicionado: {name} (tipo: {node_type}, especialista: {specialist_type})")
        
        return name
    
    def remove_node(self, node_name: str = None) -> bool:
        """Remove nó do agent_graph e ajusta dependências"""
        nodes = self.genome['agent_graph']['nodes']
        
        # Escolher nó para remover se não especificado
        if not node_name:
            # Escolher nó com menos dependentes (menos impacto)
            node_impact = {}
            for node in nodes:
                # Contar quantos nós dependem deste
                dependents = sum(1 for n in nodes if node['name'] in n.get('dependencies', []))
                node_impact[node['name']] = dependents
            
            if not node_impact:
                return False
            
            # Escolher nó com menor impacto (mas não input/output críticos)
            candidates = [n for n, impact in node_impact.items() 
                         if n not in ['input_processor', 'final_synthesis'] and impact < 2]
            
            if candidates:
                node_name = random.choice(candidates)
            else:
                # Remover nó aleatório (não crítico)
                non_critical = [n['name'] for n in nodes 
                               if n['name'] not in ['input_processor', 'final_synthesis']]
                if not non_critical:
                    return False
                node_name = random.choice(non_critical)
        
        # Encontrar e remover nó
        node_to_remove = None
        for i, node in enumerate(nodes):
            if node['name'] == node_name:
                node_to_remove = node
                nodes.pop(i)
                break
        
        if not node_to_remove:
            logger.warning(f"⚠️ Nó {node_name} não encontrado")
            return False
        
        # Remover dependências a este nó
        for node in nodes:
            if node_name in node.get('dependencies', []):
                node['dependencies'].remove(node_name)
        
        logger.info(f"➖ Nó removido: {node_name}")
        return True
    
    def create_new_specialist(self, name: str = None, 
                             description: str = None,
                             confidence_threshold: float = 0.8,
                             max_tokens: int = 1500) -> str:
        """Cria novo tipo de especialista no genoma"""
        
        specialists = self.genome['specialists']
        
        # Gerar nome se não fornecido
        if not name:
            existing_names = list(specialists.keys())
            base_name = "new_specialist"
            counter = 1
            while f"{base_name}_{counter}" in existing_names:
                counter += 1
            name = f"{base_name}_{counter}"
        
        # Gerar descrição se não fornecida
        if not description:
            specialist_types = [
                "Especialista em análise semântica profunda",
                "Especialista em detecção de padrões temporais",
                "Especialista em síntese multimodal",
                "Especialista em raciocínio causal",
                "Especialista em otimização de processos",
                "Especialista em adaptação contextual"
            ]
            description = random.choice(specialist_types)
        
        # Criar novo especialista
        new_specialist = {
            'name': f"Agente {name.title()}",
            'description': description,
            'confidence_threshold': confidence_threshold,
            'max_tokens': max_tokens,
            'fitness_focus': 'specialized_accuracy'
        }
        
        specialists[name] = new_specialist
        logger.info(f"🧠 Novo especialista criado: {name} - {description}")
        
        return name
    
    def rewire_connections(self, mutation_intensity: float = 0.3) -> int:
        """Redesenha conexões entre nós do agent_graph"""
        nodes = self.genome['agent_graph']['nodes']
        changes_made = 0
        
        # Para cada nó, potencialmente reconfigurar dependências
        for node in nodes:
            if node['name'] in ['input_processor', 'final_synthesis']:
                continue  # Não modificar nós críticos
            
            if random.random() < mutation_intensity:
                old_deps = copy.copy(node.get('dependencies', []))
                
                # Escolher nova estratégia de dependência
                strategy = random.choice(['add', 'remove', 'replace', 'shuffle'])
                
                if strategy == 'add' and len(nodes) > 1:
                    # Adicionar nova dependência
                    possible_deps = [n['name'] for n in nodes 
                                   if n['name'] != node['name'] and n['name'] not in old_deps]
                    if possible_deps:
                        new_dep = random.choice(possible_deps)
                        node.setdefault('dependencies', []).append(new_dep)
                        changes_made += 1
                
                elif strategy == 'remove' and old_deps:
                    # Remover dependência aleatória
                    dep_to_remove = random.choice(old_deps)
                    node['dependencies'].remove(dep_to_remove)
                    changes_made += 1
                
                elif strategy == 'replace' and old_deps and len(nodes) > 2:
                    # Substituir dependência
                    dep_to_replace = random.choice(old_deps)
                    possible_replacements = [n['name'] for n in nodes 
                                           if n['name'] != node['name'] and n['name'] != dep_to_replace]
                    if possible_replacements:
                        new_dep = random.choice(possible_replacements)
                        idx = node['dependencies'].index(dep_to_replace)
                        node['dependencies'][idx] = new_dep
                        changes_made += 1
                
                elif strategy == 'shuffle' and len(old_deps) > 1:
                    # Embaralhar ordem das dependências
                    random.shuffle(node['dependencies'])
                    changes_made += 1
        
        if changes_made > 0:
            logger.info(f"🔀 {changes_made} conexões redesenhadas")
        
        return changes_made
    
    def validate_genome_integrity(self) -> Dict[str, Any]:
        """Valida integridade estrutural do genoma após mutação"""
        nodes = self.genome['agent_graph']['nodes']
        specialists = self.genome['specialists']
        
        issues = []
        warnings = []
        
        # 1. Verificar referências a especialistas existentes
        for node in nodes:
            if node.get('type') == 'specialist':
                specialist_type = node.get('specialist')
                if specialist_type not in specialists:
                    issues.append(f"Nó {node['name']} referencia especialista inexistente: {specialist_type}")
        
        # 2. Verificar dependências existentes
        node_names = {n['name'] for n in nodes}
        for node in nodes:
            for dep in node.get('dependencies', []):
                if dep not in node_names:
                    issues.append(f"Nó {node['name']} depende de nó inexistente: {dep}")
        
        # 3. Verificar ciclos (detecção básica)
        # Construir grafo de dependências
        graph = {n['name']: set(n.get('dependencies', [])) for n in nodes}
        
        # DFS para detectar ciclos
        def has_cycle(node, visited, stack):
            visited.add(node)
            stack.add(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, stack):
                        return True
                elif neighbor in stack:
                    return True
            
            stack.remove(node)
            return False
        
        visited = set()
        for node in graph:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    issues.append(f"Ciclo detectado no grafo de dependências")
                    break
        
        # 4. Verificar conectividade básica
        # Há pelo menos um caminho de input para output?
        input_nodes = [n['name'] for n in nodes if n.get('type') == 'input']
        output_nodes = [n['name'] for n in nodes if n.get('type') == 'output']
        
        if not input_nodes:
            warnings.append("Nenhum nó de input encontrado")
        if not output_nodes:
            warnings.append("Nenhum nó de output encontrado")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_issues': len(issues),
            'total_warnings': len(warnings)
        }
    
    def perform_structural_mutation(self, mutation_type: str = None) -> Dict[str, Any]:
        """Executa mutação estrutural completa"""
        if not mutation_type:
            mutation_type = random.choice([
                'add_node', 'remove_node', 'create_specialist', 
                'rewire_connections', 'combined'
            ])
        
        mutation_log = {
            'timestamp': datetime.now().isoformat(),
            'mutation_type': mutation_type,
            'changes': [],
            'metrics_before': self.get_structural_metrics(),
            'validation_before': self.validate_genome_integrity()
        }
        
        try:
            if mutation_type == 'add_node':
                # Adicionar nó aleatório
                node_types = ['specialist', 'specialist', 'specialist']  # Bias para specialist
                node_type = random.choice(node_types)
                new_node_name = self.add_node(node_type=node_type)
                mutation_log['changes'].append(f"Added node: {new_node_name}")
            
            elif mutation_type == 'remove_node':
                # Remover nó
                success = self.remove_node()
                if success:
                    mutation_log['changes'].append("Removed random node")
                else:
                    mutation_log['changes'].append("No node removed (none suitable)")
            
            elif mutation_type == 'create_specialist':
                # Criar novo especialista
                new_spec_name = self.create_new_specialist()
                mutation_log['changes'].append(f"Created specialist: {new_spec_name}")
                
                # Também adicionar nó usando esse especialista
                new_node_name = self.add_node(
                    node_type='specialist',
                    specialist_type=new_spec_name
                )
                mutation_log['changes'].append(f"Added node with new specialist: {new_node_name}")
            
            elif mutation_type == 'rewire_connections':
                # Redesenhar conexões
                changes = self.rewire_connections(mutation_intensity=0.4)
                mutation_log['changes'].append(f"Rewired {changes} connections")
            
            elif mutation_type == 'combined':
                # Combinação de mutações
                num_mutations = random.randint(2, 4)
                for _ in range(num_mutations):
                    sub_type = random.choice(['add_node', 'remove_node', 'rewire_connections'])
                    if sub_type == 'add_node':
                        self.add_node()
                        mutation_log['changes'].append("Added node (combined)")
                    elif sub_type == 'remove_node':
                        self.remove_node()
                        mutation_log['changes'].append("Removed node (combined)")
                    elif sub_type == 'rewire_connections':
                        self.rewire_connections(mutation_intensity=0.2)
                        mutation_log['changes'].append("Rewired connections (combined)")
            
            # Atualizar métricas
            mutation_log['metrics_after'] = self.get_structural_metrics()
            mutation_log['validation_after'] = self.validate_genome_integrity()
            
            # Registrar se houve mudança real
            metrics_changed = (mutation_log['metrics_before'] != mutation_log['metrics_after'])
            mutation_log['structure_changed'] = metrics_changed
            
            logger.info(f"🧬 Mutação estrutural executada: {mutation_type}")
            logger.info(f"   Métricas antes: {mutation_log['metrics_before']}")
            logger.info(f"   Métricas depois: {mutation_log['metrics_after']}")
            
        except Exception as e:
            mutation_log['error'] = str(e)
            logger.error(f"❌ Erro na mutação estrutural: {e}")
        
        return mutation_log
    
    def save_mutated_genome(self, suffix: str = "mutated") -> str:
        """Salva genoma mutado com versionamento"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_version = self.original_genome.get('metadata', {}).get('version', '1.0.0')
        new_version = f"{original_version}_{suffix}_{timestamp}"
        
        # Atualizar metadados
        if 'metadata' not in self.genome:
            self.genome['metadata'] = {}
        
        self.genome['metadata']['version'] = new_version
        self.genome['metadata']['last_modified'] = datetime.now().isoformat()
        self.genome['metadata']['mutated_from'] = original_version
        
        # Salvar genoma
        genome_dir = Path("genomes/mutated")
        genome_dir.mkdir(parents=True, exist_ok=True)
        
        genome_file = genome_dir / f"genome_{new_version}.json"
        with open(genome_file, 'w', encoding='utf-8') as f:
            json.dump(self.genome, f, indent=2)
        
        logger.info(f"💾 Genoma mutado salvo: {genome_file}")
        
        # Salvar log da mutação
        log_file = genome_dir / f"mutation_log_{new_version}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.get_structural_metrics(), f, indent=2)
        
        return str(genome_file)


# Função de teste
def test_genome_mutator():
    """Testa o GenomeMutator com genoma atual"""
    try:
        genome_path = "/data/workspace/AI-Biomimetica/src/core/genome_master.yaml"
        mutator = GenomeMutator(genome_path=genome_path)
        
        print("🧬 TESTE GENOME MUTATOR")
        print("=" * 50)
        
        # Métricas iniciais
        metrics = mutator.get_structural_metrics()
        print(f"Métricas iniciais: {json.dumps(metrics, indent=2)}")
        
        # Validação inicial
        validation = mutator.validate_genome_integrity()
        print(f"Validação inicial: {'VÁLIDO' if validation['is_valid'] else 'INVÁLIDO'}")
        if validation['issues']:
            print(f"Problemas: {validation['issues']}")
        
        # Executar mutação
        print("\n🔀 Executando mutação estrutural...")
        mutation_log = mutator.perform_structural_mutation()
        
        print(f"\n📊 Resultado da mutação:")
        print(f"Tipo: {mutation_log['mutation_type']}")
        print(f"Mudanças: {mutation_log.get('changes', [])}")
        print(f"Estrutura mudou: {mutation_log.get('structure_changed', False)}")
        
        # Validação final
        validation_final = mutator.validate_genome_integrity()
        print(f"\n✅ Validação final: {'VÁLIDO' if validation_final['is_valid'] else 'INVÁLIDO'}")
        
        # Salvar genoma mutado
        if validation_final['is_valid']:
            saved_path = mutator.save_mutated_genome()
            print(f"\n💾 Genoma mutado salvo em: {saved_path}")
            return True
        else:
            print(f"\n❌ Genoma inválido após mutação: {validation_final['issues']}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_genome_mutator()