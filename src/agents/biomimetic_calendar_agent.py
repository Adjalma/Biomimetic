#!/usr/bin/env python3
"""
Biomimetic Calendar Agent - Fase 6.2
Agente biomimético com percepção e ação no calendário do usuário

Integração com Google Calendar API para:
1. Percepção contextual da agenda
2. Agendamento inteligente baseado em lógica biomimética
3. Integração com sistema biomimético principal
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from google.google_calendar_client import GoogleCalendarClient
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ GoogleCalendarClient não disponível: {e}")
    GOOGLE_CALENDAR_AVAILABLE = False

try:
    from systems.sistemas.sistema_meta_learning_biomimetico import AutoEvolvingAISystem
    BIOMIMETIC_SYSTEM_AVAILABLE = True
except ImportError:
    print("⚠️ AutoEvolvingAISystem não disponível")
    BIOMIMETIC_SYSTEM_AVAILABLE = False

logger = logging.getLogger(__name__)


class BiomimeticCalendarAgent:
    """Agente biomimético com percepção de calendário"""
    
    def __init__(self, use_real_api: bool = True):
        """Inicializa agente de calendário
        
        Args:
            use_real_api: Se True, usa Google Calendar API real
                         Se False, modo simulado para desenvolvimento
        """
        self.use_real_api = use_real_api
        
        if use_real_api and GOOGLE_CALENDAR_AVAILABLE:
            try:
                credentials_path = os.path.join(
                    os.path.dirname(__file__), '..', '..', 'credentials.json'
                )
                self.calendar = GoogleCalendarClient(credentials_path=credentials_path)
                logger.info("✅ GoogleCalendarClient inicializado com sucesso")
            except Exception as e:
                logger.error(f"❌ Falha ao inicializar GoogleCalendarClient: {e}")
                self.use_real_api = False
                self.calendar = None
        else:
            self.calendar = None
            logger.info("ℹ️  Modo simulado ativado (sem API real)")
    
    def perceive_schedule_context(self) -> Dict[str, Any]:
        """Percepção contextual: entende agenda atual do usuário
        
        Returns:
            Dict com contexto da agenda:
            - today_busy: bool (dia ocupado)
            - upcoming_important: bool (eventos importantes próximos)
            - next_free_slot: dict (próximo horário livre)
            - event_count: int (total de eventos visíveis)
            - schedule_load: str (leve, moderado, pesado)
        """
        if not self.use_real_api or self.calendar is None:
            # Modo simulado para desenvolvimento
            return {
                "today_busy": False,
                "upcoming_important": False,
                "next_free_slot": {"dateTime": "2026-04-12T15:00:00", "timeZone": "America/Sao_Paulo"},
                "event_count": 0,
                "schedule_load": "leve",
                "mode": "simulado"
            }
        
        try:
            # Eventos de hoje
            today_events = self.calendar.get_today_events()
            
            # Próximos eventos (7 dias)
            upcoming = self.calendar.get_upcoming_events(10)
            
            # Análise biomimética
            today_busy = len(today_events) > 3  # Mais de 3 eventos = dia ocupado
            
            upcoming_important = any(
                any(keyword in (e.get("summary", "") + e.get("description", "")).lower()
                    for keyword in ["reunião", "importante", "urgente", "deadline", "prazo"])
                for e in upcoming
            )
            
            next_free = self._find_next_free_slot(today_events, upcoming)
            
            total_events = len(today_events) + len(upcoming)
            if total_events > 15:
                schedule_load = "pesado"
            elif total_events > 7:
                schedule_load = "moderado"
            else:
                schedule_load = "leve"
            
            return {
                "today_busy": today_busy,
                "upcoming_important": upcoming_important,
                "next_free_slot": next_free,
                "event_count": total_events,
                "schedule_load": schedule_load,
                "mode": "real"
            }
            
        except Exception as e:
            logger.error(f"Erro na percepção de calendário: {e}")
            return {
                "today_busy": False,
                "upcoming_important": False,
                "next_free_slot": {"dateTime": "2026-04-12T15:00:00", "timeZone": "America/Sao_Paulo"},
                "event_count": 0,
                "schedule_load": "desconhecido",
                "mode": "erro",
                "error": str(e)
            }
    
    def schedule_biomimetic_task(self, task_description: str, 
                                priority: str = "medium",
                                duration: str = "1h") -> Dict[str, Any]:
        """Agenda tarefa baseado em prioridade biomimética
        
        Args:
            task_description: Descrição da tarefa
            priority: "low", "medium", "high"
            duration: Duração no formato "1h", "30m", etc.
            
        Returns:
            Dict com resultado do agendamento (evento criado ou simulado)
        """
        if not self.use_real_api or self.calendar is None:
            # Modo simulado
            best_time = self._calculate_optimal_time_simulated(priority)
            
            event_data = {
                "summary": f"[AI-Biomimetica] {task_description}",
                "description": f"Tarefa agendada automaticamente pelo sistema biomimético (modo simulado)",
                "start": best_time,
                "end": self._add_duration(best_time, duration),
                "colorId": "5" if priority == "high" else ("2" if priority == "medium" else "8"),
                "status": "simulado"
            }
            
            return {"success": True, "event": event_data, "mode": "simulado"}
        
        try:
            # Encontrar melhor horário usando lógica biomimética
            best_time = self._calculate_optimal_time(priority)
            
            event_data = {
                "summary": f"[AI-Biomimetica] {task_description}",
                "description": f"Tarefa agendada automaticamente pelo sistema biomimético\nPrioridade: {priority}",
                "start": best_time,
                "end": self._add_duration(best_time, duration),
                "colorId": "5" if priority == "high" else ("2" if priority == "medium" else "8"),
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 30}
                    ]
                }
            }
            
            # Criar evento real
            created_event = self.calendar.create_event(event_data)
            
            return {
                "success": True,
                "event": created_event,
                "mode": "real",
                "event_id": created_event.get("id"),
                "html_link": created_event.get("htmlLink")
            }
            
        except Exception as e:
            logger.error(f"Erro ao agendar tarefa: {e}")
            return {"success": False, "error": str(e), "mode": "real"}
    
    def get_upcoming_events_biomimetic(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém próximos eventos com análise biomimética
        
        Args:
            limit: Número máximo de eventos
            
        Returns:
            Lista de eventos com análise biomimética
        """
        if not self.use_real_api or self.calendar is None:
            return []
        
        try:
            events = self.calendar.get_upcoming_events(limit)
            
            # Adicionar análise biomimética
            for event in events:
                event["biomimetic_priority"] = self._analyze_event_priority(event)
                event["biomimetic_action"] = self._suggest_action_for_event(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Erro ao obter eventos: {e}")
            return []
    
    def integrate_with_biomimetic_system(self, system: Any) -> bool:
        """Integra este agente com sistema biomimético principal
        
        Args:
            system: Instância de AutoEvolvingAISystem ou similar
            
        Returns:
            True se integração bem-sucedida
        """
        if not BIOMIMETIC_SYSTEM_AVAILABLE:
            logger.warning("Sistema biomimético não disponível para integração")
            return False
        
        try:
            # Registrar este agente no sistema biomimético
            system.register_agent("calendar", self)
            logger.info("✅ Agente de calendário registrado no sistema biomimético")
            return True
            
        except Exception as e:
            logger.error(f"Erro na integração com sistema biomimético: {e}")
            return False
    
    # Métodos auxiliares privados
    
    def _find_next_free_slot(self, today_events: List[Dict], 
                            upcoming_events: List[Dict]) -> Dict[str, str]:
        """Encontra próximo horário livre (implementação simplificada)"""
        # Lógica simplificada: retorna amanhã às 10h
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_10am = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        
        return {
            "dateTime": tomorrow_10am.isoformat(),
            "timeZone": "America/Sao_Paulo"
        }
    
    def _calculate_optimal_time(self, priority: str) -> Dict[str, str]:
        """Calcula horário ótimo baseado em prioridade biomimética"""
        # Lógica biomimética: alta prioridade = mais cedo, baixa = mais tarde
        if priority == "high":
            hours_to_add = 2  # 2 horas a partir de agora
        elif priority == "medium":
            hours_to_add = 24  # Amanhã
        else:  # low
            hours_to_add = 72  # 3 dias
        
        optimal_time = datetime.now() + timedelta(hours=hours_to_add)
        
        # Arredondar para próxima meia hora
        minute = optimal_time.minute
        if minute < 30:
            optimal_time = optimal_time.replace(minute=30, second=0, microsecond=0)
        else:
            optimal_time = optimal_time.replace(minute=0, second=0, microsecond=0)
            optimal_time += timedelta(hours=1)
        
        return {
            "dateTime": optimal_time.isoformat(),
            "timeZone": "America/Sao_Paulo"
        }
    
    def _calculate_optimal_time_simulated(self, priority: str) -> Dict[str, str]:
        """Versão simulada para desenvolvimento"""
        if priority == "high":
            return {"dateTime": "2026-04-12T10:00:00", "timeZone": "America/Sao_Paulo"}
        elif priority == "medium":
            return {"dateTime": "2026-04-12T14:00:00", "timeZone": "America/Sao_Paulo"}
        else:
            return {"dateTime": "2026-04-12T16:00:00", "timeZone": "America/Sao_Paulo"}
    
    def _add_duration(self, time_slot: Dict[str, str], duration: str) -> Dict[str, str]:
        """Adiciona duração a um slot de tempo"""
        # Implementação simplificada
        return {
            "dateTime": time_slot["dateTime"],  # Em implementação real, calcularia
            "timeZone": time_slot["timeZone"]
        }
    
    def _analyze_event_priority(self, event: Dict[str, Any]) -> str:
        """Analisa prioridade biomimética de um evento"""
        summary = event.get("summary", "").lower()
        description = event.get("description", "").lower()
        
        high_priority_keywords = ["urgente", "importante", "deadline", "reunião executiva"]
        medium_priority_keywords = ["reunião", "consulta", "apresentação"]
        
        if any(keyword in summary or keyword in description 
               for keyword in high_priority_keywords):
            return "high"
        elif any(keyword in summary or keyword in description 
                 for keyword in medium_priority_keywords):
            return "medium"
        else:
            return "low"
    
    def _suggest_action_for_event(self, event: Dict[str, Any]) -> str:
        """Sugere ação biomimética para um evento"""
        priority = self._analyze_event_priority(event)
        
        if priority == "high":
            return "preparar_com_antecedencia"
        elif priority == "medium":
            return "revisar_brevemente"
        else:
            return "monitorar_passivamente"


def demo_biomimetic_calendar_agent():
    """Demonstração do agente biomimético de calendário"""
    print("🧠 AI-Biomimetica - Demonstração Biomimetic Calendar Agent")
    print("=" * 60)
    
    # Criar agente em modo simulado
    agent = BiomimeticCalendarAgent(use_real_api=False)
    
    print("\n1. 🎯 PERCEPÇÃO CONTEXTUAL (modo simulado):")
    context = agent.perceive_schedule_context()
    for key, value in context.items():
        print(f"   • {key}: {value}")
    
    print("\n2. 📅 AGENDAMENTO BIOMIMÉTICO:")
    result = agent.schedule_biomimetic_task(
        task_description="Revisar implementação Fase 6",
        priority="high",
        duration="2h"
    )
    
    if result.get("success"):
        event = result.get("event", {})
        print(f"   ✅ Tarefa agendada com sucesso (modo {result.get('mode')})")
        print(f"   • Título: {event.get('summary', 'N/A')}")
        print(f"   • Início: {event.get('start', {}).get('dateTime', 'N/A')}")
        print(f"   • Prioridade: alta (cor {event.get('colorId', 'N/A')})")
    else:
        print(f"   ❌ Falha: {result.get('error', 'Desconhecido')}")
    
    print("\n3. 🔗 INTEGRAÇÃO COM SISTEMA BIOMIMÉTICO:")
    if BIOMIMETIC_SYSTEM_AVAILABLE:
        print("   ✅ Sistema biomimético disponível para integração")
        # Nota: Não criamos instância real para demonstração
    else:
        print("   ⚠️  Sistema biomimético não disponível neste ambiente")
    
    print("\n" + "=" * 60)
    print("🎓 DEMONSTRAÇÃO CONCLUÍDA!")
    print("\n📌 STATUS DO AGENTE:")
    print("   ✅ Classe BiomimeticCalendarAgent implementada")
    print("   ✅ Modos real e simulado suportados")
    print("   ✅ Percepção contextual biomimética")
    print("   ✅ Agendamento inteligente baseado em prioridade")
    print("   ✅ Pronto para integração com sistema principal")
    
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("   1. Configurar credentials.json para modo real")
    print("   2. Testar com `python -m src.agents.biomimetic_calendar_agent`")
    print("   3. Integrar com AutoEvolvingAISystem")
    print("   4. Adicionar mais lógica biomimética avançada")


if __name__ == "__main__":
    demo_biomimetic_calendar_agent()