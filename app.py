import streamlit as st

st.set_page_config(page_title="Simulador de Escenarios", page_icon="📊")
st.title("📊 Simulador de Escenarios")

# --- Escenario base ---
PRECIO_DEF = 10.0
CANT_DEF   = 200

resultado_base = PRECIO_DEF * CANT_DEF
st.subheader("Escenario base")
st.write(f"💰 Precio: {PRECIO_DEF}")
st.write(f"📦 Cantidad: {CANT_DEF}")
st.success(f"Resultado: {resultado_base} €")

st.markdown("---")

# --- Estado: lista de escenarios ---
if "escenarios" not in st.session_state:
    st.session_state.escenarios = []  # cada item: {"precio": float, "cantidad": int}

# --- Botones de control ---
c1, c2 = st.columns(2)
with c1:
    if st.button("➕ Agregar nuevo escenario"):
        if len(st.session_state.escenarios) < 5:
            st.session_state.escenarios.append({"precio": PRECIO_DEF, "cantidad": CANT_DEF})
        else:
            st.warning("Solo puedes agregar hasta 5 escenarios adicionales.")
with c2:
    if st.button("🔄 Reiniciar escenarios"):
        st.session_state.escenarios = []
        st.rerun()

# --- Inputs de escenarios (editar sin duplicar) ---
if st.session_state.escenarios:
    st.subheader("Escenarios adicionales")
    for i, esc in enumerate(st.session_state.escenarios):
        st.write(f"**Escenario {i+1}**")
        colA, colB = st.columns(2)
        nuevo_precio = colA.number_input(
            f"Precio {i+1}", min_value=0.0, value=float(esc["precio"]), key=f"precio_{i}"
        )
        nueva_cant = colB.number_input(
            f"Cantidad {i+1}", min_value=0, value=int(esc["cantidad"]), key=f"cantidad_{i}"
        )
        # Actualizamos en sitio, no hacemos append
        st.session_state.escenarios[i]["precio"] = nuevo_precio
        st.session_state.escenarios[i]["cantidad"] = nueva_cant

    # --- Cálculo y salida ---
    if st.button("🧮 Calcular nuevos escenarios"):
        st.subheader("Resultados de los escenarios")
        for i, esc in enumerate(st.session_state.escenarios):
            total = esc["precio"] * esc["cantidad"]
            st.write(f"**Escenario {i+1}:** {esc['precio']} × {esc['cantidad']} = ✅ **{total} €**")
