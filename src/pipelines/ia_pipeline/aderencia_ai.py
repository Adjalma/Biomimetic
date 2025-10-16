#!/usr/bin/env python3
"""
PIPELINE DE ANÁLISE DE ADERÊNCIA DE CONTRATOS
Versão 2.0 - Sistema avançado de análise jurídica
"""

import torch
import torch.nn as nn
import numpy as np
import json
import logging
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AderenciaAI:
    """Sistema de análise de aderência de contratos"""
    
    def __init__(self):
        self.model = self._create_analysis_model()
        self.compliance_rules = self._load_compliance_rules()
        self.risk_factors = self._load_risk_factors()
        self.legal_terms = self._load_legal_terms()
        
    def _create_analysis_model(self) -> nn.Module:
        """Cria modelo de análise"""
        class ContractAnalysisModel(nn.Module):
            def __init__(self, vocab_size=10000, embedding_dim=256, hidden_dim=512):
                super().__init__()
                self.embedding = nn.Embedding(vocab_size, embedding_dim)
                self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
                self.attention = nn.MultiheadAttention(hidden_dim * 2, num_heads=8)
                self.classifier = nn.Sequential(
                    nn.Linear(hidden_dim * 2, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(hidden_dim, 128),
                    nn.ReLU(),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, 32),
                    nn.ReLU(),
                    nn.Linear(32, 1),
                    nn.Sigmoid()
                )
                
            def forward(self, x):
                embedded = self.embedding(x)
                lstm_out, _ = self.lstm(embedded)
                attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
                pooled = torch.mean(attn_out, dim=1)
                output = self.classifier(pooled)
                return output
        
        return ContractAnalysisModel()
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Carrega regras de conformidade"""
        return {
            'lgpd': {
                'required_clauses': [
                    'proteção de dados pessoais',
                    'consentimento',
                    'finalidade do tratamento',
                    'direitos do titular',
                    'medidas de segurança'
                ],
                'weight': 0.3
            },
            'marco_civil': {
                'required_clauses': [
                    'neutralidade da rede',
                    'privacidade',
                    'proteção de dados',
                    'responsabilidade civil'
                ],
                'weight': 0.25
            },
            'código_defesa_consumidor': {
                'required_clauses': [
                    'direitos do consumidor',
                    'responsabilidade do fornecedor',
                    'prazo de garantia',
                    'cláusulas abusivas'
                ],
                'weight': 0.25
            },
            'direito_trabalhista': {
                'required_clauses': [
                    'jornada de trabalho',
                    'remuneração',
                    'benefícios',
                    'condições de trabalho',
                    'rescisão'
                ],
                'weight': 0.2
            }
        }
    
    def _load_risk_factors(self) -> Dict[str, float]:
        """Carrega fatores de risco"""
        return {
            'cláusulas_abusivas': 0.9,
            'penalidades_excessivas': 0.8,
            'limitação_responsabilidade': 0.7,
            'renúncia_direitos': 0.8,
            'arbitragem_obrigatória': 0.6,
            'foro_inconveniente': 0.7,
            'prazo_excessivo': 0.6,
            'multa_excessiva': 0.8,
            'confidencialidade_ampliada': 0.5,
            'não_concorrência': 0.6
        }
    
    def _load_legal_terms(self) -> Dict[str, List[str]]:
        """Carrega termos jurídicos"""
        return {
            'obrigações': [
                'dever', 'obrigação', 'responsabilidade', 'compromisso',
                'deverá', 'deverão', 'obrigatório', 'compulsório'
            ],
            'direitos': [
                'direito', 'faculdade', 'prerrogativa', 'liberdade',
                'poderá', 'poderão', 'autorizado', 'permitido'
            ],
            'penalidades': [
                'multa', 'penalidade', 'sanção', 'punição',
                'indenização', 'compensação', 'reparação'
            ],
            'prazos': [
                'prazo', 'vigência', 'duração', 'período',
                'data', 'vencimento', 'expiração'
            ],
            'rescisão': [
                'rescisão', 'termino', 'encerramento', 'extinção',
                'cancelamento', 'suspensão', 'interrupção'
            ]
        }
    
    def preprocess_contract(self, contract_text: str) -> Dict[str, Any]:
        """Pré-processa o contrato"""
        # Limpar texto
        cleaned_text = re.sub(r'\s+', ' ', contract_text.strip())
        
        # Extrair cláusulas
        clauses = self._extract_clauses(cleaned_text)
        
        # Análise de estrutura
        structure_analysis = self._analyze_structure(cleaned_text)
        
        # Análise de termos
        terms_analysis = self._analyze_terms(cleaned_text)
        
        return {
            'original_text': contract_text,
            'cleaned_text': cleaned_text,
            'clauses': clauses,
            'structure': structure_analysis,
            'terms': terms_analysis,
            'word_count': len(cleaned_text.split()),
            'clause_count': len(clauses)
        }
    
    def _extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Extrai cláusulas do contrato"""
        clauses = []
        
        # Padrões para identificar cláusulas
        patterns = [
            r'CLÁUSULA\s+(\d+)[\s\-:]+([^\.]+)',
            r'ARTIGO\s+(\d+)[\s\-:]+([^\.]+)',
            r'(\d+)\.\s+([^\.]+)',
            r'(\d+)\)\s+([^\.]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                clause_num = match.group(1)
                clause_title = match.group(2).strip()
                
                # Encontrar conteúdo da cláusula
                start_pos = match.end()
                end_pos = text.find('\n\n', start_pos)
                if end_pos == -1:
                    end_pos = len(text)
                
                clause_content = text[start_pos:end_pos].strip()
                
                clauses.append({
                    'number': clause_num,
                    'title': clause_title,
                    'content': clause_content,
                    'start_pos': start_pos,
                    'end_pos': end_pos
                })
        
        return clauses
    
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analisa estrutura do contrato"""
        # Verificar seções importantes
        sections = {
            'partes': bool(re.search(r'partes?|contratantes?', text, re.IGNORECASE)),
            'objeto': bool(re.search(r'objeto|finalidade|escopo', text, re.IGNORECASE)),
            'prazo': bool(re.search(r'prazo|vigência|duração', text, re.IGNORECASE)),
            'valor': bool(re.search(r'valor|preço|remuneração', text, re.IGNORECASE)),
            'obrigações': bool(re.search(r'obrigações?|deveres?', text, re.IGNORECASE)),
            'responsabilidades': bool(re.search(r'responsabilidades?', text, re.IGNORECASE)),
            'rescisão': bool(re.search(r'rescisão|termino|encerramento', text, re.IGNORECASE)),
            'foro': bool(re.search(r'foro|jurisdição|competência', text, re.IGNORECASE))
        }
        
        return {
            'has_essential_sections': sum(sections.values()) >= 6,
            'sections_present': sections,
            'completeness_score': sum(sections.values()) / len(sections)
        }
    
    def _analyze_terms(self, text: str) -> Dict[str, Any]:
        """Analisa termos jurídicos"""
        analysis = {}
        
        for category, terms in self.legal_terms.items():
            count = 0
            for term in terms:
                count += len(re.findall(rf'\b{term}\b', text, re.IGNORECASE))
            analysis[category] = count
        
        return analysis
    
    def check_compliance(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica conformidade com regulamentações"""
        compliance_results = {}
        total_score = 0.0
        total_weight = 0.0
        
        for regulation, rules in self.compliance_rules.items():
            score = 0.0
            required_clauses = rules['required_clauses']
            weight = rules['weight']
            
            # Verificar cláusulas obrigatórias
            for clause in required_clauses:
                if any(clause.lower() in c['content'].lower() for c in contract_data['clauses']):
                    score += 1.0
            
            # Normalizar score
            if required_clauses:
                score = score / len(required_clauses)
            
            compliance_results[regulation] = {
                'score': score,
                'weight': weight,
                'weighted_score': score * weight,
                'required_clauses': required_clauses,
                'found_clauses': [c for c in required_clauses if any(c.lower() in cl['content'].lower() for cl in contract_data['clauses'])]
            }
            
            total_score += score * weight
            total_weight += weight
        
        # Score geral de conformidade
        overall_compliance = total_score / total_weight if total_weight > 0 else 0.0
        
        return {
            'overall_compliance': overall_compliance,
            'regulations': compliance_results,
            'compliance_level': self._get_compliance_level(overall_compliance)
        }
    
    def assess_risk(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia riscos do contrato"""
        risk_score = 0.0
        risk_factors = []
        
        text = contract_data['cleaned_text'].lower()
        
        for factor, weight in self.risk_factors.items():
            if self._check_risk_factor(text, factor):
                risk_score += weight
                risk_factors.append({
                    'factor': factor,
                    'weight': weight,
                    'description': self._get_risk_description(factor)
                })
        
        # Normalizar score de risco (0-1)
        max_possible_risk = sum(self.risk_factors.values())
        normalized_risk = risk_score / max_possible_risk if max_possible_risk > 0 else 0.0
        
        return {
            'risk_score': normalized_risk,
            'risk_level': self._get_risk_level(normalized_risk),
            'risk_factors': risk_factors,
            'total_risk_weight': risk_score
        }
    
    def _check_risk_factor(self, text: str, factor: str) -> bool:
        """Verifica se um fator de risco está presente"""
        risk_patterns = {
            'cláusulas_abusivas': [
                r'renúncia.*direitos?',
                r'limitação.*responsabilidade',
                r'cláusula.*abusiva'
            ],
            'penalidades_excessivas': [
                r'multa.*excessiva',
                r'penalidade.*elevada',
                r'indenização.*alta'
            ],
            'limitação_responsabilidade': [
                r'limitação.*responsabilidade',
                r'responsabilidade.*limitada',
                r'exclusão.*responsabilidade'
            ],
            'renúncia_direitos': [
                r'renúncia.*direitos?',
                r'abrir.*mão.*direitos?',
                r'desistir.*direitos?'
            ],
            'arbitragem_obrigatória': [
                r'arbitragem.*obrigatória',
                r'foro.*arbitral',
                r'juízo.*arbitral'
            ],
            'foro_inconveniente': [
                r'foro.*inconveniente',
                r'jurisdição.*estrangeira',
                r'lei.*estrangeira'
            ],
            'prazo_excessivo': [
                r'prazo.*excessivo',
                r'vigência.*longa',
                r'duração.*prolongada'
            ],
            'multa_excessiva': [
                r'multa.*excessiva',
                r'penalidade.*alta',
                r'sanção.*elevada'
            ],
            'confidencialidade_ampliada': [
                r'confidencialidade.*permanente',
                r'sigilo.*indefinido',
                r'segredo.*perpetuo'
            ],
            'não_concorrência': [
                r'não.*concorrência',
                r'vedação.*concorrência',
                r'proibição.*concorrência'
            ]
        }
        
        if factor in risk_patterns:
            for pattern in risk_patterns[factor]:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        
        return False
    
    def _get_risk_description(self, factor: str) -> str:
        """Retorna descrição do fator de risco"""
        descriptions = {
            'cláusulas_abusivas': 'Presença de cláusulas que podem ser consideradas abusivas',
            'penalidades_excessivas': 'Penalidades ou multas com valores excessivos',
            'limitação_responsabilidade': 'Limitação excessiva de responsabilidade',
            'renúncia_direitos': 'Renúncia a direitos fundamentais',
            'arbitragem_obrigatória': 'Arbitragem obrigatória sem opção de foro comum',
            'foro_inconveniente': 'Foro ou jurisdição inconveniente para uma das partes',
            'prazo_excessivo': 'Prazos ou vigência excessivamente longos',
            'multa_excessiva': 'Multas ou penalidades com valores desproporcionais',
            'confidencialidade_ampliada': 'Confidencialidade com prazo excessivamente longo',
            'não_concorrência': 'Cláusulas de não concorrência restritivas'
        }
        return descriptions.get(factor, 'Fator de risco não identificado')
    
    def _get_compliance_level(self, score: float) -> str:
        """Retorna nível de conformidade"""
        if score >= 0.9:
            return 'EXCELENTE'
        elif score >= 0.8:
            return 'MUITO BOM'
        elif score >= 0.7:
            return 'BOM'
        elif score >= 0.6:
            return 'REGULAR'
        else:
            return 'INSUFICIENTE'
    
    def _get_risk_level(self, score: float) -> str:
        """Retorna nível de risco"""
        if score >= 0.8:
            return 'ALTO'
        elif score >= 0.5:
            return 'MÉDIO'
        elif score >= 0.2:
            return 'BAIXO'
        else:
            return 'MÍNIMO'
    
    def analisar_contrato(self, contract_text: str) -> Dict[str, Any]:
        """Análise completa do contrato"""
        logger.info("📄 Iniciando análise de contrato...")
        
        # Pré-processamento
        contract_data = self.preprocess_contract(contract_text)
        
        # Análise de conformidade
        compliance_analysis = self.check_compliance(contract_data)
        
        # Análise de risco
        risk_analysis = self.assess_risk(contract_data)
        
        # Resultado final
        result = {
            'contract_info': {
                'word_count': contract_data['word_count'],
                'clause_count': contract_data['clause_count'],
                'structure_completeness': contract_data['structure']['completeness_score']
            },
            'compliance_analysis': compliance_analysis,
            'risk_analysis': risk_analysis,
            'overall_assessment': {
                'compliance_score': compliance_analysis['overall_compliance'],
                'risk_score': risk_analysis['risk_score'],
                'recommendation': self._get_recommendation(
                    compliance_analysis['overall_compliance'],
                    risk_analysis['risk_score']
                )
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Análise concluída - Conformidade: {compliance_analysis['overall_compliance']:.2f}, Risco: {risk_analysis['risk_score']:.2f}")
        
        return result
    
    def _get_recommendation(self, compliance_score: float, risk_score: float) -> str:
        """Gera recomendação baseada na análise"""
        if compliance_score >= 0.8 and risk_score <= 0.3:
            return "APROVADO - Contrato em conformidade e baixo risco"
        elif compliance_score >= 0.7 and risk_score <= 0.5:
            return "APROVADO COM RESERVAS - Revisar pontos específicos"
        elif compliance_score >= 0.6 and risk_score <= 0.6:
            return "REVISÃO NECESSÁRIA - Ajustes recomendados"
        elif compliance_score < 0.6 or risk_score > 0.7:
            return "REJEITADO - Não atende requisitos mínimos"
        else:
            return "ANÁLISE ADICIONAL NECESSÁRIA"

def main():
    """Função principal para teste"""
    print("📄 SISTEMA DE ANÁLISE DE ADERÊNCIA DE CONTRATOS")
    print("=" * 50)
    
    # Criar sistema
    analyzer = AderenciaAI()
    
    # Contrato de teste
    test_contract = """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    
    CLÁUSULA 1 - OBJETO
    O presente contrato tem por objeto a prestação de serviços de consultoria técnica em conformidade com a LGPD.
    
    CLÁUSULA 2 - PRAZO
    O prazo de vigência será de 12 meses, podendo ser prorrogado por acordo entre as partes.
    
    CLÁUSULA 3 - VALOR
    O valor total será de R$ 50.000,00, pagos em 12 parcelas mensais.
    
    CLÁUSULA 4 - OBRIGAÇÕES
    O contratado se obriga a prestar os serviços com diligência e zelo profissional.
    
    CLÁUSULA 5 - RESPONSABILIDADES
    As responsabilidades serão limitadas ao valor do contrato.
    
    CLÁUSULA 6 - PROTEÇÃO DE DADOS
    As partes se comprometem a respeitar a LGPD e proteger dados pessoais.
    
    CLÁUSULA 7 - RESCISÃO
    O contrato poderá ser rescindido por qualquer das partes com aviso prévio de 30 dias.
    
    CLÁUSULA 8 - FORO
    Fica eleito o foro da comarca de São Paulo para dirimir quaisquer dúvidas.
    """
    
    # Analisar contrato
    result = analyzer.analisar_contrato(test_contract)
    
    # Exibir resultados
    print(f"\n📊 RESULTADOS DA ANÁLISE:")
    print(f"Conformidade: {result['overall_assessment']['compliance_score']:.2f}")
    print(f"Risco: {result['overall_assessment']['risk_score']:.2f}")
    print(f"Recomendação: {result['overall_assessment']['recommendation']}")
    
    print(f"\n📋 DETALHES:")
    print(f"Palavras: {result['contract_info']['word_count']}")
    print(f"Cláusulas: {result['contract_info']['clause_count']}")
    print(f"Completude estrutural: {result['contract_info']['structure_completeness']:.2f}")

if __name__ == "__main__":
    main() 