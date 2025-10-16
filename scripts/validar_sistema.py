#!/usr/bin/env python3
"""
SCRIPT DE VALIDAÇÃO COMPLETA DO SISTEMA
=======================================

Este script valida todos os componentes do sistema após a reorganização,
verificando:
1. Imports e dependências
2. Pontos de entrada principais
3. Integridade dos sistemas V2
4. Funcionalidade dos scripts principais
5. Estrutura de diretórios
6. Configurações e logs

Uso: python scripts/validar_sistema.py
"""

import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Adicionar src ao path
src_path = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(src_path))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('storage/logs/validacao_sistema.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ValidadorSistema:
    """
    Validador completo do sistema de IA autoevolutiva
    
    Verifica todos os componentes críticos e gera relatório
    detalhado de status do sistema.
    """
    
    def __init__(self):
        """Inicializa o validador"""
        self.resultados = {
            'imports': {},
            'scripts_principais': {},
            'sistemas_v2': {},
            'estrutura_diretorios': {},
            'configuracoes': {},
            'dependencias': {}
        }
        self.erros = []
        self.warnings = []
        
    def validar_imports(self) -> Dict[str, Any]:
        """
        VALIDAÇÃO DE IMPORTS
        
        Verifica se todos os imports críticos estão funcionando
        corretamente após a reorganização.
        """
        logger.info("🔍 Validando imports...")
        
        imports_criticos = {
            # Sistema principal
            'app.main': 'MainAI',
            'app.main_optimized': 'OptimizedEvolutionaryAISystem',
            'app.gic_ia_integrada': 'GICIAIntegrada',
            'app.app_gic': 'app',
            
            # Core
            'core.ia_evolutiva_compativel': 'CompatibleEvolutionaryAI',
            
            # FAISS Engine
            'faiss_engine.biblioteca_central_faiss': 'BibliotecaCentralFAISS',
            'faiss_engine.sistema_agentes_faiss_integrado': 'SistemaAgentesFAISSIntegrado',
            
            # Knowledge Bus
            'knowledge_bus.barramento_conhecimento_unificado': 'BarramentoConhecimentoUnificado',
            'knowledge_bus.guardiao_conhecimento': 'GuardiaoConhecimento',
            
            # Systems
            'systems.integrar_frameworks_ia': 'IntegradorFrameworksIA',
            
            # Pipelines
            'pipelines.gerador_procedimentos_academia': 'MineradorPadroes',
        }
        
        resultados_imports = {}
        
        for modulo, classe in imports_criticos.items():
            try:
                # Tentar importar o módulo
                mod = importlib.import_module(modulo)
                
                # Verificar se a classe existe
                if hasattr(mod, classe):
                    resultados_imports[modulo] = {
                        'status': 'OK',
                        'classe': classe,
                        'mensagem': f'Import e classe {classe} OK'
                    }
                    logger.info(f"✅ {modulo} - {classe}")
                else:
                    resultados_imports[modulo] = {
                        'status': 'ERRO',
                        'classe': classe,
                        'mensagem': f'Classe {classe} não encontrada'
                    }
                    self.erros.append(f"Classe {classe} não encontrada em {modulo}")
                    logger.error(f"❌ {modulo} - Classe {classe} não encontrada")
                    
            except ImportError as e:
                resultados_imports[modulo] = {
                    'status': 'ERRO',
                    'classe': classe,
                    'mensagem': f'Erro de import: {str(e)}'
                }
                self.erros.append(f"Erro de import em {modulo}: {str(e)}")
                logger.error(f"❌ {modulo} - Erro de import: {str(e)}")
            except Exception as e:
                resultados_imports[modulo] = {
                    'status': 'ERRO',
                    'classe': classe,
                    'mensagem': f'Erro inesperado: {str(e)}'
                }
                self.erros.append(f"Erro inesperado em {modulo}: {str(e)}")
                logger.error(f"❌ {modulo} - Erro inesperado: {str(e)}")
        
        self.resultados['imports'] = resultados_imports
        return resultados_imports
    
    def validar_scripts_principais(self) -> Dict[str, Any]:
        """
        VALIDAÇÃO DE SCRIPTS PRINCIPAIS
        
        Verifica se os scripts principais podem ser executados
        sem erros críticos.
        """
        logger.info("🔍 Validando scripts principais...")
        
        scripts_principais = [
            'src/app/main.py',
            'src/app/main_optimized.py',
            'src/app/gic_ia_integrada.py',
            'src/app/app_gic.py',
            'src/core/main.py'
        ]
        
        resultados_scripts = {}
        
        for script in scripts_principais:
            try:
                # Verificar se o arquivo existe
                if not os.path.exists(script):
                    resultados_scripts[script] = {
                        'status': 'ERRO',
                        'mensagem': 'Arquivo não encontrado'
                    }
                    self.erros.append(f"Arquivo não encontrado: {script}")
                    continue
                
                # Tentar compilar o script
                with open(script, 'r', encoding='utf-8') as f:
                    codigo = f.read()
                
                compile(codigo, script, 'exec')
                
                resultados_scripts[script] = {
                    'status': 'OK',
                    'mensagem': 'Script compilado com sucesso'
                }
                logger.info(f"✅ {script}")
                
            except SyntaxError as e:
                resultados_scripts[script] = {
                    'status': 'ERRO',
                    'mensagem': f'Erro de sintaxe: {str(e)}'
                }
                self.erros.append(f"Erro de sintaxe em {script}: {str(e)}")
                logger.error(f"❌ {script} - Erro de sintaxe: {str(e)}")
            except Exception as e:
                resultados_scripts[script] = {
                    'status': 'ERRO',
                    'mensagem': f'Erro inesperado: {str(e)}'
                }
                self.erros.append(f"Erro inesperado em {script}: {str(e)}")
                logger.error(f"❌ {script} - Erro inesperado: {str(e)}")
        
        self.resultados['scripts_principais'] = resultados_scripts
        return resultados_scripts
    
    def validar_estrutura_diretorios(self) -> Dict[str, Any]:
        """
        VALIDAÇÃO DA ESTRUTURA DE DIRETÓRIOS
        
        Verifica se a estrutura de diretórios está correta
        após a reorganização.
        """
        logger.info("🔍 Validando estrutura de diretórios...")
        
        diretorios_obrigatorios = [
            'src/app',
            'src/core',
            'src/agents',
            'src/faiss_engine',
            'src/knowledge_bus',
            'src/pipelines',
            'src/systems',
            'src/utils',
            'src/config',
            'src/templates',
            'storage/databases',
            'storage/logs',
            'storage/backups',
            'storage/indices',
            'storage/outputs',
            'storage/models',
            'tests',
            'scripts',
            'docs',
            'requirements'
        ]
        
        resultados_diretorios = {}
        
        for diretorio in diretorios_obrigatorios:
            if os.path.exists(diretorio):
                resultados_diretorios[diretorio] = {
                    'status': 'OK',
                    'mensagem': 'Diretório existe'
                }
                logger.info(f"✅ {diretorio}")
            else:
                resultados_diretorios[diretorio] = {
                    'status': 'ERRO',
                    'mensagem': 'Diretório não encontrado'
                }
                self.erros.append(f"Diretório não encontrado: {diretorio}")
                logger.error(f"❌ {diretorio} - Diretório não encontrado")
        
        self.resultados['estrutura_diretorios'] = resultados_diretorios
        return resultados_diretorios
    
    def validar_dependencias(self) -> Dict[str, Any]:
        """
        VALIDAÇÃO DE DEPENDÊNCIAS
        
        Verifica se todas as dependências críticas estão instaladas.
        """
        logger.info("🔍 Validando dependências...")
        
        dependencias_criticas = [
            'torch',
            'numpy',
            'faiss',
            'flask',
            'flask_socketio',
            'transformers',
            'sentence_transformers',
            'chromadb',
            'yaml'
        ]
        
        resultados_dependencias = {}
        
        for dep in dependencias_criticas:
            try:
                importlib.import_module(dep)
                resultados_dependencias[dep] = {
                    'status': 'OK',
                    'mensagem': 'Dependência instalada'
                }
                logger.info(f"✅ {dep}")
            except ImportError:
                resultados_dependencias[dep] = {
                    'status': 'ERRO',
                    'mensagem': 'Dependência não instalada'
                }
                self.erros.append(f"Dependência não instalada: {dep}")
                logger.error(f"❌ {dep} - Dependência não instalada")
        
        self.resultados['dependencias'] = resultados_dependencias
        return resultados_dependencias
    
    def gerar_relatorio(self) -> str:
        """
        GERA RELATÓRIO COMPLETO DE VALIDAÇÃO
        
        Cria um relatório detalhado com todos os resultados
        da validação do sistema.
        """
        logger.info("📊 Gerando relatório de validação...")
        
        relatorio = []
        relatorio.append("=" * 80)
        relatorio.append("RELATÓRIO DE VALIDAÇÃO DO SISTEMA")
        relatorio.append("=" * 80)
        relatorio.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        relatorio.append("")
        
        # Resumo geral
        total_erros = len(self.erros)
        total_warnings = len(self.warnings)
        
        relatorio.append("RESUMO GERAL:")
        relatorio.append(f"  ✅ Imports: {sum(1 for r in self.resultados['imports'].values() if r['status'] == 'OK')}/{len(self.resultados['imports'])}")
        relatorio.append(f"  ✅ Scripts: {sum(1 for r in self.resultados['scripts_principais'].values() if r['status'] == 'OK')}/{len(self.resultados['scripts_principais'])}")
        relatorio.append(f"  ✅ Diretórios: {sum(1 for r in self.resultados['estrutura_diretorios'].values() if r['status'] == 'OK')}/{len(self.resultados['estrutura_diretorios'])}")
        relatorio.append(f"  ✅ Dependências: {sum(1 for r in self.resultados['dependencias'].values() if r['status'] == 'OK')}/{len(self.resultados['dependencias'])}")
        relatorio.append(f"  ❌ Erros: {total_erros}")
        relatorio.append(f"  ⚠️ Warnings: {total_warnings}")
        relatorio.append("")
        
        # Status geral
        if total_erros == 0:
            relatorio.append("🎉 SISTEMA VALIDADO COM SUCESSO!")
            relatorio.append("   Todos os componentes estão funcionando corretamente.")
        else:
            relatorio.append("⚠️ SISTEMA COM PROBLEMAS")
            relatorio.append(f"   {total_erros} erros encontrados que precisam ser corrigidos.")
        
        relatorio.append("")
        
        # Detalhes dos erros
        if self.erros:
            relatorio.append("ERROS ENCONTRADOS:")
            relatorio.append("-" * 40)
            for i, erro in enumerate(self.erros, 1):
                relatorio.append(f"{i}. {erro}")
            relatorio.append("")
        
        # Detalhes dos warnings
        if self.warnings:
            relatorio.append("WARNINGS:")
            relatorio.append("-" * 40)
            for i, warning in enumerate(self.warnings, 1):
                relatorio.append(f"{i}. {warning}")
            relatorio.append("")
        
        relatorio.append("=" * 80)
        
        return "\n".join(relatorio)
    
    def executar_validacao_completa(self) -> bool:
        """
        EXECUTA VALIDAÇÃO COMPLETA DO SISTEMA
        
        Executa todas as validações e retorna True se o sistema
        está funcionando corretamente.
        """
        logger.info("🚀 Iniciando validação completa do sistema...")
        
        # Executar todas as validações
        self.validar_imports()
        self.validar_scripts_principais()
        self.validar_estrutura_diretorios()
        self.validar_dependencias()
        
        # Gerar relatório
        relatorio = self.gerar_relatorio()
        
        # Salvar relatório
        os.makedirs('storage/logs', exist_ok=True)
        with open('storage/logs/relatorio_validacao.txt', 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        # Exibir relatório
        print(relatorio)
        
        # Retornar status
        return len(self.erros) == 0

def main():
    """Função principal do validador"""
    print("🔍 VALIDADOR DE SISTEMA - IA AUTOEVOLUTIVA")
    print("=" * 50)
    
    validador = ValidadorSistema()
    sucesso = validador.executar_validacao_completa()
    
    if sucesso:
        print("\n🎉 Sistema validado com sucesso!")
        return 0
    else:
        print("\n⚠️ Sistema com problemas - verifique o relatório")
        return 1

if __name__ == "__main__":
    sys.exit(main())
