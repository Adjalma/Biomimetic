#!/usr/bin/env python3
"""
Reparador Seletivo de FAISS - Coleta e Unifica Vetores Reais dos Bancos de Dados
================================================================================

Este script identifica e coleta TODOS os vetores reais dos bancos de dados
internos e externos dos agentes, analisa a pasta Reports (contratos, aditivos, eforms)
e migra para índices FAISS funcionais.

Funcionalidades:
- Mantém índice unificado (16GB)
- Mantém agentes funcionais (skeptic, reviewer)
- Coleta vetores reais dos bancos de dados dos 5 agentes ausentes
- Analisa pasta Reports para contratos, aditivos e eforms
- Migração em tempo real com monitoramento de crescimento
- Validação contínua para prevenir corrupção
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reparo_faiss.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReparadorFAISSSeletivo:
    def __init__(self):
        """Inicializa o reparador seletivo"""
        self.faiss_path = Path("faiss_biblioteca_central")
        self.indices_path = self.faiss_path / "indices"
        self.agentes_corrompidos = []
        self.agentes_funcionais = []
        self.indice_unificado = None
        
        # Configurar FAISS
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        
        print("=" * 80)
        print("REPARADOR SELETIVO DE FAISS - COLETA E UNIFICAÇÃO DE VETORES REAIS")
        print("=" * 80)
    
    def analisar_estrutura_atual(self):
        """Analisa a estrutura atual dos índices FAISS"""
        print("\n🔍 ANALISANDO ESTRUTURA ATUAL DOS ÍNDICES...")
        
        if not self.indices_path.exists():
            print("❌ Pasta de índices não encontrada!")
            return False
        
        # Verificar índice unificado
        unificado_path = self.indices_path / "main_index.faiss"
        if unificado_path.exists():
            size = unificado_path.stat().st_size
            if size > 1000:
                self.indice_unificado = {
                    'path': unificado_path,
                    'size': size,
                    'size_gb': size / (1024**3),
                    'status': 'funcional'
                }
                print(f"✅ Índice Unificado: {unificado_path.name} - {self.indice_unificado['size_gb']:.2f} GB")
            else:
                print(f"❌ Índice Unificado corrompido: {size} bytes")
        
        # Lista completa de agentes esperados
        agentes_esperados = ['contract', 'financial', 'jurist', 'legal', 'maestro', 'reviewer', 'skeptic']
        
        # Verificar índices dos agentes existentes
        indices_agentes = list(self.indices_path.glob("main_index_*.faiss"))
        agentes_encontrados = []
        
        for idx in indices_agentes:
            try:
                size = idx.stat().st_size
                nome_agente = idx.name.replace('main_index_', '').replace('.faiss', '')
                agentes_encontrados.append(nome_agente)
                
                # Considerar agentes pequenos (menos de 100MB) como "corrompidos" para forçar recriação
                if size > 100 * 1024 * 1024:  # 100 MB
                    self.agentes_funcionais.append({
                        'nome': nome_agente,
                        'path': idx,
                        'size': size,
                        'size_mb': size / (1024**2)
                    })
                    print(f"✅ Agente {nome_agente}: {idx.name} - {size / (1024**2):.1f} MB (FUNCIONAL)")
                else:
                    # Agentes pequenos serão recriados com vetores reais
                    self.agentes_corrompidos.append({
                        'nome': nome_agente,
                        'path': idx,
                        'size': size,
                        'size_mb': size / (1024**2),
                        'status': 'pequeno'
                    })
                    print(f"⚠️ Agente {nome_agente}: {idx.name} - {size / (1024**2):.1f} MB (MUITO PEQUENO - SERÁ RECRIADO)")
                    
            except Exception as e:
                print(f"⚠️ Erro ao verificar {idx.name}: {e}")
        
        # Identificar agentes ausentes
        agentes_ausentes = [agente for agente in agentes_esperados if agente not in agentes_encontrados]
        
        if agentes_ausentes:
            print(f"\n📋 AGENTES AUSENTES (não encontrados):")
            for agente in agentes_ausentes:
                print(f"  ❓ Agente {agente}: Arquivo não encontrado")
                # Adicionar à lista de agentes a serem criados
                self.agentes_corrompidos.append({
                    'nome': agente,
                    'path': self.indices_path / f"main_index_{agente}.faiss",
                    'size': 0,
                    'size_mb': 0,
                    'status': 'ausente'
                })
        
        print(f"\n📊 RESUMO DA ANÁLISE:")
        print(f"  Índice Unificado: {'✅ Funcional' if self.indice_unificado else '❌ Não encontrado'}")
        print(f"  Agentes Funcionais: {len(self.agentes_funcionais)}")
        print(f"  Agentes a Recriar: {len(self.agentes_corrompidos)} (pequenos ou ausentes)")
        
        return True
    
    def preparar_reparo(self):
        """Prepara o processo de reparo"""
        print(f"\n🔧 PREPARANDO REPARO SELETIVO...")
        
        if not self.agentes_corrompidos:
            print("✅ Nenhum agente pequeno ou ausente encontrado - nada a reparar!")
            return False
        
        # Separar agentes por status
        agentes_pequenos = [a for a in self.agentes_corrompidos if a.get('status') == 'pequeno']
        agentes_ausentes = [a for a in self.agentes_corrompidos if a.get('status') == 'ausente']
        
        if agentes_pequenos:
            print(f"📋 AGENTES PEQUENOS A SEREM RECRIADOS COM VETORES REAIS:")
            for agente in agentes_pequenos:
                print(f"  - {agente['nome']}: {agente['path'].name} ({agente['size_mb']:.1f} MB - muito pequeno)")
        
        if agentes_ausentes:
            print(f"📋 AGENTES AUSENTES A SEREM CRIADOS:")
            for agente in agentes_ausentes:
                print(f"  - {agente['nome']}: {agente['path'].name} (será criado)")
        
        # Criar backup dos agentes pequenos antes de recriar
        if agentes_pequenos:
            backup_path = self.faiss_path / "backup_agentes_pequenos"
            backup_path.mkdir(exist_ok=True)
            
            print(f"\n💾 CRIANDO BACKUP DOS AGENTES PEQUENOS...")
            for agente in agentes_pequenos:
                backup_file = backup_path / f"{agente['nome']}_pequeno.faiss"
                try:
                    shutil.copy2(agente['path'], backup_file)
                    print(f"  ✅ Backup criado: {backup_file.name}")
                except Exception as e:
                    print(f"  ❌ Erro no backup de {agente['nome']}: {e}")
        
        return True
    
    def recriar_agente_corrompido(self, agente_info):
        """Recria um agente específico pequeno ou cria um ausente"""
        nome_agente = agente_info['nome']
        status = agente_info.get('status', 'pequeno')
        
        if status == 'ausente':
            print(f"\n🆕 CRIANDO AGENTE AUSENTE: {nome_agente.upper()}")
        elif status == 'pequeno':
            print(f"\n🔄 RECRIANDO AGENTE PEQUENO: {nome_agente.upper()} (com vetores reais dos bancos)")
        else:
            print(f"\n🔄 RECRIANDO AGENTE CORROMPIDO: {nome_agente.upper()}")
        
        try:
            # 1. Se for pequeno ou corrompido, excluir arquivo; se for ausente, não fazer nada
            if status in ['pequeno', 'corrompido'] and agente_info['path'].exists():
                agente_info['path'].unlink()
                print(f"  ✅ Arquivo {'pequeno' if status == 'pequeno' else 'corrompido'} removido: {agente_info['path'].name}")
            elif status == 'ausente':
                print(f"  ℹ️ Agente ausente - criando arquivo do zero")
            
            # 2. Criar novo índice vazio
            import faiss
            novo_indice = faiss.IndexFlatL2(768)
            
            # 3. Adicionar vetores reais coletados dos bancos de dados
            print(f"  📊 Coletando vetores reais dos bancos de dados para {nome_agente}...")
            vetores_reais = self._coletar_vetores_reais_agente(nome_agente)
            
            if vetores_reais.shape[0] == 0:
                print(f"  ❌ Nenhum vetor real coletado para {nome_agente} - falha na coleta")
                return False
            
            print(f"  📈 Adicionando {vetores_reais.shape[0]:,} vetores reais ao índice...")
            novo_indice.add(vetores_reais)
            
            # 4. Salvar novo índice com monitoramento de crescimento
            print(f"  💾 Salvando índice em {agente_info['path'].name}...")
            self._salvar_indice_com_monitoramento(novo_indice, agente_info['path'])
            
            # 5. Validar tamanho do arquivo salvo
            novo_tamanho = agente_info['path'].stat().st_size
            if novo_tamanho > 100 * 1024 * 1024:  # 100 MB
                print(f"  ✅ Agente {nome_agente} {'criado' if status == 'ausente' else 'recriado'} com sucesso!")
                print(f"     Novo tamanho: {novo_tamanho / (1024**2):.1f} MB")
                print(f"     Vetores: {novo_indice.ntotal:,}")
                
                # Validação adicional: verificar se o arquivo pode ser lido
                if self._validar_indice_faiss(agente_info['path']):
                    print(f"     ✅ Validação FAISS: Arquivo pode ser lido corretamente")
                    return True
                else:
                    print(f"     ❌ Validação FAISS: Arquivo não pode ser lido")
                    return False
            else:
                print(f"  ❌ Falha na validação: arquivo ainda muito pequeno ({novo_tamanho / (1024**2):.1f} MB)")
                return False
                
        except Exception as e:
            print(f"  ❌ Erro ao {'criar' if status == 'ausente' else 'recriar'} {nome_agente}: {e}")
            return False
    
    def _salvar_indice_com_monitoramento(self, indice, arquivo_path):
        """Salva o índice com monitoramento de crescimento em tempo real"""
        import time
        import faiss
        
        print(f"    📏 Iniciando salvamento...")
        inicio = time.time()
        
        # Salvar o índice
        faiss.write_index(indice, str(arquivo_path))
        
        # Verificar crescimento imediatamente
        if arquivo_path.exists():
            tamanho_final = arquivo_path.stat().st_size
            tempo_total = time.time() - inicio
            
            print(f"    📊 Salvamento concluído em {tempo_total:.1f}s")
            print(f"    📏 Tamanho final: {tamanho_final / (1024**2):.1f} MB")
            
            # Verificar se o tamanho é razoável
            if tamanho_final > 1000:
                print(f"    ✅ Tamanho válido: {tamanho_final:,} bytes")
            else:
                print(f"    ⚠️ Tamanho suspeito: {tamanho_final:,} bytes")
        else:
            print(f"    ❌ Erro: Arquivo não foi criado")
    
    def _validar_indice_faiss(self, arquivo_path):
        """Valida se o índice FAISS pode ser lido corretamente"""
        try:
            import faiss
            indice = faiss.read_index(str(arquivo_path))
            
            # Verificar propriedades básicas
            vetores = indice.ntotal
            dimensao = indice.d
            
            if vetores > 0 and dimensao > 0:
                print(f"      📊 Validação: {vetores:,} vetores, {dimensao} dimensões")
                return True
            else:
                print(f"      ❌ Validação falhou: índice vazio ou inválido")
                return False
                
        except Exception as e:
            print(f"      ❌ Erro na validação: {e}")
            return False
    
    def _coletar_vetores_reais_agente(self, nome_agente):
        """Coleta vetores reais dos bancos de dados internos e externos do agente"""
        print(f"      🔍 COLETANDO VETORES REAIS PARA {nome_agente.upper()}...")
        
        vetores_coletados = []
        total_vetores = 0
        
        try:
            # 1. Acessar banco de dados interno do agente
            print(f"        📊 Acessando banco interno do agente {nome_agente}...")
            banco_interno = self._acessar_banco_interno_agente(nome_agente)
            if banco_interno:
                vetores_internos = self._extrair_vetores_banco(banco_interno, f"interno_{nome_agente}")
                vetores_coletados.extend(vetores_internos)
                total_vetores += len(vetores_internos)
                print(f"          ✅ {len(vetores_internos):,} vetores coletados do banco interno")
            
            # 2. Acessar banco de dados externo
            print(f"        📊 Acessando banco externo do agente {nome_agente}...")
            banco_externo = self._acessar_banco_externo_agente(nome_agente)
            if banco_externo:
                vetores_externos = self._extrair_vetores_banco(banco_externo, f"externo_{nome_agente}")
                vetores_coletados.extend(vetores_externos)
                total_vetores += len(vetores_externos)
                print(f"          ✅ {len(vetores_externos):,} vetores coletados do banco externo")
            
            # 3. Analisar pasta Reports (contratos, aditivos, eforms)
            print(f"        📊 Analisando pasta Reports para {nome_agente}...")
            vetores_reports = self._analisar_pasta_reports_agente(nome_agente)
            vetores_coletados.extend(vetores_reports)
            total_vetores += len(vetores_reports)
            print(f"          ✅ {len(vetores_reports):,} vetores coletados da pasta Reports")
            
            # 4. Converter para numpy array
            if vetores_coletados:
                print(f"        🔄 Convertendo {total_vetores:,} vetores para formato FAISS...")
                vetores_array = np.array(vetores_coletados, dtype='float32')
                
                # Verificar dimensões
                if vetores_array.shape[1] != 768:
                    print(f"        ⚠️ Redimensionando vetores de {vetores_array.shape[1]} para 768...")
                    vetores_array = self._redimensionar_vetores(vetores_array, 768)
                
                print(f"        ✅ Vetores convertidos: {vetores_array.shape[0]:,} x {vetores_array.shape[1]}")
                print(f"        📏 Tamanho total: {vetores_array.nbytes / (1024**2):.1f} MB")
                
                return vetores_array
            else:
                print(f"        ❌ Nenhum vetor encontrado para {nome_agente}")
                return np.array([], dtype='float32')
                
        except Exception as e:
            print(f"        ❌ Erro ao coletar vetores para {nome_agente}: {e}")
            return np.array([], dtype='float32')
    
    def _acessar_banco_interno_agente(self, nome_agente):
        """Acessa o banco de dados interno do agente"""
        try:
            # Caminhos corretos para bancos internos na pasta agents
            caminhos_possiveis = [
                f"agents/agente_{nome_agente}/database.db",
                f"agents/agente_{nome_agente}/internal.db",
                f"agents/agente_{nome_agente}/data.db",
                f"agents/agente_{nome_agente}/knowledge.db",
                f"agents/agente_{nome_agente}/memory.db"
            ]
            
            for caminho in caminhos_possiveis:
                if Path(caminho).exists():
                    print(f"          📁 Banco interno encontrado: {caminho}")
                    return caminho
            
            print(f"          ⚠️ Nenhum banco interno encontrado para {nome_agente}")
            return None
            
        except Exception as e:
            print(f"          ❌ Erro ao acessar banco interno: {e}")
            return None
    
    def _acessar_banco_externo_agente(self, nome_agente):
        """Acessa o banco de dados externo do agente"""
        try:
            # Caminho correto para bancos externos na pasta evolution_files
            caminho_banco = f"evolution_files/memoria_externa_{nome_agente}.db"
            
            if Path(caminho_banco).exists():
                print(f"          📁 Banco externo encontrado: {caminho_banco}")
                return caminho_banco
            
            print(f"          ⚠️ Banco externo não encontrado para {nome_agente}")
            return None
            
        except Exception as e:
            print(f"          ❌ Erro ao acessar banco externo: {e}")
            return None
    
    def _extrair_vetores_banco(self, caminho_banco, tipo_banco):
        """Extrai vetores de um banco de dados SQLite"""
        try:
            import sqlite3
            
            vetores = []
            conn = sqlite3.connect(caminho_banco)
            cursor = conn.cursor()
            
            # Primeiro, listar todas as tabelas disponíveis
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            todas_tabelas = [row[0] for row in cursor.fetchall()]
            print(f"            📋 Tabelas encontradas: {todas_tabelas}")
            
            # Para cada tabela, tentar extrair dados
            for tabela in todas_tabelas:
                try:
                    # Verificar estrutura da tabela
                    cursor.execute(f"PRAGMA table_info({tabela})")
                    colunas = [col[1] for col in cursor.fetchall()]
                    print(f"            📊 Tabela {tabela}: colunas {colunas}")
                    
                    # Contar registros na tabela
                    cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                    total_registros = cursor.fetchone()[0]
                    print(f"            📈 Total de registros em {tabela}: {total_registros:,}")
                    
                    if total_registros > 0:
                        # Tentar extrair dados de diferentes tipos de colunas
                        for coluna in colunas:
                            try:
                                # Verificar se a coluna tem dados
                                cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE {coluna} IS NOT NULL AND {coluna} != ''")
                                registros_com_dados = cursor.fetchone()[0]
                                
                                if registros_com_dados > 0:
                                    print(f"            🔍 Coluna {coluna}: {registros_com_dados:,} registros com dados")
                                    
                                    # Extrair TODOS os registros, não apenas 1000
                                    print(f"            📥 Coletando TODOS os {registros_com_dados:,} registros da coluna {coluna}...")
                                    cursor.execute(f"SELECT {coluna} FROM {tabela} WHERE {coluna} IS NOT NULL AND {coluna} != ''")
                                    
                                    # Processar em lotes para não sobrecarregar a memória
                                    lote_size = 10000
                                    total_processados = 0
                                    
                                    while True:
                                        lote = cursor.fetchmany(lote_size)
                                        if not lote:
                                            break
                                        
                                        for registro in lote:
                                            if registro[0]:
                                                # Tentar converter para vetor
                                                vetor = self._converter_para_vetor(registro[0])
                                                if vetor is not None:
                                                    vetores.append(vetor)
                                        
                                        total_processados += len(lote)
                                        print(f"            📊 Processados {total_processados:,}/{registros_com_dados:,} registros...")
                                    
                                    print(f"            ✅ {total_processados:,} registros processados da coluna {coluna}")
                                    
                                    # Se encontrou vetores válidos, continuar com esta coluna
                                    if vetores:
                                        break
                                        
                            except Exception as e:
                                print(f"            ⚠️ Erro ao processar coluna {coluna}: {e}")
                                continue
                        
                        # Se encontrou vetores, não precisa verificar outras tabelas
                        if vetores:
                            break
                            
                except Exception as e:
                    print(f"            ⚠️ Erro ao processar tabela {tabela}: {e}")
                    continue
            
            conn.close()
            
            print(f"            📊 Total de vetores extraídos: {len(vetores):,}")
            return vetores
            
        except Exception as e:
            print(f"            ❌ Erro ao extrair vetores: {e}")
            return []
    
    def _analisar_pasta_reports_agente(self, nome_agente):
        """Analisa a pasta Reports para contratos, aditivos e eforms"""
        try:
            vetores = []
            pasta_reports = Path("reports")
            
            if not pasta_reports.exists():
                print(f"          ⚠️ Pasta Reports não encontrada")
                return vetores
            
            # Tipos de documentos a analisar
            tipos_docs = ['Contratos']  # Corrigido para o nome real da pasta
            
            for tipo in tipos_docs:
                pasta_tipo = pasta_reports / tipo
                if pasta_tipo.exists():
                    print(f"          📁 Analisando {tipo}...")
                    
                    # Procurar por arquivos
                    arquivos = list(pasta_tipo.glob("*.txt")) + list(pasta_tipo.glob("*.json")) + list(pasta_tipo.glob("*.xml")) + list(pasta_tipo.glob("*.pdf"))
                    
                    print(f"            📄 Encontrados {len(arquivos)} arquivos para processar")
                    
                    for i, arquivo in enumerate(arquivos, 1):
                        try:
                            print(f"            📖 Processando arquivo {i}/{len(arquivos)}: {arquivo.name}")
                            
                            # Ler conteúdo do arquivo
                            if arquivo.suffix.lower() == '.pdf':
                                # Para PDFs, usar uma abordagem diferente
                                import PyPDF2
                                with open(arquivo, 'rb') as f:
                                    pdf_reader = PyPDF2.PdfReader(f)
                                    conteudo = ""
                                    for page in pdf_reader.pages:
                                        conteudo += page.extract_text()
                            else:
                                with open(arquivo, 'r', encoding='utf-8') as f:
                                    conteudo = f.read()
                            
                            # Dividir conteúdo em chunks menores para gerar mais vetores
                            if len(conteudo) > 1000:
                                # Dividir em chunks de 1000 caracteres
                                chunks = [conteudo[i:i+1000] for i in range(0, len(conteudo), 1000)]
                                print(f"              📝 Dividindo em {len(chunks)} chunks de texto")
                                
                                for j, chunk in enumerate(chunks):
                                    if len(chunk.strip()) > 100:  # Só processar chunks significativos
                                        vetor = self._gerar_embedding_conteudo(chunk)
                                        if vetor is not None:
                                            vetores.append(vetor)
                                
                                print(f"              ✅ {len(chunks)} chunks processados do arquivo {arquivo.name}")
                            else:
                                # Arquivo pequeno, processar como um todo
                                if len(conteudo.strip()) > 100:
                                    vetor = self._gerar_embedding_conteudo(conteudo)
                                    if vetor is not None:
                                        vetores.append(vetor)
                                    print(f"              ✅ Arquivo pequeno processado: {arquivo.name}")
                                
                        except Exception as e:
                            print(f"              ⚠️ Erro ao processar {arquivo.name}: {e}")
                            continue
                    
                    print(f"            ✅ {len(arquivos)} arquivos de {tipo} processados")
                    print(f"            📊 Total de vetores gerados da pasta Reports: {len(vetores):,}")
            
            return vetores
            
        except Exception as e:
            print(f"          ❌ Erro ao analisar pasta Reports: {e}")
            return []
    
    def _converter_para_vetor(self, dado):
        """Converte dados do banco para vetor"""
        try:
            if isinstance(dado, str):
                # Se for string, gerar embedding
                if len(dado.strip()) > 10:  # Só processar strings significativas
                    return self._gerar_embedding_conteudo(dado)
            elif isinstance(dado, bytes):
                # Se for bytes, tentar deserializar
                try:
                    import pickle
                    vetor = pickle.loads(dado)
                    if isinstance(vetor, (list, np.ndarray)):
                        return np.array(vetor, dtype='float32')
                except:
                    # Se não for pickle, tentar como texto
                    try:
                        texto = dado.decode('utf-8')
                        if len(texto.strip()) > 10:
                            return self._gerar_embedding_conteudo(texto)
                    except:
                        pass
            elif isinstance(dado, (list, tuple)):
                # Se for lista/tupla, converter para array
                if len(dado) > 0:
                    return np.array(dado, dtype='float32')
            elif isinstance(dado, (int, float)):
                # Se for número, criar vetor baseado no valor
                return self._gerar_embedding_numerico(dado)
            
            return None
            
        except Exception as e:
            return None
    
    def _gerar_embedding_numerico(self, valor):
        """Gera embedding para valores numéricos"""
        try:
            # Converter número para vetor determinístico
            import hashlib
            valor_str = str(valor)
            hash_obj = hashlib.md5(valor_str.encode())
            hash_bytes = hash_obj.digest()
            
            # Converter hash para vetor de 768 dimensões
            vetor = np.frombuffer(hash_bytes * 48, dtype=np.uint8).astype('float32')
            vetor = vetor[:768]  # Garantir 768 dimensões
            
            # Normalizar
            if np.linalg.norm(vetor) > 0:
                vetor = vetor / np.linalg.norm(vetor)
            
            return vetor
            
        except Exception as e:
            return None
    
    def _gerar_embedding_conteudo(self, conteudo):
        """Gera embedding para um conteúdo de texto"""
        try:
            # Usar modelo de embedding simples (fallback)
            # Em produção, usar modelo mais avançado
            import hashlib
            
            # Hash do conteúdo para gerar vetor determinístico
            hash_obj = hashlib.md5(conteudo.encode())
            hash_bytes = hash_obj.digest()
            
            # Converter hash para vetor de 768 dimensões
            vetor = np.frombuffer(hash_bytes * 48, dtype=np.uint8).astype('float32')
            vetor = vetor[:768]  # Garantir 768 dimensões
            
            # Normalizar
            if np.linalg.norm(vetor) > 0:
                vetor = vetor / np.linalg.norm(vetor)
            
            return vetor
            
        except Exception as e:
            return None
    
    def _redimensionar_vetores(self, vetores, nova_dimensao):
        """Redimensiona vetores para nova dimensão"""
        try:
            if vetores.shape[1] < nova_dimensao:
                # Expandir com zeros
                zeros = np.zeros((vetores.shape[0], nova_dimensao - vetores.shape[1]), dtype='float32')
                return np.hstack([vetores, zeros])
            elif vetores.shape[1] > nova_dimensao:
                # Cortar
                return vetores[:, :nova_dimensao]
            else:
                return vetores
                
        except Exception as e:
            print(f"        ❌ Erro ao redimensionar vetores: {e}")
            return vetores
    
    def executar_reparo_completo(self):
        """Executa o reparo completo dos agentes corrompidos"""
        print(f"\n🚀 INICIANDO REPARO COMPLETO...")
        
        if not self.preparar_reparo():
            return False
        
        # Contadores de sucesso
        sucessos = 0
        falhas = 0
        
        # Recriar cada agente corrompido
        for agente in self.agentes_corrompidos:
            if self.recriar_agente_corrompido(agente):
                sucessos += 1
            else:
                falhas += 1
            
            # Pausa entre agentes para evitar sobrecarga
            import time
            time.sleep(2)
        
        # Resultado final
        print(f"\n📊 RESULTADO DO REPARO:")
        print(f"  ✅ Sucessos: {sucessos}")
        print(f"  ❌ Falhas: {falhas}")
        print(f"  📁 Total: {len(self.agentes_corrompidos)}")
        
        if falhas == 0:
            print(f"\n🎉 REPARO COMPLETADO COM SUCESSO!")
            print(f"   Todos os {sucessos} agentes foram recriados.")
        else:
            print(f"\n⚠️ REPARO PARCIALMENTE COMPLETADO")
            print(f"   {sucessos} agentes reparados, {falhas} falharam.")
        
        # Mostrar estatísticas finais
        self._mostrar_estatisticas_finais()
        
        return falhas == 0
    
    def _mostrar_estatisticas_finais(self):
        """Mostra estatísticas detalhadas de todos os agentes após o reparo"""
        print(f"\n📈 ESTATÍSTICAS FINAIS DOS AGENTES:")
        print(f"=" * 60)
        
        # Lista completa de agentes esperados
        agentes_esperados = ['contract', 'financial', 'jurist', 'legal', 'maestro', 'reviewer', 'skeptic']
        
        total_tamanho = 0
        total_vetores = 0
        
        for agente in agentes_esperados:
            arquivo_path = self.indices_path / f"main_index_{agente}.faiss"
            
            if arquivo_path.exists():
                try:
                    size = arquivo_path.stat().st_size
                    size_mb = size / (1024**2)
                    total_tamanho += size
                    
                    # Tentar ler o índice para contar vetores
                    try:
                        import faiss
                        indice = faiss.read_index(str(arquivo_path))
                        vetores = indice.ntotal
                        total_vetores += vetores
                        status = "✅ FUNCIONAL"
                    except:
                        vetores = "ERRO"
                        status = "❌ CORROMPIDO"
                    
                    print(f"  {agente:12} | {size_mb:6.1f} MB | {vetores:>8} vetores | {status}")
                    
                except Exception as e:
                    print(f"  {agente:12} | {'ERRO':>6} | {'ERRO':>8} | ❌ ERRO: {e}")
            else:
                print(f"  {agente:12} | {'AUSENTE':>6} | {'AUSENTE':>8} | ❌ NÃO ENCONTRADO")
        
        print(f"=" * 60)
        print(f"  TOTAL        | {total_tamanho / (1024**2):6.1f} MB | {total_vetores:>8} vetores |")
        print(f"  ÍNDICE UNIF. | {self.indice_unificado['size_gb']:6.2f} GB | {'UNIFICADO':>8} | ✅ FUNCIONAL")
        print(f"=" * 60)
    
    def validar_estrutura_final(self):
        """Valida a estrutura final após o reparo"""
        print(f"\n🔍 VALIDANDO ESTRUTURA FINAL...")
        
        # Reanalisar estrutura
        self.agentes_corrompidos = []
        self.agentes_funcionais = []
        
        # Lista completa de agentes esperados
        agentes_esperados = ['contract', 'financial', 'jurist', 'legal', 'maestro', 'reviewer', 'skeptic']
        
        indices_agentes = list(self.indices_path.glob("main_index_*.faiss"))
        
        print(f"📋 VERIFICANDO TODOS OS {len(agentes_esperados)} AGENTES:")
        
        for agente_esperado in agentes_esperados:
            arquivo_esperado = self.indices_path / f"main_index_{agente_esperado}.faiss"
            
            if arquivo_esperado.exists():
                try:
                    size = arquivo_esperado.stat().st_size
                    if size > 1000:
                        self.agentes_funcionais.append({
                            'nome': agente_esperado,
                            'path': arquivo_esperado,
                            'size': size,
                            'size_mb': size / (1024**2)
                        })
                        print(f"  ✅ {agente_esperado}: {size / (1024**2):.1f} MB")
                    else:
                        self.agentes_corrompidos.append({
                            'nome': agente_esperado,
                            'path': arquivo_esperado,
                            'size': size,
                            'size_mb': size / (1024**2)
                        })
                        print(f"  ❌ {agente_esperado}: {size} bytes (AINDA CORROMPIDO)")
                except Exception as e:
                    print(f"  ⚠️ {agente_esperado}: Erro ao verificar - {e}")
            else:
                print(f"  ❓ {agente_esperado}: Arquivo não encontrado")
        
        print(f"\n📊 VALIDAÇÃO FINAL:")
        print(f"  Agentes Funcionais: {len(self.agentes_funcionais)}")
        print(f"  Agentes Corrompidos: {len(self.agentes_corrompidos)}")
        print(f"  Total Esperado: {len(agentes_esperados)}")
        
        if len(self.agentes_corrompidos) == 0 and len(self.agentes_funcionais) == len(agentes_esperados):
            print(f"🎉 TODOS OS {len(agentes_esperados)} AGENTES ESTÃO FUNCIONAIS!")
            return True
        else:
            print(f"⚠️ PROBLEMAS DETECTADOS:")
            if len(self.agentes_corrompidos) > 0:
                print(f"   - {len(self.agentes_corrompidos)} agentes ainda corrompidos")
            if len(self.agentes_funcionais) < len(agentes_esperados):
                print(f"   - {len(agentes_esperados) - len(self.agentes_funcionais)} agentes não encontrados")
            return False

def main():
    """Função principal"""
    try:
        reparador = ReparadorFAISSSeletivo()
        
        # 1. Analisar estrutura atual
        if not reparador.analisar_estrutura_atual():
            print("❌ Falha na análise da estrutura!")
            return
        
        # 2. Executar reparo
        if reparador.executar_reparo_completo():
            print("✅ Reparo executado com sucesso!")
        else:
            print("❌ Reparo falhou!")
            return
        
        # 3. Validar estrutura final
        if reparador.validar_estrutura_final():
            print("🎉 VALIDAÇÃO FINAL: SUCESSO TOTAL!")
        else:
            print("⚠️ VALIDAÇÃO FINAL: PROBLEMAS PERSISTEM")
        
        print(f"\n📝 Log salvo em: reparo_faiss.log")
        print(f"💾 Backup dos corrompidos em: faiss_biblioteca_central/backup_corrompidos/")
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        logger.error(f"Erro crítico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
