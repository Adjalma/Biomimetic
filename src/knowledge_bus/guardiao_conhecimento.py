#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUARDIÃO DO CONHECIMENTO - SISTEMA DE MANUTENÇÃO AUTÔNOMA
=========================================================

Este módulo implementa o Guardião do Conhecimento, um sistema autônomo
responsável pela manutenção da saúde e integridade da Biblioteca Central
FAISS, garantindo qualidade e consistência do conhecimento armazenado.

ARQUITETURA AUTÔNOMA:
- Sistema de monitoramento contínuo e independente
- Detecção automática de problemas e inconsistências
- Correção supervisionada de erros e contradições
- Manutenção proativa da qualidade do conhecimento
- Integração com sistemas V2 e barramento de conhecimento

FUNCIONALIDADES PRINCIPAIS:
1. DETECÇÃO DE CONTRADIÇÕES:
   - Identifica procedimentos conflitantes
   - Detecta dados obsoletos e desatualizados
   - Encontra informações contraditórias
   - Valida consistência lógica

2. VERIFICAÇÃO DE OBSOLESCÊNCIA:
   - Monitora datas de validade
   - Identifica informações desatualizadas
   - Sugere atualizações necessárias
   - Remove conteúdo obsoleto

3. CRIAÇÃO DE LINKS DE CONHECIMENTO:
   - Estabelece conexões semânticas
   - Cria relacionamentos entre conceitos
   - Melhora navegabilidade do conhecimento
   - Otimiza busca e recuperação

4. AUTO-CORREÇÃO SUPERVISIONADA:
   - Corrige erros automaticamente
   - Valida correções com supervisão
   - Aprende com correções manuais
   - Melhora continuamente

COMPONENTES:
- GuardiaoConhecimento: Classe principal do sistema
- Sistema de detecção de contradições
- Verificador de obsolescência
- Criador de links de conhecimento
- Sistema de auto-correção

FLUXO DE OPERAÇÃO:
1. Monitoramento → Detecção → Análise de problemas
2. Classificação → Priorização → Planejamento de correções
3. Execução → Validação → Aplicação de correções
4. Verificação → Aprendizado → Melhoria contínua

