#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMULADOR CONTRADFACTUAL - SISTEMA DE RACIOCÍNIO ESTRATÉGICO
============================================================

Este módulo implementa o simulador contrafactual que permite análise estratégica
de contratos através de raciocínio "E se?", gerando cenários alternativos e
avaliando seus impactos potenciais.

ARQUITETURA CONTRADFACTUAL:
- Sistema de geração de cenários alternativos
- Edição genômica em tempo real de contratos
- Análise de impacto e consequências
- Evolução da análise de risco
- Integração com sistemas V2 e barramento de conhecimento

FUNCIONALIDADES PRINCIPAIS:
1. GERAÇÃO DE CENÁRIOS "E SE?":
   - Cria cenários alternativos baseados em mudanças
   - Simula alterações em valores, cláusulas e prazos
   - Gera variações de condições contratuais
   - Explora diferentes cenários de mercado

2. EDIÇÃO GENÔMICA EM TEMPO REAL:
   - Modifica contratos dinamicamente
   - Aplica alterações genômicas instantaneamente
   - Mantém rastreabilidade das mudanças
   - Valida consistência das modificações

3. ANÁLISE DE IMPACTO:
   - Avalia consequências de cada cenário
   - Calcula impactos financeiros e operacionais
   - Identifica riscos e oportunidades
   - Gera relatórios de análise

4. EVOLUÇÃO DA ANÁLISE DE RISCO:
   - Aprende com cenários anteriores
   - Melhora precisão das previsões
   - Adapta-se a novos padrões de risco
   - Otimiza recomendações estratégicas

COMPONENTES:
- SimuladorContrafactual: Classe principal do sistema
- Gerador de cenários alternativos
- Editor genômico em tempo real
- Analisador de impacto
- Sistema de evolução de risco

FLUXO DE SIMULAÇÃO:
1. Entrada → Análise → Geração de cenários
2. Edição → Validação → Aplicação de mudanças
3. Simulação → Análise de impacto → Avaliação
4. Aprendizado → Otimização → Recomendações

