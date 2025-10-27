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

def calcular_probabilidad(base, aumento_salarial, aumento_cargo):
    cargo_valor = 1 if aumento_cargo == "Sí" else 0
    nueva_prob = base - 0.2 * (aumento_salarial / 100) - 0.1 * cargo_valor
    return max(min(nueva_prob, 1), 0)  # limitar entre 0 y 1

def color_prob_html(prob):
    if prob > 0.6:
        bg = "#ffb3b3"
    elif prob >= 0.4:
        bg = "#ffe699"
    else:
        bg = "#b7e1cd"
    return f"background-color:{bg}; color:black; font-weight:600;"

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

# ====== TABS PRINCIPALES ======
tab1, tab2 = st.tabs(["👤 Análisis por Persona", "🏢 Análisis del Área"])

# =====================================================================================
# 🟢 TAB 1 - ANÁLISIS INDIVIDUAL
# =====================================================================================
with tab1:
    st.title("📉 Modelo de Predicción de Fuga - Análisis por Persona")

    col_area, col_persona = st.columns(2)

    areas = ["Todas"] + sorted(df["Área"].unique().tolist())
    area_seleccionada = col_area.selectbox("Selecciona un área:", areas, key="area_tab1")

    if area_seleccionada == "Todas":
        personas_filtradas = df["Nombre"].tolist()
    else:
        personas_filtradas = df[df["Área"] == area_seleccionada]["Nombre"].tolist()

    personas = ["Todos"] + personas_filtradas
    persona_seleccionada = col_persona.selectbox("Selecciona una persona:", personas, key="persona_tab1")

    if area_seleccionada == "Todas":
        df_filtrado = df.copy()
    else:
        df_filtrado = df[df["Área"] == area_seleccionada]

    if persona_seleccionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Nombre"] == persona_seleccionada]

    st.markdown("---")

    if not df_filtrado.empty:
        st.subheader("📋 Datos filtrados")
        df_vista = df_filtrado[["Nombre", "Área", "Probabilidad_Fuga_Base"]].copy()
        df_vista["Probabilidad_Fuga_%"] = (df_vista["Probabilidad_Fuga_Base"] * 100).round(1)

        def fmt_pct(x):
            try:
                return f"{x:.1f}%".replace('.', ',')
            except Exception:
                return x

        st.dataframe(
            df_vista.style.format({"Probabilidad_Fuga_%": fmt_pct}).applymap(highlight_prob, subset=["Probabilidad_Fuga_%"]),
            hide_index=True,
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("📊 Escenario actual")

    if not df_filtrado.empty:
        if len(df_filtrado) == 1:
            empleado = df_filtrado.iloc[0]
            st.markdown(f"### 👤 {empleado['Nombre']} — {empleado['Área']}")
            render_pill("Probabilidad de Fuga", empleado["Probabilidad_Fuga_Base"])

            st.markdown("---")
            st.subheader("🧩 Simulación de nuevos escenarios")

            if "escenarios" not in st.session_state:
                st.session_state.escenarios = []

            col_reset, col_calc = st.columns([1, 1])
            with col_reset:
                if st.button("🔄 Reiniciar escenarios"):
                    st.session_state.escenarios = []
                    st.rerun()
            with col_calc:
                calcular = st.button("🧮 Calcular escenarios")

            if st.session_state.escenarios:
                for i, esc in enumerate(st.session_state.escenarios):
                    st.markdown(f"**Escenario {i+1}**")
                    c1, c2 = st.columns(2)
                    esc["aumento_cargo"] = c1.selectbox(
                        f"Aumento de Cargo (Sí/No) {i+1}", ["No", "Sí"], key=f"cargo_{i}", index=0 if esc["aumento_cargo"] == "No" else 1
                    )
                    esc["aumento_salarial"] = c2.number_input(
                        f"Aumento Salarial (%) {i+1}", min_value=0, max_value=50, value=int(esc["aumento_salarial"]), step=1, key=f"salario_{i}"
                    )

            if st.button("➕ Agregar escenario"):
                if len(st.session_state.escenarios) < 5:
                    st.session_state.escenarios.append({"aumento_cargo": "No", "aumento_salarial": 5})
                else:
                    st.warning("Máximo 5 escenarios adicionales")

            if calcular and st.session_state.escenarios:
                resultados = []
                base_prob = empleado["Probabilidad_Fuga_Base"]

                resultados.append({
                    "Escenario": "Base",
                    "Aumento_Cargo": "-",
                    "Aumento_Salarial_%": "-",
                    "Probabilidad_Fuga": base_prob
                })

                for i, esc in enumerate(st.session_state.escenarios):
                    nueva_prob = calcular_probabilidad(base_prob, esc["aumento_salarial"], esc["aumento_cargo"])
                    resultados.append({
                        "Escenario": f"Escenario {i+1}",
                        "Aumento_Cargo": esc["aumento_cargo"],
                        "Aumento_Salarial_%": f"{esc['aumento_salarial']}%",
                        "Probabilidad_Fuga": nueva_prob
                    })

                df_resultados = pd.DataFrame(resultados)

                def fmt_pct2(x):
                    try:
                        return f"{x*100:.1f}%".replace('.', ',')
                    except:
                        return x

                st.markdown("---")
                st.subheader("📈 Resultados de los escenarios")
                st.markdown(f"#### 👤 {empleado['Nombre']} — {empleado['Área']}")

                st.dataframe(
                    df_resultados.style
                    .format({"Probabilidad_Fuga": fmt_pct2})
                    .applymap(highlight_prob, subset=["Probabilidad_Fuga"]),
                    hide_index=True,
                    use_container_width=True
                )

        else:
            prom_fuga = df_filtrado["Probabilidad_Fuga_Base"].mean()
            st.markdown(f"**Selección:** {len(df_filtrado)} empleados")
            render_pill("Promedio de Fuga", prom_fuga)

# =====================================================================================
# 🔵 TAB 2 - ANÁLISIS ESTRUCTURAL POR ÁREA
# =====================================================================================
with tab2:
    st.title("🏢 Análisis del Área - Factores Estructurales")

    areas = sorted(df["Área"].unique().tolist())
    area_sel = st.selectbox("Selecciona un área:", areas, key="area_tab2")

    df_area = df[df["Área"] == area_sel].copy()

    liderazgo_base = df_area["Liderazgo"].iloc[0]
    salario_base = df_area["Salario_Beneficios"].iloc[0]
    formacion_base = df_area["Formacion"].iloc[0]

    st.markdown(f"**Valores actuales:** Liderazgo = {liderazgo_base}, Salario = {salario_base}, Formación = {formacion_base}")

    if "escenarios_area" not in st.session_state:
        st.session_state.escenarios_area = []

    col_reset, col_calc = st.columns([1, 1])
    with col_reset:
        if st.button("🔄 Reiniciar escenarios", key="reset_area"):
            st.session_state.escenarios_area = []
            st.rerun()
    with col_calc:
        calcular_area = st.button("🧮 Calcular escenarios", key="calc_area")

    if st.session_state.escenarios_area:
        for i, esc in enumerate(st.session_state.escenarios_area):
            st.markdown(f"**Escenario {i+1}**")
            c1, c2, c3 = st.columns(3)
            esc["Liderazgo"] = c1.slider(f"Liderazgo {i+1}", 1.0, 5.0, float(esc["Liderazgo"]), 0.1, key=f"lider_{i}")
            esc["Salario_Beneficios"] = c2.slider(f"Salario y Beneficios {i+1}", 1.0, 5.0, float(esc["Salario_Beneficios"]), 0.1, key=f"sal_{i}")
            esc["Formacion"] = c3.slider(f"Formación {i+1}", 1.0, 5.0, float(esc["Formacion"]), 0.1, key=f"form_{i}")

    if st.button("➕ Agregar escenario", key="add_area"):
        if len(st.session_state.escenarios_area) < 5:
            st.session_state.escenarios_area.append({
                "Liderazgo": liderazgo_base,
                "Salario_Beneficios": salario_base,
                "Formacion": formacion_base
            })
        else:
            st.warning("Máximo 5 escenarios adicionales")

    if calcular_area and st.session_state.escenarios_area:
        base_probs = df_area[["Nombre", "Área", "Probabilidad_Fuga_Base", "Liderazgo", "Salario_Beneficios", "Formacion"]].copy()

        for i, esc in enumerate(st.session_state.escenarios_area):
            delta_lid = esc["Liderazgo"] - liderazgo_base
            delta_sal = esc["Salario_Beneficios"] - salario_base
            delta_form = esc["Formacion"] - formacion_base
            factor_total = -0.05 * (delta_lid + delta_sal + delta_form)

            base_probs[f"Escenario {i+1}"] = (base_probs["Probabilidad_Fuga_Base"] + factor_total).clip(0, 1)

        def fmt_pct3(x):
            try:
                return f"{x*100:.1f}%".replace('.', ',')
            except:
                return x

        st.markdown("---")
        st.subheader(f"📈 Resultados por Empleado — {area_sel}")

        st.dataframe(
            base_probs.style
                .format({col: fmt_pct3 for col in base_probs.columns if col.startswith("Escenario") or col == "Probabilidad_Fuga_Base"})
                .applymap(lambda v: highlight_prob(v*100) if isinstance(v, float) else "", subset=[c for c in base_probs.columns if c.startswith("Escenario") or c == "Probabilidad_Fuga_Base"]),
            hide_index=True,
            use_container_width=True
        )