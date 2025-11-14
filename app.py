import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
import google.generativeai as genai
import json

# ==============================
# CONFIGURACIÓN DE GEMINI (SIN SECRETS)
# ==============================
genai.configure(api_key="AIzaSyA0oGgigHTC3EqaGBTTro62yUFrVWoS2J0")

# TE MANTENGO EL MISMO MODELO QUE FUNCIONABA
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
# CONFIGURACIÓN DE MONGODB (SIN SECRETS)
# ==============================
MONGO_URI = "mongodb+srv://danielquis21_db_user:hoambroti2013@cluster0.le4sexx.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["restaurante"]
pedidos = db["pedidos"]


# ==============================
# CRUD COMPLETO
# ==============================
def crear_pedido(data):
    return pedidos.insert_one(data)

def listar_pedidos():
    return list(pedidos.find())

def actualizar_pedido(id, data):
    return pedidos.update_one({"_id": ObjectId(id)}, {"$set": data})

def eliminar_pedido(id):
    return pedidos.delete_one({"_id": ObjectId(id)})


# ==============================
# STREAMLIT UI
# ==============================
st.set_page_config(page_title="Chatbot Restaurante", page_icon="🍽️")
st.title("🍽️ Chatbot de Menú – IA + MongoDB")

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

        # Convertir a JSON seguro
        try:
            data_json = json.loads(resultado)
        except:
            st.error("❌ La IA devolvió un formato que no es JSON válido.")
            data_json = None

        # Guardar pedido
        if data_json:
            if st.button("Guardar Pedido"):
                crear_pedido(data_json)
                st.success("Pedido guardado correctamente ✔️")
                st.experimental_rerun()


# ------------------------------
# CRUD: MOSTRAR, ACTUALIZAR Y ELIMINAR
# ------------------------------
st.subheader("📂 Pedidos Guardados")

lista = listar_pedidos()

if not lista:
    st.info("No hay pedidos registrados aún.")
else:
    for p in lista:
        st.write(f"### 🧾 Pedido ID: {p['_id']}")
        st.json({
            "cliente": p.get("cliente", ""),
            "items": p.get("items", []),
            "observaciones": p.get("observaciones", "")
        })

        # Campo editable del cliente
        nuevo_cliente = st.text_input(
            label=f"Editar cliente ({p['_id']})",
            value=p.get("cliente", ""),
            key=f"cliente_{p['_id']}"
        )

        # Botón de actualizar
        if st.button(f"Actualizar Pedido {p['_id']}", key=f"update_{p['_id']}"):
            actualizar_pedido(p["_id"], {"cliente": nuevo_cliente})
            st.success("Pedido actualizado ✔️")
            st.experimental_rerun()

        # Botón de eliminar
        if st.button(f"Eliminar Pedido {p['_id']}", key=f"delete_{p['_id']}"):
            eliminar_pedido(p["_id"])
            st.warning("Pedido eliminado ❌")
            st.experimental_rerun()

