"""
Integração com Scikit-learn para machine learning
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class ScikitLearnIntegration:
    """Integração com Scikit-learn para machine learning"""
    
    def __init__(self):
        """Inicializa a integração com Scikit-learn"""
        self.initialized = False
        self.models = {}
        
        try:
            self._import_sklearn_modules()
            self.initialized = True
            logger.info("Scikit-learn Integration inicializada com sucesso")
            print("✓ Scikit-learn Integration inicializada")
        except Exception as e:
            logger.error(f"Erro ao inicializar Scikit-learn Integration: {e}")
            print(f"✗ Erro ao inicializar Scikit-learn: {e}")
            self.initialized = False
    
    def _import_sklearn_modules(self):
        """Importa módulos do Scikit-learn"""
        try:
            # Importações básicas
            from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
            from sklearn.preprocessing import StandardScaler, LabelEncoder
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
            from sklearn.linear_model import LinearRegression, LogisticRegression
            from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
            from sklearn.cluster import KMeans
            from sklearn.decomposition import PCA
            
            # Armazenar referências
            self.train_test_split = train_test_split
            self.cross_val_score = cross_val_score
            self.GridSearchCV = GridSearchCV
            self.StandardScaler = StandardScaler
            self.LabelEncoder = LabelEncoder
            self.RandomForestClassifier = RandomForestClassifier
            self.RandomForestRegressor = RandomForestRegressor
            self.LinearRegression = LinearRegression
            self.LogisticRegression = LogisticRegression
            self.accuracy_score = accuracy_score
            self.mean_squared_error = mean_squared_error
            self.classification_report = classification_report
            self.KMeans = KMeans
            self.PCA = PCA
            
            logger.info("Módulos Scikit-learn importados com sucesso")
            
        except ImportError as e:
            logger.error(f"Erro ao importar módulos Scikit-learn: {e}")
            raise
    
    def create_model(self, model_type: str, **kwargs) -> Any:
        """Cria um modelo de machine learning"""
        if not self.initialized:
            raise RuntimeError("Scikit-learn Integration não inicializada")
        
        try:
            if model_type == 'random_forest_classifier':
                model = self.RandomForestClassifier(**kwargs)
            elif model_type == 'random_forest_regressor':
                model = self.RandomForestRegressor(**kwargs)
            elif model_type == 'linear_regression':
                model = self.LinearRegression(**kwargs)
            elif model_type == 'logistic_regression':
                model = self.LogisticRegression(**kwargs)
            elif model_type == 'kmeans':
                model = self.KMeans(**kwargs)
            else:
                raise ValueError(f"Tipo de modelo não suportado: {model_type}")
            
            model_id = f"{model_type}_{len(self.models)}"
            self.models[model_id] = model
            
            logger.info(f"Modelo {model_type} criado com ID: {model_id}")
            return model_id
            
        except Exception as e:
            logger.error(f"Erro ao criar modelo {model_type}: {e}")
            raise
    
    def train_model(self, model_id: str, X: np.ndarray, y: np.ndarray, 
                   test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """Treina um modelo"""
        if not self.initialized:
            raise RuntimeError("Scikit-learn Integration não inicializada")
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        try:
            model = self.models[model_id]
            
            # Dividir dados
            X_train, X_test, y_train, y_test = self.train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Treinar modelo
            model.fit(X_train, y_train)
            
            # Fazer predições
            y_pred = model.predict(X_test)
            
            # Calcular métricas
            if hasattr(model, 'predict_proba'):
                # Classificador
                accuracy = self.accuracy_score(y_test, y_pred)
                report = self.classification_report(y_test, y_pred, output_dict=True)
                metrics = {
                    'accuracy': accuracy,
                    'precision': report['weighted avg']['precision'],
                    'recall': report['weighted avg']['recall'],
                    'f1_score': report['weighted avg']['f1-score']
                }
            else:
                # Regressor
                mse = self.mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                metrics = {
                    'mse': mse,
                    'rmse': rmse,
                    'r2_score': model.score(X_test, y_test)
                }
            
            # Armazenar dados de treinamento
            self.models[f"{model_id}_train_data"] = {
                'X_train': X_train,
                'X_test': X_test,
                'y_train': y_train,
                'y_test': y_test,
                'y_pred': y_pred
            }
            
            logger.info(f"Modelo {model_id} treinado com sucesso")
            return {
                'model_id': model_id,
                'metrics': metrics,
                'train_size': len(X_train),
                'test_size': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Erro ao treinar modelo {model_id}: {e}")
            raise
    
    def predict(self, model_id: str, X: np.ndarray) -> np.ndarray:
        """Faz predições usando um modelo treinado"""
        if not self.initialized:
            raise RuntimeError("Scikit-learn Integration não inicializada")
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        try:
            model = self.models[model_id]
            predictions = model.predict(X)
            
            logger.info(f"Predições feitas para {len(X)} amostras usando modelo {model_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao fazer predições com modelo {model_id}: {e}")
            raise
    
    def cross_validate(self, model_id: str, X: np.ndarray, y: np.ndarray, 
                      cv: int = 5) -> Dict[str, Any]:
        """Realiza validação cruzada"""
        if not self.initialized:
            raise RuntimeError("Scikit-learn Integration não inicializada")
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        try:
            model = self.models[model_id]
            
            # Validação cruzada
            scores = self.cross_val_score(model, X, y, cv=cv)
            
            results = {
                'cv_scores': scores.tolist(),
                'mean_score': scores.mean(),
                'std_score': scores.std(),
                'cv_folds': cv
            }
            
            logger.info(f"Validação cruzada concluída para modelo {model_id}")
            return results
            
        except Exception as e:
            logger.error(f"Erro na validação cruzada do modelo {model_id}: {e}")
            raise
    
    def feature_importance(self, model_id: str) -> List[Tuple[str, float]]:
        """Retorna importância das features para modelos baseados em árvores"""
        if not self.initialized:
            raise RuntimeError("Scikit-learn Integration não inicializada")
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        try:
            model = self.models[model_id]
            
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                feature_names = [f"feature_{i}" for i in range(len(importances))]
                
                # Ordenar por importância
                feature_importance = list(zip(feature_names, importances))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                
                return feature_importance
            else:
                logger.warning(f"Modelo {model_id} não suporta feature importance")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao obter feature importance do modelo {model_id}: {e}")
            return []
    
    def preprocess_data(self, X: np.ndarray, y: np.ndarray = None, 
                       scale: bool = True, encode_labels: bool = False) -> Tuple[np.ndarray, np.ndarray]:
        """Pré-processa dados"""
        if not self.initialized:
            raise RuntimeError("Scikit-learn Integration não inicializada")
        
        try:
            X_processed = X.copy()
            y_processed = y.copy() if y is not None else None
            
            # Escalar features
            if scale:
                scaler = self.StandardScaler()
                X_processed = scaler.fit_transform(X_processed)
                logger.info("Features escaladas com StandardScaler")
            
            # Codificar labels
            if encode_labels and y_processed is not None:
                label_encoder = self.LabelEncoder()
                y_processed = label_encoder.fit_transform(y_processed)
                logger.info("Labels codificados com LabelEncoder")
            
            return X_processed, y_processed
            
        except Exception as e:
            logger.error(f"Erro no pré-processamento: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status da integração"""
        return {
            'initialized': self.initialized,
            'models_created': len(self.models),
            'available_models': list(self.models.keys()),
            'available_functions': [
                'create_model',
                'train_model',
                'predict',
                'cross_validate',
                'feature_importance',
                'preprocess_data'
            ]
        }
    
    def __str__(self):
        return f"ScikitLearnIntegration(initialized={self.initialized}, models={len(self.models)})" 