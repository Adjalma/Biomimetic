#!/usr/bin/env python3
"""
Teste da validação rigorosa - casos específicos que devem ser bloqueados
"""

def simular_validacao_fato_superveniente():
    """Simula como a validação agora bloqueia respostas inadequadas"""
    
    print("=== TESTE VALIDAÇÃO RIGOROSA - FATO SUPERVENIENTE ===\n")
    
    # Casos que DEVEM ser bloqueados
    casos_invalidos = [
        "não sei",
        "nao sei", 
        "desconheço",
        "sem informação",
        "não há",
        "não existe",
        "n/a",
        "indefinido",
        "a definir",
        "pendente",
        "teste",
        "algo genérico",
        "questão operacional"  # muito genérico
    ]
    
    # Casos que DEVEM ser aceitos
    casos_validos = [
        "Necessidade de ampliação do escopo devido à identificação de nova demanda operacional não prevista no contrato original",
        "Surgiu problema técnico na execução que demanda alteração do projeto conforme especificação técnica revisada",
        "Constatou-se mudança regulatória que exige adequação dos procedimentos contratuais para conformidade legal",
        "Verificou-se demanda adicional de serviços devido ao aumento da capacidade produtiva da unidade"
    ]
    
    print("CASOS QUE DEVEM SER BLOQUEADOS:")
    for i, caso in enumerate(casos_invalidos, 1):
        resultado = validar_resposta_simulada(caso, 'fato_superveniente')
        status = "✗ BLOQUEADO" if not resultado['valida'] else "✓ PASSOU (ERRO!)"
        print(f"{i:2d}. '{caso}' → {status}")
        if not resultado['valida']:
            print(f"    Motivo: {resultado['motivo']}")
        print()
    
    print("\nCASOS QUE DEVEM SER ACEITOS:")
    for i, caso in enumerate(casos_validos, 1):
        resultado = validar_resposta_simulada(caso, 'fato_superveniente')
        status = "✓ ACEITO" if resultado['valida'] else "✗ BLOQUEADO (ERRO!)"
        print(f"{i}. '{caso[:60]}...' → {status}")
        print()

def validar_resposta_simulada(resposta: str, tipo: str) -> dict:
    """Simula a validação implementada no sistema"""
    
    if tipo == 'fato_superveniente':
        # Respostas inválidas explícitas
        respostas_invalidas = [
            'não sei', 'nao sei', 'não tenho', 'nao tenho', 'desconheço', 'desconheco',
            'sem informação', 'sem informacao', 'não há', 'nao ha', 'não existe',
            'nao existe', 'não aplicável', 'nao aplicavel', 'n/a', 'na', 'vazio',
            'nenhum', 'nenhuma', 'indefinido', 'a definir', 'pendente', 'aguardando'
        ]
        
        if resposta.lower().strip() in respostas_invalidas:
            return {
                'valida': False,
                'motivo': 'Resposta indica falta de informação sobre o fato superveniente'
            }
        
        if len(resposta) < 15:
            return {
                'valida': False,
                'motivo': 'Descrição muito curta para um fato superveniente'
            }
        
        # Verificar palavras-chave obrigatórias
        palavras_relevantes = [
            'necessidade', 'problema', 'mudança', 'alteração', 'demanda', 'situação', 
            'circunstância', 'evento', 'ocorrência', 'fato', 'surgiu', 'identificou',
            'constatou', 'verificou', 'detectou', 'emergiu', 'aconteceu', 'ocorreu'
        ]
        
        if not any(palavra in resposta.lower() for palavra in palavras_relevantes):
            return {
                'valida': False,
                'motivo': 'Resposta não contém elementos que caracterizam um fato superveniente'
            }
        
        # Verificar se não são apenas palavras genéricas
        palavras_genericas = ['coisa', 'algo', 'questão', 'assunto', 'item', 'parte', 'aspecto']
        if any(palavra in resposta.lower() for palavra in palavras_genericas) and len(resposta) < 30:
            return {
                'valida': False,
                'motivo': 'Descrição muito genérica para um fato superveniente'
            }
        
        return {'valida': True}
    
    return {'valida': True}

def demonstrar_fluxo_api():
    """Demonstra como a API agora responde a respostas inválidas"""
    
    print("=== DEMONSTRAÇÃO DO FLUXO DA API ===\n")
    
    print("CENÁRIO: Usuário responde 'não sei' para fato superveniente")
    print()
    
    # Simulação da resposta da API
    resposta_api = {
        "status": "erro_validacao",
        "motivo": "Resposta indica falta de informação sobre o fato superveniente",
        "sugestao": "É obrigatório informar o fato superveniente que justifica o aditivo. Consulte a documentação do contrato ou a área técnica responsável.",
        "pergunta_atual": {
            "pergunta": "Qual o fato Superveniente?",
            "validacao": "fato_superveniente"
        }
    }
    
    print("RESPOSTA DA API:")
    print(f"Status: {resposta_api['status']}")
    print(f"Motivo: {resposta_api['motivo']}")
    print(f"Sugestão: {resposta_api['sugestao']}")
    print()
    print("RESULTADO: O fluxo NÃO avança até o usuário fornecer uma resposta adequada!")
    print()

if __name__ == "__main__":
    simular_validacao_fato_superveniente()
    demonstrar_fluxo_api()