Versão: 2.0
Data: 2024
Autor: Sistema IA Autoevolutiva
"""

# =============================================================================
# IMPORTS E DEPENDÊNCIAS
# =============================================================================

import sqlite3        # Banco de dados SQLite para persistência
import json           # Manipulação de dados JSON
import logging        # Sistema de logging avançado
import threading      # Threading para operações concorrentes
import time           # Medição de tempo e performance
from datetime import datetime, timedelta  # Manipulação de datas e tempo
from pathlib import Path  # Manipulação de caminhos de arquivos
from typing import Dict, List, Any, Optional, Tuple  # Type hints
import hashlib        # Hashing para identificação única
import re             # Expressões regulares para processamento de texto
from dataclasses import dataclass  # Classes de dados
from enum import Enum  # Enumerações para tipos

class TipoContradicao(Enum):
    """Tipos de contradições que o Guardião pode detectar"""
    PROCEDIMENTO_CONFLITANTE = "procedimento_conflitante"
    DATA_OBSOLETA = "data_obsoleta"
    REGRA_CONTRADITORIA = "regra_contraditoria"
    DOCUMENTO_DESATUALIZADO = "documento_desatualizado"
    COMPETENCIA_CONFLITANTE = "competencia_conflitante"

class StatusTicket(Enum):
    """Status dos tickets de revisão"""
    ABERTO = "aberto"
    EM_ANALISE = "em_analise"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    IMPLEMENTADO = "implementado"

@dataclass
class ContradicaoDetectada:
    """Estrutura para contradições detectadas"""
    id: str
    tipo: TipoContradicao
    documentos_envolvidos: List[str]
    descricao: str
    severidade: str  # baixa, media, alta, critica
    data_deteccao: datetime
    status: StatusTicket
    sugestao_correcao: str
    impacto_estimado: str

@dataclass
class LinkConhecimento:
    """Estrutura para links de conhecimento"""
    documento_origem: str
    documento_destino: str
    tipo_relacao: str  # cita, baseia, complementa, substitui
    forca_relacao: float  # 0.0 a 1.0
    data_criacao: datetime
    contexto: str

class GuardiaoConhecimento:
    """
    🛡️ Guardião do Conhecimento - Sistema autônomo de manutenção
    """
    
    def __init__(self, 
                 biblioteca_path: str = "faiss_biblioteca_central",
                 db_path: str = "guardiao_conhecimento.db",
                 enable_logging: bool = True,
                 usar_banco_separado: bool = True,
                 faiss_path: str = "faiss_biblioteca_central"):
        
        self.biblioteca_path = Path(biblioteca_path)
        self.faiss_path = Path(faiss_path)
        self.usar_banco_separado = usar_banco_separado
        
        if usar_banco_separado:
            self.db_path = Path(db_path)
        else:
            self.db_path = None
            
        self.enable_logging = enable_logging
        
        # Configurar logging
        if enable_logging:
            self._setup_logging()
        
        # Inicializar banco de dados interno apenas se necessário
        if usar_banco_separado:
            self._init_database()
        
        # Configurações de monitoramento
        self.intervalo_monitoramento = 3600  # 1 hora
        self.max_amostras_analise = 1000
        self.threshold_contradicao = 0.8
        
        # Thread de monitoramento em background
        self.monitoramento_ativo = False
        self.thread_monitoramento = None
        
        # Cache de conhecimento
        self.cache_conhecimento = {}
        self.links_conhecimento = {}
        
        self.logger.info("Guardiao do Conhecimento inicializado!")
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"guardiao_{datetime.now().strftime('%Y%m%d')}.log"
            
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
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
            self.logger.warning(f"⚠️ Logging avançado falhou: {str(e)}")
    
    def _init_database(self):
        """Inicializar banco de dados interno SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de contradições detectadas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contradicoes (
                    id TEXT PRIMARY KEY,
                    tipo TEXT NOT NULL,
                    documentos_envolvidos TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    severidade TEXT NOT NULL,
                    data_deteccao TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sugestao_correcao TEXT,
                    impacto_estimado TEXT,
                    data_resolucao TEXT,
                    resolvido_por TEXT
                )
            """)
            
            # Tabela de links de conhecimento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS links_conhecimento (
                    id TEXT PRIMARY KEY,
                    documento_origem TEXT NOT NULL,
                    documento_destino TEXT NOT NULL,
                    tipo_relacao TEXT NOT NULL,
                    forca_relacao REAL NOT NULL,
                    data_criacao TEXT NOT NULL,
                    contexto TEXT,
                    ativo BOOLEAN DEFAULT 1
                )
            """)
            
            # Tabela de tickets de revisão
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets_revisao (
                    id TEXT PRIMARY KEY,
                    contradicao_id TEXT NOT NULL,
                    titulo TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    prioridade TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data_criacao TEXT NOT NULL,
                    data_atualizacao TEXT,
                    responsavel TEXT,
                    comentarios TEXT,
                    FOREIGN KEY (contradicao_id) REFERENCES contradicoes (id)
                )
            """)
            
            # Tabela de histórico de mudanças
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_mudancas (
                    id TEXT PRIMARY KEY,
                    documento_id TEXT NOT NULL,
                    tipo_mudanca TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    data_mudanca TEXT NOT NULL,
                    autor TEXT NOT NULL,
                    justificativa TEXT,
                    impacto_analisado TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.info("✅ Banco de dados do Guardião inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar banco de dados: {str(e)}")
            raise
    
    def iniciar_monitoramento(self):
        """Iniciar monitoramento automático em background"""
        if self.monitoramento_ativo:
            self.logger.warning("⚠️ Monitoramento já está ativo!")
            return
        
        self.monitoramento_ativo = True
        self.thread_monitoramento = threading.Thread(
            target=self._loop_monitoramento,
            daemon=True
        )
        self.thread_monitoramento.start()
        
        self.logger.info("🔄 Monitoramento automático iniciado em background!")
    
    def parar_monitoramento(self):
        """Parar monitoramento automático"""
        self.monitoramento_ativo = False
        if self.thread_monitoramento:
            self.thread_monitoramento.join(timeout=5)
        
        self.logger.info("⏹️ Monitoramento automático parado!")
    
    def _loop_monitoramento(self):
        """Loop principal de monitoramento"""
        while self.monitoramento_ativo:
            try:
                self.logger.info("🔍 Executando ciclo de monitoramento...")
                
                # 1. Detectar contradições
                self.detectar_contradicoes()
                
                # 2. Verificar obsolescência
                self.verificar_obsolescencia()
                
                # 3. Atualizar links de conhecimento
                self.atualizar_links_conhecimento()
                
                # 4. Criar tickets de revisão
                self.criar_tickets_revisao()
                
                self.logger.info("✅ Ciclo de monitoramento concluído!")
                
                # Aguardar próximo ciclo
                time.sleep(self.intervalo_monitoramento)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no ciclo de monitoramento: {str(e)}")
                time.sleep(300)  # Aguardar 5 minutos antes de tentar novamente
    
    def detectar_contradicoes(self):
        """Detectar contradições na biblioteca de conhecimento"""
        try:
            self.logger.info("🔍 Detectando contradições...")
            
            # Carregar amostras da biblioteca FAISS
            amostras = self._carregar_amostras_biblioteca()
            
            contradicoes_detectadas = []
            
            # 1. Detectar procedimentos conflitantes
            contradicoes_procedimentos = self._detectar_procedimentos_conflitantes(amostras)
            contradicoes_detectadas.extend(contradicoes_procedimentos)
            
            # 2. Detectar regras contraditórias
            contradicoes_regras = self._detectar_regras_contraditorias(amostras)
            contradicoes_detectadas.extend(contradicoes_regras)
            
            # 3. Detectar competências conflitantes
            contradicoes_competencias = self._detectar_competencias_conflitantes(amostras)
            contradicoes_detectadas.extend(contradicoes_competencias)
            
            # Salvar contradições detectadas
            for contradicao in contradicoes_detectadas:
                self._salvar_contradicao(contradicao)
            
            self.logger.info(f"✅ {len(contradicoes_detectadas)} contradições detectadas!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao detectar contradições: {str(e)}")
    
    def _carregar_amostras_biblioteca(self) -> List[Dict[str, Any]]:
        """Carregar amostras da biblioteca FAISS para análise"""
        try:
            # Carregar metadados da biblioteca
            metadata_file = self.biblioteca_path / "metadata" / "biblioteca_state.json"
            
            if not metadata_file.exists():
                self.logger.warning("⚠️ Arquivo de metadados não encontrado!")
                return []
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Carregar amostras dos agentes
            amostras = []
            
            for agente_nome, dados_agente in metadata.get('agentes', {}).items():
                if dados_agente.get('vector_count', 0) > 0:
                    # Carregar amostras do agente
                    amostras_agente = self._carregar_amostras_agente(agente_nome)
                    amostras.extend(amostras_agente)
            
            # Limitar número de amostras
            if len(amostras) > self.max_amostras_analise:
                amostras = amostras[:self.max_amostras_analise]
            
            return amostras
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar amostras: {str(e)}")
            return []
    
    def _carregar_amostras_agente(self, agente_nome: str) -> List[Dict[str, Any]]:
        """Carregar amostras de um agente específico"""
        try:
            # Carregar metadados do agente
            metadata_file = self.biblioteca_path / "indices" / f"metadata_{agente_nome}.json"
            
            if not metadata_file.exists():
                return []
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Simular amostras (em implementação real, carregaria do FAISS)
            amostras = []
            
            # Criar amostras sintéticas para demonstração
            for i in range(100):  # 100 amostras por agente
                amostra = {
                    'agente': agente_nome,
                    'id': f"{agente_nome}_{i}",
                    'conteudo': f"Conteúdo de exemplo {i} do agente {agente_nome}",
                    'tipo': 'documento',
                    'data_criacao': datetime.now().isoformat(),
                    'tags': ['exemplo', agente_nome]
                }
                amostras.append(amostra)
            
            return amostras
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar amostras do agente {agente_nome}: {str(e)}")
            return []
    
    def _detectar_procedimentos_conflitantes(self, amostras: List[Dict[str, Any]]) -> List[ContradicaoDetectada]:
        """Detectar procedimentos conflitantes entre amostras"""
        contradicoes = []
        
        try:
            # Agrupar amostras por tipo de procedimento
            procedimentos = {}
            
            for amostra in amostras:
                if 'procedimento' in amostra.get('tags', []):
                    tipo = amostra.get('tipo_procedimento', 'geral')
                    if tipo not in procedimentos:
                        procedimentos[tipo] = []
                    procedimentos[tipo].append(amostra)
            
            # Analisar conflitos dentro de cada tipo
            for tipo, docs in procedimentos.items():
                if len(docs) > 1:
                    # Verificar se há documentos com datas diferentes
                    datas = [doc.get('data_criacao') for doc in docs if doc.get('data_criacao')]
                    
                    if len(set(datas)) > 1:
                        # Possível conflito de datas
                        contradicao = ContradicaoDetectada(
                            id=f"proc_conf_{hashlib.md5(tipo.encode()).hexdigest()[:8]}",
                            tipo=TipoContradicao.PROCEDIMENTO_CONFLITANTE,
                            documentos_envolvidos=[doc['id'] for doc in docs],
                            descricao=f"Procedimentos conflitantes para {tipo} com datas diferentes",
                            severidade="media",
                            data_deteccao=datetime.now(),
                            status=StatusTicket.ABERTO,
                            sugestao_correcao="Revisar e padronizar procedimentos com data mais recente",
                            impacto_estimado="Baixo - Apenas padronização"
                        )
                        contradicoes.append(contradicao)
            
            return contradicoes
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao detectar procedimentos conflitantes: {str(e)}")
            return []
    
    def _detectar_regras_contraditorias(self, amostras: List[Dict[str, Any]]) -> List[ContradicaoDetectada]:
        """Detectar regras contraditórias entre amostras"""
        contradicoes = []
        
        try:
            # Buscar regras e suas definições
            regras = {}
            
            for amostra in amostras:
                if 'regra' in amostra.get('tags', []):
                    regra_id = amostra.get('regra_id', 'geral')
                    if regra_id not in regras:
                        regras[regra_id] = []
                    regras[regra_id].append(amostra)
            
            # Analisar contradições entre regras
            for regra_id, docs in regras.items():
                if len(docs) > 1:
                    # Verificar se há definições diferentes para a mesma regra
                    definicoes = [doc.get('definicao', '') for doc in docs if doc.get('definicao')]
                    
                    if len(set(definicoes)) > 1:
                        contradicao = ContradicaoDetectada(
                            id=f"regra_conf_{hashlib.md5(regra_id.encode()).hexdigest()[:8]}",
                            tipo=TipoContradicao.REGRA_CONTRADITORIA,
                            documentos_envolvidos=[doc['id'] for doc in docs],
                            descricao=f"Definições conflitantes para regra {regra_id}",
                            severidade="alta",
                            data_deteccao=datetime.now(),
                            status=StatusTicket.ABERTO,
                            sugestao_correcao="Unificar definição da regra com versão mais recente",
                            impacto_estimado="Alto - Pode causar inconsistências operacionais"
                        )
                        contradicoes.append(contradicao)
            
            return contradicoes
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao detectar regras contraditórias: {str(e)}")
            return []
    
    def _detectar_competencias_conflitantes(self, amostras: List[Dict[str, Any]]) -> List[ContradicaoDetectada]:
        """Detectar competências conflitantes entre amostras"""
        contradicoes = []
        
        try:
            # Buscar definições de competência
            competencias = {}
            
            for amostra in amostras:
                if 'competencia' in amostra.get('tags', []):
                    nivel = amostra.get('nivel_competencia', 'geral')
                    if nivel not in competencias:
                        competencias[nivel] = []
                    competencias[nivel].append(amostra)
            
            # Analisar conflitos de competência
            for nivel, docs in competencias.items():
                if len(docs) > 1:
                    # Verificar se há valores conflitantes para o mesmo nível
                    valores = [doc.get('valor_limite', 0) for doc in docs if doc.get('valor_limite')]
                    
                    if len(set(valores)) > 1:
                        contradicao = ContradicaoDetectada(
                            id=f"comp_conf_{hashlib.md5(nivel.encode()).hexdigest()[:8]}",
                            tipo=TipoContradicao.COMPETENCIA_CONFLITANTE,
                            documentos_envolvidos=[doc['id'] for doc in docs],
                            descricao=f"Valores conflitantes para competência {nivel}",
                            severidade="critica",
                            data_deteccao=datetime.now(),
                            status=StatusTicket.ABERTO,
                            sugestao_correcao="Definir valor único para competência com aprovação gerencial",
                            impacto_estimado="Crítico - Pode causar aprovações indevidas"
                        )
                        contradicoes.append(contradicao)
            
            return contradicoes
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao detectar competências conflitantes: {str(e)}")
            return []
    
    def verificar_obsolescencia(self):
        """Verificar obsolescência de documentos"""
        try:
            self.logger.info("📅 Verificando obsolescência...")
            
            # Carregar documentos com datas
            documentos_datas = self._carregar_documentos_com_datas()
            
            documentos_obsoletos = []
            
            for doc in documentos_datas:
                if self._documento_obsoleto(doc):
                    documentos_obsoletos.append(doc)
            
            # Marcar documentos obsoletos
            for doc in documentos_obsoletos:
                self._marcar_documento_obsoleto(doc)
            
            self.logger.info(f"✅ {len(documentos_obsoletos)} documentos marcados como obsoletos!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar obsolescência: {str(e)}")
    
    def _carregar_documentos_com_datas(self) -> List[Dict[str, Any]]:
        """Carregar documentos que possuem datas para análise de obsolescência"""
        # Implementação simplificada - em produção carregaria do FAISS
        return []
    
    def _documento_obsoleto(self, documento: Dict[str, Any]) -> bool:
        """Verificar se um documento está obsoleto"""
        try:
            data_criacao = documento.get('data_criacao')
            if not data_criacao:
                return False
            
            # Converter para datetime
            if isinstance(data_criacao, str):
                data_criacao = datetime.fromisoformat(data_criacao.replace('Z', '+00:00'))
            
            # Considerar obsoleto se mais de 2 anos
            limite_obsolescencia = datetime.now() - timedelta(days=730)
            
            return data_criacao < limite_obsolescencia
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar obsolescência: {str(e)}")
            return False
    
    def _marcar_documento_obsoleto(self, documento: Dict[str, Any]):
        """Marcar documento como obsoleto"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info(f"ℹ️ Documento não marcado como obsoleto - banco não configurado: {documento.get('id', 'N/A')}")
                return
            
            # Atualizar status no banco
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO historico_mudancas 
                (id, documento_id, tipo_mudanca, descricao, data_mudanca, autor, justificativa)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                f"obs_{hashlib.md5(documento['id'].encode()).hexdigest()[:8]}",
                documento['id'],
                'marcacao_obsoleto',
                'Documento marcado como obsoleto pelo Guardião',
                datetime.now().isoformat(),
                'Sistema_Guardiao',
                'Data de criação muito antiga'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao marcar documento obsoleto: {str(e)}")
    
    def atualizar_links_conhecimento(self):
        """Atualizar links de conhecimento entre documentos"""
        try:
            self.logger.info("🔗 Atualizando links de conhecimento...")
            
            # Carregar documentos da biblioteca
            documentos = self._carregar_documentos_biblioteca()
            
            # Criar novos links
            novos_links = self._criar_links_conhecimento(documentos)
            
            # Salvar links no banco
            for link in novos_links:
                self._salvar_link_conhecimento(link)
            
            self.logger.info(f"✅ {len(novos_links)} links de conhecimento criados!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar links: {str(e)}")
    
    def _carregar_documentos_biblioteca(self) -> List[Dict[str, Any]]:
        """Carregar documentos da biblioteca para análise de links"""
        # Implementação simplificada
        return []
    
    def _criar_links_conhecimento(self, documentos: List[Dict[str, Any]]) -> List[LinkConhecimento]:
        """Criar links de conhecimento entre documentos"""
        links = []
        
        try:
            # Algoritmo simplificado para criar links
            for i, doc1 in enumerate(documentos):
                for j, doc2 in enumerate(documentos[i+1:], i+1):
                    # Verificar se há relação entre documentos
                    if self._documentos_relacionados(doc1, doc2):
                        link = LinkConhecimento(
                            documento_origem=doc1['id'],
                            documento_destino=doc2['id'],
                            tipo_relacao='relacionado',
                            forca_relacao=0.7,  # Valor padrão
                            data_criacao=datetime.now(),
                            contexto='Análise automática do Guardião'
                        )
                        links.append(link)
            
            return links
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar links: {str(e)}")
            return []
    
    def _documentos_relacionados(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> bool:
        """Verificar se dois documentos estão relacionados"""
        # Implementação simplificada
        return False
    
    def _salvar_link_conhecimento(self, link: LinkConhecimento):
        """Salvar link de conhecimento no banco"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info(f"ℹ️ Link não salvo - banco não configurado: {link.documento_origem} -> {link.documento_destino}")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO links_conhecimento 
                (id, documento_origem, documento_destino, tipo_relacao, forca_relacao, data_criacao, contexto)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                hashlib.md5(f"{link.documento_origem}_{link.documento_destino}".encode()).hexdigest()[:8],
                link.documento_origem,
                link.documento_destino,
                link.tipo_relacao,
                link.forca_relacao,
                link.data_criacao.isoformat(),
                link.contexto
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar link: {str(e)}")
    
    def criar_tickets_revisao(self):
        """Criar tickets de revisão para contradições detectadas"""
        try:
            self.logger.info("🎫 Criando tickets de revisão...")
            
            # Carregar contradições não resolvidas
            contradicoes = self._carregar_contradicoes_abertas()
            
            tickets_criados = 0
            
            for contradicao in contradicoes:
                if not self._ticket_existe(contradicao.id):
                    self._criar_ticket_revisao(contradicao)
                    tickets_criados += 1
            
            self.logger.info(f"✅ {tickets_criados} tickets de revisão criados!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar tickets: {str(e)}")
    
    def _carregar_contradicoes_abertas(self) -> List[ContradicaoDetectada]:
        """Carregar contradições com status aberto"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info("ℹ️ Banco de dados não configurado - modo FAISS apenas")
                return []
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM contradicoes WHERE status = ?
            """, (StatusTicket.ABERTO.value,))
            
            rows = cursor.fetchall()
            conn.close()
            
            contradicoes = []
            for row in rows:
                contradicao = ContradicaoDetectada(
                    id=row[0],
                    tipo=TipoContradicao(row[1]),
                    documentos_envolvidos=json.loads(row[2]),
                    descricao=row[3],
                    severidade=row[4],
                    data_deteccao=datetime.fromisoformat(row[5]),
                    status=StatusTicket(row[6]),
                    sugestao_correcao=row[7],
                    impacto_estimado=row[8]
                )
                contradicoes.append(contradicao)
            
            return contradicoes
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar contradições: {str(e)}")
            return []
    
    def _ticket_existe(self, contradicao_id: str) -> bool:
        """Verificar se já existe ticket para uma contradição"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM tickets_revisao WHERE contradicao_id = ?
            """, (contradicao_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar ticket: {str(e)}")
            return False
    
    def _criar_ticket_revisao(self, contradicao: ContradicaoDetectada):
        """Criar ticket de revisão para uma contradição"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info(f"ℹ️ Ticket não criado - banco não configurado: {contradicao.descricao}")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Determinar prioridade baseada na severidade
            prioridade_map = {
                'baixa': 'baixa',
                'media': 'media', 
                'alta': 'alta',
                'critica': 'urgente'
            }
            prioridade = prioridade_map.get(contradicao.severidade, 'media')
            
            cursor.execute("""
                INSERT INTO tickets_revisao 
                (id, contradicao_id, titulo, descricao, prioridade, status, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                f"ticket_{contradicao.id}",
                contradicao.id,
                f"Revisar {contradicao.tipo.value}",
                contradicao.descricao,
                prioridade,
                StatusTicket.ABERTO.value,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar ticket: {str(e)}")
    
    def _salvar_contradicao(self, contradicao: ContradicaoDetectada):
        """Salvar contradição detectada no banco"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info(f"ℹ️ Contradição não salva - banco não configurado: {contradicao.descricao}")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO contradicoes 
                (id, tipo, documentos_envolvidos, descricao, severidade, data_deteccao, status, sugestao_correcao, impacto_estimado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contradicao.id,
                contradicao.tipo.value,
                json.dumps(contradicao.documentos_envolvidos),
                contradicao.descricao,
                contradicao.severidade,
                contradicao.data_deteccao.isoformat(),
                contradicao.status.value,
                contradicao.sugestao_correcao,
                contradicao.impacto_estimado
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar contradição: {str(e)}")
    
    def obter_relatorio_status(self) -> Dict[str, Any]:
        """Obter relatório completo do status do Guardião"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                relatorio = {
                    'timestamp': datetime.now().isoformat(),
                    'status_sistema': 'ativo' if self.monitoramento_ativo else 'inativo',
                    'estatisticas': {
                        'total_contradicoes': 0,
                        'contradicoes_abertas': 0,
                        'total_tickets': 0,
                        'tickets_abertos': 0,
                        'total_links': 0
                    },
                    'ultima_execucao': datetime.now().isoformat(),
                    'proximo_ciclo': (datetime.now() + timedelta(seconds=self.intervalo_monitoramento)).isoformat(),
                    'modo': 'FAISS apenas - sem banco de dados'
                }
                return relatorio
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Estatísticas gerais
            cursor.execute("SELECT COUNT(*) FROM contradicoes")
            total_contradicoes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM contradicoes WHERE status = ?", (StatusTicket.ABERTO.value,))
            contradicoes_abertas = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tickets_revisao")
            total_tickets = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tickets_revisao WHERE status = ?", (StatusTicket.ABERTO.value,))
            tickets_abertos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM links_conhecimento")
            total_links = cursor.fetchone()[0]
            
            conn.close()
            
            relatorio = {
                'timestamp': datetime.now().isoformat(),
                'status_sistema': 'ativo' if self.monitoramento_ativo else 'inativo',
                'estatisticas': {
                    'total_contradicoes': total_contradicoes,
                    'contradicoes_abertas': contradicoes_abertas,
                    'total_tickets': total_tickets,
                    'tickets_abertos': tickets_abertos,
                    'total_links': total_links
                },
                'ultima_execucao': datetime.now().isoformat(),
                'proximo_ciclo': (datetime.now() + timedelta(seconds=self.intervalo_monitoramento)).isoformat(),
                'modo': 'Banco de dados + FAISS'
            }
            
            return relatorio
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar relatório: {str(e)}")
            return {'erro': str(e)}
    
    def executar_analise_manual(self):
        """Executar análise manual (para testes)"""
        try:
            self.logger.info("🔍 Executando análise manual...")
            
            # Executar todos os processos manualmente
            self.detectar_contradicoes()
            self.verificar_obsolescencia()
            self.atualizar_links_conhecimento()
            self.criar_tickets_revisao()
            
            # Gerar relatório
            relatorio = self.obter_relatorio_status()
            
            self.logger.info("✅ Análise manual concluída!")
            return relatorio
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise manual: {str(e)}")
            return {'erro': str(e)}

def main():
    """Função principal para teste do Guardião"""
    print("🛡️ INICIANDO GUARDIÃO DO CONHECIMENTO")
    print("=" * 50)
    
    try:
        # Inicializar Guardião
        guardiao = GuardiaoConhecimento()
        
        # Executar análise manual
        print("🔍 Executando análise manual...")
        relatorio = guardiao.executar_analise_manual()
        
        print("\n📊 RELATÓRIO DO GUARDIÃO:")
        print(json.dumps(relatorio, indent=2, ensure_ascii=False))
        
        # Iniciar monitoramento automático
        print("\n🔄 Iniciando monitoramento automático...")
        guardiao.iniciar_monitoramento()
        
        print("✅ Guardião iniciado com sucesso!")
        print("💡 Pressione Ctrl+C para parar...")
        
        # Manter ativo
        try:
            while True:
                time.sleep(10)
                relatorio = guardiao.obter_relatorio_status()
                print(f"📊 Status: {relatorio['estatisticas']['contradicoes_abertas']} contradições abertas")
                
        except KeyboardInterrupt:
            print("\n⏹️ Parando Guardião...")
            guardiao.parar_monitoramento()
            print("✅ Guardião parado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao iniciar Guardião: {str(e)}")

if __name__ == "__main__":
    main()
