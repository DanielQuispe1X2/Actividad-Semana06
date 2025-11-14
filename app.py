import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
import google.generativeai as genai
import json
import re

# ==============================
# CONFIGURACIÓN DE ESTILO
# ==============================
st.set_page_config(page_title="Restaurante IA", page_icon="🍽️", layout="wide")

st.markdown("""
    <style>
        .titulo {
            font-size: 40px;
            font-weight: bold;
            color: #FF6F3C;
            text-align: center;
        }
        .subtitulo {
            font-size: 22px;
            font-weight: bold;
            color: #444444;
        }
        .card {
            padding: 20px;
            border-radius: 12px;
            background-color: #FFF3E0;
            border: 1px solid #FFB07C;
            margin-top: 10px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)


# ==============================
# CONFIGURACIÓN DE GEMINI (SIN SECRETS)
# ==============================
genai.configure(api_key="AIzaSyA0oGgigHTC3EqaGBTTro62yUFrVWoS2J0")

modelo = genai.GenerativeModel("gemini-2.5-pro")


# ======================
# FIX PARA LIMPIAR EL JSON
# ======================
def limpiar_json(texto):
    """
    Extrae solo el JSON válido de la respuesta de Gemini.
    Elimina bloques Markdown: ```json ``` y cualquier texto adicional.
    """
    # Eliminar bloques ```json ``` o ``` 
    texto = texto.replace("```json", "")
    texto = texto.replace("```", "")

    # Buscar el primer { y el último }
    match = re.search(r"\{[\s\S]*\}", texto)
    if match:
        return match.group(0)  # devuelve solo el JSON

    return None


# ==============================
# CONFIGURACIÓN DE MONGODB (SIN SECRETS)
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

def actualizar_pedido(id, data):
    return pedidos.update_one({"_id": ObjectId(id)}, {"$set": data})

def eliminar_pedido(id):
    return pedidos.delete_one({"_id": ObjectId(id)})


# ==============================
# INTERFAZ CON TABS
# ==============================
tab1, tab2 = st.tabs(["🧾 Realizar Pedido", "📂 Gestión de Pedidos"])


# ==========================================================
# TAB 1 – CHATBOT PARA GENERAR PEDIDO
# ==========================================================
with tab1:
    st.markdown('<p class="titulo">🍽️ Restaurante Inteligente</p>', unsafe_allow_html=True)
    st.write("Haz tu pedido usando lenguaje natural. La IA lo interpretará automáticamente.")

    col1, col2 = st.columns([2, 1])

    with col1:
        entrada = st.text_area("¿Qué deseas ordenar hoy?", height=150)

        if st.button("🤖 Procesar Pedido con IA"):
            if entrada.strip() == "":
                st.warning("Por favor ingresa un texto.")
            else:
                resultado = modelo.generate_content(entrada).text

                st.markdown('<p class="subtitulo">🧾 Resultado de la IA</p>', unsafe_allow_html=True)
                st.code(resultado)

                # ====================
                # LIMPIAR JSON
                # ====================
                json_limpio = limpiar_json(resultado)

                if not json_limpio:
                    st.error("❌ No se pudo extraer JSON válido.")
                    pedido_json = None
                else:
                    try:
                        pedido_json = json.loads(json_limpio)
                    except:
                        st.error("❌ El contenido no es JSON válido.")
                        pedido_json = None

                # Guardar pedido
                if pedido_json:
                    if st.button("💾 Guardar Pedido"):
                        crear_pedido(pedido_json)
                        st.success("✔ Pedido guardado correctamente")
                        st.experimental_rerun()


# ==========================================================
# TAB 2 – CRUD DE PEDIDOS
# ==========================================================
with tab2:
    st.markdown('<p class="titulo">📂 Gestión de Pedidos</p>', unsafe_allow_html=True)

    lista = listar_pedidos()

    if not lista:
        st.info("Aún no hay pedidos registrados.")
    else:
        for p in lista:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(f"### 🧾 Pedido ID: `{p['_id']}`")
            st.json({
                "cliente": p.get("cliente", ""),
                "items": p.get("items", []),
                "observaciones": p.get("observaciones", "")
            })

            nuevo_nombre = st.text_input(
                "Editar nombre del cliente:",
                value=p.get("cliente", ""),
                key=f"cliente_{p['_id']}"
            )

            colA, colB = st.columns([1, 1])

            with colA:
                if st.button("Actualizar", key=f"update_{p['_id']}"):
                    actualizar_pedido(p["_id"], {"cliente": nuevo_nombre})
                    st.success("✔ Pedido actualizado")
                    st.experimental_rerun()

            with colB:
                if st.button("Eliminar", key=f"delete_{p['_id']}"):
                    eliminar_pedido(p["_id"])
                    st.error("🗑 Pedido eliminado")
                    st.experimental_rerun()

            st.markdown('</div>', unsafe_allow_html=True)

