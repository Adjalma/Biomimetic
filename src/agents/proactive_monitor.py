"""
Monitoramento Proativo para Sistema de Ação Autônoma
Autor: Jarvis (OpenClaw)
Data: 2026-04-11

Objetivo:
- Monitorar métricas de performance em tempo real
- Detectar anomalias e padrões problemáticos
- Gerar alertas proativos antes que problemas ocorram
- Sugerir correções e otimizações automáticas
- Integrar com sistema biomimético para aprendizado contínuo

Funcionalidades:
- Coleta contínua de métricas de execução
- Detecção de outliers usando estatística
- Identificação de padrões de erro recorrentes
- Previsão de problemas baseada em tendências
- Geração de alertas com prioridades
- Sugestões de correção automáticas
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Deque
from datetime import datetime, timedelta
from enum import Enum
import statistics
import json
from collections import deque, defaultdict
import time

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Severidade de alertas"""
    INFO = "info"           # Informativo, sem ação necessária
    LOW = "low"            # Baixa prioridade
    MEDIUM = "medium"      # Atenção necessária
    HIGH = "high"          # Ação recomendada
    CRITICAL = "critical"  # Ação imediata necessária

class MetricType(Enum):
    """Tipos de métricas monitoradas"""
    EXECUTION_TIME = "execution_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    ACTION_FREQUENCY = "action_frequency"
    HUMAN_APPROVAL_RATE = "human_approval_rate"
    RISK_SCORE = "risk_score"
    LATENCY = "latency"
    RESOURCE_USAGE = "resource_usage"

class AnomalyType(Enum):
    """Tipos de anomalias detectáveis"""
    SPIKE = "spike"                    # Pico súbito
    DROP = "drop"                      # Queda súbita
    TREND_UP = "trend_up"              # Tendência de alta
    TREND_DOWN = "trend_down"          # Tendência de baixa
    PATTERN_CHANGE = "pattern_change"  # Mudança de padrão
    OUTLIER = "outlier"                # Valor atípico
    SEASONALITY_BREAK = "seasonality_break"  # Quebra de sazonalidade

