"""
Módulo de Evolução para Orquestração Biomimética
Nível 1: Evolução básica com registro de histórico, otimização de decisões e dashboard

Integração com sistema principal:
    from .orchestration_evolution import OrchestrationEvolutionEngine
    
    class AutoEvolvingAISystem:
        def __init__(self):
            self.orchestration_evolution = OrchestrationEvolutionEngine()
        
        def recommend_provider(self, task_data):
            recommendation = ...  # decisão original
            # Registrar para aprendizado
            self.orchestration_evolution.record_recommendation(task_data, recommendation)
            return recommendation
        
        def record_task_result(self, task_data, result):
            # Registrar resultado para evolução
            self.orchestration_evolution.record_result(task_data, result)
            # Evoluir periodicamente
            self.orchestration_evolution.evolve_if_needed()
"""

import json
import math
import statistics
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import time
from datetime import datetime
import logging
import random

# Fallback para statistics se não disponível
try:
    from statistics import mean
    has_statistics = True
except ImportError:
    has_statistics = False
    # Implementação simples de mean
    def mean(values):
        if not values:
            return 0.0
        return sum(values) / len(values)

logger = logging.getLogger(__name__)

class TaskHistoryRecord:
    """Registro de execução de tarefa para aprendizado evolutivo"""
    
    def __init__(self, task_data: Dict, recommendation: Dict, result: Dict):
        self.task_data = task_data
        self.recommendation = recommendation
        self.result = result
        self.timestamp = time.time()
        self.metrics = self._calculate_metrics()
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calcular métricas de performance a partir do resultado"""
        metrics = {
            "success": self.result.get("success", False),
            "latency_ms": self.result.get("latency_ms", 0),
            "quality_score": self.result.get("quality_score", 0.5),
            "cost_usd": self.result.get("cost_usd", 0.0),
            "user_feedback": self.result.get("user_feedback", None),
            "confidence": self.recommendation.get("confidence", 0.5)
        }
        
        # Calcular score composto
        metrics["composite_score"] = self._calculate_composite_score(metrics)
        return metrics
    
    def _calculate_composite_score(self, metrics: Dict) -> float:
        """Calcular score composto considerando múltiplas dimensões"""
        weights = {
            "success": 0.4,
            "quality_score": 0.3,
            "latency_normalized": 0.15,
            "cost_normalized": 0.15
        }
        
        # Normalizar latência (inverter: menor latência = maior score)
        latency_score = 1.0 - min(metrics["latency_ms"] / 5000, 1.0) if metrics["latency_ms"] > 0 else 0.5
        
        # Normalizar custo (inverter: menor custo = maior score)
        cost_score = 1.0 - min(metrics["cost_usd"] / 0.1, 1.0) if metrics["cost_usd"] > 0 else 0.5
        
        score = (
            weights["success"] * float(metrics["success"]) +
            weights["quality_score"] * metrics["quality_score"] +
            weights["latency_normalized"] * latency_score +
            weights["cost_normalized"] * cost_score
        )
        
        return score

class OrchestrationEvolutionEngine:
    """
    Motor de evolução para orquestração biomimética.
    
    Funcionalidades:
    1. Registro de histórico de tarefas
    2. Atualização de perfis de provedores com média móvel exponencial
    3. Otimização da matriz de decisão baseada em taxas de sucesso
    4. Dashboard de métricas e sugestões de melhoria
    5. Evolução automática a cada N tarefas
    6. Sistema de feedback humano integrado
    """
    
    def __init__(self, history_size: int = 1000, evolution_interval: int = 100):
        self.task_history = deque(maxlen=history_size)
        self.provider_profiles = self._initialize_provider_profiles()
        self.decision_matrix = self._initialize_decision_matrix()
        self.generation = 0
        self.evolution_history = []
        self.evolution_interval = evolution_interval
        self.last_evolution_size = 0
        
        # Sistema de feedback humano
        self.user_feedback_history = []
        self.feedback_weights = {
            "explicit_feedback": 0.7,    # Nota 1-5 do usuário
            "implicit_feedback": 0.3     # Comportamento implícito (retry, cancelamento, etc.)
        }
        
        logger.info(f"🧬 OrchestrationEvolutionEngine inicializado (histórico: {history_size}, evolução a cada {evolution_interval} tarefas)")
    
    def _initialize_provider_profiles(self) -> Dict[str, Dict]:
        """Inicializar perfis de provedores com valores padrão"""
        return {
            "openai": {
                "success_rate": 0.8,
                "avg_latency_ms": 300,
                "avg_quality": 0.85,
                "avg_cost_usd": 0.00002,
                "task_count": 0,
                "strengths": ["text_completion", "code_generation", "creativity"],
                "last_updated": datetime.now().isoformat()
            },
            "anthropic": {
                "success_rate": 0.85,
                "avg_latency_ms": 500,
                "avg_quality": 0.88,
                "avg_cost_usd": 0.000025,
                "task_count": 0,
                "strengths": ["reasoning", "long_context", "safety"],
                "last_updated": datetime.now().isoformat()
            },
            "google": {
                "success_rate": 0.75,
                "avg_latency_ms": 250,
                "avg_quality": 0.82,
                "avg_cost_usd": 0.000015,
                "task_count": 0,
                "strengths": ["translation", "summarization", "multimodal"],
                "last_updated": datetime.now().isoformat()
            },
            "huggingface": {
                "success_rate": 0.7,
                "avg_latency_ms": 1000,
                "avg_quality": 0.75,
                "avg_cost_usd": 0.000005,
                "task_count": 0,
                "strengths": ["text_classification", "ner", "custom_models"],
                "last_updated": datetime.now().isoformat()
            },
            "local": {
                "success_rate": 0.6,
                "avg_latency_ms": 50,
                "avg_quality": 0.65,
                "avg_cost_usd": 0.0,
                "task_count": 0,
                "strengths": ["privacy", "zero_latency", "offline"],
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _initialize_decision_matrix(self) -> Dict[Tuple, Dict]:
        """Inicializar matriz de decisão com combinações preferenciais"""
        matrix = {}
        
        # Combinações baseadas em heurística inicial
        combinations = [
            (("text_completion", "balanced"), "openai"),
            (("text_completion", "high_quality"), "anthropic"),
            (("text_completion", "low_cost"), "huggingface"),
            (("code_generation", "balanced"), "openai"),
            (("code_generation", "high_quality"), "openai"),
            (("text_classification", "balanced"), "huggingface"),
            (("text_classification", "low_cost"), "huggingface"),
            (("translation", "balanced"), "google"),
            (("translation", "fast"), "openai"),
            (("ner", "balanced"), "huggingface"),
            (("summarization", "balanced"), "google"),
            (("summarization", "high_quality"), "anthropic"),
        ]
        
        for (task_type, criterion), provider in combinations:
            matrix[(task_type, criterion, provider)] = {
                "preferred": True,
                "success_rate": 0.8,
                "usage_count": 0,
                "last_updated": datetime.now().isoformat()
            }
        
        return matrix
    
    def record_recommendation(self, task_data: Dict, recommendation: Dict):
        """Registrar uma recomendação (antes da execução)"""
        self.current_task_data = task_data
        self.current_recommendation = recommendation
    
    def record_result(self, task_data: Dict, result: Dict):
        """
        Registrar resultado de uma tarefa executada.
        
        Args:
            task_data: Dados da tarefa original
            result: Resultado da execução incluindo métricas
        """
        if hasattr(self, 'current_task_data') and hasattr(self, 'current_recommendation'):
            record = TaskHistoryRecord(
                task_data=self.current_task_data,
                recommendation=self.current_recommendation,
                result=result
            )
            self.task_history.append(record)
            
            # Limpar variáveis temporárias
            delattr(self, 'current_task_data')
            delattr(self, 'current_recommendation')
            
            # Verificar se precisa evoluir
            if len(self.task_history) % self.evolution_interval == 0:
                self.evolve()
            
            logger.debug(f"📝 Resultado registrado: {record.metrics['composite_score']:.2f}")
        else:
            logger.warning("Tentativa de registrar resultado sem recomendação prévia")
    
    def add_user_feedback(self, task_id: str, rating: int, comments: str = ""):
        """
        Adicionar feedback explícito do usuário (nota 1-5).
        
        Args:
            task_id: Identificador da tarefa (ou hash)
            rating: Nota de 1 a 5
            comments: Comentários opcionais
        """
        feedback = {
            "task_id": task_id,
            "rating": max(1, min(5, rating)),
            "comments": comments,
            "timestamp": datetime.now().isoformat()
        }
        
        self.user_feedback_history.append(feedback)
        
        # Atualizar pesos de feedback baseado na consistência
        self._update_feedback_weights()
        
        logger.info(f"⭐ Feedback do usuário registrado: {rating}/5")
    
    def evolve(self):
        """Executar um ciclo de evolução"""
        if len(self.task_history) <= self.last_evolution_size:
            logger.info("Sem tarefas novas suficientes para evolução")
            return
        
        self.generation += 1
        logger.info(f"🔄 Evolução geração {self.generation} com {len(self.task_history)} tarefas")
        
        # 1. Atualizar perfis de provedores baseado em performance real
        self._update_provider_profiles()
        
        # 2. Otimizar matriz de decisão baseado em taxas de sucesso
        self._optimize_decision_matrix()
        
        # 3. Ajustar heurísticas baseado em feedback humano
        self._adjust_heuristics_from_feedback()
        
        # 4. Registrar estatísticas da evolução
        stats = self._calculate_evolution_stats()
        self.evolution_history.append(stats)
        self.last_evolution_size = len(self.task_history)
        
        logger.info(f"✅ Evolução completa. Melhor taxa de sucesso: {stats.get('best_success_rate', 0):.2%}")
        return stats
    
    def _update_provider_profiles(self):
        """Atualizar perfis de provedores com média móvel exponencial"""
        if not self.task_history:
            return
        
        # Agrupar registros por provedor
        provider_records = {}
        for record in self.task_history:
            provider = record.recommendation.get("provider")
            if provider:
                provider_records.setdefault(provider, []).append(record)
        
        # Atualizar cada provedor
        for provider, records in provider_records.items():
            if provider not in self.provider_profiles:
                # Adicionar novo provedor descoberto
                self.provider_profiles[provider] = {
                    "success_rate": 0.5,
                    "avg_latency_ms": 1000,
                    "avg_quality": 0.5,
                    "avg_cost_usd": 0.001,
                    "task_count": 0,
                    "strengths": [],
                    "last_updated": datetime.now().isoformat()
                }
            
            # Calcular métricas atuais
            success_rate = mean([r.metrics["success"] for r in records])
            avg_latency = mean([r.metrics["latency_ms"] for r in records])
            avg_quality = mean([r.metrics["quality_score"] for r in records])
            avg_cost = mean([r.metrics["cost_usd"] for r in records])
            
            # Atualizar com média móvel exponencial
            profile = self.provider_profiles[provider]
            alpha = 0.1  # Taxa de aprendizado
            
            profile["success_rate"] = (1 - alpha) * profile["success_rate"] + alpha * success_rate
            profile["avg_latency_ms"] = (1 - alpha) * profile["avg_latency_ms"] + alpha * avg_latency
            profile["avg_quality"] = (1 - alpha) * profile["avg_quality"] + alpha * avg_quality
            profile["avg_cost_usd"] = (1 - alpha) * profile["avg_cost_usd"] + alpha * avg_cost
            profile["task_count"] = len(records)
            profile["last_updated"] = datetime.now().isoformat()
    
    def _optimize_decision_matrix(self):
        """Otimizar matriz de decisão baseado em sucesso histórico"""
        if not self.task_history:
            return
        
        # Analisar padrões de sucesso por (tipo_tarefa, critério, provedor)
        success_patterns = {}
        
        for record in self.task_history:
            task_type = record.task_data.get("task_type", "unknown")
            criterion = record.task_data.get("context", {}).get("primary_criterion", "balanced")
            provider = record.recommendation.get("provider", "unknown")
            
            key = (task_type, criterion, provider)
            success_patterns.setdefault(key, []).append(record.metrics["success"])
        
        # Calcular taxas de sucesso
        success_rates = {}
        for key, successes in success_patterns.items():
            success_rates[key] = mean(successes)
        
        # Atualizar matriz de decisão
        for key, rate in success_rates.items():
            if rate > 0.8:  # Excelente performance
                self.decision_matrix[key] = {
                    "preferred": True,
                    "success_rate": rate,
                    "usage_count": len(success_patterns[key]),
                    "last_updated": datetime.now().isoformat()
                }
            elif rate > 0.6:  # Performance aceitável
                if key in self.decision_matrix:
                    self.decision_matrix[key]["success_rate"] = rate
                    self.decision_matrix[key]["usage_count"] = len(success_patterns[key])
                    self.decision_matrix[key]["last_updated"] = datetime.now().isoformat()
            else:  # Performance ruim
                if key in self.decision_matrix:
                    # Marcar como não preferido
                    self.decision_matrix[key]["preferred"] = False
                    self.decision_matrix[key]["success_rate"] = rate
                    self.decision_matrix[key]["last_updated"] = datetime.now().isoformat()
        
        # Remover combinações muito antigas sem uso
        current_time = time.time()
        old_keys = []
        for key, data in self.decision_matrix.items():
            last_updated = datetime.fromisoformat(data["last_updated"]).timestamp()
            if (current_time - last_updated) > 30 * 24 * 3600:  # 30 dias
                old_keys.append(key)
        
        for key in old_keys:
            del self.decision_matrix[key]
    
    def _adjust_heuristics_from_feedback(self):
        """Ajustar heurísticas baseado em feedback humano"""
        if not self.user_feedback_history:
            return
        
        # Analisar feedback recente
        recent_feedback = list(self.user_feedback_history)[-20:]  # Últimos 20 feedbacks
        
        if not recent_feedback:
            return
        
        avg_rating = mean([fb["rating"] for fb in recent_feedback])
        
        # Ajustar pesos baseado na satisfação do usuário
        if avg_rating < 3.0:  # Insatisfeito
            # Dar mais peso ao feedback explícito
            self.feedback_weights["explicit_feedback"] = min(0.9, self.feedback_weights["explicit_feedback"] + 0.1)
            self.feedback_weights["implicit_feedback"] = 1.0 - self.feedback_weights["explicit_feedback"]
        elif avg_rating > 4.0:  # Muito satisfeito
            # Balancear pesos
            self.feedback_weights["explicit_feedback"] = 0.5
            self.feedback_weights["implicit_feedback"] = 0.5
    
    def _update_feedback_weights(self):
        """Atualizar pesos de feedback baseado na consistência"""
        # Implementação simples: pesos fixos por enquanto
        # Em versões futuras, ajustar baseado na correlação entre feedback e métricas objetivas
        pass
    
    def _calculate_evolution_stats(self) -> Dict[str, Any]:
        """Calcular estatísticas para este ciclo de evolução"""
        if not self.task_history:
            return {}
        
        # Usar tarefas desde a última evolução
        recent_start = max(0, self.last_evolution_size)
        recent_records = list(self.task_history)[recent_start:]
        
        if not recent_records:
            return {}
        
        stats = {
            "generation": self.generation,
            "total_tasks": len(self.task_history),
            "new_tasks_since_last_evolution": len(recent_records),
            "success_rate": mean([r.metrics["success"] for r in recent_records]),
            "avg_composite_score": mean([r.metrics["composite_score"] for r in recent_records]),
            "avg_latency_ms": mean([r.metrics["latency_ms"] for r in recent_records]),
            "avg_quality": mean([r.metrics["quality_score"] for r in recent_records]),
            "avg_cost_usd": mean([r.metrics["cost_usd"] for r in recent_records]),
            "provider_distribution": {},
            "top_performing_combinations": [],
            "user_feedback_summary": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Distribuição por provedor
        for record in recent_records:
            provider = record.recommendation.get("provider", "unknown")
            stats["provider_distribution"][provider] = stats["provider_distribution"].get(provider, 0) + 1
        
        # Combinações de melhor performance
        combination_scores = {}
        for record in recent_records:
            task_type = record.task_data.get("task_type", "unknown")
            criterion = record.task_data.get("context", {}).get("primary_criterion", "balanced")
            provider = record.recommendation.get("provider", "unknown")
            
            key = f"{task_type}:{criterion}:{provider}"
            combination_scores.setdefault(key, []).append(record.metrics["composite_score"])
        
        avg_scores = {k: mean(v) for k, v in combination_scores.items()}
        top_combinations = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        stats["top_performing_combinations"] = [
            {"combination": k, "avg_score": v} for k, v in top_combinations
        ]
        
        # Resumo de feedback do usuário
        if self.user_feedback_history:
            recent_feedback = list(self.user_feedback_history)[-10:]
            stats["user_feedback_summary"] = {
                "count": len(recent_feedback),
                "avg_rating": mean([fb["rating"] for fb in recent_feedback]),
                "last_feedback": recent_feedback[-1] if recent_feedback else None
            }
        
        return stats
    
    def get_recommendation_improvements(self) -> List[Dict[str, Any]]:
        """Obter sugestões de melhoria para o sistema de recomendação"""
        improvements = []
        
        # Sugerir baseado em provedores com baixa performance
        for provider, profile in self.provider_profiles.items():
            if profile["task_count"] > 10 and profile["success_rate"] < 0.6:
                improvements.append({
                    "type": "provider_warning",
                    "provider": provider,
                    "success_rate": profile["success_rate"],
                    "suggestion": f"Reduzir uso de {provider} para tarefas críticas. Performance abaixo do esperado.",
                    "severity": "high"
                })
        
        # Sugerir baseado em ineficiências de custo
        for provider, profile in self.provider_profiles.items():
            if profile["avg_cost_usd"] > 0.01 and profile["avg_quality"] < 0.7:
                cost_per_quality = profile["avg_cost_usd"] / max(profile["avg_quality"], 0.01)
                improvements.append({
                    "type": "cost_efficiency",
                    "provider": provider,
                    "cost_per_quality": cost_per_quality,
                    "suggestion": f"{provider} tem custo alto para qualidade baixa. Considerar alternativas.",
                    "severity": "medium"
                })
        
        # Sugerir baseado em combinações subutilizadas mas de alta performance
        for (task_type, criterion, provider), data in self.decision_matrix.items():
            if data["preferred"] and data["usage_count"] < 5 and data["success_rate"] > 0.9:
                improvements.append({
                    "type": "underutilized_gem",
                    "combination": f"{task_type}/{criterion}/{provider}",
                    "success_rate": data["success_rate"],
                    "usage_count": data["usage_count"],
                    "suggestion": f"A combinação {task_type}/{criterion}/{provider} tem excelente performance mas é pouco utilizada.",
                    "severity": "low"
                })
        
        return improvements
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados completos para dashboard"""
        return {
            "evolution_history": self.evolution_history[-20:],  # Últimas 20 gerações
            "provider_profiles": self.provider_profiles,
            "decision_matrix_summary": {
                "total_combinations": len(self.decision_matrix),
                "preferred_combinations": sum(1 for d in self.decision_matrix.values() if d["preferred"]),
                "avg_success_rate": mean([d["success_rate"] for d in self.decision_matrix.values()])
            },
            "current_stats": self._calculate_evolution_stats() if self.task_history else {},
            "improvement_suggestions": self.get_recommendation_improvements(),
            "system_status": {
                "generation": self.generation,
                "total_tasks": len(self.task_history),
                "user_feedbacks": len(self.user_feedback_history),
                "last_evolution": self.evolution_history[-1] if self.evolution_history else None
            }
        }
    
    def evolve_if_needed(self):
        """Evoluir se atingiu o intervalo necessário"""
        if len(self.task_history) >= self.last_evolution_size + self.evolution_interval:
            self.evolve()
    
    def _dict_tuple_keys_to_strings(self, d: Dict) -> Dict:
        """Converter chaves tupla em strings para serialização JSON"""
        result = {}
        for key, value in d.items():
            if isinstance(key, tuple):
                # Converter tupla para string no formato "(a, b, c)"
                str_key = str(key)
            else:
                str_key = key
            # Recursivamente processar dicionários aninhados
            if isinstance(value, dict):
                value = self._dict_tuple_keys_to_strings(value)
            result[str_key] = value
        return result
    
    def _dict_string_keys_to_tuples(self, d: Dict) -> Dict:
        """Converter strings de volta para tuplas quando apropriado"""
        result = {}
        for key, value in d.items():
            # Tentar converter string no formato "(a, b, c)" de volta para tupla
            if isinstance(key, str) and key.startswith("(") and key.endswith(")"):
                try:
                    # Converter string de tupla de volta para tupla
                    # Exemplo: "('text_completion', 'balanced', 'openai')" -> tuple
                    import ast
                    tuple_key = ast.literal_eval(key)
                    if isinstance(tuple_key, tuple):
                        key = tuple_key
                except:
                    pass  # Manter como string se falhar
            
            if isinstance(value, dict):
                value = self._dict_string_keys_to_tuples(value)
            result[key] = value
        return result
    
    def save_state(self, filepath: str):
        """Salvar estado do motor de evolução"""
        # Converter dicionários com chaves tupla para strings
        provider_profiles_serializable = self._dict_tuple_keys_to_strings(self.provider_profiles)
        decision_matrix_serializable = self._dict_tuple_keys_to_strings(self.decision_matrix)
        
        state = {
            "task_history": [
                {
                    "task_data": record.task_data,
                    "recommendation": record.recommendation,
                    "result": record.result,
                    "timestamp": record.timestamp,
                    "metrics": record.metrics
                }
                for record in self.task_history
            ],
            "provider_profiles": provider_profiles_serializable,
            "decision_matrix": decision_matrix_serializable,
            "generation": self.generation,
            "evolution_history": self.evolution_history,
            "user_feedback_history": self.user_feedback_history,
            "last_evolution_size": self.last_evolution_size
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        logger.info(f"💾 Estado salvo em {filepath}")
    
    def load_state(self, filepath: str):
        """Carregar estado do motor de evolução"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Carregar histórico de tarefas
            self.task_history.clear()
            for record_data in state.get("task_history", []):
                # Criar objeto TaskHistoryRecord
                record = TaskHistoryRecord(
                    task_data=record_data["task_data"],
                    recommendation=record_data["recommendation"],
                    result=record_data["result"]
                )
                record.timestamp = record_data["timestamp"]
                record.metrics = record_data["metrics"]
                self.task_history.append(record)
            
            # Carregar outros dados, convertendo strings de volta para tuplas
            provider_profiles = state.get("provider_profiles", self._initialize_provider_profiles())
            decision_matrix = state.get("decision_matrix", self._initialize_decision_matrix())
            
            self.provider_profiles = self._dict_string_keys_to_tuples(provider_profiles)
            self.decision_matrix = self._dict_string_keys_to_tuples(decision_matrix)
            
            self.generation = state.get("generation", 0)
            self.evolution_history = state.get("evolution_history", [])
            self.user_feedback_history = state.get("user_feedback_history", [])
            self.last_evolution_size = state.get("last_evolution_size", 0)
            
            logger.info(f"📂 Estado carregado de {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            return False


# Demonstração simples
if __name__ == "__main__":
    print("🧪 Demonstração do OrchestrationEvolutionEngine")
    
    engine = OrchestrationEvolutionEngine(history_size=50, evolution_interval=20)
    
    # Simular algumas tarefas
    for i in range(60):
        task_type = random.choice(["text_completion", "text_classification", "code_generation", "translation"])
        criterion = random.choice(["balanced", "high_quality", "low_cost", "fast"])
        
        task_data = {
            "task_type": task_type,
            "text_length": random.randint(10, 1000),
            "context": {"primary_criterion": criterion, "budget": "balanced"}
        }
        
        # Recomendação baseada em heurística
        provider_map = {
            "text_completion": "openai",
            "text_classification": "huggingface", 
            "code_generation": "openai",
            "translation": "google"
        }
        
        recommendation = {
            "provider": provider_map.get(task_type, "openai"),
            "parameters": {"temperature": 0.7, "max_tokens": 100},
            "confidence": random.uniform(0.5, 0.9),
            "reasoning": f"Heurística básica para {task_type}"
        }
        
        # Registrar recomendação
        engine.record_recommendation(task_data, recommendation)
        
        # Simular resultado
        result = {
            "success": random.random() > 0.2,  # 80% sucesso
            "latency_ms": random.randint(100, 2000),
            "quality_score": random.uniform(0.5, 1.0),
            "cost_usd": random.uniform(0.0001, 0.01),
            "user_feedback": None
        }
        
        # Registrar resultado
        engine.record_result(task_data, result)
        
        # Adicionar feedback ocasional
        if i % 10 == 0:
            engine.add_user_feedback(f"task_{i}", random.randint(1, 5), "Comentário de teste")
    
    # Mostrar dados do dashboard
    print("\n📊 Dashboard Data:")
    dashboard = engine.get_dashboard_data()
    print(f"Geração: {dashboard['system_status']['generation']}")
    print(f"Total tarefas: {dashboard['system_status']['total_tasks']}")
    print(f"Taxa de sucesso recente: {dashboard['current_stats'].get('success_rate', 0):.2%}")
    
    print("\n💡 Sugestões de melhoria:")
    for imp in dashboard['improvement_suggestions'][:3]:
        print(f"  - [{imp['severity'].upper()}] {imp['suggestion']}")
    
    print("\n✅ Demonstração concluída. Motor pronto para integração.")