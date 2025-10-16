"""
GIC - Gerenciador Inteligente de Contratos
==========================================

Sistema especializado para criação de justificativas de aditivos contratuais
com IA integrada e fluxo estruturado conforme especificações técnicas.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gic_justificativas.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ObjetoAditivo:
    """Estrutura para armazenar informações de cada objeto de aditivo"""
    tipo: str
    respostas: Dict[str, Any]
    completo: bool = False
    justificativa: str = ""

@dataclass
class SessaoJustificativa:
    """Estrutura para armazenar toda a sessão de justificativa"""
    id_sessao: str
    data_criacao: str
    contratada: str
    icj: str
    objetos_selecionados: List[str]
    objetos: Dict[str, ObjetoAditivo]
    perguntas_gerais: Dict[str, str]
    justificativa_final: str
    status: str = "em_andamento"
    data_conclusao: Optional[str] = None

class GICJustificativas:
    """Sistema principal do GIC para criação de justificativas"""
    
    def __init__(self):
        self.sessoes = {}
        self.perguntas_por_objeto = self._definir_perguntas()
        self.diretorio_dados = Path("dados")
        self.diretorio_dados.mkdir(parents=True, exist_ok=True)
        
    def _definir_perguntas(self) -> Dict[str, List[Dict[str, Any]]]:
        """Define todas as perguntas para cada tipo de objeto"""
        return {
            "1 PRAZO": [
                {"id": "demanda_continuada", "pergunta": "É Demanda Continuada?", "tipo": "sim_nao"},
                {"id": "razao_escopo", "pergunta": "Por qual razão o escopo do contrato não foi concluído no prazo original?", "tipo": "texto", "condicao": "demanda_continuada=False"},
                {"id": "aporte_proporcional", "pergunta": "Será com aporte proporcional?", "tipo": "sim_nao", "condicao": "demanda_continuada=True"},
                {"id": "motivo_prorrogacao", "pergunta": "O que motivou a prorrogação?", "tipo": "opcoes", "opcoes": [
                    "1.1 ATRASO NA NOVA CONTRAÇÃO",
                    "1.2 CANCELAMENTO DA NOVA CONTRATAÇÃO", 
                    "1.3 OPORTUNIDADE DE NEGÓCIO"
                ], "condicao": "demanda_continuada=True"},
                {"id": "motivo_atraso", "pergunta": "Qual o motivo do atraso?", "tipo": "texto", "condicao": "motivo_prorrogacao=1.1 ATRASO NA NOVA CONTRAÇÃO"},
                {"id": "sup_oportunidade_atraso", "pergunta": "Qual número do SUP e da oportunidade da nova contratação?", "tipo": "texto", "condicao": "motivo_prorrogacao=1.1 ATRASO NA NOVA CONTRAÇÃO"},
                {"id": "motivo_cancelamento", "pergunta": "Qual o motivo do cancelamento?", "tipo": "texto", "condicao": "motivo_prorrogacao=1.2 CANCELAMENTO DA NOVA CONTRATAÇÃO"},
                {"id": "sup_oportunidade_cancelamento", "pergunta": "Qual número do SUP e da oportunidade da nova contratação?", "tipo": "texto", "condicao": "motivo_prorrogacao=1.2 CANCELAMENTO DA NOVA CONTRATAÇÃO"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "2 ACRÉSCIMO": [
                {"id": "tipo_acrescimo", "pergunta": "Será acréscimo por aumento de quantidade na PPU ou por inclusão de novo 'item' na PPU?", "tipo": "opcoes", "opcoes": ["Aumento de quantidade na PPU", "Inclusão de novo item na PPU"]},
                {"id": "supera_25", "pergunta": "O acréscimo supera 25%, considerando os aditivos já realizados no contrato?", "tipo": "sim_nao"},
                {"id": "parecer_juridico", "pergunta": "Já tem Parecer Jurídico?", "tipo": "sim_nao", "condicao": "supera_25=True"},
                {"id": "arquivo_pj", "pergunta": "Anexe o arquivo do Parecer Jurídico:", "tipo": "arquivo", "condicao": "parecer_juridico=True"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "3 DECRÉSCIMO": [
                {"id": "motivo_decrescimo", "pergunta": "Qual o motivo do decréscimo?", "tipo": "texto"},
                {"id": "impacto_decrescimo", "pergunta": "Qual o impacto do decréscimo no contrato?", "tipo": "texto"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "4 ALTERAÇÃO DE ESCOPO": [
                {"id": "reflexo_precos", "pergunta": "Essa alteração terá reflexo nos preços da PPU?", "tipo": "sim_nao"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "5 REEQUILÍBRIO ECONÔMICO-FINANCEIRO": [
                {"id": "clausula_reequilibrio", "pergunta": "Qual a cláusula de reequilíbrio constante no ICJ?", "tipo": "texto"},
                {"id": "motivo_reequilibrio", "pergunta": "Qual o motivo que gerou a necessidade de reequilíbrio?", "tipo": "texto"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "6 CESSÃO": [
                {"id": "empresa_habilitada", "pergunta": "A empresa cessionária está habilitada nos mesmos critérios da família utilizados na licitação?", "tipo": "sim_nao"},
                {"id": "numero_csp", "pergunta": "Qual o número do CSP?", "tipo": "texto", "condicao": "empresa_habilitada=True"},
                {"id": "siof_aberto", "pergunta": "Foi aberto SIOF para Análise Prévia de Finanças para verificar se haverá maior encargo tributário para a Petrobras?", "tipo": "sim_nao"},
                {"id": "proposta_original", "pergunta": "A empresa cessionária apresentou proposta no processo original da contratação?", "tipo": "sim_nao"},
                {"id": "idf_empresa", "pergunta": "O Índice de Desempenho do Fornecedor (IDF) da empresa cessionária encontra-se com bom desempenho?", "tipo": "sim_nao"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "7 RESCISÃO": [
                {"id": "conduta_contratada", "pergunta": "Qual a conduta da contratada que caracterizou descumprimento do contrato?", "tipo": "texto"},
                {"id": "numeros_rdo", "pergunta": "Qual os números do RDO que registaram os descumprimentos contratuais?", "tipo": "texto"},
                {"id": "numero_carta_multa", "pergunta": "Qual o número da carta que aplicou a multa?", "tipo": "texto"},
                {"id": "item_descumprido", "pergunta": "Qual 'item' do contrato foi descumprido?", "tipo": "texto"},
                {"id": "nota_idf", "pergunta": "Qual a nota IDF atual da contratada?", "tipo": "texto"},
                {"id": "parecer_juridico_rescisao", "pergunta": "Tem parecer Jurídico para a Rescisão?", "tipo": "sim_nao"},
                {"id": "arquivo_pj_rescisao", "pergunta": "Anexe o arquivo do Parecer Jurídico:", "tipo": "arquivo", "condicao": "parecer_juridico_rescisao=True"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "8 EXTENSÃO DE ÁREA DE ABRANGÊNCIA": [
                {"id": "area_original", "pergunta": "Qual a área de abrangência original do contrato?", "tipo": "texto"},
                {"id": "area_nova", "pergunta": "Qual a nova área de abrangência solicitada?", "tipo": "texto"},
                {"id": "justificativa_extensao", "pergunta": "Qual a justificativa para a extensão da área?", "tipo": "texto"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "9 INCLUSÃO DE CNPJ/FILIAL DA CONTRATADA": [
                {"id": "cnpj_original", "pergunta": "Qual o CNPJ original da contratada?", "tipo": "texto"},
                {"id": "cnpj_novo", "pergunta": "Qual o novo CNPJ ou filial a ser incluído?", "tipo": "texto"},
                {"id": "motivo_inclusao", "pergunta": "Qual o motivo da inclusão do novo CNPJ/filial?", "tipo": "texto"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ],
            "10 ALTERAÇÃO DE PREÂMBULO": [
                {"id": "alteracao_preambulo", "pergunta": "Qual alteração será realizada no preâmbulo?", "tipo": "texto"},
                {"id": "motivo_alteracao", "pergunta": "Qual o motivo da alteração no preâmbulo?", "tipo": "texto"},
                {"id": "fato_superveniente", "pergunta": "Qual o fato Superveniente?", "tipo": "texto", "obrigatorio": True}
            ]
        }
    
    def criar_nova_sessao(self, contratada: str, icj: str) -> str:
        """Cria uma nova sessão de justificativa"""
        id_sessao = f"gic_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(contratada)}"
        
        sessao = SessaoJustificativa(
            id_sessao=id_sessao,
            data_criacao=datetime.now().isoformat(),
            contratada=contratada,
            icj=icj,
            objetos_selecionados=[],
            objetos={},
            perguntas_gerais={},
            justificativa_final=""
        )
        
        self.sessoes[id_sessao] = sessao
        self._salvar_sessao(sessao)
        
        logger.info(f"Nova sessao criada: {id_sessao} para {contratada}")
        return id_sessao
    
    def selecionar_objetos(self, id_sessao: str, objetos: List[str]) -> Dict[str, Any]:
        """Seleciona os objetos de aditivo para a sessão"""
        if id_sessao not in self.sessoes:
            raise ValueError("Sessão não encontrada")
        
        sessao = self.sessoes[id_sessao]
        sessao.objetos_selecionados = objetos
        
        # Inicializar objetos
        for objeto in objetos:
            sessao.objetos[objeto] = ObjetoAditivo(
                tipo=objeto,
                respostas={}
            )
        
        self._salvar_sessao(sessao)
        
        return {
            "status": "sucesso",
            "objetos_selecionados": objetos,
            "proxima_pergunta": self._obter_proxima_pergunta(id_sessao)
        }
    
    def _obter_proxima_pergunta(self, id_sessao: str) -> Optional[Dict[str, Any]]:
        """Obtém a próxima pergunta a ser feita"""
        sessao = self.sessoes[id_sessao]
        
        # Verificar se há objetos para processar
        if not sessao.objetos_selecionados:
            return None
        
        # Processar objetos em sequência
        for objeto_tipo in sessao.objetos_selecionados:
            objeto = sessao.objetos[objeto_tipo]
            
            if not objeto.completo:
                # Encontrar próxima pergunta para este objeto
                perguntas = self.perguntas_por_objeto.get(objeto_tipo, [])
                
                for pergunta in perguntas:
                    pergunta_id = pergunta["id"]
                    
                    # Verificar se a pergunta já foi respondida
                    if pergunta_id not in objeto.respostas:
                        # Verificar condições
                        if self._verificar_condicoes(pergunta, objeto.respostas):
                            return {
                                "objeto": objeto_tipo,
                                "pergunta": pergunta,
                                "tipo_sessao": "objeto"
                            }
                
                # Se chegou aqui, o objeto está completo
                objeto.completo = True
        
        # Se todos os objetos estão completos, verificar perguntas gerais
        if self._todas_perguntas_objetos_completas(id_sessao):
            return self._obter_proxima_pergunta_geral(id_sessao)
        
        return None
    
    def _verificar_condicoes(self, pergunta: Dict[str, Any], respostas: Dict[str, Any]) -> bool:
        """Verifica se as condições da pergunta são atendidas"""
        if "condicao" not in pergunta:
            return True
        
        condicao = pergunta["condicao"]
        # Implementar lógica de verificação de condições
        # Por simplicidade, sempre retorna True por enquanto
        return True
    
    def _todas_perguntas_objetos_completas(self, id_sessao: str) -> bool:
        """Verifica se todas as perguntas dos objetos estão completas"""
        sessao = self.sessoes[id_sessao]
        return all(objeto.completo for objeto in sessao.objetos.values())
    
    def _obter_proxima_pergunta_geral(self, id_sessao: str) -> Optional[Dict[str, Any]]:
        """Obtém a próxima pergunta geral"""
        sessao = self.sessoes[id_sessao]
        
        perguntas_gerais = [
            "impactos_ausencia",
            "importancia_contrato", 
            "informacoes_adicionais"
        ]
        
        for pergunta_id in perguntas_gerais:
            if pergunta_id not in sessao.perguntas_gerais:
                perguntas = {
                    "impactos_ausencia": "A ausência desse contrato gera quais impactos, prejuízos e riscos para a Petrobras?",
                    "importancia_contrato": "Qual a importância desse contrato para Petrobras?",
                    "informacoes_adicionais": "Se houver alguma informação adicional para fortalecer as justificativas desse aditivo, descreva abaixo"
                }
                
                return {
                    "objeto": "GERAL",
                    "pergunta": {
                        "id": pergunta_id,
                        "pergunta": perguntas[pergunta_id],
                        "tipo": "texto"
                    },
                    "tipo_sessao": "geral"
                }
        
        return None
    
    def responder_pergunta(self, id_sessao: str, pergunta_id: str, resposta: str, objeto_tipo: str = None) -> Dict[str, Any]:
        """Registra a resposta do usuário e retorna a próxima pergunta"""
        if id_sessao not in self.sessoes:
            raise ValueError("Sessão não encontrada")
        
        sessao = self.sessoes[id_sessao]
        
        # Validar resposta antes de prosseguir
        pergunta_atual = self._obter_pergunta_atual(id_sessao, pergunta_id, objeto_tipo)
        if pergunta_atual and hasattr(self, 'gic_ia') and hasattr(self.gic_ia, 'validar_resposta_usuario'):
            validacao = self.gic_ia.validar_resposta_usuario(pergunta_atual, resposta)
            
            if not validacao.get('valida', True):
                # Resposta inválida - retornar erro com sugestão
                return {
                    "status": "erro_validacao",
                    "motivo": validacao.get('motivo', 'Resposta inválida'),
                    "sugestao": validacao.get('sugestao', 'Por favor, forneça uma resposta adequada.'),
                    "pergunta_atual": pergunta_atual
                }
        
        if objeto_tipo and objeto_tipo in sessao.objetos:
            # Resposta para pergunta de objeto específico
            sessao.objetos[objeto_tipo].respostas[pergunta_id] = resposta
        else:
            # Resposta para pergunta geral
            sessao.perguntas_gerais[pergunta_id] = resposta
        
        self._salvar_sessao(sessao)
        
        # Obter próxima pergunta
        proxima_pergunta = self._obter_proxima_pergunta(id_sessao)
        
        if proxima_pergunta is None:
            # Todas as perguntas foram respondidas, gerar justificativa
            justificativa = self._gerar_justificativa_final(sessao)
            sessao.justificativa_final = justificativa
            sessao.status = "concluida"
            sessao.data_conclusao = datetime.now().isoformat()
            self._salvar_sessao(sessao)
            
            return {
                "status": "concluida",
                "justificativa": justificativa,
                "mensagem": "Justificativa concluída com sucesso!"
            }
        
        return {
            "status": "continuar",
            "proxima_pergunta": proxima_pergunta
        }
    
    def _obter_pergunta_atual(self, id_sessao: str, pergunta_id: str, objeto_tipo: str = None) -> dict:
        """Obtém os dados da pergunta atual para validação"""
        try:
            if hasattr(self, 'gic_ia') and hasattr(self.gic_ia, '_obter_perguntas_objeto'):
                if objeto_tipo:
                    # Pergunta específica de objeto
                    return self.gic_ia._obter_perguntas_objeto(objeto_tipo, pergunta_id)
                else:
                    # Pergunta geral - definir estrutura básica
                    perguntas_gerais = {
                        "pergunta_0": {
                            "pergunta": "Qual o fato Superveniente?",
                            "validacao": "fato_superveniente"
                        },
                        "pergunta_1": {
                            "pergunta": "Quais os impactos, prejuízos ou riscos?",
                            "validacao": "texto_livre"
                        },
                        "pergunta_2": {
                            "pergunta": "Qual a importância estratégica?",
                            "validacao": "texto_livre"
                        }
                    }
                    return perguntas_gerais.get(pergunta_id, {})
            return {}
        except Exception as e:
            logger.error(f"[VALIDAÇÃO] Erro ao obter pergunta atual: {e}")
            return {}
    
    def _gerar_justificativa_final(self, sessao: SessaoJustificativa) -> str:
        """Gera a justificativa final baseada em todas as respostas"""
        justificativa = f"""
