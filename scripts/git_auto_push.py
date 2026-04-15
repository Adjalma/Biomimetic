#!/usr/bin/env python3
"""
Script de Auto-Push para GitHub

Automaticamente commita e pusha mudanças para o repositório remoto.
Uso: python3 scripts/git_auto_push.py [mensagem personalizada]

Se nenhuma mensagem for fornecida, gera uma mensagem automática baseada nas mudanças.

Configuração recomendada:
1. Adicione ao PATH
2. Execute após implementações significativas
3. Ou configure como hook pós-commit (não implementado aqui)

Autor: Jarvis (OpenClaw)
Data: 2026-04-15
Versão: 1.0.0
"""

import os
import sys
import subprocess
import datetime
import re
from pathlib import Path
from typing import List, Tuple, Optional

class GitAutoPusher:
    """Classe para gerenciar push automático para GitHub"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.git_cmd = ["git"]
        
    def run_git(self, args: List[str], capture: bool = True) -> Tuple[bool, str]:
        """Executa comando git"""
        cmd = self.git_cmd + args
        try:
            if capture:
                result = subprocess.run(
                    cmd, 
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode == 0, result.stdout.strip()
            else:
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    timeout=30
                )
                return result.returncode == 0, ""
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
    
    def has_changes(self) -> bool:
        """Verifica se há mudanças não commitadas"""
        success, output = self.run_git(["status", "--porcelain"])
        if not success:
            return False
        return len(output.strip()) > 0
    
    def get_changes_summary(self) -> str:
        """Obtém resumo das mudanças"""
        success, output = self.run_git(["status", "--porcelain"])
        if not success or not output:
            return "Nenhuma mudança detectada"
        
        lines = output.strip().split('\n')
        file_count = len(lines)
        
        # Categorizar mudanças
        added = []
        modified = []
        deleted = []
        untracked = []
        
        for line in lines:
            if line.startswith('??'):
                untracked.append(line[3:].strip())
            elif line.startswith('D'):
                deleted.append(line[3:].strip())
            elif line.startswith('M') or line.startswith('A'):
                filename = line[3:].strip()
                if line.startswith('A'):
                    added.append(filename)
                else:
                    modified.append(filename)
        
        summary = []
        if added:
            summary.append(f"{len(added)} arquivo(s) novo(s)")
        if modified:
            summary.append(f"{len(modified)} arquivo(s) modificado(s)")
        if deleted:
            summary.append(f"{len(deleted)} arquivo(s) removido(s)")
        if untracked:
            summary.append(f"{len(untracked)} arquivo(s) não rastreado(s)")
        
        return f"{file_count} mudanças: {', '.join(summary)}"
    
    def should_add_file(self, filepath: str) -> bool:
        """Decide se um arquivo deve ser adicionado ao commit"""
        path = Path(filepath)
        
        # Lista de padrões para ignorar
        ignore_patterns = [
            # Dados gerados
            r'\.log$',
            r'\.csv$',
            r'\.jsonl$',
            r'\.pkl$',
            r'\.pickle$',
            r'\.npy$',
            r'\.npz$',
            # Diretórios de dados
            r'^data/demo_dashboard/',
            r'^data/integrated_demo/',
            r'^data/logs/',
            r'^data/temp/',
            # Configurações locais
            r'^\.env$',
            r'^\.env\.local$',
            r'^\.env\.evolution$',
            r'^bio_console\.env$',
            # Cache e temporários
            r'^__pycache__/',
            r'\.pyc$',
            r'\.pyo$',
            r'\.pyd$',
            r'^\.pytest_cache/',
            r'^\.mypy_cache/',
        ]
        
        filename = str(path)
        for pattern in ignore_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return False
        
        # Verificar se está no .gitignore
        success, output = self.run_git(["check-ignore", filename])
        if success and output:
            return False
        
        return True
    
    def add_changes(self) -> Tuple[bool, str]:
        """Adiciona mudanças cuidadosamente"""
        # Primeiro verifica quais arquivos têm mudanças
        success, output = self.run_git(["status", "--porcelain"])
        if not success:
            return False, "Falha ao verificar status"
        
        if not output:
            return True, "Nenhuma mudança para adicionar"
        
        lines = output.strip().split('\n')
        files_to_add = []
        
        for line in lines:
            status = line[:2].strip()
            filepath = line[3:].strip()
            
            # Ignorar arquivos deletados (serão rastreados automaticamente)
            if status == 'D':
                continue
                
            if self.should_add_file(filepath):
                files_to_add.append(filepath)
        
        if not files_to_add:
            return True, "Nenhum arquivo qualificado para commit"
        
        # Adicionar arquivos selecionados
        for filepath in files_to_add:
            success, output = self.run_git(["add", filepath])
            if not success:
                return False, f"Falha ao adicionar {filepath}: {output}"
        
        return True, f"Adicionados {len(files_to_add)} arquivo(s)"
    
    def create_commit_message(self, custom_message: Optional[str] = None) -> str:
        """Cria mensagem de commit"""
        if custom_message:
            return custom_message
        
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        changes_summary = self.get_changes_summary()
        
        # Detectar tipo de mudança para prefixo
        prefix = "🔧"
        success, output = self.run_git(["status", "--porcelain"])
        if success and output:
            files = output.lower()
            if any(x in files for x in ['.py', 'src/', 'core/']):
                prefix = "🧬"
            elif any(x in files for x in ['.md', 'docs/', 'readme']):
                prefix = "📝"
            elif any(x in files for x in ['.json', '.yaml', '.yml', 'config']):
                prefix = "⚙️"
            elif any(x in files for x in ['.txt', 'requirements', 'dependencies']):
                prefix = "📦"
        
        # Gerar mensagem
        message = f"{prefix} Auto-commit: {changes_summary}\n\n"
        message += f"Timestamp: {timestamp}\n"
        message += "Auto-generated by Jarvis (OpenClaw)\n\n"
        message += "Detalhes das mudanças:\n"
        
        # Adicionar lista de arquivos (limitada)
        success, output = self.run_git(["status", "--porcelain"])
        if success and output:
            lines = output.strip().split('\n')[:10]  # Limitar a 10 arquivos
            for line in lines:
                status = line[:2].strip()
                filepath = line[3:].strip()
                if status == '??':
                    message += f"  + {filepath}\n"
                elif status == 'D':
                    message += f"  - {filepath}\n"
                elif status == 'M':
                    message += f"  ~ {filepath}\n"
                elif status == 'A':
                    message += f"  + {filepath}\n"
            
            total_files = len(output.strip().split('\n'))
            if total_files > 10:
                message += f"  ... e mais {total_files - 10} arquivo(s)\n"
        
        return message
    
    def commit(self, message: str) -> Tuple[bool, str]:
        """Executa commit"""
        # Primeiro verifica se há algo para commitar
        success, output = self.run_git(["diff", "--cached", "--name-only"])
        if not success or not output.strip():
            return False, "Nada para commitar (nenhum arquivo staged)"
        
        success, output = self.run_git(["commit", "-m", message])
        return success, output
    
    def push(self) -> Tuple[bool, str]:
        """Executa push para origin/main"""
        success, output = self.run_git(["push", "origin", "main"])
        return success, output
    
    def auto_push(self, custom_message: Optional[str] = None) -> Tuple[bool, str]:
        """Executa fluxo completo: add, commit, push"""
        steps = []
        
        # 1. Verificar se há mudanças
        if not self.has_changes():
            return True, "Nenhuma mudança detectada"
        
        steps.append("✅ Verificadas mudanças")
        
        # 2. Adicionar mudanças
        success, msg = self.add_changes()
        if not success:
            return False, f"Falha ao adicionar: {msg}"
        steps.append(f"✅ {msg}")
        
        # 3. Criar mensagem de commit
        commit_msg = self.create_commit_message(custom_message)
        steps.append("✅ Mensagem de commit gerada")
        
        # 4. Commit
        success, output = self.commit(commit_msg)
        if not success:
            return False, f"Falha no commit: {output}"
        steps.append("✅ Commit realizado")
        
        # 5. Push
        success, output = self.push()
        if not success:
            return False, f"Falha no push: {output}"
        steps.append("✅ Push para GitHub realizado")
        
        # 6. Obter hash do commit
        success, hash_output = self.run_git(["rev-parse", "--short", "HEAD"])
        if success:
            steps.append(f"✅ Commit hash: {hash_output}")
        
        return True, "\n".join(steps)

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-push para GitHub')
    parser.add_argument('message', nargs='?', help='Mensagem personalizada para o commit')
    parser.add_argument('--repo', default='.', help='Caminho do repositório (padrão: atual)')
    parser.add_argument('--dry-run', action='store_true', help='Mostra o que seria feito sem executar')
    
    args = parser.parse_args()
    
    print("🚀 Git Auto-Pusher - Jarvis (OpenClaw)")
    print("=" * 50)
    
    pusher = GitAutoPusher(args.repo)
    
    if args.dry_run:
        print("🔍 Modo dry-run (simulação):")
        print(f"  Repositório: {pusher.repo_path}")
        print(f"  Mudanças detectadas: {pusher.has_changes()}")
        if pusher.has_changes():
            print(f"  Resumo: {pusher.get_changes_summary()}")
            print(f"  Mensagem de commit gerada:")
            print("-" * 40)
            print(pusher.create_commit_message(args.message))
            print("-" * 40)
        return 0
    
    print(f"📁 Repositório: {pusher.repo_path}")
    print(f"🌿 Branch: main (origin/main)")
    print()
    
    success, result = pusher.auto_push(args.message)
    
    if success:
        print("🎉 Auto-push concluído com sucesso!")
        print()
        print(result)
    else:
        print("❌ Falha no auto-push:")
        print()
        print(result)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())