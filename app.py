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
          <div class="pill {color}">{label}: {valor*100:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

def calcular_probabilidad(base, aumento_salarial, aumento_cargo):
    cargo_valor = 1 if aumento_cargo == "Sí" else 0
    nueva_prob = base - 0.2 * (aumento_salarial / 100) - 0.1 * cargo_valor
    return max(min(nueva_prob, 1), 0)

def highlight_prob(val):
    try:
        if val > 60:
            return "background-color:#ffb3b3; color:black"
        elif val >= 40:
            return "background-color:#ffe699; color:black"
        else:
            return "background-color:#b7e1cd; color:black"
    except Exception:
        return ""

# ====== CARGAR CSV ======
df = pd.read_csv("INPUT/predicciones_fuga.csv")

# ====== TABS ======
tab1, tab2 = st.tabs(["👤 Análisis por Persona", "🏢 Análisis del Área"])

# =====================================================================================
# 🟢 TAB 1 - ANÁLISIS INDIVIDUAL
# =====================================================================================
with tab1:
    st.title("📉 Análisis por Persona")
    st.header("Resultados y Simulaciones Individuales")

    col_area, col_persona = st.columns(2)
    areas = ["Todas"] + sorted(df["Área"].unique().tolist())
    area_sel = col_area.selectbox("Selecciona un área:", areas, key="area_tab1")

    if area_sel == "Todas":
        personas_filtradas = df["Nombre"].tolist()
    else:
        personas_filtradas = df[df["Área"] == area_sel]["Nombre"].tolist()

    personas = ["Todos"] + personas_filtradas
    persona_sel = col_persona.selectbox("Selecciona una persona:", personas, key="persona_tab1")

    df_filtrado = df.copy() if area_sel == "Todas" else df[df["Área"] == area_sel]
    if persona_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Nombre"] == persona_sel]

    st.markdown("---")

    if not df_filtrado.empty:
        st.subheader("📋 Datos Filtrados")
        df_vista = df_filtrado[["Nombre", "Área", "Probabilidad_Fuga_Base"]].copy()
        df_vista["Probabilidad_Fuga_%"] = (df_vista["Probabilidad_Fuga_Base"] * 100).round(1)

        st.dataframe(
            df_vista.style.format({"Probabilidad_Fuga_%": lambda x: f"{x:.1f}%".replace('.', ',')})
            .applymap(highlight_prob, subset=["Probabilidad_Fuga_%"]),
            hide_index=True,
            use_container_width=True
        )

        # Mostrar promedio si hay varios empleados seleccionados
        if len(df_filtrado) > 1:
            prom_fuga = df_filtrado["Probabilidad_Fuga_Base"].mean()
            st.markdown(f"**Selección:** {len(df_filtrado)} empleados")
            render_pill("Promedio de Fuga", prom_fuga)

    st.markdown("---")
    st.subheader("📊 Escenario Actual")

    if not df_filtrado.empty:
        if len(df_filtrado) == 1:
            emp = df_filtrado.iloc[0]
            st.markdown(f"### 👤 {emp['Nombre']} — {emp['Área']}")
            render_pill("Probabilidad de Fuga", emp["Probabilidad_Fuga_Base"])

            st.markdown("---")
            st.subheader("🧩 Simulación de nuevos escenarios")

            if "escenarios" not in st.session_state:
                st.session_state.escenarios = []

            if st.button("🔄 Reiniciar escenarios"):
                st.session_state.escenarios = []
                st.rerun()

            if st.session_state.escenarios:
                for i, esc in enumerate(st.session_state.escenarios):
                    st.markdown(f"**Escenario {i+1}**")
                    c1, c2 = st.columns(2)
                    esc["aumento_cargo"] = c1.selectbox(f"Aumento Cargo {i+1}", ["No", "Sí"], key=f"cargo_{i}")
                    esc["aumento_salarial"] = c2.number_input(f"Aumento Salarial (%) {i+1}", 0, 50, int(esc["aumento_salarial"]), 1, key=f"salario_{i}")

            col_add, col_calc = st.columns([3, 1])
            with col_add:
                if st.button("➕ Agregar escenario"):
                    if len(st.session_state.escenarios) < 5:
                        st.session_state.escenarios.append({"aumento_cargo": "No", "aumento_salarial": 5})
                        st.rerun()
                    else:
                        st.warning("Máximo 5 escenarios")
            with col_calc:
                calcular = st.button("🧮 Calcular escenarios")

            if calcular and st.session_state.escenarios:
                res = []
                base_prob = emp["Probabilidad_Fuga_Base"]
                res.append({"Escenario": "Base", "Aumento_Cargo": "-", "Aumento_Salarial_%": "-", "Probabilidad_Fuga": base_prob})
                for i, esc in enumerate(st.session_state.escenarios):
                    nueva = calcular_probabilidad(base_prob, esc["aumento_salarial"], esc["aumento_cargo"])
                    res.append({"Escenario": f"Escenario {i+1}", "Aumento_Cargo": esc["aumento_cargo"], "Aumento_Salarial_%": f"{esc['aumento_salarial']}%", "Probabilidad_Fuga": nueva})
                df_res = pd.DataFrame(res)
                st.markdown("---")
                st.subheader("📈 Resultados")
                st.dataframe(df_res.style.format({"Probabilidad_Fuga": lambda x: f"{x*100:.1f}%".replace('.', ',')}).applymap(lambda v: highlight_prob(v*100) if isinstance(v, float) else "", subset=["Probabilidad_Fuga"]), hide_index=True, use_container_width=True)

# =====================================================================================
# 🔵 TAB 2 - ANÁLISIS ESTRUCTURAL
# =====================================================================================
with tab2:
    st.title("🏢 Análisis del Área")
    st.header("Resultados y Simulaciones Estructurales")
    #st.subheader("Valores base de la encuesta de clima")

    areas = sorted(df["Área"].unique().tolist())
    area_sel = st.selectbox("Selecciona un área:", areas, key="area_tab2")
    df_area = df[df["Área"] == area_sel].copy()

    lid_base = df_area["Liderazgo"].iloc[0]
    sal_base = df_area["Salario_Beneficios"].iloc[0]
    form_base = df_area["Formacion"].iloc[0]

    st.markdown(f"**Valores actuales:** Liderazgo = {lid_base}, Salario = {sal_base}, Formación = {form_base}")

    if "escenarios_area" not in st.session_state:
        st.session_state.escenarios_area = []

    if st.button("🔄 Reiniciar escenarios", key="reset_area"):
        st.session_state.escenarios_area = []
        st.rerun()

    if st.session_state.escenarios_area:
        for i, esc in enumerate(st.session_state.escenarios_area):
            st.markdown(f"**Escenario {i+1}**")
            c1, c2, c3 = st.columns(3)
            esc["Liderazgo"] = c1.slider(f"Liderazgo {i+1}", 1.0, 5.0, float(esc["Liderazgo"]), 0.1, key=f"lid_{i}")
            esc["Salario_Beneficios"] = c2.slider(f"Salario y Beneficios {i+1}", 1.0, 5.0, float(esc["Salario_Beneficios"]), 0.1, key=f"sal_{i}")
            esc["Formacion"] = c3.slider(f"Formación {i+1}", 1.0, 5.0, float(esc["Formacion"]), 0.1, key=f"form_{i}")

    col_add, col_calc = st.columns([3, 1])
    with col_add:
        if st.button("➕ Agregar escenario", key="add_area"):
            if len(st.session_state.escenarios_area) < 5:
                st.session_state.escenarios_area.append({
                    "Liderazgo": lid_base,
                    "Salario_Beneficios": sal_base,
                    "Formacion": form_base
                })
                st.rerun()
            else:
                st.warning("Máximo 5 escenarios")
    with col_calc:
        calcular_area = st.button("🧮 Calcular escenarios", key="calc_area")

    if calcular_area and st.session_state.escenarios_area:
        base_probs = df_area[["Nombre", "Probabilidad_Fuga_Base"]].copy()
        for i, esc in enumerate(st.session_state.escenarios_area):
            delta_lid = esc["Liderazgo"] - lid_base
            delta_sal = esc["Salario_Beneficios"] - sal_base
            delta_form = esc["Formacion"] - form_base
            factor_total = -0.05 * (delta_lid + delta_sal + delta_form)
            base_probs[f"Escenario {i+1}"] = (base_probs["Probabilidad_Fuga_Base"] + factor_total).clip(0, 1)

        st.markdown("---")
        st.subheader(f"📈 Nuevos Resultados por Empleado — {area_sel}")
        st.dataframe(base_probs.style.format({col: lambda x: f"{x*100:.1f}%".replace('.', ',') for col in base_probs.columns if col != "Nombre"}).applymap(lambda v: highlight_prob(v*100) if isinstance(v, float) else "", subset=[c for c in base_probs.columns if c != "Nombre"]), hide_index=True, use_container_width=True)