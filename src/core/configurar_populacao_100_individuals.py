#!/usr/bin/env python3
"""
Configurador de População de 100 Indivíduos
Distribui 100 indivíduos pelos 7 agentes existentes
Usa os bancos de dados já existentes
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PopulationIndividualConfigurator:
    """Configurador de 100 indivíduos para população evolutiva"""
    
    def __init__(self):
        self.evolution_files_dir = "evolution_files"
        
        # 7 agentes existentes
        self.existing_agents = [
            "agente_maestro",
            "agente_legal", 
            "agente_financial",
            "agente_jurist",
            "agente_contract",
            "agente_reviewer",
            "agente_skeptic"
        ]
        
        # Distribuição de 100 indivíduos pelos 7 agentes
        self.individual_distribution = {
            "agente_maestro": 15,      # 15 indivíduos
            "agente_legal": 20,        # 20 indivíduos
            "agente_financial": 20,    # 20 indivíduos
            "agente_jurist": 15,       # 15 indivíduos
            "agente_contract": 15,     # 15 indivíduos
            "agente_reviewer": 10,     # 10 indivíduos
            "agente_skeptic": 5        # 5 indivíduos
        }
        
        # Total: 100 indivíduos
        self.total_individuals = sum(self.individual_distribution.values())
        
    def create_evolution_state_with_100_individuals(self) -> str:
        """Cria estado de evolução com 100 indivíduos distribuídos pelos agentes"""
        logger.info("🔄 Criando estado de evolução com 100 indivíduos...")
        
        # Criar diretório se não existir
        os.makedirs(self.evolution_files_dir, exist_ok=True)
        
        # Lista de todos os indivíduos
        all_individuals = []
        individual_id_counter = 1
        
        for agent_type, count in self.individual_distribution.items():
            for i in range(count):
                individual_data = {
                    "id": f"ind_{individual_id_counter:03d}",
                    "agent_type": agent_type,
                    "agent_name": agent_type,
                    "generation": 0,
                    "fitness": random.uniform(0.1, 0.9),  # Fitness inicial aleatório
                    "specialization": self._get_specialization(agent_type),
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                    "performance_metrics": {
                        "accuracy": random.uniform(0.5, 0.9),
                        "response_time": random.uniform(0.1, 2.0),
                        "learning_rate": random.uniform(0.01, 0.1),
                        "knowledge_base_size": random.randint(50, 200)
                    },
                    "database_info": {
                        "fixed_db": f"agents/{agent_type}/memory.db",
                        "external_db": f"memoria_externa_{agent_type.replace('agente_', '')}.db"
                    }
                }
                all_individuals.append(individual_data)
                individual_id_counter += 1
        
        # Estado de evolução
        evolution_state = {
            "generation": 0,
            "population_size": self.total_individuals,
            "agents": all_individuals,  # Lista de 100 indivíduos
            "best_fitness": max(ind["fitness"] for ind in all_individuals),
            "average_fitness": sum(ind["fitness"] for ind in all_individuals) / len(all_individuals),
            "evolution_history": [],
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "total_individuals": self.total_individuals,
                "individual_distribution": self.individual_distribution,
                "existing_agents": self.existing_agents,
                "created_by": "PopulationIndividualConfigurator",
                "version": "1.0.0"
            }
        }
        
        # Salvar estado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"evolution_state_100_individuals_{timestamp}.json"
        file_path = os.path.join(self.evolution_files_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(evolution_state, f, indent=2)
        
        logger.info(f"✅ Estado de evolução criado: {file_path}")
        logger.info(f"📊 {self.total_individuals} indivíduos distribuídos pelos {len(self.existing_agents)} agentes")
        return file_path
    
    def _get_specialization(self, agent_type: str) -> str:
        """Retorna especialização do agente"""
        specializations = {
            "agente_maestro": "Coordenação e Orquestração",
            "agente_legal": "Conformidade Legal",
            "agente_financial": "Análise Financeira",
            "agente_jurist": "Interpretação Jurídica",
            "agente_contract": "Gestão de Contratos",
            "agente_reviewer": "Revisão e Validação",
            "agente_skeptic": "Validação Crítica"
        }
        return specializations.get(agent_type, "Especialização Geral")
    
    def configure_100_individuals(self) -> Dict[str, Any]:
        """Configura população de 100 indivíduos"""
        logger.info("🚀 CONFIGURANDO 100 INDIVÍDUOS NA POPULAÇÃO")
        logger.info("=" * 60)
        
        try:
            # Criar estado de evolução
            evolution_file = self.create_evolution_state_with_100_individuals()
            
            results = {
                "status": "success",
                "total_individuals": self.total_individuals,
                "individual_distribution": self.individual_distribution,
                "existing_agents": self.existing_agents,
                "evolution_state": evolution_file,
                "timestamp": datetime.now().isoformat(),
                "message": f"100 indivíduos configurados para {len(self.existing_agents)} agentes existentes"
            }
            
            # Resumo
            logger.info("🎉 CONFIGURAÇÃO CONCLUÍDA!")
            logger.info(f"📊 Total de indivíduos: {self.total_individuals}")
            logger.info(f"👥 Agentes existentes: {len(self.existing_agents)}")
            logger.info(f"📁 Estado de evolução: {evolution_file}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na configuração: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Erro durante a configuração dos 100 indivíduos"
            }

def main():
    """Função principal"""
    print("👥 CONFIGURADOR DE 100 INDIVÍDUOS NA POPULAÇÃO")
    print("=" * 60)
    print("🎯 Distribuição de 100 indivíduos pelos 7 agentes existentes:")
    
    configurator = PopulationIndividualConfigurator()
    
    for agent_type, count in configurator.individual_distribution.items():
        print(f"   • {agent_type}: {count} indivíduos")
    
    print(f"📊 Total: {configurator.total_individuals} indivíduos")
    print(f"👥 Agentes existentes: {len(configurator.existing_agents)}")
    print("=" * 60)
    
    # Executar configuração
    result = configurator.configure_100_individuals()
    
    if result["status"] == "success":
        print("\n✅ POPULAÇÃO DE 100 INDIVÍDUOS CONFIGURADA!")
        print(f"📊 Total de indivíduos: {result['total_individuals']}")
        print(f"👥 Agentes utilizados: {len(result['existing_agents'])}")
        print(f"📁 Estado de evolução: {result['evolution_state']}")
        print("\n🚀 Sistema pronto para evolução com 100 indivíduos!")
    else:
        print(f"\n❌ ERRO: {result['message']}")

if __name__ == "__main__":
    main() 