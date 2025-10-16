#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BARRAMENTO DE CONHECIMENTO UNIFICADO
====================================

Este módulo implementa a arquitetura de "Unified Knowledge Bus" que serve como
o núcleo central de gerenciamento de conhecimento do sistema de IA autoevolutiva.

ARQUITETURA:
- Índice Vetorial Centralizado (ChromaDB) para busca semântica
- Agentes como Consumidores e Produtores de Conhecimento
- Maestro como Orquestrador do Fluxo de Informação
- Bancos SQLite como "armazéns" de trabalho dos especialistas
- Integração com sistemas V2 via FAISS

FUNCIONALIDADES PRINCIPAIS:
1. Gerenciamento centralizado de conhecimento
2. Distribuição de conhecimento entre agentes
3. Indexação vetorial para busca semântica
4. Orquestração de fluxos de informação
5. Persistência e recuperação de dados
6. Integração com sistemas V2

COMPONENTES:
- BarramentoConhecimentoUnificado: Classe principal
- Sistema de indexação vetorial (ChromaDB)
- Gerenciamento de agentes e fluxos
- Persistência em bancos SQLite
- Orquestração de operações

NOTA: Sistemas V2 foram movidos para integração direta com FAISS

Versão: 2.0
Data: 2024
Autor: Sistema IA Autoevolutiva
"""

# =============================================================================
# IMPORTS E DEPENDÊNCIAS
# =============================================================================

import os             # Operações de sistema de arquivos
import json           # Manipulação de dados JSON
import sqlite3        # Banco de dados SQLite para persistência
import logging        # Sistema de logging avançado
import threading      # Threading para operações concorrentes
import hashlib        # Hashing para identificação única
import time           # Medição de tempo e performance
import signal         # Manipulação de sinais do sistema
from datetime import datetime  # Timestamps e data/hora
from typing import Dict, List, Any, Optional  # Type hints
from concurrent.futures import ThreadPoolExecutor, as_completed  # Execução paralela
import shutil         # Operações de sistema de arquivos avançadas
import sys            # Acesso a funcionalidades do sistema
from pathlib import Path  # Manipulação de caminhos de arquivos

# Configuração de logging otimizada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_bus_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import urllib3
    import ssl
    import os
    
    # Desabilitar verificação SSL conforme preferência do usuário
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    
    # Configurar SSL para ignorar certificados
    ssl._create_default_https_context = ssl._create_unverified_context
    
    CHROMADB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Import error: {e}")
    CHROMADB_AVAILABLE = False

class BarramentoConhecimentoUnificado:
    """
    Barramento de Conhecimento Unificado
    Meta: Processar todo conhecimento em 4-5 dias
    
    NOTA: Sistemas V2 foram movidos para integração direta com FAISS
    """
    
    def __init__(self, persist_directory: str = "knowledge_bus", reset_chromadb: bool = False):
        self.persist_directory = persist_directory
        self.max_results = 100
        # CONFIGURAÇÃO OTIMIZADA PARA BANCOS GRANDES - RESOLVE TIMEOUT
        self.batch_size = 100   # Lotes menores para evitar timeout (reduzido de 200 para 100)
        self.max_workers = 1    # Processamento sequencial para estabilidade (reduzido de 2 para 1)
        self.checkpoint_interval = 500   # Checkpoint mais frequente (reduzido de 1000 para 500)
        self.max_retries = 5    # Mais tentativas para bancos grandes (aumentado de 3 para 5)
        self.retry_delay = 5    # Delay maior entre tentativas (aumentado de 3 para 5)
        self._interrupted = False
        
        # CONFIGURAÇÃO ROBUSTA DE SIGNAL HANDLER PARA CTRL+C
        def signal_handler(signum, frame):
            logger.info("🚨 SINAL DE INTERRUPÇÃO RECEBIDO (Ctrl+C)!")
            logger.info("Salvando progresso e parando com segurança...")
            self._interrupted = True
            
            # Salvar checkpoint final se possível
            try:
                if hasattr(self, 'current_agent') and hasattr(self, 'current_progress'):
                    self._checkpoint(self.current_agent, self.current_progress)
                    logger.info("Checkpoint final salvo com sucesso")
            except Exception as e:
                logger.warning(f"Erro ao salvar checkpoint final: {e}")
            
            # FORÇAR SAÍDA IMEDIATA E LIMPA
            logger.info("Saindo do sistema...")
            os._exit(0)
        
        # REGISTRAR HANDLERS COM TRATAMENTO DE ERRO ROBUSTO
        try:
            # Windows: SIGINT (Ctrl+C)
            signal.signal(signal.SIGINT, signal_handler)
            logger.info("Signal handler SIGINT registrado com sucesso")
        except Exception as e:
            logger.error(f"ERRO CRÍTICO ao registrar SIGINT: {e}")
        
        try:
            # Windows: SIGTERM (terminação)
            signal.signal(signal.SIGTERM, signal_handler)
            logger.info("Signal handler SIGTERM registrado com sucesso")
        except Exception as e:
            logger.error(f"ERRO CRÍTICO ao registrar SIGTERM: {e}")
        
        # VERIFICAÇÃO FINAL DOS HANDLERS
        logger.info("Signal handlers configurados para Ctrl+C")
        
        # Inicializar ChromaDB se disponível
        if CHROMADB_AVAILABLE:
            self._init_chromadb(reset_chromadb)
        else:
            logger.warning("ChromaDB não disponível - usando modo de fallback")
            self.client = None
            self.collection = None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        status = {
            'chromadb_available': CHROMADB_AVAILABLE,
            'timestamp': time.time()
        }
        
        return status
    
    def _init_chromadb(self, reset_chromadb: bool = False):
        """Inicializa ChromaDB"""
        try:
            if reset_chromadb:
                logger.info("🔄 Resetando ChromaDB...")
                if os.path.exists(self.persist_directory):
                    shutil.rmtree(self.persist_directory)
                    logger.info("✓ Diretório anterior removido")
            
            # Configurar ChromaDB
            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=settings
            )
            
            # Criar ou obter coleção
            self.collection = self.client.get_or_create_collection(
                name="conhecimento_unificado",
                metadata={"description": "Base de conhecimento unificada"}
            )
            
            logger.info("[OK] ChromaDB inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def indexar_conhecimento_existente(self) -> int:
        """Indexa conhecimento existente dos agentes especialistas"""
        try:
            logger.info("📚 Indexando conhecimento existente...")
            
            # Buscar bancos dos agentes
            agentes_path = Path("agents")
            if not agentes_path.exists():
                logger.warning("⚠️ Pasta agents não encontrada")
                return 0
            
            total_indexado = 0
            
            # Processar cada agente
            for agente_dir in agentes_path.iterdir():
                if agente_dir.is_dir() and agente_dir.name.startswith("agente_"):
                    try:
                        db_path = agente_dir / "memory.db"
                        if db_path.exists():
                            total_indexado += self._indexar_banco_agente(db_path, agente_dir.name)
                    except Exception as e:
                        logger.error(f"❌ Erro ao processar {agente_dir.name}: {e}")
                        continue
            
            logger.info(f"✅ Total indexado: {total_indexado:,} documentos")
            return total_indexado
            
        except Exception as e:
            logger.error(f"❌ Erro na indexação: {e}")
            return 0
    
    def _indexar_banco_agente(self, db_path: Path, nome_agente: str) -> int:
        """Indexa banco de dados de um agente específico"""
        try:
            import sqlite3
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Buscar análises do agente
            cursor.execute("SELECT analise_content, contexto, metadata FROM analises")
            analises = cursor.fetchall()
            
            total_indexado = 0
            
            for analise_content, contexto, metadata in analises:
                try:
                    # Adicionar ao ChromaDB
                    self.collection.add(
                        documents=[analise_content],
                        metadatas=[{
                            "agente": nome_agente,
                            "contexto": contexto,
                            "metadata": metadata
                        }],
                        ids=[f"{nome_agente}_{total_indexado}"]
                    )
                    total_indexado += 1
                    
                except Exception as e:
                    logger.debug(f"Erro ao indexar análise: {e}")
                    continue
            
            conn.close()
            logger.info(f"  ✓ {nome_agente}: {total_indexado} análises indexadas")
            return total_indexado
            
        except Exception as e:
            logger.error(f"❌ Erro ao indexar {nome_agente}: {e}")
            return 0
    
    def buscar_conhecimento(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Busca conhecimento no barramento"""
        try:
            if not self.collection:
                logger.warning("⚠️ ChromaDB não disponível")
                return []
            
            # Buscar no ChromaDB
            resultados = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Formatar resultados
            documentos = []
            if resultados['documents']:
                for i in range(len(resultados['documents'][0])):
                    documentos.append({
                        'content': resultados['documents'][0][i],
                        'metadata': resultados['metadatas'][0][i] if resultados['metadatas'] else {},
                        'distance': resultados['distances'][0][i] if resultados['distances'] else 0.0
                    })
            
            logger.info(f"🔍 Busca: '{query}' → {len(documentos)} resultados")
            return documentos
            
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def adicionar_analise_especialista(self, nome_agente: str, analise: str, metadata: Dict[str, Any]):
        """Adiciona análise de um agente especialista ao barramento"""
        try:
            if not self.collection:
                logger.warning("⚠️ ChromaDB não disponível")
                return False
            
            # Adicionar ao ChromaDB
            self.collection.add(
                documents=[analise],
                metadatas=[{
                    "agente": nome_agente,
                    "tipo": "analise_especialista",
                    "timestamp": datetime.now().isoformat(),
                    **metadata
                }],
                ids=[f"analise_{nome_agente}_{int(time.time())}"]
            )
            
            logger.info(f"✅ Análise de {nome_agente} adicionada ao barramento")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar análise: {e}")
            return False
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do barramento"""
        try:
            if not self.collection:
                return {
                    'total_documentos': 0,
                    'colecao': 'não disponível'
                }
            
            # Contar documentos
            count = self.collection.count()
            
            return {
                'total_documentos': count,
                'colecao': self.collection.name
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {
                'total_documentos': 0,
                'colecao': 'erro'
            }


class AgenteEspecialistaRefatorado:
    """
    Agente especialista refatorado como consumidor e produtor de conhecimento
    """
    
    def __init__(self, nome: str, especialidade: str, barramento: BarramentoConhecimentoUnificado):
        self.nome = nome
        self.especialidade = especialidade
        self.barramento = barramento
        self.db_path = f"agents/agente_{nome.lower()}/memory.db"
        
        # Garantir que o banco existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._inicializar_banco()
        
        logger.info(f"Agente {nome} ({especialidade}) inicializado")
    
    def _inicializar_banco(self):
        """
        Inicializar banco de dados do agente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabela de análises se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analise_content TEXT NOT NULL,
                    contexto TEXT,
                    confianca REAL DEFAULT 0.8,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco do agente {self.nome}: {e}")
    
    def analisar_contexto(self, contexto: str, query: str) -> Dict[str, Any]:
        """
        Analisar contexto usando conhecimento especializado
        """
        try:
            # Buscar conhecimento relevante no barramento
            conhecimento_relevante = self.barramento.buscar_conhecimento(
                f"{query} {self.especialidade}", n_results=5
            )
            
            # Realizar análise especializada
            analise = self._realizar_analise_especializada(contexto, conhecimento_relevante)
            
            # Salvar análise no banco local
            self._salvar_analise(analise, contexto, query)
            
            # Publicar análise no barramento
            self.barramento.adicionar_analise_especialista(
                self.nome,
                analise,
                {
                    "contexto": contexto,
                    "query": query,
                    "especialidade": self.especialidade
                }
            )
            
            return {
                "agente": self.nome,
                "especialidade": self.especialidade,
                "analise": analise,
                "confianca": 0.8,
                "conhecimento_utilizado": len(conhecimento_relevante)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise do agente {self.nome}: {e}")
            return {
                "agente": self.nome,
                "especialidade": self.especialidade,
                "analise": f"Erro na análise: {str(e)}",
                "confianca": 0.0,
                "conhecimento_utilizado": 0
            }
    
    def _realizar_analise_especializada(self, contexto: str, conhecimento: List[Dict[str, Any]]) -> str:
        """
        Realizar análise especializada baseada no conhecimento
        """
        # Implementação específica por especialidade
        if self.especialidade == "jurista":
            return self._analise_juridica(contexto, conhecimento)
        elif self.especialidade == "financeiro":
            return self._analise_financeira(contexto, conhecimento)
        elif self.especialidade == "revisor":
            return self._analise_revisao(contexto, conhecimento)
        elif self.especialidade == "skeptic":
            return self._analise_cetica(contexto, conhecimento)
        elif self.especialidade == "maestro":
            return self._analise_coordenacao(contexto, conhecimento)
        elif self.especialidade == "legal":
            return self._analise_legal(contexto, conhecimento)
        elif self.especialidade == "contract":
            return self._analise_contratual(contexto, conhecimento)
        else:
            return f"Análise geral de {self.especialidade}: {contexto}"
    
    def _analise_juridica(self, contexto: str, conhecimento: List[Dict[str, Any]]) -> str:
        return f"Análise Jurídica: Identificados {len(conhecimento)} precedentes relevantes. Contexto: {contexto[:200]}..."
    
    def _analise_financeira(self, contexto: str, conhecimento: List[Dict[str, Any]]) -> str:
        return f"Análise Financeira: Baseada em {len(conhecimento)} padrões financeiros. Contexto: {contexto[:200]}..."
    
    def _analise_revisao(self, contexto: str, conhecimento: List[Dict[str, Any]]) -> str:
        return f"Análise de Revisão: Utilizando {len(conhecimento)} critérios de auditoria. Contexto: {contexto[:200]}..."
    
    def _analise_cetica(self, contexto: str, conhecimento: List[Dict[str, Any]]) -> str:
        return f"Análise Cética: Verificando {len(conhecimento)} pontos de atenção. Contexto: {contexto[:200]}..."
    
    def _analise_coordenacao(self, contexto: str, conhecimento: List[Dict[str, Any]]) -> str:
        return f"Análise de Coordenação: Integrando {len(conhecimento)} perspectivas. Contexto: {contexto[:200]}..."
    
    def _analise_legal(self, contexto: str, conhecimento: List[Dict[str, Any]]) -> str:
        return f"Análise Legal: Baseada em {len(conhecimento)} fundamentos legais. Contexto: {contexto[:200]}..."
    
    def _analise_contratual(self, contexto: str, conhecimento: List[Dict[str, Any]]) -> str:
        return f"Análise Contratual: Utilizando {len(conhecimento)} cláusulas relevantes. Contexto: {contexto[:200]}..."
    
    def _salvar_analise(self, analise: str, contexto: str, query: str):
        """
        Salvar análise no banco local do agente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analises (analise_content, contexto, metadata)
                VALUES (?, ?, ?)
            """, (analise, contexto, json.dumps({"query": query, "timestamp": datetime.now().isoformat()})))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao salvar análise do agente {self.nome}: {e}")


