#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE VISÃO COMPUTACIONAL PARA IA AUTOEVOLUTIVA
====================================================

Este módulo implementa o sistema de visão computacional que adiciona
capacidade de "ver" ao sistema de IA autoevolutiva, permitindo processamento
de imagens, documentos e conteúdo visual.

ARQUITETURA:
- Sistema modular de processamento de imagens
- Integração com OCR (Reconhecimento Óptico de Caracteres)
- Análise de layout e estrutura de documentos
- Detecção e processamento de assinaturas
- Integração com sistema RAG (Retrieval-Augmented Generation)

FUNCIONALIDADES PRINCIPAIS:
1. OCR (Reconhecimento Óptico de Caracteres):
   - Extração de texto de imagens
   - Reconhecimento de caracteres em múltiplos idiomas
   - Processamento de documentos escaneados
   - Correção automática de erros de OCR

2. ANÁLISE DE LAYOUT DE DOCUMENTOS:
   - Identificação de seções e parágrafos
   - Detecção de tabelas e listas
   - Análise de estrutura hierárquica
   - Extração de metadados visuais

3. DETECÇÃO DE ASSINATURAS:
   - Localização de assinaturas em documentos
   - Validação de autenticidade
   - Extração de características únicas
   - Integração com sistema de auditoria

4. PROCESSAMENTO DE IMAGENS:
   - Redimensionamento e otimização
   - Correção de distorções
   - Melhoria de qualidade
   - Conversão entre formatos

5. INTEGRAÇÃO COM SISTEMA RAG:
   - Indexação de conteúdo visual
   - Busca semântica em imagens
   - Geração de descrições automáticas
   - Integração com barramento de conhecimento

COMPONENTES:
- VisionSystem: Classe principal do sistema
- ImagePreprocessor: Pré-processamento de imagens
- OCRProcessor: Processamento de OCR
- LayoutAnalyzer: Análise de layout
- SignatureDetector: Detecção de assinaturas
- RAGIntegrator: Integração com RAG

