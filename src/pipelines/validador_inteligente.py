#!/usr/bin/env python3
"""
Validador Inteligente - Usa a arquitetura completa da IA para validação
Implementa o fluxo RAG completo: Maestro -> Especialistas -> Síntese -> Decisão
"""

import logging
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidadorInteligente:
    """Validador que usa a arquitetura completa da IA para análise contextual"""
    
    def __init__(self, barramento_conhecimento=None):
        self.barramento = barramento_conhecimento
        self.genome_config = self._carregar_genome()
        self.especialistas = self._inicializar_especialistas()
    
    def validar_resposta_contextual(self, resposta: str, pergunta_id: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Valida qualquer resposta usando análise contextual da IA"""
        try:
            logger.info(f"[IA-VALIDAÇÃO] Analisando resposta '{resposta}' para pergunta '{pergunta_id}'")
            
            # Prompt para análise contextual inteligente
            prompt_analise = f"""
ANÁLISE CONTEXTUAL DE RESPOSTA - SISTEMA GIC

PERGUNTA: {pergunta_id}
RESPOSTA DO USUÁRIO: "{resposta}"
CONTEXTO: {json.dumps(contexto, indent=2)}

MISSÃO: Analise se esta resposta é adequada para um sistema de justificativas contratuais profissionais.

CRITÉRIOS DE ANÁLISE:
1. ADEQUAÇÃO TÉCNICA: A resposta contém informação técnica relevante?
2. ESPECIFICIDADE: A resposta é específica ou vaga demais?
3. PROFISSIONALISMO: A resposta atende padrões profissionais?
4. COMPLETUDE: A resposta fornece informação suficiente?
5. CONTEXTO: A resposta faz sentido no contexto da pergunta?

RESPONDA EM JSON:
{{
    "valida": true/false,
    "score_confianca": 0.0-1.0,
    "motivo": "Explicação detalhada da decisão",
    "sugestao": "Como melhorar a resposta",
    "analise_detalhada": {{
        "adequacao_tecnica": "análise",
        "especificidade": "análise", 
        "profissionalismo": "análise",
        "completude": "análise",
        "contexto": "análise"
    }},
    "pergunta_reformulada": "Pergunta reformulada se necessário"
}}
"""
            
            # Consultar IA via barramento
            if self.barramento:
                resultado_ia = self.barramento.processar_consulta(prompt_analise)
                
                # Tentar parsear JSON da resposta da IA
                try:
                    if isinstance(resultado_ia, str):
                        # Extrair JSON da resposta
                        inicio_json = resultado_ia.find('{')
                        fim_json = resultado_ia.rfind('}') + 1
                        if inicio_json >= 0 and fim_json > inicio_json:
                            json_str = resultado_ia[inicio_json:fim_json]
                            resultado_parsed = json.loads(json_str)
                        else:
                            raise ValueError("JSON não encontrado na resposta")
                    else:
                        resultado_parsed = resultado_ia
                    
                    logger.info(f"[IA-VALIDAÇÃO] IA decidiu: {resultado_parsed.get('valida')} (confiança: {resultado_parsed.get('score_confianca')})")
                    return resultado_parsed
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"[IA-VALIDAÇÃO] Erro ao parsear resposta da IA: {e}")
                    # Fallback: analisar se IA rejeitou textualmente
                    if any(palavra in str(resultado_ia).lower() for palavra in ['inadequada', 'inválida', 'rejeitada', 'insuficiente']):
                        return {
                            "valida": False,
                            "score_confianca": 0.7,
                            "motivo": "IA identificou resposta inadequada",
                            "sugestao": "Forneça resposta técnica específica e detalhada",
                            "analise_detalhada": {"ia_textual": str(resultado_ia)[:200]},
                            "pergunta_reformulada": "Resposta técnica profissional obrigatória"
                        }
            
            # Fallback se IA não disponível: análise básica
            return self._analise_basica_fallback(resposta, pergunta_id)
            
        except Exception as e:
            logger.error(f"[IA-VALIDAÇÃO] Erro na validação contextual: {e}")
            return self._analise_basica_fallback(resposta, pergunta_id)
    
    def _analise_basica_fallback(self, resposta: str, pergunta_id: str) -> Dict[str, Any]:
        """Análise básica quando IA não está disponível"""
        resposta_limpa = resposta.strip().lower()
        
        # Apenas rejeitar respostas extremamente inadequadas
        if len(resposta_limpa) <= 1 or resposta_limpa in ['sim', 'não', 'ok', 'a', 'b', 'c', 'd', 'e']:
            return {
                "valida": False,
                "score_confianca": 0.9,
                "motivo": f"Resposta '{resposta}' é inadequada para justificativa contratual",
                "sugestao": "Forneça descrição técnica específica da situação",
                "analise_detalhada": {"fallback": "IA indisponível - análise básica"},
                "pergunta_reformulada": "Descrição técnica detalhada obrigatória"
            }
        
        # Aceitar outras respostas (deixar IA principal decidir)
        return {
            "valida": True,
            "score_confianca": 0.5,
            "motivo": "Análise básica - resposta aceita",
            "sugestao": "",
            "analise_detalhada": {"fallback": "IA indisponível"},
            "pergunta_reformulada": ""
        }
        
    def _carregar_genome(self) -> Dict:
        """Carrega configuração do genome.yaml"""
        try:
            genome_path = Path(__file__).parent.parent / "genomes" / "genome_1.0.0_gen_1.yaml"
            if genome_path.exists():
                with open(genome_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("Genome não encontrado, usando configuração padrão")
                return self._genome_padrao()
        except Exception as e:
            logger.error(f"Erro ao carregar genome: {e}")
            return self._genome_padrao()
    
    def _genome_padrao(self) -> Dict:
        """Configuração padrão baseada no genome.yaml"""
        return {
            'specialists': {
                'maestro': {
                    'name': 'Agente Maestro',
                    'description': 'Orquestrador que coordena os especialistas',
                    'confidence_threshold': 0.9,
                    'max_tokens': 3000
                },
                'jurist': {
                    'name': 'Agente Jurista', 
                    'description': 'Especialista em análise de riscos legais e cláusulas contratuais',
                    'confidence_threshold': 0.8,
                    'max_tokens': 2000
                },
                'financial': {
                    'name': 'Agente Financeiro',
                    'description': 'Especialista em análise de dados financeiros e numéricos', 
                    'confidence_threshold': 0.85,
                    'max_tokens': 1500
                },
                'reviewer': {
                    'name': 'Agente Revisor',
                    'description': 'Especialista em clareza, coesão e gramática',
                    'confidence_threshold': 0.75,
                    'max_tokens': 1000
                },
                'skeptic': {
                    'name': 'Agente Cético',
                    'description': 'Advogado do diabo - encontra falhas no raciocínio',
                    'confidence_threshold': 0.7,
                    'max_tokens': 1200
                }
            }
        }
    
    def _inicializar_especialistas(self) -> Dict:
        """Inicializa os especialistas baseado no genome"""
        especialistas = {}
        for key, config in self.genome_config.get('specialists', {}).items():
            especialistas[key] = {
                'nome': config.get('name', f'Agente {key.title()}'),
                'descricao': config.get('description', ''),
                'confianca_minima': config.get('confidence_threshold', 0.7),
                'max_tokens': config.get('max_tokens', 1500)
            }
        return especialistas
    
    def validar_fato_superveniente_inteligente(self, resposta: str, contexto: Dict = None) -> Dict[str, Any]:
        """
        Validação INTELIGENTE usando fluxo RAG completo:
        1. Maestro analisa a pergunta e contexto
        2. Especialistas fazem análises específicas
        3. Síntese final com decisão fundamentada
        """
        
        logger.info(f"[VALIDAÇÃO-IA] Iniciando análise inteligente para: '{resposta}'")
        
        try:
            # ETAPA 1: Maestro orquestra a análise
            analise_maestro = self._maestro_analisar_contexto(resposta, contexto)
            
            # ETAPA 2: Especialistas fazem análises específicas
            analises_especialistas = self._executar_analises_especialistas(resposta, analise_maestro)
            
            # ETAPA 3: Síntese final e decisão
            decisao_final = self._sintetizar_decisao_final(resposta, analises_especialistas)
            
            logger.info(f"[VALIDAÇÃO-IA] Decisão final: {'APROVADA' if decisao_final['valida'] else 'REJEITADA'}")
            
            return decisao_final
            
        except Exception as e:
            logger.error(f"[VALIDAÇÃO-IA] Erro na análise inteligente: {e}")
            # Fallback para validação simples
            return self._validacao_fallback(resposta)
    
    def _maestro_analisar_contexto(self, resposta: str, contexto: Dict = None) -> Dict:
        """Maestro analisa o contexto e define estratégia de validação"""
        
        prompt_maestro = f"""
        ANÁLISE CONTEXTUAL - MAESTRO
        
        Você é o Agente Maestro, responsável por orquestrar a validação de respostas para aditivos contratuais.
        
        RESPOSTA DO USUÁRIO: "{resposta}"
        CONTEXTO: {json.dumps(contexto or {}, ensure_ascii=False, indent=2)}
        
        TAREFA: Analise esta resposta para "fato superveniente" e defina:
        
        1. CLASSIFICAÇÃO INICIAL:
           - É uma resposta técnica válida?
           - Contém informações específicas?
           - Demonstra conhecimento do assunto?
        
        2. PONTOS DE ANÁLISE PARA ESPECIALISTAS:
           - Jurista: Aspectos legais e contratuais
           - Financeiro: Impactos econômicos mencionados
           - Cético: Possíveis falhas ou inconsistências
           - Revisor: Clareza e completude
        
        3. ESTRATÉGIA DE VALIDAÇÃO:
           - Nível de rigor necessário
           - Critérios específicos a verificar
        
        Responda em JSON:
        {{
            "classificacao_inicial": "tecnica|vaga|inadequada",
            "confianca_inicial": 0.0-1.0,
            "pontos_analise": {{
                'jurist': ["ponto1", "ponto2"],
                'financial': ["ponto1", "ponto2"],
                'legal': ["ponto1", "ponto2"],
                'contract': ["ponto1", "ponto2"],
                'reviewer': ["ponto1", "ponto2"],
                'skeptic': ["ponto1", "ponto2"]
            }},
            "estrategia": "rigorosa|moderada|basica",
            "observacoes": "observações do maestro"
        }}
        """
        
        if self.barramento:
            resultado = self.barramento.processar_consulta_especializada(
                prompt_maestro,
                tipo_consulta="maestro_validacao_contexto"
            )
            
            if resultado:
                try:
                    # Extrair JSON da resposta
                    inicio = resultado.find('{')
                    fim = resultado.rfind('}') + 1
                    if inicio >= 0 and fim > inicio:
                        json_str = resultado[inicio:fim]
                        return json.loads(json_str)
                except Exception as e:
                    logger.warning(f"Erro ao processar resposta do Maestro: {e}")
        
        # Fallback: análise básica
        return {
            "classificacao_inicial": "vaga" if len(resposta) < 20 else "tecnica",
            "confianca_inicial": 0.3 if len(resposta) < 20 else 0.7,
            "estrategia": "rigorosa",
            "observacoes": "Análise básica - barramento indisponível"
        }
    
    def _executar_analises_especialistas(self, resposta: str, analise_maestro: Dict) -> Dict:
        """Executa análises específicas dos 7 especialistas"""
        
        analises = {}
        pontos_analise = analise_maestro.get('pontos_analise', {})
        
        # JURISTA: Análise de riscos legais e cláusulas
        analises['jurist'] = self._analise_jurista(resposta, pontos_analise.get('jurist', []))
        
        # FINANCEIRO: Análise de impactos econômicos
        analises['financial'] = self._analise_financeiro(resposta, pontos_analise.get('financial', []))
        
        # LEGAL: Conformidade legal e regulamentações
        analises['legal'] = self._analise_legal(resposta, pontos_analise.get('legal', []))
        
        # CONTRACT: Estrutura e análise de contratos
        analises['contract'] = self._analise_contract(resposta, pontos_analise.get('contract', []))
        
        # REVISOR: Análise de clareza e completude
        analises['reviewer'] = self._analise_revisor(resposta, pontos_analise.get('reviewer', []))
        
        # CÉTICO: Busca falhas e inconsistências
        analises['skeptic'] = self._analise_cetico(resposta, pontos_analise.get('skeptic', []))
        
        return analises
    
    def _analise_jurista(self, resposta: str, pontos_foco: List[str]) -> Dict:
        """Agente Jurista analisa aspectos legais"""
        
        prompt_jurista = f"""
        ANÁLISE JURÍDICA - FATO SUPERVENIENTE
        
        Você é o Agente Jurista especializado em contratos da Petrobras.
        
        RESPOSTA: "{resposta}"
        PONTOS DE FOCO: {pontos_foco}
        
        ANALISE:
        1. Esta resposta caracteriza um fato superveniente válido juridicamente?
        2. Contém elementos técnicos/legais necessários?
        3. É específica o suficiente para justificar um aditivo contratual?
        4. Há riscos legais em aceitar esta justificativa?
        
        Responda em JSON:
        {{
            "valida_juridicamente": true/false,
            "confianca": 0.0-1.0,
            "elementos_presentes": ["elemento1", "elemento2"],
            "elementos_ausentes": ["elemento1", "elemento2"],
            "riscos_identificados": ["risco1", "risco2"],
            "recomendacao": "aprovar|rejeitar|solicitar_esclarecimentos"
        }}
        """
        
        return self._executar_consulta_especialista(prompt_jurista, "jurista_validacao")
    
    def _analise_financeiro(self, resposta: str, pontos_foco: List[str]) -> Dict:
        """Agente Financeiro analisa impactos econômicos"""
        
        prompt_financeiro = f"""
        ANÁLISE FINANCEIRA - FATO SUPERVENIENTE
        
        Você é o Agente Financeiro especializado em contratos da Petrobras.
        
        RESPOSTA: "{resposta}"
        PONTOS DE FOCO: {pontos_foco}
        
        ANALISE:
        1. A resposta menciona impactos financeiros/econômicos?
        2. Há justificativa para alteração de valores contratuais?
        3. É possível quantificar o impacto mencionado?
        4. A justificativa é consistente com práticas financeiras?
        
        Responda em JSON:
        {{
            "impacto_financeiro_claro": true/false,
            "confianca": 0.0-1.0,
            "elementos_quantitativos": ["elemento1", "elemento2"],
            "consistencia_financeira": 0.0-1.0,
            "recomendacao": "aprovar|rejeitar|solicitar_detalhamento"
        }}
        """
        
        return self._executar_consulta_especialista(prompt_financeiro, "financeiro_validacao")
    
    def _analise_legal(self, resposta: str, pontos_foco: List[str]) -> Dict:
        """Agente Legal analisa conformidade legal e regulamentações"""
        
        prompt_legal = f"""
        ANÁLISE DE CONFORMIDADE LEGAL - FATO SUPERVENIENTE
        
        Você é o Agente Legal especializado em conformidade e regulamentações da Petrobras.
        
        RESPOSTA: "{resposta}"
        PONTOS DE FOCO: {pontos_foco}
        
        ANALISE:
        1. A resposta está em conformidade com regulamentações vigentes?
        2. Há aspectos regulatórios que precisam ser considerados?
        3. Existem normas específicas aplicáveis ao caso?
        4. A justificativa atende requisitos legais mínimos?
        
        Responda em JSON:
        {{
            "conformidade_regulatoria": true/false,
            "confianca": 0.0-1.0,
            "normas_aplicaveis": ["norma1", "norma2"],
            "requisitos_atendidos": ["req1", "req2"],
            "alertas_regulatorios": ["alerta1", "alerta2"],
            "recomendacao": "aprovar|rejeitar|verificar_normas"
        }}
        """
        
        return self._executar_consulta_especialista(prompt_legal, "legal_validacao")
    
    def _analise_contract(self, resposta: str, pontos_foco: List[str]) -> Dict:
        """Agente Contract analisa estrutura e aspectos contratuais"""
        
        prompt_contract = f"""
        ANÁLISE CONTRATUAL - FATO SUPERVENIENTE
        
        Você é o Agente Contract especializado em estrutura e análise de contratos da Petrobras.
        
        RESPOSTA: "{resposta}"
        PONTOS DE FOCO: {pontos_foco}
        
        ANALISE:
        1. A resposta caracteriza adequadamente um fato superveniente contratual?
        2. Há elementos estruturais necessários para aditivo?
        3. A justificativa é consistente com práticas contratuais?
        4. Existem cláusulas contratuais relevantes ao caso?
        
        Responda em JSON:
        {{
            "adequacao_contratual": true/false,
            "confianca": 0.0-1.0,
            "elementos_estruturais": ["elemento1", "elemento2"],
            "clausulas_relevantes": ["clausula1", "clausula2"],
            "consistencia_praticas": 0.0-1.0,
            "recomendacao": "aprovar|rejeitar|revisar_clausulas"
        }}
        """
        
        return self._executar_consulta_especialista(prompt_contract, "contract_validacao")
    
    def _analise_cetico(self, resposta: str, pontos_foco: List[str]) -> Dict:
        """Agente Cético busca falhas e inconsistências"""
        
        prompt_cetico = f"""
        ANÁLISE CRÍTICA - FATO SUPERVENIENTE
        
        Você é o Agente Cético, advogado do diabo que encontra falhas no raciocínio.
        
        RESPOSTA: "{resposta}"
        PONTOS DE FOCO: {pontos_foco}
        
        BUSQUE FALHAS:
        1. A resposta é vaga ou genérica demais?
        2. Há contradições internas?
        3. Faltam informações críticas?
        4. Pode ser uma resposta "copiada" ou sem análise?
        5. Há sinais de que o usuário não entende o conceito?
        
        Responda em JSON:
        {{
            "falhas_identificadas": ["falha1", "falha2"],
            "nivel_criticidade": "baixo|medio|alto",
            "confianca_critica": 0.0-1.0,
            "sinais_copia": true/false,
            "recomendacao": "aprovar|rejeitar|questionar_mais"
        }}
        """
        
        return self._executar_consulta_especialista(prompt_cetico, "cetico_validacao")
    
    def _analise_revisor(self, resposta: str, pontos_foco: List[str]) -> Dict:
        """Agente Revisor analisa clareza e completude"""
        
        prompt_revisor = f"""
        ANÁLISE DE QUALIDADE - FATO SUPERVENIENTE
        
        Você é o Agente Revisor especializado em clareza e completude.
        
        RESPOSTA: "{resposta}"
        PONTOS DE FOCO: {pontos_foco}
        
        ANALISE:
        1. A resposta é clara e bem estruturada?
        2. Contém informações suficientes?
        3. A linguagem é adequada para contexto contratual?
        4. Há completude na descrição do fato?
        
        Responda em JSON:
        {{
            "clareza": 0.0-1.0,
            "completude": 0.0-1.0,
            "adequacao_linguagem": 0.0-1.0,
            "score_qualidade": 0.0-1.0,
            "melhorias_sugeridas": ["melhoria1", "melhoria2"],
            "recomendacao": "aprovar|melhorar|reescrever"
        }}
        """
        
        return self._executar_consulta_especialista(prompt_revisor, "revisor_validacao")
    
    def _executar_consulta_especialista(self, prompt: str, tipo_consulta: str) -> Dict:
        """Executa consulta para um especialista específico"""
        
        if self.barramento:
            resultado = self.barramento.processar_consulta_especializada(prompt, tipo_consulta)
            
            if resultado:
                try:
                    inicio = resultado.find('{')
                    fim = resultado.rfind('}') + 1
                    if inicio >= 0 and fim > inicio:
                        json_str = resultado[inicio:fim]
                        return json.loads(json_str)
                except Exception as e:
                    logger.warning(f"Erro ao processar resposta do especialista {tipo_consulta}: {e}")
        
        # Fallback básico
        return {
            "confianca": 0.5,
            "recomendacao": "solicitar_esclarecimentos",
            "observacao": "Análise básica - especialista indisponível"
        }
    
    def _sintetizar_decisao_final(self, resposta: str, analises: Dict) -> Dict[str, Any]:
        """Síntese final das análises dos especialistas"""
        
        # Coletar recomendações
        recomendacoes = []
        confiancas = []
        
        for especialista, analise in analises.items():
            rec = analise.get('recomendacao', 'solicitar_esclarecimentos')
            conf = analise.get('confianca', 0.5)
            
            recomendacoes.append(rec)
            confiancas.append(conf)
        
        # Calcular score geral
        score_medio = sum(confiancas) / len(confiancas) if confiancas else 0.5
        
        # Decisão baseada em consenso
        aprovacoes = sum(1 for rec in recomendacoes if 'aprovar' in rec)
        rejeicoes = sum(1 for rec in recomendacoes if 'rejeitar' in rec)
        
        # Critérios de decisão
        valida = False
        motivo = ""
        sugestao = ""
        
        if aprovacoes >= 3 and score_medio >= 0.7:
            valida = True
            motivo = "Resposta aprovada pelos especialistas"
        elif rejeicoes >= 2 or score_medio < 0.4:
            valida = False
            motivo = "Resposta rejeitada - não atende critérios técnicos"
            sugestao = self._gerar_sugestao_melhorias(analises)
        else:
            valida = False
            motivo = "Resposta necessita esclarecimentos adicionais"
            sugestao = "Forneça mais detalhes técnicos específicos sobre o fato superveniente"
        
        return {
            'valida': valida,
            'motivo': motivo,
            'sugestao': sugestao,
            'score_confianca': score_medio,
            'analises_detalhadas': analises,
            'timestamp': datetime.now().isoformat()
        }
    
    def _gerar_sugestao_melhorias(self, analises: Dict) -> str:
        """Gera sugestão baseada nas análises dos especialistas"""
        
        sugestoes = []
        
        # Coletar sugestões dos especialistas
        for especialista, analise in analises.items():
            if 'melhorias_sugeridas' in analise:
                sugestoes.extend(analise['melhorias_sugeridas'])
            elif 'elementos_ausentes' in analise:
                sugestoes.extend([f"Incluir: {elem}" for elem in analise['elementos_ausentes']])
        
        if sugestoes:
            return "Melhorias necessárias: " + "; ".join(sugestoes[:3])
        else:
            return "Descreva especificamente a situação técnica/operacional que justifica o aditivo"
    
    def _validacao_fallback(self, resposta: str) -> Dict[str, Any]:
        """Validação de fallback quando IA não está disponível"""
        
        # Validação básica similar à implementada anteriormente
        respostas_invalidas = [
            'não sei', 'nao sei', 'sei la', 'sei lá', 'acredito nisso', 
            'acho que', 'talvez', 'pode ser', 'isso', 'nisso'
        ]
        
        resposta_limpa = resposta.lower().strip()
        
        if resposta_limpa in respostas_invalidas or len(resposta) < 20:
            return {
                'valida': False,
                'motivo': 'Resposta inadequada para fato superveniente',
                'sugestao': 'Descreva especificamente a situação técnica que justifica o aditivo',
                'score_confianca': 0.1,
                'modo': 'fallback'
            }
        
        return {
            'valida': True,
            'score_confianca': 0.6,
            'modo': 'fallback'
        }
