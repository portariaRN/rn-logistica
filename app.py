import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

# Configuração da página e identidade visual da RN LOGÍSTICA
st.set_page_config(page_title="RN LOGISTICA", page_icon="🚚", layout="wide")

# Estilização da Logo da Marca
st.markdown(
    """
    <h1 style='text-align: center; font-family: sans-serif; margin-bottom: 5px;'>
        <span style='color: #004AAD; font-size: 55px; font-weight: bold;'>R</span><span style='color: #FF0000; font-size: 55px; font-weight: bold;'>N</span> 
        <span style='color: #333333; font-size: 40px; font-weight: 300; letter-spacing: 2px;'>LOGÍSTICA</span>
    </h1>
    <p style='text-align: center; color: #666666; font-size: 14px; margin-bottom: 30px;'>Sistema Integrado Multiplataforma v2.0</p>
    """, 
    unsafe_allow_html=True
)

# Caminhos dos arquivos de persistência de dados
ARQUIVO_CADASTROS = "cadastros_rn.csv"
ARQUIVO_PORTARIA = "portaria_rn.csv"

# Inicialização síncrona dos arquivos
if os.path.exists(ARQUIVO_CADASTROS):
    df_cadastros = pd.read_csv(ARQUIVO_CADASTROS)
else:
    df_cadastros = pd.DataFrame(columns=['ID', 'Tipo', 'Nome_Razao', 'Documento', 'Contato_Placa'])

if os.path.exists(ARQUIVO_PORTARIA):
    df_portaria = pd.read_csv(ARQUIVO_PORTARIA)
else:
    df_portaria = pd.DataFrame(columns=['Data_Hora', 'Usuario', 'Tipo_Fluxo', 'Categoria', 'Nome_Condutor', 'Identificacao_Placa', 'Motivo_Destino', 'Status_Mercadoria', 'Avarias_Checklist'])

# --- MELHORIA 1: SISTEMA DE LOGIN E CONTROLE DE ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['perfil'] = None
    st.session_state['usuario_logado'] = ""

if not st.session_state['autenticado']:
    st.subheader("🔒 Autenticação de Usuário")
    col_l1, col_l2 = st.columns([1, 2])
    with col_l1:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Acessar Sistema", use_container_width=True):
            if usuario.lower() == "portaria" and senha == "rn123":
                st.session_state['autenticado'] = True
                st.session_state['perfil'] = "Portaria"
                st.session_state['usuario_logado'] = "Portaria"
                st.success("Logado com sucesso!")
                st.rerun()
            elif usuario.lower() == "gerente" and senha == "master_rn":
                st.session_state['autenticado'] = True
                st.session_state['perfil'] = "Gerente"
                st.session_state['usuario_logado'] = "Gerente Logística"
                st.success("Logado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas! Use portaria/rn123 ou gerente/master_rn")
    st.stop()

# Barra lateral com dados de login e botão de logout
with st.sidebar:
    st.write(f"👤 **Operador:** {st.session_state['usuario_logado']}")
    st.write(f"🛡️ **Nível:** {st.session_state['perfil']}")
    if st.button("Sair / Logout"):
        st.session_state['autenticado'] = False
        st.session_state['perfil'] = None
        st.rerun()

# Restrição e construção das Abas com base no perfil logado
if st.session_state['perfil'] == "Gerente":
    abas = st.tabs(["🚧 Controle de Portaria", "📦 Mercadorias & Cargas", "👥 Cadastros Gerais", "📊 Relatórios e Excel"])
else:
    # Perfil Portaria não visualiza cadastros nem relatórios gerenciais estruturados
    abas = st.tabs(["🚧 Controle de Portaria", "📦 Mercadorias & Cargas"])

