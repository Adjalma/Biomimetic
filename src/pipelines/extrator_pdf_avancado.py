"""
Sistema Avançado de Extração de PDFs para GIC
============================================

Implementa múltiplas bibliotecas de extração com fallbacks inteligentes
baseado nas melhores práticas de 2024.
"""

import logging
import io
import base64
import re
import unicodedata
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ExtratorPDFAvancado:
    """Extrator robusto de PDFs com múltiplas estratégias"""
    
    def __init__(self):
        self.estrategias_disponiveis = []
        self._verificar_dependencias()
    
    def _verificar_dependencias(self):
        """Verifica quais bibliotecas estão disponíveis"""
        try:
            import pymupdf4llm
            self.estrategias_disponiveis.append('pymupdf4llm')
            logger.info("[PDF] PyMuPDF4LLM disponível - Estratégia premium ativada")
        except ImportError:
            pass
        
        try:
            import unstructured
            self.estrategias_disponiveis.append('unstructured')
            logger.info("[PDF] Unstructured disponível - Estratégia semântica ativada")
        except ImportError:
            pass
        
        try:
            import pdfplumber
            self.estrategias_disponiveis.append('pdfplumber')
            logger.info("[PDF] PDFPlumber disponível - Estratégia de tabelas ativada")
        except ImportError:
            pass
        
        try:
            import fitz  # PyMuPDF
            self.estrategias_disponiveis.append('pymupdf')
            logger.info("[PDF] PyMuPDF disponível - Estratégia robusta ativada")
        except ImportError:
            pass
        
        try:
            import textract
            self.estrategias_disponiveis.append('textract')
            logger.info("[PDF] Textract disponível - Estratégia OCR ativada")
        except ImportError:
            pass
        
        logger.info(f"[PDF] Estratégias disponíveis: {self.estrategias_disponiveis}")
    
    def extrair_dados_completos(self, documentos: List[Dict]) -> Dict[str, Any]:
        """Extrai dados completos usando múltiplas estratégias"""
        try:
            resultados = {
                'campos_extraidos': {},
                'texto_completo': '',
                'tabelas': [],
                'metadados': {},
                'estrategia_usada': None,
                'qualidade_extracao': 0.0
            }
            
            for doc in documentos:
                if not self._eh_pdf(doc):
                    continue
                
                logger.info(f"[PDF] Processando: {doc.get('nome', 'documento')}")
                
                # Tentar estratégias em ordem de qualidade
                for estrategia in ['pymupdf4llm', 'unstructured', 'pdfplumber', 'pymupdf', 'textract']:
                    if estrategia in self.estrategias_disponiveis:
                        try:
                            resultado = self._extrair_com_estrategia(doc, estrategia)
                            if self._validar_qualidade_extracao(resultado):
                                resultados.update(resultado)
                                resultados['estrategia_usada'] = estrategia
                                logger.info(f"[PDF] Sucesso com estratégia: {estrategia}")
                                break
                        except Exception as e:
                            logger.warning(f"[PDF] Falha na estratégia {estrategia}: {e}")
                            continue
                
                # Se chegou aqui, extrair campos específicos
                if resultados['texto_completo']:
                    campos = self._extrair_campos_contratuais(resultados['texto_completo'])
                    resultados['campos_extraidos'].update(campos)
            
            # Calcular qualidade final
            resultados['qualidade_extracao'] = self._calcular_qualidade(resultados)
            
            logger.info(f"[PDF] Extração concluída - Qualidade: {resultados['qualidade_extracao']:.2f}")
            return resultados
            
        except Exception as e:
            logger.error(f"[PDF] Erro na extração completa: {e}")
            return self._resultado_vazio()
    
    def _eh_pdf(self, doc: Dict) -> bool:
        """Verifica se o documento é um PDF"""
        nome = doc.get('nome', '').lower()
        tipo = doc.get('tipo', '').lower()
        data_url = doc.get('dataUrl', '')
        
        return (nome.endswith('.pdf') or 
                'pdf' in tipo or 
                'application/pdf' in data_url)
    
    def _extrair_com_estrategia(self, doc: Dict, estrategia: str) -> Dict[str, Any]:
        """Extrai dados usando estratégia específica"""
        data_url = doc.get('dataUrl', '')
        if not data_url or ',' not in data_url:
            raise ValueError("DataURL inválida")
        
        _, b64 = data_url.split(',', 1)
        pdf_bytes = base64.b64decode(b64)
        
        if estrategia == 'pymupdf4llm':
            return self._extrair_pymupdf4llm(pdf_bytes)
        elif estrategia == 'unstructured':
            return self._extrair_unstructured(pdf_bytes)
        elif estrategia == 'pdfplumber':
            return self._extrair_pdfplumber(pdf_bytes)
        elif estrategia == 'pymupdf':
            return self._extrair_pymupdf(pdf_bytes)
        elif estrategia == 'textract':
            return self._extrair_textract(pdf_bytes)
        else:
            raise ValueError(f"Estratégia desconhecida: {estrategia}")
    
    def _extrair_pymupdf4llm(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extração premium com PyMuPDF4LLM - Melhor para LLMs"""
        import pymupdf4llm
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            
            # Extrair markdown estruturado
            markdown_text = pymupdf4llm.to_markdown(tmp.name)
            
            return {
                'texto_completo': markdown_text,
                'formato': 'markdown',
                'estruturado': True,
                'qualidade_estimada': 0.95
            }
    
    def _extrair_unstructured(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extração semântica com Unstructured - Melhor para chunking"""
        from unstructured.partition.auto import partition
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            
            elements = partition(filename=tmp.name)
            
            texto_completo = ""
            metadados = []
            
            for element in elements:
                texto_completo += f"{element.text}\n"
                metadados.append({
                    'tipo': element.category,
                    'texto': element.text[:100],
                    'posicao': getattr(element, 'metadata', {})
                })
            
            return {
                'texto_completo': texto_completo,
                'metadados': metadados,
                'elementos_semanticos': len(elements),
                'qualidade_estimada': 0.90
            }
    
    def _extrair_pdfplumber(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extração focada em tabelas com PDFPlumber"""
        import pdfplumber
        
        texto_completo = ""
        tabelas = []
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                # Extrair texto
                texto_pagina = page.extract_text()
                if texto_pagina:
                    texto_completo += f"--- Página {i+1} ---\n{texto_pagina}\n\n"
                
                # Extrair tabelas
                tabelas_pagina = page.extract_tables()
                for j, tabela in enumerate(tabelas_pagina):
                    tabelas.append({
                        'pagina': i+1,
                        'tabela': j+1,
                        'dados': tabela,
                        'linhas': len(tabela),
                        'colunas': len(tabela[0]) if tabela else 0
                    })
        
        return {
            'texto_completo': texto_completo,
            'tabelas': tabelas,
            'total_tabelas': len(tabelas),
            'qualidade_estimada': 0.85
        }
    
    def _extrair_pymupdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extração robusta com PyMuPDF"""
        import fitz
        
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texto_completo = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            texto_pagina = page.get_text()
            texto_completo += f"--- Página {page_num+1} ---\n{texto_pagina}\n\n"
        
        doc.close()
        
        return {
            'texto_completo': texto_completo,
            'total_paginas': len(doc),
            'qualidade_estimada': 0.80
        }
    
    def _extrair_textract(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extração com OCR usando Textract"""
        import textract
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            
            texto = textract.process(tmp.name).decode('utf-8')
            
            return {
                'texto_completo': texto,
                'metodo': 'ocr',
                'qualidade_estimada': 0.75
            }
    
    def _extrair_campos_contratuais(self, texto: str) -> Dict[str, str]:
        """Extrai campos específicos de contratos usando regex avançado"""
        campos = {}
        
        # Normalizar texto
        texto_norm = unicodedata.normalize('NFKD', texto)
        
        # Padrões mais robustos baseados em contratos reais
        padroes = {
            'numero_contrato': [
                r'(?:ICJ|Contrato|Instrumento)\s*[Nn]?[ºo°]?\s*:?\s*([A-Z0-9\./\-]{6,})',
                r'(?:Número|N[ºo°])\s*do\s*[Cc]ontrato\s*:?\s*([A-Z0-9\./\-]{6,})',
                r'[Cc]ontrato\s*[Nn]?[ºo°]?\s*([A-Z0-9\./\-]{6,})'
            ],
            'contratada': [
                r'[Cc]ontratada\s*:?\s*([A-Z][A-Za-z\s\.,&\-]{10,100})',
                r'[Ee]mpresa\s*[Cc]ontratada\s*:?\s*([A-Z][A-Za-z\s\.,&\-]{10,100})',
                r'[Ff]ornecedor\s*:?\s*([A-Z][A-Za-z\s\.,&\-]{10,100})'
            ],
            'objeto_contrato': [
                r'[Oo]bjeto\s*:?\s*([^\.]{20,300}?)(?:\n|[Vv]igência|[Pp]razo|[Vv]alor)',
                r'[Ff]inalidade\s*:?\s*([^\.]{20,300}?)(?:\n|[Vv]igência|[Pp]razo)',
                r'[Ee]scopo\s*:?\s*([^\.]{20,300}?)(?:\n|[Vv]igência|[Pp]razo)'
            ],
            'data_final_contrato': [
                r'[Vv]igência\s*até\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
                r'[Pp]razo\s*final\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
                r'[Tt]érmino\s*em\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})'
            ]
        }
        
        for campo, patterns in padroes.items():
            for pattern in patterns:
                match = re.search(pattern, texto_norm, re.IGNORECASE | re.MULTILINE)
                if match:
                    valor = match.group(1).strip()
                    if len(valor) > 3:  # Filtrar valores muito curtos
                        campos[campo] = valor
                        logger.info(f"[PDF] Campo extraído - {campo}: {valor[:50]}...")
                        break
        
        return campos
    
    def _validar_qualidade_extracao(self, resultado: Dict) -> bool:
        """Valida se a extração teve qualidade mínima"""
        texto = resultado.get('texto_completo', '')
        qualidade = resultado.get('qualidade_estimada', 0.0)
        
        # Critérios de qualidade
        tem_texto_suficiente = len(texto.strip()) > 100
        tem_qualidade_minima = qualidade > 0.5
        nao_tem_muito_lixo = texto.count('�') < len(texto) * 0.1
        
        return tem_texto_suficiente and tem_qualidade_minima and nao_tem_muito_lixo
    
    def _calcular_qualidade(self, resultados: Dict) -> float:
        """Calcula qualidade geral da extração"""
        try:
            texto = resultados.get('texto_completo', '')
            campos = resultados.get('campos_extraidos', {})
            
            # Pontuação base
            pontuacao = 0.0
            
            # Texto extraído (40%)
            if len(texto) > 500:
                pontuacao += 0.4
            elif len(texto) > 100:
                pontuacao += 0.2
            
            # Campos extraídos (40%)
            campos_importantes = ['numero_contrato', 'contratada', 'objeto_contrato']
            campos_encontrados = sum(1 for campo in campos_importantes if campo in campos)
            pontuacao += (campos_encontrados / len(campos_importantes)) * 0.4
            
            # Qualidade estimada da estratégia (20%)
            qualidade_estrategia = resultados.get('qualidade_estimada', 0.0)
            pontuacao += qualidade_estrategia * 0.2
            
            return min(pontuacao, 1.0)
            
        except Exception:
            return 0.0
    
    def _resultado_vazio(self) -> Dict[str, Any]:
        """Retorna resultado vazio em caso de falha"""
        return {
            'campos_extraidos': {},
            'texto_completo': '',
            'tabelas': [],
            'metadados': {},
            'estrategia_usada': None,
            'qualidade_extracao': 0.0,
            'erro': 'Falha na extração'
        }

# Função de conveniência para uso direto
def extrair_dados_pdf_avancado(documentos: List[Dict]) -> Dict[str, Any]:
    """Função principal para extração avançada de PDFs"""
    extrator = ExtratorPDFAvancado()
    return extrator.extrair_dados_completos(documentos)
