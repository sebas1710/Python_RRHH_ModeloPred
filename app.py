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
  color:white;
  padding:8px 14px;
  border-radius:12px;
  font-weight:600;
  display:inline-block;
}
.pill-verde { background:#155d2b; }
.pill-amarillo { background:#a87900; }
.pill-rojo { background:#7a1111; }
.sep { height: 8px; }
</style>
""", unsafe_allow_html=True)

# ====== FUNCIONES ======
def color_porcentaje(prob):
    if prob > 0.6:
        return "pill-rojo"
    elif prob >= 0.4:
        return "pill-amarillo"
    else:
        return "pill-verde"

def render_pill(label, valor):
    color = color_porcentaje(valor)
    st.markdown(
        f"""
        <div class="scenario-row">
          <div class="pill {color}">Probabilidad de Fuga: {valor*100:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

def color_celda(val):
    color = ""
    if val > 0.6:
        color = "background-color:#ffb3b3"
    elif val >= 0.4:
        color = "background-color:#ffe699"
    else:
        color = "background-color:#b7e1cd"
    return color

# ====== CARGAR CSV ======
df = pd.read_csv("INPUT/predicciones_fuga.csv")

# ====== SELECTORES ======
st.title("📉 Modelo de Predicción de Fuga")

col_area, col_persona = st.columns(2)

areas = ["Todas"] + sorted(df["Área"].unique().tolist())
area_seleccionada = col_area.selectbox("Selecciona un área:", areas)

if area_seleccionada == "Todas":
    personas_filtradas = df["Nombre"].tolist()
else:
    personas_filtradas = df[df["Área"] == area_seleccionada]["Nombre"].tolist()

personas = ["Todos"] + personas_filtradas
persona_seleccionada = col_persona.selectbox("Selecciona una persona:", personas)

# ====== FILTRAR DATOS ======
if area_seleccionada == "Todas":
    df_filtrado = df.copy()
else:
    df_filtrado = df[df["Área"] == area_seleccionada]

if persona_seleccionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Nombre"] == persona_seleccionada]

# ====== MOSTRAR TABLA ======
st.markdown("---")

if not df_filtrado.empty:
    st.subheader("📋 Datos filtrados")
    df_vista = df_filtrado[["Nombre", "Área", "Probabilidad_Fuga_Base"]].copy()
    df_vista["Probabilidad_Fuga_%"] = (df_vista["Probabilidad_Fuga_Base"] * 100).round(1)

    def highlight_prob(val):
        style = ""
        if val > 60:
            style = "background-color:#ffb3b3"   # rojo claro
        elif val >= 40:
            style = "background-color:#ffe699"   # amarillo
        else:
            style = "background-color:#b7e1cd"   # verde
        return style

    st.dataframe(
        df_vista.style.applymap(highlight_prob, subset=["Probabilidad_Fuga_%"]),
        hide_index=True,
        use_container_width=True
    )

# ====== ESCENARIO / RESUMEN ======
st.markdown("---")

st.subheader("📊 Resumen del escenario actual")

if not df_filtrado.empty:
    if len(df_filtrado) == 1:
        empleado = df_filtrado.iloc[0]
        st.markdown(f"**Empleado:** {empleado['Nombre']}  |  **Área:** {empleado['Área']}")
        render_pill("Probabilidad de Fuga", empleado["Probabilidad_Fuga_Base"])
    else:
        prom_fuga = df_filtrado["Probabilidad_Fuga_Base"].mean()
        st.markdown(f"**Selección:** {len(df_filtrado)} empleados")
        render_pill("Promedio de Fuga", prom_fuga)
