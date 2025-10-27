import streamlit as st

# --- Configuración inicial ---
st.set_page_config(page_title="Simulador de Escenarios", page_icon="📊")

st.title("📊 Simulador de escenarios de Precio × Cantidad")

# --- Escenario base ---
precio_base = 10
cantidad_base = 200
resultado_base = precio_base * cantidad_base

st.subheader("Escenario base")
st.write(f"💰 Precio: {precio_base}")
st.write(f"📦 Cantidad: {cantidad_base}")
st.success(f"Resultado: {resultado_base} €")

st.markdown("---")

# --- Control de número de escenarios ---
if "num_escenarios" not in st.session_state:
    st.session_state.num_escenarios = 0

col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Agregar nuevo escenario"):
        if st.session_state.num_escenarios < 5:
            st.session_state.num_escenarios += 1
        else:
            st.warning("Solo puedes agregar hasta 5 escenarios adicionales.")

with col2:
    if st.button("🔄 Reiniciar escenarios"):
        st.session_state.num_escenarios = 0
        st.session_state.pop("escenarios", None)
        st.rerun()

# --- Crear los inputs dinámicos ---
st.subheader("Escenarios adicionales")

if "escenarios" not in st.session_state:
    st.session_state.escenarios = []

for i in range(st.session_state.num_escenarios):
    with st.container():
        st.write(f"**Escenario {i+1}**")
        c1, c2 = st.columns(2)
        precio = c1.number_input(f"Precio {i+1}", min_value=0.0, value=10.0, key=f"precio_{i}")
        cantidad = c2.number_input(f"Cantidad {i+1}", min_value=0, value=200, key=f"cantidad_{i}")
        st.session_state.escenarios.append({"precio": precio, "cantidad": cantidad})

# --- Calcular escenarios ---
if st.session_state.num_escenarios > 0:
    if st.button("🧮 Calcular nuevos escenarios"):
        st.subheader("Resultados de los escenarios")
        for i, esc in enumerate(st.session_state.escenarios):
            total = esc["precio"] * esc["cantidad"]
            st.write(f"**Escenario {i+1}:** {esc['precio']} × {esc['cantidad']} = ✅ **{total} €**")
