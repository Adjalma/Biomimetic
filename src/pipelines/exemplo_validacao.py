#!/usr/bin/env python3
"""
Exemplo prático do sistema de validação implementado
"""

def exemplo_fluxo_validacao():
    """Demonstra como o sistema de validação funciona no fluxo"""
    
    print("=== EXEMPLO DO SISTEMA DE VALIDAÇÃO ===\n")
    
    # Simulação de resposta da API quando validação falha
    resposta_validacao_falha = {
        "status": "erro_validacao",
        "motivo": "Resposta deve ser 'sim' ou 'não'",
        "sugestao": "Por favor, responda com 'sim' ou 'não'.",
        "pergunta_atual": {
            "pergunta": "O acréscimo supera 25%, considerando os aditivos já realizados no contrato?",
            "proximo_passo": "verificar_parecer_25",
            "validacao": "sim_nao",
            "opcoes_validas": ["sim", "não", "nao", "s", "n"]
        }
    }
    
    # Simulação de resposta da API quando validação passa
    resposta_validacao_sucesso = {
        "status": "continuar",
        "proxima_pergunta": {
            "pergunta": "⚠️ ATENÇÃO: O acréscimo supera 25% do valor original. Conforme exigência legal, é OBRIGATÓRIO o Parecer Jurídico (PJUR). Você já possui o parecer jurídico?",
            "proximo_passo": "parecer_juridico",
            "tipo": "obrigatorio_pjur"
        }
    }
    
    print("1. CENÁRIO: Usuário responde 'talvez' para pergunta sim/não")
    print("   Resposta da API:")
    print(f"   Status: {resposta_validacao_falha['status']}")
    print(f"   Motivo: {resposta_validacao_falha['motivo']}")
    print(f"   Sugestão: {resposta_validacao_falha['sugestao']}")
    print()
    
    print("2. CENÁRIO: Usuário responde 'sim' (resposta válida)")
    print("   Resposta da API:")
    print(f"   Status: {resposta_validacao_sucesso['status']}")
    print(f"   Próxima pergunta: {resposta_validacao_sucesso['proxima_pergunta']['pergunta'][:80]}...")
    print()
    
    print("=== TIPOS DE VALIDAÇÃO IMPLEMENTADOS ===")
    validacoes = [
        ("sim_nao", "Valida respostas sim/não", ["sim", "não", "s", "n"]),
        ("tipo_acrescimo", "Valida tipo de acréscimo", ["quantidade", "novo item", "ppu"]),
        ("fato_superveniente", "Valida descrição de fato superveniente", ["mínimo 10 caracteres", "palavras-chave relevantes"]),
        ("texto_livre", "Valida texto descritivo", ["mínimo 5 caracteres", "não apenas números"]),
        ("generica", "Validação geral", ["mínimo 3 caracteres", "não respostas nonsense"])
    ]
    
    for tipo, descricao, criterios in validacoes:
        print(f"• {tipo}: {descricao}")
        print(f"  Critérios: {', '.join(criterios)}")
        print()

if __name__ == "__main__":
    exemplo_fluxo_validacao()
