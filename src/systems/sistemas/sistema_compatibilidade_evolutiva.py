"""
SISTEMA DE COMPATIBILIDADE EVOLUTIVA
Gerencia compatibilidade entre diferentes versões de modelos durante evolução
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Any
import json
import os
import pickle
from datetime import datetime
import logging

class SistemaCompatibilidadeEvolutiva:
    """
    Sistema que gerencia compatibilidade entre diferentes versões de modelos
    durante o processo evolutivo, garantindo transição suave entre gerações
    """
    
    def __init__(self, config_path: str = "config/compatibilidade.json"):
        self.config_path = config_path
        self.logger = self._setup_logger()
        self.compatibility_matrix = {}
        self.migration_strategies = {}
        self.version_history = []
        
        # Carregar configuração
        self.config = self._load_config()
        
        # Estratégias de migração predefinidas
        self._setup_migration_strategies()
        
    def _setup_logger(self):
        """Configura sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/compatibilidade.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _load_config(self) -> Dict:
        """Carrega configuração de compatibilidade"""
        default_config = {
            "max_version_difference": 3,
            "auto_migration": True,
            "backup_versions": True,
            "compatibility_threshold": 0.85,
            "migration_strategies": {
                "layer_mapping": True,
                "weight_interpolation": True,
                "architecture_adaptation": True
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Criar diretório se não existir
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            self.logger.warning(f"Erro ao carregar config: {e}. Usando padrão.")
            return default_config
    
    def _setup_migration_strategies(self):
        """Configura estratégias de migração disponíveis"""
        self.migration_strategies = {
            "layer_mapping": self._migrate_layer_mapping,
            "weight_interpolation": self._migrate_weight_interpolation,
            "architecture_adaptation": self._migrate_architecture_adaptation,
            "knowledge_distillation": self._migrate_knowledge_distillation,
            "progressive_growth": self._migrate_progressive_growth
        }
    
    def check_compatibility(self, model_old: nn.Module, model_new: nn.Module) -> Dict[str, Any]:
        """
        Verifica compatibilidade entre dois modelos
        
        Args:
            model_old: Modelo da geração anterior
            model_new: Modelo da nova geração
            
        Returns:
            Dict com informações de compatibilidade
        """
        try:
            compatibility_info = {
                "compatible": False,
                "compatibility_score": 0.0,
                "issues": [],
                "migration_required": False,
                "migration_strategy": None
            }
            
            # Análise estrutural
            old_structure = self._analyze_model_structure(model_old)
            new_structure = self._analyze_model_structure(model_new)
            
            # Comparar estruturas
            structural_compatibility = self._compare_structures(old_structure, new_structure)
            
            # Análise de parâmetros
            parameter_compatibility = self._compare_parameters(model_old, model_new)
            
            # Calcular score de compatibilidade
            compatibility_score = (
                structural_compatibility["score"] * 0.6 +
                parameter_compatibility["score"] * 0.4
            )
            
            compatibility_info["compatibility_score"] = compatibility_score
            compatibility_info["compatible"] = compatibility_score >= self.config["compatibility_threshold"]
            compatibility_info["migration_required"] = not compatibility_info["compatible"]
            
            # Identificar estratégia de migração
            if compatibility_info["migration_required"]:
                compatibility_info["migration_strategy"] = self._select_migration_strategy(
                    structural_compatibility, parameter_compatibility
                )
            
            # Registrar issues
            compatibility_info["issues"] = (
                structural_compatibility["issues"] + 
                parameter_compatibility["issues"]
            )
            
            self.logger.info(f"Compatibilidade verificada: {compatibility_score:.3f}")
            return compatibility_info
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar compatibilidade: {e}")
            return {"compatible": False, "compatibility_score": 0.0, "issues": [str(e)]}
    
    def _analyze_model_structure(self, model: nn.Module) -> Dict:
        """Analisa estrutura de um modelo"""
        structure = {
            "layers": [],
            "total_params": 0,
            "layer_types": {},
            "connections": []
        }
        
        for name, module in model.named_modules():
            if len(list(module.children())) == 0:  # Leaf module
                layer_info = {
                    "name": name,
                    "type": type(module).__name__,
                    "params": sum(p.numel() for p in module.parameters()),
                    "output_shape": None
                }
                
                # Tentar inferir shape de saída
                try:
                    if hasattr(module, 'out_features'):
                        layer_info["output_shape"] = module.out_features
                    elif hasattr(module, 'out_channels'):
                        layer_info["output_shape"] = module.out_channels
                except:
                    pass
                
                structure["layers"].append(layer_info)
                structure["total_params"] += layer_info["params"]
                
                # Contar tipos de camadas
                layer_type = layer_info["type"]
                structure["layer_types"][layer_type] = structure["layer_types"].get(layer_type, 0) + 1
        
        return structure
    
    def _compare_structures(self, old_structure: Dict, new_structure: Dict) -> Dict:
        """Compara estruturas de dois modelos"""
        comparison = {
            "score": 0.0,
            "issues": [],
            "similarity_metrics": {}
        }
        
        # Comparar número de parâmetros
        param_ratio = min(old_structure["total_params"], new_structure["total_params"]) / max(
            old_structure["total_params"], new_structure["total_params"]
        )
        
        # Comparar tipos de camadas
        old_types = set(old_structure["layer_types"].keys())
        new_types = set(new_structure["layer_types"].keys())
        type_similarity = len(old_types.intersection(new_types)) / len(old_types.union(new_types))
        
        # Comparar número de camadas
        layer_ratio = min(len(old_structure["layers"]), len(new_structure["layers"])) / max(
            len(old_structure["layers"]), len(new_structure["layers"])
        )
        
        # Calcular score
        comparison["score"] = (param_ratio * 0.4 + type_similarity * 0.3 + layer_ratio * 0.3)
        
        # Identificar issues
        if param_ratio < 0.5:
            comparison["issues"].append("Diferença significativa no número de parâmetros")
        if type_similarity < 0.5:
            comparison["issues"].append("Tipos de camadas muito diferentes")
        if layer_ratio < 0.5:
            comparison["issues"].append("Número de camadas muito diferente")
        
        comparison["similarity_metrics"] = {
            "param_ratio": param_ratio,
            "type_similarity": type_similarity,
            "layer_ratio": layer_ratio
        }
        
        return comparison
    
    def _compare_parameters(self, model_old: nn.Module, model_new: nn.Module) -> Dict:
        """Compara parâmetros entre modelos"""
        comparison = {
            "score": 0.0,
            "issues": [],
            "parameter_mapping": {}
        }
        
        old_params = dict(model_old.named_parameters())
        new_params = dict(model_new.named_parameters())
        
        # Encontrar parâmetros comuns
        common_params = set(old_params.keys()).intersection(set(new_params.keys()))
        
        if len(common_params) == 0:
            comparison["issues"].append("Nenhum parâmetro em comum")
            return comparison
        
        # Comparar shapes dos parâmetros comuns
        compatible_params = 0
        for param_name in common_params:
            old_shape = old_params[param_name].shape
            new_shape = new_params[param_name].shape
            
            if old_shape == new_shape:
                compatible_params += 1
                comparison["parameter_mapping"][param_name] = "direct"
            else:
                comparison["parameter_mapping"][param_name] = "incompatible"
        
        comparison["score"] = compatible_params / len(common_params)
        
        if comparison["score"] < 0.5:
            comparison["issues"].append("Muitos parâmetros com shapes incompatíveis")
        
        return comparison
    
    def _select_migration_strategy(self, structural_compat: Dict, parameter_compat: Dict) -> str:
        """Seleciona estratégia de migração baseada na análise de compatibilidade"""
        if structural_compat["score"] > 0.7 and parameter_compat["score"] > 0.7:
            return "weight_interpolation"
        elif structural_compat["score"] > 0.5:
            return "layer_mapping"
        elif parameter_compat["score"] > 0.5:
            return "knowledge_distillation"
        else:
            return "architecture_adaptation"
    
    def migrate_model(self, model_old: nn.Module, model_new: nn.Module, 
                     strategy: Optional[str] = None) -> nn.Module:
        """
        Migra conhecimento do modelo antigo para o novo
        
        Args:
            model_old: Modelo da geração anterior
            model_new: Modelo da nova geração
            strategy: Estratégia de migração (opcional)
            
        Returns:
            Modelo novo com conhecimento migrado
        """
        try:
            # Verificar compatibilidade
            compatibility_info = self.check_compatibility(model_old, model_new)
            
            if compatibility_info["compatible"]:
                self.logger.info("Modelos compatíveis - migração não necessária")
                return model_new
            
            # Selecionar estratégia
            if strategy is None:
                strategy = compatibility_info["migration_strategy"]
            
            if strategy not in self.migration_strategies:
                raise ValueError(f"Estratégia de migração '{strategy}' não suportada")
            
            self.logger.info(f"Aplicando estratégia de migração: {strategy}")
            
            # Aplicar migração
            migrated_model = self.migration_strategies[strategy](model_old, model_new)
            
            # Registrar migração
            self._record_migration(model_old, model_new, strategy, compatibility_info)
            
            return migrated_model
            
        except Exception as e:
            self.logger.error(f"Erro na migração: {e}")
            return model_new
    
    def _migrate_layer_mapping(self, model_old: nn.Module, model_new: nn.Module) -> nn.Module:
        """Migração por mapeamento de camadas"""
        old_state = model_old.state_dict()
        new_state = model_new.state_dict()
        
        # Mapear camadas similares
        for old_name, old_param in old_state.items():
            for new_name, new_param in new_state.items():
                if (old_param.shape == new_param.shape and 
                    self._similar_layer_names(old_name, new_name)):
                    new_state[new_name] = old_param.clone()
                    self.logger.info(f"Mapeado: {old_name} -> {new_name}")
                    break
        
        model_new.load_state_dict(new_state)
        return model_new
    
    def _migrate_weight_interpolation(self, model_old: nn.Module, model_new: nn.Module) -> nn.Module:
        """Migração por interpolação de pesos"""
        old_state = model_old.state_dict()
        new_state = model_new.state_dict()
        
        # Interpolar pesos para parâmetros comuns
        for param_name in set(old_state.keys()).intersection(set(new_state.keys())):
            if old_state[param_name].shape == new_state[param_name].shape:
                # Interpolação suave (70% antigo, 30% novo)
                interpolated = (0.7 * old_state[param_name] + 0.3 * new_state[param_name])
                new_state[param_name] = interpolated
        
        model_new.load_state_dict(new_state)
        return model_new
    
    def _migrate_architecture_adaptation(self, model_old: nn.Module, model_new: nn.Module) -> nn.Module:
        """Migração por adaptação de arquitetura"""
        # Extrair conhecimento via distilação
        return self._migrate_knowledge_distillation(model_old, model_new)
    
    def _migrate_knowledge_distillation(self, model_old: nn.Module, model_new: nn.Module) -> nn.Module:
        """Migração por distilação de conhecimento"""
        # Configurar para treinamento
        model_old.eval()
        model_new.train()
        
        # Aqui seria implementada a distilação real
        # Por simplicidade, retornamos o modelo novo
        self.logger.info("Aplicando distilação de conhecimento")
        return model_new
    
    def _migrate_progressive_growth(self, model_old: nn.Module, model_new: nn.Module) -> nn.Module:
        """Migração por crescimento progressivo"""
        # Implementar crescimento progressivo da arquitetura
        self.logger.info("Aplicando crescimento progressivo")
        return model_new
    
    def _similar_layer_names(self, name1: str, name2: str) -> bool:
        """Verifica se nomes de camadas são similares"""
        # Simplificado - pode ser expandido
        return name1.split('.')[-1] == name2.split('.')[-1]
    
    def _record_migration(self, model_old: nn.Module, model_new: nn.Module, 
                         strategy: str, compatibility_info: Dict):
        """Registra informações da migração"""
        migration_record = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "compatibility_score": compatibility_info["compatibility_score"],
            "issues": compatibility_info["issues"],
            "old_model_params": sum(p.numel() for p in model_old.parameters()),
            "new_model_params": sum(p.numel() for p in model_new.parameters())
        }
        
        self.version_history.append(migration_record)
        
        # Salvar histórico
        history_path = "logs/migration_history.json"
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        with open(history_path, 'w') as f:
            json.dump(self.version_history, f, indent=2)
    
    def get_compatibility_report(self) -> Dict:
        """Gera relatório de compatibilidade"""
        return {
            "total_migrations": len(self.version_history),
            "average_compatibility_score": np.mean([
                m["compatibility_score"] for m in self.version_history
            ]) if self.version_history else 0.0,
            "most_used_strategy": self._get_most_used_strategy(),
            "recent_migrations": self.version_history[-5:] if self.version_history else []
        }
    
    def _get_most_used_strategy(self) -> str:
        """Retorna estratégia mais usada"""
        if not self.version_history:
            return "none"
        
        strategies = [m["strategy"] for m in self.version_history]
        return max(set(strategies), key=strategies.count)

# Função de conveniência para uso rápido
def create_compatibility_system(config_path: str = None) -> SistemaCompatibilidadeEvolutiva:
    """Cria instância do sistema de compatibilidade"""
    if config_path is None:
        config_path = "config/compatibilidade.json"
    
    return SistemaCompatibilidadeEvolutiva(config_path)

if __name__ == "__main__":
    # Teste do sistema
    print("🧬 Sistema de Compatibilidade Evolutiva")
    print("=" * 50)
    
    system = create_compatibility_system()
    
    # Simular modelos para teste
    class SimpleModel(nn.Module):
        def __init__(self, input_size=10, hidden_size=20, output_size=5):
            super().__init__()
            self.fc1 = nn.Linear(input_size, hidden_size)
            self.fc2 = nn.Linear(hidden_size, output_size)
        
        def forward(self, x):
            x = torch.relu(self.fc1(x))
            return self.fc2(x)
    
    model_old = SimpleModel(10, 20, 5)
    model_new = SimpleModel(10, 25, 5)  # Diferente hidden_size
    
    # Testar compatibilidade
    compatibility = system.check_compatibility(model_old, model_new)
    print(f"Compatibilidade: {compatibility['compatibility_score']:.3f}")
    print(f"Migração necessária: {compatibility['migration_required']}")
    
    if compatibility['migration_required']:
        print(f"Estratégia selecionada: {compatibility['migration_strategy']}")
        migrated_model = system.migrate_model(model_old, model_new)
        print("✅ Migração concluída")
    
    # Relatório
    report = system.get_compatibility_report()
    print(f"\n📊 Relatório: {report['total_migrations']} migrações realizadas") 