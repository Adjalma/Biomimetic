"""
IA Especializada em Análise de Contratos e Justificativas
========================================================

Sistema autoevolutivo para análise de documentos jurídicos e administrativos.
"""

import sys
import os
import re
import json
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Tuple
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalisadorContratos:
    """Analisador especializado em contratos e justificativas"""
    
    def __init__(self):
        self.vocabulario_juridico = self._carregar_vocabulario_juridico()
        self.padroes_contratos = self._carregar_padroes_contratos()
        self.classificadores = self._inicializar_classificadores()
        
    def _carregar_vocabulario_juridico(self) -> Dict[str, List[str]]:
        """Carrega vocabulário jurídico especializado"""
        return {
            'contratos': [
                'contrato', 'acordo', 'convenção', 'pacto', 'termo', 'cláusula',
                'obrigações', 'direitos', 'responsabilidades', 'vigência',
                'rescindir', 'prorrogar', 'aditivo', 'emenda', 'modificação',
                'fornecedor', 'contratante', 'contratado', 'valor', 'prazo',
                'multa', 'penalidade', 'garantia', 'caução', 'fiança'
            ],
            'aditivos': [
                'aditivo', 'emenda', 'modificação', 'alteração', 'prorrogação',
                'ampliação', 'redução', 'suspensão', 'rescisão', 'novo prazo',
                'novo valor', 'nova cláusula', 'supressão', 'inclusão',
                'substituição', 'revisão', 'atualização', 'correção'
            ],
            'justificativas': [
                'justificativa', 'fundamentação', 'motivação', 'justificativa',
                'necessidade', 'interesse público', 'conveniência', 'oportunidade',
                'urgência', 'excepcionalidade', 'singularidade', 'especificidade',
                'técnica', 'econômica', 'operacional', 'estratégica',
                'legal', 'regulatória', 'normativa', 'institucional'
            ],
            'riscos': [
                'risco', 'perigo', 'ameaça', 'vulnerabilidade', 'exposição',
                'probabilidade', 'impacto', 'severidade', 'mitigação',
                'prevenção', 'contingência', 'plano de ação', 'monitoramento'
            ],
            'compliance': [
                'compliance', 'conformidade', 'legalidade', 'licitude',
                'regularidade', 'legitimidade', 'adequação', 'observância',
                'cumprimento', 'obediência', 'respeito', 'submissão',
                'norma', 'regulamento', 'legislação', 'estatuto'
            ]
        }
    
    def _carregar_padroes_contratos(self) -> Dict[str, List[str]]:
        """Carrega padrões de reconhecimento de contratos"""
        return {
            'identificacao_contrato': [
                r'contrato\s+n[º°]\s*\d+',
                r'acordo\s+de\s+coopera[çc][ãa]o',
                r'termo\s+de\s+compromisso',
                r'conven[çc][ãa]o\s+administrativa'
            ],
            'valores': [
                r'valor\s+de\s+R?\$?\s*[\d.,]+',
                r'pre[çc]o\s+total\s+de\s+R?\$?\s*[\d.,]+',
                r'valor\s+contratual\s+de\s+R?\$?\s*[\d.,]+'
            ],
            'prazos': [
                r'prazo\s+de\s+(\d+)\s+(dias?|meses?|anos?)',
                r'vig[êe]ncia\s+de\s+(\d+)\s+(dias?|meses?|anos?)',
                r'dura[çc][ãa]o\s+de\s+(\d+)\s+(dias?|meses?|anos?)'
            ],
            'aditivos': [
                r'aditivo\s+n[º°]\s*\d+',
                r'emenda\s+n[º°]\s*\d+',
                r'modifica[çc][ãa]o\s+n[º°]\s*\d+'
            ],
            'justificativas': [
                r'justificativa[s]?\s*:',
                r'fundamenta[çc][ãa]o\s*:',
                r'motiva[çc][ãa]o\s*:',
                r'considerando[s]?\s*:'
            ]
        }
    
    def _inicializar_classificadores(self) -> Dict[str, Any]:
        """Inicializa classificadores especializados"""
        return {
            'tipo_documento': self._criar_classificador_tipo(),
            'risco': self._criar_classificador_risco(),
            'compliance': self._criar_classificador_compliance(),
            'qualidade': self._criar_classificador_qualidade()
        }
    
    def _criar_classificador_tipo(self) -> nn.Module:
        """Cria classificador de tipo de documento"""
        return nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 5),  # contrato, aditivo, justificativa, risco, outros
            nn.Softmax(dim=1)
        )
    
    def _criar_classificador_risco(self) -> nn.Module:
        """Cria classificador de risco"""
        return nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 4),  # baixo, médio, alto, crítico
            nn.Softmax(dim=1)
        )
    
    def _criar_classificador_compliance(self) -> nn.Module:
        """Cria classificador de compliance"""
        return nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 3),  # conform, não conform, parcial
            nn.Softmax(dim=1)
        )
    
    def _criar_classificador_qualidade(self) -> nn.Module:
        """Cria classificador de qualidade"""
        return nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 5),  # 1-5 estrelas
            nn.Softmax(dim=1)
        )

