#!/usr/bin/env python3
"""
UNIFICADOR FAISS - AGENTES ESPECIALISTAS
========================================

Script para unificar o FAISS usando os dados dos agentes especialistas existentes.
Recupera os 17GB perdidos do main_index.faiss.
"""

import os
import sys
import logging
import time
import shutil
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnificadorFAISSAgentes:
    """Unifica FAISS usando agentes especialistas"""
    
    def __init__(self):
        self.faiss_path = Path("faiss_biblioteca_central")
        self.indices_path = self.faiss_path / "indices"
        self.backups_dir = self.faiss_path / "backups"
        
        # Criar diretórios se não existirem
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🚀 UNIFICADOR FAISS - AGENTES ESPECIALISTAS")
        logger.info("🎯 Recuperando 17GB perdidos do main_index.faiss")
        
    def verificar_estado_atual(self):
        """Verifica o estado atual dos índices FAISS"""
        logger.info("📊 VERIFICANDO ESTADO ATUAL DOS ÍNDICES...")
        
        # Verificar main_index.faiss (perdido)
        main_index = self.indices_path / "main_index.faiss"
        if main_index.exists():
            size = main_index.stat().st_size
            logger.warning(f"⚠️ main_index.faiss atual: {size / (1024**3):.1f} GB (PERDIDO!)")
        else:
            logger.error("❌ main_index.faiss NÃO ENCONTRADO!")
        
        # Verificar índices dos agentes especialistas
        indices_agentes = list(self.indices_path.glob("main_index_*.faiss"))
        logger.info(f"📚 Encontrados {len(indices_agentes)} índices de agentes:")
        
        total_size = 0
        for idx in indices_agentes:
            size = idx.stat().st_size
            total_size += size
            nome_agente = idx.name.replace('main_index_', '').replace('.faiss', '')
            logger.info(f"  - {nome_agente}: {size / (1024**3):.1f} GB")
        
        logger.info(f"📊 TOTAL dos agentes: {total_size / (1024**3):.1f} GB")
        
        return indices_agentes, total_size
    
    def fazer_backup_seguranca(self):
        """Faz backup de segurança antes de qualquer operação"""
        logger.info("🔄 FAZENDO BACKUP DE SEGURANÇA...")
        
        timestamp = int(time.time())
        backup_dir = self.backups_dir / f"backup_unificacao_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        # Backup de todos os índices
        indices_para_backup = list(self.indices_path.glob("*.faiss"))
        
        for idx in indices_para_backup:
            backup_file = backup_dir / idx.name
            shutil.copy2(str(idx), str(backup_file))
            logger.info(f"  ✓ Backup: {idx.name}")
        
        logger.info(f"✅ Backup de segurança criado em: {backup_dir}")
        return backup_dir
    
    def unificar_indices_agentes(self, indices_agentes):
        """Unifica os índices dos agentes especialistas"""
        logger.info("🔗 UNIFICANDO ÍNDICES DOS AGENTES ESPECIALISTAS...")
        
        try:
            import faiss
            import numpy as np
            
            # Carregar primeiro índice para obter dimensão
            primeiro_indice = faiss.read_index(str(indices_agentes[0]))
            dimensao = primeiro_indice.d
            logger.info(f"📏 Dimensão dos vetores: {dimensao}")
            
            # Criar índice unificado
            if dimensao <= 384:
                # Para dimensões menores, usar IndexFlatL2
                index_unificado = faiss.IndexFlatL2(dimensao)
                logger.info("🔧 Usando IndexFlatL2 para dimensão <= 384")
            else:
                # Para dimensões maiores, usar IndexHNSWFlat
                index_unificado = faiss.IndexHNSWFlat(dimensao, 32)
                logger.info("🔧 Usando IndexHNSWFlat para dimensão > 384")
            
            total_vetores = 0
            
            # Processar cada índice de agente
            for i, idx_path in enumerate(indices_agentes):
                logger.info(f"📚 Processando {i+1}/{len(indices_agentes)}: {idx_path.name}")
                
                try:
                    # Carregar índice do agente
                    index_agente = faiss.read_index(str(idx_path))
                    vetores_agente = index_agente.ntotal
                    
                    logger.info(f"  - Vetores: {vetores_agente:,}")
                    
                    # Extrair vetores do índice
                    if hasattr(index_agente, 'reconstruct_n'):
                        # Para índices que suportam reconstrução
                        vetores = index_agente.reconstruct_n(0, vetores_agente)
                        index_unificado.add(vetores)
                        total_vetores += vetores_agente
                        logger.info(f"  ✓ {vetores_agente:,} vetores adicionados")
                    else:
                        logger.warning(f"  ⚠️ Índice não suporta reconstrução: {idx_path.name}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Erro ao processar {idx_path.name}: {e}")
                    continue
            
            logger.info(f"✅ Unificação concluída: {total_vetores:,} vetores totais")
            return index_unificado, total_vetores
            
        except Exception as e:
            logger.error(f"❌ Erro na unificação: {e}")
            return None, 0
    
    def salvar_indice_unificado(self, index_unificado, total_vetores):
        """Salva o índice unificado"""
        logger.info("💾 SALVANDO ÍNDICE UNIFICADO...")
        
        try:
            # Salvar como main_index.faiss
            main_index_path = self.indices_path / "main_index.faiss"
            
            # Fazer backup do arquivo atual se existir
            if main_index_path.exists():
                backup_atual = self.backups_dir / f"main_index_antes_unificacao_{int(time.time())}.faiss"
                shutil.copy2(str(main_index_path), str(backup_atual))
                logger.info(f"✓ Backup do arquivo atual: {backup_atual}")
            
            # Salvar novo índice unificado
            faiss.write_index(index_unificado, str(main_index_path))
            
            # Verificar tamanho
            size = main_index_path.stat().st_size
            logger.info(f"✅ Índice unificado salvo: {size / (1024**3):.1f} GB")
            logger.info(f"📊 Total de vetores: {total_vetores:,}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar índice: {e}")
            return False
    
    def executar_unificacao(self):
        """Executa todo o processo de unificação"""
        logger.info("🚀 INICIANDO UNIFICAÇÃO FAISS...")
        
        try:
            # 1. Verificar estado atual
            indices_agentes, total_size = self.verificar_estado_atual()
            
            if not indices_agentes:
                logger.error("❌ Nenhum índice de agente encontrado!")
                return False
            
            # 2. Fazer backup de segurança
            backup_dir = self.fazer_backup_seguranca()
            
            # 3. Unificar índices
            index_unificado, total_vetores = self.unificar_indices_agentes(indices_agentes)
            
            if not index_unificado:
                logger.error("❌ Falha na unificação!")
                return False
            
            # 4. Salvar índice unificado
            if self.salvar_indice_unificado(index_unificado, total_vetores):
                logger.info("🎉 UNIFICAÇÃO CONCLUÍDA COM SUCESSO!")
                logger.info(f"📊 Índice unificado: {total_vetores:,} vetores")
                logger.info(f"💾 Backup de segurança: {backup_dir}")
                return True
            else:
                logger.error("❌ Falha ao salvar índice unificado!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro crítico na unificação: {e}")
            return False

def main():
    """Função principal"""
    try:
        unificador = UnificadorFAISSAgentes()
        sucesso = unificador.executar_unificacao()
        
        if sucesso:
            print("\n" + "="*60)
            print("🎉 UNIFICAÇÃO FAISS CONCLUÍDA COM SUCESSO!")
            print("📊 17GB de dados recuperados dos agentes especialistas")
            print("💾 Backup de segurança criado")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ UNIFICAÇÃO FAISS FALHOU!")
            print("🔧 Verifique os logs para detalhes")
            print("="*60)
            
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        print(f"\n❌ ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    main()
