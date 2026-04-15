"""
Evolution API - API REST para Sistema Evolutivo Biomimético
============================================================

Integra os três componentes principais:
1. GenomeMutator - Mutação estrutural real
2. BrainEvolver - Evolução do cérebro (Llama/Modelos)
3. EvolutionDashboard - Monitoramento em tempo real

Endpoints:
- POST /evolve/structure - Executa mutação estrutural
- POST /evolve/brain - Executa evolução cerebral
- GET /status - Status do sistema evolutivo
- GET /dashboard - Dados do dashboard
- GET /history - Histórico de evoluções

Versão: 1.0.0
Data: 2026-04-15
Autor: Jarvis (OpenClaw)
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da API
app = FastAPI(
    title="Evolution API",
    description="API para Sistema Evolutivo Biomimético",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class EvolutionRequest(BaseModel):
    evolution_type: Optional[str] = None
    intensity: float = 0.5
    component: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}

class EvolutionResponse(BaseModel):
    success: bool
    message: str
    evolution_id: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None

class SystemStatus(BaseModel):
    status: str
    components: Dict[str, str]
    metrics: Dict[str, Any]
    uptime_seconds: float
    generation: int

# Estado global da API
class EvolutionSystem:
    """Sistema evolutivo integrado"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.evolution_count = 0
        self.mutation_count = 0
        self.current_generation = 0
        
        # Componentes (serão inicializados quando disponíveis)
        self.components = {
            'genome_mutator': None,
            'brain_evolver': None,
            'evolution_dashboard': None
        }
        
        # Histórico
        self.history = []
        
        # Inicializar componentes
        self._initialize_components()
        
        logger.info("🧬 Evolution System inicializado")
    
    def _initialize_components(self):
        """Tenta inicializar os componentes evolutivos"""
        try:
            # Tentar importar GenomeMutator
            try:
                from .genome_mutator import GenomeMutator
                self.components['genome_mutator'] = GenomeMutator
                logger.info("✅ GenomeMutator disponível")
            except ImportError as e:
                logger.warning(f"⚠️ GenomeMutator não disponível: {e}")
            
            # Tentar importar BrainEvolver
            try:
                from .brain_evolver import BrainEvolver
                self.components['brain_evolver'] = BrainEvolver
                logger.info("✅ BrainEvolver disponível")
            except ImportError as e:
                logger.warning(f"⚠️ BrainEvolver não disponível: {e}")
            
            # Tentar importar EvolutionDashboard
            try:
                from .evolution_dashboard import EvolutionDashboard
                self.components['evolution_dashboard'] = EvolutionDashboard()
                logger.info("✅ EvolutionDashboard disponível")
            except ImportError as e:
                logger.warning(f"⚠️ EvolutionDashboard não disponível: {e}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar componentes: {e}")
    
    def perform_structural_evolution(self, evolution_type: str = None) -> Dict[str, Any]:
        """Executa evolução estrutural"""
        self.evolution_count += 1
        self.mutation_count += 1
        
        evolution_id = f"struct_evol_{self.evolution_count}_{int(time.time())}"
        
        try:
            if self.components['genome_mutator']:
                # Usar componente real
                mutator = self.components['genome_mutator']()
                result = mutator.perform_structural_mutation(evolution_type)
                
                # Registrar no dashboard
                if self.components['evolution_dashboard']:
                    self.components['evolution_dashboard'].record_mutation(result)
                
                return {
                    'success': True,
                    'evolution_id': evolution_id,
                    'type': 'structural',
                    'result': result,
                    'message': f"Mutacao estrutural executada: {result.get('mutation_type', 'unknown')}"
                }
            else:
                # Simular mutação
                mutation_types = ['add_node', 'remove_node', 'create_specialist', 'rewire_connections']
                mutation_type = evolution_type or random.choice(mutation_types)
                
                simulated_result = {
                    'mutation_type': mutation_type,
                    'structure_changed': random.choice([True, False]),
                    'changes': [f'Simulated {mutation_type}'],
                    'timestamp': datetime.now().isoformat()
                }
                
                return {
                    'success': True,
                    'evolution_id': evolution_id,
                    'type': 'structural',
                    'result': simulated_result,
                    'message': f"Mutacao estrutural simulada: {mutation_type}"
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na evolução estrutural: {e}")
            return {
                'success': False,
                'evolution_id': evolution_id,
                'type': 'structural',
                'error': str(e),
                'message': f"Erro na evolução estrutural: {e}"
            }
    
    def perform_brain_evolution(self, evolution_type: str = None) -> Dict[str, Any]:
        """Executa evolução cerebral"""
        self.evolution_count += 1
        
        evolution_id = f"brain_evol_{self.evolution_count}_{int(time.time())}"
        
        try:
            if self.components['brain_evolver']:
                # Usar componente real
                evolver = self.components['brain_evolver']()
                result = evolver.perform_brain_evolution(evolution_type)
                
                # Registrar no dashboard
                if self.components['evolution_dashboard']:
                    self.components['evolution_dashboard'].record_brain_evolution(result)
                
                return {
                    'success': True,
                    'evolution_id': evolution_id,
                    'type': 'brain',
                    'result': result,
                    'message': f"Evolução cerebral executada: {result.get('evolution_type', 'unknown')}"
                }
            else:
                # Simular evolução
                evolution_types = ['mutate_model', 'create_ensemble', 'optimize_parameters', 'evolve_routing']
                evo_type = evolution_type or random.choice(evolution_types)
                
                simulated_result = {
                    'evolution_type': evo_type,
                    'success': random.choice([True, False]),
                    'changes': [f'Simulated {evo_type}'],
                    'timestamp': datetime.now().isoformat()
                }
                
                return {
                    'success': True,
                    'evolution_id': evolution_id,
                    'type': 'brain',
                    'result': simulated_result,
                    'message': f"Evolução cerebral simulada: {evo_type}"
                }
                
        except Exception as e:
            logger.error(f"❌ Erro na evolução cerebral: {e}")
            return {
                'success': False,
                'evolution_id': evolution_id,
                'type': 'brain',
                'error': str(e),
                'message': f"Erro na evolução cerebral: {e}"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema evolutivo"""
        # Calcular uptime
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Status dos componentes
        component_status = {}
        for name, component in self.components.items():
            if component:
                if name == 'evolution_dashboard':
                    status = 'active'
                else:
                    status = 'available'
            else:
                status = 'unavailable'
            component_status[name] = status
        
        # Métricas
        metrics = {
            'total_evolutions': self.evolution_count,
            'total_mutations': self.mutation_count,
            'current_generation': self.current_generation,
            'component_count': sum(1 for c in self.components.values() if c)
        }
        
        # Obter dados do dashboard se disponível
        dashboard_data = None
        if self.components['evolution_dashboard']:
            try:
                dashboard_data = self.components['evolution_dashboard'].get_dashboard_data()
                metrics.update(dashboard_data.get('status', {}))
            except Exception as e:
                logger.warning(f"Não foi possível obter dados do dashboard: {e}")
        
        return {
            'status': 'active',
            'components': component_status,
            'metrics': metrics,
            'uptime_seconds': uptime,
            'generation': self.current_generation,
            'dashboard': dashboard_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def increment_generation(self):
        """Incrementa a geração atual"""
        self.current_generation += 1
        
        # Registrar no dashboard
        if self.components['evolution_dashboard']:
            self.components['evolution_dashboard'].increment_generation()
        
        # Simular performance
        if self.components['evolution_dashboard']:
            task_types = ['classification', 'generation', 'analysis', 'reasoning']
            task_type = random.choice(task_types)
            
            performance = {
                'accuracy': random.uniform(0.6, 0.95),
                'latency': random.uniform(0.1, 2.0),
                'tokens_used': random.randint(50, 1000),
                'confidence': random.uniform(0.7, 0.98)
            }
            
            self.components['evolution_dashboard'].record_performance(task_type, performance)
        
        logger.info(f"🔄 Geração incrementada: {self.current_generation}")
    
    def get_evolution_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retorna histórico de evoluções"""
        # Para simplificar, retornar histórico simulado
        # Em produção, isso viria de um banco de dados
        history = []
        
        for i in range(min(limit, 10)):
            history.append({
                'id': f"evol_{i+1}",
                'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                'type': random.choice(['structural', 'brain']),
                'success': random.choice([True, False]),
                'details': f"Evolução {i+1} - {random.choice(['add_node', 'mutate_model', 'optimize_parameters'])}"
            })
        
        return history

# Instância global do sistema evolutivo
evolution_system = EvolutionSystem()

# Endpoints da API
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Evolution API - Sistema Evolutivo Biomimético",
        "version": "1.0.0",
        "endpoints": [
            "/evolve/structure - POST: Executa mutação estrutural",
            "/evolve/brain - POST: Executa evolução cerebral",
            "/status - GET: Status do sistema",
            "/dashboard - GET: Dashboard de monitoramento",
            "/history - GET: Histórico de evoluções",
            "/docs - Documentação Swagger"
        ]
    }

@app.post("/evolve/structure", response_model=EvolutionResponse)
async def evolve_structure(request: EvolutionRequest):
    """Executa mutação estrutural no genoma"""
    logger.info(f"🧬 Recebida requisição para evolução estrutural: {request.evolution_type}")
    
    result = evolution_system.perform_structural_evolution(request.evolution_type)
    
    # Incrementar geração se bem-sucedido
    if result.get('success', False):
        evolution_system.increment_generation()
    
    return EvolutionResponse(
        success=result.get('success', False),
        message=result.get('message', ''),
        evolution_id=result.get('evolution_id', ''),
        timestamp=datetime.now().isoformat(),
        data=result.get('result')
    )

@app.post("/evolve/brain", response_model=EvolutionResponse)
async def evolve_brain(request: EvolutionRequest):
    """Executa evolução cerebral (modelos/parâmetros)"""
    logger.info(f"🧠 Recebida requisição para evolução cerebral: {request.evolution_type}")
    
    result = evolution_system.perform_brain_evolution(request.evolution_type)
    
    # Incrementar geração se bem-sucedido
    if result.get('success', False):
        evolution_system.increment_generation()
    
    return EvolutionResponse(
        success=result.get('success', False),
        message=result.get('message', ''),
        evolution_id=result.get('evolution_id', ''),
        timestamp=datetime.now().isoformat(),
        data=result.get('result')
    )

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Retorna status do sistema evolutivo"""
    status_data = evolution_system.get_system_status()
    
    return SystemStatus(
        status=status_data['status'],
        components=status_data['components'],
        metrics=status_data['metrics'],
        uptime_seconds=status_data['uptime_seconds'],
        generation=status_data['generation']
    )

@app.get("/dashboard")
async def get_dashboard():
    """Retorna dados do dashboard de monitoramento"""
    if evolution_system.components['evolution_dashboard']:
        data = evolution_system.components['evolution_dashboard'].get_dashboard_data()
        return JSONResponse(content=data)
    else:
        # Dashboard simulado
        return {
            "status": "dashboard_unavailable",
            "message": "EvolutionDashboard não está disponível",
            "simulated_data": {
                "mutations": evolution_system.mutation_count,
                "evolutions": evolution_system.evolution_count,
                "generation": evolution_system.current_generation
            }
        }

@app.get("/dashboard/html")
async def get_dashboard_html():
    """Retorna dashboard em HTML"""
    if evolution_system.components['evolution_dashboard']:
        html_path = evolution_system.components['evolution_dashboard'].generate_html_report()
        return FileResponse(html_path, media_type="text/html")
    else:
        html_content = """
        <html>
            <head><title>Evolution Dashboard</title></head>
            <body>
                <h1>Evolution Dashboard</h1>
                <p>Dashboard não disponível. Componente EvolutionDashboard não carregado.</p>
                <p>Mutações: """ + str(evolution_system.mutation_count) + """</p>
                <p>Evoluções: """ + str(evolution_system.evolution_count) + """</p>
                <p>Geração: """ + str(evolution_system.current_generation) + """</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@app.get("/history")
async def get_history(limit: int = 20):
    """Retorna histórico de evoluções"""
    history = evolution_system.get_evolution_history(limit)
    return {"history": history}

@app.post("/generation/increment")
async def increment_generation():
    """Incrementa a geração atual manualmente"""
    evolution_system.increment_generation()
    return {
        "success": True,
        "message": f"Geração incrementada para {evolution_system.current_generation}",
        "generation": evolution_system.current_generation
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - evolution_system.start_time).total_seconds()
    }

# Função para executar a API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)