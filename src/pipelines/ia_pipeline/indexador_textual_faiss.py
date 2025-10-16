#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Indexador Textual FAISS
========================
Varrre recursivamente ia_pipeline/documentos, extrai texto de PDFs,
gera embeddings (TF-IDF + SVD 384d), cria índice FAISS e salva metadados.

Saídas:
- faiss_biblioteca_central/indices/textual.faiss
- faiss_biblioteca_central/metadata/textual_vectorizer.pkl
- faiss_biblioteca_central/metadata/textual_svd.pkl
- faiss_biblioteca_central/metadata/textual_metadata.pkl

Uso:
  python ia_pipeline/indexador_textual_faiss.py
"""

import os
import re
import json
import pickle
import logging
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np

try:
    import faiss  # type: ignore
except Exception as e:
    raise RuntimeError(f"FAISS não disponível: {e}")

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    from sklearn.pipeline import Pipeline
except ImportError as e:
    raise RuntimeError(f"scikit-learn não disponível: {e}")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IndexadorTextualFAISS:
    """Indexador textual para documentos PDF com fallback OCR."""
    
    def __init__(self, documentos_path: str = "ia_pipeline/documentos"):
        self.documentos_path = Path(documentos_path)
        self.faiss_path = Path("faiss_biblioteca_central")
        self.indices_path = self.faiss_path / "indices"
        self.metadata_path = self.faiss_path / "metadata"
        
        # Criar diretórios se não existirem
        self.indices_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        
        # Pipeline de embeddings
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        # SVD será ajustado dinamicamente baseado no número de features
        self.svd = None
        self.pipeline = None
        
        # Dados indexados
        self.texts: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = None
        
    def extrair_texto_pdf(self, pdf_path: Path) -> str:
        """Extrai texto de PDF com MÚLTIPLAS estratégias para capturar MUITO MAIS conteúdo."""
        try:
            # ESTRATÉGIA 1: PyPDF2 (mais rápido)
            if PdfReader:
                text = self._extrair_com_pypdf2(pdf_path)
                if len(text.strip()) > 200:
                    logger.info(f"Texto extraído via PyPDF2: {pdf_path.name} ({len(text)} chars)")
                    return text
            
            # ESTRATÉGIA 2: PyMuPDF (mais robusto)
            if PYMUPDF_AVAILABLE:
                text = self._extrair_com_pymupdf(pdf_path)
                if len(text.strip()) > 200:
                    logger.info(f"Texto extraído via PyMuPDF: {pdf_path.name} ({len(text)} chars)")
                    return text
            
            # ESTRATÉGIA 3: pdfplumber (especializado em tabelas)
            if PDFPLUMBER_AVAILABLE:
                text = self._extrair_com_pdfplumber(pdf_path)
                if len(text.strip()) > 200:
                    logger.info(f"Texto extraído via pdfplumber: {pdf_path.name} ({len(text)} chars)")
                    return text
            
            # ESTRATÉGIA 4: OCR com Tesseract (para PDFs escaneados)
            if OCR_AVAILABLE:
                text = self._extrair_com_ocr(pdf_path)
                if len(text.strip()) > 200:
                    logger.info(f"Texto extraído via OCR: {pdf_path.name} ({len(text)} chars)")
                    return text
            
            # NÃO ACEITAR FALLBACKS - FALHAR SE NÃO CONSEGUIR EXTRAIR TEXTO REAL
            raise RuntimeError(f"FALHA TOTAL: Nenhuma estratégia conseguiu extrair texto de {pdf_path.name}")
            
        except Exception as e:
            logger.error(f"ERRO CRÍTICO ao processar {pdf_path.name}: {e}")
            raise  # Re-raise para falhar completamente

    def _extrair_com_pypdf2(self, pdf_path: Path) -> str:
        """Extrai texto usando PyPDF2."""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and len(page_text.strip()) > 10:
                            text += f"=== PÁGINA {page_num + 1} ===\n{page_text.strip()}\n\n"
                    except Exception as e:
                        logger.debug(f"Erro PyPDF2 página {page_num + 1}: {e}")
                        continue
                
                return text
        except Exception as e:
            logger.debug(f"PyPDF2 falhou: {e}")
            return ""

    def _extrair_com_pymupdf(self, pdf_path: Path) -> str:
        """Extrai texto usando PyMuPDF (mais robusto)."""
        try:
            doc = fitz.open(str(pdf_path))
            text = ""
            
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text and len(page_text.strip()) > 10:
                        text += f"=== PÁGINA {page_num + 1} ===\n{page_text.strip()}\n\n"
                except Exception as e:
                    logger.debug(f"Erro PyMuPDF página {page_num + 1}: {e}")
                    continue
            
            doc.close()
            return text
        except Exception as e:
            logger.debug(f"PyMuPDF falhou: {e}")
            return ""

    def _extrair_com_pdfplumber(self, pdf_path: Path) -> str:
        """Extrai texto usando pdfplumber (especializado em tabelas)."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and len(page_text.strip()) > 10:
                            text += f"=== PÁGINA {page_num + 1} ===\n{page_text.strip()}\n\n"
                    except Exception as e:
                        logger.debug(f"Erro pdfplumber página {page_num + 1}: {e}")
                        continue
                
                return text
        except Exception as e:
            logger.debug(f"pdfplumber falhou: {e}")
            return ""

    def _extrair_com_ocr(self, pdf_path: Path) -> str:
        """Extrai texto usando OCR (para PDFs escaneados)."""
        try:
            # Timeout compatível com Windows usando threading
            import threading
            import time
            
            resultado = {"images": None, "erro": None}
            
            def converter_pdf():
                try:
                    resultado["images"] = pdf2image.convert_from_path(str(pdf_path), timeout=30)
                except Exception as e:
                    resultado["erro"] = e
            
            # Executar conversão em thread separada com timeout
            thread = threading.Thread(target=converter_pdf)
            thread.daemon = True
            thread.start()
            thread.join(timeout=30)  # 30 segundos para OCR
            
            if thread.is_alive():
                logger.warning(f"OCR timeout para {pdf_path.name} - pulando")
                return ""
            
            if resultado["erro"]:
                raise resultado["erro"]
            
            images = resultado["images"]
            if not images:
                return ""
            
            text = ""
            for page_num, image in enumerate(images):
                try:
                    # OCR da imagem
                    page_text = pytesseract.image_to_string(image, lang='por')
                    if page_text and len(page_text.strip()) > 10:
                        text += f"=== PÁGINA {page_num + 1} ===\n{page_text.strip()}\n\n"
                except Exception as e:
                    logger.debug(f"Erro OCR página {page_num + 1}: {e}")
                    continue
            
            return text
                
        except Exception as e:
            logger.debug(f"OCR falhou: {e}")
            return ""

    def _identificar_secoes_pagina(self, texto_pagina: str) -> List[str]:
        """Identifica seções na página para melhor estruturação"""
        secoes = []
        
        # Padrões comuns em contratos/aditivos
        padroes_secao = [
            r'(OBJETO[:\s].*?)(?=\n[A-Z]|$)',
            r'(CLÁUSULA\s+\d+[:\s].*?)(?=\n[A-Z]|$)',
            r'(VALOR[:\s].*?)(?=\n[A-Z]|$)',
            r'(PRAZO[:\s].*?)(?=\n[A-Z]|$)',
            r'(CONDIÇÕES[:\s].*?)(?=\n[A-Z]|$)',
            r'(RESPONSABILIDADES[:\s].*?)(?=\n[A-Z]|$)',
            r'(PENALIDADES[:\s].*?)(?=\n[A-Z]|$)',
            r'(RESCISÃO[:\s].*?)(?=\n[A-Z]|$)',
            r'(ADITIVOS[:\s].*?)(?=\n[A-Z]|$)',
            r'(ANEXOS[:\s].*?)(?=\n[A-Z]|$)',
            r'(CONSIDERANDO[:\s].*?)(?=\n[A-Z]|$)',
            r'(RESOLVE[:\s].*?)(?=\n[A-Z]|$)',
        ]
        
        for padrao in padroes_secao:
            matches = re.findall(padrao, texto_pagina, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match.strip()) > 50:  # Seção com pelo menos 50 chars
                    secoes.append(match.strip())
        
        # Se não encontrou seções específicas, dividir por parágrafos
        if not secoes:
            paragrafos = texto_pagina.split('\n\n')
            for paragrafo in paragrafos:
                if len(paragrafo.strip()) > 30:
                    secoes.append(paragrafo.strip())
        
        return secoes
    
    def processar_documentos(self) -> None:
        """Processa TODOS os documentos PDF aos poucos para evitar congelamento."""
        pdf_files = list(self.documentos_path.rglob("*.pdf"))
        total_pdfs = len(pdf_files)
        logger.info(f"Encontrados {total_pdfs} arquivos PDF para processar")
        
        # PROCESSAR TODOS os PDFs, mas aos poucos para não travar
        logger.info(f"PROCESSANDO TODOS OS {total_pdfs} PDFs aos poucos para máxima extração")
        
        for i, pdf_path in enumerate(pdf_files):
            logger.info(f"Processando {i+1}/{total_pdfs}: {pdf_path.name}")
            
            try:
                # Timeout compatível com Windows usando threading
                import threading
                import time
                
                resultado = {"texto": None, "erro": None}
                
                def processar_pdf():
                    try:
                        resultado["texto"] = self.extrair_texto_pdf(pdf_path)
                    except Exception as e:
                        resultado["erro"] = e
                
                # Executar em thread separada com timeout
                thread = threading.Thread(target=processar_pdf)
                thread.daemon = True
                thread.start()
                thread.join(timeout=60)  # 60 segundos por PDF
                
                if thread.is_alive():
                    logger.warning(f"⏰ Timeout ao processar {pdf_path.name} - pulando")
                    continue
                
                if resultado["erro"]:
                    raise resultado["erro"]
                
                texto = resultado["texto"]
                
                # Fatiar em chunks se for muito longo
                chunks = self.fatiar_texto(texto, pdf_path.name)
                
                for j, chunk in enumerate(chunks):
                    if len(chunk.strip()) >= 30:  # Chunk mínimo útil
                        self.texts.append(chunk)
                        self.metadata.append({
                            'arquivo': pdf_path.name,
                            'caminho': str(pdf_path),
                            'chunk': j + 1,
                            'tamanho_arquivo': pdf_path.stat().st_size,
                            'tipo': 'contrato' if 'contrato' in pdf_path.name.lower() else 'aditivo' if 'aditivo' in pdf_path.name.lower() else 'outro'
                        })
                
                logger.info(f"✓ {pdf_path.name}: {len(chunks)} chunks extraídos")
                
                # PAUSA a cada 5 PDFs para não travar o sistema
                if (i + 1) % 5 == 0:
                    logger.info(f"⏸️ Pausa após {i + 1} PDFs processados...")
                    import time
                    time.sleep(1)  # Pausa de 1 segundo
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar {pdf_path.name}: {e}")
                continue  # Continuar com o próximo arquivo
            except Exception as e:
                logger.error(f"❌ Erro ao processar {pdf_path.name}: {e}")
                continue  # Continuar com o próximo arquivo
        
        logger.info(f"Total de chunks processados: {len(self.texts)} de {total_pdfs} PDFs")
    
    def fatiar_texto(self, texto: str, nome_arquivo: str) -> List[str]:
        """Faz o fatiamento SIMPLIFICADO e RÁPIDO para evitar congelamento."""
        # Remover quebras de linha excessivas
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        
        chunks = []
        
        # ESTRATÉGIA SIMPLIFICADA: Dividir por parágrafos e frases
        paragrafos = texto.split('\n\n')
        for paragrafo in paragrafos:
            paragrafo = paragrafo.strip()
            if len(paragrafo) >= 100:  # Parágrafos com pelo menos 100 chars
                chunks.append(paragrafo)
        
        # Dividir por frases longas
        frases = re.split(r'[.!?]+', texto)
        for frase in frases:
            frase = frase.strip()
            if len(frase) >= 150:  # Frases com pelo menos 150 chars
                chunks.append(frase)
        
        # Chunking por tamanho fixo (mais simples)
        chunk_size = 1000  # Chunks maiores para menos processamento
        overlap = 100      # Overlap menor
        
        for i in range(0, len(texto), chunk_size - overlap):
            chunk = texto[i:i + chunk_size]
            chunk = chunk.strip()
            if len(chunk) >= 200:  # Chunks com pelo menos 200 chars
                chunks.append(chunk)
        
        # Limitar a máximo de 50 chunks por documento para máxima extração
        max_chunks_per_doc = 50
        if len(chunks) > max_chunks_per_doc:
            chunks = chunks[:max_chunks_per_doc]
        
        logger.info(f"Documento {nome_arquivo}: {len(chunks)} chunks criados (MÁXIMA EXTRAÇÃO)")
        return chunks
    
    def gerar_embeddings(self) -> None:
        """Gera embeddings TF-IDF + SVD para os textos."""
        if not self.texts:
            raise ValueError("Nenhum texto para processar")
        
        logger.info("Gerando embeddings TF-IDF + SVD...")
        
        # Ajustar pipeline para o número de documentos
        if len(self.texts) < 100:
            # Para poucos documentos, ajustar parâmetros
            self.vectorizer.min_df = 1
            self.vectorizer.max_features = min(5000, len(self.texts) * 10)
        
        # Primeiro gerar TF-IDF para descobrir o número de features
        tfidf_matrix = self.vectorizer.fit_transform(self.texts)
        n_features = tfidf_matrix.shape[1]
        
        logger.info(f"TF-IDF gerado com {n_features} features")
        
        # Ajustar SVD dinamicamente
        n_components = min(384, n_features - 1)  # Máximo 384, mas não mais que features disponíveis
        if n_components < 2:
            n_components = 2  # Mínimo de 2 componentes
        
        logger.info(f"Usando {n_components} componentes SVD")
        
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        
        # Criar pipeline
        self.pipeline = Pipeline([
            ('tfidf', self.vectorizer),
            ('svd', self.svd)
        ])
        
        # Gerar embeddings
        self.embeddings = self.pipeline.fit_transform(self.texts)
        
        logger.info(f"Embeddings gerados: {self.embeddings.shape}")
    
    def criar_indice_faiss(self) -> None:
        """Cria índice FAISS para busca vetorial."""
        if self.embeddings is None:
            raise ValueError("Embeddings não foram gerados")
        
        logger.info("Criando índice FAISS...")
        
        # Converter para float32 e normalizar embeddings
        embeddings_float32 = self.embeddings.astype('float32')
        
        # Normalizar embeddings usando numpy
        norms = np.linalg.norm(embeddings_float32, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Evitar divisão por zero
        embeddings_normalized = embeddings_float32 / norms
        
        # NUNCA SOBRESCREVER main_index.faiss EXISTENTE!
        main_index_path = self.indices_path / "main_index.faiss"
        
        if main_index_path.exists():
            logger.warning(f"⚠️ main_index.faiss EXISTENTE DETECTADO - NÃO MODIFICAR!")
            logger.info(f"Índice existente: {main_index_path}")
            
            # FAZER BACKUP DE SEGURANÇA
            backup_path = self.indices_path / f"main_index_backup_{int(time.time())}.faiss"
            logger.warning(f"⚠️ FAZENDO BACKUP DE SEGURANÇA: {backup_path}")
            
            import shutil
            shutil.copy2(str(main_index_path), str(backup_path))
            logger.info(f"✅ Backup criado: {backup_path}")
            
            # SEMPRE CRIAR ARQUIVO SEPARADO
            logger.warning(f"⚠️ CRIANDO ÍNDICE TEXTUAL SEPARADO para não perder dados!")
            self._criar_novo_indice(embeddings_normalized)
            
        else:
            logger.info("Índice principal não encontrado, criando novo...")
            self._criar_novo_indice(embeddings_normalized)
    
    def _criar_novo_indice(self, embeddings_normalized: np.ndarray) -> None:
        """Cria novo índice FAISS quando necessário."""
        # NUNCA SOBRESCREVER main_index.faiss EXISTENTE!
        main_index_path = self.indices_path / "main_index.faiss"
        
        if main_index_path.exists():
            # FAZER BACKUP ANTES DE QUALQUER MODIFICAÇÃO
            backup_path = self.indices_path / f"main_index_backup_{int(time.time())}.faiss"
            logger.warning(f"⚠️ FAZENDO BACKUP DE SEGURANÇA: {backup_path}")
            
            import shutil
            shutil.copy2(str(main_index_path), str(backup_path))
            logger.info(f"✅ Backup criado: {backup_path}")
            
            # CRIAR NOVO ARQUIVO SEPARADO, NÃO SOBRESCREVER
            index_path = self.indices_path / "textual_index.faiss"
            logger.warning(f"⚠️ CRIANDO ÍNDICE SEPARADO: {index_path}")
        else:
            index_path = self.indices_path / "textual_index.faiss"
        
        # Criar índice
        dimension = embeddings_normalized.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner Product para similaridade de cosseno
        
        # Adicionar vetores
        index.add(embeddings_normalized)
        
        # Salvar como arquivo SEPARADO
        faiss.write_index(index, str(index_path))
        
        logger.info(f"✅ Novo índice FAISS criado em: {index_path}")
        logger.warning(f"⚠️ NÃO SOBRESCREVEU main_index.faiss existente!")
        self.faiss_index = index
    
    def salvar_metadados(self) -> None:
        """Salva metadados e modelos treinados."""
        logger.info("Salvando metadados...")
        
        # Salvar vectorizer
        vectorizer_path = self.metadata_path / "textual_vectorizer.pkl"
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Salvar SVD
        svd_path = self.metadata_path / "textual_svd.pkl"
        with open(svd_path, 'wb') as f:
            pickle.dump(self.svd, f)
        
        # Salvar metadados
        metadata_path = self.metadata_path / "textual_metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        # Salvar estatísticas
        stats = {
            'total_documentos': len(set(m['arquivo'] for m in self.metadata)),
            'total_chunks': len(self.texts),
            'dimensao_embeddings': self.embeddings.shape[1] if self.embeddings is not None else 0,
            'arquivos_processados': list(set(m['arquivo'] for m in self.metadata))
        }
        
        stats_path = self.metadata_path / "textual_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadados salvos em: {self.metadata_path}")
        logger.info(f"Estatísticas: {stats}")
    
    def executar_indexacao(self) -> None:
        """Executa todo o processo de indexação."""
        try:
            logger.info("=== INICIANDO INDEXAÇÃO TEXTUAL ===")
            
            # Processar documentos
            self.processar_documentos()
            
            if not self.texts:
                logger.error("Nenhum texto foi extraído dos documentos")
                return
            
            # Gerar embeddings
            self.gerar_embeddings()
            
            # Criar índice FAISS
            self.criar_indice_faiss()
            
            # Salvar metadados
            self.salvar_metadados()
            
            logger.info("=== INDEXAÇÃO TEXTUAL CONCLUÍDA COM SUCESSO ===")
            
        except Exception as e:
            logger.error(f"Erro durante indexação: {e}")
            raise


def main():
    """Função principal."""
    try:
        indexador = IndexadorTextualFAISS()
        indexador.executar_indexacao()
    except Exception as e:
        logger.error(f"Falha na indexação: {e}")
        exit(1)


if __name__ == "__main__":
    main()


