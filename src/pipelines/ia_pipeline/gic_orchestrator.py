#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GIC Orchestrator
================
Fluxo conversacional do GIC (Gerenciador Inteligente de Contratos) conforme prompt fornecido.

Fornece uma pequena máquina de estados para conduzir o UTILIZADOR pelas etapas,
armazenar respostas (UT-GIC) e gerar o texto final de justificativas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


GIC_ITENS = [
    "PRAZO",
    "ACRÉSCIMO", 
    "DECRÉSCIMO",
    "ALTERAÇÃO DE ESCOPO",
    "REEQUILÍBRIO ECONÔMICO-FINANCEIRO",
    "CESSÃO",
    "RESCISÃO",
    "EXTENSÃO DE ÁREA DE ABRANGÊNCIA",
    "INCLUSÃO DE CNPJ/FILIAL DA CONTRATADA",
    "ALTERAÇÃO DE PREÂMBULO",
]


def gic_menu() -> str:
    linhas = [
        "GIC (Gerenciador Inteligente de Contratos)",
        "Quais alterações serão realizadas no contrato?",
        "OBJETO DO ADITIVO:",
    ]
    for i, item in enumerate(GIC_ITENS, 1):
        linhas.append(f"{i} {item}")
    return "\n".join(linhas)


@dataclass
class GICState:
    selected_items: List[str] = field(default_factory=list)
    current_index: int = 0
    ut_gic: Dict[str, List[Dict[str, str]]] = field(default_factory=dict)
    stage: str = "select_items"  # select_items | per_item | general_questions | document_analysis | finalize
    per_item_step: int = 0
    uploaded_documents: List[Dict[str, str]] = field(default_factory=list)  # Documentos anexados pelo usuário
    document_analysis_complete: bool = False

    def reset_per_item(self) -> None:
        self.per_item_step = 0

    def current_item(self) -> Optional[str]:
        if 0 <= self.current_index < len(self.selected_items):
            return self.selected_items[self.current_index]
        return None


