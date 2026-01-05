from dataclasses import dataclass

@dataclass
class Cookie:
    id: int = None
    sabor: str = ""
    preco: float = 0.0
    custo: float = 0.0
    
    @property
    def lucro(self) -> float:
        return self.preco - self.custo