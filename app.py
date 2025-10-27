import streamlit as st
import pandas as pd

# ====== CONFIGURACIÓN ======
st.set_page_config(page_title="Predicción de Fuga", page_icon="📉")

# ====== ESTILOS ======
st.markdown("""
<style>
.scenario-row { display:flex; gap:24px; align-items:center; flex-wrap:wrap; }
.badge { font-size:16px; }
.pill {
  background:#155d2b; color:#d1fae5; 
  padding:8px 14px; border-radius:12px; font-weight:600;
  display:inline-block;
}
.sep { height: 8px; }
</style>
""", unsafe_allow_html=True)

# ====== CARGAR CSV ======
df = pd.read_csv("input/predicciones_fuga.csv")

# ====== BLOQUE SUPERIOR: SELECTORES ======
st.title("📉 Modelo de Predicción de Fuga")

col_area, col_persona = st.columns(2)

# Selector de área
areas = sorted(df["Área"].unique())
area_seleccionada = col_area.selectbox("Selecciona un área:", areas)

# Selector de persona según área
personas = df[df["Área"] == area_seleccionada]["Nombre"].tolist()
persona_seleccionada = col_persona.selectbox("Selecciona una persona:", personas)

# Filtrar datos de la persona seleccionada
empleado = df[(df["Área"] == area_seleccionada) & (df["Nombre"] == persona_seleccionada)].iloc[0]

st.markdown("---")

# ====== FUNCIONES ======
def render_scenario(title: str, precio: float, cantidad: int, total: float):
    st.subheader(title)
    st.markdown(
        f"""
        <div class="scenario-row">
          <div class="badge">💰 <b>Precio:</b> {precio}</div>
          <div class="badge">📦 <b>Cantidad:</b> {cantidad}</div>
          <div class="pill">Resultado: {total:,.1f} €</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

# ====== ESTADO ======
if "escenarios" not in st.session_state:
    st.session_state.escenarios = []
if "resultados" not in st.session_state:
    st.session_state.resultados = []
if "mostrar_resultados" not in st.session_state:
    st.session_state.mostrar_resultados = False

# ====== ESCENARIO BASE ======
PRECIO_DEF = 10.0
CANT_DEF   = 200
TOTAL_DEF  = PRECIO_DEF * CANT_DEF

render_scenario("Escenario base", PRECIO_DEF, CANT_DEF, TOTAL_DEF)

# Mostrar info del empleado seleccionado debajo del escenario base
st.markdown(f"**Empleado seleccionado:** {empleado['Nombre']}  |  **Área:** {empleado['Área']}")
st.markdown(f"**Probabilidad de Fuga Base:** {empleado['Probabilidad_Fuga_Base']*100:.1f}%")
st.markdown("---")

# ====== RESULTADOS ======
if st.session_state.mostrar_resultados and st.session_state.resultados:
    st.subheader("Resultados de los escenarios")
    for i, r in enumerate(st.session_state.resultados, start=1):
        render_scenario(f"Escenario {i}", r["precio"], r["cantidad"], r["total"])

st.markdown("---")

# ====== CONTROLES ======
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Agregar nuevo escenario"):
        if len(st.session_state.escenarios) < 5:
            st.session_state.escenarios.append({"precio": PRECIO_DEF, "cantidad": CANT_DEF})
            st.session_state.mostrar_resultados = False
        else:
            st.warning("Solo puedes agregar hasta 5 escenarios adicionales.")
with col2:
    if st.button("🔄 Reiniciar escenarios"):
        st.session_state.escenarios = []
        st.session_state.resultados = []
        st.session_state.mostrar_resultados = False
        st.rerun()

# ====== INPUTS ======
if st.session_state.escenarios:
    st.subheader("Escenarios adicionales")
    for i, esc in enumerate(st.session_state.escenarios):
        st.write(f"**Escenario {i+1}**")
        c1, c2 = st.columns(2)
        nuevo_precio = c1.number_input(
            f"Precio {i+1}", min_value=0.0, value=float(esc["precio"]), key=f"precio_{i}"
        )
        nueva_cant = c2.number_input(
            f"Cantidad {i+1}", min_value=0, value=int(esc["cantidad"]), key=f"cantidad_{i}"
        )
        st.session_state.escenarios[i]["precio"] = nuevo_precio
        st.session_state.escenarios[i]["cantidad"] = nueva_cant

# ====== CALCULAR ======
if st.session_state.escenarios:
    if st.button("🧮 Calcular nuevos escenarios"):
        st.session_state.resultados = [
            {
                "precio": e["precio"],
                "cantidad": e["cantidad"],
                "total": e["precio"] * e["cantidad"]
            }
            for e in st.session_state.escenarios
        ]
        st.session_state.mostrar_resultados = True
        st.rerun()
