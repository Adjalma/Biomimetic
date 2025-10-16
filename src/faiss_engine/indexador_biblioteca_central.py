#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INDEXADOR DA BIBLIOTECA CENTRAL - SISTEMA DE CONTROLE DE ACESSO
==============================================================

Este módulo implementa o indexador da biblioteca central que é o único processo
autorizado a escrever na biblioteca FAISS, mantendo controle total sobre a
indexação e organização do conhecimento.

ARQUITETURA DE CONTROLE:
- Apenas o Indexador tem permissão de ESCRITA na biblioteca
- Todos os agentes têm permissão de LEITURA
- Sistema de autorização e controle de acesso
- Migração controlada de conhecimento entre agentes
- Gerenciamento centralizado de metadados

FUNCIONALIDADES PRINCIPAIS:
1. Migração de conhecimento dos agentes para biblioteca central
2. Controle de acesso exclusivo para escrita
3. Processamento e indexação de novos dados
4. Gerenciamento de metadados e organização
5. Validação e integridade dos dados
6. Backup e recuperação de índices

RESPONSABILIDADES:
- Migrar conhecimento dos agentes para a Biblioteca Central
- Manter controle de acesso (apenas ele pode escrever)
- Processar novos dados e adicionar à biblioteca
- Gerenciar metadados e organização do conhecimento
- Validar integridade dos dados indexados
- Coordenar operações de backup e recuperação

COMPONENTES:
- IndexadorBibliotecaCentral: Classe principal do indexador
- Sistema de autorização e controle de acesso
- Processador de dados e metadados
- Validador de integridade
- Gerenciador de migração

FLUXO DE INDEXAÇÃO:
1. Autorização → Validação → Recebimento de dados
2. Processamento → Limpeza → Validação
3. Indexação → Metadados → Integração
4. Verificação → Backup → Confirmação

