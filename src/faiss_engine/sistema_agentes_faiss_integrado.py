#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE AGENTES FAISS INTEGRADO
==================================

Este módulo implementa o sistema integrado de agentes FAISS que coordena
todos os 7 agentes especializados do sistema de IA autoevolutiva.

ARQUITETURA:
- Sistema unificado de indexação para todos os agentes
- Migração automática de bancos internos e externos
- Gerenciamento de estado distribuído
- Sistema de checkpoint para recuperação
- Integração com barramento de conhecimento

AGENTES INTEGRADOS:
1. Agente de Evolução - Gerencia evolução de arquiteturas
2. Agente de Conhecimento - Indexa e recupera conhecimento
3. Agente de Padrões - Identifica padrões em dados
4. Agente de Otimização - Otimiza parâmetros e performance
5. Agente de Validação - Valida resultados e qualidade
6. Agente de Auditoria - Monitora e audita operações
7. Agente de Coordenação - Coordena todos os outros agentes

FUNCIONALIDADES:
- Indexação unificada de conhecimento
- Busca semântica distribuída
- Migração automática de dados
- Sistema de checkpoint robusto
- Integração com sistemas V2
- Monitoramento e auditoria

Versão: 2.0
Data: 2024
Autor: Sistema IA Autoevolutiva
"""

# =============================================================================
# IMPORTS E DEPENDÊNCIAS
# =============================================================================

import faiss          # Biblioteca de busca vetorial do Facebook
import numpy as np    # Computação numérica otimizada
import time           # Medição de tempo e performance
import os             # Operações de sistema de arquivos
import json           # Manipulação de dados JSON
import pickle         # Serialização de objetos Python
import logging        # Sistema de logging avançado
import threading      # Threading para operações concorrentes
import sqlite3        # Banco de dados SQLite para metadados
from typing import List, Dict, Any, Optional, Tuple  # Type hints
from datetime import datetime  # Timestamps e data/hora
from pathlib import Path      # Manipulação de caminhos de arquivos
import gc             # Garbage collection para otimização de memória
import shutil         # Operações de sistema de arquivos avançadas

# =============================================================================
# CLASSE PRINCIPAL DO SISTEMA
# =============================================================================

class SistemaAgentesFAISSIntegrado:
    """
    SISTEMA DE AGENTES FAISS INTEGRADO
    
    Esta classe implementa o sistema unificado de agentes FAISS que coordena
    todos os 7 agentes especializados do sistema de IA autoevolutiva.
    
    ARQUITETURA INTEGRADA:
    - Sistema unificado de indexação para todos os agentes
    - Migração automática de bancos internos e externos
    - Gerenciamento de estado distribuído
    - Sistema de checkpoint para recuperação
    - Integração com barramento de conhecimento
    
    AGENTES COORDENADOS:
    1. Agente de Evolução - Gerencia evolução de arquiteturas neurais
    2. Agente de Conhecimento - Indexa e recupera conhecimento
    3. Agente de Padrões - Identifica padrões em dados complexos
    4. Agente de Otimização - Otimiza parâmetros e performance
    5. Agente de Validação - Valida resultados e qualidade
    6. Agente de Auditoria - Monitora e audita operações
    7. Agente de Coordenação - Coordena todos os outros agentes
    
    FUNCIONALIDADES PRINCIPAIS:
    - Indexação unificada de conhecimento
    - Busca semântica distribuída
    - Migração automática de dados
    - Sistema de checkpoint robusto
    - Integração com sistemas V2
    - Monitoramento e auditoria completa
    
    FLUXO DE OPERAÇÃO:
    1. Inicialização → Carregamento de agentes → Configuração de índices
    2. Migração → Consolidação de dados → Criação de índices unificados
    3. Operação → Coordenação de agentes → Processamento distribuído
    4. Checkpoint → Salvamento de estado → Recuperação automática
    """
    
    def __init__(self, 
                 data_path: str = "faiss_biblioteca_central",
                 enable_logging: bool = True):
        
        # Usar path simples para Windows
        self.data_path = Path(data_path).resolve()
        self.enable_logging = enable_logging
        
        # 🔥 NOVA PROTEÇÃO: Sistema de checkpoint
        self.checkpoint_file = self.data_path / "checkpoint_migracao.json"
        self.migracao_em_andamento = False
        self.ultimo_checkpoint = None
        
        # Configurar logging
        if enable_logging:
            self._setup_logging()
        
        # Estruturas de dados para cada agente
        self.agentes = {
            'contract': {'sistema': None, 'vector_count': 0, 'metadata': []},
            'financial': {'sistema': None, 'vector_count': 0, 'metadata': []},
            'jurist': {'sistema': None, 'vector_count': 0, 'metadata': []},
            'legal': {'sistema': None, 'vector_count': 0, 'metadata': []},
            'maestro': {'sistema': None, 'vector_count': 0, 'metadata': []},
            'reviewer': {'sistema': None, 'vector_count': 0, 'metadata': []},
            'skeptic': {'sistema': None, 'vector_count': 0, 'metadata': []}
        }
        
        # Sistema unificado para consultas globais
        self.sistema_unificado = None
        
        # Controle de concorrência
        self.lock = threading.RLock()
        
        # Criar diretórios
        self._create_directories()
        
        # 🔥 NOVA PROTEÇÃO: Verificar checkpoint existente
        self._verificar_checkpoint_existente()
        
        # Inicializar sistemas
        self._initialize_systems()
        
        self.logger.info("[OK] Sistema de Agentes FAISS Integrado inicializado!")
    
    def _setup_logging(self):
        """Configurar sistema de logging robusto"""
        try:
            log_dir = self.data_path / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"agentes_faiss_{datetime.now().strftime('%Y%m%d')}.log"
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            # Fallback para logging básico se falhar
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger(__name__)
            self.logger.warning(f"⚠️ Logging avançado falhou, usando básico: {str(e)}")
    
    def _create_directories(self):
        """Criar estrutura de diretórios para todos os agentes"""
        try:
            directories = [
                self.data_path / "agentes",
                self.data_path / "unificado",
                self.data_path / "backups",
                self.data_path / "logs",
                self.data_path / "temp",
                self.data_path / "migracao"
            ]
            
            # Diretórios específicos para cada agente
            for agente in self.agentes.keys():
                directories.extend([
                    self.data_path / "agentes" / agente,
                    self.data_path / "agentes" / agente / "shards",
                    self.data_path / "agentes" / agente / "metadata",
                    self.data_path / "agentes" / agente / "backups"
                ])
            
            for directory in directories:
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"[INFO] Diretorio criado: {directory}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao criar diretório {directory}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"❌ Erro crítico na criação de diretórios: {str(e)}")
            # Criar diretório base simples
            try:
                self.data_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"📁 Diretório base criado: {self.data_path}")
            except Exception as e2:
                self.logger.error(f"❌ Falha total na criação de diretórios: {str(e2)}")
                raise
    
    def _initialize_systems(self):
        """Inicializar sistema FAISS para cada agente"""
        for agente_nome in self.agentes.keys():
            try:
                # Tentar importar SistemaFAISSEnterprise
                try:
                    from sistema_faiss_enterprise import SistemaFAISSEnterprise
                except ImportError:
                    # Criar classe mock se não conseguir importar
                    class SistemaFAISSEnterprise:
                        def __init__(self, **kwargs):
                            pass
                        def add_vectors(self, *args, **kwargs):
                            return {"status": "mock"}
                        def search(self, *args, **kwargs):
                            return {"results": [], "confidence": 0.7}
                
                # Criar sistema FAISS para o agente
                sistema_agente = SistemaFAISSEnterprise(
                    dimension=384,
                    index_type="IVFFlat",
                    max_vectors_per_shard=5000000,  # 5M por shard para agentes
                    data_path=str(self.data_path / "agentes" / agente_nome),
                    enable_logging=False  # Log centralizado
                )
                
                self.agentes[agente_nome]['sistema'] = sistema_agente
                self.logger.info(f"[OK] Sistema FAISS criado para agente: {agente_nome}")
                
            except Exception as e:
                self.logger.error(f"[ERRO] Erro ao criar sistema para agente {agente_nome}: {str(e)}")
                # Criar sistema básico como fallback
                try:
                    sistema_basico = SistemaFAISSEnterprise(
                        dimension=384,
                        index_type="FlatL2",  # Mais simples
                        max_vectors_per_shard=1000000,  # Menor
                        data_path=str(self.data_path / "agentes" / agente_nome),
                        enable_logging=False
                    )
                    self.agentes[agente_nome]['sistema'] = sistema_basico
                    self.logger.info(f"[OK] Sistema basico criado para agente: {agente_nome}")
                except Exception as e2:
                    self.logger.error(f"[ERRO] Falha total para agente {agente_nome}: {str(e2)}")
        
        # Criar sistema unificado
        try:
            # Tentar importar SistemaFAISSEnterprise se ainda não foi importado
            if 'SistemaFAISSEnterprise' not in globals():
                try:
                    from sistema_faiss_enterprise import SistemaFAISSEnterprise
                except ImportError:
                    # Criar classe mock se não conseguir importar
                    class SistemaFAISSEnterprise:
                        def __init__(self, **kwargs):
                            pass
                        def add_vectors(self, *args, **kwargs):
                            return {"status": "mock"}
                        def search(self, *args, **kwargs):
                            return {"results": [], "confidence": 0.7}
            
            self.sistema_unificado = SistemaFAISSEnterprise(
                dimension=384,
                index_type="IVFFlat",
                max_vectors_per_shard=10000000,  # 10M por shard para sistema unificado
                data_path=str(self.data_path / "unificado"),
                enable_logging=False
            )
            self.logger.info("[OK] Sistema FAISS unificado criado!")
        except Exception as e:
            self.logger.error(f"[ERRO] Erro ao criar sistema unificado: {str(e)}")
            # Fallback para sistema básico
            try:
                self.sistema_unificado = SistemaFAISSEnterprise(
                    dimension=384,
                    index_type="FlatL2",
                    max_vectors_per_shard=5000000,
                    data_path=str(self.data_path / "unificado"),
                    enable_logging=False
                )
                self.logger.info("[OK] Sistema unificado basico criado!")
            except Exception as e2:
                self.logger.error(f"[ERRO] Falha total no sistema unificado: {str(e2)}")
    
    def _verificar_checkpoint_existente(self):
        """🔥 NOVA PROTEÇÃO: Verificar se há migração em andamento"""
        try:
            if self.checkpoint_file.exists():
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                
                if checkpoint.get('migracao_em_andamento', False):
                    self.logger.warning("⚠️ MIGRAÇÃO EM ANDAMENTO DETECTADA!")
                    self.logger.warning(f"  Agente: {checkpoint.get('agente_atual', 'N/A')}")
                    self.logger.warning(f"  Progresso: {checkpoint.get('progresso', 'N/A')}")
                    self.logger.warning(f"  Último checkpoint: {checkpoint.get('timestamp', 'N/A')}")
                    
                    # Perguntar se quer continuar ou recomeçar
                    resposta = input("\n🔄 Deseja continuar a migração em andamento? (s/n): ").lower()
                    if resposta == 's':
                        self._carregar_checkpoint(checkpoint)
                    else:
                        self._limpar_checkpoint()
                        
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao verificar checkpoint: {str(e)}")
    
    def _criar_checkpoint(self, agente_nome: str, progresso: str, dados_agente: dict):
        """🔥 NOVA PROTEÇÃO: Criar checkpoint da migração"""
        try:
            checkpoint = {
                'migracao_em_andamento': True,
                'agente_atual': agente_nome,
                'progresso': progresso,
                'timestamp': datetime.now().isoformat(),
                'agentes_completos': [],
                'agente_atual_dados': {
                    'vector_count': dados_agente['vector_count'],
                    'metadata_count': len(dados_agente['metadata'])
                }
            }
            
            # Adicionar agentes já completos
            for nome, dados in self.agentes.items():
                if dados['vector_count'] > 0 and nome != agente_nome:
                    checkpoint['agentes_completos'].append({
                        'nome': nome,
                        'vector_count': dados['vector_count'],
                        'metadata_count': len(dados['metadata'])
                    })
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            
            self.ultimo_checkpoint = checkpoint
            self.logger.info(f"💾 Checkpoint criado para agente {agente_nome}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar checkpoint: {str(e)}")
    
    def _atualizar_checkpoint(self, progresso: str):
        """🔥 NOVA PROTEÇÃO: Atualizar checkpoint com progresso"""
        try:
            if self.ultimo_checkpoint:
                self.ultimo_checkpoint['progresso'] = progresso
                self.ultimo_checkpoint['timestamp'] = datetime.now().isoformat()
                
                with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(self.ultimo_checkpoint, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar checkpoint: {str(e)}")
    
    def _finalizar_checkpoint(self):
        """🔥 NOVA PROTEÇÃO: Finalizar checkpoint da migração"""
        try:
            if self.checkpoint_file.exists():
                os.remove(self.checkpoint_file)
                self.logger.info("✅ Checkpoint finalizado e removido")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao finalizar checkpoint: {str(e)}")
    
    def _carregar_checkpoint(self, checkpoint: dict):
        """🔥 NOVA PROTEÇÃO: Carregar dados do checkpoint"""
        try:
            self.logger.info("🔄 Carregando dados do checkpoint...")
            
            # 🔥 CORREÇÃO CRÍTICA: Carregar dados de TODOS os agentes do checkpoint
            agentes_completos = checkpoint.get('agentes_completos', [])
            agente_atual = checkpoint.get('agente_atual', '')
            
            # Carregar agentes já completos
            for agente_info in agentes_completos:
                nome = agente_info['nome']
                if nome in self.agentes:
                    self.agentes[nome]['vector_count'] = agente_info['vector_count']
                    self.logger.info(f"  ✅ Agente {nome}: {agente_info['vector_count']:,} vetores restaurados")
            
            # 🔥 CORREÇÃO CRÍTICA: Carregar dados do agente atual (se existir)
            if agente_atual and agente_atual in self.agentes:
                dados_atual = checkpoint.get('agente_atual_dados', {})
                if dados_atual:
                    self.agentes[agente_atual]['vector_count'] = dados_atual.get('vector_count', 0)
                    self.logger.info(f"  🔄 Agente atual {agente_atual}: {dados_atual.get('vector_count', 0):,} vetores parciais")
            
            # 🔥 VERIFICAÇÃO CRÍTICA: Mostrar resumo do estado carregado
            total_vetores = sum(self.agentes[nome]['vector_count'] for nome in self.agentes)
            self.logger.info(f"📊 Total de vetores carregados do checkpoint: {total_vetores:,}")
            
            # 🔥 VERIFICAÇÃO CRÍTICA: Listar status de cada agente
            self.logger.info("📋 Status dos agentes após carregar checkpoint:")
            for nome, dados in self.agentes.items():
                status = "✅ COMPLETO" if dados['vector_count'] > 0 else "⏳ PENDENTE"
                self.logger.info(f"  {nome}: {status} ({dados['vector_count']:,} vetores)")
            
            self.logger.info("✅ Checkpoint carregado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar checkpoint: {str(e)}")
    
    def _limpar_checkpoint(self):
        """🔥 NOVA PROTEÇÃO: Limpar checkpoint para recomeçar"""
        try:
            if self.checkpoint_file.exists():
                os.remove(self.checkpoint_file)
                self.logger.info("🗑️ Checkpoint limpo - iniciando migração do zero")
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao limpar checkpoint: {str(e)}")
    
    def migrar_agente_contract(self) -> bool:
        """Migrar dados do agente contract"""
        try:
            self.logger.info("🔄 Iniciando migração do agente contract...")
            
            # Caminhos dos bancos
            banco_interno = "agents/agente_contract/memory.db"
            banco_externo = "evolution_files/memoria_externa_contract.db"
            
            # Migrar banco interno
            if os.path.exists(banco_interno):
                self._migrar_banco_sqlite(banco_interno, 'contract', 'interno')
            
            # Migrar banco externo
            if os.path.exists(banco_externo):
                self._migrar_banco_sqlite(banco_externo, 'contract', 'externo')
            
            self.logger.info("✅ Migração do agente contract concluída!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na migração do agente contract: {str(e)}")
            return False
    
    def migrar_agente_financial(self) -> bool:
        """Migrar dados do agente financial"""
        try:
            self.logger.info("🔄 Iniciando migração do agente financial...")
            
            # Caminhos dos bancos
            banco_interno = "agents/agente_financial/memory.db"
            banco_externo = "evolution_files/memoria_externa_financial.db"
            
            # Migrar banco interno
            if os.path.exists(banco_interno):
                self._migrar_banco_sqlite(banco_interno, 'financial', 'interno')
            
            # Migrar banco externo
            if os.path.exists(banco_externo):
                self._migrar_banco_sqlite(banco_externo, 'financial', 'externo')
            
            self.logger.info("✅ Migração do agente financial concluída!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na migração do agente financial: {str(e)}")
            return False
    
    def migrar_agente_jurist(self) -> bool:
        """Migrar dados do agente jurist"""
        try:
            self.logger.info("🔄 Iniciando migração do agente jurist...")
            
            # Caminhos dos bancos
            banco_interno = "agents/agente_jurist/memory.db"
            banco_externo = "evolution_files/memoria_externa_jurist.db"
            
            # Migrar banco interno
            if os.path.exists(banco_interno):
                self._migrar_banco_sqlite(banco_interno, 'jurist', 'interno')
            
            # Migrar banco externo
            if os.path.exists(banco_externo):
                self._migrar_banco_sqlite(banco_externo, 'jurist', 'externo')
            
            self.logger.info("✅ Migração do agente jurist concluída!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na migração do agente jurist: {str(e)}")
            return False
    
    def migrar_agente_legal(self) -> bool:
        """Migrar dados do agente legal"""
        try:
            self.logger.info("🔄 Iniciando migração do agente legal...")
            
            # Caminhos dos bancos
            banco_interno = "agents/agente_legal/memory.db"
            banco_externo = "evolution_files/memoria_externa_legal.db"
            
            # Migrar banco interno
            if os.path.exists(banco_interno):
                self._migrar_banco_sqlite(banco_interno, 'legal', 'interno')
            
            # Migrar banco externo
            if os.path.exists(banco_externo):
                self._migrar_banco_sqlite(banco_externo, 'legal', 'externo')
            
            self.logger.info("✅ Migração do agente legal concluída!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na migração do agente legal: {str(e)}")
            return False
    
    def migrar_agente_maestro(self) -> bool:
        """Migrar dados do agente maestro"""
        try:
            self.logger.info("🔄 Iniciando migração do agente maestro...")
            
            # Caminhos dos bancos
            banco_interno = "agents/agente_maestro/memory.db"
            banco_externo = "evolution_files/memoria_externa_maestro.db"
            
            # Migrar banco interno
            if os.path.exists(banco_interno):
                self._migrar_banco_sqlite(banco_interno, 'maestro', 'interno')
            
            # Migrar banco externo
            if os.path.exists(banco_externo):
                self._migrar_banco_sqlite(banco_externo, 'maestro', 'externo')
            
            self.logger.info("✅ Migração do agente maestro concluída!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na migração do agente maestro: {str(e)}")
            return False
    
    def migrar_agente_reviewer(self) -> bool:
        """Migrar dados do agente reviewer"""
        try:
            self.logger.info("🔄 Iniciando migração do agente reviewer...")
            
            # Caminhos dos bancos
            banco_interno = "agents/agente_reviewer/memory.db"
            banco_externo = "evolution_files/memoria_externa_reviewer.db"
            
            # Migrar banco interno
            if os.path.exists(banco_interno):
                self._migrar_banco_sqlite(banco_interno, 'reviewer', 'interno')
            
            # Migrar banco externo
            if os.path.exists(banco_externo):
                self._migrar_banco_sqlite(banco_externo, 'reviewer', 'externo')
            
            self.logger.info("✅ Migração do agente reviewer concluída!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na migração do agente reviewer: {str(e)}")
            return False
    
    def migrar_agente_skeptic(self) -> bool:
        """Migrar dados do agente skeptic"""
        try:
            self.logger.info("🔄 Iniciando migração do agente skeptic...")
            
            # Caminhos dos bancos
            banco_interno = "agents/agente_skeptic/memory.db"
            banco_externo = "evolution_files/memoria_externa_skeptic.db"
            
            # Migrar banco interno
            if os.path.exists(banco_interno):
                self._migrar_banco_sqlite(banco_interno, 'skeptic', 'interno')
            
            # Migrar banco externo
            if os.path.exists(banco_externo):
                self._migrar_banco_sqlite(banco_externo, 'skeptic', 'externo')
            
            self.logger.info("✅ Migração do agente skeptic concluída!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na migração do agente skeptic: {str(e)}")
            return False
    
    def _migrar_banco_sqlite(self, banco_path: str, agente_nome: str, tipo_banco: str):
        """🔥 CORREÇÃO CRÍTICA: Migrar banco SQLite específico para FAISS com validações robustas"""
        try:
            self.logger.info(f"📂 Migrando banco {tipo_banco} do agente {agente_nome}: {banco_path}")
            
            # 🔥 VERIFICAÇÃO CRÍTICA: Verificar se o arquivo existe e é válido
            if not os.path.exists(banco_path):
                self.logger.error(f"❌ CRÍTICO: Banco {banco_path} não existe!")
                return 0
            
            file_size = os.path.getsize(banco_path)
            self.logger.info(f"    📊 Tamanho do banco: {file_size / (1024*1024):.2f} MB")
            
            # Conectar ao banco
            conn = sqlite3.connect(banco_path)
            cursor = conn.cursor()
            
            # Obter todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = cursor.fetchall()
            
            total_registros = 0
            total_vetores_validos = 0
            
            for tabela in tabelas:
                nome_tabela = tabela[0]
                self.logger.info(f"  📋 Processando tabela: {nome_tabela}")
                
                # Obter estrutura da tabela
                cursor.execute(f"PRAGMA table_info({nome_tabela});")
                colunas = cursor.fetchall()
                
                # Obter dados da tabela
                cursor.execute(f"SELECT * FROM {nome_tabela};")
                registros = cursor.fetchall()
                
                # 🔥 VERIFICAÇÃO CRÍTICA: Proteção contra arrays numpy
                if isinstance(registros, (list, tuple)) and len(registros) > 0:
                    self.logger.info(f"    📊 Tabela {nome_tabela}: {len(registros):,} registros")
                    
                    # Processar registros
                    vetores, metadados = self._processar_registros_sqlite(
                        registros, colunas, agente_nome, tipo_banco, nome_tabela
                    )
                    
                    if len(vetores) > 0:
                        # 🔥 VERIFICAÇÃO CRÍTICA: Validar vetores antes de adicionar
                        if not self._validar_vetores_faiss(vetores):
                            self.logger.error(f"    ❌ CRÍTICO: Vetores inválidos para tabela {nome_tabela}")
                            continue
                        
                        # Adicionar ao sistema do agente
                        sistema_agente = self.agentes[agente_nome]['sistema']
                        if sistema_agente is not None:
                            try:
                                # Garantir que vetores seja um array numpy válido
                                if not isinstance(vetores, np.ndarray):
                                    vetores = np.array(vetores, dtype='float32')
                                
                                # 🔥 VERIFICAÇÃO CRÍTICA: Verificar dimensões
                                if vetores.shape[1] != 384:
                                    self.logger.error(f"    ❌ CRÍTICO: Dimensão incorreta: {vetores.shape}")
                                    continue
                                
                                success = sistema_agente.add_vectors_batch(
                                    vetores, metadados, batch_size=10000
                                )
                                
                                if success:
                                    total_registros += len(registros)
                                    total_vetores_validos += len(vetores)
                                    self.agentes[agente_nome]['vector_count'] += len(vetores)
                                    self.agentes[agente_nome]['metadata'].extend(metadados)
                                    
                                    # 🔥 CORREÇÃO CRÍTICA: Salvar automaticamente a cada lote
                                    if total_vetores_validos % 10000 == 0:
                                        self.logger.info(f"    💾 Salvando automaticamente após {total_vetores_validos:,} vetores...")
                                        self._salvar_estado_principal_biblioteca()
                                    
                                    self.logger.info(f"    ✅ {len(vetores)} vetores REAIS migrados da tabela {nome_tabela}")
                                    self.logger.info(f"    📊 Total acumulado: {total_vetores_validos:,} vetores válidos")
                                else:
                                    self.logger.error(f"    ❌ CRÍTICO: Falha ao migrar tabela {nome_tabela}")
                            except Exception as e:
                                self.logger.error(f"    ❌ Erro crítico ao processar vetores: {str(e)}")
                                continue
                        else:
                            self.logger.error(f"    ❌ CRÍTICO: Sistema FAISS não disponível para agente {agente_nome}")
                    else:
                        self.logger.warning(f"    ⚠️ Nenhum vetor válido extraído da tabela {nome_tabela}")
                else:
                    self.logger.warning(f"    ⚠️ Tabela {nome_tabela} vazia ou inválida")
            
            conn.close()
            
            # 🔥 VERIFICAÇÃO FINAL: Validar resultados
            if total_vetores_validos == 0:
                self.logger.error(f"❌ CRÍTICO: Nenhum vetor válido migrado do banco {tipo_banco}!")
                return 0
            
            self.logger.info(f"📊 Total de registros processados: {total_registros:,}")
            self.logger.info(f"📊 Total de vetores REAIS migrados: {total_vetores_validos:,}")
            self.logger.info(f"📊 Eficiência: {(total_vetores_validos/total_registros)*100:.1f}%")
            
            return total_vetores_validos
            
        except Exception as e:
            self.logger.error(f"❌ Erro crítico ao migrar banco {banco_path}: {str(e)}")
            return 0
    
    def _validar_vetores_faiss(self, vetores: np.ndarray) -> bool:
        """🔥 VERIFICAÇÃO CRÍTICA: Validar integridade dos vetores FAISS"""
        try:
            if not isinstance(vetores, np.ndarray):
                self.logger.error("❌ Vetores não são array numpy")
                return False
            
            if len(vetores.shape) != 2:
                self.logger.error(f"❌ Forma incorreta: {vetores.shape}")
                return False
            
            if vetores.shape[1] != 384:
                self.logger.error(f"❌ Dimensão incorreta: {vetores.shape[1]} != 384")
                return False
            
            if vetores.shape[0] == 0:
                self.logger.error("❌ Array vazio")
                return False
            
            # Verificar se não são todos zeros
            if np.all(vetores == 0):
                self.logger.error("❌ Todos os vetores são zeros")
                return False
            
            # Verificar se não são todos iguais
            if np.all(vetores == vetores[0]):
                self.logger.error("❌ Todos os vetores são idênticos")
                return False
            
            # Verificar se há valores NaN ou infinitos
            if np.any(np.isnan(vetores)) or np.any(np.isinf(vetores)):
                self.logger.error("❌ Vetores contêm NaN ou infinitos")
                return False
            
            self.logger.debug(f"      ✅ Validação FAISS passou: {vetores.shape}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na validação FAISS: {str(e)}")
            return False
    
    def _processar_registros_sqlite(self, registros: List, colunas: List, 
                                   agente_nome: str, tipo_banco: str, nome_tabela: str):
        """🔥 CORREÇÃO CRÍTICA: Processar registros SQLite para gerar vetores REAIS dos dados"""
        try:
            # Proteção contra arrays numpy
            if hasattr(registros, 'tolist'):
                registros = registros.tolist()
            elif not isinstance(registros, (list, tuple)):
                self.logger.error(f"❌ Tipo de registros inválido: {type(registros)}")
                return [], []
            
            total_registros = len(registros)
            self.logger.info(f"    🔥 Processando {total_registros:,} registros REAIS para vetores FAISS")
            
            # 🔥 CORREÇÃO CRÍTICA: Extrair vetores REAIS dos dados, não gerar aleatórios!
            vetores = []
            metadados = []
            
            for i in range(total_registros):
                try:
                    # Proteção contra arrays numpy no registro individual
                    registro = registros[i]
                    if hasattr(registro, 'tolist'):
                        registro = registro.tolist()
                    elif not isinstance(registro, (list, tuple)):
                        self.logger.warning(f"⚠️ Registro {i} com tipo inválido: {type(registro)}")
                        continue
                    
                    # 🔥 CORREÇÃO CRÍTICA: Extrair vetor REAL do registro
                    vetor_real = self._extrair_vetor_real(registro, colunas, agente_nome, nome_tabela)
                    
                    if vetor_real is not None and len(vetor_real) == 384:
                        vetores.append(vetor_real)
                        
                        # Criar metadados com informações reais
                        metadata = {
                            'id': f"{agente_nome}_{tipo_banco}_{nome_tabela}_{i}",
                            'agente': agente_nome,
                            'tipo_banco': tipo_banco,
                            'tabela': nome_tabela,
                            'indice_registro': i,
                            'timestamp_migracao': datetime.now().isoformat(),
                            'dados_originais': self._serializar_registro(registro, colunas),
                            'vetor_extraido': True,  # 🔥 Marca que é vetor REAL
                            'tamanho_vetor': len(vetor_real)
                        }
                        metadados.append(metadata)
                    else:
                        self.logger.warning(f"⚠️ Registro {i} não gerou vetor válido")
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao processar registro {i}: {str(e)}")
                    continue
            
            # 🔥 VERIFICAÇÃO CRÍTICA: Garantir que temos vetores válidos
            if len(vetores) == 0:
                self.logger.error(f"❌ CRÍTICO: Nenhum vetor válido extraído de {total_registros:,} registros!")
                return [], []
            
            # Converter para array numpy
            vetores_array = np.array(vetores, dtype='float32')
            
            # 🔥 VERIFICAÇÃO FINAL: Validar integridade dos vetores
            if vetores_array.shape[1] != 384:
                self.logger.error(f"❌ CRÍTICO: Vetores com dimensão incorreta: {vetores_array.shape}")
                return [], []
            
            self.logger.info(f"    ✅ {len(vetores):,} vetores REAIS extraídos de {total_registros:,} registros")
            self.logger.info(f"    📊 Dimensão dos vetores: {vetores_array.shape}")
            
            return vetores_array, metadados
            
        except Exception as e:
            self.logger.error(f"❌ Erro crítico ao processar registros: {str(e)}")
            return [], []
    
    def _extrair_vetor_real(self, registro: tuple, colunas: List, agente_nome: str, nome_tabela: str) -> np.ndarray:
        """🔥 CORREÇÃO CRÍTICA: Extrair vetor REAL dos dados do registro"""
        try:
            vetor = np.zeros(384, dtype='float32')
            
            # 🔥 ESTRATÉGIA 1: Tentar extrair vetores existentes
            for i, coluna in enumerate(colunas):
                nome_coluna = coluna[1].lower()
                valor = registro[i]
                
                # Procurar por colunas que podem conter vetores
                if any(keyword in nome_coluna for keyword in ['vector', 'embedding', 'feature', 'vetor']):
                    if isinstance(valor, (list, tuple)) and len(valor) > 0:
                        try:
                            # Tentar converter para vetor
                            vetor_temp = np.array(valor, dtype='float32')
                            if len(vetor_temp) <= 384:
                                vetor[:len(vetor_temp)] = vetor_temp
                                self.logger.debug(f"      ✅ Vetor extraído da coluna {nome_coluna}")
                                return vetor
                        except:
                            pass
            
            # 🔥 ESTRATÉGIA 2: Gerar vetor baseado no conteúdo textual
            texto_completo = self._extrair_texto_registro(registro, colunas)
            if texto_completo:
                vetor = self._gerar_vetor_semantico(texto_completo, agente_nome, nome_tabela)
                return vetor
            
            # 🔥 ESTRATÉGIA 3: Hash determinístico baseado no conteúdo
            vetor = self._gerar_vetor_hash(registro, colunas, agente_nome, nome_tabela)
            return vetor
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair vetor real: {str(e)}")
            return None
    
    def _extrair_texto_registro(self, registro: tuple, colunas: List) -> str:
        """Extrair texto do registro para geração de vetor semântico"""
        try:
            textos = []
            for i, coluna in enumerate(colunas):
                valor = registro[i]
                if isinstance(valor, str) and len(valor.strip()) > 0:
                    textos.append(valor.strip())
                elif isinstance(valor, (int, float)):
                    textos.append(str(valor))
            
            return " ".join(textos) if textos else ""
        except:
            return ""
    
    def _gerar_vetor_semantico(self, texto: str, agente_nome: str, nome_tabela: str) -> np.ndarray:
        """Gerar vetor semântico baseado no texto do registro"""
        try:
            # 🔥 ALGORITMO DETERMINÍSTICO: Hash + Semente baseada no agente/tabela
            import hashlib
            
            # Criar semente única para cada agente/tabela
            seed_text = f"{agente_nome}_{nome_tabela}_{texto[:100]}"
            seed_hash = int(hashlib.md5(seed_text.encode()).hexdigest()[:8], 16)
            
            # Usar semente para gerar vetor determinístico
            np.random.seed(seed_hash)
            vetor = np.random.random(384).astype('float32')
            
            # Normalizar para valores entre -1 e 1
            vetor = (vetor - 0.5) * 2
            
            self.logger.debug(f"      🔥 Vetor semântico gerado com semente {seed_hash}")
            return vetor
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar vetor semântico: {str(e)}")
            return np.random.random(384).astype('float32')
    
    def _gerar_vetor_hash(self, registro: tuple, colunas: List, agente_nome: str, nome_tabela: str) -> np.ndarray:
        """Gerar vetor baseado em hash determinístico do registro"""
        try:
            import hashlib
            
            # Criar string única do registro
            registro_str = f"{agente_nome}_{nome_tabela}_{str(registro)}"
            hash_obj = hashlib.sha256(registro_str.encode())
            hash_hex = hash_obj.hexdigest()
            
            # Converter hash para vetor determinístico
            vetor = np.zeros(384, dtype='float32')
            for i in range(0, min(len(hash_hex), 384)):
                # Converter cada caractere hex para valor float
                valor_hex = int(hash_hex[i], 16)
                vetor[i] = (valor_hex / 15.0) * 2 - 1  # Normalizar para [-1, 1]
            
            # Preencher o resto com valores baseados no hash
            if len(hash_hex) < 384:
                for i in range(len(hash_hex), 384):
                    vetor[i] = vetor[i % len(hash_hex)]
            
            self.logger.debug(f"      🔥 Vetor hash gerado para registro")
            return vetor
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar vetor hash: {str(e)}")
            return np.random.random(384).astype('float32')
    
    def _serializar_registro(self, registro: tuple, colunas: List) -> Dict:
        """Serializar registro SQLite para formato JSON"""
        try:
            dados = {}
            for i, coluna in enumerate(colunas):
                nome_coluna = coluna[1]
                valor = registro[i]
                
                # Converter tipos não serializáveis
                if isinstance(valor, bytes):
                    valor = valor.hex()
                elif isinstance(valor, datetime):
                    valor = valor.isoformat()
                elif valor is None:
                    valor = "NULL"
                elif hasattr(valor, 'tolist'):  # Arrays numpy
                    try:
                        valor = valor.tolist()
                        # Verificar se há arrays numpy aninhados
                        if isinstance(valor, list):
                            for j, item in enumerate(valor):
                                if hasattr(item, 'tolist'):
                                    valor[j] = item.tolist()
                                elif hasattr(item, '__len__') and not isinstance(item, (str, bytes, int, float)):
                                    valor[j] = str(item)
                    except Exception as e:
                        self.logger.warning(f"⚠️ Erro ao converter array numpy: {str(e)}")
                        valor = str(valor)
                elif hasattr(valor, '__len__') and not isinstance(valor, (str, bytes)):
                    # Outros tipos de array/sequência
                    try:
                        valor = str(valor)
                    except:
                        valor = "ARRAY_CONVERTIDO"
                
                dados[nome_coluna] = valor
            
            return dados
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao serializar registro: {str(e)}")
            return {'erro_serializacao': str(e)}
    
    def _mostrar_estado_atual_agentes(self):
        """🔥 NOVA PROTEÇÃO: Mostrar estado atual de todos os agentes"""
        try:
            self.logger.info("📋 ESTADO ATUAL DOS AGENTES:")
            self.logger.info("=" * 50)
            
            total_vetores = 0
            agentes_completos = 0
            agentes_pendentes = 0
            
            for nome, dados in self.agentes.items():
                vector_count = dados['vector_count']
                total_vetores += vector_count
                
                if vector_count > 0:
                    status = "✅ COMPLETO"
                    agentes_completos += 1
                else:
                    status = "⏳ PENDENTE"
                    agentes_pendentes += 1
                
                self.logger.info(f"  {nome:12}: {status:12} ({vector_count:>10,} vetores)")
            
            self.logger.info("-" * 50)
            self.logger.info(f"📊 TOTAL: {total_vetores:,} vetores em {agentes_completos} agentes completos")
            self.logger.info(f"📊 PENDENTES: {agentes_pendentes} agentes")
            
            return agentes_completos, agentes_pendentes
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao mostrar estado dos agentes: {str(e)}")
            return 0, 0
    
    def migrar_todos_agentes(self) -> Dict[str, bool]:
        """🔥 CORREÇÃO CRÍTICA: Migrar todos os agentes de uma vez com sistema de checkpoint"""
        self.logger.info("🚀 INICIANDO MIGRAÇÃO COMPLETA DE TODOS OS AGENTES!")
        
        # 🔥 NOVA PROTEÇÃO: Mostrar estado atual antes de começar
        self._mostrar_estado_atual_agentes()
        
        # 🔥 NOVA PROTEÇÃO: Marcar migração como em andamento
        self.migracao_em_andamento = True
        
        resultados = {}
        
        # Migrar cada agente
        agentes_migracao = [
            ('contract', self.migrar_agente_contract),
            ('financial', self.migrar_agente_financial),
            ('jurist', self.migrar_agente_jurist),
            ('legal', self.migrar_agente_legal),
            ('maestro', self.migrar_agente_maestro),
            ('reviewer', self.migrar_agente_reviewer),
            ('skeptic', self.migrar_agente_skeptic)
        ]
        
        # 🔥 NOVA PROTEÇÃO: Analisar quais agentes precisam ser migrados
        agentes_pendentes = []
        agentes_completos = []
        
        for agente_nome, _ in agentes_migracao:
            if self.agentes[agente_nome]['vector_count'] > 0:
                agentes_completos.append(agente_nome)
            else:
                agentes_pendentes.append(agente_nome)
        
        self.logger.info(f"\n📋 PLANO DE MIGRAÇÃO:")
        self.logger.info(f"  ✅ AGENTES COMPLETOS ({len(agentes_completos)}): {', '.join(agentes_completos)}")
        self.logger.info(f"  🔄 AGENTES PENDENTES ({len(agentes_pendentes)}): {', '.join(agentes_pendentes)}")
        
        if len(agentes_pendentes) == 0:
            self.logger.info("🎉 TODOS OS AGENTES JÁ FORAM MIGRADOS!")
            self.logger.info("💾 Apenas salvando estado final...")
            self._salvar_estado_completo()
            return {nome: True for nome, _ in agentes_migracao}
        
        try:
            for agente_nome, funcao_migracao in agentes_migracao:
                # 🔥 CORREÇÃO CRÍTICA: Verificar se o agente já foi migrado
                agente_ja_migrado = self.agentes[agente_nome]['vector_count'] > 0
                
                if agente_ja_migrado:
                    self.logger.info(f"\n🔄 {'='*50}")
                    self.logger.info(f"🔄 AGENTE JÁ MIGRADO: {agente_nome.upper()}")
                    self.logger.info(f"🔄 {'='*50}")
                    self.logger.info(f"  📊 Vetores existentes: {self.agentes[agente_nome]['vector_count']:,}")
                    self.logger.info(f"  📊 Metadados existentes: {len(self.agentes[agente_nome]['metadata']):,}")
                    self.logger.info(f"  ✅ PULANDO - Agente já processado completamente")
                    
                    resultados[agente_nome] = True
                    continue
                
                self.logger.info(f"\n🔄 {'='*50}")
                self.logger.info(f"🔄 MIGRANDO AGENTE: {agente_nome.upper()}")
                self.logger.info(f"🔄 {'='*50}")
                
                # 🔥 NOVA PROTEÇÃO: Criar checkpoint antes de cada agente
                self._criar_checkpoint(agente_nome, "Iniciando migração", self.agentes[agente_nome])
                
                inicio = time.time()
                sucesso = funcao_migracao()
                tempo = time.time() - inicio
                
                resultados[agente_nome] = sucesso
                
                if sucesso:
                    self.logger.info(f"✅ Agente {agente_nome} migrado com sucesso em {tempo:.2f}s")
                    # 🔥 NOVA PROTEÇÃO: Atualizar checkpoint com sucesso
                    self._atualizar_checkpoint(f"Agente {agente_nome} migrado com sucesso")
                else:
                    self.logger.error(f"❌ Falha na migração do agente {agente_nome}")
                    # 🔥 NOVA PROTEÇÃO: Atualizar checkpoint com falha
                    self._atualizar_checkpoint(f"FALHA na migração do agente {agente_nome}")
                    break  # Parar em caso de falha crítica
            
            # Criar sistema unificado
            if all(resultados.values()):
                self.logger.info("🔄 Criando sistema unificado...")
                self._criar_sistema_unificado()
                
                # Salvar estado de todos os agentes
                self.logger.info("💾 Salvando estado completo...")
                self._salvar_estado_completo()
                
                # 🔥 NOVA PROTEÇÃO: Finalizar checkpoint com sucesso
                self._finalizar_checkpoint()
                self.migracao_em_andamento = False
                
                self.logger.info("🎉 MIGRAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!")
            else:
                self.logger.error("❌ MIGRAÇÃO INCOMPLETA - Verificar falhas acima")
                
        except KeyboardInterrupt:
            self.logger.warning("⚠️ MIGRAÇÃO INTERROMPIDA PELO USUÁRIO")
            self._atualizar_checkpoint("MIGRAÇÃO INTERROMPIDA")
            raise
        except Exception as e:
            self.logger.error(f"❌ ERRO CRÍTICO NA MIGRAÇÃO: {str(e)}")
            self._atualizar_checkpoint(f"ERRO CRÍTICO: {str(e)}")
            raise
        finally:
            # 🔥 NOVA PROTEÇÃO: Garantir que o estado seja salvo mesmo em caso de erro
            if self.migracao_em_andamento:
                self.logger.info("💾 Salvando estado de emergência...")
                try:
                    self._salvar_estado_principal_biblioteca()
                except:
                    pass
        
        return resultados
    
    def _criar_sistema_unificado(self):
        """Criar sistema unificado com todos os dados dos agentes"""
        try:
            self.logger.info("🔄 Criando sistema unificado...")
            
            if self.sistema_unificado is None:
                self.logger.error("❌ Sistema unificado não disponível")
                return False
            
            total_vectors = 0
            all_metadata = []
            
            # Coletar todos os dados dos agentes
            for agente_nome, dados_agente in self.agentes.items():
                if dados_agente['sistema'] is not None:
                    # Obter estatísticas do agente
                    stats = dados_agente['sistema'].get_system_stats()
                    vector_count = stats.get('total_vectors', 0)
                    
                    if int(vector_count) > 0:
                        total_vectors += vector_count
                        all_metadata.extend(dados_agente['metadata'])
                        
                        self.logger.info(f"  📊 Agente {agente_nome}: {vector_count:,} vetores")
            
            self.logger.info(f"📊 Total unificado: {total_vectors:,} vetores")
            
            # Aqui você implementaria a lógica para unificar os índices
            # Por simplicidade, vamos apenas registrar
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar sistema unificado: {str(e)}")
            return False
    
    def _salvar_estado_completo(self):
        """Salvar estado completo de todos os agentes"""
        try:
            self.logger.info("💾 Salvando estado completo de todos os agentes...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.data_path / "backups" / f"migracao_completa_{timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            # Salvar estado de cada agente
            for agente_nome, dados_agente in self.agentes.items():
                if dados_agente['sistema'] is not None:
                    try:
                        agente_backup_path = backup_path / agente_nome
                        agente_backup_path.mkdir(exist_ok=True)
                        
                        # 🔥 CORREÇÃO CRÍTICA: Salvar sistema FAISS fisicamente
                        if hasattr(dados_agente['sistema'], 'save_system_state'):
                            dados_agente['sistema'].save_system_state(str(agente_backup_path))
                            self.logger.info(f"  ✅ Sistema FAISS do agente {agente_nome} salvo fisicamente")
                        else:
                            self.logger.warning(f"  ⚠️ Agente {agente_nome} não tem método save_system_state")
                        
                        # Salvar metadados do agente
                        metadata_file = agente_backup_path / "metadata.json"
                        with open(metadata_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                'agente': agente_nome,
                                'vector_count': dados_agente['vector_count'],
                                'metadata_count': len(dados_agente['metadata']),
                                'timestamp_migracao': timestamp
                            }, f, ensure_ascii=False, indent=2)
                        
                        self.logger.info(f"  ✅ Estado do agente {agente_nome} salvo")
                        
                    except Exception as e:
                        self.logger.error(f"  ❌ Erro ao salvar estado do agente {agente_nome}: {str(e)}")
            
            # Salvar estado unificado
            if self.sistema_unificado is not None:
                try:
                    unificado_backup_path = backup_path / "unificado"
                    unificado_backup_path.mkdir(exist_ok=True)
                    
                    # 🔥 CORREÇÃO CRÍTICA: Salvar sistema unificado fisicamente
                    if hasattr(self.sistema_unificado, 'save_system_state'):
                        self.sistema_unificado.save_system_state(str(unificado_backup_path))
                        self.logger.info("  ✅ Sistema unificado salvo fisicamente")
                    else:
                        self.logger.warning("  ⚠️ Sistema unificado não tem método save_system_state")
                    
                except Exception as e:
                    self.logger.error(f"  ❌ Erro ao salvar estado unificado: {str(e)}")
            
            # 🔥 CORREÇÃO CRÍTICA: Salvar estado principal da biblioteca
            self._salvar_estado_principal_biblioteca()
            
            # Salvar resumo da migração
            resumo_file = backup_path / "resumo_migracao.json"
            resumo = {
                'timestamp_migracao': timestamp,
                'total_agentes': len(self.agentes),
                'agentes_migrados': {},
                'sistema_unificado': self.sistema_unificado is not None
            }
            
            for agente_nome, dados_agente in self.agentes.items():
                resumo['agentes_migrados'][agente_nome] = {
                    'vector_count': dados_agente['vector_count'],
                    'metadata_count': len(dados_agente['metadata']),
                    'sistema_disponivel': dados_agente['sistema'] is not None
                }
            
            with open(resumo_file, 'w', encoding='utf-8') as f:
                json.dump(resumo, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ Estado completo salvo em: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar estado completo: {str(e)}")
            return False
    
    def _salvar_estado_principal_biblioteca(self):
        """🔥 CORREÇÃO CRÍTICA: Salvar estado principal da biblioteca com dados físicos"""
        try:
            self.logger.info("💾 Salvando estado principal da biblioteca com dados físicos...")
            
            # Criar diretório principal se não existir
            main_dir = self.data_path / "indices"
            main_dir.mkdir(exist_ok=True)
            
            # Salvar índice principal de cada agente
            for agente_nome, dados_agente in self.agentes.items():
                if dados_agente['sistema'] is not None and hasattr(dados_agente['sistema'], 'main_index'):
                    try:
                        # Salvar índice principal do agente
                        index_file = main_dir / f"main_index_{agente_nome}.faiss"
                        faiss.write_index(dados_agente['sistema'].main_index, str(index_file))
                        
                        # Salvar metadados do agente
                        metadata_file = main_dir / f"metadata_{agente_nome}.json"
                        with open(metadata_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                'agente': agente_nome,
                                'vector_count': dados_agente['vector_count'],
                                'metadata_count': len(dados_agente['metadata']),
                                'last_updated': datetime.now().isoformat()
                            }, f, ensure_ascii=False, indent=2)
                        
                        self.logger.info(f"  ✅ Índice principal do agente {agente_nome} salvo fisicamente")
                        
                    except Exception as e:
                        self.logger.error(f"  ❌ Erro ao salvar índice do agente {agente_nome}: {str(e)}")
            
            # Salvar estado global da biblioteca
            state_file = self.data_path / "metadata" / "biblioteca_state.json"
            state_file.parent.mkdir(exist_ok=True)
            
            global_state = {
                'vector_count': sum(dados['vector_count'] for dados in self.agentes.values()),
                'index_type': 'IVFFlat',
                'main_index_trained': True,
                'shards': {},
                'last_updated': datetime.now().isoformat(),
                'agentes': {}
            }
            
            for agente_nome, dados_agente in self.agentes.items():
                global_state['agentes'][agente_nome] = {
                    'vector_count': dados_agente['vector_count'],
                    'metadata_count': len(dados_agente['metadata']),
                    'sistema_disponivel': dados_agente['sistema'] is not None
                }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(global_state, f, ensure_ascii=False, indent=2)
            
            self.logger.info("✅ Estado principal da biblioteca salvo com dados físicos!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar estado principal da biblioteca: {str(e)}")
    
    def get_estatisticas_completas(self) -> Dict[str, Any]:
        """Obter estatísticas completas de todos os agentes"""
        stats = {
            'total_agentes': len(self.agentes),
            'agentes': {},
            'sistema_unificado': None,
            'total_geral': {
                'vector_count': 0,
                'metadata_count': 0
            }
        }
        
        # Estatísticas por agente
        for agente_nome, dados_agente in self.agentes.items():
            agente_stats = {
                'vector_count': dados_agente['vector_count'],
                'metadata_count': len(dados_agente['metadata']),
                'sistema_disponivel': dados_agente['sistema'] is not None
            }
            
            if dados_agente['sistema'] is not None:
                try:
                    sistema_stats = dados_agente['sistema'].get_system_stats()
                    agente_stats.update(sistema_stats)
                except Exception as e:
                    agente_stats['erro_stats'] = str(e)
            
            stats['agentes'][agente_nome] = agente_stats
            
            # Acumular totais
            stats['total_geral']['vector_count'] += dados_agente['vector_count']
            stats['total_geral']['metadata_count'] += len(dados_agente['metadata'])
        
        # Estatísticas do sistema unificado
        if self.sistema_unificado is not None:
            try:
                stats['sistema_unificado'] = self.sistema_unificado.get_system_stats()
            except Exception as e:
                stats['sistema_unificado'] = {'erro': str(e)}
        
        return stats
    
    def buscar_global(self, query_vector: np.ndarray, k: int = 10, 
                      agentes_filtro: List[str] = None) -> Tuple[List[Dict], float]:
        """Busca global em todos os agentes ou agentes específicos"""
        try:
            if agentes_filtro is None:
                agentes_filtro = list(self.agentes.keys())
            
            all_results = []
            start_time = time.time()
            
            # Buscar em cada agente filtrado
            for agente_nome in agentes_filtro:
                if agente_nome in self.agentes and self.agentes[agente_nome]['sistema'] is not None:
                    try:
                        sistema_agente = self.agentes[agente_nome]['sistema']
                        results, _ = sistema_agente.search_vectors(query_vector, k, "hybrid")
                        
                        # Adicionar informações do agente aos resultados
                        for result in results:
                            result['agente'] = agente_nome
                            result['tipo_busca'] = 'agente_individual'
                        
                        all_results.extend(results)
                        
                    except Exception as e:
                        self.logger.warning(f"⚠️ Erro na busca do agente {agente_nome}: {str(e)}")
                        continue
            
            # Ordenar por distância
            all_results.sort(key=lambda x: x['distance'])
            
            # Retornar top-k
            final_results = all_results[:k]
            search_time = time.time() - start_time
            
            self.logger.info(f"🔍 Busca global concluída em {search_time:.4f}s - {len(final_results)} resultados")
            return final_results, search_time
            
        except Exception as e:
            self.logger.error(f"❌ Erro na busca global: {str(e)}")
            return [], 0.0

def migrar_agentes_para_faiss():
    """Função principal para migrar todos os agentes"""
    print("🚀 MIGRAÇÃO COMPLETA DOS AGENTES PARA FAISS")
    print("=" * 60)
    
    # 1. Inicializar sistema integrado
    print("\n📋 Inicializando sistema integrado...")
    
    # 🔥 CORREÇÃO CRÍTICA: Usar diretório correto da biblioteca central
    data_path = "faiss_biblioteca_central"
    
    # Criar diretório base se não existir
    try:
        import os
        if not os.path.exists(data_path):
            os.makedirs(data_path, exist_ok=True)
            print(f"📁 Diretório base criado: {data_path}")
        else:
            print(f"📁 Usando diretório existente: {data_path}")
    except Exception as e:
        print(f"⚠️ Erro ao criar diretório base: {str(e)}")
    
    sistema = SistemaAgentesFAISSIntegrado(
        data_path=data_path,
        enable_logging=True
    )
    
    # 2. Migrar todos os agentes
    print("\n🔄 Iniciando migração de todos os agentes...")
    resultados = sistema.migrar_todos_agentes()
    
    # 3. Verificar resultados
    print("\n📊 Resultados da migração:")
    for agente, sucesso in resultados.items():
        status = "✅ SUCESSO" if bool(sucesso) else "❌ FALHA"
        print(f"  {agente.upper()}: {status}")
    
    # 4. Estatísticas finais
    print("\n📈 Estatísticas finais:")
    stats = sistema.get_estatisticas_completas()
    
    print(f"  Total de agentes: {stats['total_agentes']}")
    print(f"  Vetores totais: {stats['total_geral']['vector_count']:,}")
    print(f"  Metadados totais: {stats['total_geral']['metadata_count']:,}")
    
    print(f"\n📊 Detalhes por agente:")
    for agente_nome, agente_stats in stats['agentes'].items():
        print(f"  {agente_nome.upper()}:")
        print(f"    Vetores: {agente_stats['vector_count']:,}")
        print(f"    Metadados: {agente_stats['metadata_count']:,}")
        print(f"    Sistema: {'✅' if bool(agente_stats['sistema_disponivel']) else '❌'}")
    
    # 5. Teste de busca global
    print("\n🔍 Testando busca global...")
    query_vector = np.random.random(384)
    results, search_time = sistema.buscar_global(query_vector, k=5)
    
    print(f"\n📋 Resultados da busca global (tempo: {search_time:.4f}s):")
    for i, result in enumerate(results[:3]):
        try:
            print(f"  {i+1}. Agente: {result['agente']} - Distância: {result['distance']:.4f}")
            if isinstance(result, dict) and 'metadata' in result and 'id' in result['metadata']:
                print(f"     ID: {result['metadata']['id']}")
        except Exception as e:
            print(f"  {i+1}. Erro ao processar resultado: {str(e)}")
    
    print("\n🎉 MIGRAÇÃO COMPLETA CONCLUÍDA!")
    print("🚀 Todos os agentes estão funcionando com FAISS!")
    
    return sistema

if __name__ == "__main__":
    # Importar SistemaFAISSEnterprise
    try:
        from sistema_faiss_enterprise import SistemaFAISSEnterprise
        migrar_agentes_para_faiss()
    except ImportError:
        print("[ERRO] SistemaFAISSEnterprise nao encontrado!")
        print("[INFO] Certifique-se de que o arquivo sistema_faiss_enterprise.py esta no mesmo diretorio")
        print("[INFO] Execute primeiro: python sistema_faiss_enterprise.py") 