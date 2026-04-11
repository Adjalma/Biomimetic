"""
Google Calendar API Client para sistema biomimético AI-Biomimetica
Fase 6: Percepção Multimodal - Integração com Google Calendar

Autor: Jarvis (OpenClaw)
Data: 2026-04-11

Funcionalidades:
- Autenticação OAuth2 com fluxo local/server
- Leitura de eventos do calendário
- Criação de eventos (futuro)
- Atualização/exclusão de eventos (futuro)

Dependências:
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- google-auth
"""

import os
import pickle
import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopos da API (permissões)
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarClient:
    """Cliente para integração com Google Calendar API"""
    
    def __init__(self, 
                 credentials_path: str = "credentials.json",
                 token_path: str = "token.pickle",
                 storage_dir: str = "storage"):
        """
        Inicializa cliente Google Calendar.
        
        Args:
            credentials_path: Caminho para arquivo credentials.json
            token_path: Caminho para salvar token de autenticação
            storage_dir: Diretório para armazenamento persistente
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.storage_dir = storage_dir
        self.service = None
        
        # Garantir diretório de storage existe
        os.makedirs(storage_dir, exist_ok=True)
    
    def authenticate(self) -> Any:
        """
        Autentica com Google OAuth2 e retorna serviço.
        
        Fluxo:
        1. Tenta carregar token salvo
        2. Se token inválido/inexistente, inicia fluxo OAuth2 no browser
        3. Salva token para uso futuro
        4. Constroi serviço Calendar API
        
        Returns:
            Serviço Google Calendar API construído
        """
        creds = None
        
        # Caminho completo para token
        token_full_path = os.path.join(self.storage_dir, self.token_path)
        
        # 1. Tentar carregar token salvo
        if os.path.exists(token_full_path):
            with open(token_full_path, 'rb') as token:
                creds = pickle.load(token)
        
        # 2. Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 3. Salvar credenciais para próxima vez
            with open(token_full_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # 4. Construir serviço Calendar API
        self.service = build('calendar', 'v3', credentials=creds)
        return self.service
    
    def get_service(self) -> Any:
        """Retorna serviço (autentica se necessário)"""
        if not self.service:
            self.authenticate()
        return self.service
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca próximos eventos do calendário primário.
        
        Args:
            max_results: Número máximo de eventos a retornar
            
        Returns:
            Lista de eventos (dicionários)
        """
        try:
            service = self.get_service()
            
            # Hora atual em UTC
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Formatar eventos para saída mais limpa
            formatted_events = []
            for event in events:
                formatted = {
                    'id': event.get('id'),
                    'summary': event.get('summary', 'Sem título'),
                    'description': event.get('description', ''),
                    'start': event.get('start', {}),
                    'end': event.get('end', {}),
                    'location': event.get('location', ''),
                    'attendees': event.get('attendees', []),
                    'created': event.get('created'),
                    'updated': event.get('updated'),
                    'status': event.get('status'),
                    'htmlLink': event.get('htmlLink', '')
                }
                formatted_events.append(formatted)
            
            return formatted_events
            
        except HttpError as error:
            print(f'❌ Erro ao buscar eventos do Google Calendar: {error}')
            return []
        except Exception as e:
            print(f'❌ Erro inesperado: {e}')
            return []
    
    def create_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Cria um novo evento no calendário (Fase 6.2).
        
        Args:
            event_data: Dicionário com dados do evento
                Exemplo: {
                    'summary': 'Reunião de equipe',
                    'description': 'Discussão de projetos',
                    'start': {'dateTime': '2024-04-12T10:00:00', 'timeZone': 'America/Sao_Paulo'},
                    'end': {'dateTime': '2024-04-12T11:00:00', 'timeZone': 'America/Sao_Paulo'},
                    'attendees': [{'email': 'email@exemplo.com'}]
                }
        
        Returns:
            Evento criado ou None em caso de erro
        """
        try:
            service = self.get_service()
            
            event = service.events().insert(
                calendarId='primary',
                body=event_data
            ).execute()
            
            print(f'✅ Evento criado: {event.get("htmlLink")}')
            return event
            
        except HttpError as error:
            print(f'❌ Erro ao criar evento: {error}')
            return None
    
    def get_calendar_list(self) -> List[Dict[str, Any]]:
        """Lista todos os calendários disponíveis"""
        try:
            service = self.get_service()
            calendar_list = service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as error:
            print(f'❌ Erro ao listar calendários: {error}')
            return []
    
    def format_event_for_display(self, event: Dict[str, Any]) -> str:
        """Formata evento para exibição legível"""
        summary = event.get('summary', 'Sem título')
        start = event.get('start', {})
        end = event.get('end', {})
        
        # Extrair data/hora
        start_time = start.get('dateTime', start.get('date', 'N/A'))
        end_time = end.get('dateTime', end.get('date', 'N/A'))
        
        return f"📅 {summary}\n   ⏰ {start_time} → {end_time}"
    
    def get_today_events(self) -> List[Dict[str, Any]]:
        """Busca eventos de hoje"""
        try:
            service = self.get_service()
            
            # Início do dia
            today_start = datetime.datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            ).isoformat() + 'Z'
            
            # Fim do dia
            today_end = datetime.datetime.utcnow().replace(
                hour=23, minute=59, second=59, microsecond=999999
            ).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=today_start,
                timeMax=today_end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except HttpError as error:
            print(f'❌ Erro ao buscar eventos de hoje: {error}')
            return []
    
    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Atualiza um evento existente no calendário.
        
        Args:
            event_id: ID do evento a ser atualizado
            event_data: Dados atualizados do evento
            
        Returns:
            Evento atualizado ou None em caso de erro
        """
        try:
            service = self.get_service()
            
            event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event_data
            ).execute()
            
            print(f'✅ Evento atualizado: {event.get("htmlLink")}')
            return event
            
        except HttpError as error:
            print(f'❌ Erro ao atualizar evento: {error}')
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """
        Exclui um evento do calendário.
        
        Args:
            event_id: ID do evento a ser excluído
            
        Returns:
            True se excluído com sucesso, False caso contrário
        """
        try:
            service = self.get_service()
            
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            print(f'✅ Evento excluído: {event_id}')
            return True
            
        except HttpError as error:
            print(f'❌ Erro ao excluir evento: {error}')
            return False
    
    def search_events(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca eventos por texto livre (full-text search).
        
        Args:
            query: Texto para busca (ex: "reunião equipe", "dentista")
            max_results: Número máximo de resultados
            
        Returns:
            Lista de eventos encontrados
        """
        try:
            service = self.get_service()
            
            events_result = service.events().list(
                calendarId='primary',
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except HttpError as error:
            print(f'❌ Erro ao buscar eventos: {error}')
            return []
    
    def quick_add_event(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Cria evento usando Quick Add (Google Calendar natural language).
        Ex: "Reunião amanhã às 14h na sala 5"
        
        Args:
            text: Texto em linguagem natural para criação do evento
            
        Returns:
            Evento criado ou None em caso de erro
        """
        try:
            service = self.get_service()
            
            event = service.events().quickAdd(
                calendarId='primary',
                text=text
            ).execute()
            
            print(f'✅ Evento criado via Quick Add: {event.get("htmlLink")}')
            return event
            
        except HttpError as error:
            print(f'❌ Erro ao criar evento via Quick Add: {error}')
            return None
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca um evento específico pelo ID.
        
        Args:
            event_id: ID do evento
            
        Returns:
            Evento completo ou None se não encontrado
        """
        try:
            service = self.get_service()
            
            event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return event
            
        except HttpError as error:
            print(f'❌ Erro ao buscar evento: {error}')
            return None
    
    def get_events_in_range(self, 
                           start_time: str, 
                           end_time: str,
                           max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Busca eventos em um intervalo de tempo específico.
        
        Args:
            start_time: Data/hora inicial (ISO 8601 format)
            end_time: Data/hora final (ISO 8601 format)
            max_results: Número máximo de resultados
            
        Returns:
            Lista de eventos no intervalo
        """
        try:
            service = self.get_service()
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except HttpError as error:
            print(f'❌ Erro ao buscar eventos no intervalo: {error}')
            return []
    
    def create_recurring_event(self, 
                              event_data: Dict[str, Any],
                              recurrence_rule: str) -> Optional[Dict[str, Any]]:
        """
        Cria evento recorrente (ex: "RRULE:FREQ=WEEKLY;BYDAY=MO").
        
        Args:
            event_data: Dados do evento
            recurrence_rule: Regra de recorrência no formato RRULE
            
        Returns:
            Evento criado ou None em caso de erro
        """
        try:
            # Adicionar regra de recorrência aos dados do evento
            event_data_with_recurrence = event_data.copy()
            event_data_with_recurrence['recurrence'] = [recurrence_rule]
            
            return self.create_event(event_data_with_recurrence)
            
        except Exception as e:
            print(f'❌ Erro ao criar evento recorrente: {e}')
            return None


# Exemplo de uso (descomentar para testar)
if __name__ == "__main__":
    print("🧪 Testando Google Calendar Client...")
    
    client = GoogleCalendarClient()
    
    # 1. Testar autenticação
    print("🔑 Autenticando...")
    service = client.authenticate()
    print("✅ Autenticação bem-sucedida!")
    
    # 2. Listar calendários
    print("\n📋 Listando calendários...")
    calendars = client.get_calendar_list()
    print(f"   Encontrados {len(calendars)} calendário(s)")
    
    # 3. Buscar próximos eventos
    print("\n🔍 Buscando próximos eventos...")
    events = client.get_upcoming_events(5)
    print(f"   Próximos {len(events)} evento(s):")
    
    for i, event in enumerate(events, 1):
        print(f"   {i}. {client.format_event_for_display(event)}")
    
    print("\n🎯 Integração Google Calendar API pronta para Fase 6!")