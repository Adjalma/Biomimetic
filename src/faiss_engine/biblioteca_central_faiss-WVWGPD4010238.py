import logging
import numpy as np
import faiss
import json
import pickle
import hashlib
from pathlib import Path
from datetime import datetime
from threading import RLock
from typing import List, Dict, Any, Optional, Tuple

class BibliotecaCentralFAISS:
    """
    Biblioteca Central - Índice Vetorial Unificado com Acesso Governado
    
    Funciona como uma biblioteca central onde:
    - TODOS os agentes têm acesso de LEITURA
    - Apenas o INDEXADOR tem acesso de ESCRITA
    - Conhecimento geral é centralizado e compartilhado
    """
    
    def __init__(self, base_path: str, enable_logging: bool = True):
        self.base_path = Path(base_path).resolve()
        self.lock = RLock()
        
        # Inicializar logger primeiro
        self.logger = logging.getLogger("BibliotecaCentral")
        
        # Configuração de diretórios
        self.indices_path = self.base_path / "indices"
        self.metadata_path = self.base_path / "metadata"
        self.backups_path = self.base_path / "backups"
        self.logs_path = self.base_path / "logs"
        self.temp_path = self.base_path / "temp"
        
        # Configurar logging
        self._setup_logging(enable_logging)
        
        # Criar diretórios
        self._create_directories()
        
        # Estado do sistema
        self.vector_count = 0
        self.index_type = "IVFFlat"
        self.main_index = None
        self.main_index_trained = False
        self.shards = {}
        self.shard_metadata = {}
        self.max_shard_size = 1000000  # 1M vetores por shard
        
        # Controle de acesso
        self.indexador_authorized = False
        self.agentes_authorized = True  # Todos os agentes podem ler
        
        # Inicializar sistema
        self._setup_main_index()
        self._load_existing_state()
        
        self.logger.info("🏛️ Biblioteca Central FAISS inicializada com controle de acesso governado")
    
    def _create_directories(self):
        """Criar estrutura de diretórios da biblioteca"""
        directories = [
            self.indices_path, self.metadata_path, 
            self.backups_path, self.logs_path, self.temp_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Diretório criado: {directory}")
    
    def _setup_logging(self, enable_logging: bool):
        """Configurar sistema de logging"""
        # Limpar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        if not enable_logging:
            self.logger.addHandler(logging.NullHandler())
            self.logger.setLevel(logging.CRITICAL)
            return
        
        self.logger.setLevel(logging.INFO)
        
        try:
            # Handler para arquivo
            log_file = self.logs_path / f"biblioteca_central_{datetime.now().strftime('%Y%m%d')}.log"
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
        except Exception as e:
            # Fallback se falhar
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _setup_main_index(self):
        """Configurar índice principal da biblioteca"""
        try:
            dimension = 384
            if self.index_type == "IVFFlat":
                nlist = 100  # Número de clusters
                self.main_index = faiss.IndexIVFFlat(
                    faiss.IndexFlatL2(dimension), dimension, nlist
                )
                self.main_index_trained = False
            elif self.index_type == "HNSW":
                self.main_index = faiss.IndexHNSWFlat(dimension, 32)
                self.main_index_trained = True
            else:
                self.main_index = faiss.IndexFlatL2(dimension)
                self.main_index_trained = True
            
            self.logger.info(f"🔧 Índice principal criado: {self.index_type}")
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar índice principal: {e}")
            # Fallback para FlatL2
            self.index_type = "FlatL2"
            self.main_index = faiss.IndexFlatL2(384)
            self.main_index_trained = True
    
    def _load_existing_state(self):
        """Carregar estado existente da biblioteca"""
        state_file = self.metadata_path / "biblioteca_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                self.vector_count = int(state.get('vector_count', 0))
                self.index_type = state.get('index_type', 'IVFFlat')
                self.main_index_trained = state.get('main_index_trained', False)
                
                # Carregar índices dos shards
                shards_info = state.get('shards', {})
                for shard_id, shard_info in shards_info.items():
                    shard_file = self.indices_path / f"shard_{shard_id}.faiss"
                    if shard_file.exists():
                        try:
                            shard_index = faiss.read_index(str(shard_file))
                            self.shards[int(shard_id)] = shard_index
                            self.shard_metadata[int(shard_id)] = shard_info
                        except Exception as e:
                            self.logger.warning(f"⚠️ Erro ao carregar shard {shard_id}: {e}")
                
                self.logger.info(f"📚 Estado da biblioteca carregado: {self.vector_count:,} vetores")
            except Exception as e:
                self.logger.error(f"❌ Erro ao carregar estado: {e}")
    
    def autorizar_indexador(self, token: str = None):
        """Autorizar o Indexador para escrita na biblioteca"""
        # Em produção, implementar autenticação real
        if token == "INDEXADOR_2024" or token is None:  # Simplificado para teste
            self.indexador_authorized = True
            self.logger.info("🔑 Indexador autorizado para escrita na Biblioteca Central")
            return True
        else:
            self.logger.warning("🚫 Token de autorização inválido para Indexador")
            return False
    
    def revogar_indexador(self):
        """Revogar autorização do Indexador"""
        self.indexador_authorized = False
        self.logger.info("🔒 Autorização do Indexador revogada")
    
    def adicionar_conhecimento(self, vectors: np.ndarray, metadata: List[Dict[str, Any]], 
                              source_agent: str = None) -> bool:
        """
        ADICIONAR conhecimento à Biblioteca Central (apenas Indexador autorizado)
        """
        if not self.indexador_authorized:
            self.logger.error("🚫 Acesso negado: Apenas o Indexador pode adicionar conhecimento")
            return False
        
        if not isinstance(vectors, np.ndarray) or vectors.size == 0:
            self.logger.error("❌ Vetores inválidos ou vazios")
            return False
        
        try:
            with self.lock:
                # Adicionar ao índice principal
                if not self.main_index_trained and self.index_type == "IVFFlat":
                    if len(vectors) >= 100:  # Mínimo para treinar IVFFlat
                        self.main_index.train(vectors)
                        self.main_index_trained = True
                        self.logger.info("🎯 Índice principal treinado com sucesso")
                    else:
                        # Fallback para FlatL2 se não há vetores suficientes
                        self.logger.warning("⚠️ Vetores insuficientes para IVFFlat, usando FlatL2")
                        self.index_type = "FlatL2"
                        self.main_index = faiss.IndexFlatL2(384)
                        self.main_index_trained = True
                
                # Se já temos vetores mas o índice não está treinado, treinar com os existentes
                elif not self.main_index_trained and self.index_type == "IVFFlat" and self.vector_count > 0:
                    self.logger.warning("⚠️ Índice IVFFlat não treinado mas com vetores existentes")
                    self.logger.warning("⚠️ Convertendo para FlatL2 para compatibilidade")
                    self.index_type = "FlatL2"
                    self.main_index = faiss.IndexFlatL2(384)
                    self.main_index_trained = True
                
                # Adicionar vetores
                self.main_index.add(vectors)
                self.vector_count += len(vectors)
                
                # Salvar metadados
                for i, meta in enumerate(metadata):
                    meta['id'] = self.vector_count - len(vectors) + i
                    meta['source_agent'] = source_agent
                    meta['added_timestamp'] = datetime.now().isoformat()
                
                # Salvar estado
                self._save_state()
                
                self.logger.info(f"📚 Conhecimento adicionado: {len(vectors):,} vetores de {source_agent}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao adicionar conhecimento: {e}")
            return False
    
    def buscar_conhecimento(self, query_vector: np.ndarray, k: int = 10, 
                           filters: Dict[str, Any] = None) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        BUSCAR conhecimento na Biblioteca Central (todos os agentes autorizados)
        """
        if not self.agentes_authorized:
            self.logger.error("🚫 Acesso negado: Agentes não autorizados")
            return np.array([]), []
        
        if not isinstance(query_vector, np.ndarray) or query_vector.size == 0:
            self.logger.error("❌ Vetor de consulta inválido")
            return np.array([]), []
        
        try:
            with self.lock:
                if self.vector_count == 0:
                    self.logger.warning("⚠️ Biblioteca vazia, nada para buscar")
                    return np.array([]), []
                
                if not self.main_index_trained and self.index_type == "IVFFlat":
                    self.logger.warning("⚠️ Índice principal não treinado, usando busca linear")
                    # Fallback para busca linear
                    return self._linear_search(query_vector, k, filters)
                
                # Busca normal
                start_time = datetime.now()
                distances, indices = self.main_index.search(query_vector.reshape(1, -1), k)
                search_time = (datetime.now() - start_time).total_seconds()
                
                # Processar resultados
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx != -1:  # FAISS retorna -1 para resultados inválidos
                        result = {
                            'id': int(idx),
                            'distance': float(distances[0][i]),
                            'metadata': self._get_metadata_by_id(int(idx))
                        }
                        results.append(result)
                
                self.logger.info(f"🔍 Busca concluída: {len(results)} resultados em {search_time:.4f}s")
                return distances, results
                
        except Exception as e:
            self.logger.error(f"❌ Erro na busca: {e}")
            return np.array([]), []
    
    def _linear_search(self, query_vector: np.ndarray, k: int, 
                      filters: Dict[str, Any] = None) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Busca linear como fallback"""
        # Implementação simplificada para fallback
        return np.array([]), []
    
    def _get_metadata_by_id(self, vector_id: int) -> Dict[str, Any]:
        """Obter metadados de um vetor por ID"""
        # Implementar busca em metadados
        return {'id': vector_id, 'source': 'biblioteca_central'}
    
    def _save_state(self):
        """Salvar estado atual da biblioteca"""
        try:
            state = {
                'vector_count': self.vector_count,
                'index_type': self.index_type,
                'main_index_trained': self.main_index_trained,
                'shards': {},
                'last_updated': datetime.now().isoformat()
            }
            
            # Salvar metadados dos shards
            for shard_id, metadata in self.shard_metadata.items():
                state['shards'][str(shard_id)] = metadata
            
            # Salvar estado
            state_file = self.metadata_path / "biblioteca_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            # Salvar índice principal
            index_file = self.indices_path / "main_index.faiss"
            faiss.write_index(self.main_index, str(index_file))
            
            self.logger.info("💾 Estado da biblioteca salvo com sucesso")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar estado: {e}")
    
    def get_estatisticas(self) -> Dict[str, Any]:
        """Obter estatísticas da biblioteca"""
        return {
            'total_vectors': self.vector_count,
            'index_type': self.index_type,
            'index_trained': self.main_index_trained,
            'shards_count': len(self.shards),
            'indexador_authorized': self.indexador_authorized,
            'agentes_authorized': self.agentes_authorized,
            'base_path': str(self.base_path)
        }
    
    def backup_biblioteca(self) -> bool:
        """Criar backup completo sem duplicatas (rotativo único).

        Regras:
        - Só cria/sobrescreve backup se o hash do índice atual diferir do último backup.
        - Mantém apenas um diretório fixo: backups/backup_current (sem múltiplas cópias).
        - Registra o hash do último backup em backups/last_backup_hash.txt.
        """
        if not self.indexador_authorized:
            self.logger.error("🚫 Apenas Indexador pode criar backups")
            return False

        try:
            # Caminho do índice atual salvo em disco
            current_index_path = self.indices_path / "main_index.faiss"

            # Garantir que existe um índice em disco para comparar
            try:
                # Salva o índice atual no caminho principal antes de calcular hash
                faiss.write_index(self.main_index, str(current_index_path))
            except Exception as e:
                self.logger.error(f"❌ Erro ao salvar índice principal antes do backup: {e}")
                return False

            if not current_index_path.exists():
                self.logger.error("❌ Índice principal não encontrado para backup")
                return False

            # Calcular hash SHA-256 do índice atual
            def _compute_sha256(file_path: Path) -> str:
                sha256 = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(1024 * 1024), b''):
                        sha256.update(chunk)
                return sha256.hexdigest()

            current_hash = _compute_sha256(current_index_path)

            # Verificar último hash salvo
            last_hash_file = self.backups_path / "last_backup_hash.txt"
            last_hash = None
            if last_hash_file.exists():
                try:
                    last_hash = last_hash_file.read_text(encoding='utf-8').strip()
                except Exception:
                    last_hash = None

            # Se o hash não mudou, não criar novo backup
            if last_hash and last_hash == current_hash:
                self.logger.info("🛑 Backup ignorado: índice não mudou desde o último backup")
                return False

            # Diretório de backup rotativo único
            backup_dir = self.backups_path / "backup_current"
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Limpar arquivos antigos do diretório rotativo (sem remover a pasta)
            try:
                for item in backup_dir.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            # Evitar subdiretórios, mas se existir, ignorar silenciosamente
                            pass
                    except Exception:
                        # Se não conseguir apagar algum arquivo, continua para sobrescrever
                        pass
            except Exception:
                pass

            # Escrever índice e metadados no backup rotativo
            backup_index = backup_dir / "main_index.faiss"
            faiss.write_index(self.main_index, str(backup_index))

            backup_metadata = backup_dir / "biblioteca_state.json"
            with open(backup_metadata, 'w', encoding='utf-8') as f:
                json.dump(self.get_estatisticas(), f, indent=2, ensure_ascii=False)

            # Salvar hash deste backup
            try:
                (backup_dir / "hash.txt").write_text(current_hash, encoding='utf-8')
                last_hash_file.parent.mkdir(parents=True, exist_ok=True)
                last_hash_file.write_text(current_hash, encoding='utf-8')
            except Exception as e:
                self.logger.warning(f"⚠️ Não foi possível registrar hash do backup: {e}")

            self.logger.info(f"💾 Backup atualizado em: {backup_dir}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao criar backup: {e}")
            return False
    
    def limpar_biblioteca(self) -> bool:
        """Limpar toda a biblioteca (apenas Indexador)"""
        if not self.indexador_authorized:
            self.logger.error("🚫 Apenas Indexador pode limpar a biblioteca")
            return False
        
        try:
            with self.lock:
                # Resetar índices
                self._setup_main_index()
                self.vector_count = 0
                self.shards = {}
                self.shard_metadata = {}
                
                # Salvar estado limpo
                self._save_state()
                
                self.logger.warning("🧹 Biblioteca limpa completamente")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao limpar biblioteca: {e}")
            return False

if __name__ == "__main__":
    # Teste da Biblioteca Central
    biblioteca = BibliotecaCentralFAISS("faiss_biblioteca_central")
    
    # Autorizar Indexador
    biblioteca.autorizar_indexador()
    
    # Criar vetores de teste
    test_vectors = np.random.random((100, 384)).astype('float32')
    test_metadata = [{'content': f'teste_{i}', 'type': 'exemplo'} for i in range(100)]
    
    # Adicionar conhecimento
    success = biblioteca.adicionar_conhecimento(test_vectors, test_metadata, "teste")
    
    if success:
        # Testar busca
        query_vector = np.random.random(384).astype('float32')
        distances, results = biblioteca.buscar_conhecimento(query_vector, k=5)
        
        print(f"🔍 Busca retornou {len(results)} resultados")
        
        # Estatísticas
        stats = biblioteca.get_estatisticas()
        print(f"📊 Estatísticas: {stats}")
        
        # Backup
        biblioteca.backup_biblioteca()
    else:
        print("❌ Falha ao adicionar conhecimento")
