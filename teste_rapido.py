#!/usr/bin/env python3
"""
TESTE RÁPIDO DO SISTEMA BIOMIMÉTICO
===================================

Script de validação rápida para verificar se todas as dependências
estão instaladas corretamente.

Execute após instalar as dependências:
python teste_rapido.py
"""

import sys
import importlib.util
from datetime import datetime

def check_python_version():
    """Verifica versão do Python"""
    print("🔍 Verificando Python...")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("  ✅ Versão Python OK (3.11+)")
        return True
    else:
        print(f"  ⚠️  Versão Python {version.major}.{version.minor} - Recomendado 3.11+")
        return False

def check_module(module_name, pip_name=None):
    """Verifica se um módulo está instalado"""
    try:
        if pip_name is None:
            pip_name = module_name
        
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"  ❌ {module_name} NÃO instalado")
            print(f"     Execute: pip install {pip_name}")
            return False
        else:
            # Tenta importar para ver versão
            module = importlib.import_module(module_name)
            if hasattr(module, '__version__'):
                print(f"  ✅ {module_name} v{module.__version__}")
            else:
                print(f"  ✅ {module_name} OK")
            return True
    except ImportError as e:
        print(f"  ❌ {module_name} erro: {e}")
        print(f"     Execute: pip install {pip_name}")
        return False

def check_essential_modules():
    """Verifica módulos essenciais"""
    print("\n🔍 Verificando módulos essenciais...")
    
    essentials = [
        ("numpy", "numpy"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn[standard]"),
        ("pydantic", "pydantic"),
        ("requests", "requests"),
    ]
    
    results = []
    for module_name, pip_name in essentials:
        results.append(check_module(module_name, pip_name))
    
    return all(results)

def check_optional_modules():
    """Verifica módulos opcionais"""
    print("\n🔍 Verificando módulos opcionais...")
    
    optionals = [
        ("plotly", "plotly"),
        ("shap", "shap"),
        ("lime", "lime"),
        ("boto3", "boto3"),
        ("torch", "torch"),
        ("transformers", "transformers"),
    ]
    
    for module_name, pip_name in optionals:
        check_module(module_name, pip_name)

def check_system_imports():
    """Tenta importar componentes do sistema biomimético"""
    print("\n🔍 Verificando importações do sistema...")
    
    try:
        # Adiciona src ao path
        sys.path.insert(0, 'src')
        
        # Tenta importar módulos principais
        imports_to_test = [
            "core.evolution.evolution_engine",
            "core.evolution.genome_mutator", 
            "core.evolution.brain_evolver",
            "systems.auto_evolving_ai_system",
        ]
        
        for module_path in imports_to_test:
            try:
                module = importlib.import_module(module_path)
                print(f"  ✅ {module_path.split('.')[-1]}")
            except ImportError as e:
                print(f"  ⚠️  {module_path.split('.')[-1]}: {e}")
                
        return True
    except Exception as e:
        print(f"  ❌ Erro ao verificar sistema: {e}")
        return False

def create_simple_test():
    """Cria um teste simples do sistema evolutivo"""
    print("\n🧪 Criando teste simples do sistema...")
    
    test_code = '''#!/usr/bin/env python3
"""
TESTE SIMPLES DO SISTEMA BIOMIMÉTICO
=====================================

Execute após instalar dependências:
python teste_sistema.py
"""

import sys
sys.path.insert(0, 'src')

try:
    # Teste de importação básica
    from core.evolution.evolution_engine import EvolutionEngine
    
    print("✅ EvolutionEngine importado com sucesso!")
    
    # Criação básica
    engine = EvolutionEngine(population_size=3, generations=1)
    print(f"✅ Engine criada: {engine}")
    
    # Teste de execução
    print("📊 Executando ciclo evolutivo...")
    engine.run()
    
    print("\\n🎉 SISTEMA BIOMIMÉTICO FUNCIONANDO!")
    print("\\n✅ Próximos passos:")
    print("   1. Inicie a API: python src/core/evolution/evolution_api.py")
    print("   2. Acesse: http://localhost:8000/health")
    print("   3. Gere dashboard: python src/core/evolution/evolution_dashboard.py --generate")
    
except ImportError as e:
    print(f"❌ ImportError: {e}")
    print("   Verifique se está na pasta correta do projeto")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
'''
    
    try:
        with open('teste_sistema.py', 'w') as f:
            f.write(test_code)
        
        print("  📄 Arquivo 'teste_sistema.py' criado")
        print("  ▶️  Execute: python teste_sistema.py")
        return True
    except Exception as e:
        print(f"  ❌ Erro ao criar arquivo: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("🧬 VALIDAÇÃO DO SISTEMA BIOMIMÉTICO")
    print("="*60)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.executable}")
    print()
    
    # Verificações
    py_ok = check_python_version()
    essential_ok = check_essential_modules()
    
    print("\n" + "-"*60)
    
    if not py_ok or not essential_ok:
        print("\n❌ PROBLEMAS ENCONTRADOS:")
        if not py_ok:
            print("  - Python 3.11+ necessário")
        if not essential_ok:
            print("  - Módulos essenciais faltando")
        print("\n🔧 Execute os comandos sugeridos acima")
        return 1
    
    # Verificações opcionais
    check_optional_modules()
    
    # Verifica sistema
    sys_ok = check_system_imports()
    
    # Cria teste
    create_simple_test()
    
    print("\n" + "="*60)
    print("🎯 PRÓXIMOS PASSOS:")
    print("="*60)
    print("1. Execute o teste criado:")
    print("   python teste_sistema.py")
    print()
    print("2. Inicie a API evolutiva:")
    print("   python src/core/evolution/evolution_api.py")
    print()
    print("3. Acesse o dashboard:")
    print("   http://localhost:8000/health")
    print()
    print("4. Gere dashboard evolutivo:")
    print("   python src/core/evolution/evolution_dashboard.py --generate")
    print()
    print("📞 Se houver erros, envie a mensagem completa para mim.")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())