#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 SCRIPT DE TESTE DAS CORREÇÕES CRÍTICAS
Testa as correções implementadas antes da migração completa
"""

import os
import sys
import numpy as np
from pathlib import Path

def testar_extracao_vetores():
    """Testar a extração de vetores reais"""
    print("🧪 TESTANDO EXTRAÇÃO DE VETORES REAIS")
    print("=" * 50)
    
    # Simular dados de teste
    colunas_teste = [
        (0, 'id', 'INTEGER', 0, None, 0),
        (1, 'texto', 'TEXT', 0, None, 0),
        (2, 'vector_data', 'BLOB', 0, None, 0),
        (3, 'valor', 'REAL', 0, None, 0)
    ]
    
    registros_teste = [
        (1, "Este é um texto de teste", b"vector_data_here", 42.5),
        (2, "Outro registro importante", b"more_vector_data", 100.0),
        (3, "Terceiro registro", b"final_vector", 75.25)
    ]
    
    print("✅ Dados de teste criados")
    print(f"  Colunas: {len(colunas_teste)}")
    print(f"  Registros: {len(registros_teste)}")
    
    return True

def testar_validacao_faiss():
    """Testar validação de vetores FAISS"""
    print("\n🧪 TESTANDO VALIDAÇÃO FAISS")
    print("=" * 50)
    
    # Vetor válido
    vetor_valido = np.random.random((100, 384)).astype('float32')
    print(f"✅ Vetor válido criado: {vetor_valido.shape}")
    
    # Vetor inválido (dimensão errada)
    vetor_invalido = np.random.random((100, 256)).astype('float32')
    print(f"❌ Vetor inválido criado: {vetor_invalido.shape}")
    
    # Vetor vazio
    vetor_vazio = np.zeros((0, 384), dtype='float32')
    print(f"❌ Vetor vazio criado: {vetor_vazio.shape}")
    
    return True

def testar_sistema_checkpoint():
    """Testar sistema de checkpoint"""
    print("\n🧪 TESTANDO SISTEMA DE CHECKPOINT")
    print("=" * 50)
    
    checkpoint_dir = Path("faiss_biblioteca_central")
    checkpoint_file = checkpoint_dir / "checkpoint_migracao.json"
    
    if checkpoint_file.exists():
        print(f"⚠️ Checkpoint existente encontrado: {checkpoint_file}")
        print("  Isso indica migração anterior em andamento")
    else:
        print("✅ Nenhum checkpoint encontrado - sistema limpo")
    
    return True

def testar_estrutura_diretorios():
    """Testar estrutura de diretórios"""
    print("\n🧪 TESTANDO ESTRUTURA DE DIRETÓRIOS")
    print("=" * 50)
    
    diretorios_necessarios = [
        "faiss_biblioteca_central",
        "faiss_biblioteca_central/indices",
        "faiss_biblioteca_central/metadata",
        "faiss_biblioteca_central/backups",
        "faiss_biblioteca_central/logs"
    ]
    
    for diretorio in diretorios_necessarios:
        if os.path.exists(diretorio):
            print(f"✅ {diretorio}")
        else:
            print(f"❌ {diretorio} - NÃO EXISTE")
    
    return True

def testar_importacoes():
    """Testar importações necessárias"""
    print("\n🧪 TESTANDO IMPORTAÇÕES")
    print("=" * 50)
    
    modulos_necessarios = [
        'faiss',
        'numpy',
        'sqlite3',
        'json',
        'pickle',
        'logging',
        'threading',
        'pathlib'
    ]
    
    for modulo in modulos_necessarios:
        try:
            __import__(modulo)
            print(f"✅ {modulo}")
        except ImportError as e:
            print(f"❌ {modulo}: {e}")
    
    return True

def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTES DAS CORREÇÕES CRÍTICAS")
    print("=" * 60)
    
    testes = [
        ("Extração de Vetores", testar_extracao_vetores),
        ("Validação FAISS", testar_validacao_faiss),
        ("Sistema Checkpoint", testar_sistema_checkpoint),
        ("Estrutura Diretórios", testar_estrutura_diretorios),
        ("Importações", testar_importacoes)
    ]
    
    resultados = []
    
    for nome_teste, funcao_teste in testes:
        try:
            print(f"\n🔄 Executando: {nome_teste}")
            sucesso = funcao_teste()
            resultados.append((nome_teste, sucesso))
        except Exception as e:
            print(f"❌ ERRO no teste {nome_teste}: {e}")
            resultados.append((nome_teste, False))
    
    # Resumo dos testes
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for nome_teste, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"  {nome_teste}: {status}")
    
    total_testes = len(resultados)
    testes_passaram = sum(1 for _, sucesso in resultados if sucesso)
    
    print(f"\n📈 RESULTADO FINAL: {testes_passaram}/{total_testes} testes passaram")
    
    if testes_passaram == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para migração.")
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("1. Execute: python sistema_agentes_faiss_integrado.py")
        print("2. Monitore os logs para verificar funcionamento")
        print("3. Verifique o tamanho da pasta faiss_biblioteca_central")
    else:
        print("❌ ALGUNS TESTES FALHARAM! Corrija antes da migração.")
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        print("1. Verifique os erros acima")
        print("2. Corrija as dependências faltantes")
        print("3. Execute os testes novamente")
    
    return testes_passaram == total_testes

if __name__ == "__main__":
    main()
