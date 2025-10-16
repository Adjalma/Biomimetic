"""
Integração Sphinx-RTD-Theme
===========================
Utilitários para tema de documentação Read the Docs.
NÃO MODIFICAR INSIGHTS CENTRAIS.
"""
import logging

logger = logging.getLogger(__name__)

class SphinxRtdThemeIntegration:
    def __init__(self):
        self.framework_name = "sphinx-rtd-theme"
        self.is_available = True

    def configure_rtd_theme(self, conf_py_path):
        try:
            # Configuration for Read the Docs theme
            return {"success": True, "theme": "sphinx_rtd_theme"}
        except Exception as e:
            logger.error(f"Erro ao configurar tema RTD: {e}")
            return {"success": False, "error": str(e)} 