import streamlit as st

# --- Título ---
st.title("🧮 Calculadora simple de precio x cantidad")

# --- Valores por defecto ---
precio = 10
cantidad = 200

# --- Cálculo ---
resultado = precio * cantidad

# --- Mostrar resultados ---
st.subheader("Valores por defecto:")
st.write(f"💰 Precio: {precio}")
st.write(f"📦 Cantidad: {cantidad}")

st.markdown("---")

st.subheader("Resultado del cálculo:")
st.success(f"**Total: {resultado} €**")
