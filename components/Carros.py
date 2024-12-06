# components/carros/view.py
from utils.state_manager import StateManager
from utils.templates import render_dashboard
import streamlit as st

def Carros():
    if StateManager.get_state('logado'):
        render_dashboard(
            title="Dashboard - Carros",
            power_bi_url="https://app.powerbi.com/view?r=eyJrIjoiNTNiMzRjMWUtZjE4Mi00ZWJhLWIzNzUtNzAwZGY0NDlhM2NmIiwidCI6IjA5Y2RmOWY2LTcyOGEtNDIyMi1hOGUwLTllNTBjMjI0ZTRjNSJ9"
        )
    else:
        StateManager.set_state('selected_page', 'Login')
        st.rerun()
