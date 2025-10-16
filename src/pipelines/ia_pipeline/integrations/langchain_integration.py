"""
Integração com LangChain para processamento de linguagem natural
"""

import logging
from typing import List, Dict, Any, Optional
import os

# Imports corrigidos para LangChain v0.2+
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_community.llms import OpenAI
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    print("✓ LangChain v0.2+ importado com sucesso")
except ImportError:
    # Fallback para versão antiga
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.llms import OpenAI
        from langchain.schema import Document
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        print("✓ LangChain versão antiga importado com sucesso")
    except ImportError as e:
        print(f"✗ Erro ao importar LangChain: {e}")
        raise

logger = logging.getLogger(__name__)

class LangchainIntegration:
    """Integração com LangChain para processamento de linguagem natural"""
    
    def __init__(self):
        """Inicializa a integração com LangChain"""
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.text_splitter = None
        self.initialized = False
        
        try:
            self._initialize_components()
            self.initialized = True
            logger.info("LangChain Integration inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar LangChain Integration: {e}")
            self.initialized = False
    
    def _initialize_components(self):
        """Inicializa os componentes do LangChain"""
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Embeddings (usando modelo local se disponível)
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            logger.info("Embeddings HuggingFace carregados")
        except Exception as e:
            logger.warning(f"Erro ao carregar embeddings: {e}")
            self.embeddings = None
        
        # LLM (OpenAI se API key disponível)
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.llm = OpenAI(
                    temperature=0.7,
                    max_tokens=1000,
                    api_key=api_key
                )
                logger.info("LLM OpenAI configurado")
            except Exception as e:
                logger.warning(f"Erro ao configurar OpenAI: {e}")
                self.llm = None
        else:
            logger.info("OpenAI API key não encontrada")
    
    def process_text(self, text: str) -> List[Document]:
        """Processa texto e retorna documentos"""
        if not self.initialized:
            raise RuntimeError("LangChain Integration não inicializada")
        
        try:
            documents = self.text_splitter.split_text(text)
            return [Document(page_content=doc) for doc in documents]
        except Exception as e:
            logger.error(f"Erro ao processar texto: {e}")
            return []
    
    def create_vectorstore(self, documents: List[Document], persist_directory: str = None) -> bool:
        """Cria um vectorstore FAISS"""
        if not self.embeddings:
            logger.error("Embeddings não disponíveis")
            return False
        
        try:
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
            
            if persist_directory:
                self.vectorstore.save_local(persist_directory)
                logger.info(f"Vectorstore salvo em: {persist_directory}")
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar vectorstore: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Realiza busca por similaridade"""
        if not self.vectorstore:
            logger.error("Vectorstore não disponível")
            return []
        
        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {e}")
            return []
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Gera resposta usando LLM"""
        if not self.llm:
            logger.error("LLM não disponível")
            return "LLM não configurado"
        
        try:
            template = PromptTemplate(
                input_variables=["context", "prompt"],
                template="Contexto: {context}\n\nPergunta: {prompt}\n\nResposta:"
            )
            
            chain = LLMChain(llm=self.llm, prompt=template)
            response = chain.run(context=context, prompt=prompt)
            
            return response.strip()
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return f"Erro: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status da integração"""
        return {
            'initialized': self.initialized,
            'embeddings_available': self.embeddings is not None,
            'vectorstore_available': self.vectorstore is not None,
            'llm_available': self.llm is not None,
            'text_splitter_available': self.text_splitter is not None
        }
    
    def __str__(self):
        return f"LangchainIntegration(initialized={self.initialized})" 