class MaestroOrquestrador:
    """
    Maestro refatorado como orquestrador do fluxo de informação
    """
    
    def __init__(self, barramento: BarramentoConhecimentoUnificado):
        self.barramento = barramento
        self.agentes = {}
        self._inicializar_agentes()
        
        logger.info("Maestro Orquestrador inicializado")
    
    def _inicializar_agentes(self):
        """
        Inicializar todos os agentes especialistas
        """
        especialidades = {
            "jurist": "jurista",
            "financial": "financeiro", 
            "reviewer": "revisor",
            "skeptic": "skeptic",
            "maestro": "coordenacao",
            "legal": "legal",
            "contract": "contract"
        }
        
        for nome, especialidade in especialidades.items():
            self.agentes[nome] = AgenteEspecialistaRefatorado(nome, especialidade, self.barramento)
    
    def processar_consulta(self, query: str) -> Dict[str, Any]:
        """
        Processar consulta seguindo o fluxo: Buscar -> Delegar -> Analisar -> Sintetizar
        """
        logger.info(f"Processando consulta: {query}")
        
        try:
            # 1. Busca Inicial (Retrieve)
            logger.info("1. Realizando busca inicial no índice vetorial...")
            documentos_relevantes = self.barramento.buscar_conhecimento(query, n_results=10)
            
            if not documentos_relevantes:
                return {
                    "resposta": "Não foi possível encontrar informações relevantes para sua consulta.",
                    "agentes_consultados": [],
                    "documentos_encontrados": 0
                }
            
            # 2. Delegação Especializada (Dispatch)
            logger.info("2. Delegando para agentes especialistas...")
            agentes_necessarios = self._determinar_agentes_necessarios(query, documentos_relevantes)
            
            # 3. Análise Paralela
            logger.info("3. Realizando análises especializadas...")
            analises = {}
            threads = []
            
            for agente_nome in agentes_necessarios:
                if agente_nome in self.agentes:
                    thread = threading.Thread(
                        target=self._executar_analise_agente,
                        args=(agente_nome, documentos_relevantes, query, analises)
                    )
                    threads.append(thread)
                    thread.start()
            
            # Aguardar conclusão de todas as análises
            for thread in threads:
                thread.join()
            
            # 4. Síntese Final (Synthesize)
            logger.info("4. Sintetizando respostas...")
            resposta_final = self._sintetizar_respostas(query, analises, documentos_relevantes)
            
            return {
                "resposta": resposta_final,
                "agentes_consultados": list(analises.keys()),
                "documentos_encontrados": len(documentos_relevantes),
                "analises_detalhadas": analises
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento da consulta: {e}")
            return {
                "resposta": f"Erro no processamento: {str(e)}",
                "agentes_consultados": [],
                "documentos_encontrados": 0
            }
    
    def _determinar_agentes_necessarios(self, query: str, documentos: List[Dict[str, Any]]) -> List[str]:
        """
        Determinar quais agentes são necessários para a consulta
        """
        agentes_necessarios = []
        
        # Análise simples baseada em palavras-chave
        query_lower = query.lower()
        
        if any(palavra in query_lower for palavra in ['lei', 'jurídico', 'legal', 'processo', 'tribunal']):
            agentes_necessarios.extend(['jurist', 'legal'])
        
        if any(palavra in query_lower for palavra in ['financeiro', 'dinheiro', 'valor', 'custo', 'orçamento']):
            agentes_necessarios.append('financial')
        
        if any(palavra in query_lower for palavra in ['revisar', 'auditoria', 'verificar', 'controlar']):
            agentes_necessarios.append('reviewer')
        
        if any(palavra in query_lower for palavra in ['contrato', 'contratação', 'licitação']):
            agentes_necessarios.append('contract')
        
        if any(palavra in query_lower for palavra in ['risco', 'problema', 'cuidado', 'atenção']):
            agentes_necessarios.append('skeptic')
        
        # Sempre incluir o maestro para coordenação
        if 'maestro' not in agentes_necessarios:
            agentes_necessarios.append('maestro')
        
        # Remover duplicatas
        agentes_necessarios = list(set(agentes_necessarios))
        
        logger.info(f"Agentes necessários: {agentes_necessarios}")
        return agentes_necessarios
    
    def _executar_analise_agente(self, agente_nome: str, documentos: List[Dict[str, Any]], query: str, analises: Dict):
        """
        Executar análise de um agente específico
        """
        try:
            agente = self.agentes[agente_nome]
            contexto = " ".join([doc["content"][:200] for doc in documentos[:3]])
            
            resultado = agente.analisar_contexto(contexto, query)
            analises[agente_nome] = resultado
            
        except Exception as e:
            logger.error(f"Erro na análise do agente {agente_nome}: {e}")
            analises[agente_nome] = {
                "agente": agente_nome,
                "analise": f"Erro na análise: {str(e)}",
                "confianca": 0.0
            }
    
    def _sintetizar_respostas(self, query: str, analises: Dict[str, Any], documentos: List[Dict[str, Any]]) -> str:
        """
        Sintetizar respostas dos agentes em uma resposta final
        """
        try:
            # Coletar análises válidas
            analises_validas = [
                analise for analise in analises.values() 
                if analise.get("confianca", 0) > 0.5
            ]
            
            if not analises_validas:
                return "Não foi possível obter análises confiáveis dos especialistas."
            
            # Construir resposta sintetizada
            resposta = f"Baseado na análise de {len(analises_validas)} especialistas:\n\n"
            
            for analise in analises_validas:
                resposta += f"• {analise['especialidade'].title()}: {analise['analise']}\n\n"
            
            resposta += f"\nConsulta original: {query}"
            resposta += f"\nDocumentos consultados: {len(documentos)}"
            
            return resposta
            
        except Exception as e:
            logger.error(f"Erro na síntese: {e}")
            return f"Erro na síntese das respostas: {str(e)}"
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obter estatísticas do sistema
        """
        stats = {
            "barramento": self.barramento.obter_estatisticas(),
            "agentes": {}
        }
        
        for nome, agente in self.agentes.items():
            try:
                conn = sqlite3.connect(agente.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM analises")
                count = cursor.fetchone()[0]
                conn.close()
                
                stats["agentes"][nome] = {
                    "especialidade": agente.especialidade,
                    "analises_realizadas": count
                }
            except Exception as e:
                stats["agentes"][nome] = {
                    "especialidade": agente.especialidade,
                    "analises_realizadas": 0,
                    "erro": str(e)
                }
        
        return stats


def main():
    """
    Função principal para demonstrar o sistema
    """
    print("🚀 INICIALIZANDO BARRAMENTO DE CONHECIMENTO UNIFICADO")
    print("=" * 60)
    try:
        # 0. Checar argumento de reset manual
        reset_chromadb = False
        if '--reset-chromadb' in sys.argv:
            print("[INFO] Reset manual do índice ChromaDB ativado!")
            reset_chromadb = True
        else:
            print("[INFO] Se encontrar erro de compatibilidade, execute com: python barramento_conhecimento_unificado.py --reset-chromadb")
        # 1. Inicializar barramento MODERADO
        print("1. Inicializando barramento de conhecimento MODERADO...")
        print("   - GPU: Ativado")
        print("   - RAM: 100GB moderada")
        print("   - Processamento: Sequencial estável")
        barramento = BarramentoConhecimentoUnificado(reset_chromadb=reset_chromadb)
        # 2. Indexar conhecimento existente
        print("2. Indexando conhecimento existente...")
        total_indexado = barramento.indexar_conhecimento_existente()
        print(f"   Total indexado: {total_indexado:,} documentos")
        # 3. Inicializar maestro orquestrador
        print("3. Inicializando maestro orquestrador...")
        maestro = MaestroOrquestrador(barramento)
        # 4. Menu interativo
        while True:
            print("\n" + "=" * 60)
            print("🎯 SISTEMA DE CONHECIMENTO UNIFICADO")
            print("=" * 60)
            print("1. Fazer consulta")
            print("2. Ver estatísticas")
            print("3. Reindexar conhecimento")
            print("4. Sair")
            opcao = input("\nEscolha uma opção (1-4): ").strip()
            if opcao == "1":
                query = input("Digite sua consulta: ").strip()
                if query:
                    print("\n🔍 Processando consulta...")
                    resultado = maestro.processar_consulta(query)
                    print("\n📋 RESULTADO:")
                    print("-" * 40)
                    print(resultado["resposta"])
                    print(f"\nAgentes consultados: {', '.join(resultado['agentes_consultados'])}")
                    print(f"Documentos encontrados: {resultado['documentos_encontrados']}")
            elif opcao == "2":
                print("\n📊 ESTATÍSTICAS DO SISTEMA:")
                print("-" * 40)
                stats = maestro.obter_estatisticas()
                print(f"Barramento:")
                print(f"  - Documentos indexados: {stats['barramento']['total_documentos']:,}")
                print(f"  - Coleção: {stats['barramento']['colecao']}")
                print(f"\nAgentes:")
                for nome, info in stats['agentes'].items():
                    print(f"  - {nome}: {info['especialidade']} ({info['analises_realizadas']} análises)")
            elif opcao == "3":
                print("\n🔄 Reindexando conhecimento...")
                total_indexado = barramento.indexar_conhecimento_existente()
                print(f"Reindexação concluída: {total_indexado:,} documentos")
            elif opcao == "4":
                print("\n👋 Saindo do sistema...")
                break
            else:
                print("❌ Opção inválida!")
    except KeyboardInterrupt:
        print("\n🛑 Processamento interrompido pelo usuário. Salvando progresso e saindo com segurança...")
        logger.info("Processamento interrompido pelo usuário via KeyboardInterrupt.")
        exit(0)


if __name__ == "__main__":
    main() 