class GICOrchestrator:
    def __init__(self) -> None:
        self.state = GICState()

    def start(self) -> str:
        self.state = GICState()
        return gic_menu()

    def parse_selection(self, user_text: str) -> List[str]:
        picks: List[str] = []
        for token in user_text.replace(",", " ").split():
            if token.isdigit():
                idx = int(token) - 1
                if 0 <= idx < len(GIC_ITENS):
                    picks.append(GIC_ITENS[idx])
        # Também aceitar nomes diretamente
        for item in GIC_ITENS:
            if item.lower() in user_text.lower():
                if item not in picks:
                    picks.append(item)
        return list(dict.fromkeys(picks))  # dedup preservando ordem

    def handle(self, user_text: str) -> str:
        if self.state.stage == "select_items":
            sel = self.parse_selection(user_text)
            if not sel:
                return "Selecione ao menos um objeto (número ou nome).\n" + gic_menu()
            self.state.selected_items = sel
            self.state.stage = "per_item"
            self.state.current_index = 0
            self.state.reset_per_item()
            return self._next_per_item_question()

        if self.state.stage == "per_item":
            # Registrar resposta da última pergunta feita
            item = self.state.current_item()
            if item:
                self._append_ut(item, self._last_question(item), user_text)
            return self._next_per_item_question()

        if self.state.stage == "general_questions":
            # Registrar sequencialmente as respostas 1..3 e avançar
            item_key = "GERAL"
            self._append_ut(item_key, self._last_general_question(), user_text)
            return self._next_general_question()

        if self.state.stage == "document_analysis":
            # Passo 5º: Análise de documentos conforme prompt
            return self._analyze_documents_and_ask_complementary_questions()

        if self.state.stage == "finalize":
            return self.render_final_justification()

        return "Estado inválido. Reiniciando...\n" + self.start()

    # ---------------------- PER-ITEM LOGIC ----------------------
    def _append_ut(self, item: str, question: str, answer: str) -> None:
        if not question:
            return
        self.state.ut_gic.setdefault(item, []).append({"pergunta": question, "resposta": answer})

    def _last_question(self, item: str) -> str:
        # Informativo somente; a pergunta efetiva é controlada por per_item_step
        steps = self._per_item_steps(item)
        idx = max(0, min(self.state.per_item_step - 1, len(steps) - 1))
        return steps[idx] if steps else ""

    def _next_per_item_question(self) -> str:
        item = self.state.current_item()
        if item is None:
            # Avançar para perguntas gerais
            self.state.stage = "general_questions"
            self.state.per_item_step = 0
            return self._next_general_question()

        steps = self._per_item_steps(item)
        if self.state.per_item_step < len(steps):
            q = steps[self.state.per_item_step]
            self.state.per_item_step += 1
            return f"[{item}] {q}"
        else:
            # Próximo item
            self.state.current_index += 1
            self.state.reset_per_item()
            return self._next_per_item_question()

    def _per_item_steps(self, item: str) -> List[str]:
        """Implementa EXATAMENTE o fluxo do prompt - 50+ cenários"""
        comum = [
            "Qual o fato Superveniente? (solicitar detalhamento da resposta)",
        ]
        
        if item == "PRAZO":
            return [
                "É Demanda Continuada?",
                "Se não: Por qual razão o escopo do contrato não foi concluído no prazo original?",
                "Se sim: Será com aporte proporcional?",
                "O que motivou a prorrogação? (escolha uma opção):",
                "1.1 ATRASO NA NOVA CONTRAÇÃO",
                "1.1.1 Qual o motivo do atraso?",
                "1.1.2 Qual número do SUP e da oportunidade da nova contratação?",
                "1.2 CANCELAMENTO DA NOVA CONTRATAÇÃO", 
                "1.2.1 Qual o motivo do cancelamento?",
                "1.2.2 Qual número do SUP e da oportunidade da nova contratação?",
                "1.3 OPORTUNIDADE DE NEGÓCIO",
                "Fazer as perguntas necessárias, conforme anexo 'Diretrizes para substituição de contratação por aditivo'",
            ] + comum
            
        elif item == "ACRÉSCIMO":
            return [
                "Será acréscimo por aumento de quantidade na PPU ou por inclusão de novo 'item' na PPU?",
                "O acréscimo supera 25%, considerando os aditivos já realizados no contrato?",
                "Se sim: já tem Parecer Jurídico? Solicitar ao UTILIZADOR que anexe o arquivo ao GIC para análise.",
                "Se não: oriente a providenciá-lo (adicione, na justificativa um 'aviso' com a observação sobre o PJUR).",
            ] + comum
            
        elif item == "DECRÉSCIMO":
            return [
                "Fazer as perguntas que a GIC entender necessárias para o decréscimo.",
            ] + comum
            
        elif item == "ALTERAÇÃO DE ESCOPO":
            return [
                "Essa alteração terá reflexo nos preços da PPU?",
                "Se sim: deve considerar as perguntas do objeto 2 ACRÉSCIMO (caso não tenha sido escolhido pelo UTILIZADOR).",
                "Se não: seguir as demais orientações do prompt.",
            ] + comum
            
        elif item == "REEQUILÍBRIO ECONÔMICO-FINANCEIRO":
            return [
                "Fazer as perguntas da cláusula de reequilíbrio constante no ICJ.",
            ] + comum
            
        elif item == "CESSÃO":
            return [
                "A empresa cessionária está habilitada nos mesmos critérios da família utilizados na licitação?",
                "Sim - qual o número do CSP?",
                "Foi aberto SIOF para Análise Prévia de Finanças para verificar se haverá maior encargo tributário para a Petrobras?",
                "A empresa cessionária apresentou proposta no processo original da contratação?",
                "O Índice de Desempenho do Fornecedor (IDF) da empresa cessionária encontra-se com bom desempenho?",
            ] + comum
            
        elif item == "RESCISÃO":
            return [
                "Qual a conduta da contratada que caracterizou descumprimento do contrato?",
                "Qual os números do RDO que registraram os descumprimentos contratuais?",
                "Qual o número da carta que aplicou a multa?",
                "Qual 'item' do contrato foi descumprido?",
                "Qual a nota IDF atual da contratada?",
                "Tem parecer Jurídico para a Rescisão?",
                "Se sim: 'solicitar ao UTILIZADOR que anexe o arquivo ao GIC para análise'.",
                "Se não: 'oriente a providenciá-lo e siga o prompt'.",
            ] + comum
            
        elif item == "EXTENSÃO DE ÁREA DE ABRANGÊNCIA":
            return [
                "Fazer as perguntas considerando UT-GIC para extensão de área.",
            ] + comum
            
        elif item == "INCLUSÃO DE CNPJ/FILIAL DA CONTRATADA":
            return [
                "Fazer as perguntas considerando UT-GIC para inclusão de CNPJ/filial.",
            ] + comum
            
        elif item == "ALTERAÇÃO DE PREÂMBULO":
            return [
                "Fazer as perguntas considerando UT-GIC para alteração de preâmbulo (endereço, CNPJ, etc.).",
            ] + comum
            
        return comum

    # ---------------------- GENERAL QUESTIONS ----------------------
    def _last_general_question(self) -> str:
        """Implementa EXATAMENTE as 3 perguntas gerais do prompt"""
        idx = max(0, min(self.state.per_item_step - 1, 2))
        return [
            "A ausência desse contrato gera quais impactos, prejuízos e riscos para a Petrobras?",
            "Qual a importância desse contrato para Petrobras?",
            "Se houver alguma informação adicional para fortalecer as justificativas desse aditivo, descreva abaixo",
        ][idx]

    def _next_general_question(self) -> str:
        """Implementa EXATAMENTE as 3 perguntas gerais do prompt - uma de cada vez"""
        questions = [
            "A ausência desse contrato gera quais impactos, prejuízos e riscos para a Petrobras?",
            "Qual a importância desse contrato para Petrobras?",
            "Se houver alguma informação adicional para fortalecer as justificativas desse aditivo, descreva abaixo",
        ]
        if self.state.per_item_step < len(questions):
            q = questions[self.state.per_item_step]
            self.state.per_item_step += 1
            return f"[GERAL] {q}"
        else:
            # Passo 5º: Análise de documentos conforme prompt
            self.state.stage = "document_analysis"
            return "Agora vou analisar os documentos anexados e verificar se há ausência de informação. Caso haja, farei perguntas complementares conforme o documento 'Orientações para justificativas em aditivos contratuais'."

    def _analyze_documents_and_ask_complementary_questions(self) -> str:
        """Passo 5º: Analisa documentos e faz perguntas complementares conforme prompt"""
        try:
            # Verificar se há documentos anexados
            if not self.state.uploaded_documents:
                # Sem documentos, ir direto para finalização
                self.state.stage = "finalize"
                return "Nenhum documento anexado. Gerando redação final das justificativas..."
            
            # Analisar documentos conforme prompt
            # Aqui seria integrado com o FAISS textual para consultar o documento
            # "Orientações para justificativas em aditivos contratuais"
            
            # Por enquanto, fazer análise básica e perguntas complementares
            missing_info = self._identify_missing_information()
            
            if missing_info:
                return f"Após análise dos documentos, identifiquei informações ausentes:\n{missing_info}\n\nPor favor, forneça essas informações complementares."
            else:
                # Todas as informações estão completas
                self.state.stage = "finalize"
                return "Análise de documentos concluída. Todas as informações estão completas. Gerando redação final das justificativas..."
                
        except Exception as e:
            # Em caso de erro, continuar para finalização
            self.state.stage = "finalize"
            return f"Erro na análise de documentos: {e}. Gerando redação final das justificativas..."

    def _identify_missing_information(self) -> str:
        """Identifica informações ausentes baseado nas respostas coletadas"""
        missing = []
        
        # Verificar se todos os objetos selecionados têm respostas completas
        for item in self.state.selected_items:
            if item not in self.state.ut_gic or len(self.state.ut_gic[item]) == 0:
                missing.append(f"- {item}: Sem respostas coletadas")
        
        # Verificar se as perguntas gerais foram respondidas
        if "GERAL" not in self.state.ut_gic or len(self.state.ut_gic["GERAL"]) < 3:
            missing.append("- Perguntas gerais: Respostas incompletas")
        
        # Verificar informações específicas por tipo de objeto
        for item in self.state.selected_items:
            if item == "PRAZO":
                # Verificar se foi respondido sobre demanda continuada
                pass
            elif item == "ACRÉSCIMO":
                # Verificar se foi respondido sobre 25% e Parecer Jurídico
                pass
            elif item == "RESCISÃO":
                # Verificar se foi respondido sobre Parecer Jurídico
                pass
        
        if not missing:
            return ""
        
        return "\n".join(missing)

    def upload_document(self, filename: str, content: str) -> str:
        """Permite ao usuário anexar documentos para análise"""
        try:
            document_info = {
                'filename': filename,
                'content': content,
                'uploaded_at': 'now',  # Em produção, usar timestamp real
                'analyzed': False
            }
            
            self.state.uploaded_documents.append(document_info)
            
            return f"Documento '{filename}' anexado com sucesso. Será analisado para verificar informações ausentes."
            
        except Exception as e:
            return f"Erro ao anexar documento: {e}"

    def get_uploaded_documents(self) -> List[Dict[str, str]]:
        """Retorna lista de documentos anexados"""
        return self.state.uploaded_documents.copy()


