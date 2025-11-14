import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
import google.generativeai as genai
import json

# ==============================
# CONFIGURACIÓN DE GEMINI
# ==============================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

modelo = genai.GenerativeModel("gemini-2.0-flash")

def procesar_pedido(texto):
    prompt = f"""
    Eres un asistente para un restaurante. Interpreta el pedido del cliente y devuélvelo SOLO en formato JSON:

    {{
        "cliente": "",
        "items": [
            {{"producto": "", "cantidad": 0}}
        ],
        "observaciones": ""
    }}

    Texto del cliente: {texto}
    """

    respuesta = modelo.generate_content(prompt)
    return respuesta.text


# ==============================
# CONFIGURACIÓN DE MONGODB ATLAS
# ==============================
MONGO_URI = st.secrets["MONGO_URI"]

client = MongoClient(MONGO_URI)
db = client["restaurante"]
pedidos = db["pedidos"]


# ==============================
# CRUD
# ==============================
def crear_pedido(data):
    return pedidos.insert_one(data)

def listar_pedidos():
    return list(pedidos.find())

def eliminar_pedido(id):
    return pedidos.delete_one({"_id": ObjectId(id)})


# ==============================
# STREAMLIT – INTERFAZ
# ==============================
st.set_page_config(page_title="Chatbot de Restaurante", page_icon="🍽️")
st.title("🍽️ Chatbot de Menú – IA con Gemini + MongoDB")

st.write("Escribe tu pedido en lenguaje natural para que la IA lo procese.")

input_usuario = st.text_input("¿Qué deseas ordenar?")

# ------------------------------
# PROCESAR PEDIDO
# ------------------------------
if st.button("Enviar"):
    if input_usuario.strip() == "":
        st.warning("Por favor escribe un pedido.")
    else:
        resultado = procesar_pedido(input_usuario)

        st.subheader("🧾 Resultado interpretado por la IA")
        st.code(resultado)

        # Intentar convertir a JSON
        try:
            data_json = json.loads(resultado)
        except:
            st.error("❌ La IA no devolvió JSON válido.")
            data_json = None

        if data_json:
            if st.button("Guardar Pedido"):
                crear_pedido(data_json)
                st.success("Pedido guardado correctamente ✔️")
                st.experimental_rerun()


# ------------------------------
# MOSTRAR PEDIDOS GUARDADOS (CRUD)
# ------------------------------
st.subheader("📂 Pedidos Guardados")

lista = listar_pedidos()

if len(lista) == 0:
    st.info("No hay pedidos registrados aún.")
else:
    for p in lista:
        st.write(f"### 🧾 Pedido ID: {p['_id']}")
        st.json({
            "cliente": p.get("cliente", ""),
            "items": p.get("items", []),
            "observaciones": p.get("observaciones", "")
        })

        if st.button(f"❌ Eliminar pedido", key=f"del_{p['_id']}"):
            eliminar_pedido(p["_id"])
            st.warning("Pedido eliminado.")
            st.experimental_rerun()
