"""
Integração com Transformers para modelos de linguagem
"""

import logging
from typing import List, Dict, Any, Optional, Union
import torch
import numpy as np

logger = logging.getLogger(__name__)

class TransformersIntegration:
    """Integração com Transformers para modelos de linguagem"""
    
    def __init__(self):
        """Inicializa a integração com Transformers"""
        self.initialized = False
        self.models = {}
        self.tokenizers = {}
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        try:
            self._import_transformers_modules()
            self.initialized = True
            logger.info("Transformers Integration inicializada com sucesso")
            print(f"✓ Transformers Integration inicializada (device: {self.device})")
        except Exception as e:
            logger.error(f"Erro ao inicializar Transformers Integration: {e}")
            print(f"✗ Erro ao inicializar Transformers: {e}")
            self.initialized = False
    
    def _import_transformers_modules(self):
        """Importa módulos do Transformers"""
        try:
            from transformers import (
                AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
                AutoModelForTokenClassification, AutoModelForQuestionAnswering,
                pipeline, TextGenerationPipeline, QuestionAnsweringPipeline
            )
            
            # Armazenar referências
            self.AutoTokenizer = AutoTokenizer
            self.AutoModel = AutoModel
            self.AutoModelForSequenceClassification = AutoModelForSequenceClassification
            self.AutoModelForTokenClassification = AutoModelForTokenClassification
            self.AutoModelForQuestionAnswering = AutoModelForQuestionAnswering
            self.pipeline = pipeline
            self.TextGenerationPipeline = TextGenerationPipeline
            self.QuestionAnsweringPipeline = QuestionAnsweringPipeline
            
            logger.info("Módulos Transformers importados com sucesso")
            
        except ImportError as e:
            logger.error(f"Erro ao importar módulos Transformers: {e}")
            raise
    
    def load_model(self, model_name: str, task: str = None) -> str:
        """Carrega um modelo do Hugging Face"""
        if not self.initialized:
            raise RuntimeError("Transformers Integration não inicializada")
        
        try:
            model_id = f"{model_name}_{task or 'base'}"
            
            if task == 'text-classification':
                model = self.AutoModelForSequenceClassification.from_pretrained(model_name)
                tokenizer = self.AutoTokenizer.from_pretrained(model_name)
            elif task == 'token-classification':
                model = self.AutoModelForTokenClassification.from_pretrained(model_name)
                tokenizer = self.AutoTokenizer.from_pretrained(model_name)
            elif task == 'question-answering':
                model = self.AutoModelForQuestionAnswering.from_pretrained(model_name)
                tokenizer = self.AutoTokenizer.from_pretrained(model_name)
            else:
                model = self.AutoModel.from_pretrained(model_name)
                tokenizer = self.AutoTokenizer.from_pretrained(model_name)
            
            # Mover para device
            model = model.to(self.device)
            
            # Armazenar modelo e tokenizer
            self.models[model_id] = model
            self.tokenizers[model_id] = tokenizer
            
            logger.info(f"Modelo {model_name} carregado com sucesso para task: {task}")
            return model_id
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo {model_name}: {e}")
            raise
    
    def create_pipeline(self, task: str, model_name: str, **kwargs) -> str:
        """Cria um pipeline para uma tarefa específica"""
        if not self.initialized:
            raise RuntimeError("Transformers Integration não inicializada")
        
        try:
            pipeline_id = f"{task}_{model_name}"
            
            # Configurar parâmetros padrão
            default_kwargs = {
                'device': self.device,
                'model': model_name
            }
            default_kwargs.update(kwargs)
            
            # Criar pipeline
            pipe = self.pipeline(task, **default_kwargs)
            
            # Armazenar pipeline
            self.models[pipeline_id] = pipe
            
            logger.info(f"Pipeline {task} criado com sucesso para modelo {model_name}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"Erro ao criar pipeline {task}: {e}")
            raise
    
    def generate_text(self, model_id: str, prompt: str, max_length: int = 100, 
                     temperature: float = 0.7, **kwargs) -> str:
        """Gera texto usando um modelo"""
        if not self.initialized:
            raise RuntimeError("Transformers Integration não inicializada")
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        try:
            model = self.models[model_id]
            tokenizer = self.tokenizers.get(model_id)
            
            if tokenizer is None:
                raise ValueError(f"Tokenizer não encontrado para modelo {model_id}")
            
            # Tokenizar input
            inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Gerar texto
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decodificar output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            logger.info(f"Texto gerado com sucesso usando modelo {model_id}")
            return generated_text
            
        except Exception as e:
            logger.error(f"Erro ao gerar texto com modelo {model_id}: {e}")
            raise
    
    def classify_text(self, model_id: str, text: str) -> Dict[str, Any]:
        """Classifica texto usando um modelo de classificação"""
        if not self.initialized:
            raise RuntimeError("Transformers Integration não inicializada")
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        try:
            model = self.models[model_id]
            tokenizer = self.tokenizers[model_id]
            
            # Tokenizar texto
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
            
            # Fazer predição
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            # Obter classe predita
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Obter nome da classe se disponível
            if hasattr(model.config, 'id2label'):
                class_name = model.config.id2label[predicted_class]
            else:
                class_name = f"class_{predicted_class}"
            
            results = {
                'predicted_class': predicted_class,
                'class_name': class_name,
                'confidence': confidence,
                'probabilities': probabilities[0].tolist()
            }
            
            logger.info(f"Texto classificado com sucesso usando modelo {model_id}")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao classificar texto com modelo {model_id}: {e}")
            raise
    
    def extract_embeddings(self, model_id: str, texts: Union[str, List[str]]) -> np.ndarray:
        """Extrai embeddings de textos"""
        if not self.initialized:
            raise RuntimeError("Transformers Integration não inicializada")
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        try:
            model = self.models[model_id]
            tokenizer = self.tokenizers[model_id]
            
            if isinstance(texts, str):
                texts = [texts]
            
            embeddings = []
            
            for text in texts:
                # Tokenizar texto
                inputs = tokenizer(text, return_tensors="pt", truncation=True, 
                                 max_length=512, padding=True).to(self.device)
                
                # Extrair embeddings
                with torch.no_grad():
                    outputs = model(**inputs)
                    # Usar último hidden state como embedding
                    embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                    embeddings.append(embedding.flatten())
            
            embeddings_array = np.array(embeddings)
            
            logger.info(f"Embeddings extraídos com sucesso para {len(texts)} textos")
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Erro ao extrair embeddings com modelo {model_id}: {e}")
            raise
    
    def question_answering(self, model_id: str, question: str, context: str) -> Dict[str, Any]:
        """Responde perguntas usando um modelo de QA"""
        if not self.initialized:
            raise RuntimeError("Transformers Integration não inicializada")
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        try:
            model = self.models[model_id]
            tokenizer = self.tokenizers[model_id]
            
            # Tokenizar pergunta e contexto
            inputs = tokenizer(
                question,
                context,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Fazer predição
            with torch.no_grad():
                outputs = model(**inputs)
                answer_start = torch.argmax(outputs.start_logits)
                answer_end = torch.argmax(outputs.end_logits) + 1
                
                # Decodificar resposta
                answer_tokens = inputs["input_ids"][0][answer_start:answer_end]
                answer = tokenizer.decode(answer_tokens, skip_special_tokens=True)
                
                # Calcular confiança
                start_score = torch.softmax(outputs.start_logits, dim=-1)[0][answer_start].item()
                end_score = torch.softmax(outputs.end_logits, dim=-1)[0][answer_end-1].item()
                confidence = (start_score + end_score) / 2
            
            results = {
                'answer': answer,
                'confidence': confidence,
                'start_score': start_score,
                'end_score': end_score
            }
            
            logger.info(f"Pergunta respondida com sucesso usando modelo {model_id}")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao responder pergunta com modelo {model_id}: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status da integração"""
        return {
            'initialized': self.initialized,
            'device': self.device,
            'models_loaded': len(self.models),
            'tokenizers_loaded': len(self.tokenizers),
            'available_models': list(self.models.keys()),
            'available_functions': [
                'load_model',
                'create_pipeline',
                'generate_text',
                'classify_text',
                'extract_embeddings',
                'question_answering'
            ]
        }
    
    def __str__(self):
        return f"TransformersIntegration(initialized={self.initialized}, device={self.device}, models={len(self.models)})" 