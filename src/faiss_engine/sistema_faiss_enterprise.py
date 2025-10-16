import faiss
import numpy as np
import time
import os
import json
import pickle
import hashlib
import logging
import threading
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import gc

class SistemaFAISSEnterprise:
    """
    Sistema FAISS Enterprise para gerenciamento de 500M+ vetores
    com segurança, performance e persistência robusta
    """
    
    def __init__(self, 
                 dimension: int = 384, 
                 index_type: str = "IVFFlat",
                 max_vectors_per_shard: int = 10000000,  # 10M por shard
                 data_path: str = "faiss_enterprise_data",
                 enable_logging: bool = True):
        
        self.dimension = dimension
        self.index_type = index_type
        self.max_vectors_per_shard = max_vectors_per_shard
        self.data_path = Path(data_path)
        self.enable_logging = enable_logging
        
        # Always initialize logger
        self.logger = logging.getLogger(f"FAISSEnterprise_{self.data_path.name}")
        self.logger.propagate = False  # Prevent propagation to root logger by default
        
        if enable_logging:
            # Only set up handlers if not already configured for this logger instance
            if not self.logger.handlers:
                self._setup_logging()
        else:
            # If logging is disabled, ensure no output
            if not self.logger.handlers:  # Add NullHandler only if no handlers exist
                self.logger.addHandler(logging.NullHandler())
            self.logger.setLevel(logging.CRITICAL)  # Suppress all messages
        
        # Estruturas de dados
        self.shards = {}  # Múltiplos índices para escalabilidade
        self.metadata_shards = {}  # Metadados por shard
        self.global_metadata = {}  # Metadados globais
        self.vector_count = int(0)  # Garantir que seja sempre um inteiro
        self.last_backup = None
        
        # Controle de concorrência
        self.lock = threading.RLock()
        
        # Criar diretórios
        self._create_directories()
        
        # Configurar índice principal
        self._setup_main_index()
        
        self.logger.info(f"🚀 Sistema FAISS Enterprise inicializado - Dimensão: {dimension}")
        self.logger.info(f"📊 Configuração: {index_type}, Max por shard: {max_vectors_per_shard:,}")
    
    def _setup_logging(self):
        """Configurar sistema de logging robusto"""
        log_dir = self.data_path / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"faiss_enterprise_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Clear existing handlers to prevent duplicate logs if called multiple times
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
            if hasattr(handler, 'close'):  # Close file handlers if they are file handlers
                handler.close()
        
        # Add new handlers
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(stream_handler)
        
        self.logger.setLevel(logging.INFO)
    
    def _create_directories(self):
        """Criar estrutura de diretórios segura"""
        try:
            directories = [
                self.data_path / "shards",
                self.data_path / "metadata",
                self.data_path / "backups",
                self.data_path / "logs",
                self.data_path / "temp"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"📁 Diretório criado: {directory}")
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar diretórios: {str(e)}")
    
    def _setup_main_index(self):
        """Configurar índice principal otimizado para grandes volumes"""
        index_type_str = str(self.index_type)
        if index_type_str == "IVFFlat":
            # Índice mais eficiente para 500M+ vetores
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.main_index = faiss.IndexIVFFlat(quantizer, self.dimension, 1000)
            self.main_index.nprobe = 10  # Otimizar precisão vs velocidade
            # IVFFlat precisa ser treinado antes de aceitar vetores
            self.main_index_trained = False
        elif index_type_str == "HNSW":
            # Índice mais rápido para consultas
            self.main_index = faiss.IndexHNSWFlat(self.dimension, 64)
            self.main_index.hnsw.efConstruction = 200
            self.main_index.hnsw.efSearch = 100
            self.main_index_trained = True
        else:
            # Fallback para FlatL2
            self.main_index = faiss.IndexFlatL2(self.dimension)
            self.main_index_trained = True
        
        self.logger.info(f"✅ Índice principal {index_type_str} configurado")
    
    def _create_shard_index(self, shard_id: int) -> faiss.Index:
        """Criar índice para um shard específico"""
        index_type_str = str(self.index_type)
        if index_type_str == "IVFFlat":
            quantizer = faiss.IndexFlatL2(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            index.nprobe = 10
            # IVFFlat precisa ser treinado antes de aceitar vetores
            index_trained = False
        elif index_type_str == "HNSW":
            index = faiss.IndexHNSWFlat(self.dimension, 32)
            index.hnsw.efConstruction = 100
            index.hnsw.efSearch = 50
            index_trained = True
        else:
            index = faiss.IndexFlatL2(self.dimension)
            index_trained = True
        
        # Armazenar flag de treinamento no índice
        index.is_trained = index_trained
        return index
    
    def _get_shard_id(self, vector_count: int) -> int:
        """Determinar ID do shard baseado no número de vetores"""
        try:
            return int(vector_count) // self.max_vectors_per_shard
        except (TypeError, ValueError):
            return 0
    
    def _add_to_shard(self, vectors: np.ndarray, metadata: List[Dict], shard_id: int):
        """Adicionar vetores a um shard específico"""
        try:
            shard_id_int = int(shard_id)
        except (TypeError, ValueError):
            shard_id_int = 0
            
        if shard_id_int not in self.shards:
            self.shards[shard_id_int] = self._create_shard_index(shard_id_int)
            self.metadata_shards[shard_id_int] = []
        
        # Verificar se o índice precisa ser treinado
        shard_index = self.shards[shard_id_int]
        if hasattr(shard_index, 'is_trained') and not shard_index.is_trained:
            # Treinar o índice com os primeiros vetores
            if len(vectors) >= 100:  # Mínimo de vetores para treinar
                shard_index.train(vectors.astype('float32'))
                shard_index.is_trained = True
                self.logger.info(f"🔧 Shard {shard_id_int} treinado com {len(vectors):,} vetores")
            else:
                # Se não há vetores suficientes, usar FlatL2 como fallback
                self.logger.warning(f"⚠️ Vetores insuficientes para treinar IVFFlat, usando FlatL2")
                shard_index = faiss.IndexFlatL2(self.dimension)
                self.shards[shard_id_int] = shard_index
                shard_index.is_trained = True
        
        # Adicionar vetores ao shard
        shard_index.add(vectors.astype('float32'))
        
        # Adicionar metadados
        self.metadata_shards[shard_id_int].extend(metadata)
        
        # Atualizar contador global
        try:
            self.vector_count = int(self.vector_count) + len(vectors)
        except (TypeError, ValueError):
            self.vector_count = len(vectors)
        
        self.logger.info(f"📥 Shard {shard_id_int}: {len(vectors):,} vetores adicionados")
    
    def add_vectors_batch(self, 
                          vectors: np.ndarray, 
                          metadata: List[Dict[str, Any]],
                          batch_size: int = 100000) -> bool:
        """
        Adicionar vetores em lotes para otimizar performance
        """
        try:
            with self.lock:
                total_vectors = len(vectors)
                self.logger.info(f"📥 Iniciando adição de {total_vectors:,} vetores")
                
                # Garantir que o contador global seja um inteiro
                if not isinstance(self.vector_count, int):
                    self.vector_count = 0
                
                # Processar em lotes
                for i in range(0, total_vectors, batch_size):
                    end_idx = min(i + batch_size, total_vectors)
                    batch_vectors = vectors[i:end_idx]
                    batch_metadata = metadata[i:end_idx]
                    
                    # Determinar shard para este lote
                    current_shard_id = self._get_shard_id(self.vector_count)
                    
                    # Adicionar ao shard
                    self._add_to_shard(batch_vectors, batch_metadata, current_shard_id)
                    
                    # O contador global já foi atualizado em _add_to_shard
                    
                    # Log de progresso
                    if (i // batch_size) % 10 == 0:
                        progress = (end_idx / total_vectors) * 100
                        self.logger.info(f"📊 Progresso: {progress:.1f}% ({end_idx:,}/{total_vectors:,})")
                
                # Adicionar ao índice principal (para consultas globais)
                if str(self.index_type) != "FlatL2":
                    if hasattr(self, 'main_index_trained') and not self.main_index_trained:
                        # Treinar o índice principal com os primeiros vetores
                        if len(vectors) >= 1000:  # Mínimo de vetores para treinar
                            self.main_index.train(vectors.astype('float32'))
                            self.main_index_trained = True
                            self.logger.info(f"🔧 Índice principal treinado com {len(vectors):,} vetores")
                        else:
                            # Se não há vetores suficientes, usar FlatL2 como fallback
                            self.logger.warning(f"⚠️ Vetores insuficientes para treinar índice principal, usando FlatL2")
                            self.main_index = faiss.IndexFlatL2(self.dimension)
                            self.main_index_trained = True
                    
                    if self.main_index_trained:
                        self.main_index.add(vectors.astype('float32'))
                
                # Garantir que o contador global seja um inteiro
                if not isinstance(self.vector_count, int):
                    self.vector_count = int(self.vector_count)
                
                self.logger.info(f"✅ Adição concluída: {total_vectors:,} vetores, Total: {self.vector_count:,}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao adicionar vetores: {str(e)}")
            return False
    
    def search_vectors(self, 
                      query_vector: np.ndarray, 
                      k: int = 10,
                      search_type: str = "hybrid") -> Tuple[List[Dict], float]:
        """
        Buscar vetores mais similares com estratégias otimizadas
        """
        try:
            query_vector = query_vector.astype('float32').reshape(1, -1)
            
            start_time = time.time()
            
            if str(search_type) == "hybrid" and len(self.shards) > 1:
                # Busca híbrida em múltiplos shards
                results = self._hybrid_search(query_vector, k)
            else:
                # Busca no índice principal
                if hasattr(self, 'main_index_trained') and self.main_index_trained:
                    distances, indices = self.main_index.search(query_vector, k)
                    results = self._process_search_results(distances[0], indices[0], k)
                else:
                    # Se o índice principal não está treinado, usar busca híbrida nos shards
                    self.logger.warning("⚠️ Índice principal não treinado, usando busca híbrida")
                    results = self._hybrid_search(query_vector, k)
            
            search_time = time.time() - start_time
            
            self.logger.info(f"🔍 Busca concluída em {search_time:.4f}s - {len(results)} resultados")
            return results, search_time
            
        except Exception as e:
            self.logger.error(f"❌ Erro na busca: {str(e)}")
            return [], 0.0
    
    def _hybrid_search(self, query_vector: np.ndarray, k: int) -> List[Dict]:
        """Busca híbrida em múltiplos shards para melhor precisão"""
        all_results = []
        
        # Buscar em cada shard
        for shard_id, shard_index in self.shards.items():
            try:
                # Verificar se o shard está treinado
                if hasattr(shard_index, 'is_trained') and not shard_index.is_trained:
                    self.logger.warning(f"⚠️ Shard {shard_id} não treinado, pulando...")
                    continue
                
                distances, indices = shard_index.search(query_vector, min(k, 50))
                
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    if int(idx) < len(self.metadata_shards[shard_id]):
                        result = {
                            'shard_id': shard_id,
                            'distance': float(distance),
                            'index': int(idx),
                            'metadata': self.metadata_shards[shard_id][int(idx)]
                        }
                        all_results.append(result)
                        
            except Exception as e:
                self.logger.warning(f"⚠️ Erro no shard {shard_id}: {str(e)}")
                continue
        
        # Ordenar por distância e retornar top-k
        all_results.sort(key=lambda x: x['distance'])
        return all_results[:k]
    
    def _process_search_results(self, distances: np.ndarray, indices: np.ndarray, k: int) -> List[Dict]:
        """Processar resultados da busca"""
        results = []
        
        for i, (distance, idx) in enumerate(zip(distances, indices)):
            if int(idx) < 0:  # FAISS retorna -1 para índices inválidos
                continue
                
            result = {
                'rank': i + 1,
                'distance': float(distance),
                'index': int(idx),
                'metadata': self._get_metadata_by_index(int(idx))
            }
            results.append(result)
        
        return results
    
    def _get_metadata_by_index(self, idx: int) -> Optional[Dict]:
        """Obter metadados por índice global"""
        # Implementar busca binária ou hash para otimizar
        for shard_id, metadata_list in self.metadata_shards.items():
            if int(idx) < len(metadata_list):
                return metadata_list[int(idx)]
        return None
    
    def save_system_state(self, backup_name: str = None) -> bool:
        """
        Salvar estado completo do sistema com backup
        """
        try:
            with self.lock:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = backup_name or f"backup_{timestamp}"
                backup_path = self.data_path / "backups" / backup_name
                backup_path.mkdir(exist_ok=True)
                
                self.logger.info(f"💾 Iniciando backup: {backup_name}")
                
                # Salvar índices dos shards
                for shard_id, shard_index in self.shards.items():
                    shard_file = backup_path / f"shard_{shard_id}.faiss"
                    faiss.write_index(shard_index, str(shard_file))
                    
                    # Salvar metadados do shard
                    metadata_file = backup_path / f"shard_{shard_id}_metadata.pkl"
                    shard_data = {
                        'metadata': self.metadata_shards[shard_id],
                        'is_trained': getattr(shard_index, 'is_trained', True)
                    }
                    with open(metadata_file, 'wb') as f:
                        pickle.dump(shard_data, f)
                
                # Salvar índice principal
                main_index_file = backup_path / "main_index.faiss"
                faiss.write_index(self.main_index, str(main_index_file))
                
                # Salvar metadados globais
                global_metadata_file = backup_path / "global_metadata.json"
                with open(global_metadata_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'vector_count': self.vector_count,
                        'shard_count': len(self.shards),
                        'index_type': str(self.index_type),
                        'dimension': self.dimension,
                        'backup_timestamp': timestamp,
                        'last_backup': self.last_backup,
                        'main_index_trained': getattr(self, 'main_index_trained', True)
                    }, f, ensure_ascii=False, indent=2)
                
                # Atualizar último backup
                self.last_backup = timestamp
                
                # Limpar backups antigos (manter apenas os últimos 5)
                self._cleanup_old_backups()
                
                self.logger.info(f"✅ Backup concluído: {backup_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro no backup: {str(e)}")
            return False
    
    def load_system_state(self, backup_name: str) -> bool:
        """
        Carregar estado do sistema de um backup
        """
        try:
            with self.lock:
                backup_path = self.data_path / "backups" / backup_name
                
                if not backup_path.exists():
                    self.logger.error(f"❌ Backup não encontrado: {backup_name}")
                    return False
                
                self.logger.info(f"📂 Carregando backup: {backup_name}")
                
                # Limpar estado atual
                self.shards.clear()
                self.metadata_shards.clear()
                self.vector_count = int(0)
                
                # Carregar metadados globais
                global_metadata_file = backup_path / "global_metadata.json"
                with open(global_metadata_file, 'r', encoding='utf-8') as f:
                    global_data = json.load(f)
                
                # Carregar índices dos shards
                shard_files = list(backup_path.glob("shard_*_metadata.pkl"))
                for metadata_file in shard_files:
                    shard_id = int(metadata_file.stem.split('_')[1])
                    
                    # Carregar índice do shard
                    shard_file = backup_path / f"shard_{shard_id}.faiss"
                    if shard_file.exists():
                        self.shards[shard_id] = faiss.read_index(str(shard_file))
                    
                    # Carregar metadados do shard
                    with open(metadata_file, 'rb') as f:
                        shard_data = pickle.load(f)
                        if isinstance(shard_data, dict):
                            self.metadata_shards[shard_id] = shard_data.get('metadata', [])
                            # Restaurar status de treinamento
                            if shard_id in self.shards:
                                self.shards[shard_id].is_trained = shard_data.get('is_trained', True)
                        else:
                            # Compatibilidade com versões antigas
                            self.metadata_shards[shard_id] = shard_data
                            if shard_id in self.shards:
                                self.shards[shard_id].is_trained = True
                    
                    self.vector_count = int(self.vector_count) + len(self.metadata_shards[shard_id])
                
                # Carregar índice principal
                main_index_file = backup_path / "main_index.faiss"
                if main_index_file.exists():
                    self.main_index = faiss.read_index(str(main_index_file))
                
                # Atualizar contadores e status
                self.vector_count = int(global_data.get('vector_count', self.vector_count))
                self.main_index_trained = global_data.get('main_index_trained', True)
                
                self.logger.info(f"✅ Backup carregado: {backup_name} - {self.vector_count:,} vetores")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar backup: {str(e)}")
            return False
    
    def _cleanup_old_backups(self, keep_count: int = 5):
        """Manter apenas os backups mais recentes"""
        backup_dir = self.data_path / "backups"
        backups = sorted([d for d in backup_dir.iterdir() if d.is_dir()], 
                        key=lambda x: x.name, reverse=True)
        
        # Remover backups antigos
        for old_backup in backups[keep_count:]:
            try:
                import shutil
                shutil.rmtree(old_backup)
                self.logger.info(f"🗑️ Backup antigo removido: {old_backup.name}")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao remover backup: {str(e)}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obter estatísticas completas do sistema"""
        stats = {
            'total_vectors': int(self.vector_count),
            'shard_count': len(self.shards),
            'index_type': str(self.index_type),
            'dimension': self.dimension,
            'max_vectors_per_shard': self.max_vectors_per_shard,
            'last_backup': self.last_backup,
            'data_path': str(self.data_path),
            'main_index_trained': getattr(self, 'main_index_trained', True),
            'shard_details': {}
        }
        
        # Estatísticas por shard
        for shard_id, shard_index in self.shards.items():
            stats['shard_details'][f'shard_{shard_id}'] = {
                'vector_count': shard_index.ntotal,
                'metadata_count': len(self.metadata_shards.get(shard_id, [])),
                'index_size_mb': 0,  # Será calculado se arquivo existir
                'is_trained': getattr(shard_index, 'is_trained', True)
            }
        
        # Calcular tamanhos dos arquivos
        total_size = 0
        for shard_id in self.shards.keys():
            shard_file = self.data_path / "shards" / f"shard_{shard_id}.faiss"
            if shard_file.exists():
                size_mb = shard_file.stat().st_size / (1024 * 1024)
                stats['shard_details'][f'shard_{shard_id}']['index_size_mb'] = round(size_mb, 2)
                total_size += size_mb
        
        stats['total_size_gb'] = round(total_size / 1024, 2)
        
        return stats
    
    def optimize_index(self) -> bool:
        """Otimizar índices para melhor performance"""
        try:
            with self.lock:
                self.logger.info("🔧 Iniciando otimização dos índices...")
                
                # Otimizar cada shard
                for shard_id, shard_index in self.shards.items():
                    if hasattr(shard_index, 'is_trained') and shard_index.is_trained:
                        if hasattr(shard_index, 'make_direct_map'):
                            shard_index.make_direct_map()
                        if hasattr(shard_index, 'train'):
                            # Re-treinar se necessário
                            pass
                    else:
                        self.logger.warning(f"⚠️ Shard {shard_id} não treinado, pulando otimização")
                
                # Otimizar índice principal
                if hasattr(self, 'main_index_trained') and self.main_index_trained:
                    if hasattr(self.main_index, 'make_direct_map'):
                        self.main_index.make_direct_map()
                else:
                    self.logger.warning("⚠️ Índice principal não treinado, pulando otimização")
                
                self.logger.info("✅ Otimização concluída")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro na otimização: {str(e)}")
            return False
    
    def cleanup_temp_files(self):
        """Limpar arquivos temporários"""
        temp_dir = self.data_path / "temp"
        if temp_dir.exists():
            for temp_file in temp_dir.iterdir():
                try:
                    temp_file.unlink()
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao remover arquivo temporário: {str(e)}")
        
        # Forçar garbage collection
        gc.collect()
        self.logger.info("🧹 Limpeza de arquivos temporários concluída")

def test_sistema_enterprise():
    """Teste completo do sistema FAISS Enterprise"""
    print("🧪 TESTE COMPLETO DO SISTEMA FAISS ENTERPRISE")
    print("=" * 60)
    
    # 1. Inicializar sistema
    sistema = SistemaFAISSEnterprise(
        dimension=384,
        index_type="IVFFlat",
        max_vectors_per_shard=1000000,  # 1M por shard para teste
        enable_logging=True
    )
    
    # 2. Gerar dados de teste (simular 5M vetores)
    print("\n📊 Gerando dados de teste...")
    num_vectors = 5000000  # 5M vetores para teste
    batch_size = 100000
    
    vectors = np.random.random((num_vectors, 384)).astype('float32')
    
    metadata = []
    for i in range(num_vectors):
        metadata.append({
            'id': f'vector_{i:08d}',
            'text': f'Texto de exemplo número {i:,} para teste do sistema enterprise',
            'category': f'categoria_{i % 10}',
            'timestamp': time.time(),
            'source': 'test_data',
            'confidence': np.random.random()
        })
    
    # 3. Adicionar vetores em lotes
    print(f"\n📥 Adicionando {num_vectors:,} vetores em lotes de {batch_size:,}...")
    success = sistema.add_vectors_batch(vectors, metadata, batch_size)
    
    if not success:
        print("❌ Falha na adição de vetores")
        return False
    
    # 4. Testar busca
    print("\n🔍 Testando busca...")
    query_vector = np.random.random(384)
    results, search_time = sistema.search_vectors(query_vector, k=10, search_type="hybrid")
    
    print(f"\n📋 Resultados da busca (tempo: {search_time:.4f}s):")
    for i, result in enumerate(results[:5]):
        print(f"  {i+1}. Distância: {result['distance']:.4f} - {result['metadata']['text'][:50]}...")
    
    # 5. Salvar estado do sistema
    print("\n💾 Salvando estado do sistema...")
    backup_success = sistema.save_system_state("teste_enterprise_5M")
    
    if backup_success:
        print("✅ Backup criado com sucesso")
    else:
        print("❌ Falha no backup")
    
    # 6. Estatísticas finais
    print("\n📊 Estatísticas finais do sistema:")
    stats = sistema.get_system_stats()
    for key, value in stats.items():
        if key != 'shard_details':
            print(f"  {key}: {value}")
    
    print(f"\n📊 Detalhes dos shards:")
    for shard_name, shard_stats in stats['shard_details'].items():
        print(f"  {shard_name}: {shard_stats['vector_count']:,} vetores, {shard_stats['index_size_mb']} MB")
    
    # 7. Teste de otimização
    print("\n🔧 Testando otimização...")
    sistema.optimize_index()
    
    # 8. Limpeza
    print("\n🧹 Limpeza final...")
    sistema.cleanup_temp_files()
    
    print("\n🎉 TESTE ENTERPRISE CONCLUÍDO COM SUCESSO!")
    print(f"🚀 Sistema preparado para {stats['total_vectors']:,} vetores!")
    return True

if __name__ == "__main__":
    test_sistema_enterprise()
