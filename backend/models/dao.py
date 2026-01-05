import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from datetime import datetime, timedelta
from models.cliente import Cliente
from models.cookie import Cookie
from models.pedido import Pedido
from config import Config

class DAO:
    def __init__(self):
        self.config = Config()
        self._init_db()
    
    def _get_connection(self):
        return psycopg2.connect(self.config.database_url)
    
    def _init_db(self):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clientes (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(255) NOT NULL,
                        telefone VARCHAR(20),
                        local VARCHAR(255)
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cookies (
                        id SERIAL PRIMARY KEY,
                        sabor VARCHAR(100) NOT NULL UNIQUE,
                        preco DECIMAL(10,2) NOT NULL,
                        custo DECIMAL(10,2) NOT NULL
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pedidos (
                        id SERIAL PRIMARY KEY,
                        cliente_id INTEGER NOT NULL,
                        cookie_id INTEGER NOT NULL,
                        quantidade INTEGER NOT NULL,
                        data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                        FOREIGN KEY (cookie_id) REFERENCES cookies (id)
                    )
                ''')
            conn.commit()
    
    # Cliente operations
    def criar_cliente(self, cliente: Cliente) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO clientes (nome, telefone, local) VALUES (%s, %s, %s) RETURNING id",
                    (cliente.nome, cliente.telefone, cliente.local)
                )
                return cursor.fetchone()[0]
    
    def obter_cliente(self, cliente_id: int) -> Optional[Cliente]:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
                row = cursor.fetchone()
                if row:
                    return Cliente(id=row[0], nome=row[1], telefone=row[2], local=row[3])
        return None
    
    def listar_clientes(self) -> List[Cliente]:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM clientes")
                return [Cliente(id=row[0], nome=row[1], telefone=row[2], local=row[3]) 
                       for row in cursor.fetchall()]
    
    # Cookie operations
    def criar_cookie(self, cookie: Cookie) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO cookies (sabor, preco, custo) VALUES (%s, %s, %s) RETURNING id",
                    (cookie.sabor, cookie.preco, cookie.custo)
                )
                return cursor.fetchone()[0]
    
    def obter_cookie(self, cookie_id: int) -> Optional[Cookie]:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM cookies WHERE id = %s", (cookie_id,))
                row = cursor.fetchone()
                if row:
                    return Cookie(id=row[0], sabor=row[1], preco=float(row[2]), custo=float(row[3]))
        return None
    
    def listar_cookies(self) -> List[Cookie]:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM cookies")
                return [Cookie(id=row[0], sabor=row[1], preco=float(row[2]), custo=float(row[3])) 
                       for row in cursor.fetchall()]
    
    # Pedido operations
    def criar_pedido(self, pedido: Pedido) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO pedidos (cliente_id, cookie_id, quantidade, data_pedido) VALUES (%s, %s, %s, %s) RETURNING id",
                    (pedido.cliente_id, pedido.cookie_id, pedido.quantidade, pedido.data_pedido)
                )
                return cursor.fetchone()[0]
    
    def listar_pedidos_semana(self, data_inicio: datetime, data_fim: datetime) -> List[dict]:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT p.id, c.nome, ck.sabor, p.quantidade, ck.preco, ck.custo, p.data_pedido
                    FROM pedidos p
                    JOIN clientes c ON p.cliente_id = c.id
                    JOIN cookies ck ON p.cookie_id = ck.id
                    WHERE p.data_pedido BETWEEN %s AND %s
                ''', (data_inicio, data_fim))
                
                return [{
                    'pedido_id': row[0],
                    'cliente_nome': row[1],
                    'cookie_sabor': row[2],
                    'quantidade': row[3],
                    'preco_unitario': float(row[4]),
                    'custo_unitario': float(row[5]),
                    'data_pedido': row[6],
                    'valor_total': row[3] * float(row[4]),
                    'custo_total': row[3] * float(row[5]),
                    'lucro_total': row[3] * (float(row[4]) - float(row[5]))
                } for row in cursor.fetchall()]
    
    def relatorio_semanal(self, data_inicio: datetime, data_fim: datetime) -> dict:
        pedidos = self.listar_pedidos_semana(data_inicio, data_fim)
        
        total_valor = sum(p['valor_total'] for p in pedidos)
        total_custo = sum(p['custo_total'] for p in pedidos)
        total_lucro = total_valor - total_custo
        total_quantidade = sum(p['quantidade'] for p in pedidos)
        
        # Agrupar por sabor
        sabores = {}
        clientes = set()
        
        for pedido in pedidos:
            sabor = pedido['cookie_sabor']
            if sabor not in sabores:
                sabores[sabor] = 0
            sabores[sabor] += pedido['quantidade']
            clientes.add(pedido['cliente_nome'])
        
        return {
            'total_valor': total_valor,
            'total_custo': total_custo,
            'total_lucro': total_lucro,
            'total_quantidade': total_quantidade,
            'quantidade_clientes': len(clientes),
            'sabores': sabores,
            'pedidos': pedidos
        }