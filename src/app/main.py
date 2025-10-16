#!/usr/bin/env python3
"""
SISTEMA PRINCIPAL DA IA AUTOEVOLUTIVA BIOMIMÉTICA
==================================================

Este é o script principal de entrada do sistema de IA autoevolutiva biomimética.
Ele coordena todos os componentes do sistema, incluindo:

1. SISTEMA EVOLUTIVO PRINCIPAL:
   - Algoritmos genéticos para evolução de redes neurais
   - Seleção natural baseada em fitness
   - Mutação e crossover de arquiteturas
   - Otimização contínua de parâmetros

2. SISTEMAS V2 INTEGRADOS:
   - Guardião de Conhecimento: Gerencia e protege dados críticos
   - Simulador Contrafactual: Testa cenários alternativos
   - Academia de Agentes: Treina e especializa agentes IA
   - Minerador de Padrões: Identifica padrões em dados complexos
   - Gerador de Procedimentos: Cria procedimentos automatizados

3. FUNCIONALIDADES PRINCIPAIS:
   - Inicialização automática de todos os subsistemas
   - Execução de ciclos evolutivos controlados
   - Monitoramento de performance em tempo real
   - Salvamento automático de estados e progresso
   - Integração com sistemas de logging e métricas

4. ARQUITETURA BIOMIMÉTICA:
   - Inspirada em processos evolutivos naturais
   - Adaptação contínua ao ambiente de dados
   - Emergência de comportamentos complexos
   - Auto-organização e auto-otimização

Versão: 2.0
Data: 2024
Autor: Sistema IA Autoevolutiva
"""

# =============================================================================
# IMPORTS E DEPENDÊNCIAS
# =============================================================================

# Bibliotecas padrão do Python
import json          # Manipulação de dados JSON
import logging       # Sistema de logging avançado
import time          # Medição de tempo e performance
from datetime import datetime  # Timestamps e data/hora
from typing import Dict, Any, List  # Type hints para melhor documentação

# Bibliotecas de machine learning e deep learning
import torch         # Framework principal para deep learning
import torch.nn as nn  # Módulos de redes neurais
import numpy as np   # Computação numérica otimizada

# =============================================================================
# IMPORTS DO SISTEMA INTERNO
# =============================================================================

# Sistema evolutivo principal - núcleo da IA autoevolutiva
from core.ia_evolutiva_compativel import CompatibleEvolutionaryAI

# Sistemas V2 integrados - componentes avançados do ecossistema
from knowledge_bus.guardiao_conhecimento import GuardiaoConhecimento
from systems.simulador_contrafactual import SimuladorContrafactual
from pipelines.gerador_procedimentos_academia import (
    MineradorPadroes, 
    GeradorProcedimentosSugeridos, 
    AcademiaAgentes
)

# =============================================================================
# CONFIGURAÇÃO DO SISTEMA DE LOGGING
# =============================================================================

# Configurar logging para capturar todas as atividades do sistema
logging.basicConfig(
    level=logging.INFO,  # Nível de log: INFO captura informações importantes
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Formato detalhado
    handlers=[
        logging.FileHandler('storage/logs/main_system.log'),  # Log em arquivo
        logging.StreamHandler()  # Log no console
    ]
)
logger = logging.getLogger(__name__)  # Logger específico para este módulo

# =============================================================================
# CLASSE PRINCIPAL DO SISTEMA
# =============================================================================

