import streamlit as st

def carros():
    """
    Renderiza a página 'Carros'.
    """
    # Botão para voltar à página inicial
    if st.button("Voltar à Página Inicial"):
        st.session_state['selected_page'] = "Dashboard"  # Atualiza o estado da página
        st.rerun()  # Recarrega o Streamlit para aplicar a mudança

    # Conteúdo da página Carros
    st.markdown("""
        <h1 style="text-align: center; font-size: 2.5em; color: #000000;">Dashboard - Carros</h1>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px;">
            <iframe title="carros" width="90%" height="800" 
                    src="https://app.powerbi.com/view?r=eyJrIjoiNTNiMzRjMWUtZjE4Mi00ZWJhLWIzNzUtNzAwZGY0NDlhM2NmIiwidCI6IjA5Y2RmOWY2LTcyOGEtNDIyMi1hOGUwLTllNTBjMjI0ZTRjNSJ9" 
                    frameborder="0" allowFullScreen="true" style="border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            </iframe>
        </div>
    """, unsafe_allow_html=True)