# ----------------- ABA: CONTROLE DE PORTARIA -----------------
with abas[0]:
    st.header("Fluxo Operacional de Entrada e Saída")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Registrar Movimentação")
        tipo_fluxo = st.radio("Operação", ["ENTRADA", "SAÍDA"], horizontal=True)
        categoria = st.selectbox("Categoria", ["Veículo Frota Própria", "Prestador/Agregado", "Funcionário", "Visitante"])
        nome_portaria = st.text_input("Nome do Condutor / Pessoa")
        id_portaria = st.text_input("Placa do Veículo ou RG/CPF")
        motivo = st.text_input("Motivo da Visita / Destino")
        
        # --- MELHORIA 2: CHECK-LIST DE AVARIAS INTEGRADO ---
        avarias_selecionadas = []
        if "Veículo" in categoria or "Agregado" in categoria:
            st.markdown("**🔍 Vistoria / Check-list de Avarias Visual**")
            pneus = st.checkbox("Problema nos Pneus / Rodas")
            vidros = st.checkbox("Trincas ou Danos nos Vidros")
            funilaria = st.checkbox("Amassados ou Riscos na Funilaria")
            farois = st.checkbox("Faróis / Lanternas Quebradas")
            
            if pneus: avarias_selecionadas.append("Pneus Danificados")
            if vidros: avarias_selecionadas.append("Vidro Trincado")
            if funilaria: avarias_selecionadas.append("Avaria Funilaria")
            if farois: avarias_selecionadas.append("Lanterna/Farol Defeituoso")
        
        txt_avarias = ", ".join(avarias_selecionadas) if avarias_selecionadas else "Nenhuma Avaria Detectada"
        
        if st.button("Confirmar Registro", use_container_width=True):
            if nome_portaria and id_portaria:
                novo_fluxo = pd.DataFrame([{
                    'Data_Hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'Usuario': st.session_state['usuario_logado'],
                    'Tipo_Fluxo': tipo_fluxo,
                    'Categoria': categoria,
                    'Nome_Condutor': nome_portaria,
                    'Identificacao_Placa': id_portaria,
                    'Motivo_Destino': motivo,
                    'Status_Mercadoria': 'N/A',
                    'Avarias_Checklist': txt_avarias
                }])
                df_portaria = pd.concat([df_portaria, novo_fluxo], ignore_index=True)
                df_portaria.to_csv(ARQUIVO_PORTARIA, index=False)
                st.success("Movimentação e checklist salvos com sucesso!")
                st.rerun()
            else:
                st.error("Campos Nome e Identificação são obrigatórios!")

    with col2:
        st.subheader("Painel de Monitoramento da Portaria")
        st.dataframe(df_portaria, use_container_width=True, hide_index=True)

# ----------------- ABA: MERCADORIAS E CARGAS -----------------
with abas[1]:
    st.header("Recebimento de Mercadorias e Notas Fiscais")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Entrada de Carga / Fornecedor")
        transp_merc = st.text_input("Transportadora / Empresa")
        motorista = st.text_input("Nome do Motorista")
        placa_merc = st.text_input("Placa do Cavalo/Carreta")
        nf_merc = st.text_input("Número da Nota Fiscal (NF-e)")
        
        if st.button("Registrar Carga", use_container_width=True):
            if transp_merc and nf_merc:
                novo_recebimento = pd.DataFrame([{
                    'Data_Hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'Usuario': st.session_state['usuario_logado'],
                    'Tipo_Fluxo': 'ENTRADA CARGA',
                    'Categoria': 'Carga Comercial',
                    'Nome_Condutor': motorista,
                    'Identificacao_Placa': f"{transp_merc} / {placa_merc}",
                    'Motivo_Destino': 'Doca de Descarga',
                    'Status_Mercadoria': f"NF: {nf_merc} - Aguardando Descarregamento",
                    'Avarias_Checklist': "N/A"
                }])
                df_portaria = pd.concat([df_portaria, novo_recebimento], ignore_index=True)
                df_portaria.to_csv(ARQUIVO_PORTARIA, index=False)
                st.success("Carga integrada na fila de triagem!")
                st.rerun()
            else:
                st.error("Informe a Transportadora e a NF!")

    with col2:
        st.subheader("Status das Docas e Cargas em Pátio")
        cargas = df_portaria[df_portaria['Tipo_Fluxo'] == 'ENTRADA CARGA']
        st.dataframe(cargas[['Data_Hora', 'Identificacao_Placa', 'Nome_Condutor', 'Status_Mercadoria']], use_container_width=True, hide_index=True)

# Lógica condicional para abas administrativas restritas ao Gerente
if st.session_state['perfil'] == "Gerente":
    # ----------------- ABA: CADASTROS GERAIS -----------------
    with abas[2]:
        st.header("Painel de Cadastros Homologados")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Novo Registro de Base")
            tipo = st.selectbox("Tipo", ["Funcionário", "Prestador/Agregado", "Transportadora", "Veículo Frota"])
            nome = st.text_input("Razão Social / Nome Completo")
            doc = st.text_input("CNPJ / CPF / Matrícula")
            contato = st.text_input("Contato Telefônico ou Placa Fixa")
            
            if st.button("Salvar na Base", use_container_width=True):
                if nome and doc:
                    novo_id = int(df_cadastros['ID'].max() + 1) if not df_cadastros.empty else 1
                    novo_reg = pd.DataFrame([{'ID': novo_id, 'Tipo': tipo, 'Nome_Razao': nome, 'Documento': doc, 'Contato_Placa': contato}])
                    df_cadastros = pd.concat([df_cadastros, novo_reg], ignore_index=True)
                    df_cadastros.to_csv(ARQUIVO_CADASTROS, index=False)
                    st.success("Cadastro inserido no ecossistema!")
                    st.rerun()
                else:
                    st.error("Preencha Nome e Documento!")

        with col2:
            st.subheader("Registros Ativos")
            st.dataframe(df_cadastros, use_container_width=True, hide_index=True)

    # ----------------- ABA: RELATÓRIOS E EXCEL -----------------
    with abas[3]:
        st.header("Inteligência e Auditoria de Dados")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Cadastros", len(df_cadastros))
        m2.metric("Movimentos Registrados", len(df_portaria))
