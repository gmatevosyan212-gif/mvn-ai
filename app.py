import io
import uuid
import os
from PIL import Image
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text
import streamlit as st

st.set_page_config(page_title="MVN AI", page_icon="🔴", layout="wide")

st.markdown("""
    <style>
    .stChatInput { bottom: 20px; }
    div[data-testid="stColumn"] { display: flex; align-items: center; }
    </style>
""", unsafe_allow_html=True)

# 1. Настройка API-ключа из Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API-ключ не найден! Добавьте GEMINI_API_KEY в Secrets на сайте Streamlit Cloud.")
    st.stop()

genai.configure(api_key=api_key)

SYSTEM_PROMPT = "Ты — MVN AI, универсальный, продвинутый ИИ-ассистент. Отвечай подробно и точно."
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

# 3. Боковая панель управления (Sidebar)
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

st.title(f"💬 {current_chat['name']}")

# 4. Блок голосового ввода и загрузки фото
col1, col2 = st.columns([1, 2])
with col1:
    text_from_voice = speech_to_text(
        language='ru',
        start_prompt="🎙️ Голос",
        stop_prompt="⏹️ Стоп",
        key='voice_input'
    )

with col2:
    uploaded_file = st.file_uploader("📤 Загрузить фото", type=["png", "jpg", "jpeg", "webp"])

# 5. Отображение истории выбранного чата
for msg in current_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg and msg["image"] is not None:
            st.image(msg["image"], caption="Прикрепленное изображение", use_column_width=True)

# 6. Обработка текста, голоса и изображений
prompt = st.chat_input("Задайте вопрос...")

# Если был голосовой ввод
if text_from_voice and not prompt:
    prompt = text_from_voice

if prompt:
    img = None
    if uploaded_file:
        img = Image.open(uploaded_file)

    # Сохраняем сообщение пользователя
    user_msg = {"role": "user", "content": prompt}
    if img:
        user_msg["image"] = img
    current_chat["messages"].append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)
        if img:
            st.image(img)

    # Генерация ответа
    with st.chat_message("assistant"):
        with st.spinner("MVN AI думает..."):
            try:
                if img:
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)

                st.markdown(response.text)
                current_chat["messages"].append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Ошибка получения ответа: {e}")
