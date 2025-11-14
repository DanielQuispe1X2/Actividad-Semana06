
import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
import google.generativeai as genai

# ==============================
# CONFIGURACIÓN DE GEMINI
# ==============================
genai.configure(api_key="AIzaSyA0oGgigHTC3EqaGBTTro62yUFrVWoS2J0")

modelo = genai.GenerativeModel("gemini-pro")

def procesar_pedido(texto):
    prompt = f"""
    Eres un asistente para un restaurante. Interpreta el pedido del cliente y devuélvelo en formato JSON:

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
MONGO_URI = "mongodb+srv://danielquis21_db_user:hoambroti2013@cluster0.le4sexx.mongodb.net/"

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

if st.button("Enviar"):
    if input_usuario.strip() == "":
        st.warning("Por favor escribe un pedido.")
    else:
        resultado = procesar_pedido(input_usuario)
        st.subheader("🧾 Resultado interpretado por la IA")
        st.code(resultado)

        if st.button("Guardar Pedido"):
            try:
                doc = eval(resultado)
                crear_pedido(doc)
                st.success("Pedido guardado correctamente ✔️")
            except Exception as e:
                st.error(f"Error al guardar: {e}")


# ==============================
# MOSTRAR PEDIDOS GUARDADOS
# ==============================
st.subheader("📂 Pedidos Guardados")

for p in listar_pedidos():
    st.write(p)
    if st.button(f"Eliminar {p['_id']}", key=str(p["_id"])):
        eliminar_pedido(p["_id"])
        st.warning("Pedido eliminado.")
        st.experimental_rerun()