Versão: 2.0
Data: 2024
Autor: Sistema IA Autoevolutiva
"""

# =============================================================================
# IMPORTS E DEPENDÊNCIAS
# =============================================================================

import os             # Operações de sistema de arquivos
import sqlite3        # Banco de dados SQLite para metadados
import numpy as np    # Computação numérica otimizada
import logging        # Sistema de logging avançado
from pathlib import Path  # Manipulação de caminhos de arquivos
from datetime import datetime  # Timestamps e data/hora
from typing import List, Dict, Any, Optional, Tuple  # Type hints
from biblioteca_central_faiss import BibliotecaCentralFAISS  # Biblioteca central

# =============================================================================
# CLASSE PRINCIPAL DO INDEXADOR
# =============================================================================

class IndexadorBibliotecaCentral:
    """
    INDEXADOR DA BIBLIOTECA CENTRAL - SISTEMA DE CONTROLE DE ACESSO
    
    Esta classe implementa o indexador da biblioteca central que é o único
    processo autorizado a escrever na biblioteca FAISS, mantendo controle
    total sobre a indexação e organização do conhecimento.
    
    ARQUITETURA DE CONTROLE:
    - Apenas o Indexador tem permissão de ESCRITA na biblioteca
    - Todos os agentes têm permissão de LEITURA
    - Sistema de autorização e controle de acesso
    - Migração controlada de conhecimento entre agentes
    - Gerenciamento centralizado de metadados
    
    FUNCIONALIDADES PRINCIPAIS:
    1. Migração de conhecimento dos agentes para biblioteca central
    2. Controle de acesso exclusivo para escrita
    3. Processamento e indexação de novos dados
    4. Gerenciamento de metadados e organização
    5. Validação e integridade dos dados
    6. Backup e recuperação de índices
    
    FLUXO DE INDEXAÇÃO:
    1. Autorização → Validação → Recebimento de dados
    2. Processamento → Limpeza → Validação
    3. Indexação → Metadados → Integração
    4. Verificação → Backup → Confirmação
    """
    
    def __init__(self, biblioteca_path: str = "faiss_biblioteca_central", enable_logging: bool = True):
        """
        INICIALIZAÇÃO DO INDEXADOR DA BIBLIOTECA CENTRAL
        
        Configura e inicializa o indexador com controle de acesso exclusivo
        para escrita na biblioteca central FAISS.
        
        PARÂMETROS:
        - biblioteca_path (str): Caminho para a biblioteca central FAISS
        - enable_logging (bool): Se deve habilitar logging detalhado
        
        ATRIBUTOS INICIALIZADOS:
        - biblioteca_path: Caminho da biblioteca central
        - biblioteca: Instância da biblioteca central FAISS
        - logger: Sistema de logging do indexador
        """
        # Configurar caminho da biblioteca central
        self.biblioteca_path = biblioteca_path
        
        # Inicializar biblioteca central FAISS
        self.biblioteca = BibliotecaCentralFAISS(biblioteca_path, enable_logging)
        
        # Autorizar o Indexador para operações de escrita
        self.biblioteca.autorizar_indexador()
        
        # Configurar sistema de logging
        self._setup_logging(enable_logging)
        
        # Caminhos dos bancos SQLite originais
        self.agents_path = Path("agents")
        self.evolution_path = Path("evolution_files")
        
        self.logger.info("🔧 Indexador da Biblioteca Central inicializado e autorizado")
        self.logger.info(f"📂 Migrando dos bancos SQLite originais: {self.agents_path} e {self.evolution_path}")
    
    def _setup_logging(self, enable_logging: bool):
        """Configurar logging do Indexador"""
        self.logger = logging.getLogger("IndexadorBiblioteca")
        self.logger.setLevel(logging.INFO)
        
        if not enable_logging:
            self.logger.addHandler(logging.NullHandler())
            self.logger.setLevel(logging.CRITICAL)
            return
        
        # Limpar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler para arquivo
        log_file = Path(self.biblioteca_path) / "logs" / f"indexador_{datetime.now().strftime('%Y%m%d')}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def migrar_conhecimento_completo(self) -> Dict[str, Any]:
        """
        Migrar TODO o conhecimento dos sistemas FAISS existentes para a Biblioteca Central
        
        Retorna estatísticas da migração
        """
        self.logger.info("🚀 INICIANDO MIGRAÇÃO COMPLETA PARA BIBLIOTECA CENTRAL")
        self.logger.info("=" * 60)
        self.logger.info("📂 Migrando dos bancos SQLite originais (internos e externos)")
        
        # Estatísticas da migração
        stats = {
            'total_vectors_migrated': 0,
            'agents_processed': 0,
            'errors': [],
            'start_time': datetime.now(),
            'end_time': None
        }
        
        # Lista de agentes
        agentes = ['contract', 'financial', 'jurist', 'legal', 'maestro', 'reviewer', 'skeptic']
        
        # Migrar agentes individuais
        for agente in agentes:
            try:
                self.logger.info(f"🔄 Migrando conhecimento do agente: {agente.upper()}")
                self.logger.info("-" * 40)
                
                # Migrar banco interno
                internal_stats = self._migrar_banco_interno(agente)
                if internal_stats:
                    stats['total_vectors_migrated'] += internal_stats['vectors_migrated']
                
                # Migrar banco externo
                external_stats = self._migrar_banco_externo(agente)
                if external_stats:
                    stats['total_vectors_migrated'] += external_stats['vectors_migrated']
                
                stats['agents_processed'] += 1
                self.logger.info(f"✅ Agente {agente} migrado com sucesso")
                
                # Salvar estado intermediário a cada agente
                try:
                    self.biblioteca._save_state()
                    self.logger.info(f"💾 Estado salvo após migração do agente {agente}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao salvar estado intermediário: {e}")
                
            except Exception as e:
                error_msg = f"❌ Erro ao migrar agente {agente}: {e}"
                self.logger.error(error_msg)
                stats['errors'].append(error_msg)
                
                # Continuar com o próximo agente em caso de erro
                continue
        
        # Finalizar estatísticas
        stats['end_time'] = datetime.now()
        duration = (stats['end_time'] - stats['start_time']).total_seconds()
        
        self.logger.info("=" * 60)
        self.logger.info(f"🎉 MIGRAÇÃO COMPLETA CONCLUÍDA!")
        self.logger.info(f"📊 Total de vetores migrados: {stats['total_vectors_migrated']:,}")
        self.logger.info(f"👥 Agentes processados: {stats['agents_processed']}")
        self.logger.info(f"⏱️ Tempo total: {duration:.2f} segundos")
        
        if stats['errors']:
            self.logger.warning(f"⚠️ {len(stats['errors'])} erros encontrados durante a migração")
        
        return stats
    
    def _migrar_banco_interno(self, agente: str) -> Optional[Dict[str, Any]]:
        """Migrar banco interno de um agente"""
        db_path = self.agents_path / f"agente_{agente}" / "memory.db"
        
        if not db_path.exists():
            self.logger.warning(f"⚠️ Banco interno não encontrado: {db_path}")
            return None
        
        try:
            self.logger.info(f"📂 Migrando banco interno: {db_path}")
            
            # Conectar ao banco
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Verificar tabelas disponíveis
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            total_vectors = 0
            
            # Processar cada tabela
            for table in tables:
                if table in ['learned_facts', 'conversations', 'knowledge_base']:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        
                        if count > 0:
                            self.logger.info(f"📋 Processando tabela: {table}")
                            
                            # Processar em lotes
                            batch_size = 10000
                            for i in range(0, count, batch_size):
                                # Extrair dados reais da tabela
                                cursor.execute(f"SELECT * FROM {table} LIMIT {batch_size} OFFSET {i}")
                                rows = cursor.fetchall()
                                
                                if not rows:
                                    break
                                
                                batch_count = len(rows)
                                
                                # Extrair vetores reais ou gerar embeddings baseados no conteúdo
                                vectors = self._extrair_vetores_reais(rows, table, agente, batch_count)
                                
                                if vectors is not None and len(vectors) > 0:
                                    # Criar metadados baseados no conteúdo real
                                    metadata = []
                                    for j, row in enumerate(rows):
                                        meta = {
                                            'agent': agente,
                                            'source': 'banco_interno',
                                            'table': table,
                                            'record_id': i + j,
                                            'content': str(row)[:200],  # Primeiros 200 chars do conteúdo
                                            'migrated_timestamp': datetime.now().isoformat()
                                        }
                                        metadata.append(meta)
                                    
                                    # Adicionar à biblioteca central
                                    success = self.biblioteca.adicionar_conhecimento(vectors, metadata, agente)
                                    
                                    if success:
                                        total_vectors += batch_count
                                        self.logger.info(f"📚 Conhecimento adicionado: {batch_count:,} vetores de {agente}")
                                        self.logger.info(f"⚡ Lote processado: {batch_count:,} vetores")
                                    else:
                                        self.logger.error(f"❌ Falha ao adicionar lote de {agente}")
                                        break
                                else:
                                    self.logger.warning(f"⚠️ Nenhum vetor válido extraído do lote {i//batch_size + 1}")
                                    
                    except Exception as e:
                        self.logger.warning(f"⚠️ Erro ao processar tabela {table}: {e}")
                        continue
            
            conn.close()
            
            if total_vectors > 0:
                self.logger.info(f"✅ Total migrado do banco interno de {agente}: {total_vectors:,} vetores")
                return {'vectors_migrated': total_vectors, 'source': 'banco_interno'}
            else:
                self.logger.warning(f"⚠️ Nenhum vetor migrado do banco interno de {agente}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao migrar banco interno de {agente}: {e}")
            return None
    
    def _extrair_vetores_reais(self, rows, table_name, agente, batch_count):
        """Extrai vetores reais dos dados das tabelas"""
        try:
            vectors = []
            
            for row in rows:
                # Tentar extrair vetor real se existir
                if len(row) > 1 and isinstance(row[1], bytes):
                    # Se o segundo campo é bytes, pode ser um vetor serializado
                    try:
                        vector = np.frombuffer(row[1], dtype=np.float32)
                        if len(vector) == 384:  # Dimensão esperada
                            # Validar vetor antes de adicionar
                            if np.all(np.isfinite(vector)):
                                vectors.append(vector)
                                continue
                    except:
                        pass
                
                # Se não conseguiu extrair vetor real, gerar embedding baseado no conteúdo
                content = str(row)
                vector = self._gerar_embedding_do_conteudo(content, agente)
                if vector is not None and np.all(np.isfinite(vector)):
                    vectors.append(vector)
            
            if vectors:
                # Validação final de todos os vetores
                vectors_array = np.array(vectors, dtype=np.float32)
                
                # Verificar se há vetores válidos
                valid_mask = np.all(np.isfinite(vectors_array), axis=1)
                valid_vectors = vectors_array[valid_mask]
                
                if len(valid_vectors) > 0:
                    self.logger.info(f"✅ {len(valid_vectors)} vetores válidos extraídos de {len(vectors)} total")
                    return valid_vectors
                else:
                    self.logger.warning(f"⚠️ Nenhum vetor válido encontrado em {len(vectors)} vetores")
                    return None
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair vetores reais: {e}")
            return None
    
    def _gerar_embedding_do_conteudo(self, content, agente):
        """Gera embedding baseado no conteúdo usando hash determinístico"""
        try:
            import hashlib
            
            # Usar hash MD5 do conteúdo para gerar vetor determinístico
            hash_obj = hashlib.md5(content.encode('utf-8'))
            hash_bytes = hash_obj.digest()
            
            # Converter hash para vetor de 384 dimensões
            vector = np.frombuffer(hash_bytes, dtype=np.float32)
            
            # Expandir para 384 dimensões se necessário
            if len(vector) < 384:
                # Repetir o hash para preencher as dimensões
                repetitions = (384 // len(vector)) + 1
                vector = np.tile(vector, repetitions)[:384]
            elif len(vector) > 384:
                vector = vector[:384]
            
            # Garantir que não há valores NaN ou Inf
            vector = np.nan_to_num(vector, nan=0.0, posinf=1.0, neginf=-1.0)
            
            # Normalizar para valores entre -1 e 1 de forma segura
            vector_mean = np.mean(vector)
            vector_std = np.std(vector)
            
            if vector_std > 1e-8:  # Evitar divisão por zero
                vector = (vector - vector_mean) / vector_std
                # Clamp para evitar valores extremos
                vector = np.clip(vector, -3.0, 3.0)
            else:
                # Se std é muito pequeno, usar valores pequenos aleatórios
                vector = np.random.uniform(-0.1, 0.1, 384).astype(np.float32)
            
            # Verificação final de validade
            if not np.all(np.isfinite(vector)):
                # Fallback: vetor simples baseado no hash
                vector = np.zeros(384, dtype=np.float32)
                for i in range(min(len(hash_bytes), 384)):
                    vector[i] = (hash_bytes[i] - 128) / 128.0
            
            return vector.astype(np.float32)
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar embedding: {e}")
            # Fallback: vetor zero
            return np.zeros(384, dtype=np.float32)
    
    def _migrar_banco_externo(self, agente: str) -> Optional[Dict[str, Any]]:
        """Migrar banco externo de um agente"""
        db_path = self.evolution_path / f"memoria_externa_{agente}.db"
        
        if not db_path.exists():
            self.logger.warning(f"⚠️ Banco externo não encontrado: {db_path}")
            return None
        
        try:
            self.logger.info(f"📂 Migrando banco externo: {db_path}")
            
            # Conectar ao banco
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Verificar tabelas disponíveis
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            total_vectors = 0
            
            # Processar cada tabela
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        self.logger.info(f"📋 Processando tabela externa: {table}")
                        
                        # Processar em lotes
                        batch_size = 10000
                        for i in range(0, count, batch_size):
                            # Extrair dados reais da tabela
                            cursor.execute(f"SELECT * FROM {table} LIMIT {batch_size} OFFSET {i}")
                            rows = cursor.fetchall()
                            
                            if not rows:
                                break
                            
                            batch_count = len(rows)
                            
                            # Extrair vetores reais ou gerar embeddings baseados no conteúdo
                            vectors = self._extrair_vetores_reais(rows, table, agente, batch_count)
                            
                            if vectors is not None and len(vectors) > 0:
                                # Criar metadados baseados no conteúdo real
                                metadata = []
                                for j, row in enumerate(rows):
                                    meta = {
                                        'agent': agente,
                                        'source': 'banco_externo',
                                        'table': table,
                                        'record_id': i + j,
                                        'content': str(row)[:200],  # Primeiros 200 chars do conteúdo
                                        'migrated_timestamp': datetime.now().isoformat()
                                    }
                                    metadata.append(meta)
                                
                                # Adicionar à biblioteca central
                                success = self.biblioteca.adicionar_conhecimento(vectors, metadata, agente)
                                
                                if success:
                                    total_vectors += batch_count
                                    self.logger.info(f"📚 Conhecimento externo adicionado: {batch_count:,} vetores de {agente}")
                                    self.logger.info(f"⚡ Lote externo processado: {batch_count:,} vetores")
                                else:
                                    self.logger.error(f"❌ Falha ao adicionar lote externo de {agente}")
                                    break
                            else:
                                self.logger.warning(f"⚠️ Nenhum vetor válido extraído do lote externo {i//batch_size + 1}")
                                
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao processar tabela externa {table}: {e}")
                    continue
            
            conn.close()
            
            if total_vectors > 0:
                self.logger.info(f"✅ Total migrado do banco externo de {agente}: {total_vectors:,} vetores")
                return {'vectors_migrated': total_vectors, 'source': 'banco_externo'}
            else:
                self.logger.warning(f"⚠️ Nenhum vetor migrado do banco externo de {agente}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao migrar banco externo de {agente}: {e}")
            return None
    
    def adicionar_novo_conhecimento(self, vectors: np.ndarray, metadata: List[Dict[str, Any]], 
                                   source_agent: str) -> bool:
        """
        Adicionar novo conhecimento à Biblioteca Central
        
        Usado quando agentes geram novos conhecimentos
        """
        try:
            success = self.biblioteca.adicionar_conhecimento(vectors, metadata, source_agent)
            
            if success:
                self.logger.info(f"📚 Novo conhecimento adicionado: {len(vectors):,} vetores de {source_agent}")
            else:
                self.logger.error(f"❌ Falha ao adicionar novo conhecimento de {source_agent}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao adicionar novo conhecimento: {e}")
            return False
    
    def buscar_conhecimento(self, query_vector: np.ndarray, k: int = 10, 
                           filters: Dict[str, Any] = None) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Buscar conhecimento na Biblioteca Central
        
        Usado pelos agentes para consultar conhecimento compartilhado
        """
        try:
            distances, results = self.biblioteca.buscar_conhecimento(query_vector, k, filters)
            return distances, results
            
        except Exception as e:
            self.logger.error(f"❌ Erro na busca: {e}")
            return np.array([]), []
    
    def get_estatisticas_biblioteca(self) -> Dict[str, Any]:
        """Obter estatísticas da Biblioteca Central"""
        return self.biblioteca.get_estatisticas()
    
    def criar_backup_biblioteca(self) -> bool:
        """Criar backup da Biblioteca Central"""
        return self.biblioteca.backup_biblioteca()
    
    def limpar_biblioteca(self) -> bool:
        """Limpar toda a Biblioteca Central (cuidado!)"""
        self.logger.warning("⚠️ ATENÇÃO: Limpando toda a Biblioteca Central!")
        return self.biblioteca.limpar_biblioteca()

