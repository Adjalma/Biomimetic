import sys
import os

print("Python version:", sys.version)
print("Current directory:", os.getcwd())

try:
    sys.path.insert(0, 'justifications')
    from gic_ia_integrada import GICIAIntegrada
    print("✓ GIC class imported successfully")
    
    gic = GICIAIntegrada()
    print("✓ GIC instance created")
    
    resultado = gic.iniciar_fluxo()
    print("✓ Flow started:", type(resultado))
    
except Exception as e:
    print("✗ Error:", str(e))
    import traceback
    traceback.print_exc()
