"""
Módulo de IA Local como Cérebro Biomimético

Fornece implementações de cérebro biomimético usando IA local:
1. MockLocalBrain: Simulação sem dependências externas
2. OllamaBrain: Integração real com Ollama (se disponível)
3. HybridBiomimeticSystem: Sistema híbrido com fallback automático

Integração com sistema principal:
    from .local_brain import HybridBiomimeticSystem
    
    class AutoEvolvingAISystem:
        def __init__(self):
            self.local_brain = HybridBiomimeticSystem(brain_type="ollama")
        
        def recommend_provider(self, task_data):
            decision = asyncio.run(self.local_brain.recommend_provider(task_data))
            return decision
"""

import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class MockLocalBrain:
    """
    Cérebro biomimético simulado que toma decisões inteligentes.
    Simula uma IA local sem dependências externas.
    """
    
    def __init__(self, brain_name: str = "BioMind-Mock"):
        self.name = brain_name
        self.learning_history = []
        self.decision_patterns = {}
        logger.info(f"🧠 {self.name} inicializado (mock)")
    
    async def analyze_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa a tarefa e toma decisão biomimética.
        Simula raciocínio de IA local.
        """
        task_type = task_data.get("task_type", "text_completion")
        text_length = task_data.get("text_length", 0)
        context = task_data.get("context", {})
        
        logger.info(f"🧠 {self.name} analisando tarefa: {task_type}")
        
        # Simular processamento de IA local
        await asyncio.sleep(0.1)  # Simula inferência
        
        # Lógica de decisão simulada (mais sofisticada que heurística simples)
        decision = self._simulate_ai_reasoning(task_type, text_length, context)
        
        # Registrar para aprendizado
        self.learning_history.append({
            "task": task_data,
            "decision": decision,
            "timestamp": time.time()
        })
        
        return decision
    
    def _simulate_ai_reasoning(self, task_type: str, text_length: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simula raciocínio de IA local baseado em padrões aprendidos"""
        
        # Padrões de decisão (simulando conhecimento aprendido)
        patterns = {
            "text_completion": {
                "creative": {"provider": "openai", "temperature": 0.8, "strategy": "creative_flow"},
                "technical": {"provider": "anthropic", "temperature": 0.3, "strategy": "structured"},
                "quick": {"provider": "google", "temperature": 0.5, "strategy": "concise"}
            },
            "text_classification": {
                "simple": {"provider": "huggingface", "temperature": 0.1, "strategy": "few_shot"},
                "complex": {"provider": "anthropic", "temperature": 0.2, "strategy": "chain_of_thought"}
            },
            "code_generation": {
                "python": {"provider": "openai", "temperature": 0.4, "strategy": "syntax_aware"},
                "web": {"provider": "anthropic", "temperature": 0.3, "strategy": "component_based"}
            },
            "translation": {
                "standard": {"provider": "google", "temperature": 0.4, "strategy": "accurate"},
                "creative": {"provider": "openai", "temperature": 0.6, "strategy": "natural"}
            },
            "summarization": {
                "concise": {"provider": "google", "temperature": 0.3, "strategy": "extractive"},
                "detailed": {"provider": "anthropic", "temperature": 0.4, "strategy": "abstractive"}
            },
            "ner": {
                "standard": {"provider": "huggingface", "temperature": 0.1, "strategy": "entity_focused"},
                "contextual": {"provider": "anthropic", "temperature": 0.2, "strategy": "relation_aware"}
            }
        }
        
        # Determinar sub-tipo baseado em contexto
        budget = context.get("budget", "balanced")
        latency = context.get("latency", "standard")
        quality_req = context.get("quality", "balanced")
        
        # Escolher padrão baseado em contexto
        if task_type in patterns:
            subtype = self._determine_subtype(task_type, budget, latency, quality_req)
            base_decision = patterns[task_type].get(subtype, patterns[task_type][list(patterns[task_type].keys())[0]])
        else:
            base_decision = {"provider": "openai", "temperature": 0.7, "strategy": "default"}
        
        # Ajustar baseado em comprimento e complexidade
        length_factor = min(1.0, text_length / 5000)
        temperature_adjust = min(0.9, base_decision.get("temperature", 0.7) + length_factor * 0.2)
        
        # Calcular confiança baseada em múltiplos fatores
        confidence_factors = {
            "pattern_match": 0.8 if subtype != "default" else 0.5,
            "text_length": 1.0 - (length_factor * 0.3),
            "context_match": 0.9 if budget != "contradictory" else 0.6
        }
        confidence = np.mean(list(confidence_factors.values()))
        
        # Gerar explicação simulada (como se a IA estivesse "pensando")
        reasoning = (
            f"Como {self.name}, analisei: tarefa={task_type}, comprimento={text_length}, "
            f"contexto={context}. Padrão identificado: '{self._get_pattern_name(task_type, base_decision)}'. "
            f"Ajustei parâmetros para temperatura={temperature_adjust:.2f} considerando complexidade."
        )
        
        return {
            "provider": base_decision["provider"],
            "parameters": {
                "temperature": temperature_adjust,
                "max_tokens": min(1000, max(50, int(text_length * 1.5))),
                "top_p": 0.95,
                "frequency_penalty": 0.1 if text_length > 1000 else 0.0
            },
            "strategy": base_decision["strategy"],
            "confidence": float(confidence),
            "reasoning": reasoning,
            "brain_type": "mock",
            "metadata": {
                "pattern_used": self._get_pattern_name(task_type, base_decision),
                "subtype": subtype,
                "learning_phase": "initial"
            }
        }
    
    def _determine_subtype(self, task_type: str, budget: str, latency: str, quality: str) -> str:
        """Determina sub-tipo baseado em múltiplos fatores"""
        if task_type == "text_completion":
            if budget == "low":
                return "quick"
            elif quality == "high":
                return "technical"
            else:
                return "creative"
        elif task_type == "text_classification":
            return "complex" if quality == "high" else "simple"
        elif task_type == "code_generation":
            return "web" if "api" in quality else "python"
        elif task_type == "translation":
            return "creative" if quality == "high" else "standard"
        elif task_type == "summarization":
            return "detailed" if quality == "high" else "concise"
        elif task_type == "ner":
            return "contextual" if quality == "high" else "standard"
        return "default"
    
    def _get_pattern_name(self, task_type: str, decision: Dict[str, Any]) -> str:
        """Gera nome descritivo para o padrão usado"""
        strategy = decision.get("strategy", "default")
        provider = decision.get("provider", "unknown")
        return f"{task_type}_{provider}_{strategy}"
    
    def learn_from_feedback(self, task_data: Dict[str, Any], result: Dict[str, Any]):
        """Aprende com feedback da execução (simulação de meta-learning)"""
        feedback_entry = {
            "task": task_data,
            "result": result,
            "success": result.get("success", False),
            "quality_score": result.get("quality_score", 0.5),
            "timestamp": time.time()
        }
        
        self.learning_history.append(feedback_entry)
        
        # Simular ajuste de padrões baseado em feedback
        if len(self.learning_history) % 10 == 0:
            self._update_decision_patterns()
        
        logger.debug(f"🧠 {self.name} aprendendo com feedback (histórico: {len(self.learning_history)})")
    
    def _update_decision_patterns(self):
        """Simula atualização de padrões baseado em histórico"""
        # Em implementação real, usaria ML para ajustar pesos
        logger.info(f"🧠 {self.name} atualizando padrões de decisão (simulação)")

