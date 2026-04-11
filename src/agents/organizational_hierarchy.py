"""
Sistema de Hierarquia Organizacional
Fase 9: Contexto Empresarial - Entendimento de Hierarquias

Autor: Jarvis (OpenClaw)
Data: 2026-04-11

Objetivo:
- Mapear estrutura organizacional (departamentos, cargos, níveis)
- Entender relações de reporte (quem reporta a quem)
- Calcular distância hierárquica entre indivíduos
- Determinar formalidade apropriada baseada em hierarquia
- Integrar com sistema de etiqueta para reuniões

Funcionalidades:
- Importar estrutura organizacional de múltiplas fontes (CSV, API, manual)
- Consultar relações hierárquicas
- Determinar nível de autoridade
- Sugerir protocolos de comunicação baseados em hierarquia
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class EmployeeRole(Enum):
    """Cargos organizacionais típicos"""
    CEO = "ceo"
    CTO = "cto"
    CFO = "cfo"
    COO = "coo"
    VP = "vp"
    DIRECTOR = "director"
    SENIOR_MANAGER = "senior_manager"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"
    SENIOR_ENGINEER = "senior_engineer"
    ENGINEER = "engineer"
    ANALYST = "analyst"
    INTERN = "intern"
    CONTRACTOR = "contractor"
    EXTERNAL = "external"

@dataclass
class Employee:
    """Representa um funcionário na hierarquia"""
    id: str
    name: str
    email: str
    role: EmployeeRole
    department: str
    manager_id: Optional[str] = None
    direct_reports: List[str] = field(default_factory=list)
    level: int = 0  # 0 = CEO, maior número = mais baixo
    start_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role.value,
            'department': self.department,
            'manager_id': self.manager_id,
            'direct_reports': self.direct_reports,
            'level': self.level,
            'start_date': self.start_date,
            'tags': self.tags
        }

@dataclass
class Department:
    """Representa um departamento"""
    id: str
    name: str
    head_id: Optional[str] = None
    member_ids: List[str] = field(default_factory=list)
    parent_department_id: Optional[str] = None
    child_department_ids: List[str] = field(default_factory=list)

class OrganizationalHierarchy:
    """Sistema de hierarquia organizacional"""
    
    def __init__(self, data_source: Optional[str] = None):
        """
        Inicializa hierarquia organizacional.
        
        Args:
            data_source: Caminho para arquivo de dados (JSON/CSV) ou None para vazio
        """
        self.employees: Dict[str, Employee] = {}
        self.departments: Dict[str, Department] = {}
        self.ceo_id: Optional[str] = None
        
        if data_source:
            self.load_from_source(data_source)
        
        logger.info(f"✅ OrganizationalHierarchy inicializado com {len(self.employees)} funcionários")
    
    def load_from_source(self, data_source: str):
        """
        Carrega dados organizacionais de uma fonte.
        
        Args:
            data_source: Caminho para arquivo JSON/CSV
        """
        try:
            path = Path(data_source)
            if not path.exists():
                logger.warning(f"⚠️  Arquivo de dados não encontrado: {data_source}")
                return
            
            if path.suffix.lower() == '.json':
                self._load_from_json(path)
            elif path.suffix.lower() == '.csv':
                self._load_from_csv(path)
            else:
                logger.error(f"❌ Formato não suportado: {path.suffix}")
        
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {e}")
    
    def _load_from_json(self, path: Path):
        """Carrega dados de arquivo JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Carregar funcionários
        if 'employees' in data:
            for emp_data in data['employees']:
                try:
                    employee = Employee(
                        id=emp_data['id'],
                        name=emp_data['name'],
                        email=emp_data['email'],
                        role=EmployeeRole(emp_data['role']),
                        department=emp_data['department'],
                        manager_id=emp_data.get('manager_id'),
                        direct_reports=emp_data.get('direct_reports', []),
                        level=emp_data.get('level', 0),
                        start_date=emp_data.get('start_date'),
                        tags=emp_data.get('tags', [])
                    )
                    self.employees[employee.id] = employee
                    
                    # Identificar CEO
                    if employee.role == EmployeeRole.CEO:
                        self.ceo_id = employee.id
                        
                except Exception as e:
                    logger.warning(f"⚠️  Erro ao carregar funcionário {emp_data.get('id')}: {e}")
        
        # Carregar departamentos
        if 'departments' in data:
            for dept_data in data['departments']:
                try:
                    department = Department(
                        id=dept_data['id'],
                        name=dept_data['name'],
                        head_id=dept_data.get('head_id'),
                        member_ids=dept_data.get('member_ids', []),
                        parent_department_id=dept_data.get('parent_department_id'),
                        child_department_ids=dept_data.get('child_department_ids', [])
                    )
                    self.departments[department.id] = department
                except Exception as e:
                    logger.warning(f"⚠️  Erro ao carregar departamento {dept_data.get('id')}: {e}")
        
        # Calcular níveis hierárquicos se não fornecidos
        self._calculate_hierarchy_levels()
        
        logger.info(f"✅ Dados carregados: {len(self.employees)} funcionários, {len(self.departments)} departamentos")
    
    def _load_from_csv(self, path: Path):
        """Carrega dados de arquivo CSV (simplificado)"""
        # Implementação básica - em produção seria mais completa
        import csv
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    employee = Employee(
                        id=row['id'],
                        name=row['name'],
                        email=row['email'],
                        role=EmployeeRole(row['role'].lower()),
                        department=row['department'],
                        manager_id=row.get('manager_id') or None,
                        direct_reports=row.get('direct_reports', '').split(';') if row.get('direct_reports') else [],
                        level=int(row.get('level', 0)),
                        start_date=row.get('start_date'),
                        tags=row.get('tags', '').split(';') if row.get('tags') else []
                    )
                    self.employees[employee.id] = employee
                    
                    if employee.role == EmployeeRole.CEO:
                        self.ceo_id = employee.id
                        
                except Exception as e:
                    logger.warning(f"⚠️  Erro ao carregar funcionário da linha CSV: {e}")
        
        self._calculate_hierarchy_levels()
    
    def _calculate_hierarchy_levels(self):
        """Calcula níveis hierárquicos baseados na estrutura de reporte"""
        if not self.ceo_id:
            # Tentar encontrar CEO
            for emp in self.employees.values():
                if emp.role == EmployeeRole.CEO:
                    self.ceo_id = emp.id
                    break
        
        if not self.ceo_id:
            logger.warning("⚠️  CEO não encontrado. Definindo primeiro funcionário como nível 0.")
            if self.employees:
                first_emp = list(self.employees.values())[0]
                first_emp.level = 0
                self.ceo_id = first_emp.id
            return
        
        # Inicializar todos os níveis como -1 (não calculado)
        for emp in self.employees.values():
            emp.level = -1
        
        # Definir CEO como nível 0
        self.employees[self.ceo_id].level = 0
        
        # Calcular níveis usando BFS (busca em largura)
        queue = [self.ceo_id]
        
        while queue:
            current_id = queue.pop(0)
            current_emp = self.employees[current_id]
            
            # Atribuir nível para subordinados diretos
            for report_id in current_emp.direct_reports:
                if report_id in self.employees:
                    report_emp = self.employees[report_id]
                    if report_emp.level == -1 or report_emp.level > current_emp.level + 1:
                        report_emp.level = current_emp.level + 1
                        queue.append(report_id)
        
        # Verificar se algum funcionário não foi alcançado
        unreached = [emp for emp in self.employees.values() if emp.level == -1]
        if unreached:
            logger.warning(f"⚠️  {len(unreached)} funcionários não alcançados na hierarquia")
    
    def add_employee(self, employee: Employee):
        """Adiciona funcionário à hierarquia"""
        self.employees[employee.id] = employee
        
        # Atualizar CEO se necessário
        if employee.role == EmployeeRole.CEO:
            self.ceo_id = employee.id
        
        logger.info(f"✅ Funcionário adicionado: {employee.name} ({employee.role.value})")
    
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """Obtém funcionário por ID"""
        return self.employees.get(employee_id)
    
    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Obtém funcionário por email"""
        for emp in self.employees.values():
            if emp.email.lower() == email.lower():
                return emp
        return None
    
    def get_manager_chain(self, employee_id: str) -> List[Employee]:
        """
        Obtém cadeia de comando de um funcionário até o CEO.
        
        Args:
            employee_id: ID do funcionário
            
        Returns:
            Lista de funcionários do funcionário até o CEO (inclusive)
        """
        chain = []
        current_id = employee_id
        
        while current_id and current_id in self.employees:
            emp = self.employees[current_id]
            chain.append(emp)
            current_id = emp.manager_id
        
        return chain
    
    def get_hierarchical_distance(self, emp1_id: str, emp2_id: str) -> Optional[int]:
        """
        Calcula distância hierárquica entre dois funcionários.
        
        Args:
            emp1_id: ID do primeiro funcionário
            emp2_id: ID do segundo funcionário
            
        Returns:
            Distância em níveis, ou None se não conectados
        """
        if emp1_id not in self.employees or emp2_id not in self.employees:
            return None
        
        # Obter cadeias até o CEO
        chain1 = self.get_manager_chain(emp1_id)
        chain2 = self.get_manager_chain(emp2_id)
        
        # Encontrar ancestral comum mais próximo
        for i, emp1 in enumerate(chain1):
            for j, emp2 in enumerate(chain2):
                if emp1.id == emp2.id:
                    return i + j  # Distância total
        
        return None  # Sem ancestral comum
    
    def get_communication_formality(self, from_emp_id: str, to_emp_id: str) -> str:
        """
        Determina nível de formalidade para comunicação baseada em hierarquia.
        
        Args:
            from_emp_id: ID do remetente
            to_emp_id: ID do destinatário
            
        Returns:
            'high', 'medium', ou 'low'
        """
        if from_emp_id not in self.employees or to_emp_id not in self.employees:
            return 'medium'
        
        from_emp = self.employees[from_emp_id]
        to_emp = self.employees[to_emp_id]
        
        # Se mesmo nível ou colegas
        if from_emp.level == to_emp.level:
            return 'low'
        
        # Se destinatário é superior (mais alto = nível menor)
        if to_emp.level < from_emp.level:
            difference = from_emp.level - to_emp.level
            
            if difference >= 3:  # Muitos níveis acima
                return 'high'
            elif difference >= 2:
                return 'medium'
            else:
                return 'low'
        
        # Se destinatário é subordinado
        else:
            return 'low'
    
    def get_department_members(self, department_id: str) -> List[Employee]:
        """Obtém membros de um departamento"""
        if department_id not in self.departments:
            return []
        
        dept = self.departments[department_id]
        members = []
        
        for emp_id in dept.member_ids:
            if emp_id in self.employees:
                members.append(self.employees[emp_id])
        
        return members
    
    def find_common_manager(self, emp_ids: List[str]) -> Optional[Employee]:
        """
        Encontra gerente comum mais próximo para uma lista de funcionários.
        
        Args:
            emp_ids: Lista de IDs de funcionários
            
        Returns:
            Gerente comum ou None
        """
        if not emp_ids:
            return None
        
        # Obter cadeias de comando para cada funcionário
        chains = []
        for emp_id in emp_ids:
            if emp_id in self.employees:
                chain = self.get_manager_chain(emp_id)
                chain_ids = [emp.id for emp in chain]
                chains.append(chain_ids)
        
        if not chains:
            return None
        
        # Encontrar interseção (ancestrais comuns)
        common = set(chains[0])
        for chain in chains[1:]:
            common.intersection_update(chain)
        
        if not common:
            return None
        
        # Retornar o mais próximo (menor nível)
        common_managers = [self.employees[emp_id] for emp_id in common]
        return min(common_managers, key=lambda x: x.level)
    
    def export_to_json(self, filepath: str):
        """Exporta hierarquia para arquivo JSON"""
        data = {
            'employees': [emp.to_dict() for emp in self.employees.values()],
            'departments': [
                {
                    'id': dept.id,
                    'name': dept.name,
                    'head_id': dept.head_id,
                    'member_ids': dept.member_ids,
                    'parent_department_id': dept.parent_department_id,
                    'child_department_ids': dept.child_department_ids
                }
                for dept in self.departments.values()
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Hierarquia exportada para {filepath}")

def create_organizational_hierarchy(data_source: Optional[str] = None) -> OrganizationalHierarchy:
    """
    Factory function para criar hierarquia organizacional.
    
    Args:
        data_source: Caminho para arquivo de dados (opcional)
        
    Returns:
        Instância do OrganizationalHierarchy
    """
    return OrganizationalHierarchy(data_source)