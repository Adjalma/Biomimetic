#!/usr/bin/env python3
"""
Verificador de Integridade FAISS - Monitoramento em Tempo Real
==============================================================

Este script verifica a integridade dos índices FAISS durante a criação
e previne corrupção com validações contínuas.
"""

import os
import time
import hashlib
from pathlib import Path
import numpy as np

class VerificadorIntegridadeFAISS:
    def __init__(self):
        """Inicializa o verificador de integridade"""
        self.faiss_path = Path("faiss_biblioteca_central")
        self.indices_path = self.faiss_path / "indices"
        self.log_file = "verificacao_integridade.log"
        
        print("=" * 60)
        print("VERIFICADOR DE INTEGRIDADE FAISS")
        print("=" * 60)
    
    def verificar_indice_tempo_real(self, arquivo_path, timeout_minutos=10):
        """Verifica um índice em tempo real durante a criação"""
        print(f"\n🔍 VERIFICANDO ÍNDICE EM TEMPO REAL: {arquivo_path.name}")
        
        inicio = time.time()
        ultimo_tamanho = 0
        verificacoes = 0
        
        while time.time() - inicio < timeout_minutos * 60:
            try:
                if not arquivo_path.exists():
                    print(f"  ⏳ Aguardando criação do arquivo...")
                    time.sleep(5)
                    continue
                
                # Verificar tamanho atual
                tamanho_atual = arquivo_path.stat().st_size
                tempo_decorrido = time.time() - inicio
                
                if tamanho_atual > ultimo_tamanho:
                    print(f"  📈 Crescimento detectado: {tamanho_atual / (1024**2):.1f} MB (+{tempo_decorrido:.0f}s)")
                    ultimo_tamanho = tamanho_atual
                    
                    # Verificar integridade básica
                    if self._verificar_integridade_basica(arquivo_path):
                        print(f"    ✅ Integridade básica: OK")
                    else:
                        print(f"    ❌ Integridade básica: FALHOU")
                        return False
                    
                    verificacoes += 1
                
                # Verificar se o arquivo parou de crescer (possível finalização)
                if tamanho_atual > 0 and tamanho_atual == ultimo_tamanho:
                    print(f"  ⏸️ Arquivo estabilizou em: {tamanho_atual / (1024**2):.1f} MB")
                    
                    # Aguardar um pouco para confirmar finalização
                    time.sleep(10)
                    
                    # Verificação final
                    if self._verificacao_final(arquivo_path):
                        print(f"  🎉 VERIFICAÇÃO FINAL: SUCESSO!")
                        return True
                    else:
                        print(f"  ❌ VERIFICAÇÃO FINAL: FALHOU!")
                        return False
                
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Erro durante verificação: {e}")
                time.sleep(5)
        
        print(f"  ⏰ Timeout atingido ({timeout_minutos} minutos)")
        return False
    
    def _verificar_integridade_basica(self, arquivo_path):
        """Verifica integridade básica do arquivo"""
        try:
            # Verificar tamanho mínimo
            if arquivo_path.stat().st_size < 100:
                return False
            
            # Verificar se não é apenas zeros
            with open(arquivo_path, 'rb') as f:
                # Ler primeiros bytes
                header = f.read(100)
                if not header or len(header) < 10:
                    return False
                
                # Verificar se não é apenas zeros
                if all(b == 0 for b in header):
                    return False
                
                # Verificar se não é apenas um byte repetido
                if len(set(header)) < 3:
                    return False
            
            return True
            
        except Exception as e:
            print(f"    ⚠️ Erro na verificação básica: {e}")
            return False
    
    def _verificacao_final(self, arquivo_path):
        """Verificação final completa do arquivo"""
        try:
            tamanho = arquivo_path.stat().st_size
            print(f"    📏 Tamanho final: {tamanho / (1024**2):.1f} MB")
            
            # Verificar se o tamanho é razoável
            if tamanho < 1000:
                print(f"    ❌ Arquivo muito pequeno: {tamanho} bytes")
                return False
            
            # Verificar se pode ser lido pelo FAISS
            try:
                import faiss
                indice = faiss.read_index(str(arquivo_path))
                vetores = indice.ntotal
                dimensao = indice.d
                
                print(f"    ✅ FAISS pode ler o arquivo")
                print(f"    📊 Vetores: {vetores:,}")
                print(f"    📐 Dimensão: {dimensao}")
                
                # Verificar se tem vetores válidos
                if vetores > 0 and dimensao > 0:
                    return True
                else:
                    print(f"    ❌ Índice vazio ou inválido")
                    return False
                    
            except Exception as e:
                print(f"    ❌ FAISS não consegue ler: {e}")
                return False
                
        except Exception as e:
            print(f"    ❌ Erro na verificação final: {e}")
            return False
    
    def monitorar_criacao_indices(self, indices_para_criar):
        """Monitora a criação de múltiplos índices"""
        print(f"\n🚀 MONITORANDO CRIAÇÃO DE {len(indices_para_criar)} ÍNDICES...")
        
        resultados = {}
        
        for nome_agente in indices_para_criar:
            arquivo_path = self.indices_path / f"main_index_{nome_agente}.faiss"
            
            print(f"\n📋 Monitorando: {nome_agente}")
            
            if self.verificar_indice_tempo_real(arquivo_path):
                resultados[nome_agente] = "SUCESSO"
                print(f"  ✅ {nome_agente}: CRIADO COM SUCESSO")
            else:
                resultados[nome_agente] = "FALHA"
                print(f"  ❌ {nome_agente}: FALHOU NA CRIAÇÃO")
            
            # Pausa entre agentes
            time.sleep(3)
        
        # Resumo final
        print(f"\n📊 RESUMO FINAL DO MONITORAMENTO:")
        sucessos = sum(1 for r in resultados.values() if r == "SUCESSO")
        falhas = sum(1 for r in resultados.values() if r == "FALHA")
        
        print(f"  ✅ Sucessos: {sucessos}")
        print(f"  ❌ Falhas: {falhas}")
        print(f"  📁 Total: {len(indices_para_criar)}")
        
        return resultados

def main():
    """Função principal para teste"""
    verificador = VerificadorIntegridadeFAISS()
    
    # Lista de agentes para monitorar (os corrompidos)
    agentes_corrompidos = ['contract', 'financial', 'jurist', 'legal', 'maestro']
    
    print(f"Agentes a serem monitorados: {', '.join(agentes_corrompidos)}")
    
    # Simular monitoramento
    resultados = verificador.monitorar_criacao_indices(agentes_corrompidos)
    
    print(f"\n🎯 RESULTADO FINAL:")
    for agente, resultado in resultados.items():
        status_emoji = "✅" if resultado == "SUCESSO" else "❌"
        print(f"  {status_emoji} {agente}: {resultado}")

if __name__ == "__main__":
    main()
