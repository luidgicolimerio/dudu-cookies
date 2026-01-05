from dataclasses import dataclass

@dataclass
class Cliente:
    id: int = None
    nome: str = ""
    telefone: str = ""
    local: str = ""