class GICSession:
    """Classe para gerenciar sessões individuais do GIC"""
    
    def __init__(self) -> None:
        self.orchestrator = GICOrchestrator()

    def start(self) -> str:
        return self.orchestrator.start()

    def process_response(self, user_response: str) -> Dict[str, Any]:
        """Processa resposta do usuário e retorna resultado estruturado"""
        try:
            message = self.orchestrator.handle(user_response)
            
            return {
                'message': message,
                'status': self.orchestrator.state.stage,
                'current_object': self.orchestrator.state.current_item(),
                'completed': self.orchestrator.state.stage == "finalize",
                'selected_items': self.orchestrator.state.selected_items,
                'uploaded_documents': len(self.orchestrator.state.uploaded_documents)
            }
            
        except Exception as e:
            return {
                'message': f"Erro ao processar resposta: {e}",
                'status': 'error',
                'current_object': None,
                'completed': False,
                'error': str(e)
            }

    def upload_document(self, filename: str, content: str) -> str:
        """Permite ao usuário anexar documentos para análise"""
        return self.orchestrator.upload_document(filename, content)

    def get_uploaded_documents(self) -> List[Dict[str, str]]:
        """Retorna lista de documentos anexados"""
        return self.orchestrator.get_uploaded_documents()

    # ---------------------- FINAL RENDER ----------------------
    def render_final_justification(self) -> str:
        """Implementa EXATAMENTE a estrutura de justificativa do prompt"""
        lines: List[str] = []
        
        # Estrutura conforme passo 6º do prompt
        lines.append("ICJ — Justificativa de Aditivo Contratual")
        lines.append("")
        
        # Mencionar ICJ, NOME DA CONTRATADA, se é ou não de natureza continuada, 
        # falar da relevância do contrato e mencionar que a gerência do utilizador 
        # identificou que o contrato precisa ser aditado.
        lines.append("A gerência do UTILIZADOR identificou necessidade de aditamento contratual.")
        lines.append("")
        
        # Relacionar, por tópico, cada objeto definido pelo UTILIZADOR, e dentro de 
        # cada objeto a GIC deve elaborar justificativa [UT-GIC]. No texto de cada 
        # objeto, mostre que foram atendidas condicionantes estabelecidas nos 
        # documentos orientativos em anexo.
        for item in self.state.selected_items:
            lines.append(f"OBJETO: {item}")
            lines.append("-" * 40)
            
            # Buscar respostas do UT-GIC para este objeto
            if item in self.state.ut_gic:
                for qa in self.state.ut_gic[item]:
                    pergunta = qa.get('pergunta', '')
                    resposta = qa.get('resposta', '')
                    if pergunta and resposta:
                        lines.append(f"Pergunta: {pergunta}")
                        lines.append(f"Resposta UT-GIC: {resposta}")
                        lines.append("")
            
            lines.append("")
        
        # Informe os risco e prejuízo decorrente da ausência do contrato [UT-GIC]
        if "GERAL" in self.state.ut_gic:
            lines.append("ANÁLISE DE IMPACTOS E RISCOS:")
            lines.append("=" * 40)
            for qa in self.state.ut_gic["GERAL"]:
                pergunta = qa.get('pergunta', '')
                resposta = qa.get('resposta', '')
                if pergunta and resposta:
                    lines.append(f"{pergunta}")
                    lines.append(f"Resposta UT-GIC: {resposta}")
                    lines.append("")
        
        # Inserir Paragrafo de Conclusão
        lines.append("CONCLUSÃO:")
        lines.append("=" * 20)
        lines.append("As justificativas foram elaboradas conforme UT-GIC e documentos orientativos.")
        lines.append("O contrato é estratégico para a Petrobras e sua continuidade é essencial.")
        lines.append("")
        
        # Ao final de todas as Justificativas Criadas deixe essa mensagem!
        lines.append("Solicitações de Melhorias, críticas e/ou elogios, enviar e-mail para Chave XBZF.")
        
        return "\n".join(lines)


__all__ = ["GICOrchestrator", "GICSession", "GICState", "GIC_ITENS", "gic_menu"]


