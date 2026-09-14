import io
import uuid
import os
from PIL import Image
import google.generativeai as genai
import streamlit as st

st.set_page_config(page_title="MVN AI", page_icon="🔴", layout="wide")

st.markdown("""
    <style>
    .stChatInput { bottom: 20px; }
    div[data-testid="stColumn"] { display: flex; align-items: center; }
    </style>
""", unsafe_allow_html=True)

# 1. Получение API-ключа из настроек Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Ошибка: API-ключ не найден! Добавьте GEMINI_API_KEY в Secrets на сайте Streamlit Cloud.")
    st.stop()

genai.configure(api_key=api_key)

# Настройка модели Gemini 1.5 Flash
SYSTEM_PROMPT = "Ты — MVN AI, универсальный и продвинутый ИИ-ассистент."
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

MAX_CHATS = 100

# 2. Инициализация чатов
if "chats" not in st.session_state:
    default_id = str(uuid.uuid4())
    st.session_state.chats = {
        default_id: {"name": "Новый чат 1", "messages": []}
    }
    st.session_state.current_chat_id = default_id

def create_new_chat():
    if len(st.session_state.chats) >= MAX_CHATS:
        st.sidebar.error(f"Достигнут лимит в {MAX_CHATS} чатов!")
        return
    new_id = str(uuid.uuid4())
    chat_num = len(st.session_state.chats) + 1
    st.session_state.chats[new_id] = {
        "name": f"Новый чат {chat_num}",
        "messages": []
    }
    st.session_state.current_chat_id = new_id

# 3. Боковая панель (Sidebar)
st.sidebar.title("🔴 MVN AI Control")

if st.sidebar.button("➕ Создать новый чат"):
    create_new_chat()

chat_options = {cid: data["name"] for cid, data in st.session_state.chats.items()}
selected_chat_id = st.sidebar.selectbox(
    "Мои чаты:",
    options=list(chat_options.keys()),
    format_func=lambda x: chat_options[x],
    index=list(chat_options.keys()).index(st.session_state.current_chat_id)
)
st.session_state.current_chat_id = selected_chat_id

current_chat = st.session_state.chats[st.session_state.current_chat_id]

# 4. Главный экран чата
st.title(f"💬 {current_chat['name']}")

for msg in current_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Отправка сообщений
if prompt := st.chat_input("Задайте вопрос..."):
    current_chat["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("MVN AI думает..."):
            try:
                # Отправка запроса в Gemini 1.5 Flash
                response = model.generate_content(prompt)
                st.markdown(response.text)
                current_chat["messages"].append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Ошибка подключения: {e}")
