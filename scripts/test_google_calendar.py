#!/usr/bin/env python3
"""
Script de teste para integração Google Calendar API
Fase 6: Percepção Multimodal

Uso:
    python scripts/test_google_calendar.py

Requisitos:
    - credentials.json na raiz do projeto
    - Dependências Google APIs instaladas
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_google_calendar():
    """Testa integração com Google Calendar API"""
    print("🧪 Testando Google Calendar API...")
    print("=" * 50)
    
    try:
        from src.google.google_calendar_client import GoogleCalendarClient
        print("✅ Módulo importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        print("\n📦 Instale as dependências:")
        print("   pip install -r requirements/requirements_google.txt")
        return False
    
    # Verificar se credentials.json existe
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
    if not os.path.exists(credentials_path):
        print(f"❌ Arquivo credentials.json não encontrado em: {credentials_path}")
        print("\n📝 Crie o arquivo credentials.json com suas credenciais Google Cloud")
        print("   Use credentials.example.json como modelo")
        return False
    
    print(f"✅ credentials.json encontrado: {credentials_path}")
    
    try:
        # Inicializar cliente
        client = GoogleCalendarClient()
        print("✅ Cliente GoogleCalendarClient inicializado")
        
        # Tentar autenticar
        print("\n🔑 Iniciando autenticação OAuth2...")
        print("   NOTA: Se for a primeira vez, abrirá o browser para login")
        print("   Aperte Ctrl+C para cancelar se necessário")
        
        service = client.authenticate()
        print("✅ Autenticação bem-sucedida!")
        
        # Testar listagem de calendários
        print("\n📋 Listando calendários...")
        calendars = client.get_calendar_list()
        print(f"   Encontrados {len(calendars)} calendário(s)")
        
        for i, cal in enumerate(calendars[:3], 1):  # Mostrar até 3
            print(f"   {i}. {cal.get('summary', 'Sem nome')} ({cal.get('id', 'N/A')})")
        
        if len(calendars) > 3:
            print(f"   ... e mais {len(calendars) - 3} calendário(s)")
        
        # Testar busca de eventos
        print("\n🔍 Buscando próximos eventos...")
        events = client.get_upcoming_events(5)
        print(f"   Próximos {len(events)} evento(s):")
        
        if events:
            for i, event in enumerate(events, 1):
                display = client.format_event_for_display(event)
                print(f"   {i}. {display}")
        else:
            print("   📭 Nenhum evento futuro encontrado")
        
        # Testar eventos de hoje
        print("\n📅 Buscando eventos de hoje...")
        today_events = client.get_today_events()
        print(f"   {len(today_events)} evento(s) hoje:")
        
        for i, event in enumerate(today_events[:5], 1):
            summary = event.get('summary', 'Sem título')
            start = event.get('start', {})
            time = start.get('dateTime', start.get('date', 'N/A'))
            print(f"   {i}. {summary} ({time})")
        
        if len(today_events) > 5:
            print(f"   ... e mais {len(today_events) - 5} evento(s)")
        
        print("\n" + "=" * 50)
        print("🎯 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Google Calendar API integrado ao sistema biomimético")
        print("\n📌 Próximos passos:")
        print("   1. Integrar com Obsidian (memória persistente)")
        print("   2. Conectar ao sistema biomimético principal")
        print("   3. Implementar criação de eventos (Fase 6.2)")
        print("   4. Adicionar Gmail API (Fase 6.3)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Verifique se credentials.json está correto")
        print("   2. Confirme URLs de redirecionamento no Google Cloud Console")
        print("   3. Verifique se Calendar API está ativada")
        print("   4. Tente regenerar credentials.json se necessário")
        return False

if __name__ == "__main__":
    print("🚀 AI-Biomimetica - Teste Google Calendar API")
    print("   Fase 6: Percepção Multimodal\n")
    
    success = test_google_calendar()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)