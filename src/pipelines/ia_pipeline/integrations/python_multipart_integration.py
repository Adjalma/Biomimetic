"""
Integração Python-Multipart
===========================
Utilitários para upload de arquivos multipart.
NÃO MODIFICAR INSIGHTS CENTRAIS.
"""
import logging

logger = logging.getLogger(__name__)

class PythonMultipartIntegration:
    def __init__(self):
        self.framework_name = "python-multipart"
        self.is_available = False
        
        try:
            from fastapi import UploadFile
            self.UploadFile = UploadFile
            self.is_available = True
            logger.info(f"✅ Python-Multipart integrado com sucesso")
        except ImportError as e:
            logger.warning(f"⚠️ Python-Multipart não disponível: {e}")

    async def save_uploaded_file(self, file, destination: str):
        if not self.is_available:
            return {"success": False, "error": "Python-Multipart não disponível"}
        
        try:
            with open(destination, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return {"success": True, "filename": file.filename, "size": len(content)}
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {e}")
            return {"success": False, "error": str(e)} 