JUSTIFICATIVA PARA ADITIVO CONTRATUAL

ICJ: {sessao.icj}
CONTRATADA: {sessao.contratada}
DATA: {sessao.data_criacao}

A Gerência identificou que o contrato em referência necessita ser aditado pelos seguintes motivos:

"""
        
        # Adicionar justificativas por objeto
        for objeto_tipo in sessao.objetos_selecionados:
            objeto = sessao.objetos[objeto_tipo]
            justificativa += f"\n{objeto_tipo.upper()}:\n"
            
            # Adicionar fato superveniente
            if "fato_superveniente" in objeto.respostas:
                justificativa += f"Fato Superveniente: {objeto.respostas['fato_superveniente']}\n"
            
            # Adicionar outras respostas específicas do objeto
            for pergunta_id, resposta in objeto.respostas.items():
                if pergunta_id != "fato_superveniente":
                    pergunta = next((p for p in self.perguntas_por_objeto.get(objeto_tipo, []) if p["id"] == pergunta_id), None)
                    if pergunta:
                        justificativa += f"{pergunta['pergunta']}: {resposta}\n"
            
            justificativa += "\n"
        
        # Adicionar perguntas gerais
        if sessao.perguntas_gerais:
            justificativa += "\nANÁLISE GERAL:\n"
            if "impactos_ausencia" in sessao.perguntas_gerais:
                justificativa += f"Impactos da ausência do contrato: {sessao.perguntas_gerais['impactos_ausencia']}\n"
            if "importancia_contrato" in sessao.perguntas_gerais:
                justificativa += f"Importância do contrato: {sessao.perguntas_gerais['importancia_contrato']}\n"
            if "informacoes_adicionais" in sessao.perguntas_gerais:
                justificativa += f"Informações adicionais: {sessao.perguntas_gerais['informacoes_adicionais']}\n"
        
        justificativa += f"""