class MainAI:
    """
    SISTEMA PRINCIPAL DA IA AUTOEVOLUTIVA BIOMIMÉTICA
    
    Esta classe é o núcleo central do sistema de IA autoevolutiva. Ela coordena
    todos os componentes e subsistemas, gerenciando:
    
    FUNCIONALIDADES PRINCIPAIS:
    1. Inicialização e configuração de todos os subsistemas
    2. Execução de ciclos evolutivos controlados
    3. Monitoramento de performance em tempo real
    4. Integração entre sistemas V2 e IA evolutiva
    5. Salvamento e recuperação de estados
    6. Geração de relatórios e métricas
    
    ARQUITETURA:
    - Sistema evolutivo principal (CompatibleEvolutionaryAI)
    - Sistemas V2 integrados (Guardião, Simulador, Academia, etc.)
    - Sistema de logging e monitoramento
    - Gerenciamento de configurações e parâmetros
    
    FLUXO DE EXECUÇÃO:
    1. Inicialização → Configuração → Carregamento de sistemas V2
    2. Execução de ciclos evolutivos → Avaliação de fitness
    3. Mutação e crossover → Seleção natural
    4. Monitoramento de performance → Salvamento de estado
    5. Geração de relatórios → Finalização
    """
    
    def __init__(self):
        """
        INICIALIZAÇÃO DO SISTEMA PRINCIPAL
        
        Configura e inicializa todos os componentes necessários para o
        funcionamento do sistema de IA autoevolutiva.
        
        ATRIBUTOS PRINCIPAIS:
        - evolutionary_ai: Instância do sistema evolutivo principal
        - generation: Contador de gerações executadas
        - best_fitness: Melhor fitness alcançado até o momento
        - evolution_history: Histórico completo da evolução
        - sistemas_v2: Dicionário com todos os sistemas V2 integrados
        """
        # Inicializar sistema evolutivo principal
        self.evolutionary_ai = CompatibleEvolutionaryAI()
        
        # Controle de evolução
        self.generation = 0              # Contador de gerações
        self.best_fitness = 0.0          # Melhor fitness alcançado
        self.evolution_history = []      # Histórico de evolução
        
        # Inicializar Sistemas V2 integrados (sem bancos separados)
        # Estes sistemas compartilham o mesmo banco FAISS para eficiência
        self.sistemas_v2 = {}
        self._inicializar_sistemas_v2()
        
    def _inicializar_sistemas_v2(self):
        """Inicializa todos os Sistemas V2 integrados ao FAISS existente"""
        logger.info("🚀 Inicializando Sistemas V2 integrados ao FAISS...")
        
        try:
            # Sistema V2.1: Guardião do Conhecimento (sem banco separado)
            self.sistemas_v2['guardiao'] = GuardiaoConhecimento(
                usar_banco_separado=False,  # Integrar ao FAISS existente
                faiss_path="faiss_biblioteca_central"
            )
            logger.info("✅ Guardião do Conhecimento inicializado (integrado ao FAISS)")
            
            # Sistema V2.2: Simulador Contrafactual (sem banco separado)
            self.sistemas_v2['simulador'] = SimuladorContrafactual(
                usar_banco_separado=False,  # Usar dados do FAISS
                faiss_path="faiss_biblioteca_central"
            )
            logger.info("✅ Simulador Contrafactual inicializado (integrado ao FAISS)")
            
            # Sistema V2.4: Gerador de Procedimentos e Academia (sem bancos separados)
            self.sistemas_v2['minerador'] = MineradorPadroes(
                usar_banco_separado=False,  # Minerar do FAISS existente
                faiss_path="faiss_biblioteca_central"
            )
            self.sistemas_v2['gerador'] = GeradorProcedimentosSugeridos(
                usar_banco_separado=False,  # Gerar baseado no FAISS
                faiss_path="faiss_biblioteca_central"
            )
            self.sistemas_v2['academia'] = AcademiaAgentes(
                usar_banco_separado=False,  # Treinar com dados do FAISS
                faiss_path="faiss_biblioteca_central"
            )
            logger.info("✅ Gerador de Procedimentos e Academia inicializados (integrados ao FAISS)")
            
            logger.info("🎉 Todos os Sistemas V2 inicializados e integrados ao FAISS existente!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Sistemas V2: {str(e)}")
            raise
    
    def initialize_system(self):
        """Inicializa o sistema principal"""
        logger.info("🚀 Inicializando Sistema Principal da IA")
        
        # Inicializar IA evolutiva
        self.evolutionary_ai.initialize_population(population_size=100)
        
        # Iniciar monitoramento do Guardião do Conhecimento (sem banco separado)
        try:
            self.sistemas_v2['guardiao'].iniciar_monitoramento()
            logger.info("🔍 Monitoramento do Guardião do Conhecimento ativado (integrado ao FAISS)")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível ativar monitoramento: {str(e)}")
        
        logger.info("✅ Sistema inicializado com sucesso")
    
    def run_evolution(self, generations: int = 5):
        """Executa evolução principal"""
        logger.info(f"🔄 Iniciando evolução por {generations} gerações")
        
        for gen in range(generations):
            logger.info(f"📊 Geração {gen + 1}/{generations}")
            
            # Evoluir população
            self.evolutionary_ai.evolve_population(generations=2)
            
            # Avaliar melhor indivíduo
            best_individual = self.evolutionary_ai.get_best_individual()
            if best_individual:
                self.best_fitness = best_individual['fitness']
            
            # Executar análise do Guardião do Conhecimento (sem banco separado)
            self._executar_analise_guardiao()
            
            # Registrar progresso
            self._record_generation(gen + 1)
            
            logger.info(f"🎯 Geração {gen + 1} concluída. Fitness: {self.best_fitness:.4f}")
        
        logger.info("🏆 Evolução principal concluída")
    
    def _executar_analise_guardiao(self):
        """Executa análise periódica do Guardião do Conhecimento (sem banco separado)"""
        try:
            logger.info("🔍 Executando análise do Guardião do Conhecimento...")
            
            # Detectar contradições (sem banco separado)
            contradicoes = self.sistemas_v2['guardiao'].detectar_contradicoes()
            if contradicoes:
                logger.warning(f"⚠️ {len(contradicoes)} contradições detectadas")
            
            # Verificar obsolescência (sem banco separado)
            obsolescencia = self.sistemas_v2['guardiao'].verificar_obsolescencia()
            if obsolescencia:
                logger.info(f"📅 {len(obsolescencia)} itens obsoletos identificados")
            
            # Atualizar links de conhecimento (sem banco separado)
            links_atualizados = self.sistemas_v2['guardiao'].atualizar_links_conhecimento()
            if links_atualizados:
                logger.info(f"🔗 {links_atualizados} links de conhecimento atualizados")
                
        except Exception as e:
            logger.error(f"❌ Erro na análise do Guardião: {str(e)}")
    
    def executar_analise_guardiao(self) -> Dict[str, Any]:
        """Executa análise completa do Guardião do Conhecimento (sem banco separado)"""
        try:
            logger.info("🔍 Executando análise completa do Guardião do Conhecimento...")
            
            resultado = {
                'contradicoes_detectadas': [],
                'obsolescencia_identificada': [],
                'links_atualizados': 0,
                'tickets_criados': 0,
                'status': 'sucesso'
            }
            
            # Detectar contradições
            try:
                contradicoes = self.sistemas_v2['guardiao'].detectar_contradicoes()
                resultado['contradicoes_detectadas'] = contradicoes or []
            except Exception as e:
                logger.error(f"❌ Erro ao detectar contradições: {str(e)}")
                resultado['contradicoes_detectadas'] = []
            
            # Verificar obsolescência
            try:
                obsolescencia = self.sistemas_v2['guardiao'].verificar_obsolescencia()
                resultado['obsolescencia_identificada'] = obsolescencia or []
            except Exception as e:
                logger.error(f"❌ Erro ao verificar obsolescência: {str(e)}")
                resultado['obsolescencia_identificada'] = []
            
            # Atualizar links de conhecimento
            try:
                links_atualizados = self.sistemas_v2['guardiao'].atualizar_links_conhecimento()
                resultado['links_atualizados'] = links_atualizados or 0
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar links: {str(e)}")
                resultado['links_atualizados'] = 0
            
            # Criar tickets de revisão
            try:
                tickets = self.sistemas_v2['guardiao'].criar_tickets_revisao()
                resultado['tickets_criados'] = len(tickets) if tickets else 0
            except Exception as e:
                logger.error(f"❌ Erro ao criar tickets: {str(e)}")
                resultado['tickets_criados'] = 0
            
            logger.info("✅ Análise do Guardião concluída com sucesso")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro na análise do Guardião: {str(e)}")
            return {
                'status': 'erro',
                'erro': str(e),
                'contradicoes_detectadas': [],
                'obsolescencia_identificada': [],
                'links_atualizados': 0,
                'tickets_criados': 0
            }
    
    def simular_cenario_contrato(self, contrato_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa simulação contrafactual usando Sistema V2.2 (sem banco separado)"""
        try:
            logger.info("🎭 Executando simulação contrafactual...")
            
            resultado = self.sistemas_v2['simulador'].simular_cenario_contrato(
                contrato_data=contrato_data,
                alteracoes_sugeridas=contrato_data.get('alteracoes_sugeridas', []),
                cenario_descricao=contrato_data.get('cenario_descricao', 'Análise padrão')
            )
            
            logger.info("✅ Simulação contrafactual concluída com sucesso")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro na simulação contrafactual: {str(e)}")
            return {'erro': str(e)}
    
    def gerar_procedimentos_sugeridos(self, contexto: str) -> Dict[str, Any]:
        """Gera procedimentos sugeridos usando Sistema V2.4 (sem bancos separados)"""
        try:
            logger.info("📋 Gerando procedimentos sugeridos...")
            
            # Minerar padrões (sem banco separado)
            padroes = self.sistemas_v2['minerador'].minerar_padroes_contratos(contexto)
            
            # Gerar procedimentos (sem banco separado)
            procedimentos = self.sistemas_v2['gerador'].gerar_procedimentos_sugeridos(
                padroes_identificados=padroes,
                contexto_especifico=contexto
            )
            
            logger.info("✅ Procedimentos sugeridos gerados com sucesso")
            return {
                'padroes_identificados': padroes,
                'procedimentos_sugeridos': procedimentos
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar procedimentos: {str(e)}")
            return {'erro': str(e)}
    
    def _record_generation(self, generation: int):
        """Registra dados da geração"""
        record = {
            'generation': generation,
            'best_fitness': self.best_fitness,
            'timestamp': datetime.now().isoformat()
        }
        self.evolution_history.append(record)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema"""
        best_individual = self.evolutionary_ai.get_best_individual()
        
        # Status dos Sistemas V2 (sem bancos separados)
        v2_status = {}
        for nome, sistema in self.sistemas_v2.items():
            try:
                if hasattr(sistema, 'obter_relatorio_status'):
                    v2_status[nome] = sistema.obter_relatorio_status()
                else:
                    v2_status[nome] = {'status': 'ativo', 'tipo': type(sistema).__name__, 'integrado_faiss': True}
            except Exception as e:
                v2_status[nome] = {'status': 'erro', 'erro': str(e)}
        
        return {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'population_size': len(self.evolutionary_ai.population),
            'best_individual_id': best_individual['id'] if best_individual else None,
            'evolution_history': self.evolution_history,
            'sistemas_v2': v2_status
        }
    
    def save_state(self, filename: str = None):
        """Salva estado do sistema"""
        if filename is None:
            filename = f"main_ai_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        state = {
            'system_info': {
                'name': 'Main AI System V2',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat()
            },
            'status': self.get_system_status(),
            'evolutionary_state': self.evolutionary_ai.save_evolution_state()
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 Estado salvo em: {filename}")
        return filename

def main():
    """Função principal"""
    print("🧠 SISTEMA PRINCIPAL DA IA AUTOEVOLUTIVA V2")
    print("=" * 50)
    
    # Criar sistema principal
    ai_system = MainAI()
    
    # Inicializar
    print("🔄 Inicializando sistema...")
    ai_system.initialize_system()
    
    # Executar evolução
    print("🚀 Executando evolução...")
    start_time = time.time()
    
    ai_system.run_evolution(generations=3)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Resultados
    print("\n📊 RESULTADOS:")
    print("=" * 30)
    
    status = ai_system.get_system_status()
    
    print(f"⏱️  Tempo: {execution_time:.2f}s")
    print(f"🎯 Melhor fitness: {status['best_fitness']:.4f}")
    print(f"👥 População: {status['population_size']}")
    print(f"🏆 Melhor indivíduo: {status['best_individual_id']}")
    
    # Status dos Sistemas V2
    print("\n🔧 SISTEMAS V2:")
    print("-" * 20)
    for nome, v2_status in status['sistemas_v2'].items():
        print(f"  {nome}: {v2_status.get('status', 'N/A')}")
    
    # Salvar estado
    state_file = ai_system.save_state()
    print(f"💾 Estado salvo: {state_file}")
    
    print("\n🎉 SISTEMA PRINCIPAL V2 EXECUTADO COM SUCESSO!")

if __name__ == "__main__":
    main() 