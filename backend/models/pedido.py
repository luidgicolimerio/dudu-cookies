from dataclasses import dataclass
from datetime import datetime

@dataclass
class Pedido:
    id: int = None
    cliente_id: int = None
    cookie_id: int = None
    quantidade: int = 0
    data_pedido: datetime = None
    
    def __post_init__(self):
        if self.data_pedido is None:
            self.data_pedido = datetime.now()
    
    def valor_total(self, cookie_preco: float) -> float:
        return cookie_preco * self.quantidade