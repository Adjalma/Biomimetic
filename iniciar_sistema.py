#!/usr/bin/env python3
"""
SCRIPT DE INICIALIZAÇÃO DO SISTEMA
==================================

Script principal para inicializar o sistema de IA autoevolutiva.
Este script facilita o acesso aos diferentes componentes do sistema.

Uso:
    python iniciar_sistema.py [opcao]

Opções:
    main        - Executar sistema principal
    optimized   - Executar versão otimizada
    gic         - Executar dashboard GIC
    gic-ia      - Executar GIC com IA integrada
    validate    - Validar sistema
    help        - Mostrar ajuda
"""

import os
import sys
import subprocess
from pathlib import Path

def mostrar_ajuda():
    """Mostra a ajuda do sistema"""
    print("""
🧠 SISTEMA DE IA AUTOEVOLUTIVA BIOMIMÉTICA
==========================================

COMANDOS DISPONÍVEIS:

1. Sistema Principal:
   python iniciar_sistema.py main
   - Executa o sistema principal da IA autoevolutiva
   - Localização: src/app/main.py

2. Versão Otimizada:
   python iniciar_sistema.py optimized
   - Executa a versão otimizada para hardware dedicado
   - Localização: src/app/main_optimized.py

3. Dashboard GIC:
   python iniciar_sistema.py gic
   - Inicia o dashboard web do GIC
   - Localização: src/app/app_gic.py

4. GIC com IA Integrada:
   python iniciar_sistema.py gic-ia
   - Inicia o GIC com IA autoevolutiva integrada
   - Localização: src/app/iniciar_gic_ia.py

5. Validação do Sistema:
   python iniciar_sistema.py validate
   - Executa validação completa do sistema
   - Localização: scripts/validar_sistema.py

6. Ajuda:
   python iniciar_sistema.py help
   - Mostra esta mensagem de ajuda

ESTRUTURA DO SISTEMA:
- src/app/          - Aplicações principais
- src/core/         - Núcleo da IA evolutiva
- src/faiss_engine/ - Sistema FAISS
- src/knowledge_bus/ - Barramento de conhecimento
- src/systems/      - Sistemas V2 integrados
- src/pipelines/    - Pipelines de processamento
- storage/          - Dados persistentes
- tests/            - Testes automatizados
- scripts/          - Scripts de execução

Para mais informações, consulte o README.md
""")

def executar_comando(comando, arquivo):
    """Executa um comando Python"""
    try:
        print(f"🚀 Executando: {comando}")
        print(f"📁 Arquivo: {arquivo}")
        print("=" * 50)
        
        # Verificar se o arquivo existe
        if not os.path.exists(arquivo):
            print(f"❌ Erro: Arquivo não encontrado: {arquivo}")
            return False
        
        # Executar o comando
        result = subprocess.run([sys.executable, arquivo], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ Comando executado com sucesso!")
            return True
        else:
            print(f"❌ Erro na execução: código {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("❌ Erro: Opção não especificada")
        print("Use: python iniciar_sistema.py help")
        return 1
    
    opcao = sys.argv[1].lower()
    
    # Mapear opções para arquivos
    comandos = {
        'main': 'src/app/main.py',
        'optimized': 'src/app/main_optimized.py',
        'gic': 'src/app/app_gic.py',
        'gic-ia': 'src/app/iniciar_gic_ia.py',
        'validate': 'scripts/validar_sistema.py',
        'help': None
    }
    
    if opcao == 'help':
        mostrar_ajuda()
        return 0
    
    if opcao not in comandos:
        print(f"❌ Erro: Opção inválida: {opcao}")
        print("Use: python iniciar_sistema.py help")
        return 1
    
    arquivo = comandos[opcao]
    
    if arquivo is None:
        mostrar_ajuda()
        return 0
    
    # Executar comando
    sucesso = executar_comando(opcao, arquivo)
    return 0 if sucesso else 1

if __name__ == "__main__":
    sys.exit(main())