class OllamaBrain:
    """
    Cérebro biomimético usando Ollama real.
    Requer Ollama instalado e rodando em localhost:11434.
    """
    
    def __init__(self, model: str = "llama3:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.available = False
        self._check_availability()
    
    def _check_availability(self):
        """Verifica se Ollama está disponível"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self.available = response.status_code == 200
            if self.available:
                logger.info(f"✅ Ollama disponível com modelo: {self.model}")
            else:
                logger.warning("⚠️ Ollama não respondeu corretamente")
        except ImportError:
            logger.warning("⚠️ Biblioteca 'requests' não instalada. Ollama não disponível.")
            self.available = False
        except Exception as e:
            logger.warning(f"⚠️ Ollama não disponível: {e}")
            self.available = False
    
    async def analyze_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Usa Ollama real para analisar tarefa e tomar decisão.
        """
        if not self.available:
            logger.error("Ollama não disponível. Usando fallback mock.")
            fallback_brain = MockLocalBrain("Ollama-Fallback")
            return await fallback_brain.analyze_task(task_data)
        
        try:
            import requests
            import json as json_module
            
            # Preparar prompt para o modelo
            prompt = self._create_decision_prompt(task_data)
            
            # Chamar Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Baixa temperatura para decisões consistentes
                    "num_predict": 500
                }
            }
            
            logger.info(f"🧠 Consultando Ollama ({self.model}) para decisão...")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                decision_text = result.get("response", "").strip()
                
                # Parse da decisão (formato JSON esperado)
                decision = self._parse_ollama_response(decision_text, task_data)
                decision["brain_type"] = "ollama"
                decision["model_used"] = self.model
                
                logger.info(f"✅ Decisão do Ollama: {decision.get('provider', 'unknown')}")
                return decision
            else:
                logger.error(f"Erro Ollama: {response.status_code}")
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro ao consultar Ollama: {e}")
            fallback_brain = MockLocalBrain("Ollama-Error-Fallback")
            return await fallback_brain.analyze_task(task_data)
    
    def _create_decision_prompt(self, task_data: Dict[str, Any]) -> str:
        """Cria prompt estruturado para o modelo tomar decisão"""
        task_type = task_data.get("task_type", "text_completion")
        text_length = task_data.get("text_length", 0)
        context = task_data.get("context", {})
        
        prompt = f"""Você é um sistema biomimético de orquestração de IA. Sua tarefa é decidir qual provedor de IA usar e com quais parâmetros.

TAREFA:
- Tipo: {task_type}
- Comprimento do texto: {text_length} caracteres
- Contexto: {json.dumps(context, indent=2)}

PROVEDORES DISPONÍVEIS:
1. OpenAI: Bom para criatividade, geração de código, completamento geral
2. Anthropic: Bom para raciocínio, contexto longo, segurança
3. Google: Bom para tradução, baixa latência, multimodal
4. HuggingFace: Bom para classificação, NER, modelos especializados
5. Local: Zero custo, privacidade, personalização (mais lento)

PARÂMETROS IMPORTANTES:
- temperature: 0.0-1.0 (criatividade vs consistência)
- max_tokens: número de tokens a gerar
- strategy: abordagem de execução

SUA DECISÃO (responda APENAS em JSON válido):
{{
  "provider": "nome_do_provedor",
  "parameters": {{
    "temperature": 0.0-1.0,
    "max_tokens": número,
    "top_p": 0.95
  }},
  "strategy": "nome_da_estratégia",
  "confidence": 0.0-1.0,
  "reasoning": "explicação da sua decisão"
}}

Exemplo de estratégias: "creative_flow", "structured", "few_shot", "chain_of_thought", "syntax_aware", "concise"

RESPOSTA (APENAS JSON):"""
        
        return prompt
    
    def _parse_ollama_response(self, response_text: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parseia a resposta do Ollama para extrair decisão"""
        try:
            # Tentar extrair JSON da resposta
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                decision = json.loads(json_str)
            else:
                # Se não encontrar JSON, usar fallback
                raise ValueError("Resposta não contém JSON válido")
            
            # Validar campos obrigatórios
            required = ["provider", "parameters", "strategy", "confidence", "reasoning"]
            for field in required:
                if field not in decision:
                    decision[field] = self._get_fallback_value(field, task_data)
            
            return decision
            
        except Exception as e:
            logger.warning(f"Erro ao parsear resposta Ollama: {e}. Usando fallback.")
            # Retornar decisão mock básica
            return {
                "provider": "openai",
                "parameters": {"temperature": 0.7, "max_tokens": 200},
                "strategy": "default",
                "confidence": 0.5,
                "reasoning": f"Fallback devido a erro de parse: {e}",
                "error": str(e)
            }
    
    def _get_fallback_value(self, field: str, task_data: Dict[str, Any]) -> Any:
        """Valores fallback para campos faltantes"""
        if field == "provider":
            return "openai"
        elif field == "parameters":
            return {"temperature": 0.7, "max_tokens": 200}
        elif field == "strategy":
            return "default"
        elif field == "confidence":
            return 0.5
        elif field == "reasoning":
            return "Fallback: campo faltante na resposta"
        return None

class HybridBiomimeticSystem:
    """
    Sistema híbrido que combina IA local com heurística.
    Pode alternar entre mock, Ollama, ou outros backends.
    """
    
    def __init__(self, brain_type: str = "mock", **kwargs):
        self.brain_type = brain_type
        self.brain = self._initialize_brain(brain_type, kwargs)
        self.performance_stats = {}
        logger.info(f"🧬 Sistema biomimético híbrido inicializado (brain: {brain_type})")
    
    def _initialize_brain(self, brain_type: str, kwargs: Dict[str, Any]):
        """Inicializa o cérebro baseado no tipo"""
        if brain_type == "ollama":
            model = kwargs.get("model", "llama3:8b")
            base_url = kwargs.get("base_url", "http://localhost:11434")
            brain = OllamaBrain(model=model, base_url=base_url)
            if brain.available:
                return brain
            else:
                logger.warning("Ollama não disponível. Usando mock.")
                return MockLocalBrain("Hybrid-Fallback")
        elif brain_type == "mock":
            name = kwargs.get("name", "BioMind-Hybrid")
            return MockLocalBrain(name)
        else:
            logger.warning(f"Tipo de cérebro desconhecido: {brain_type}. Usando mock.")
            return MockLocalBrain("Default-Hybrid")
    
    async def recommend_provider(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Recomenda provedor usando cérebro biomimético"""
        decision = await self.brain.analyze_task(task_data)
        
        # Adicionar metadata do sistema híbrido
        decision["hybrid_metadata"] = {
            "brain_type": self.brain_type,
            "system_version": "2.0",
            "decision_timestamp": time.time()
        }
        
        return decision
    
    def record_task_result(self, task_data: Dict[str, Any], result: Dict[str, Any]):
        """Registra resultado para aprendizado"""
        if hasattr(self.brain, 'learn_from_feedback'):
            self.brain.learn_from_feedback(task_data, result)
        
        # Atualizar estatísticas
        task_type = task_data.get("task_type", "unknown")
        provider = result.get("provider", "unknown")
        
        key = f"{task_type}_{provider}"
        if key not in self.performance_stats:
            self.performance_stats[key] = {
                "total": 0,
                "successes": 0,
                "total_quality": 0.0
            }
        
        stats = self.performance_stats[key]
        stats["total"] += 1
        if result.get("success", False):
            stats["successes"] += 1
        stats["total_quality"] += result.get("quality_score", 0.5)
        
        logger.debug(f"📊 Estatísticas atualizadas: {key} = {stats['successes']}/{stats['total']}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance"""
        return self.performance_stats
    
    def get_learning_history_size(self) -> int:
        """Retorna tamanho do histórico de aprendizado"""
        if hasattr(self.brain, 'learning_history'):
            return len(self.brain.learning_history)
        return 0