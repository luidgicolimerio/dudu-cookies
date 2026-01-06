import streamlit as st
import requests
from datetime import datetime, timedelta

API_BASE = "https://dudu-cookies.vercel.app"

st.title("🍪 Sistema de Controle de Cookies")

# Sidebar para navegação
menu = st.sidebar.selectbox("Menu", ["Clientes", "Cookies", "Pedidos", "Relatório Semanal"])

if menu == "Clientes":
    st.header("Gerenciar Clientes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cadastrar Cliente")
        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone")
        local = st.text_input("Local")
        
        if st.button("Cadastrar"):
            data = {"nome": nome, "telefone": telefone, "local": local}
            response = requests.post(f"{API_BASE}/clientes", json=data)
            if response.status_code == 201:
                st.success("Cliente cadastrado com sucesso!")
            else:
                st.error("Erro ao cadastrar cliente")
    
    with col2:
        st.subheader("Lista de Clientes")
        if st.button("Atualizar Lista"):
            response = requests.get(f"{API_BASE}/clientes")
            if response.status_code == 200:
                clientes = response.json()
                for cliente in clientes:
                    st.write(f"**{cliente['nome']}** - {cliente['telefone']} - {cliente['local']}")

elif menu == "Cookies":
    st.header("Gerenciar Cookies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cadastrar Cookie")
        sabor = st.text_input("Sabor")
        preco = st.number_input("Preço (R$)", min_value=0.0, step=0.01)
        custo = st.number_input("Custo (R$)", min_value=0.0, step=0.01)
        
        if st.button("Cadastrar Cookie"):
            data = {"sabor": sabor, "preco": preco, "custo": custo}
            response = requests.post(f"{API_BASE}/cookies", json=data)
            if response.status_code == 201:
                st.success("Cookie cadastrado com sucesso!")
            else:
                st.error("Erro ao cadastrar cookie")
    
    with col2:
        st.subheader("Lista de Cookies")
        if st.button("Atualizar Cookies"):
            response = requests.get(f"{API_BASE}/cookies")
            if response.status_code == 200:
                cookies = response.json()
                for cookie in cookies:
                    st.write(f"**{cookie['sabor']}** - R${cookie['preco']:.2f} (Lucro: R${cookie['lucro']:.2f})")

elif menu == "Pedidos":
    st.header("Criar Pedido")
    
    # Carregar clientes e cookies
    clientes_response = requests.get(f"{API_BASE}/clientes")
    cookies_response = requests.get(f"{API_BASE}/cookies")
    
    if clientes_response.status_code == 200 and cookies_response.status_code == 200:
        clientes = clientes_response.json()
        cookies = cookies_response.json()
        
        cliente_opcoes = {f"{c['nome']} ({c['id']})": c['id'] for c in clientes}
        cookie_opcoes = {f"{c['sabor']} - R${c['preco']:.2f} ({c['id']})": c['id'] for c in cookies}
        
        cliente_selecionado = st.selectbox("Cliente", list(cliente_opcoes.keys()))
        cookie_selecionado = st.selectbox("Cookie", list(cookie_opcoes.keys()))
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        
        if st.button("Criar Pedido"):
            data = {
                "cliente_id": cliente_opcoes[cliente_selecionado],
                "cookie_id": cookie_opcoes[cookie_selecionado],
                "quantidade": quantidade
            }
            response = requests.post(f"{API_BASE}/pedidos", json=data)
            if response.status_code == 201:
                st.success("Pedido criado com sucesso!")
            else:
                st.error("Erro ao criar pedido")

elif menu == "Relatório Semanal":
    st.header("Relatório Semanal")
    
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início")
    with col2:
        data_fim = st.date_input("Data Fim")
    
    if st.button("Gerar Relatório"):
        params = {
            "data_inicio": data_inicio.strftime("%Y-%m-%d"),
            "data_fim": data_fim.strftime("%Y-%m-%d")
        }
        response = requests.get(f"{API_BASE}/relatorio/semanal", params=params)
        
        if response.status_code == 200:
            relatorio = response.json()
            
            st.subheader("Resumo da Semana")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Vendas", f"R$ {relatorio['total_valor']:.2f}")
            with col2:
                st.metric("Total Custos", f"R$ {relatorio['total_custo']:.2f}")
            with col3:
                st.metric("Lucro", f"R$ {relatorio['total_lucro']:.2f}")
            with col4:
                st.metric("Quantidade", f"{relatorio['total_quantidade']} un")
            
            st.subheader("Por Sabor")
            for sabor, qtd in relatorio['sabores'].items():
                st.write(f"**{sabor}**: {qtd} unidades")
            
            st.subheader("Pedidos Detalhados")
            for pedido in relatorio['pedidos']:
                st.write(f"{pedido['cliente_nome']} - {pedido['cookie_sabor']} - {pedido['quantidade']}un - R${pedido['valor_total']:.2f}")

# Botão para inicializar dados
if st.sidebar.button("Inicializar Dados"):
    response = requests.post(f"{API_BASE}/inicializar")
    if response.status_code == 200:
        st.sidebar.success("Dados inicializados!")
    else:
        st.sidebar.error("Erro ao inicializar")