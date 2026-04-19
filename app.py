import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Dunas Fleet - Hub Operacional")

# --- TRAVA DE SEGURANÇA ---
senha = st.sidebar.text_input("Acesso", type="password")

if senha == "gsr17":
    st.sidebar.success("Painel Liberado")
    
    # --- CONFIGURAÇÕES E BANCO DE DADOS ---
    STATUS_OPCOES = ["Reunião", "A Iniciar", "Em Andamento", "Projetos Futuros", "Concluído"]
    CORES_MAP = {
        "Reunião": "#444444", 
        "A Iniciar": "#FF8C00", 
        "Em Andamento": "#FF4500", 
        "Projetos Futuros": "#FFA500", 
        "Concluído": "#28B463"
    }
    DB_FILE = "dunas_fleet_complete.json"

    def carregar_dados():
        colunas = ["Projeto", "Data Inicial", "Prazo", "Status", "Foco", "Escopo", "Detalhamento", "Resultado Esperado"]
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                try:
                    dados = json.load(f)
                    if dados:
                        df = pd.DataFrame(dados)
                        df["Data Inicial"] = pd.to_datetime(df["Data Inicial"], errors='coerce').fillna(pd.Timestamp.now())
                        df["Prazo"] = pd.to_datetime(df["Prazo"], errors='coerce').fillna(pd.Timestamp.now())
                        return df[colunas]
                except: pass
        return pd.DataFrame(columns=colunas)

    if 'df_projetos' not in st.session_state:
        st.session_state.df_projetos = carregar_dados()

    # --- FILTROS GLOBAIS (SIDEBAR) ---
    with st.sidebar:
        st.header("👔 Dunas Fleet")
        st.markdown("---")
        st.subheader("🔍 Filtros Globais")
        f_nome = st.text_input("Buscar Projeto")
        f_data = st.date_input("Data Inicial", value=None)
        
        df_exibicao = st.session_state.df_projetos.copy()
        if f_nome:
            df_exibicao = df_exibicao[df_exibicao['Projeto'].str.contains(f_nome, case=False, na=False)]
        if f_data:
            df_exibicao = df_exibicao[df_exibicao['Data Inicial'].dt.date == f_data]

        st.markdown("---")
        st.subheader("💾 Persistência")
        if st.button("SALVAR TUDO (JSON)"):
            df_save = st.session_state.df_projetos.copy()
            df_save["Data Inicial"] = df_save["Data Inicial"].dt.strftime('%Y-%m-%d')
            df_save["Prazo"] = df_save["Prazo"].dt.strftime('%Y-%m-%d')
            df_save.to_json(DB_FILE, orient="records", force_ascii=False, indent=4)
            st.success("Dados salvos fisicamente!")

    # --- ESTILO DUNAS FLEET ---
    st.markdown("""
        <style>
        .stApp { background-color: #FFFFFF; }
        [data-testid="stSidebar"] { background-color: #FF8C00 !important; border-right: 5px solid #444444; }
        [data-testid="stSidebar"] * { color: white !important; }
        .stTabs [aria-selected="true"] { background-color: #FF8C00 !important; color: white !important; font-weight: bold; }
        @media (max-width: 768px) {
            [data-testid="stMetric"] { width: 100% !important; margin-bottom: 10px; }
            .stColumnsBlock { flex-direction: column !important; }
            div[data-testid="column"] { width: 100% !important; }
            .stTabs [role="tablist"] { display: flex; flex-wrap: wrap; }
        }
        </style>
    """, unsafe_allow_html=True)

    # --- NAVEGAÇÃO POR ABAS ---
    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 PAINEL DUNAS", "🗺️ AMBIENTE VIRTUAL", "📋 FLUXO (TRELLO)", "📝 MANIFESTO (BANCO)", "✍️ NOTAS", "📊 RESUMO IA"
    ])

    # ABA 0: PAINEL DUNAS (POWER BI)
    with tab0:
        st.subheader("📊 Central de Dashboards Power BI")
        cliente = st.selectbox("Selecione o Cliente para Visualização:", ["Autotruck Transportes", "Mlog Transportes"])
        
        links = {
            "Autotruck Transportes": "https://app.powerbi.com/view?r=eyJrIjoiMjhjMWFlZDUtY2E0Zi00NjlmLWE0NGItM2EwMWM2YWFlZDBlIiwidCI6IjZhNmZhNjk4LWZhZTYtNDJkOC05YjRkLWRiZGY4ZDc3MmI4MCJ9",
            "Mlog Transportes": "https://app.powerbi.com/view?r=eyJrIjoiNzAzNzNlY2EtZjU1YS00ZjRkLWJmMzQtOGNmYjYzYmQyZmFkIiwidCI6IjZhNmZhNjk4LWZhZTYtNDJkOC05YjRkLWRiZGY4ZDc3MmI4MCJ9"
        }
        
        components.iframe(links[cliente], height=800)

    with tab1:
        st.subheader("🗺️ Mapa Estratégico")
        def gerar_mapa_html(df):
            atividades = df.to_dict('records')
            salas = {
                "Reunião": {"t": "1%", "l": "1%", "w": "98%", "h": "20%", "n": "🤝 REUNIÃO ESTRATÉGICA"},
                "A Iniciar": {"t": "23%", "l": "1%", "w": "32%", "h": "75%", "n": "🚀 BACKLOG"},
                "Em Andamento": {"t": "23%", "l": "34%", "w": "32%", "h": "45%", "n": "⚙️ EM EXECUÇÃO"},
                "Projetos Futuros": {"t": "70%", "l": "34%", "w": "32%", "h": "28%", "n": "📅 PIPELINE"},
                "Concluído": {"t": "23%", "l": "67%", "w": "32%", "h": "75%", "n": "✅ FINALIZADOS"}
            }
            html_final = ""
            for status, pos in salas.items():
                cards_html = ""
                status_cards = [x for x in atividades if x.get('Status') == status]
                for idx, a in enumerate(status_cards):
                    cor = CORES_MAP.get(status, "#ccc")
                    cards_html += f'''
                    <div style="background:#fff; border-left:6px solid {cor}; margin-bottom:12px; border-radius:8px; padding:12px; box-shadow:0 4px 6px rgba(0,0,0,0.1); border:1px solid #eee; font-family: sans-serif;">
                        <div style="display:flex; align-items:center; margin-bottom:8px;">
                            <span style="background:#FF8C00; color:white; font-size:8px; padding:2px 6px; border-radius:4px; font-weight:bold;">DUNAS</span>
                            <div style="flex-grow:1; height:10px; position:relative; margin-left:10px; background:#f0f0f0; border-radius:10px; overflow:hidden;"><div class="walker" style="animation-delay:{idx*0.5}s;"></div></div>
                        </div>
                        <div style="font-size:13px; font-weight:900; color:#444; margin-bottom:4px;">{str(a.get("Projeto","")).upper()}</div>
                        <div style="font-size:10px; color:#FF4500; font-weight:bold; margin-bottom:8px;">📅 {pd.to_datetime(a.get("Data Inicial")).strftime('%d/%m/%Y')}</div>
                        <div style="font-size:10px; color:#555; line-height:1.4;">
                            <b>🎯 Foco:</b> {a.get('Foco')}<br>
                            <b>📑 Escopo:</b> {a.get('Escopo')}<br>
                            <b>🔍 Detalhes:</b> {a.get('Detalhamento')}<br>
                            <b>✅ Result:</b> {a.get('Resultado Esperado')}
                        </div>
                    </div>'''
                html_final += f'''<div style="position:absolute; top:{pos["t"]}; left:{pos["l"]}; width:{pos["w"]}; height:{pos["h"]}; background:rgba(255,245,230,0.6); border-radius:12px; border:1px solid #ddd; display:flex; flex-direction:column;">
                    <div style="font-size:11px; font-weight:bold; color:#444; padding:10px; border-bottom:1px solid #ddd; background:rgba(255,255,255,0.4); border-radius:12px 12px 0 0;">{pos["n"]}</div>
                    <div style="overflow-y:auto; flex-grow:1; padding:10px;">{cards_html}</div></div>'''
            return f"""<style>.walker {{ width:10px; height:10px; background: #FF4500; border-radius:50%; position:absolute; top:0; animation: move 5s infinite ease-in-out alternate; }} @keyframes move {{ from {{ left:0%; }} to {{ left:calc(100% - 10px); }} }}</style>
            <div style="background:#FFFFFF; width:100%; height:82vh; position:relative; border-radius:15px; border:2px solid #eee; overflow:hidden;">{html_final}</div>"""
        components.html(gerar_mapa_html(df_exibicao), height=850)

    with tab2:
        st.subheader("📋 Visualização Estilo Trello")
        cols = st.columns(len(STATUS_OPCOES))
        for i, status in enumerate(STATUS_OPCOES):
            with cols[i]:
                st.markdown(f'<div style="background:{CORES_MAP[status]}; color:white; padding:10px; border-radius:5px; text-align:center; font-weight:bold; margin-bottom:15px;">{status.upper()}</div>', unsafe_allow_html=True)
                for a in df_exibicao[df_exibicao['Status'] == status].to_dict('records'):
                    st.markdown(f"""<div style="background:#FFFFFF; border:1px solid #ddd; border-left:5px solid {CORES_MAP[status]}; padding:15px; border-radius:10px; margin-bottom:15px; font-size:12px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                        <div style="font-size:14px; font-weight:bold; color:#444; margin-bottom:5px;">{a.get('Projeto')}</div>
                        <div style="color:#FF4500; margin-bottom:10px; font-weight:bold;">📅 {pd.to_datetime(a.get('Data Inicial')).strftime('%d/%m/%Y')}</div>
                        <div style="margin-bottom:3px;"><b>🎯 Foco:</b> {a.get('Foco')}</div>
                        <div style="margin-bottom:3px;"><b>📑 Escopo:</b> {a.get('Escopo')}</div>
                        <div style="margin-bottom:3px;"><b>🔍 Detalhes:</b> {a.get('Detalhamento')}</div>
                        <div style="margin-bottom:3px;"><b>✅ Resultado:</b> {a.get('Resultado Esperado')}</div>
                        </div>""", unsafe_allow_html=True)

    with tab3:
        st.subheader("📝 Manifesto de Dados")
        df_editado = st.data_editor(st.session_state.df_projetos, use_container_width=True, num_rows="dynamic", height=500,
            column_config={
                "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPCOES, required=True),
                "Data Inicial": st.column_config.DateColumn("Data Inicial", format="DD/MM/YYYY"),
                "Prazo": st.column_config.DateColumn("Prazo", format="DD/MM/YYYY")
            })
        if st.button("🚀 ATUALIZAR ALTERAÇÕES"):
            st.session_state.df_projetos = df_editado
            st.rerun()

    with tab4:
        st.text_area("✍️ Notas Estratégicas", height=600)

    with tab5:
        st.header("📊 Inteligência da Operação")
        df = df_exibicao
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Projetos Exibidos", len(df))
            c2.metric("Em Execução", len(df[df['Status']=='Em Andamento']))
            c3.metric("Taxa Conclusão", f"{(len(df[df['Status']=='Concluído'])/len(df)*100 if len(df)>0 else 0):.1f}%")
            c4.metric("Backlog", len(df[df['Status']=='A Iniciar']))
            st.markdown("---")
            col_L, col_R = st.columns([1, 1])
            with col_L:
                st.subheader("📈 Carga por Status")
                st.bar_chart(df['Status'].value_counts().reindex(STATUS_OPCOES, fill_value=0))
                st.subheader("🚨 Próximos Prazos")
                st.table(df[df['Status'] != 'Concluído'].sort_values('Prazo')[['Projeto', 'Prazo', 'Status']].head(5))
            with col_R:
                st.subheader("💡 Insights")
                if len(df[df['Status'] == 'Em Andamento']) > 3: st.warning("Sobrecarga detectada.")
                else: st.success("Fluxo saudável.")
                st.info(f"**Status Predominante:** {df['Status'].mode()[0] if not df['Status'].mode().empty else 'N/A'}")
        else:
            st.warning("Nenhum dado encontrado para os filtros aplicados.")
else:
    st.warning("Aguardando autenticação...")
    st.stop()
