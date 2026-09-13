import streamlit as st
import pandas as pd
import uuid
import os

# Define the local database file path
CSV_FILE = "financas.csv"

USER_CREDENTIALS = {
    "": "",
    "admin": "admin",
    "user1": "user1"
}

# --- PERSISTENCE FUNCTIONS ---
def load_spents():
    """Loads spents from CSV or returns an empty DataFrame if the file doesn't exist."""
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            # Ensure proper data types
            df["id"] = df["id"].astype(str)
            df["Descrição"] = df["Descrição"].fillna("").astype(str)
            return df
        except Exception:
            # Fallback in case of a corrupted CSV file
            return pd.DataFrame(columns=["id", "Tipo", "Descrição", "Valor", "Data", "Categoria"])
    return pd.DataFrame(columns=["id", "Tipo", "Descrição", "Valor", "Data", "Categoria"])

def calcula_totais():
    df = st.session_state.spents
    totais = df.groupby('Tipo')['Valor'].sum()
    st.session_state.total_creditos = 0
    st.session_state.total_debitos = 0
    st.session_state.total_creditos = float(totais.get('Crédito', 0))
    st.session_state.total_debitos = float(totais.get('Débito', 0))
    st.session_state.total_geral = st.session_state.total_creditos + st.session_state.total_debitos

def save_spents(df):
    calcula_totais()
    df.to_csv(CSV_FILE, index=False)


# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "spents" not in st.session_state:
    # Load from local file instead of starting empty
    st.session_state.spents = load_spents()
    calcula_totais()

CATEGORIASMAP = {
    "Débito": ["Mercado", "Luz", "Internet", "Água", "Lazer","Outros"],
    "Crédito": ["Salário", "Venda", "Serviço Prestado"]
}

CATEGORIAS = ["Mercado", "Luz", "Internet", "Água", "Lazer","Outros", "Salário", "Venda", "Serviço Prestado"]

def show_login_page():
    st.title("Gastos")
    st.subheader("Faça login no sistema.")
    
    with st.form("login_form"):
        username_input = st.text_input("Usuário", placeholder="Nome de Usuário")
        password_input = st.text_input("Senha", type="password", placeholder="••••••••")
        submit_button = st.form_submit_button("Log In")
        
        if submit_button:
            if username_input in USER_CREDENTIALS and USER_CREDENTIALS[username_input] == password_input:
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.success("Sucesso!")
                st.rerun()
            else:
                st.error("Falha ao logar no sistema.") 

def show_main_app():
    st.title(f"Bem vindo, {st.session_state.username}!")

    if st.session_state.total_geral < 0:
        st.badge(f"Total geral: {st.session_state.total_geral*-1}", icon=":material/remove:", color="red")
    else:
        st.badge(f"Total geral: {st.session_state.total_geral}", icon=":material/add:", color="green")

    st.subheader("➕ Criar Débito/Crédito")
    tipo = st.selectbox("Tipo",options=list(CATEGORIASMAP.keys()))
    with st.form("spent_form", clear_on_submit=True):
        description = st.text_input("Descrição", placeholder="Descrição da movimentação", value="")
        date = st.date_input("Data", "today")
        value = st.number_input("Valor", min_value=0.0, placeholder="Quanto foi gasto?", step=1.0)
        if tipo == "Crédito":
            category = st.selectbox("Categoria", options=CATEGORIASMAP[tipo])
        else:
            category = st.selectbox("Categoria", options=CATEGORIASMAP[tipo])
        add_button = st.form_submit_button("Adicionar")
        
        if add_button:
            if value == 0:
                st.warning("Gasto deve ser maior que zero")
            else:
                sinal = 1 if tipo=='Crédito' else -1
                new_spent = {
                    "id": str(uuid.uuid4()),
                    "Tipo": tipo,
                    "Descrição": description,
                    "Data": date,
                    "Valor": value * sinal,
                    "Categoria": category 
                }
                row_df = pd.DataFrame([new_spent])
                
                updated_df = pdAppend(row_df)
                save_spents(updated_df)
                
                st.success("Adicionado com sucesso!")
                st.rerun()

    st.subheader("Sua lista de gastos")
    
    if st.session_state.spents.empty:
        st.info("Nenhum gasto cadastrado ainda. Adicione alguns...")
    else:
        col1, col2 = st.columns(2)
        coluna_sort = col1.selectbox("Ordenar por", ["Tipo", "Data", "Valor", "Descrição", "Categoria"])
        ordem = col2.radio("Ordem", ["Crescente", "Decrescente"], horizontal=True)

        if coluna_sort == 'Data':
            st.session_state.spents[coluna_sort] = pd.to_datetime(st.session_state.spents[coluna_sort], errors='coerce').dt.date
        df_completo = st.session_state.spents.copy().sort_values(
            by=coluna_sort, ascending=(ordem == "Crescente")
        ).reset_index(drop=True)
        
        if "editor_version" not in st.session_state:
            st.session_state.editor_version = 0

        editor_key = f"editor_gastos_{st.session_state.editor_version}"

        edited_df = st.data_editor(
            df_completo, 
            width='stretch', 
            hide_index=True, 
            num_rows="dynamic",
            key=editor_key,
            column_config={
                "id": None,
                "Categoria": st.column_config.SelectboxColumn(
                    "Categoria",
                    options=CATEGORIAS,
                    required=True,
                ),
            }
        )

        st.markdown(f'Total de Créditos: :green-background[{st.session_state.total_creditos}]', text_alignment="right")
        st.markdown(f'Total de Débitos: :red-background[{st.session_state.total_debitos}]', text_alignment="right")
        if st.session_state.total_geral < 0:
            st.markdown(f'Total geral: :red-background[{st.session_state.total_geral}]', text_alignment="right")
        else:
            st.markdown(f'Total geral: :green-background[{st.session_state.total_geral}]', text_alignment="right")

        if editor_key in st.session_state:
            mudancas = st.session_state[editor_key]
            houve_mudanca = False
            master_df = st.session_state.spents.copy()
            
            # 1. Handle deleted rows
            if mudancas["deleted_rows"]:
                indices_para_deletar = [int(idx) for idx in mudancas["deleted_rows"]]
                ids_para_deletar = df_completo.iloc[indices_para_deletar]["id"].tolist()
                master_df = master_df[~master_df["id"].isin(ids_para_deletar)]
                houve_mudanca = True

            # 2. Handle edited rows
            if mudancas["edited_rows"]:
                for idx_str, alteracoes in mudancas["edited_rows"].items():
                    idx = int(idx_str)
                    if idx >= len(df_completo):
                        continue
                        
                    task_id = df_completo.at[idx, "id"]
                    matching_indices = master_df[master_df["id"] == task_id].index
                    
                    if len(matching_indices) == 0:
                        continue
                    master_idx = matching_indices[0]
                    
                    for coluna, valor in alteracoes.items():
                        master_df.at[master_idx, coluna] = valor
                houve_mudanca = True
            
            # Save state changes locally
            if houve_mudanca:
                master_df["Descrição"] = master_df["Descrição"].fillna("")
                st.session_state.spents = master_df
                save_spents(master_df)
                st.session_state.editor_version += 1
                st.rerun()
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Você saiu do sistema!")
        st.rerun()

def pdAppend(row_df):
    updated_df = pd.concat([st.session_state.spents, row_df], ignore_index=True)
    st.session_state.spents = updated_df
    return updated_df


if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()