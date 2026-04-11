#!/usr/bin/env python3
"""
Exemplo de integração Google Calendar + Obsidian
Demonstra como conectar percepção multimodal (calendário) com memória persistente

Uso:
    python scripts/example_google_obsidian_integration.py
"""

import sys
import os
import json
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def example_integration():
    print("🔗 Exemplo: Google Calendar + Obsidian Integration")
    print("=" * 60)
    
    try:
        # Importar módulos
        from src.google.google_calendar_client import GoogleCalendarClient
        from src.app.obsidian_vault import ObsidianVault
        
        print("✅ Módulos importados com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("\n📦 Verifique se todas as dependências estão instaladas")
        return False
    
    # 1. Inicializar Google Calendar Client
    print("\n1. 📅 Inicializando Google Calendar Client...")
    try:
        calendar_client = GoogleCalendarClient()
        print("   ✅ Cliente inicializado")
    except Exception as e:
        print(f"   ❌ Erro ao inicializar cliente: {e}")
        return False
    
    # 2. Buscar eventos
    print("\n2. 🔍 Buscando próximos eventos do calendário...")
    try:
        events = calendar_client.get_upcoming_events(5)
        print(f"   ✅ Encontrados {len(events)} evento(s)")
        
        if events:
            for i, event in enumerate(events, 1):
                summary = event.get('summary', 'Sem título')
                print(f"   {i}. {summary}")
        else:
            print("   📭 Nenhum evento encontrado")
            # Criar dados de exemplo para demonstração
            events = [{
                'summary': 'Evento de Exemplo - Reunião de Equipe',
                'description': 'Demonstração de integração Google Calendar + Obsidian',
                'start': {'dateTime': datetime.now().isoformat()},
                'end': {'dateTime': datetime.now().isoformat()},
                'location': 'Sala Virtual',
                'htmlLink': 'https://example.com'
            }]
            print("   📝 Usando evento de exemplo para demonstração")
            
    except Exception as e:
        print(f"   ❌ Erro ao buscar eventos: {e}")
        return False
    
    # 3. Inicializar Obsidian Vault
    print("\n3. 🗃️ Inicializando Obsidian Vault...")
    try:
        # Supondo que Obsidian Vault está configurado
        obsidian = ObsidianVault()
        print("   ✅ Obsidian Vault inicializado")
    except Exception as e:
        print(f"   ⚠️ Obsidian não disponível: {e}")
        print("   📝 Continuando sem Obsidian (apenas demonstração)")
        obsidian = None
    
    # 4. Formatar eventos para Obsidian
    print("\n4. 📝 Formatando eventos para memória persistente...")
    
    # Criar conteúdo Markdown
    markdown_content = "# Eventos do Google Calendar\n\n"
    markdown_content += f"*Data de sincronização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    
    if events:
        markdown_content += "## Próximos Eventos\n\n"
        for event in events:
            summary = event.get('summary', 'Sem título')
            description = event.get('description', '')
            location = event.get('location', '')
            start = event.get('start', {})
            end = event.get('end', {})
            html_link = event.get('htmlLink', '')
            
            # Extrair data/hora
            start_time = start.get('dateTime', start.get('date', 'N/A'))
            end_time = end.get('dateTime', end.get('date', 'N/A'))
            
            markdown_content += f"### {summary}\n"
            markdown_content += f"- **Horário:** {start_time} → {end_time}\n"
            if location:
                markdown_content += f"- **Local:** {location}\n"
            if description:
                markdown_content += f"- **Descrição:** {description[:100]}...\n"
            if html_link:
                markdown_content += f"- **Link:** {html_link}\n"
            markdown_content += "\n"
    else:
        markdown_content += "Nenhum evento futuro encontrado.\n"
    
    markdown_content += "\n---\n"
    markdown_content += "*Sincronizado automaticamente pelo sistema biomimético AI-Biomimetica*"
    
    print("   ✅ Conteúdo Markdown gerado")
    
    # 5. Salvar no Obsidian (se disponível)
    if obsidian:
        print("\n5. 💾 Salvando no Obsidian Vault...")
        try:
            note_data = {
                "title": f"Google Calendar Sync - {datetime.now().strftime('%Y-%m-%d')}",
                "content": markdown_content,
                "tags": ["google-calendar", "percepção-multimodal", "sincronização", "sistema-biomimético"],
                "folder": "CHOKMAH/Calendario"
            }
            
            # Método específico depende da implementação do ObsidianVault
            result = obsidian.save_note(note_data)
            print(f"   ✅ Nota salva no Obsidian: {result}")
            
        except Exception as e:
            print(f"   ⚠️ Erro ao salvar no Obsidian: {e}")
            print("   📝 Exibindo conteúdo que seria salvo:")
            print("\n" + "=" * 60)
            print(markdown_content)
            print("=" * 60)
    else:
        print("\n5. 📄 Exibindo conteúdo gerado (Obsidian não disponível):")
        print("\n" + "=" * 60)
        print(markdown_content)
        print("=" * 60)
    
    # 6. Demonstrando integração com sistema biomimético
    print("\n6. 🧠 Integração com Sistema Biomimético")
    print("\n   Como usar no sistema biomimético principal:")
    
    integration_code = '''
# Exemplo de uso no sistema biomimético
from src.google.google_calendar_client import GoogleCalendarClient
from src.app.obsidian_vault import ObsidianVault

class BiomimeticSystemWithCalendar:
    def __init__(self):
        self.calendar = GoogleCalendarClient()
        self.memory = ObsidianVault()
    
    def perceive_world_state(self):
        """Percepção multimodal: estado atual do mundo via calendário"""
        events = self.calendar.get_today_events()
        
        # Salvar percepção na memória
        perception_note = {
            "title": f"Percepção Calendário - {datetime.now()}",
            "content": f"Eventos hoje: {len(events)}",
            "tags": ["percepção", "calendário", "contexto-mundial"]
        }
        self.memory.save_note(perception_note)
        
        return {
            "calendar_events_today": len(events),
            "upcoming_events": self.calendar.get_upcoming_events(3),
            "perception_timestamp": datetime.now().isoformat()
        }
    
    def schedule_meeting(self, meeting_data):
        """Ação no mundo real: agendar reunião"""
        event = self.calendar.create_event(meeting_data)
        
        # Registrar ação na memória
        action_note = {
            "title": f"Ação: Agendamento Reunião",
            "content": f"Reunião '{meeting_data.get(\'summary\')}' agendada",
            "tags": ["ação", "calendário", "reunião"]
        }
        self.memory.save_note(action_note)
        
        return event
    '''
    
    print("   ```python")
    for line in integration_code.strip().split('\n')[:20]:
        print(f"   {line}")
    print("   ...")
    print("   ```")
    
    print("\n" + "=" * 60)
    print("✅ EXEMPLO DE INTEGRAÇÃO CONCLUÍDO!")
    print("\n📌 Este exemplo demonstra:")
    print("   • Percepção do mundo real via Google Calendar")
    print("   • Memória persistente via Obsidian")
    print("   • Integração completa com sistema biomimético")
    print("   • Fluxo: Percepção → Processamento → Ação → Memória")
    
    return True

if __name__ == "__main__":
    print("🚀 AI-Biomimetica - Exemplo de Integração Google Calendar + Obsidian")
    print("   Fase 6: Percepção Multimodal → Memória Persistente\n")
    
    success = example_integration()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)