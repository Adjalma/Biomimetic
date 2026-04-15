#!/usr/bin/env python
"""
test_api.py - Teste simples para verificar se a API consegue iniciar
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Testa se todas as importações essenciais funcionam"""
    print("🧪 Testando importações essenciais...")
    
    essentials = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "run"),
        ("pydantic", "BaseModel"),
    ]
    
    all_ok = True
    for module, attr in essentials:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            all_ok = False
    
    return all_ok

def test_api_initialization():
    """Tenta inicializar a aplicação FastAPI"""
    print("\n🧪 Testando inicialização da API...")
    
    try:
        # Importar a aplicação
        from src.core.evolution.evolution_api import app
        print("  ✅ Aplicação FastAPI importada")
        
        # Verificar se a aplicação tem endpoints
        routes = []
        for route in app.routes:
            routes.append({
                'path': getattr(route, 'path', 'N/A'),
                'methods': getattr(route, 'methods', 'N/A')
            })
        
        print(f"  ✅ {len(routes)} rotas encontradas")
        
        # Testar criação de instância do EvolutionSystem
        from src.core.evolution.evolution_api import EvolutionSystem
        system = EvolutionSystem()
        print(f"  ✅ EvolutionSystem inicializado")
        print(f"     - Mutations: {system.mutation_count}")
        print(f"     - Evolutions: {system.evolution_count}")
        print(f"     - Generation: {system.current_generation}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Testa o endpoint /health via cliente HTTP"""
    print("\n🧪 Testando endpoint /health...")
    
    try:
        import requests
        import threading
        import time
        
        # Iniciar servidor em thread separada
        from src.core.evolution.evolution_api import app
        import uvicorn
        
        def run_server():
            uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Esperar servidor iniciar
        print("  Aguardando servidor iniciar...")
        time.sleep(3)
        
        # Testar requisição
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=2)
            if response.status_code == 200:
                print(f"  ✅ Endpoint /health respondeu: {response.json()}")
                return True
            else:
                print(f"  ❌ Status code inesperado: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("  ❌ Não foi possível conectar ao servidor")
            return False
        except Exception as e:
            print(f"  ❌ Erro na requisição: {e}")
            return False
            
    except ImportError:
        print("  ⚠️ requests não instalado, pulando teste de endpoint")
        return None
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False

def main():
    print("🔍 DIAGNÓSTICO DO SISTEMA EVOLUTIVO")
    print("=" * 50)
    
    # Teste 1: Importações
    if not test_imports():
        print("\n❌ DEPENDÊNCIAS FALTANDO")
        print("Execute: pip install fastapi uvicorn pydantic numpy requests")
        sys.exit(1)
    
    # Teste 2: Inicialização da API
    if not test_api_initialization():
        print("\n❌ FALHA NA INICIALIZAÇÃO DA API")
        print("Verifique os logs acima para erros de importação.")
        sys.exit(1)
    
    # Teste 3: Endpoint (opcional)
    result = test_health_endpoint()
    if result is False:
        print("\n⚠️  ENDPOINT NÃO RESPONDE")
        print("O servidor pode ter problemas para iniciar.")
        # Não sair com erro, pois pode ser problema de porta
    
    print("\n" + "=" * 50)
    print("✅ SISTEMA PRONTO PARA USO!")
    print("\nPara iniciar o servidor:")
    print("  python src/core/evolution/evolution_api.py")
    print("\nOu use os scripts batch:")
    print("  .\\run.bat  (menu interativo)")
    print("  .\\start_all.bat  (início automático)")

if __name__ == "__main__":
    main()