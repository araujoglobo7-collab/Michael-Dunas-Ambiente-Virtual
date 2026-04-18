import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os
from datetime import datetime

# Produtividade UDA - JARVIS (Dunas Fleet Hub + Notes 2026)
st.set_page_config(layout="wide", page_title="Dunas Fleet - Hub de Inteligência")

# --- CONFIGURAÇÕES E BANCO DE DADOS ---
STATUS_OPCOES = ["Reunião", "A Iniciar", "Em Andamento", "Projetos Futuros", "Concluído"]
CORES_MAP = {"Reunião": "#e67e22", "A Iniciar": "#ffb347", "Em Andamento": "#fb8c00", "Projetos Futuros": "#edbb99", "Concluído": "#2ecc71"}
DB_FILE = "dunas_fleet_complete.json"
NOTES_FILE = "dunas_notes.txt"

# --- LINKS POWER BI ---
LINKS_POWER_BI = {
    "Selecione um Painel": "",
    "MLOG TRANSPORTES ": "https://app.powerbi.com/view?r=eyJrIjoiNzAzNzNlY2EtZjU1YS00ZjRkLWJmMzQtOGNmYjYzYmQyZmFkIiwidCI6IjZhNmZhNjk4LWZhZTYtNDJkOC05YjRkLWRiZGY4ZDc3MmI4MCJ9",
    "AUTOTRUCK TRANSPORTES": "https://app.powerbi.com/view?r=eyJrIjoiMjhjMWFlZDUtY2E0Zi00NjlmLWE0NGItM2EwMWM2YWFlZDBlIiwidCI6IjZhNmZhNjk4LWZhZTYtNDJkOC05YjRkLWRiZGY4ZDc3MmI4MCJ9"
}

def carregar_dados():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return [{"atv": "Operação Dunas", "exec": "Gabriel", "status": "Reunião", "data": "2026-04-18"}]

def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def carregar_notas():
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def salvar_notas(texto):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        f.write(texto)

if 'atividades' not in st.session_state:
    st.session_state.atividades = carregar_dados()