class ProactiveMonitor:
    """Sistema de monitoramento proativo"""
    
    def __init__(self, window_size: int = 100, alert_threshold: float = 3.0):
        """
        Inicializa monitor proativo.
        
        Args:
            window_size: Tamanho da janela para cálculo de métricas
            alert_threshold: Limite de desvio padrão para alertas
        """
        self.window_size = window_size
        self.alert_threshold = alert_threshold
        
        # Armazenamento de métricas
        self.metrics: Dict[MetricType, Deque[Tuple[datetime, float]]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        
        # Histórico de ações
        self.action_history: Deque[Dict[str, Any]] = deque(maxlen=window_size * 2)
        
        # Alertas ativos
        self.active_alerts: List[Dict[str, Any]] = []
        self.alert_history: Deque[Dict[str, Any]] = deque(maxlen=100)
        
        # Padrões de erro
        self.error_patterns: Dict[str, Dict[str, Any]] = {}
        
        # Configurações
        self.check_interval_seconds = 60  # Verificar a cada 60 segundos
        self.last_check = datetime.now()
        
        # Limites de alerta por métrica
        self.alert_limits = {
            MetricType.EXECUTION_TIME: {
                "warning": 10.0,   # segundos
                "critical": 30.0   # segundos
            },
            MetricType.SUCCESS_RATE: {
                "warning": 0.85,   # 85%
                "critical": 0.70   # 70%
            },
            MetricType.ERROR_RATE: {
                "warning": 0.15,   # 15%
                "critical": 0.30   # 30%
            },
            MetricType.HUMAN_APPROVAL_RATE: {
                "warning": 0.25,   # 25%
                "critical": 0.50   # 50%
            },
        }
        
        # Integração com sistema biomimético
        self.biomimetic_system = None
        
        logger.info(f"✅ ProactiveMonitor inicializado (window: {window_size}, threshold: {alert_threshold})")
    
    def record_action(self, action_result: Dict[str, Any]):
        """
        Registra resultado de ação para monitoramento.
        
        Args:
            action_result: Resultado da ação executada
        """
        try:
            timestamp = datetime.now()
            
            # Extrair métricas do resultado
            execution_time = action_result.get("execution_time", 0.0)
            success = action_result.get("status") == "completed"
            action_type = action_result.get("action_type", "unknown")
            risk_score = action_result.get("risk_score", 0.0)
            
            # Registrar métricas básicas
            self.metrics[MetricType.EXECUTION_TIME].append((timestamp, execution_time))
            self.metrics[MetricType.SUCCESS_RATE].append((timestamp, 1.0 if success else 0.0))
            self.metrics[MetricType.RISK_SCORE].append((timestamp, risk_score))
            
            # Registrar ação no histórico
            action_record = {
                "timestamp": timestamp.isoformat(),
                "action_type": action_type,
                "success": success,
                "execution_time": execution_time,
                "risk_score": risk_score,
                "result": action_result
            }
            self.action_history.append(action_record)
            
            # Analisar padrões de erro
            if not success:
                self._analyze_error_pattern(action_record)
            
            # Verificar se precisa emitir alertas imediatos
            self._check_immediate_alerts(action_record)
            
            logger.debug(f"✅ Ação registrada: {action_type} (sucesso: {success}, tempo: {execution_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar ação: {e}")
    
    def _analyze_error_pattern(self, action_record: Dict[str, Any]):
        """Analisa padrões de erro recorrentes"""
        action_type = action_record["action_type"]
        error_msg = action_record["result"].get("error", "unknown")
        
        # Criar chave para o padrão de erro
        error_key = f"{action_type}:{error_msg[:50]}"
        
        if error_key not in self.error_patterns:
            self.error_patterns[error_key] = {
                "action_type": action_type,
                "error_pattern": error_msg,
                "first_seen": action_record["timestamp"],
                "last_seen": action_record["timestamp"],
                "count": 1,
                "recent_occurrences": deque(maxlen=10)
            }
        else:
            pattern = self.error_patterns[error_key]
            pattern["last_seen"] = action_record["timestamp"]
            pattern["count"] += 1
        
        # Registrar ocorrência recente
        self.error_patterns[error_key]["recent_occurrences"].append(action_record["timestamp"])
        
        # Verificar se é um padrão recorrente
        pattern = self.error_patterns[error_key]
        if pattern["count"] >= 3:
            # Calcular frequência
            occurrences = list(pattern["recent_occurrences"])
            if len(occurrences) >= 3:
                time_diffs = []
                for i in range(1, len(occurrences)):
                    t1 = datetime.fromisoformat(occurrences[i-1])
                    t2 = datetime.fromisoformat(occurrences[i])
                    time_diffs.append((t2 - t1).total_seconds())
                
                if time_diffs:
                    avg_frequency = statistics.mean(time_diffs)
                    pattern["avg_frequency_seconds"] = avg_frequency
                    
                    # Se erro ocorre frequentemente, gerar alerta
                    if avg_frequency < 3600:  # Mais de uma vez por hora
                        self._create_pattern_alert(pattern, avg_frequency)
    
    def _check_immediate_alerts(self, action_record: Dict[str, Any]):
        """Verifica alertas imediatos baseados na ação"""
        action_type = action_record["action_type"]
        execution_time = action_record["execution_time"]
        success = action_record["success"]
        
        # Verificar tempo de execução excessivo
        time_limit = self.alert_limits[MetricType.EXECUTION_TIME]
        if execution_time > time_limit["critical"]:
            self.create_alert(
                title=f"Tempo de execução CRÍTICO para {action_type}",
                message=f"Ação {action_type} levou {execution_time:.1f}s (limite: {time_limit['critical']}s)",
                severity=AlertSeverity.CRITICAL,
                metric_type=MetricType.EXECUTION_TIME,
                value=execution_time,
                suggested_action="Investigar gargalos de performance ou dividir ação em partes menores"
            )
        elif execution_time > time_limit["warning"]:
            self.create_alert(
                title=f"Tempo de execução ALTO para {action_type}",
                message=f"Ação {action_type} levou {execution_time:.1f}s (limite de aviso: {time_limit['warning']}s)",
                severity=AlertSeverity.HIGH,
                metric_type=MetricType.EXECUTION_TIME,
                value=execution_time,
                suggested_action="Monitorar performance e considerar otimizações"
            )
        
        # Verificar falhas consecutivas
        if not success:
            recent_failures = self._count_recent_failures(action_type, window_minutes=15)
            if recent_failures >= 3:
                self.create_alert(
                    title=f"Falhas consecutivas para {action_type}",
                    message=f"Ação {action_type} falhou {recent_failures} vezes nos últimos 15 minutos",
                    severity=AlertSeverity.HIGH,
                    metric_type=MetricType.ERROR_RATE,
                    value=recent_failures,
                    suggested_action="Verificar dependências, credenciais ou parâmetros da ação"
                )
    
    def _count_recent_failures(self, action_type: str, window_minutes: int) -> int:
        """Conta falhas recentes para um tipo de ação"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        count = 0
        
        for action in reversed(self.action_history):
            if datetime.fromisoformat(action["timestamp"]) < cutoff:
                break
            if action["action_type"] == action_type and not action["success"]:
                count += 1
        
        return count
    
    def _create_pattern_alert(self, pattern: Dict[str, Any], frequency: float):
        """Cria alerta para padrão de erro recorrente"""
        frequency_min = frequency / 60
        
        self.create_alert(
            title=f"Padrão de erro recorrente: {pattern['action_type']}",
            message=f"Erro '{pattern['error_pattern'][:50]}...' ocorreu {pattern['count']} vezes (a cada {frequency_min:.1f} min)",
            severity=AlertSeverity.HIGH,
            metric_type=MetricType.ERROR_RATE,
            value=pattern["count"],
            suggested_action="Investigar causa raiz do erro e implementar correção permanente",
            metadata={
                "pattern": pattern["error_pattern"],
                "action_type": pattern["action_type"],
                "frequency_minutes": frequency_min,
                "occurrence_count": pattern["count"]
            }
        )
    
    def check_metrics(self):
        """Verifica todas as métricas em busca de anomalias"""
        current_time = datetime.now()
        
        # Verificar se precisa executar (baseado no intervalo)
        if (current_time - self.last_check).total_seconds() < self.check_interval_seconds:
            return
        
        self.last_check = current_time
        
        logger.debug("🔍 Verificando métricas para anomalias...")
        
        # Verificar cada tipo de métrica
        for metric_type in MetricType:
            if metric_type in self.metrics and len(self.metrics[metric_type]) >= 10:
                self._check_metric_anomalies(metric_type)
        
        # Verificar tendências de longo prazo
        self._check_long_term_trends()
        
        # Verificar padrões sazonais (se houver dados suficientes)
        if len(self.action_history) >= self.window_size:
            self._check_seasonal_patterns()
        
        # Limpar alertas antigos
        self._cleanup_old_alerts()
    
    def _check_metric_anomalies(self, metric_type: MetricType):
        """Verifica anomalias em uma métrica específica"""
        metric_data = self.metrics[metric_type]
        
        if len(metric_data) < 10:
            return  # Dados insuficientes
        
        # Extrair valores
        timestamps, values = zip(*metric_data)
        values_list = list(values)
        
        # Calcular estatísticas
        mean = statistics.mean(values_list)
        stdev = statistics.stdev(values_list) if len(values_list) > 1 else 0
        
        if stdev == 0:
            return  # Sem variabilidade
        
        # Verificar último valor
        last_value = values_list[-1]
        z_score = abs((last_value - mean) / stdev) if stdev > 0 else 0
        
        # Verificar se é um outlier
        if z_score > self.alert_threshold:
            self._create_anomaly_alert(metric_type, last_value, mean, stdev, z_score)
        
        # Verificar tendência recente (últimos 5 valores)
        if len(values_list) >= 5:
            recent_values = values_list[-5:]
            trend = self._calculate_trend(recent_values)
            
            if abs(trend) > 0.5:  # Tendência significativa
                self._create_trend_alert(metric_type, trend, recent_values)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcula tendência linear simples"""
        if len(values) < 2:
            return 0.0
        
        # Coeficiente angular simples
        x = list(range(len(values)))
        y = values
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x_i * x_i for x_i in x)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = n * sum_x2 - sum_x * sum_x
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def _create_anomaly_alert(self, metric_type: MetricType, value: float, 
                             mean: float, stdev: float, z_score: float):
        """Cria alerta para anomalia detectada"""
        
        metric_name = metric_type.value.replace("_", " ").title()
        
        self.create_alert(
            title=f"Anomalia detectada em {metric_name}",
            message=f"Valor {value:.2f} desvia {z_score:.1f}σ da média ({mean:.2f} ± {stdev:.2f})",
            severity=AlertSeverity.HIGH if z_score > 4.0 else AlertSeverity.MEDIUM,
            metric_type=metric_type,
            value=value,
            suggested_action="Investigar causa da variação anormal",
            metadata={
                "z_score": z_score,
                "mean": mean,
                "stdev": stdev,
                "anomaly_type": AnomalyType.OUTLIER.value
            }
        )
    
    def _create_trend_alert(self, metric_type: MetricType, trend: float, 
                           recent_values: List[float]):
        """Cria alerta para tendência detectada"""
        
        metric_name = metric_type.value.replace("_", " ").title()
        trend_direction = "alta" if trend > 0 else "baixa"
        trend_strength = "forte" if abs(trend) > 1.0 else "moderada"
        
        self.create_alert(
            title=f"Tendência de {trend_direction} em {metric_name}",
            message=f"Tendência {trend_strength} de {trend_direction} detectada nos últimos {len(recent_values)} valores",
            severity=AlertSeverity.MEDIUM if abs(trend) > 1.0 else AlertSeverity.LOW,
            metric_type=metric_type,
            value=trend,
            suggested_action="Monitorar continuamente e ajustar limites se necessário",
            metadata={
                "trend": trend,
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "recent_values": recent_values,
                "anomaly_type": AnomalyType.TREND_UP.value if trend > 0 else AnomalyType.TREND_DOWN.value
            }
        )
    
    def _check_long_term_trends(self):
        """Verifica tendências de longo prazo"""
        if len(self.action_history) < 50:
            return  # Dados insuficientes
        
        # Analisar taxa de sucesso em janelas de tempo
        window_days = 7
        daily_success = defaultdict(list)
        
        for action in self.action_history:
            timestamp = datetime.fromisoformat(action["timestamp"])
            date_key = timestamp.strftime("%Y-%m-%d")
            daily_success[date_key].append(action["success"])
        
        # Calcular taxa de sucesso diária
        success_rates = []
        dates = []
        
        for date_key, successes in sorted(daily_success.items())[-window_days:]:
            if successes:
                success_rate = sum(1 for s in successes if s) / len(successes)
                success_rates.append(success_rate)
                dates.append(date_key)
        
        if len(success_rates) >= 3:
            trend = self._calculate_trend(success_rates)
            
            if trend < -0.05:  # Tendência de queda na taxa de sucesso
                self.create_alert(
                    title="Queda na taxa de sucesso ao longo do tempo",
                    message=f"Taxa de sucesso mostrando tendência de queda ({trend:.3f}/dia) nos últimos {len(dates)} dias",
                    severity=AlertSeverity.HIGH,
                    metric_type=MetricType.SUCCESS_RATE,
                    value=trend,
                    suggested_action="Revisar ações recentes e identificar causas comuns de falha",
                    metadata={
                        "trend": trend,
                        "days_analyzed": len(dates),
                        "success_rates": success_rates,
                        "dates": dates
                    }
                )
    
    def _check_seasonal_patterns(self):
        """Verifica padrões sazonais (horário do dia, dia da semana)"""
        if len(self.action_history) < 100:
            return
        
        # Agrupar por hora do dia
        hourly_success = defaultdict(list)
        hourly_count = defaultdict(int)
        
        for action in self.action_history:
            timestamp = datetime.fromisoformat(action["timestamp"])
            hour = timestamp.hour
            hourly_success[hour].append(action["success"])
            hourly_count[hour] += 1
        
        # Identificar horas com baixa performance
        for hour in range(24):
            successes = hourly_success.get(hour, [])
            if len(successes) >= 10:
                success_rate = sum(1 for s in successes if s) / len(successes)
                
                if success_rate < 0.7:  # Baixa taxa de sucesso nesta hora
                    self.create_alert(
                        title=f"Baixa performance nas {hour:02d}:00",
                        message=f"Taxa de sucesso de {success_rate:.1%} nas {hour:02d}:00 ({len(successes)} ações)",
                        severity=AlertSeverity.MEDIUM,
                        metric_type=MetricType.SUCCESS_RATE,
                        value=success_rate,
                        suggested_action="Investigar fatores específicos deste horário (carga do sistema, disponibilidade de APIs, etc.)",
                        metadata={
                            "hour": hour,
                            "action_count": len(successes),
                            "success_rate": success_rate
                        }
                    )
    
    def create_alert(self, title: str, message: str, severity: AlertSeverity,
                    metric_type: MetricType, value: float, 
                    suggested_action: str, metadata: Dict[str, Any] = None):
        """Cria um novo alerta"""
        
        alert_id = f"alert_{int(time.time())}_{len(self.active_alerts)}"
        
        alert = {
            "alert_id": alert_id,
            "title": title,
            "message": message,
            "severity": severity.value,
            "metric_type": metric_type.value,
            "value": value,
            "suggested_action": suggested_action,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "acknowledged": False,
            "resolved": False
        }
        
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        
        logger.warning(f"🚨 ALERTA {severity.value}: {title}")
        logger.warning(f"   {message}")
        logger.warning(f"   Ação sugerida: {suggested_action}")
        
        # Se tiver sistema biomimético, registrar aprendizado
        if self.biomimetic_system and hasattr(self.biomimetic_system, 'record_alert'):
            try:
                self.biomimetic_system.record_alert(alert)
            except Exception as e:
                logger.error(f"❌ Erro ao registrar alerta no sistema biomimético: {e}")
        
        return alert_id
    
    def _cleanup_old_alerts(self):
        """Remove alertas antigos e resolvidos"""
        cutoff = datetime.now() - timedelta(hours=24)
        
        # Manter apenas alertas recentes ou não resolvidos
        self.active_alerts = [
            alert for alert in self.active_alerts
            if (datetime.fromisoformat(alert["created_at"]) > cutoff or 
                not alert.get("resolved", False))
        ]
    
    def acknowledge_alert(self, alert_id: str, user_id: str = "system"):
        """Reconhece um alerta"""
        for alert in self.active_alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_by"] = user_id
                alert["acknowledged_at"] = datetime.now().isoformat()
                logger.info(f"✅ Alerta reconhecido: {alert_id} por {user_id}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = ""):
        """Resolve um alerta"""
        for alert in self.active_alerts:
            if alert["alert_id"] == alert_id:
                alert["resolved"] = True
                alert["resolution_notes"] = resolution_notes
                alert["resolved_at"] = datetime.now().isoformat()
                logger.info(f"✅ Alerta resolvido: {alert_id}")
                return True
        return False
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtém resumo das métricas atuais"""
        summary = {}
        
        for metric_type in MetricType:
            if metric_type in self.metrics and self.metrics[metric_type]:
                values = [v for _, v in self.metrics[metric_type]]
                
                summary[metric_type.value] = {
                    "current": values[-1] if values else 0,
                    "average": statistics.mean(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                    "count": len(values)
                }
        
        return summary
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Obtém recomendações proativas baseadas em métricas"""
        recommendations = []
        
        # Analisar métricas para recomendações
        metrics_summary = self.get_metrics_summary()
        
        # Recomendação 1: Tempo de execução alto
        exec_time = metrics_summary.get(MetricType.EXECUTION_TIME.value, {})
        if exec_time.get("average", 0) > 5.0:  # Mais de 5 segundos em média
            recommendations.append({
                "title": "Otimizar tempo de execução",
                "description": f"Tempo médio de execução é {exec_time['average']:.1f}s",
                "priority": "medium",
                "action": "Considerar cache, paralelismo ou otimização de algoritmos",
                "impact": "Alta",
                "effort": "Médio"
            })
        
        # Recomendação 2: Taxa de erro alta
        error_rate = metrics_summary.get(MetricType.ERROR_RATE.value, {})
        if error_rate.get("average", 0) > 0.2:  # Mais de 20% de erro
            recommendations.append({
                "title": "Reduzir taxa de erro",
                "description": f"Taxa média de erro é {error_rate['average']:.1%}",
                "priority": "high",
                "action": "Investigar causas principais de erro e implementar tratamento melhorado",
                "impact": "Alta",
                "effort": "Alto"
            })
        
        # Recomendação 3: Padrões de erro recorrentes
        if self.error_patterns:
            recurring_count = sum(1 for p in self.error_patterns.values() if p["count"] >= 3)
            if recurring_count > 0:
                recommendations.append({
                    "title": "Corrigir padrões de erro recorrentes",
                    "description": f"{recurring_count} padrões de erro ocorrem repetidamente",
                    "priority": "high",
                    "action": "Implementar correções permanentes para os erros mais frequentes",
                    "impact": "Alta",
                    "effort": "Variado"
                })
        
        return recommendations
    
    def get_status(self) -> Dict[str, Any]:
        """Obtém status do monitor proativo"""
        return {
            "metrics_tracked": len(self.metrics),
            "total_actions_recorded": len(self.action_history),
            "active_alerts": len(self.active_alerts),
            "error_patterns_detected": len(self.error_patterns),
            "window_size": self.window_size,
            "alert_threshold": self.alert_threshold,
            "check_interval_seconds": self.check_interval_seconds,
            "last_check": self.last_check.isoformat() if self.last_check else None
        }
    
    def set_biomimetic_system(self, biomimetic_system):
        """Configura sistema biomimético para aprendizado"""
        self.biomimetic_system = biomimetic_system
        logger.info("✅ Sistema biomimético conectado ao ProactiveMonitor")