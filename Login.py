import streamlit as st
import pandas as pd

# 1. Setup mock user credentials (In production, use secure hashing or a database)
USER_CREDENTIALS = {
    "admin": "admin",
    "user1": "user1"
}

# 2. Initialize session state variables to track login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "tasks" not in st.session_state:
    st.session_state.tasks = []

PRIORITY_WEIGHTS = {"🔴 Alta": 0, "🟡 Média": 1, "🟢 Baixa": 2}

# 3. Define the login form layout
def show_login_page():
    st.title("Tarefas")
    st.subheader("Faça login no sistema.")
    
    # Use st.form to capture inputs seamlessly on a single submit click
    with st.form("login_form"):
        username_input = st.text_input("Usuário", placeholder="Nome de Usuário")
        password_input = st.text_input("Senha", type="password", placeholder="••••••••")
        submit_button = st.form_submit_button("Log In")
        
        if submit_button:
            # Validate credentials against our mock database
            if username_input in USER_CREDENTIALS and USER_CREDENTIALS[username_input] == password_input:
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.success("Sucesso!")
                st.rerun()  # Rerun the app immediately to switch layouts
            else:
                st.error("Falha ao logar no sistema.")

# 4. Define the main application dashboard layout
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
                # Store task attributes as a basic record unit
                new_task = {
                    "Descrição": task_msg,
                    "Prioridade": task_priority,
                    "Weight": PRIORITY_WEIGHTS[task_priority],
                    "Check": False
                }
                st.session_state.A.append(new_task)
                st.success("Adicionada com sucesso!")
                st.rerun()

    # --- TASK DISPLAY WITH PANDAS ---
    st.subheader("Sua lista de tarefas")
    
    if not st.session_state.tasks:
        st.info("Nenhuma tarefa ainda. Adicione algumas...")
    else:
        # Convert the session tasks list straight into a Pandas DataFrame
        df = pd.DataFrame(st.session_state.tasks)
        
        df_sorted = df.sort_values(by="Weight", ascending=True)
        
        # Drop the technical 'Weight' column so it doesn't clutter the user's interface
        df_display = df_sorted.drop(columns=["Weight"])
        
        # Render the sorted data directly as an interactive Streamlit table/dataframe
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Você saiu do sistema!")
        st.rerun()

if not st.session_state.logged_in:
    show_login_page()
else:
    show_main_app()
