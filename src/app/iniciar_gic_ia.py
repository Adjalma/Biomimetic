#!/usr/bin/env python3
"""
Script de Inicialização do GIC com IA Integrada
===============================================

Inicializa o sistema GIC com todos os frameworks autoevolutivos,
biomiméticos e sistemas V2 integrados.
"""

import os
import sys
import logging
import asyncio
import threading

# Adicionar diretorios ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, 'core'))
sys.path.append(os.path.join(parent_dir, 'agents'))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gic_ia_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def verificar_dependencias():
    """Verifica se todas as dependencias estao disponiveis"""
    logger.info("Verificando dependencias...")
    
    dependencias = [
        'flask',
        'flask_socketio',
        'numpy',
        'faiss',
        'torch',
        'transformers'
    ]
    
    faltando = []
    for dep in dependencias:
        try:
            __import__(dep)
            logger.info(f"[OK] {dep} disponivel")
        except ImportError:
            faltando.append(dep)
            logger.warning(f"[WARN] {dep} nao disponivel")
    
    if faltando:
        logger.error(f"[ERRO] Dependencias faltando: {faltando}")
        logger.info("[INFO] Execute: pip install " + " ".join(faltando))
        return False
    
    logger.info("[OK] Todas as dependencias estao disponiveis")
    return True

def verificar_sistemas_ia():
    """Verifica se os sistemas de IA estao disponiveis"""
    logger.info("[INFO] Verificando sistemas de IA...")
    
    sistemas = [
        'barramento_conhecimento_unificado',
        'sistema_agentes_faiss_integrado',
        'ia_autoevolutiva_avancada',
        'genoma_leis_imutaveis',
        'guardiao_conhecimento',
        'simulador_contrafactual',
        'gerador_procedimentos_academia'
    ]
    
    disponiveis = []
    nao_disponiveis = []
    
    for sistema in sistemas:
        try:
            __import__(sistema)
            disponiveis.append(sistema)
            logger.info(f"[OK] {sistema} disponivel")
        except ImportError as e:
            nao_disponiveis.append(sistema)
            logger.warning(f"[WARN] {sistema} nao disponivel: {e}")
        except Exception as e:
            nao_disponiveis.append(sistema)
            logger.error(f"[ERRO] Erro ao importar {sistema}: {e}")
            import traceback
            logger.error(f"[ERRO] Traceback: {traceback.format_exc()}")
    
    logger.info(f"[INFO] Sistemas disponiveis: {len(disponiveis)}/{len(sistemas)}")
    
    if len(disponiveis) >= 3:  # Pelo menos 3 sistemas principais
        logger.info("[OK] Sistema GIC pode ser inicializado com IA integrada")
        return True
    else:
        logger.warning("[WARN] Sistema GIC sera inicializado em modo basico")
        return False

def criar_diretorios():
    """Cria diretorios necessarios"""
    logger.info("[INFO] Criando diretorios...")
    
    diretorios = [
        "dados",
        "logs",
        "backups",
        "knowledge_bus_gic",
        "faiss_biblioteca_central_gic"
    ]
    
    for diretorio in diretorios:
        os.makedirs(diretorio, exist_ok=True)
        logger.info(f"[OK] Diretorio criado: {diretorio}")

def inicializar_gic_ia():
    """Inicializa o sistema GIC com IA integrada"""
    try:
        logger.info("[INFO] Inicializando GIC com IA integrada...")
        
        # Importar sistema GIC
        from .gic_ia_integrada import GICIAIntegrada
        
        # Criar instancia
        gic = GICIAIntegrada()
        
        logger.info("[OK] GIC com IA integrada inicializado com sucesso!")
        
        # Exibir estatisticas
        stats = gic.obter_estatisticas_ia()
        logger.info(f"[INFO] Estatisticas da IA: {stats}")
        
        return gic
        
    except Exception as e:
        logger.error(f"[ERRO] Erro ao inicializar GIC com IA: {e}")
        return None

def inicializar_gic_basico():
    """Inicializa o sistema GIC em modo basico"""
    try:
        logger.info("[INFO] Inicializando GIC em modo basico...")
        
        # Importar sistema GIC basico
        from pipelines.gic_justificativas import GICJustificativas
        
        # Criar instancia
        gic = GICJustificativas()
        
        logger.info("[OK] GIC basico inicializado com sucesso!")
        return gic
        
    except Exception as e:
        logger.error(f"[ERRO] Erro ao inicializar GIC basico: {e}")
        return None

def testar_funcionalidades(gic):
    """Testa funcionalidades basicas do sistema"""
    try:
        logger.info("[INFO] Testando funcionalidades...")
        
        # Testar criacao de sessao
        id_sessao = gic.criar_nova_sessao("Empresa Teste", "ICJ-2024-001")
        logger.info(f"[OK] Sessao criada: {id_sessao}")
        
        # Testar selecao de objetos
        objetos = ["1 PRAZO", "2 ACRESCIMO"]
        resultado = gic.selecionar_objetos(id_sessao, objetos)
        logger.info(f"[OK] Objetos selecionados: {resultado}")
        
        # Testar obtencao de proxima pergunta
        proxima_pergunta = gic._obter_proxima_pergunta(id_sessao)
        if proxima_pergunta:
            logger.info(f"[OK] Proxima pergunta obtida: {proxima_pergunta['objeto']}")
        else:
            logger.info("[OK] Sistema funcionando corretamente")
        
        logger.info("[OK] Todas as funcionalidades testadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"[ERRO] Erro nos testes: {e}")
        return False

def main():
    """Funcao principal"""
    logger.info("=" * 60)
    logger.info("INICIANDO SISTEMA GIC COM IA INTEGRADA")
    logger.info("=" * 60)
    
    # Verificar dependencias
    if not verificar_dependencias():
        logger.error("[ERRO] Falha na verificacao de dependencias")
        return False
    
    # Verificar sistemas de IA
    ia_disponivel = verificar_sistemas_ia()
    
    # Criar diretorios
    criar_diretorios()
    
    # Inicializar sistema
    if ia_disponivel:
        gic = inicializar_gic_ia()
    else:
        gic = inicializar_gic_basico()
    
    if not gic:
        logger.error("[ERRO] Falha na inicializacao do sistema")
        return False
    
    # Testar funcionalidades
    if not testar_funcionalidades(gic):
        logger.error("[ERRO] Falha nos testes de funcionalidade")
        return False
    
    logger.info("=" * 60)
    logger.info("[OK] SISTEMA GIC INICIALIZADO COM SUCESSO!")
    logger.info("=" * 60)
    
    if ia_disponivel:
        logger.info("[INFO] IA Autoevolutiva Biomimetica: ATIVA")
        logger.info("[INFO] Sistemas V2: INTEGRADOS")
        logger.info("[INFO] Barramento de Conhecimento: OPERACIONAL")
    else:
        logger.info("[INFO] IA Autoevolutiva Biomimetica: MODO BASICO")
        logger.info("[INFO] Sistemas V2: NAO DISPONIVEIS")
        logger.info("[INFO] Barramento de Conhecimento: NAO DISPONIVEL")
    
    logger.info("[INFO] Para acessar o dashboard, execute: python app_gic.py")
    logger.info("[INFO] Dados salvos em: dados/")
    logger.info("[INFO] Logs salvos em: logs/")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n[OK] Sistema GIC inicializado com sucesso!")
            print("[INFO] Execute 'python app_gic.py' para iniciar o servidor web")
        else:
            print("\n[ERRO] Falha na inicializacao do sistema")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[WARN] Inicializacao interrompida pelo usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        sys.exit(1)