class ProcessadorDocumentos:
    """Processador de documentos jurídicos"""
    
    def __init__(self):
        self.analisador = AnalisadorContratos()
        self.embedding_model = self._carregar_embedding_model()
        
    def _carregar_embedding_model(self):
        """Carrega modelo de embedding para textos jurídicos"""
        # Simulação de modelo de embedding
        class EmbeddingModel:
            def __init__(self):
                self.dim = 512
                
            def encode(self, text: str) -> np.ndarray:
                """Codifica texto em vetor"""
                # Simulação de embedding
                return np.random.randn(self.dim)
        
        return EmbeddingModel()
    
    def processar_documento(self, texto: str) -> Dict[str, Any]:
        """Processa documento completo"""
        resultado = {
            'tipo_documento': self.classificar_tipo_documento(texto),
            'extracao_info': self.extrair_informacoes(texto),
            'analise_risco': self.analisar_risco(texto),
            'compliance': self.verificar_compliance(texto),
            'qualidade': self.avaliar_qualidade(texto),
            'recomendacoes': self.gerar_recomendacoes(texto),
            'pontos_atencao': self.identificar_pontos_atencao(texto)
        }
        
        return resultado
    
    def classificar_tipo_documento(self, texto: str) -> Dict[str, float]:
        """Classifica o tipo de documento"""
        embedding = self.embedding_model.encode(texto)
        embedding_tensor = torch.FloatTensor(embedding).unsqueeze(0)
        
        with torch.no_grad():
            output = self.analisador.classificadores['tipo_documento'](embedding_tensor)
            probs = output.squeeze().numpy()
        
        tipos = ['contrato', 'aditivo', 'justificativa', 'risco', 'outros']
        return dict(zip(tipos, probs))
    
    def extrair_informacoes(self, texto: str) -> Dict[str, Any]:
        """Extrai informações específicas do documento"""
        info = {
            'valores': self._extrair_valores(texto),
            'prazos': self._extrair_prazos(texto),
            'partes': self._extrair_partes(texto),
            'objeto': self._extrair_objeto(texto),
            'clausulas_importantes': self._extrair_clausulas(texto)
        }
        
        return info
    
    def _extrair_valores(self, texto: str) -> List[Dict[str, str]]:
        """Extrai valores monetários"""
        valores = []
        padroes = self.analisador.padroes_contratos['valores']
        
        for padrao in padroes:
            matches = re.finditer(padrao, texto, re.IGNORECASE)
            for match in matches:
                valores.append({
                    'valor': match.group(),
                    'posicao': match.start(),
                    'contexto': texto[max(0, match.start()-50):match.end()+50]
                })
        
        return valores
    
    def _extrair_prazos(self, texto: str) -> List[Dict[str, str]]:
        """Extrai prazos e vigências"""
        prazos = []
        padroes = self.analisador.padroes_contratos['prazos']
        
        for padrao in padroes:
            matches = re.finditer(padrao, texto, re.IGNORECASE)
            for match in matches:
                prazos.append({
                    'prazo': match.group(),
                    'posicao': match.start(),
                    'contexto': texto[max(0, match.start()-50):match.end()+50]
                })
        
        return prazos
    
    def _extrair_partes(self, texto: str) -> List[str]:
        """Extrai partes envolvidas"""
        # Padrões para identificar partes
        padroes_partes = [
            r'contratante[s]?\s*:\s*([^,\n]+)',
            r'contratado[s]?\s*:\s*([^,\n]+)',
            r'fornecedor[es]?\s*:\s*([^,\n]+)',
            r'prestador[es]?\s*:\s*([^,\n]+)'
        ]
        
        partes = []
        for padrao in padroes_partes:
            matches = re.finditer(padrao, texto, re.IGNORECASE)
            for match in matches:
                partes.append(match.group(1).strip())
        
        return partes
    
    def _extrair_objeto(self, texto: str) -> str:
        """Extrai objeto do contrato"""
        padroes_objeto = [
            r'objeto\s*:\s*([^.\n]+)',
            r'finalidade\s*:\s*([^.\n]+)',
            r'escopo\s*:\s*([^.\n]+)'
        ]
        
        for padrao in padroes_objeto:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Objeto não identificado"
    
    def _extrair_clausulas(self, texto: str) -> List[Dict[str, str]]:
        """Extrai cláusulas importantes"""
        clausulas = []
        
        # Padrões de cláusulas importantes
        padroes_clausulas = [
            r'cl[áa]usula\s+\d+[^.]*\.',
            r'penalidade[s]?\s*[^.]*\.',
            r'multa[s]?\s*[^.]*\.',
            r'garantia[s]?\s*[^.]*\.',
            r'rescis[ãa]o\s*[^.]*\.'
        ]
        
        for padrao in padroes_clausulas:
            matches = re.finditer(padrao, texto, re.IGNORECASE)
            for match in matches:
                clausulas.append({
                    'tipo': self._classificar_clausula(match.group()),
                    'texto': match.group(),
                    'posicao': match.start()
                })
        
        return clausulas
    
    def _classificar_clausula(self, texto: str) -> str:
        """Classifica o tipo de cláusula"""
        texto_lower = texto.lower()
        
        if 'penalidade' in texto_lower or 'multa' in texto_lower:
            return 'penalidade'
        elif 'garantia' in texto_lower:
            return 'garantia'
        elif 'rescis' in texto_lower:
            return 'rescisao'
        elif 'prazo' in texto_lower:
            return 'prazo'
        else:
            return 'geral'
    
    def analisar_risco(self, texto: str) -> Dict[str, Any]:
        """Analisa riscos do documento"""
        embedding = self.embedding_model.encode(texto)
        embedding_tensor = torch.FloatTensor(embedding).unsqueeze(0)
        
        with torch.no_grad():
            output = self.analisador.classificadores['risco'](embedding_tensor)
            probs = output.squeeze().numpy()
        
        niveis = ['baixo', 'medio', 'alto', 'critico']
        risco_classificado = niveis[np.argmax(probs)]
        
        # Análise detalhada de riscos
        riscos_identificados = self._identificar_riscos_especificos(texto)
        
        return {
            'nivel_geral': risco_classificado,
            'probabilidades': dict(zip(niveis, probs)),
            'riscos_especificos': riscos_identificados,
            'score_risco': float(np.max(probs))
        }
    
    def _identificar_riscos_especificos(self, texto: str) -> List[Dict[str, str]]:
        """Identifica riscos específicos no texto"""
        riscos = []
        
        # Padrões de risco
        padroes_risco = [
            (r'prazo\s+muito\s+curto', 'Prazo inadequado'),
            (r'valor\s+muito\s+alto', 'Valor excessivo'),
            (r'sem\s+garantia', 'Falta de garantia'),
            (r'cl[áa]usula\s+aberta', 'Cláusula vaga'),
            (r'penalidade\s+excessiva', 'Penalidade desproporcional'),
            (r'rescis[ãa]o\s+unilateral', 'Rescisão unilateral'),
            (r'sem\s+fundamenta[çc][ãa]o', 'Falta de fundamentação')
        ]
        
        for padrao, descricao in padroes_risco:
            matches = re.finditer(padrao, texto, re.IGNORECASE)
            for match in matches:
                riscos.append({
                    'tipo': descricao,
                    'contexto': texto[max(0, match.start()-100):match.end()+100],
                    'posicao': match.start()
                })
        
        return riscos
    
    def verificar_compliance(self, texto: str) -> Dict[str, Any]:
        """Verifica compliance do documento"""
        embedding = self.embedding_model.encode(texto)
        embedding_tensor = torch.FloatTensor(embedding).unsqueeze(0)
        
        with torch.no_grad():
            output = self.analisador.classificadores['compliance'](embedding_tensor)
            probs = output.squeeze().numpy()
        
        niveis = ['conform', 'parcial', 'nao_conform']
        compliance_classificado = niveis[np.argmax(probs)]
        
        # Verificações específicas
        verificacoes = self._verificar_compliance_especifico(texto)
        
        return {
            'status_geral': compliance_classificado,
            'probabilidades': dict(zip(niveis, probs)),
            'verificacoes': verificacoes,
            'score_compliance': float(np.max(probs))
        }
    
    def _verificar_compliance_especifico(self, texto: str) -> Dict[str, bool]:
        """Verifica compliance específico"""
        verificacoes = {
            'tem_fundamentacao': bool(re.search(r'fundamenta[çc][ãa]o', texto, re.IGNORECASE)),
            'tem_justificativa': bool(re.search(r'justificativa', texto, re.IGNORECASE)),
            'tem_valor': bool(re.search(r'valor\s+de\s+R?\$?\s*[\d.,]+', texto)),
            'tem_prazo': bool(re.search(r'prazo\s+de\s+\d+', texto)),
            'tem_partes': bool(re.search(r'contratante|contratado', texto, re.IGNORECASE)),
            'tem_objeto': bool(re.search(r'objeto\s*:', texto, re.IGNORECASE))
        }
        
        return verificacoes
    
    def avaliar_qualidade(self, texto: str) -> Dict[str, Any]:
        """Avalia qualidade do documento"""
        embedding = self.embedding_model.encode(texto)
        embedding_tensor = torch.FloatTensor(embedding).unsqueeze(0)
        
        with torch.no_grad():
            output = self.analisador.classificadores['qualidade'](embedding_tensor)
            probs = output.squeeze().numpy()
        
        # Converter para estrelas (1-5)
        estrelas = np.argmax(probs) + 1
        
        # Análise de qualidade específica
        qualidade_especifica = self._avaliar_qualidade_especifica(texto)
        
        return {
            'estrelas': estrelas,
            'probabilidades': dict(zip(range(1, 6), probs)),
            'aspectos': qualidade_especifica,
            'score_qualidade': float(np.max(probs))
        }
    
    def _avaliar_qualidade_especifica(self, texto: str) -> Dict[str, float]:
        """Avalia aspectos específicos da qualidade"""
        aspectos = {
            'clareza': self._avaliar_clareza(texto),
            'completude': self._avaliar_completude(texto),
            'consistencia': self._avaliar_consistencia(texto),
            'precisao': self._avaliar_precisao(texto)
        }
        
        return aspectos
    
    def _avaliar_clareza(self, texto: str) -> float:
        """Avalia clareza do texto"""
        # Métricas simples de clareza
        palavras = texto.split()
        frases = texto.split('.')
        
        if len(palavras) == 0 or len(frases) == 0:
            return 0.0
        
        # Tamanho médio das frases (menor = mais claro)
        tamanho_medio_frases = len(palavras) / len(frases)
        
        # Score baseado no tamanho médio (ideal: 15-25 palavras)
        if 15 <= tamanho_medio_frases <= 25:
            return 1.0
        elif 10 <= tamanho_medio_frases <= 30:
            return 0.8
        elif 5 <= tamanho_medio_frases <= 40:
            return 0.6
        else:
            return 0.3
    
    def _avaliar_completude(self, texto: str) -> float:
        """Avalia completude do documento"""
        elementos_necessarios = [
            'objeto', 'valor', 'prazo', 'partes', 'fundamentacao'
        ]
        
        elementos_presentes = 0
        for elemento in elementos_necessarios:
            if re.search(elemento, texto, re.IGNORECASE):
                elementos_presentes += 1
        
        return elementos_presentes / len(elementos_necessarios)
    
    def _avaliar_consistencia(self, texto: str) -> float:
        """Avalia consistência do documento"""
        # Verificar inconsistências básicas
        inconsistencias = 0
        
        # Verificar se há valores duplicados ou conflitantes
        valores = re.findall(r'R?\$?\s*[\d.,]+', texto)
        if len(valores) != len(set(valores)):
            inconsistencias += 1
        
        # Verificar se há prazos conflitantes
        prazos = re.findall(r'prazo\s+de\s+\d+', texto)
        if len(prazos) > 1:
            inconsistencias += 0.5
        
        # Score baseado em inconsistências
        return max(0.0, 1.0 - inconsistencias * 0.3)
    
    def _avaliar_precisao(self, texto: str) -> float:
        """Avalia precisão do documento"""
        # Verificar elementos de precisão
        elementos_precisao = [
            r'\d{2}/\d{2}/\d{4}',  # datas
            r'R?\$?\s*[\d.,]+',    # valores
            r'n[º°]\s*\d+',        # números
            r'CNPJ\s*\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'  # CNPJ
        ]
        
        elementos_encontrados = 0
        for padrao in elementos_precisao:
            if re.search(padrao, texto):
                elementos_encontrados += 1
        
        return elementos_encontrados / len(elementos_precisao)
    
    def gerar_recomendacoes(self, texto: str) -> List[str]:
        """Gera recomendações para melhorar o documento"""
        recomendacoes = []
        
        # Verificar elementos faltantes
        if not re.search(r'fundamenta[çc][ãa]o', texto, re.IGNORECASE):
            recomendacoes.append("Adicionar fundamentação legal adequada")
        
        if not re.search(r'justificativa', texto, re.IGNORECASE):
            recomendacoes.append("Incluir justificativa técnica e econômica")
        
        if not re.search(r'valor\s+de\s+R?\$?\s*[\d.,]+', texto):
            recomendacoes.append("Especificar valor contratual claramente")
        
        if not re.search(r'prazo\s+de\s+\d+', texto):
            recomendacoes.append("Definir prazo de execução")
        
        if not re.search(r'penalidade', texto, re.IGNORECASE):
            recomendacoes.append("Incluir cláusula de penalidade")
        
        if not re.search(r'garantia', texto, re.IGNORECASE):
            recomendacoes.append("Estabelecer garantias contratuais")
        
        # Verificar qualidade do texto
        if len(texto.split()) < 100:
            recomendacoes.append("Expandir o conteúdo do documento")
        
        return recomendacoes
    
    def identificar_pontos_atencao(self, texto: str) -> List[Dict[str, str]]:
        """Identifica pontos que merecem atenção especial"""
        pontos = []
        
        # Padrões de atenção
        padroes_atencao = [
            (r'prazo\s+muito\s+curto', 'Prazo pode ser inadequado'),
            (r'valor\s+muito\s+alto', 'Valor pode ser excessivo'),
            (r'sem\s+garantia', 'Falta de garantia pode ser risco'),
            (r'cl[áa]usula\s+aberta', 'Cláusula pode ser muito vaga'),
            (r'rescis[ãa]o\s+unilateral', 'Rescisão unilateral pode ser problemática'),
            (r'sem\s+fundamenta[çc][ãa]o', 'Falta de fundamentação legal'),
            (r'contrato\s+verbal', 'Contrato verbal pode ser inválido')
        ]
        
        for padrao, descricao in padroes_atencao:
            matches = re.finditer(padrao, texto, re.IGNORECASE)
            for match in matches:
                pontos.append({
                    'tipo': descricao,
                    'contexto': texto[max(0, match.start()-50):match.end()+50],
                    'posicao': match.start(),
                    'severidade': 'alta' if 'muito' in match.group() else 'media'
                })
        
        return pontos

