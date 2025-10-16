#!/usr/bin/env python3
"""
🧠 SISTEMA DE MEMÓRIA PERSISTENTE - IA AUTOEVOLUTIVA
============================================================
Implementação do "Cérebro Persistente" para resolver o problema
da amnésia dos agentes e garantir herança de conhecimento
entre gerações e sessões.

INTEGRADO COM FAISS PARA MEMÓRIA VETORIAL PERSISTENTE
"""

import sqlite3
import json
import os
import yaml
import pickle
import hashlib
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil

# Integração com FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    print("⚠️ FAISS não disponível - usando apenas SQLite")
    FAISS_AVAILABLE = False

class AgentMemory:
    """
    Classe para gerenciar a memória persistente de cada agente.
    Implementa o conceito de "Cérebro Persistente" descrito no texto.
    INTEGRADO COM FAISS para memória vetorial.
    """
    
    def __init__(self, agent_id: str, memory_path: str = None, faiss_index: Any = None):
        """
        Inicializa a memória do agente.
        
        Args:
            agent_id: Identificador único do agente
            memory_path: Caminho para o arquivo de memória (opcional)
            faiss_index: Índice FAISS para memória vetorial (opcional)
        """
        self.agent_id = agent_id
        self.faiss_index = faiss_index
        
        # Criar diretório do agente se não existir
        if memory_path:
            self.agent_dir = Path(memory_path)
        else:
            self.agent_dir = Path(f"agents/{agent_id}")
        
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Caminhos dos arquivos de memória
        self.memory_db = self.agent_dir / "memory.db"
        self.genome_file = self.agent_dir / "genome.yaml"
        self.confidence_file = self.agent_dir / "confidence.json"
        self.experience_file = self.agent_dir / "experience.pkl"
        self.vectors_file = self.agent_dir / "vectors.faiss"
        
        # Inicializar banco de dados
        self._init_database()
        
        # Inicializar FAISS se disponível
        if FAISS_AVAILABLE and self.faiss_index is None:
            self._init_faiss_index()
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite para memória persistente"""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        # Tabela para fatos aprendidos (Conhecimento Adquirido)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_type TEXT NOT NULL,
                fact_content TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 1
            )
        ''')
        
        # Tabela para padrões reconhecidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para decisões tomadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_type TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL,
                success BOOLEAN,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def remember_fact(self, fact_type: str, fact_content: str, confidence: float = 1.0, source: str = None):
        """
        Salva um fato aprendido na memória persistente.
        
        Args:
            fact_type: Tipo do fato (ex: 'contract_rule', 'calculation_pattern')
            fact_content: Conteúdo do fato
            confidence: Confiança no fato (0.0 a 1.0)
            source: Fonte do fato
        """
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        # Verificar se o fato já existe
        cursor.execute('''
            SELECT id, usage_count FROM learned_facts 
            WHERE fact_type = ? AND fact_content = ?
        ''', (fact_type, fact_content))
        
        existing = cursor.fetchone()
        
        if existing:
            # Atualizar fato existente
            fact_id, usage_count = existing
            cursor.execute('''
                UPDATE learned_facts 
                SET confidence = ?, last_used = CURRENT_TIMESTAMP, usage_count = ?
                WHERE id = ?
            ''', (confidence, usage_count + 1, fact_id))
        else:
            # Inserir novo fato
            cursor.execute('''
                INSERT INTO learned_facts (fact_type, fact_content, confidence, source)
                VALUES (?, ?, ?, ?)
            ''', (fact_type, fact_content, confidence, source))
        
        conn.commit()
        conn.close()
    
    def recall_facts(self, fact_type: str = None, min_confidence: float = 0.5) -> List[Dict]:
        """
        Recupera fatos da memória.
        
        Args:
            fact_type: Tipo de fato a buscar (opcional)
            min_confidence: Confiança mínima para retornar
            
        Returns:
            Lista de fatos encontrados
        """
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        if fact_type:
            cursor.execute('''
                SELECT fact_type, fact_content, confidence, source, usage_count, last_used
                FROM learned_facts 
                WHERE fact_type = ? AND confidence >= ?
                ORDER BY usage_count DESC, last_used DESC
            ''', (fact_type, min_confidence))
        else:
            cursor.execute('''
                SELECT fact_type, fact_content, confidence, source, usage_count, last_used
                FROM learned_facts 
                WHERE confidence >= ?
                ORDER BY usage_count DESC, last_used DESC
            ''', (min_confidence,))
        
        facts = []
        for row in cursor.fetchall():
            facts.append({
                'type': row[0],
                'content': row[1],
                'confidence': row[2],
                'source': row[3],
                'usage_count': row[4],
                'last_used': row[5]
            })
        
        conn.close()
        return facts
    
    def save_confidence_matrix(self, confidence_data: Dict[str, float]):
        """
        Salva a matriz de confiança do agente (Conhecimento Ponderado).
        
        Args:
            confidence_data: Dicionário com valores de confiança
        """
        with open(self.confidence_file, 'w') as f:
            json.dump(confidence_data, f, indent=2)
    
    def load_confidence_matrix(self) -> Dict[str, float]:
        """
        Carrega a matriz de confiança do agente.
        
        Returns:
            Dicionário com valores de confiança
        """
        if self.confidence_file.exists():
            with open(self.confidence_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_experience(self, experience_data: Any):
        """
        Salva dados de experiência do agente.
        
        Args:
            experience_data: Dados de experiência (qualquer tipo serializável)
        """
        with open(self.experience_file, 'wb') as f:
            pickle.dump(experience_data, f)
    
    def load_experience(self) -> Any:
        """
        Carrega dados de experiência do agente.
        
        Returns:
            Dados de experiência carregados
        """
        if self.experience_file.exists():
            with open(self.experience_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def record_decision(self, decision_type: str, input_data: str, output_data: str, 
                       success: bool = None, feedback: str = None):
        """
        Registra uma decisão tomada pelo agente.
        
        Args:
            decision_type: Tipo da decisão
            input_data: Dados de entrada
            output_data: Dados de saída
            success: Se a decisão foi bem-sucedida
            feedback: Feedback sobre a decisão
        """
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO decisions (decision_type, input_data, output_data, success, feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (decision_type, input_data, output_data, success, feedback))
        
        conn.commit()
        conn.close()
    
    def get_decision_history(self, decision_type: str = None, limit: int = 100) -> List[Dict]:
        """
        Recupera histórico de decisões.
        
        Args:
            decision_type: Tipo de decisão a buscar (opcional)
            limit: Limite de registros
            
        Returns:
            Lista de decisões
        """
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        if decision_type:
            cursor.execute('''
                SELECT decision_type, input_data, output_data, success, feedback, created_at
                FROM decisions 
                WHERE decision_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (decision_type, limit))
        else:
            cursor.execute('''
                SELECT decision_type, input_data, output_data, success, feedback, created_at
                FROM decisions 
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        decisions = []
        for row in cursor.fetchall():
            decisions.append({
                'type': row[0],
                'input': row[1],
                'output': row[2],
                'success': row[3],
                'feedback': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return decisions
    
    def inherit_from_parent(self, parent_memory_path: str):
        """
        Herda memória de um agente pai (crucial para evolução).
        
        Args:
            parent_memory_path: Caminho para a memória do agente pai
        """
        parent_path = Path(parent_memory_path)
        
        if not parent_path.exists():
            print(f"⚠️ Caminho do pai não encontrado: {parent_memory_path}")
            return
        
        # Copiar banco de dados de memória
        parent_db = parent_path / "memory.db"
        if parent_db.exists():
            shutil.copy2(parent_db, self.memory_db)
            print(f"✅ Memória herdada de: {parent_memory_path}")
        
        # Copiar arquivo de confiança
        parent_confidence = parent_path / "confidence.json"
        if parent_confidence.exists():
            shutil.copy2(parent_confidence, self.confidence_file)
        
        # Copiar arquivo de experiência
        parent_experience = parent_path / "experience.pkl"
        if parent_experience.exists():
            shutil.copy2(parent_experience, self.experience_file)
    
    def _init_faiss_index(self):
        """Inicializa índice FAISS para memória vetorial do agente"""
        try:
            if os.path.exists(self.vectors_file):
                # Carregar índice existente
                self.faiss_index = faiss.read_index(str(self.vectors_file))
                print(f"✓ Índice FAISS carregado para agente {self.agent_id}")
            else:
                # Criar novo índice
                dimension = 768  # Dimensão padrão para embeddings
                self.faiss_index = faiss.IndexFlatL2(dimension)
                print(f"✓ Novo índice FAISS criado para agente {self.agent_id}")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar FAISS para agente {self.agent_id}: {e}")
            self.faiss_index = None
    
    def salvar_memoria_vetorial(self, vectors: np.ndarray, metadata: List[Dict]):
        """
        Salva memória vetorial no FAISS
        
        Args:
            vectors: Array numpy com vetores
            metadata: Lista de metadados para cada vetor
        """
        try:
            if FAISS_AVAILABLE and self.faiss_index is not None:
                # Adicionar vetores ao índice
                self.faiss_index.add(vectors)
                
                # Salvar metadados
                metadata_file = self.agent_dir / "vectors_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                # Salvar índice FAISS
                faiss.write_index(self.faiss_index, str(self.vectors_file))
                
                print(f"✓ {len(vectors)} vetores salvos na memória do agente {self.agent_id}")
                return True
            else:
                print("⚠️ FAISS não disponível para salvar vetores")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao salvar memória vetorial: {e}")
            return False
    
    def buscar_memoria_vetorial(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Busca na memória vetorial usando FAISS
        
        Args:
            query_vector: Vetor de consulta
            k: Número de resultados a retornar
            
        Returns:
            Lista de resultados com metadados
        """
        try:
            if FAISS_AVAILABLE and self.faiss_index is not None:
                # Buscar no FAISS
                distances, indices = self.faiss_index.search(query_vector.reshape(1, -1), k)
                
                # Carregar metadados
                metadata_file = self.agent_dir / "vectors_metadata.json"
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Retornar resultados com metadados
                    resultados = []
                    for i, idx in enumerate(indices[0]):
                        if idx < len(metadata):
                            resultados.append({
                                'metadata': metadata[idx],
                                'distance': float(distances[0][i]),
                                'index': int(idx)
                            })
                    
                    return resultados
                else:
                    return []
            else:
                print("⚠️ FAISS não disponível para busca vetorial")
                return []
                
        except Exception as e:
            print(f"❌ Erro ao buscar memória vetorial: {e}")
            return []
    
    def obter_estatisticas_memoria(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória do agente"""
        stats = {
            'agent_id': self.agent_id,
            'memoria_sqlite': self._get_sqlite_stats(),
            'memoria_faiss': self._get_faiss_stats(),
            'arquivos_memoria': self._get_file_stats()
        }
        return stats
    
    def _get_sqlite_stats(self) -> Dict[str, Any]:
        """Estatísticas do banco SQLite"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            
            # Contar registros em cada tabela
            cursor.execute("SELECT COUNT(*) FROM learned_facts")
            facts_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM patterns")
            patterns_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM decisions")
            decisions_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'learned_facts': facts_count,
                'patterns': patterns_count,
                'decisions': decisions_count,
                'total': facts_count + patterns_count + decisions_count
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_faiss_stats(self) -> Dict[str, Any]:
        """Estatísticas do FAISS"""
        if FAISS_AVAILABLE and self.faiss_index is not None:
            try:
                return {
                    'total_vectors': self.faiss_index.ntotal,
                    'dimension': self.faiss_index.d,
                    'index_type': type(self.faiss_index).__name__,
                    'available': True
                }
            except Exception as e:
                return {'error': str(e)}
        else:
            return {'available': False}
    
    def _get_file_stats(self) -> Dict[str, Any]:
        """Estatísticas dos arquivos de memória"""
        stats = {}
        files = [
            ('genome', self.genome_file),
            ('confidence', self.confidence_file),
            ('experience', self.experience_file),
            ('vectors', self.vectors_file)
        ]
        
        for name, file_path in files:
            if os.path.exists(file_path):
                stats[name] = {
                    'exists': True,
                    'size_bytes': os.path.getsize(file_path)
                }
            else:
                stats[name] = {'exists': False}
        
        return stats

class GenomeCompiler:
    """
    Compilador de genoma que integra com o sistema de memória persistente.
    """
    
    def __init__(self):
        self.agents_dir = Path("agents")
        self.agents_dir.mkdir(exist_ok=True)
    
    def create_agent(self, agent_id: str, genome_data: Dict[str, Any]) -> AgentMemory:
        """
        Cria um novo agente com genoma e memória persistente.
        
        Args:
            agent_id: ID do agente
            genome_data: Dados do genoma
            
        Returns:
            Instância da memória do agente
        """
        # Criar memória do agente
        memory = AgentMemory(agent_id)
        
        # Salvar genoma
        with open(memory.genome_file, 'w') as f:
            yaml.dump(genome_data, f, default_flow_style=False)
        
        print(f"✅ Agente criado: {agent_id}")
        return memory
    
    def load_agent(self, agent_id: str) -> Optional[AgentMemory]:
        """
        Carrega um agente existente.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Instância da memória do agente ou None
        """
        agent_path = self.agents_dir / agent_id
        
        if agent_path.exists():
            return AgentMemory(agent_id, str(agent_path))
        else:
            print(f"⚠️ Agente não encontrado: {agent_id}")
            return None
    
    def reproduce_agent(self, parent_id: str, child_id: str, 
                       genome_mutations: Dict[str, Any] = None) -> AgentMemory:
        """
        Cria um agente filho herdando genoma e memória do pai.
        
        Args:
            parent_id: ID do agente pai
            child_id: ID do agente filho
            genome_mutations: Mutações a aplicar no genoma
            
        Returns:
            Instância da memória do agente filho
        """
        # Carregar agente pai
        parent_memory = self.load_agent(parent_id)
        if not parent_memory:
            raise ValueError(f"Agente pai não encontrado: {parent_id}")
        
        # Carregar genoma do pai
        with open(parent_memory.genome_file, 'r') as f:
            parent_genome = yaml.safe_load(f)
        
        # Aplicar mutações
        child_genome = parent_genome.copy()
        if genome_mutations:
            child_genome.update(genome_mutations)
        
        # Criar agente filho
        child_memory = self.create_agent(child_id, child_genome)
        
        # Herdar memória do pai
        child_memory.inherit_from_parent(str(parent_memory.agent_dir))
        
        print(f"✅ Agente filho criado: {child_id} (herdou de {parent_id})")
        return child_memory

def main():
    """Função de teste do sistema de memória persistente"""
    print("🧠 TESTE DO SISTEMA DE MEMÓRIA PERSISTENTE")
    print("=" * 50)
    
    # Criar compilador
    compiler = GenomeCompiler()
    
    # Criar agente pai
    parent_genome = {
        'agent_type': 'jurista',
        'version': '1.0.0',
        'capabilities': ['contract_analysis', 'legal_reasoning'],
        'ethical_guardrails': ['always_verify_sources', 'require_human_review'],
        'resource_limits': {'max_analysis_time': 300, 'max_memory_mb': 512}
    }
    
    parent_memory = compiler.create_agent("jurista_pai", parent_genome)
    
    # Adicionar conhecimento ao pai
    parent_memory.remember_fact(
        fact_type="contract_rule",
        fact_content="Cláusulas de força maior sempre anulam obrigações de prazo",
        confidence=0.95,
        source="manual_petrobras_v2.1"
    )
    
    parent_memory.remember_fact(
        fact_type="calculation_pattern",
        fact_content="Para aderência: (valor_atual / valor_original) * 100",
        confidence=0.98,
        source="procedimento_financeiro"
    )
    
    # Salvar matriz de confiança
    confidence_matrix = {
        'financial_agent': 0.85,
        'legal_agent': 0.92,
        'audit_agent': 0.78
    }
    parent_memory.save_confidence_matrix(confidence_matrix)
    
    # Registrar decisão
    parent_memory.record_decision(
        decision_type="contract_approval",
        input_data="Contrato de R$ 500.000 para serviços de manutenção",
        output_data="APROVADO - Dentro dos limites de competência",
        success=True,
        feedback="Decisão correta conforme procedimentos"
    )
    
    # Criar agente filho
    mutations = {
        'version': '1.1.0',
        'capabilities': ['contract_analysis', 'legal_reasoning', 'risk_assessment']
    }
    
    child_memory = compiler.reproduce_agent("jurista_pai", "jurista_filho", mutations)
    
    # Verificar herança
    print("\n📊 VERIFICANDO HERANÇA DE CONHECIMENTO:")
    
    # Fatos herdados
    inherited_facts = child_memory.recall_facts()
    print(f"✅ Fatos herdados: {len(inherited_facts)}")
    
    # Matriz de confiança herdada
    inherited_confidence = child_memory.load_confidence_matrix()
    print(f"✅ Matriz de confiança herdada: {inherited_confidence}")
    
    # Histórico de decisões herdado
    inherited_decisions = child_memory.get_decision_history()
    print(f"✅ Decisões herdadas: {len(inherited_decisions)}")
    
    # Estatísticas
    parent_stats = parent_memory.obter_estatisticas_memoria()
    child_stats = child_memory.obter_estatisticas_memoria()
    
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"Pai - Fatos: {parent_stats['memoria_sqlite']['learned_facts']}, Decisões: {parent_stats['memoria_sqlite']['decisions']}")
    print(f"Filho - Fatos: {child_stats['memoria_sqlite']['learned_facts']}, Decisões: {child_stats['memoria_sqlite']['decisions']}")
    
    print("\n🎉 SISTEMA DE MEMÓRIA PERSISTENTE FUNCIONANDO!")
    print("✅ Conhecimento sendo herdado corretamente entre gerações")

if __name__ == "__main__":
    main() 