# --- ESTILO INTERFACE ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfaf6; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 4px solid #fb8c00; }
    .calc-box { background: white; padding: 20px; border-radius: 12px; border-left: 10px solid #fb8c00; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    iframe { border-radius: 15px; border: 2px solid #f0f0f0; }
    /* Estilo para o Bloco de Notas */
    .stTextArea textarea { background-color: #fff; border: 1px solid #ddd; border-radius: 10px; font-family: 'Inter', sans-serif; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏜️ Dunas Fleet")
    st.markdown("---")
    st.subheader("🔍 Filtro de Operação")
    data_filtro = st.date_input("Filtrar Mapa por Dia", value=datetime.now())
    data_str = data_filtro.strftime("%Y-%m-%d")
    st.markdown("---")
    if st.button("💾 SALVAR TUDO"):
        salvar_dados(st.session_state.atividades)
        st.success("Dados e Mapa Sincronizados!")

# --- FILTRAGEM ---
atividades_filtradas = [a for a in st.session_state.atividades if str(a.get("data")) == data_str]

# --- ABAS (Agora com 5 abas) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ CENTRO DE COMANDO", "📊 DASHBOARDS BI", "📝 MANIFESTO", "🧮 LOGÍSTICA", "✍️ ANOTAÇÕES"])

with tab1:
    def gerar_mapa_filtrado(atividades):
        salas_cfg = {
            "Reunião": {"t": "1%", "l": "1%", "w": "98%", "h": "22%", "n": "🤝 SALA DE COMANDO"},
            "A Iniciar": {"t": "25%", "l": "1%", "w": "32%", "h": "72%", "n": "🚀 PÁTIO DE CARGA"},
            "Em Andamento": {"t": "25%", "l": "34%", "w": "32%", "h": "40%", "n": "🚚 EM ROTA"},
            "Projetos Futuros": {"t": "67%", "l": "34%", "w": "32%", "h": "30%", "n": "📅 GARAGEM"},
            "Concluído": {"t": "25%", "l": "67%", "w": "32%", "h": "72%", "n": "✅ CHECK-OUT"}
        }
        salas_html = ""
        for status_nome, p in salas_cfg.items():
            atvs = [a for a in atividades if a and a.get('status') == status_nome]
            cards_html = ""
            for idx, a in enumerate(atvs):
                cor = CORES_MAP.get(status_nome, "#ccc")
                cards_html += f'''
                <div class="card" style="border-left: 5px solid {cor};">
                    <div class="card-top-row"><span class="badge">GABRIEL</span>
                    <div class="track"><div class="mini-walker" style="border-color:{cor}; animation-delay:{idx*0.3}s;"></div></div></div>
                    <div class="card-content">{a.get("atv","-")}</div>
                    <div class="card-date">📅 {a.get("data","---")}</div>
                </div>'''
            salas_html += f'<div class="room" style="top:{p["t"]}; left:{p["l"]}; width:{p["w"]}; height:{p["h"]};"><div class="room-label">{p["n"]}</div><div class="scroll-v">{cards_html}</div></div>'
        return f"""
        <style>
            .map-outer {{ background:#ece4db; width:100%; height:82vh; position:relative; border-radius:15px; border:10px solid #fff; overflow:hidden; }}
            .room {{ position:absolute; background:rgba(255,255,255,0.5); border-radius:8px; border:1px solid rgba(0,0,0,0.05); }}
            .room-label {{ font-size:10px; font-weight:900; color:#d35400; padding:8px 0 0 12px; text-transform:uppercase; }}
            .scroll-v {{ position:absolute; top:35px; left:0; width:100%; height:calc(100% - 40px); overflow-y:auto; padding:0 10px; box-sizing:border-box; }}
            .card {{ background:#fff; margin-bottom:10px; border-radius:6px; padding:10px; box-shadow:0 2px 5px rgba(0,0,0,0.05); }}
            .badge {{ background:#333; color:#fff; font-size:8px; padding:2px 6px; border-radius:3px; font-weight:bold; }}
            .track {{ flex-grow:1; height:18px; position:relative; margin-left:10px; background:rgba(0,0,0,0.02); border-radius:10px; overflow:hidden; }}
            .mini-walker {{ width:16px; height:16px; background: url('https://cdn-icons-png.flaticon.com/512/3135/3135715.png') center/cover; border-radius:50%; border:1.5px solid; position:absolute; animation: move 4s infinite ease-in-out alternate; }}
            @keyframes move {{ from {{ left:0%; }} to {{ left:calc(100% - 18px); }} }}
            .card-content {{ font-size:12px; font-weight:bold; color:#333; }}
            .card-date {{ font-size:9px; color:#999; margin-top:5px; font-weight:bold; }}
            ::-webkit-scrollbar {{ width:4px; }} ::-webkit-scrollbar-thumb {{ background:#fb8c00; border-radius:10px; }}
        </style>
        <div class="map-outer">{salas_html}</div>"""
    
    if atividades_filtradas:
        components.html(gerar_mapa_filtrado(atividades_filtradas), height=850)
    else:
        st.info(f"Nenhuma operação registrada para o dia {data_filtro.strftime('%d/%m/%Y')}")

with tab2:
    st.header("📊 Inteligência de Dados - Power BI")
    escolha = st.selectbox("Selecione o Cliente:", list(LINKS_POWER_BI.keys()))
    link_selecionado = LINKS_POWER_BI[escolha]
    if link_selecionado:
        st.markdown(f'<iframe width="100%" height="800" src="{link_selecionado}" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)

with tab3:
    st.write("### 📝 Manifesto")
    df = pd.DataFrame(st.session_state.atividades)
    if 'data' in df.columns: df['data'] = pd.to_datetime(df['data'])
    df_edit = st.data_editor(df, column_config={"status": st.column_config.SelectboxColumn("Status", options=STATUS_OPCOES, required=True), "data": st.column_config.DateColumn("Data", required=True)}, use_container_width=True, num_rows="dynamic")
    if st.button("🚀 ATUALIZAR MANIFESTO"):
        new_data = df_edit.to_dict('records')
        for item in new_data:
            if isinstance(item.get('data'), (datetime, pd.Timestamp)):
                item['data'] = item['data'].strftime("%Y-%m-%d")
        st.session_state.atividades = [item for item in new_data if item.get('atv') is not None]
        salvar_dados(st.session_state.atividades)
        st.rerun()

with tab4:
    st.write("### 🧮 Logística de Carga")
    total_dia = len(atividades_filtradas)
    tempo_min = st.number_input("Tempo por Operação (Min)", min_value=1, value=20)
    st.metric(f"Total para {data_filtro.strftime('%d/%m')}", f"{total_dia} Atividades")
    st.metric("Estimativa de Tempo", f"{(total_dia * tempo_min / 60):.1f} Horas")

with tab5:
    st.header("✍️ Bloco de Notas - Insights e Ideias")
    notas_atuais = carregar_notas()
    # Área para digitar as ideias
    ideias = st.text_area("Digite aqui suas anotações estratégicas...", value=notas_atuais, height=600, placeholder="Escreva o que quiser, ideias de automação, lembretes de reuniões...")
    if st.button("💾 SALVAR ANOTAÇÕES"):
        salvar_notas(ideias)
        st.success("Anotações salvas com sucesso!")