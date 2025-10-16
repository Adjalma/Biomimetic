"""
Integração com NLTK para processamento de linguagem natural
"""

import logging
from typing import List, Dict, Any, Optional
import nltk
import os

logger = logging.getLogger(__name__)

class NLTKIntegration:
    """Integração com NLTK para processamento de linguagem natural"""
    
    def __init__(self):
        """Inicializa a integração com NLTK"""
        self.initialized = False
        self.downloaded_packages = set()
        
        try:
            self._download_required_packages()
            self.initialized = True
            logger.info("NLTK Integration inicializada com sucesso")
            print("✓ NLTK Integration inicializada")
        except Exception as e:
            logger.error(f"Erro ao inicializar NLTK Integration: {e}")
            print(f"✗ Erro ao inicializar NLTK: {e}")
            self.initialized = False
    
    def _download_required_packages(self):
        """Baixa pacotes NLTK necessários"""
        required_packages = [
            'punkt',
            'stopwords',
            'wordnet',
            'averaged_perceptron_tagger',
            'maxent_ne_chunker',
            'words'
        ]
        
        for package in required_packages:
            try:
                nltk.download(package, quiet=True)
                self.downloaded_packages.add(package)
                logger.info(f"Pacote NLTK '{package}' baixado")
            except Exception as e:
                logger.warning(f"Erro ao baixar pacote '{package}': {e}")
    
    def tokenize_text(self, text: str) -> List[str]:
        """Tokeniza texto em palavras"""
        if not self.initialized:
            raise RuntimeError("NLTK Integration não inicializada")
        
        try:
            tokens = nltk.word_tokenize(text)
            return tokens
        except Exception as e:
            logger.error(f"Erro ao tokenizar texto: {e}")
            return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords dos tokens"""
        if not self.initialized:
            return tokens
        
        try:
            stop_words = set(nltk.corpus.stopwords.words('english'))
            filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
            return filtered_tokens
        except Exception as e:
            logger.error(f"Erro ao remover stopwords: {e}")
            return tokens
    
    def pos_tagging(self, tokens: List[str]) -> List[tuple]:
        """Realiza POS tagging dos tokens"""
        if not self.initialized:
            return []
        
        try:
            pos_tags = nltk.pos_tag(tokens)
            return pos_tags
        except Exception as e:
            logger.error(f"Erro no POS tagging: {e}")
            return []
    
    def named_entity_recognition(self, text: str) -> List[tuple]:
        """Reconhece entidades nomeadas"""
        if not self.initialized:
            return []
        
        try:
            tokens = nltk.word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            named_entities = nltk.chunk.ne_chunk(pos_tags)
            
            entities = []
            for chunk in named_entities:
                if hasattr(chunk, 'label'):
                    entities.append((chunk.label(), ' '.join(c[0] for c in chunk)))
            
            return entities
        except Exception as e:
            logger.error(f"Erro no NER: {e}")
            return []
    
    def lemmatize_words(self, tokens: List[str]) -> List[str]:
        """Lematiza palavras"""
        if not self.initialized:
            return tokens
        
        try:
            lemmatizer = nltk.WordNetLemmatizer()
            lemmatized = [lemmatizer.lemmatize(word) for word in tokens]
            return lemmatized
        except Exception as e:
            logger.error(f"Erro na lematização: {e}")
            return tokens
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """Extrai palavras-chave do texto"""
        if not self.initialized:
            return []
        
        try:
            # Tokenização e limpeza
            tokens = self.tokenize_text(text)
            tokens = self.remove_stopwords(tokens)
            tokens = self.lemmatize_words(tokens)
            
            # Frequência das palavras
            freq_dist = nltk.FreqDist(tokens)
            
            # Top k palavras mais frequentes
            keywords = [word for word, freq in freq_dist.most_common(top_k)]
            return keywords
        except Exception as e:
            logger.error(f"Erro ao extrair keywords: {e}")
            return []
    
    def sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Análise de sentimento básica"""
        if not self.initialized:
            return {'sentiment': 'neutral', 'confidence': 0.0}
        
        try:
            # Análise simples baseada em palavras positivas/negativas
            positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'}
            negative_words = {'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'worst'}
            
            tokens = self.tokenize_text(text.lower())
            
            positive_count = sum(1 for word in tokens if word in positive_words)
            negative_count = sum(1 for word in tokens if word in negative_words)
            
            if positive_count > negative_count:
                sentiment = 'positive'
                confidence = min(0.9, positive_count / (positive_count + negative_count + 1))
            elif negative_count > positive_count:
                sentiment = 'negative'
                confidence = min(0.9, negative_count / (positive_count + negative_count + 1))
            else:
                sentiment = 'neutral'
                confidence = 0.5
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'positive_words': positive_count,
                'negative_words': negative_count
            }
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {e}")
            return {'sentiment': 'neutral', 'confidence': 0.0}
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status da integração"""
        return {
            'initialized': self.initialized,
            'downloaded_packages': list(self.downloaded_packages),
            'nltk_version': nltk.__version__,
            'available_functions': [
                'tokenize_text',
                'remove_stopwords',
                'pos_tagging',
                'named_entity_recognition',
                'lemmatize_words',
                'extract_keywords',
                'sentiment_analysis'
            ]
        }
    
    def __str__(self):
        return f"NLTKIntegration(initialized={self.initialized}, packages={len(self.downloaded_packages)})"
