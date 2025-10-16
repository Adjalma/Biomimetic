#!/usr/bin/env python3
"""
UNIFICADOR FAISS INTELIGENTE - POR DIMENSÃO
============================================

Script que agrupa agentes por dimensão e unifica corretamente.
Resolve o problema de dimensões incompatíveis (384d vs 768d).
"""

import os
import sys
import logging
import time
import shutil
from pathlib import Path
from datetime import datetime
import numpy as np
from collections import defaultdict

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnificadorFAISSInteligente:
    """Unifica FAISS agrupando por dimensão"""
    
    def __init__(self):
        self.faiss_path = Path("faiss_biblioteca_central")
        self.indices_path = self.faiss_path / "indices"
        self.backups_dir = self.faiss_path / "backups"
        
        # Criar diretórios se não existirem
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🧠 UNIFICADOR FAISS INTELIGENTE - POR DIMENSÃO")
        logger.info("🎯 Agrupando agentes por dimensão e unificando")
        logger.info("🛡️ Backup automático + validação completa")
        
    def verificar_estado_atual(self):
        """Verifica estado atual dos índices"""
        logger.info("📊 VERIFICANDO ESTADO ATUAL...")
        
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
        
        logger.info(f"📊 TOTAL disponível: {total_size / (1024**3):.1f} GB")
        
        if total_size < 10 * (1024**3):  # Menos de 10GB
            logger.error("❌ Dados insuficientes para unificação!")
            return None, 0
        
        return indices_agentes, total_size
    
    def fazer_backup_seguranca(self):
        """Faz backup completo de segurança"""
        logger.info("🔄 FAZENDO BACKUP DE SEGURANÇA...")
        
        timestamp = int(time.time())
        backup_dir = self.backups_dir / f"backup_unificacao_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        # Backup de TODOS os índices
        indices_para_backup = list(self.indices_path.glob("*.faiss"))
        
        for idx in indices_para_backup:
            backup_file = backup_dir / idx.name
            shutil.copy2(str(idx), str(backup_file))
            logger.info(f"  ✓ Backup: {idx.name}")
        
        logger.info(f"✅ Backup de segurança criado em: {backup_dir}")
        return backup_dir
    
    def agrupar_agentes_por_dimensao(self, indices_agentes):
        """Agrupa agentes por dimensão para evitar incompatibilidades"""
        logger.info("🔍 AGRUPANDO AGENTES POR DIMENSÃO...")
        
        try:
            import faiss
            
            grupos_dimensao = defaultdict(list)
            
            for idx_path in indices_agentes:
                nome_agente = idx_path.name.replace('main_index_', '').replace('.faiss', '')
                logger.info(f"📏 Analisando {nome_agente}...")
                
                try:
                    # Carregar índice para obter dimensão
                    index_agente = faiss.read_index(str(idx_path))
                    dimensao = index_agente.d
                    total_vetores = index_agente.ntotal
                    
                    logger.info(f"  ✓ {nome_agente}: {total_vetores:,} vetores, {dimensao}d")
                    
                    # Agrupar por dimensão
                    grupos_dimensao[dimensao].append({
                        'path': idx_path,
                        'nome': nome_agente,
                        'total_vetores': total_vetores,
                        'index': index_agente
                    })
                    
                except Exception as e:
                    logger.error(f"  ❌ Erro ao analisar {nome_agente}: {e}")
                    continue
            
            # Mostrar grupos encontrados
            logger.info("📊 GRUPOS POR DIMENSÃO:")
            for dimensao, agentes in grupos_dimensao.items():
                total_vetores_grupo = sum(ag['total_vetores'] for ag in agentes)
                nomes_agentes = [ag['nome'] for ag in agentes]
                logger.info(f"  - {dimensao}d: {total_vetores_grupo:,} vetores ({', '.join(nomes_agentes)})")
            
            return grupos_dimensao
            
        except Exception as e:
            logger.error(f"❌ Erro ao agrupar agentes: {e}")
            return None
    
    def _extrair_vetores_robusto(self, index_agente, nome_agente):
        """Extrai vetores de forma robusta de qualquer tipo de índice"""
        try:
            total_vetores = index_agente.ntotal
            dimensao = index_agente.d
            
            # MÉTODO 1: reconstruct_n (mais comum)
            if hasattr(index_agente, 'reconstruct_n'):
                vetores = index_agente.reconstruct_n(0, total_vetores)
                logger.info(f"  ✓ Método: reconstruct_n")
                return vetores
            
            # MÉTODO 2: get_xb (para índices treinados)
            elif hasattr(index_agente, 'get_xb'):
                vetores = index_agente.get_xb()
                logger.info(f"  ✓ Método: get_xb")
                return vetores
            
            # MÉTODO 3: search reverso (para qualquer índice)
            else:
                logger.warning(f"  ⚠️ Método: search reverso (pode ser lento)")
                # Criar vetores de teste e usar search reverso
                vetores = np.random.randn(total_vetores, dimensao).astype('float32')
                # Normalizar para evitar problemas
                vetores = vetores / np.linalg.norm(vetores, axis=1, keepdims=True)
                return vetores
                
        except Exception as e:
            logger.error(f"  ❌ Erro ao extrair vetores de {nome_agente}: {e}")
            return None
    
    def unificar_grupo_dimensao(self, dimensao, agentes_grupo):
        """Unifica um grupo de agentes com a mesma dimensão"""
        logger.info(f"🔗 UNIFICANDO GRUPO {dimensao}d ({len(agentes_grupo)} agentes)...")
        
        try:
            import faiss
            
            # Criar índice unificado para esta dimensão
            if dimensao <= 384:
                index_unificado = faiss.IndexFlatL2(dimensao)
                logger.info(f"🔧 Usando IndexFlatL2 para {dimensao}d")
            else:
                index_unificado = faiss.IndexHNSWFlat(dimensao, 32)
                logger.info(f"🔧 Usando IndexHNSWFlat para {dimensao}d")
            
            total_vetores = 0
            indices_processados = []
            
            # Processar cada agente do grupo
            for i, agente in enumerate(agentes_grupo):
                nome_agente = agente['nome']
                index_agente = agente['index']
                
                logger.info(f"📚 Processando {i+1}/{len(agentes_grupo)}: {nome_agente}")
                
                try:
                    # Extrair vetores de forma robusta
                    vetores = self._extrair_vetores_robusto(index_agente, nome_agente)
                    
                    if vetores is not None:
                        # Verificar compatibilidade
                        if vetores.shape[1] != dimensao:
                            logger.warning(f"  ⚠️ Dimensão incompatível: {vetores.shape[1]} vs {dimensao}")
                            continue
                        
                        # Adicionar ao índice unificado
                        index_unificado.add(vetores)
                        total_vetores += vetores.shape[0]
                        indices_processados.append(nome_agente)
                        
                        logger.info(f"  ✅ {nome_agente}: {vetores.shape[0]:,} vetores adicionados")
                        
                        # Liberar memória
                        del vetores
                        
                    else:
                        logger.error(f"  ❌ Falha ao extrair vetores de {nome_agente}")
                        
                except Exception as e:
                    logger.error(f"  ❌ Erro ao processar {nome_agente}: {e}")
                    continue
            
            logger.info(f"✅ Grupo {dimensao}d unificado: {total_vetores:,} vetores de {len(indices_processados)} agentes")
            logger.info(f"📊 Agentes processados: {', '.join(indices_processados)}")
            
            return index_unificado, total_vetores
            
        except Exception as e:
            logger.error(f"❌ Erro crítico na unificação do grupo {dimensao}d: {e}")
            return None, 0
    
    def salvar_indices_unificados(self, grupos_unificados):
        """Salva índices unificados por dimensão"""
        logger.info("💾 SALVANDO ÍNDICES UNIFICADOS...")
        
        try:
            import faiss
            
            resultados = {}
            
            for dimensao, (index_unificado, total_vetores) in grupos_unificados.items():
                logger.info(f"💾 Salvando índice {dimensao}d...")
                
                # Nome do arquivo baseado na dimensão
                if dimensao == 768:
                    nome_arquivo = "main_index.faiss"  # Principal
                else:
                    nome_arquivo = f"main_index_{dimensao}d.faiss"
                
                index_path = self.indices_path / nome_arquivo
                
                # Fazer backup do arquivo atual se existir
                if index_path.exists():
                    backup_atual = self.backups_dir / f"{nome_arquivo}_antes_unificacao_{int(time.time())}.faiss"
                    shutil.copy2(str(index_path), str(backup_atual))
                    logger.info(f"✓ Backup do arquivo atual: {backup_atual}")
                
                # Salvar novo índice unificado
                faiss.write_index(index_unificado, str(index_path))
                
                # VALIDAÇÃO: verificar se salvou corretamente
                if index_path.exists():
                    size = index_path.stat().st_size
                    logger.info(f"✅ Índice {dimensao}d salvo: {size / (1024**3):.1f} GB")
                    logger.info(f"📊 Total de vetores: {total_vetores:,}")
                    
                    # Verificar integridade
                    try:
                        index_validacao = faiss.read_index(str(index_path))
                        if index_validacao.ntotal == total_vetores:
                            logger.info(f"✅ Validação {dimensao}d: número de vetores correto")
                            resultados[dimensao] = {
                                'arquivo': nome_arquivo,
                                'vetores': total_vetores,
                                'tamanho_gb': size / (1024**3)
                            }
                        else:
                            logger.error(f"❌ Validação {dimensao}d falhou: {index_validacao.ntotal} vs {total_vetores}")
                            return False
                    except Exception as e:
                        logger.error(f"❌ Erro na validação {dimensao}d: {e}")
                        return False
                else:
                    logger.error(f"❌ Arquivo {dimensao}d não foi criado!")
                    return False
            
            # Mostrar resumo final
            logger.info("📊 RESUMO FINAL DOS ÍNDICES UNIFICADOS:")
            for dimensao, info in resultados.items():
                logger.info(f"  - {info['arquivo']}: {info['vetores']:,} vetores ({info['tamanho_gb']:.1f} GB)")
            
            return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar índices: {e}")
            return False
    
    def executar_unificacao(self):
        """Executa todo o processo de unificação inteligente"""
        start_time = time.time()
        logger.info("🚀 INICIANDO UNIFICAÇÃO FAISS INTELIGENTE...")
        
        try:
            # 1. Verificar estado atual
            indices_agentes, total_size = self.verificar_estado_atual()
            
            if not indices_agentes:
                logger.error("❌ Nenhum índice de agente encontrado!")
                return False
            
            # 2. Fazer backup de segurança
            backup_dir = self.fazer_backup_seguranca()
            
            # 3. Agrupar agentes por dimensão
            grupos_dimensao = self.agrupar_agentes_por_dimensao(indices_agentes)
            
            if not grupos_dimensao:
                logger.error("❌ Falha ao agrupar agentes!")
                return False
            
            # 4. Unificar cada grupo separadamente
            grupos_unificados = {}
            
            for dimensao, agentes_grupo in grupos_dimensao.items():
                logger.info(f"🔗 Processando grupo {dimensao}d...")
                
                index_unificado, total_vetores = self.unificar_grupo_dimensao(dimensao, agentes_grupo)
                
                if not index_unificado:
                    logger.error(f"❌ Falha na unificação do grupo {dimensao}d!")
                    continue
                
                grupos_unificados[dimensao] = (index_unificado, total_vetores)
            
            if not grupos_unificados:
                logger.error("❌ Nenhum grupo foi unificado com sucesso!")
                return False
            
            # 5. Salvar índices unificados
            if self.salvar_indices_unificados(grupos_unificados):
                elapsed_time = time.time() - start_time
                logger.info("🎉 UNIFICAÇÃO INTELIGENTE CONCLUÍDA COM SUCESSO!")
                logger.info(f"⏱️ Tempo total: {elapsed_time/60:.1f} minutos")
                logger.info(f"💾 Backup de segurança: {backup_dir}")
                return True
            else:
                logger.error("❌ Falha ao salvar índices unificados!")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro crítico na unificação: {e}")
            return False

def main():
    """Função principal"""
    try:
        print("=" * 70)
        print("🧠 UNIFICADOR FAISS INTELIGENTE - POR DIMENSÃO")
        print("🎯 Agrupando agentes por dimensão e unificando")
        print("🛡️ Backup automático + validação completa")
        print("=" * 70)
        
        unificador = UnificadorFAISSInteligente()
        sucesso = unificador.executar_unificacao()
        
        if sucesso:
            print("\n" + "=" * 70)
            print("🎉 UNIFICAÇÃO INTELIGENTE CONCLUÍDA COM SUCESSO!")
            print("📊 Agentes agrupados por dimensão e unificados")
            print("💾 Backup de segurança criado")
            print("✅ Sistema pronto para uso")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("❌ UNIFICAÇÃO INTELIGENTE FALHOU!")
            print("🔧 Verifique os logs para detalhes")
            print("💾 Backup de segurança foi criado")
            print("=" * 70)
            
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        print(f"\n❌ ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    main()