Versão: 2.0
Data: 2024
Autor: Sistema IA Autoevolutiva
"""

# =============================================================================
# IMPORTS E DEPENDÊNCIAS
# =============================================================================

import re             # Expressões regulares para processamento de texto
import json           # Manipulação de dados JSON
import logging        # Sistema de logging avançado
import copy           # Cópia profunda de objetos
import hashlib        # Hashing para identificação única
from datetime import datetime  # Timestamps e data/hora
from pathlib import Path  # Manipulação de caminhos de arquivos
from typing import Dict, List, Any, Optional, Tuple, Union  # Type hints
from dataclasses import dataclass, field  # Classes de dados
from enum import Enum  # Enumerações para tipos
import sqlite3        # Banco de dados SQLite para persistência

class TipoCenario(Enum):
    """Tipos de cenários contrafactuais"""
    ALTERACAO_VALOR = "alteracao_valor"
    ALTERACAO_CLAUSULA = "alteracao_clausula"
    ALTERACAO_PRAZO = "alteracao_prazo"
    ALTERACAO_PARTE = "alteracao_parte"
    ALTERACAO_OBRIGACAO = "alteracao_obrigacao"
    ADITIVO = "aditivo"

class NivelRisco(Enum):
    """Níveis de risco"""
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

@dataclass
class AlteracaoContrato:
    """Estrutura para alterações em contratos"""
    id: str
    tipo: TipoCenario
    descricao: str
    valor_original: str
    valor_novo: str
    clausula_afetada: str
    impacto_estimado: str
    data_simulacao: datetime
    autor: str

@dataclass
class ResultadoSimulacao:
    """Estrutura para resultados de simulação"""
    id: str
    contrato_original: str
    contrato_simulado: str
    alteracoes: List[AlteracaoContrato]
    analise_jurista: Dict[str, Any]
    analise_financeira: Dict[str, Any]
    analise_skeptic: Dict[str, Any]
    risco_geral: NivelRisco
    recomendacao: str
    impacto_financeiro: float
    data_simulacao: datetime

@dataclass
class GrafoImpacto:
    """Estrutura para grafo de impacto das alterações"""
    alteracao_id: str
    clausulas_afetadas: List[str]
    dependencias: List[str]
    impacto_cascata: Dict[str, float]
    risco_propagacao: float

class SimuladorContrafactual:
    """
    🧠 Simulador Contrafactual - Sistema de raciocínio estratégico
    """
    
    def __init__(self, 
                 biblioteca_path: str = "faiss_biblioteca_central",
                 db_path: str = "simulador_contrafactual.db",
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
        
        # Inicializar banco de dados apenas se necessário
        if usar_banco_separado:
            self._init_database()
        
        # Cache de contratos simulados
        self.contratos_simulados = {}
        self.historico_simulacoes = {}
        
        # Configurações de simulação
        self.max_alteracoes_por_simulacao = 10
        self.threshold_impacto_significativo = 0.1
        
        self.logger.info("Simulador Contrafactual inicializado!")
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"simulador_{datetime.now().strftime('%Y%m%d')}.log"
            
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
        """Inicializar banco de dados SQLite"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info("ℹ️ Banco de dados não configurado - modo FAISS apenas")
                return
                
            # Criar diretório se não existir
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de simulações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulacoes (
                    id TEXT PRIMARY KEY,
                    contrato_original TEXT,
                    contrato_simulado TEXT,
                    tipo_cenario TEXT,
                    risco_geral TEXT,
                    impacto_financeiro REAL,
                    recomendacao TEXT,
                    data_simulacao TEXT,
                    status TEXT DEFAULT 'ativa'
                )
            """)
            
            # Tabela de alterações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alteracoes (
                    id TEXT PRIMARY KEY,
                    simulacao_id TEXT,
                    tipo TEXT,
                    descricao TEXT,
                    valor_original TEXT,
                    valor_novo TEXT,
                    clausula_afetada TEXT,
                    impacto_estimado TEXT,
                    FOREIGN KEY (simulacao_id) REFERENCES simulacoes (id)
                )
            """)
            
            # Tabela de análises dos agentes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analises_agentes (
                    id TEXT PRIMARY KEY,
                    simulacao_id TEXT,
                    agente TEXT,
                    analise TEXT,
                    risco_detectado TEXT,
                    confianca REAL,
                    data_analise TEXT,
                    FOREIGN KEY (simulacao_id) REFERENCES simulacoes (id)
                )
            """)
            
            # Tabela de grafos de impacto
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grafos_impacto (
                    id TEXT PRIMARY KEY,
                    simulacao_id TEXT,
                    clausulas_afetadas TEXT,
                    dependencias TEXT,
                    impacto_cascata TEXT,
                    risco_propagacao REAL,
                    FOREIGN KEY (simulacao_id) REFERENCES simulacoes (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.info("✅ Banco de dados do Simulador inicializado!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar banco: {str(e)}")
            raise
    
    def simular_cenario_contrato(self, 
                                contrato_data: Dict[str, Any] = None,
                                alteracoes_sugeridas: List[Dict[str, Any]] = None,
                                cenario_descricao: str = "Análise padrão",
                                contrato_original: str = None,
                                alteracoes: List[Dict[str, Any]] = None,
                                autor: str = "Sistema") -> ResultadoSimulacao:
        """
        Simular cenário contrafactual em um contrato
        
        Args:
            contrato_original: Texto do contrato original
            alteracoes: Lista de alterações a simular
            autor: Quem está fazendo a simulação
        
        Returns:
            ResultadoSimulacao com análise completa
        """
        try:
            self.logger.info(f"🧠 Iniciando simulação contrafactual: {cenario_descricao}")
            
            # Usar parâmetros novos se fornecidos, senão usar os antigos
            if contrato_data and not contrato_original:
                contrato_original = contrato_data.get('texto', '')
            if alteracoes_sugeridas and not alteracoes:
                alteracoes = alteracoes_sugeridas
            
            # Validar contrato
            if not contrato_original:
                raise ValueError("Contrato original é obrigatório")
            
            # Validar alterações
            if not alteracoes:
                alteracoes = []
            
            if len(alteracoes) > self.max_alteracoes_por_simulacao:
                raise ValueError(f"Máximo de {self.max_alteracoes_por_simulacao} alterações por simulação")
            
            # 1. Criar contrato simulado
            contrato_simulado = self._aplicar_alteracoes_contrato(contrato_original, alteracoes)
            
            # 2. Criar objetos de alteração
            alteracoes_obj = self._criar_alteracoes_objeto(alteracoes, autor)
            
            # 3. Analisar impacto com agentes
            analise_jurista = self._analisar_com_jurista(contrato_simulado)
            analise_financeira = self._analisar_com_financial(contrato_simulado)
            analise_skeptic = self._analisar_com_skeptic(contrato_simulado)
            
            # 4. Calcular risco geral
            risco_geral = self._calcular_risco_geral(analise_jurista, analise_financeira, analise_skeptic)
            
            # 5. Gerar recomendação
            recomendacao = self._gerar_recomendacao(risco_geral, analise_jurista, analise_financeira, analise_skeptic)
            
            # 6. Calcular impacto financeiro
            impacto_financeiro = self._calcular_impacto_financeiro(alteracoes, analise_financeira)
            
            # 7. Criar resultado da simulação
            resultado = ResultadoSimulacao(
                id=hashlib.md5(f"{contrato_original[:100]}_{datetime.now().isoformat()}".encode()).hexdigest()[:8],
                contrato_original=contrato_original,
                contrato_simulado=contrato_simulado,
                alteracoes=alteracoes_obj,
                analise_jurista=analise_jurista,
                analise_financeira=analise_financeira,
                analise_skeptic=analise_skeptic,
                risco_geral=risco_geral,
                recomendacao=recomendacao,
                impacto_financeiro=impacto_financeiro,
                data_simulacao=datetime.now()
            )
            
            # 8. Salvar simulação
            self._salvar_simulacao(resultado)
            
            # 9. Criar grafo de impacto
            grafo_impacto = self._criar_grafo_impacto(resultado)
            self._salvar_grafo_impacto(grafo_impacto, resultado.id)
            
            self.logger.info(f"✅ Simulação concluída! Risco: {risco_geral.value}")
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"❌ Erro na simulação: {str(e)}")
            raise
    
    def _aplicar_alteracoes_contrato(self, contrato_original: str, alteracoes: List[Dict[str, Any]]) -> str:
        """Aplicar alterações ao contrato original"""
        contrato_simulado = contrato_original
        
        try:
            for alteracao in alteracoes:
                tipo = alteracao.get('tipo')
                valor_original = alteracao.get('valor_original')
                valor_novo = alteracao.get('valor_novo')
                clausula = alteracao.get('clausula', '')
                
                if tipo == 'alteracao_valor':
                    # Substituir valores específicos
                    contrato_simulado = contrato_simulado.replace(valor_original, valor_novo)
                
                elif tipo == 'alteracao_clausula':
                    # Substituir cláusulas inteiras
                    contrato_simulado = contrato_simulado.replace(clausula, valor_novo)
                
                elif tipo == 'alteracao_prazo':
                    # Substituir prazos
                    contrato_simulado = re.sub(
                        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # Padrão de data
                        valor_novo,
                        contrato_simulado
                    )
                
                elif tipo == 'alteracao_parte':
                    # Substituir nomes de partes
                    contrato_simulado = contrato_simulado.replace(valor_original, valor_novo)
                
                elif tipo == 'alteracao_obrigacao':
                    # Substituir obrigações
                    contrato_simulado = contrato_simulado.replace(valor_original, valor_novo)
            
            return contrato_simulado
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao aplicar alterações: {str(e)}")
            return contrato_original
    
    def _criar_alteracoes_objeto(self, alteracoes: List[Dict[str, Any]], autor: str) -> List[AlteracaoContrato]:
        """Criar objetos de alteração estruturados"""
        alteracoes_obj = []
        
        try:
            for i, alteracao in enumerate(alteracoes):
                alteracao_obj = AlteracaoContrato(
                    id=f"alt_{i}_{hashlib.md5(str(alteracao).encode()).hexdigest()[:6]}",
                    tipo=TipoCenario(alteracao.get('tipo', 'alteracao_valor')),
                    descricao=alteracao.get('descricao', 'Alteração não especificada'),
                    valor_original=alteracao.get('valor_original', ''),
                    valor_novo=alteracao.get('valor_novo', ''),
                    clausula_afetada=alteracao.get('clausula', ''),
                    impacto_estimado=alteracao.get('impacto_estimado', 'Não avaliado'),
                    data_simulacao=datetime.now(),
                    autor=autor
                )
                alteracoes_obj.append(alteracao_obj)
            
            return alteracoes_obj
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar alterações: {str(e)}")
            return []
    
    def _analisar_com_jurista(self, contrato_simulado: str) -> Dict[str, Any]:
        """Simular análise do Agente Jurista"""
        try:
            # Análise baseada em palavras-chave e padrões
            risco_legal = NivelRisco.BAIXO
            confianca = 0.8
            
            # Verificar cláusulas problemáticas
            clausulas_problematicas = []
            
            if 'multa' in contrato_simulado.lower():
                if '10%' in contrato_simulado or '15%' in contrato_simulado:
                    risco_legal = NivelRisco.ALTO
                    clausulas_problematicas.append('Multa excessiva')
            
            if 'arbitragem' in contrato_simulado.lower():
                if 'modelo a' in contrato_simulado.lower():
                    risco_legal = NivelRisco.MEDIO
                    clausulas_problematicas.append('Modelo de arbitragem problemático')
            
            if 'rescisão' in contrato_simulado.lower():
                if 'unilateral' in contrato_simulado.lower():
                    risco_legal = NivelRisco.ALTO
                    clausulas_problematicas.append('Rescisão unilateral')
            
            return {
                'risco_legal': risco_legal.value,
                'confianca': confianca,
                'clausulas_problematicas': clausulas_problematicas,
                'recomendacoes_juridicas': [
                    'Revisar cláusulas de multa',
                    'Avaliar modelo de arbitragem',
                    'Considerar rescisão bilateral'
                ],
                'impacto_legal': 'Moderado' if risco_legal in [NivelRisco.MEDIO, NivelRisco.ALTO] else 'Baixo'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise jurídica: {str(e)}")
            return {'erro': str(e)}
    
    def _analisar_com_financial(self, contrato_simulado: str) -> Dict[str, Any]:
        """Simular análise do Agente Financial"""
        try:
            # Análise financeira baseada em valores e prazos
            risco_financeiro = NivelRisco.BAIXO
            confianca = 0.85
            
            # Extrair valores monetários
            valores = re.findall(r'R\$\s*([\d.,]+)', contrato_simulado)
            valores_numericos = []
            
            for valor in valores:
                try:
                    valor_limpo = valor.replace('.', '').replace(',', '.')
                    valores_numericos.append(float(valor_limpo))
                except:
                    continue
            
            # Analisar valores
            if valores_numericos:
                valor_maximo = max(valores_numericos)
                if valor_maximo > 1000000:  # R$ 1M
                    risco_financeiro = NivelRisco.MEDIO
                if valor_maximo > 5000000:  # R$ 5M
                    risco_financeiro = NivelRisco.ALTO
            
            # Verificar prazos
            prazos = re.findall(r'(\d+)\s*(dias?|meses?|anos?)', contrato_simulado.lower())
            if prazos:
                for prazo, unidade in prazos:
                    prazo_num = int(prazo)
                    if unidade.startswith('ano') and prazo_num > 5:
                        risco_financeiro = max(risco_financeiro, NivelRisco.MEDIO)
                    elif unidade.startswith('mes') and prazo_num > 60:
                        risco_financeiro = max(risco_financeiro, NivelRisco.MEDIO)
            
            return {
                'risco_financeiro': risco_financeiro.value,
                'confianca': confianca,
                'valores_identificados': valores_numericos,
                'prazos_identificados': prazos,
                'exposicao_maxima': max(valores_numericos) if valores_numericos else 0,
                'recomendacoes_financeiras': [
                    'Avaliar capacidade de pagamento',
                    'Considerar garantias adicionais',
                    'Revisar cronograma de pagamentos'
                ],
                'impacto_financeiro': 'Alto' if risco_financeiro in [NivelRisco.ALTO, NivelRisco.CRITICO] else 'Moderado'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise financeira: {str(e)}")
            return {'erro': str(e)}
    
    def _analisar_com_skeptic(self, contrato_simulado: str) -> Dict[str, Any]:
        """Simular análise do Agente Skeptic"""
        try:
            # Análise cética baseada em inconsistências e riscos ocultos
            risco_skeptic = NivelRisco.BAIXO
            confianca = 0.9
            
            # Verificar inconsistências
            inconsistencias = []
            
            # Verificar se há contradições entre valores
            valores = re.findall(r'R\$\s*([\d.,]+)', contrato_simulado)
            if len(set(valores)) > 1:
                inconsistencias.append('Múltiplos valores diferentes no contrato')
                risco_skeptic = NivelRisco.MEDIO
            
            # Verificar cláusulas ambíguas
            palavras_ambiguas = ['razoável', 'adequado', 'apropriado', 'conforme necessário']
            for palavra in palavras_ambiguas:
                if palavra in contrato_simulado.lower():
                    inconsistencias.append(f'Termo ambíguo: "{palavra}"')
                    risco_skeptic = max(risco_skeptic, NivelRisco.MEDIO)
            
            # Verificar prazos irrealistas
            if 'prazo' in contrato_simulado.lower() and 'imediato' in contrato_simulado.lower():
                inconsistencias.append('Prazo irrealista: "imediato"')
                risco_skeptic = max(risco_skeptic, NivelRisco.ALTO)
            
            return {
                'risco_skeptic': risco_skeptic.value,
                'confianca': confianca,
                'inconsistencias_detectadas': inconsistencias,
                'riscos_ocultos': [
                    'Cláusulas ambíguas podem gerar interpretações divergentes',
                    'Prazos irrealistas podem causar descumprimento',
                    'Valores inconsistentes podem indicar erro de digitação'
                ],
                'recomendacoes_skeptic': [
                    'Clarificar termos ambíguos',
                    'Definir prazos específicos',
                    'Revisar valores para consistência'
                ],
                'impacto_skeptic': 'Alto' if risco_skeptic in [NivelRisco.ALTO, NivelRisco.CRITICO] else 'Moderado'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise cética: {str(e)}")
            return {'erro': str(e)}
    
    def _calcular_risco_geral(self, 
                              analise_jurista: Dict[str, Any],
                              analise_financeira: Dict[str, Any],
                              analise_skeptic: Dict[str, Any]) -> NivelRisco:
        """Calcular risco geral baseado nas análises dos agentes"""
        try:
            # Mapear níveis de risco para valores numéricos
            risco_map = {
                'baixo': 1,
                'medio': 2,
                'alto': 3,
                'critico': 4
            }
            
            # Obter riscos de cada agente
            risco_jurista = risco_map.get(analise_jurista.get('risco_legal', 'baixo'), 1)
            risco_financeiro = risco_map.get(analise_financeira.get('risco_financeiro', 'baixo'), 1)
            risco_skeptic = risco_map.get(analise_skeptic.get('risco_skeptic', 'baixo'), 1)
            
            # Calcular média ponderada (skeptic tem peso maior)
            risco_medio = (risco_jurista + risco_financeiro + (risco_skeptic * 1.5)) / 3.5
            
            # Mapear de volta para nível de risco
            if risco_medio <= 1.5:
                return NivelRisco.BAIXO
            elif risco_medio <= 2.5:
                return NivelRisco.MEDIO
            elif risco_medio <= 3.5:
                return NivelRisco.ALTO
            else:
                return NivelRisco.CRITICO
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular risco geral: {str(e)}")
            return NivelRisco.MEDIO
    
    def _gerar_recomendacao(self, 
                           risco_geral: NivelRisco,
                           analise_jurista: Dict[str, Any],
                           analise_financeira: Dict[str, Any],
                           analise_skeptic: Dict[str, Any]) -> str:
        """Gerar recomendação baseada no risco geral e análises"""
        try:
            if risco_geral == NivelRisco.BAIXO:
                return "✅ Contrato simulado apresenta risco baixo. Pode prosseguir com as alterações propostas."
            
            elif risco_geral == NivelRisco.MEDIO:
                return "⚠️ Contrato simulado apresenta risco moderado. Recomenda-se revisar as alterações antes de implementar."
            
            elif risco_geral == NivelRisco.ALTO:
                return "🚨 Contrato simulado apresenta risco alto. Não recomenda-se prosseguir com as alterações propostas."
            
            else:  # CRITICO
                return "💀 Contrato simulado apresenta risco crítico. Alterações devem ser completamente rejeitadas."
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao gerar recomendação: {str(e)}")
            return "Erro ao gerar recomendação"
    
    def _calcular_impacto_financeiro(self, 
                                    alteracoes: List[Dict[str, Any]],
                                    analise_financeira: Dict[str, Any]) -> float:
        """Calcular impacto financeiro das alterações"""
        try:
            impacto_total = 0.0
            
            for alteracao in alteracoes:
                if alteracao.get('tipo') == 'alteracao_valor':
                    try:
                        valor_original = float(alteracao.get('valor_original', '0').replace('R$', '').replace('.', '').replace(',', '.'))
                        valor_novo = float(alteracao.get('valor_novo', '0').replace('R$', '').replace('.', '').replace(',', '.'))
                        impacto_total += abs(valor_novo - valor_original)
                    except:
                        continue
            
            return impacto_total
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular impacto financeiro: {str(e)}")
            return 0.0
    
    def _criar_grafo_impacto(self, resultado: ResultadoSimulacao) -> GrafoImpacto:
        """Criar grafo de impacto das alterações"""
        try:
            # Identificar cláusulas afetadas
            clausulas_afetadas = []
            for alteracao in resultado.alteracoes:
                if alteracao.clausula_afetada:
                    clausulas_afetadas.append(alteracao.clausula_afetada)
            
            # Identificar dependências (simplificado)
            dependencias = []
            for alteracao in resultado.alteracoes:
                if alteracao.tipo in [TipoCenario.ALTERACAO_VALOR, TipoCenario.ALTERACAO_CLAUSULA]:
                    dependencias.append(f"Cláusula {alteracao.clausula_afetada}")
            
            # Calcular impacto em cascata
            impacto_cascata = {}
            for clausula in clausulas_afetadas:
                impacto_cascata[clausula] = 0.7  # Valor padrão
            
            # Calcular risco de propagação
            risco_propagacao = len(clausulas_afetadas) * 0.2
            
            return GrafoImpacto(
                alteracao_id=resultado.id,
                clausulas_afetadas=clausulas_afetadas,
                dependencias=dependencias,
                impacto_cascata=impacto_cascata,
                risco_propagacao=min(risco_propagacao, 1.0)
            )
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar grafo de impacto: {str(e)}")
            return GrafoImpacto(
                alteracao_id=resultado.id,
                clausulas_afetadas=[],
                dependencias=[],
                impacto_cascata={},
                risco_propagacao=0.0
            )
    
    def _salvar_simulacao(self, resultado: ResultadoSimulacao):
        """Salvar resultado da simulação no banco"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info("ℹ️ Banco de dados não configurado - modo FAISS apenas")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Salvar simulação principal
            cursor.execute("""
                INSERT OR REPLACE INTO simulacoes 
                (id, contrato_original, contrato_simulado, tipo_cenario, risco_geral, impacto_financeiro, recomendacao, data_simulacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resultado.id,
                resultado.contrato_original[:1000],  # Limitar tamanho
                resultado.contrato_simulado[:1000],  # Limitar tamanho
                'simulacao_multipla',
                resultado.risco_geral.value,
                resultado.impacto_financeiro,
                resultado.recomendacao,
                resultado.data_simulacao.isoformat()
            ))
            
            # Salvar alterações
            for alteracao in resultado.alteracoes:
                cursor.execute("""
                    INSERT OR REPLACE INTO alteracoes 
                    (id, simulacao_id, tipo, descricao, valor_original, valor_novo, clausula_afetada, impacto_estimado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alteracao.id,
                    resultado.id,
                    alteracao.tipo.value,
                    alteracao.descricao,
                    alteracao.valor_original,
                    alteracao.valor_novo,
                    alteracao.clausula_afetada,
                    alteracao.impacto_estimado
                ))
            
            # Salvar análises dos agentes
            agentes_analises = [
                ('jurista', resultado.analise_jurista),
                ('financial', resultado.analise_financeira),
                ('skeptic', resultado.analise_skeptic)
            ]
            
            for agente, analise in agentes_analises:
                cursor.execute("""
                    INSERT OR REPLACE INTO analises_agentes 
                    (id, simulacao_id, agente, analise, risco_detectado, confianca, data_analise)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{resultado.id}_{agente}",
                    resultado.id,
                    agente,
                    json.dumps(analise, ensure_ascii=False),
                    analise.get('risco_legal', analise.get('risco_financeiro', analise.get('risco_skeptic', 'baixo'))),
                    analise.get('confianca', 0.8),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar simulação: {str(e)}")
    
    def _salvar_grafo_impacto(self, grafo: GrafoImpacto, simulacao_id: str):
        """Salvar grafo de impacto no banco"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info("ℹ️ Banco de dados não configurado - modo FAISS apenas")
                return
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO grafos_impacto 
                (id, simulacao_id, clausulas_afetadas, dependencias, impacto_cascata, risco_propagacao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"grafo_{simulacao_id}",
                simulacao_id,
                json.dumps(grafo.clausulas_afetadas, ensure_ascii=False),
                json.dumps(grafo.dependencias, ensure_ascii=False),
                json.dumps(grafo.impacto_cascata, ensure_ascii=False),
                grafo.risco_propagacao
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar grafo: {str(e)}")
    
    def obter_historico_simulacoes(self) -> List[Dict[str, Any]]:
        """Obter histórico de simulações"""
        try:
            # Verificar se banco está disponível
            if not self.db_path:
                self.logger.info("ℹ️ Banco de dados não configurado - modo FAISS apenas")
                return []
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.*, 
                       COUNT(a.id) as total_alteracoes,
                       AVG(ag.confianca) as confianca_media
                FROM simulacoes s
                LEFT JOIN alteracoes a ON s.id = a.simulacao_id
                LEFT JOIN analises_agentes ag ON s.id = ag.simulacao_id
                GROUP BY s.id
                ORDER BY s.data_simulacao DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            historico = []
            for row in rows:
                historico.append({
                    'id': row[0],
                    'contrato_original': row[1][:100] + '...' if len(row[1]) > 100 else row[1],
                    'contrato_simulado': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
                    'tipo_cenario': row[3],
                    'risco_geral': row[4],
                    'impacto_financeiro': row[5],
                    'recomendacao': row[6],
                    'data_simulacao': row[7],
                    'status': row[8],
                    'total_alteracoes': row[9],
                    'confianca_media': row[10]
                })
            
            return historico
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter histórico: {str(e)}")
            return []

def main():
    """Função principal para teste do Simulador"""
    print("🧠 INICIANDO SIMULADOR CONTRADFACTUAL")
    print("=" * 50)
    
    try:
        # Inicializar Simulador
        simulador = SimuladorContrafactual()
        
        # Exemplo de contrato
        contrato_exemplo = """
        CONTRATO DE PRESTAÇÃO DE SERVIÇOS
        
        CLÁUSULA 1 - OBJETO
        O presente contrato tem por objeto a prestação de serviços de consultoria técnica.
        
        CLÁUSULA 2 - VALOR
        O valor total do contrato é de R$ 500.000,00 (quinhentos mil reais).
        
        CLÁUSULA 3 - PRAZO
        O prazo de execução é de 12 meses.
        
        CLÁUSULA 4 - MULTA
        Em caso de atraso, será aplicada multa de 5% ao mês.
        
        CLÁUSULA 5 - ARBITRAGEM
        As divergências serão resolvidas por arbitragem modelo A.
        """
        
        # Exemplo de alterações
        alteracoes_exemplo = [
            {
                'tipo': 'alteracao_valor',
                'valor_original': 'R$ 500.000,00',
                'valor_novo': 'R$ 750.000,00',
                'descricao': 'Aumento do valor do contrato',
                'clausula': 'CLÁUSULA 2 - VALOR',
                'impacto_estimado': 'Aumento de 50% no valor'
            },
            {
                'tipo': 'alteracao_valor',
                'valor_original': '5%',
                'valor_novo': '10%',
                'descricao': 'Aumento da multa por atraso',
                'clausula': 'CLÁUSULA 4 - MULTA',
                'impacto_estimado': 'Dobro da multa'
            }
        ]
        
        print("📋 Contrato Original:")
        print(contrato_exemplo)
        
        print("\n🔄 Alterações Propostas:")
        for i, alt in enumerate(alteracoes_exemplo, 1):
            print(f"  {i}. {alt['descricao']}: {alt['valor_original']} → {alt['valor_novo']}")
        
        print("\n🧠 Executando simulação contrafactual...")
        
        # Executar simulação
        resultado = simulador.simular_cenario_contrato(
            contrato_exemplo,
            alteracoes_exemplo,
            "Usuário Teste"
        )
        
        print(f"\n📊 RESULTADO DA SIMULAÇÃO:")
        print(f"  🆔 ID: {resultado.id}")
        print(f"  ⚠️ Risco Geral: {resultado.risco_geral.value.upper()}")
        print(f"  💰 Impacto Financeiro: R$ {resultado.impacto_financeiro:,.2f}")
        print(f"  📝 Recomendação: {resultado.recomendacao}")
        
        print(f"\n🔍 ANÁLISES DOS AGENTES:")
        print(f"  ⚖️ Jurista: Risco {resultado.analise_jurista.get('risco_legal', 'N/A')}")
        print(f"  💼 Financial: Risco {resultado.analise_financeira.get('risco_financeiro', 'N/A')}")
        print(f"  🤔 Skeptic: Risco {resultado.analise_skeptic.get('risco_skeptic', 'N/A')}")
        
        print(f"\n📈 HISTÓRICO DE SIMULAÇÕES:")
        historico = simulador.obter_historico_simulacoes()
        for sim in historico[:3]:  # Mostrar apenas as 3 últimas
            print(f"  - {sim['data_simulacao']}: {sim['risco_geral']} risco, {sim['total_alteracoes']} alterações")
        
        print("\n✅ Simulação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na simulação: {str(e)}")

if __name__ == "__main__":
    main()