if __name__ == "__main__":
    # Teste do Indexador
    print("🔧 Testando Indexador da Biblioteca Central...")
    
    indexador = IndexadorBibliotecaCentral()
    
    # Limpar biblioteca para começar do zero
    print("🧹 Limpando biblioteca para migração limpa...")
    indexador.limpar_biblioteca()
    
    # Verificar estatísticas iniciais
    stats_iniciais = indexador.get_estatisticas_biblioteca()
    print(f"📊 Estatísticas iniciais: {stats_iniciais}")
    
    # Executar migração completa dos bancos SQLite originais
    print("\n🚀 Iniciando migração dos bancos SQLite originais para Biblioteca Central...")
    stats_migracao = indexador.migrar_conhecimento_completo()
    
    # Verificar estatísticas finais
    stats_finais = indexador.get_estatisticas_biblioteca()
    print(f"\n📊 Estatísticas finais: {stats_finais}")
    
    # Testar busca
    print("\n🔍 Testando busca na biblioteca...")
    query_vector = np.random.random(384).astype('float32')
    distances, results = indexador.buscar_conhecimento(query_vector, k=5)
    
    print(f"🔍 Busca retornou {len(results)} resultados")
    
    # Criar backup
    print("\n💾 Criando backup...")
    indexador.criar_backup_biblioteca()
    
    print("\n✅ Teste do Indexador concluído!")
