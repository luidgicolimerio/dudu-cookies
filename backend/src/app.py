from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório models ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.dao import DAO
from models.cliente import Cliente
from models.cookie import Cookie
from models.pedido import Pedido

app = Flask(__name__)
dao = DAO()

@app.route('/clientes', methods=['POST'])
def criar_cliente():
    data = request.json
    cliente = Cliente(
        nome=data['nome'],
        telefone=data.get('telefone', ''),
        local=data.get('local', '')
    )
    cliente_id = dao.criar_cliente(cliente)
    return jsonify({'id': cliente_id, 'message': 'Cliente criado com sucesso'}), 201

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    clientes = dao.listar_clientes()
    return jsonify([{
        'id': c.id,
        'nome': c.nome,
        'telefone': c.telefone,
        'local': c.local
    } for c in clientes])

@app.route('/cookies', methods=['POST'])
def criar_cookie():
    data = request.json
    cookie = Cookie(
        sabor=data['sabor'],
        preco=float(data['preco']),
        custo=float(data['custo'])
    )
    cookie_id = dao.criar_cookie(cookie)
    return jsonify({'id': cookie_id, 'message': 'Cookie criado com sucesso'}), 201

@app.route('/cookies', methods=['GET'])
def listar_cookies():
    cookies = dao.listar_cookies()
    return jsonify([{
        'id': c.id,
        'sabor': c.sabor,
        'preco': c.preco,
        'custo': c.custo,
        'lucro': c.lucro
    } for c in cookies])

@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    data = request.json
    pedido = Pedido(
        cliente_id=int(data['cliente_id']),
        cookie_id=int(data['cookie_id']),
        quantidade=int(data['quantidade'])
    )
    pedido_id = dao.criar_pedido(pedido)
    return jsonify({'id': pedido_id, 'message': 'Pedido criado com sucesso'}), 201

@app.route('/relatorio/semanal', methods=['GET'])
def relatorio_semanal():
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    if not data_inicio_str or not data_fim_str:
        return jsonify({'error': 'Parâmetros data_inicio e data_fim são obrigatórios (formato: YYYY-MM-DD)'}), 400
    
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
    
    relatorio = dao.relatorio_semanal(data_inicio, data_fim)
    return jsonify(relatorio)

@app.route('/inicializar', methods=['POST'])
def inicializar_dados():
    """Rota para inicializar dados de exemplo"""
    # Criar cookies padrão
    cookies_padrao = [
        Cookie(sabor="Nutella", preco=4.0, custo=1.70),
        Cookie(sabor="Mil Gotas", preco=4.0, custo=1.30),
        Cookie(sabor="Ninho", preco=4.0, custo=1.90),
        Cookie(sabor="Red", preco=3.5, custo=1.00),
        Cookie(sabor="Tradicional", preco=3.5, custo=1.00)
    ]
    
    for cookie in cookies_padrao:
        try:
            dao.criar_cookie(cookie)
        except:
            pass  # Cookie já existe
    
    return jsonify({'message': 'Dados inicializados com sucesso'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)