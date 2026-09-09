import streamlit as st
import pandas as pd
import uuid
import os

# Define the local database file path
CSV_FILE = "tasks.csv"

USER_CREDENTIALS = {
    "": "",
    "admin": "admin",
    "user1": "user1"
}

# --- PERSISTENCE FUNCTIONS ---
def load_tasks():
    """Loads tasks from CSV or returns an empty DataFrame if the file doesn't exist."""
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            # Ensure proper data types
            df["id"] = df["id"].astype(str)
            df["Check"] = df["Check"].astype(bool)
            return df
        except Exception:
            # Fallback in case of a corrupted CSV file
            return pd.DataFrame(columns=["id", "Descrição", "Prioridade", "Check"])
    return pd.DataFrame(columns=["id", "Descrição", "Prioridade", "Check"])

def save_tasks(df):
    """Saves the current tasks DataFrame to the local CSV file."""
    df.to_csv(CSV_FILE, index=False)


# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "tasks" not in st.session_state:
    # Load from local file instead of starting empty
    st.session_state.tasks = load_tasks()

PRIORITY_WEIGHTS = {"🔴 Alta": 0, "🟡 Média": 1, "🟢 Baixa": 2}

def aplicar_riscado_unicode(texto):
    texto_limpo = str(texto).replace("\u0336", "")
    return "".join([ch + "\u0336" for ch in texto_limpo])

def remover_riscado_unicode(texto):
    return str(texto).replace("\u0336", "")

def show_login_page():
    st.title("Tarefas")
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
    st.write("Aqui está sua lista de tarefas:")

    st.subheader("➕ Criar Tarefa")
    with st.form("task_form", clear_on_submit=True):
        task_msg = st.text_input("Descrição", placeholder="O que precisa ser feito?")
        task_priority = st.selectbox("Prioridade", options=list(PRIORITY_WEIGHTS.keys()))
        add_button = st.form_submit_button("Adicionar")
        
        if add_button:
            if task_msg.strip() == "":
                st.warning("Descrição não pode estar vazia!")
            else:
                new_task = {
                    "id": str(uuid.uuid4()),
                    "Descrição": task_msg,
                    "Prioridade": task_priority,
                    "Check": False
                }
                row_df = pd.DataFrame([new_task])
                
                updated_df = pdAppend(row_df)
                save_tasks(updated_df)
                
                st.success("Adicionada com sucesso!")
                st.rerun()

    st.subheader("Sua lista de tarefas")
    
    if st.session_state.tasks.empty:
        st.info("Nenhuma tarefa ainda. Adicione algumas...")
    else:
        df_completo = st.session_state.tasks.copy()
        
        df_completo['priority_peso'] = df_completo['Prioridade'].map(PRIORITY_WEIGHTS)
        df_completo['check_peso'] = df_completo['Check'].map({False: 0, True: 1})
        
        df_sorted = (
            df_completo.sort_values(by=["check_peso", "priority_peso"], ascending=[True, True])
            .drop(columns=['priority_peso', 'check_peso'])
            .reset_index(drop=True)
        )
        
        if "editor_version" not in st.session_state:
            st.session_state.editor_version = 0

        editor_key = f"editor_tarefas_{st.session_state.editor_version}"

        edited_df = st.data_editor(
            df_sorted, 
            use_container_width=True, 
            hide_index=True, 
            num_rows="dynamic",
            key=editor_key,
            column_config={
                "id": None,
                "Prioridade": st.column_config.SelectboxColumn(
                    "Prioridade",
                    options=list(PRIORITY_WEIGHTS.keys()),
                    required=True,
                ),
                "Check": st.column_config.CheckboxColumn(
                    "Check",
                    help="Marque para concluir a tarefa",
                    default=False,
                )
            }
        )

        if editor_key in st.session_state:
            mudancas = st.session_state[editor_key]
            houve_mudanca = False
            master_df = st.session_state.tasks.copy()
            
            # 1. Handle deleted rows
            if mudancas["deleted_rows"]:
                indices_para_deletar = [int(idx) for idx in mudancas["deleted_rows"]]
                ids_para_deletar = df_sorted.iloc[indices_para_deletar]["id"].tolist()
                master_df = master_df[~master_df["id"].isin(ids_para_deletar)]
                houve_mudanca = True

            # 2. Handle edited rows
            if mudancas["edited_rows"]:
                for idx_str, alteracoes in mudancas["edited_rows"].items():
                    idx = int(idx_str)
                    if idx >= len(df_sorted):
                        continue
                        
                    task_id = df_sorted.at[idx, "id"]
                    matching_indices = master_df[master_df["id"] == task_id].index
                    
                    if len(matching_indices) == 0:
                        continue
                    master_idx = matching_indices
                    
                    for coluna, valor in alteracoes.items():
                        master_df.at[master_idx, coluna] = valor
                        
                        if coluna == "Check":
                            texto_original = master_df.at[master_idx, "Descrição"].item()
                            if valor is True:
                                master_df.at[master_idx, "Descrição"] = aplicar_riscado_unicode(texto_original)
                            else:
                                master_df.at[master_idx, "Descrição"] = remover_riscado_unicode(texto_original)
                houve_mudanca = True
            
            # Save state changes locally
            if houve_mudanca:
                st.session_state.tasks = master_df
                save_tasks(master_df)
                st.session_state.editor_version += 1
                st.rerun()
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Você saiu do sistema!")
        st.rerun()

def pdAppend(row_df):
    updated_df = pd.concat([st.session_state.tasks, row_df], ignore_index=True)
    st.session_state.tasks = updated_df
    return updated_df


if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()