def criar_tarefas_contratos() -> List[Dict[str, Any]]:
    """Cria tarefas de treinamento para análise de contratos"""
    tarefas = [
        {
            'task_id': 'classificacao_tipo_documento',
            'type': 'classification',
            'input_data': np.random.randn(100, 512),
            'target_data': np.random.randint(0, 5, (100, 1)),
            'metadata': {
                'dificuldade': 0.6,
                'tipo': 'classificacao_documentos',
                'descricao': 'Classificar tipo de documento jurídico'
            }
        },
        {
            'task_id': 'analise_risco_contratos',
            'type': 'regression',
            'input_data': np.random.randn(100, 512),
            'target_data': np.random.randn(100, 1),
            'metadata': {
                'dificuldade': 0.8,
                'tipo': 'analise_risco',
                'descricao': 'Analisar nível de risco em contratos'
            }
        },
        {
            'task_id': 'verificacao_compliance',
            'type': 'classification',
            'input_data': np.random.randn(100, 512),
            'target_data': np.random.randint(0, 3, (100, 1)),
            'metadata': {
                'dificuldade': 0.7,
                'tipo': 'compliance',
                'descricao': 'Verificar compliance de documentos'
            }
        },
        {
            'task_id': 'avaliacao_qualidade',
            'type': 'regression',
            'input_data': np.random.randn(100, 512),
            'target_data': np.random.randn(100, 1),
            'metadata': {
                'dificuldade': 0.5,
                'tipo': 'qualidade',
                'descricao': 'Avaliar qualidade de documentos'
            }
        },
        {
            'task_id': 'extracao_informacoes',
            'type': 'nlp',
            'input_data': np.random.randn(100, 512),
            'target_data': np.random.randn(100, 1),
            'metadata': {
                'dificuldade': 0.9,
                'tipo': 'extracao',
                'descricao': 'Extrair informações específicas de contratos'
            }
        }
    ]
    
    return tarefas

# Função principal para uso
def analisar_documento_juridico(texto: str) -> Dict[str, Any]:
    """Função principal para análise de documento jurídico"""
    processador = ProcessadorDocumentos()
    return processador.processar_documento(texto)

def treinar_ia_contratos(ai_evolutionary):
    """Treina a IA com tarefas específicas de contratos"""
    tarefas = criar_tarefas_contratos()
    
    for tarefa in tarefas:
        ai_evolutionary.add_custom_task(tarefa)
        print(f"✅ Tarefa adicionada: {tarefa['task_id']}")
    
    # Evolução especializada
    print("🔄 Treinando IA para análise de contratos...")
    resultados = ai_evolutionary.start_evolution(generations=10)
    
    return resultados 