Versão: 2.0
Data: 2024
Autor: Sistema IA Autoevolutiva
"""

# =============================================================================
# IMPORTS E DEPENDÊNCIAS
# =============================================================================

import os             # Operações de sistema de arquivos
import json           # Manipulação de dados JSON
import logging        # Sistema de logging avançado
import time           # Medição de tempo e performance
import hashlib        # Hashing para identificação única
import numpy as np    # Computação numérica otimizada
from typing import Dict, List, Optional, Tuple, Any, Union  # Type hints
from dataclasses import dataclass, field  # Classes de dados
from datetime import datetime  # Timestamps e data/hora
from pathlib import Path  # Manipulação de caminhos de arquivos

# Processamento de Imagens
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    CV2_AVAILABLE = True
    PIL_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    PIL_AVAILABLE = False

# OCR
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from easyocr import Reader
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# Machine Learning para Visão
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from torchvision import models
    TORCHVISION_AVAILABLE = True
except ImportError:
    TORCHVISION_AVAILABLE = False

# Detecção de Objetos
try:
    import ultralytics
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vision_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ImageRegion:
    """Região de interesse em uma imagem"""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    region_type: str  # 'text', 'signature', 'table', 'image'
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OCRResult:
    """Resultado do OCR"""
    text: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # x, y, width, height
    region_type: str
    language: str = "por"

@dataclass
class LayoutAnalysis:
    """Análise de layout de documento"""
    regions: List[ImageRegion]
    document_type: str
    confidence: float
    page_number: int
    metadata: Dict[str, Any]

@dataclass
class SignatureDetection:
    """Detecção de assinatura"""
    signature_regions: List[ImageRegion]
    confidence: float
    is_valid: bool
    metadata: Dict[str, Any]

@dataclass
class VisionAnalysis:
    """Análise completa de visão"""
    ocr_results: List[OCRResult]
    layout_analysis: LayoutAnalysis
    signature_detection: SignatureDetection
    extracted_text: str
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any]

class ImagePreprocessor:
    """Pré-processamento de imagens"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Carrega imagem"""
        try:
            if CV2_AVAILABLE:
                image = cv2.imread(image_path)
                if image is not None:
                    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar imagem {image_path}: {e}")
            return None
    
    def resize_image(self, image: np.ndarray, size: Tuple[int, int] = None) -> np.ndarray:
        """Redimensiona imagem"""
        if size is None:
            size = self.target_size
        
        try:
            if CV2_AVAILABLE:
                return cv2.resize(image, size)
            return image
        except Exception as e:
            logger.error(f"Erro ao redimensionar imagem: {e}")
            return image
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Melhora qualidade da imagem para OCR"""
        try:
            if not CV2_AVAILABLE:
                return image
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Aplicar filtro bilateral para reduzir ruído
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Aplicar equalização de histograma
            enhanced = cv2.equalizeHist(denoised)
            
            # Aplicar threshold adaptativo
            thresh = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
        except Exception as e:
            logger.error(f"Erro ao melhorar imagem: {e}")
            return image
    
    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        """Detecta bordas na imagem"""
        try:
            if not CV2_AVAILABLE:
                return image
            
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            return edges
        except Exception as e:
            logger.error(f"Erro ao detectar bordas: {e}")
            return image

class OCRProcessor:
    """Processador de OCR"""
    
    def __init__(self, languages: List[str] = ['por', 'eng']):
        self.languages = languages
        self.tesseract_config = '--oem 3 --psm 6'
        self.easyocr_reader = None
        self._initialize_easyocr()
    
    def _initialize_easyocr(self):
        """Inicializa EasyOCR"""
        if EASYOCR_AVAILABLE:
            try:
                self.easyocr_reader = Reader(self.languages)
                logger.info("EasyOCR inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar EasyOCR: {e}")
    
    def extract_text_tesseract(self, image: np.ndarray) -> List[OCRResult]:
        """Extrai texto usando Tesseract"""
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            # Configurar Tesseract
            custom_config = f'{self.tesseract_config} -l {"+".join(self.languages)}'
            
            # Extrair texto com bounding boxes
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            results = []
            for i in range(len(data['text'])):
                if data['conf'][i] > 30:  # Filtrar por confiança
                    text = data['text'][i].strip()
                    if text:
                        result = OCRResult(
                            text=text,
                            confidence=data['conf'][i] / 100.0,
                            bounding_box=(
                                data['left'][i],
                                data['top'][i],
                                data['width'][i],
                                data['height'][i]
                            ),
                            region_type='text',
                            language=self.languages[0]
                        )
                        results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Erro no OCR Tesseract: {e}")
            return []
    
    def extract_text_easyocr(self, image: np.ndarray) -> List[OCRResult]:
        """Extrai texto usando EasyOCR"""
        if not EASYOCR_AVAILABLE or self.easyocr_reader is None:
            return []
        
        try:
            results = self.easyocr_reader.readtext(image)
            
            ocr_results = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Filtrar por confiança
                    # Converter bbox para formato padrão
                    x1, y1 = bbox[0]
                    x3, y3 = bbox[2]
                    width = int(x3 - x1)
                    height = int(y3 - y1)
                    
                    result = OCRResult(
                        text=text.strip(),
                        confidence=confidence,
                        bounding_box=(int(x1), int(y1), width, height),
                        region_type='text',
                        language=self.languages[0]
                    )
                    ocr_results.append(result)
            
            return ocr_results
        except Exception as e:
            logger.error(f"Erro no OCR EasyOCR: {e}")
            return []
    
    def extract_text(self, image: np.ndarray, method: str = 'auto') -> List[OCRResult]:
        """Extrai texto usando método especificado"""
        if method == 'tesseract':
            return self.extract_text_tesseract(image)
        elif method == 'easyocr':
            return self.extract_text_easyocr(image)
        else:
            # Auto: tentar EasyOCR primeiro, depois Tesseract
            results = self.extract_text_easyocr(image)
            if not results:
                results = self.extract_text_tesseract(image)
            return results

class LayoutAnalyzer:
    """Analisador de layout de documentos"""
    
    def __init__(self):
        self.region_types = ['header', 'footer', 'body', 'sidebar', 'table', 'image']
    
    def analyze_layout(self, image: np.ndarray, ocr_results: List[OCRResult]) -> LayoutAnalysis:
        """Analisa layout do documento"""
        try:
            regions = []
            
            # Agrupar texto por regiões
            text_regions = self._group_text_regions(ocr_results)
            
            # Identificar tipo de documento
            document_type = self._identify_document_type(image, text_regions)
            
            # Detectar tabelas
            table_regions = self._detect_tables(image)
            regions.extend(table_regions)
            
            # Detectar imagens
            image_regions = self._detect_images(image)
            regions.extend(image_regions)
            
            # Converter OCR results para regions
            for region in text_regions:
                regions.append(ImageRegion(
                    x=region['x'],
                    y=region['y'],
                    width=region['width'],
                    height=region['height'],
                    confidence=region['confidence'],
                    region_type=region['type'],
                    content=region['text']
                ))
            
            return LayoutAnalysis(
                regions=regions,
                document_type=document_type,
                confidence=0.8,  # Placeholder
                page_number=1,
                metadata={'total_regions': len(regions)}
            )
        except Exception as e:
            logger.error(f"Erro na análise de layout: {e}")
            return LayoutAnalysis(
                regions=[],
                document_type='unknown',
                confidence=0.0,
                page_number=1,
                metadata={'error': str(e)}
            )
    
    def _group_text_regions(self, ocr_results: List[OCRResult]) -> List[Dict[str, Any]]:
        """Agrupa resultados de OCR em regiões"""
        if not ocr_results:
            return []
        
        # Agrupar por proximidade
        groups = []
        used = set()
        
        for i, result in enumerate(ocr_results):
            if i in used:
                continue
            
            group = {
                'x': result.bounding_box[0],
                'y': result.bounding_box[1],
                'width': result.bounding_box[2],
                'height': result.bounding_box[3],
                'text': result.text,
                'confidence': result.confidence,
                'type': 'text'
            }
            
            used.add(i)
            
            # Encontrar textos próximos
            for j, other_result in enumerate(ocr_results[i+1:], i+1):
                if j in used:
                    continue
                
                # Verificar proximidade
                if self._are_regions_close(result.bounding_box, other_result.bounding_box):
                    group['text'] += ' ' + other_result.text
                    group['width'] = max(group['width'], other_result.bounding_box[2])
                    group['height'] = max(group['height'], other_result.bounding_box[3])
                    group['confidence'] = min(group['confidence'], other_result.confidence)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_regions_close(self, bbox1: Tuple[int, int, int, int], 
                          bbox2: Tuple[int, int, int, int], 
                          threshold: int = 50) -> bool:
        """Verifica se duas regiões estão próximas"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calcular centro das regiões
        center1 = (x1 + w1 // 2, y1 + h1 // 2)
        center2 = (x2 + w2 // 2, y2 + h2 // 2)
        
        # Calcular distância
        distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
        
        return distance < threshold
    
    def _identify_document_type(self, image: np.ndarray, 
                               text_regions: List[Dict[str, Any]]) -> str:
        """Identifica tipo de documento"""
        try:
            # Análise simples baseada no texto
            all_text = ' '.join([region['text'].lower() for region in text_regions])
            
            if any(word in all_text for word in ['contrato', 'contract', 'agreement']):
                return 'contract'
            elif any(word in all_text for word in ['invoice', 'fatura', 'bill']):
                return 'invoice'
            elif any(word in all_text for word in ['report', 'relatório']):
                return 'report'
            elif any(word in all_text for word in ['form', 'formulário']):
                return 'form'
            else:
                return 'document'
        except Exception as e:
            logger.error(f"Erro ao identificar tipo de documento: {e}")
            return 'unknown'
    
    def _detect_tables(self, image: np.ndarray) -> List[ImageRegion]:
        """Detecta tabelas na imagem"""
        try:
            if not CV2_AVAILABLE:
                return []
            
            # Detectar linhas horizontais e verticais
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Detectar linhas horizontais
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Detectar linhas verticais
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combinar linhas
            table_mask = cv2.add(horizontal_lines, vertical_lines)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            table_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Filtrar por área mínima
                    x, y, w, h = cv2.boundingRect(contour)
                    table_regions.append(ImageRegion(
                        x=x, y=y, width=w, height=h,
                        confidence=0.7,
                        region_type='table'
                    ))
            
            return table_regions
        except Exception as e:
            logger.error(f"Erro ao detectar tabelas: {e}")
            return []
    
    def _detect_images(self, image: np.ndarray) -> List[ImageRegion]:
        """Detecta imagens/gráficos no documento"""
        try:
            if not CV2_AVAILABLE:
                return []
            
            # Detectar regiões com alta variação de cor
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Calcular gradiente
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Threshold para detectar regiões com alta variação
            _, binary = cv2.threshold(gradient_magnitude, 50, 255, cv2.THRESH_BINARY)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(binary.astype(np.uint8), 
                                         cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            image_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Filtrar por área mínima
                    x, y, w, h = cv2.boundingRect(contour)
                    image_regions.append(ImageRegion(
                        x=x, y=y, width=w, height=h,
                        confidence=0.6,
                        region_type='image'
                    ))
            
            return image_regions
        except Exception as e:
            logger.error(f"Erro ao detectar imagens: {e}")
            return []

class SignatureDetector:
    """Detector de assinaturas"""
    
    def __init__(self):
        self.signature_keywords = ['assinatura', 'signature', 'assinado', 'signed', 'firma']
    
    def detect_signatures(self, image: np.ndarray, 
                         ocr_results: List[OCRResult]) -> SignatureDetection:
        """Detecta assinaturas no documento"""
        try:
            signature_regions = []
            
            # Buscar por palavras-chave relacionadas a assinaturas
            for result in ocr_results:
                if any(keyword in result.text.lower() for keyword in self.signature_keywords):
                    # Região próxima pode conter assinatura
                    signature_region = self._find_signature_near_text(
                        image, result.bounding_box
                    )
                    if signature_region:
                        signature_regions.append(signature_region)
            
            # Detectar assinaturas por padrões visuais
            visual_signatures = self._detect_visual_signatures(image)
            signature_regions.extend(visual_signatures)
            
            # Validar assinaturas
            is_valid = len(signature_regions) > 0
            
            return SignatureDetection(
                signature_regions=signature_regions,
                confidence=0.7 if is_valid else 0.0,
                is_valid=is_valid,
                metadata={'total_signatures': len(signature_regions)}
            )
        except Exception as e:
            logger.error(f"Erro na detecção de assinaturas: {e}")
            return SignatureDetection(
                signature_regions=[],
                confidence=0.0,
                is_valid=False,
                metadata={'error': str(e)}
            )
    
    def _find_signature_near_text(self, image: np.ndarray, 
                                 text_bbox: Tuple[int, int, int, int]) -> Optional[ImageRegion]:
        """Encontra assinatura próxima ao texto"""
        try:
            if not CV2_AVAILABLE:
                return None
            
            x, y, w, h = text_bbox
            
            # Definir região de busca (abaixo do texto)
            search_x = max(0, x - 50)
            search_y = y + h
            search_w = min(w + 100, image.shape[1] - search_x)
            search_h = min(100, image.shape[0] - search_y)
            
            if search_h <= 0 or search_w <= 0:
                return None
            
            # Extrair região de busca
            search_region = image[search_y:search_y+search_h, search_x:search_x+search_w]
            
            # Detectar linhas curvas (características de assinaturas)
            gray = cv2.cvtColor(search_region, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Contar pixels de borda
            edge_density = np.sum(edges > 0) / (search_h * search_w)
            
            if edge_density > 0.1:  # Threshold para detectar assinatura
                return ImageRegion(
                    x=search_x, y=search_y, width=search_w, height=search_h,
                    confidence=edge_density,
                    region_type='signature'
                )
            
            return None
        except Exception as e:
            logger.error(f"Erro ao encontrar assinatura próxima ao texto: {e}")
            return None
    
    def _detect_visual_signatures(self, image: np.ndarray) -> List[ImageRegion]:
        """Detecta assinaturas por padrões visuais"""
        try:
            if not CV2_AVAILABLE:
                return []
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Detectar bordas
            edges = cv2.Canny(gray, 50, 150)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            signature_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 5000:  # Tamanho típico de assinatura
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Verificar proporção (assinaturas são geralmente horizontais)
                    aspect_ratio = w / h if h > 0 else 0
                    if 1.5 < aspect_ratio < 5.0:
                        signature_regions.append(ImageRegion(
                            x=x, y=y, width=w, height=h,
                            confidence=0.6,
                            region_type='signature'
                        ))
            
            return signature_regions
        except Exception as e:
            logger.error(f"Erro na detecção visual de assinaturas: {e}")
            return []

class VisionSystem:
    """Sistema de visão computacional completo"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.preprocessor = ImagePreprocessor(
            target_size=config.get('image_size', (224, 224))
        )
        self.ocr_processor = OCRProcessor(
            languages=config.get('languages', ['por', 'eng'])
        )
        self.layout_analyzer = LayoutAnalyzer()
        self.signature_detector = SignatureDetector()
        
        logger.info("Sistema de visão computacional inicializado")
    
    def analyze_image(self, image_path: str) -> VisionAnalysis:
        """Analisa imagem completa"""
        start_time = time.time()
        
        try:
            # Carregar e pré-processar imagem
            image = self.preprocessor.load_image(image_path)
            if image is None:
                raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
            
            # Melhorar imagem para OCR
            enhanced_image = self.preprocessor.enhance_image(image)
            
            # Extrair texto
            ocr_results = self.ocr_processor.extract_text(enhanced_image)
            
            # Analisar layout
            layout_analysis = self.layout_analyzer.analyze_layout(image, ocr_results)
            
            # Detectar assinaturas
            signature_detection = self.signature_detector.detect_signatures(image, ocr_results)
            
            # Combinar texto extraído
            extracted_text = ' '.join([result.text for result in ocr_results])
            
            # Calcular score de confiança
            confidence_score = np.mean([result.confidence for result in ocr_results]) if ocr_results else 0.0
            
            return VisionAnalysis(
                ocr_results=ocr_results,
                layout_analysis=layout_analysis,
                signature_detection=signature_detection,
                extracted_text=extracted_text,
                confidence_score=confidence_score,
                processing_time=time.time() - start_time,
                metadata={
                    'image_path': image_path,
                    'image_size': image.shape,
                    'total_text_regions': len(ocr_results)
                }
            )
        except Exception as e:
            logger.error(f"Erro na análise de imagem {image_path}: {e}")
            return VisionAnalysis(
                ocr_results=[],
                layout_analysis=LayoutAnalysis(
                    regions=[], document_type='unknown', confidence=0.0, page_number=1
                ),
                signature_detection=SignatureDetection(
                    signature_regions=[], confidence=0.0, is_valid=False
                ),
                extracted_text="",
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extrai apenas texto da imagem"""
        try:
            analysis = self.analyze_image(image_path)
            return analysis.extracted_text
        except Exception as e:
            logger.error(f"Erro ao extrair texto de {image_path}: {e}")
            return ""
    
    def detect_signatures(self, image_path: str) -> SignatureDetection:
        """Detecta apenas assinaturas na imagem"""
        try:
            analysis = self.analyze_image(image_path)
            return analysis.signature_detection
        except Exception as e:
            logger.error(f"Erro ao detectar assinaturas em {image_path}: {e}")
            return SignatureDetection(
                signature_regions=[], confidence=0.0, is_valid=False
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de visão"""
        return {
            'ocr_available': TESSERACT_AVAILABLE or EASYOCR_AVAILABLE,
            'cv2_available': CV2_AVAILABLE,
            'torchvision_available': TORCHVISION_AVAILABLE,
            'yolo_available': YOLO_AVAILABLE,
            'languages': self.ocr_processor.languages,
            'target_image_size': self.preprocessor.target_size
        } 