CONCLUSÃO:
Com base nas informações coletadas e analisadas, justifica-se plenamente a realização do aditivo contratual solicitado, atendendo aos requisitos legais e técnicos necessários.

---
Solicitações de Melhorias, críticas e/ou elogios, enviar e-mail para Chave XBZF
"""
        
        return justificativa
    
    def _salvar_sessao(self, sessao: SessaoJustificativa):
        """Salva a sessão em arquivo JSON"""
        arquivo = self.diretorio_dados / f"{sessao.id_sessao}.json"
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(asdict(sessao), f, indent=2, ensure_ascii=False)
    
    def carregar_sessao(self, id_sessao: str) -> Optional[SessaoJustificativa]:
        """Carrega uma sessão do arquivo"""
        arquivo = self.diretorio_dados / f"{id_sessao}.json"
        if arquivo.exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                return SessaoJustificativa(**dados)
        return None
    
    def listar_sessoes(self) -> List[Dict[str, Any]]:
        """Lista todas as sessões existentes"""
        sessoes = []
        for arquivo in self.diretorio_dados.glob("*.json"):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    sessoes.append({
                        "id": dados["id_sessao"],
                        "contratada": dados["contratada"],
                        "icj": dados["icj"],
                        "data_criacao": dados["data_criacao"],
                        "status": dados["status"],
                        "objetos": dados["objetos_selecionados"]
                    })
            except Exception as e:
                logger.error(f"Erro ao carregar sessao {arquivo}: {e}")
        
        return sorted(sessoes, key=lambda x: x["data_criacao"], reverse=True)
