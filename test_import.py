import sys
sys.path.insert(0, 'src')
try:
    import app.bio_console_api
    print("✅ Importação bem-sucedida")
except Exception as e:
    print(f"❌ Erro de importação: {e}")
    import traceback
    traceback.print_exc()