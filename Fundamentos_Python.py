import streamlit as st
import pandas as pd
import uuid
import os

# Define the local database file path
CSV_FILE = "spents.csv"

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
            return pd.DataFrame(columns=["id", "Descrição", "Valor", "Data", "Categoria"])
    return pd.DataFrame(columns=["id", "Descrição", "Valor", "Data", "Categoria"])

def save_spents(df):
    """Saves the current spents DataFrame to the local CSV file."""
    df.to_csv(CSV_FILE, index=False)


# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "spents" not in st.session_state:
    # Load from local file instead of starting empty
    st.session_state.spents = load_spents()

CATEGORIAS = ["Mercado", "Luz", "Internet", "Água", "Lazer","Outros"]

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
    st.write("Aqui está sua lista de gastos:")

    st.subheader("➕ Criar Gasto")
    with st.form("spent_form", clear_on_submit=True):
        description = st.text_input("Descrição", placeholder="Com o que foi gasto?", value="")
        date = st.date_input("Data", "today")
        value = st.number_input("Valor", min_value=0.0, placeholder="Quanto foi gasto?", step=1.0)
        category = st.selectbox("Categoria", options=CATEGORIAS)
        add_button = st.form_submit_button("Adicionar")
        
        if add_button:
            if value == 0:
                st.warning("Gasto deve ser maior que zero")
            else:
                new_spent = {
                    "id": str(uuid.uuid4()),
                    "Descrição": description,
                    "Data": date,
                    "Valor": value,
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
        coluna_sort = col1.selectbox("Ordenar por", ["Data", "Valor", "Descrição", "Categoria"])
        ordem = col2.radio("Ordem", ["Crescente", "Decrescente"], horizontal=True)

        df_completo = st.session_state.spents.copy().sort_values(
            by=coluna_sort, ascending=(ordem == "Crescente")
        ).reset_index(drop=True)
        
        # df_completo['priority_peso'] = df_completo['Prioridade'].map(PRIORITY_WEIGHTS)
        # df_completo['check_peso'] = df_completo['Check'].map({False: 0, True: 1})
        
        # df_sorted = (
        #     df_completo.sort_values(by=["check_peso", "priority_peso"], ascending=[True, True])
        #     .drop(columns=['priority_peso', 'check_peso'])
        #     .reset_index(drop=True)
        # )
        
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
                # "Check": st.column_config.CheckboxColumn(
                #     "Check",
                #     help="Marque para concluir a tarefa",
                #     default=False,
                # )
            }
        )

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
