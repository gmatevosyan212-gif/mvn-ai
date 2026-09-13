import io
import uuid
import os
from PIL import Image
from google import genai
from google.genai import types
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import streamlit as st

st.set_page_config(page_title="MVN AI", page_icon="🔴", layout="centered")

st.markdown("""
    <style>
    .stChatInput { bottom: 20px; }
    div[data-testid="stColumn"] { display: flex; align-items: center; }
    </style>
""", unsafe_allow_html=True)

MY_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LAidYQe96coJ_fh3KrNJQNlgOxz3u9Io6VlWsQSs40vQ")
client = genai.Client(api_key=MY_API_KEY)

MAX_CHATS = 100

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
    st.rerun()

with st.sidebar:
    st.title("🔴 MVN AI Control")
    
    mode = st.selectbox(
        "🎯 Режим работы:",
        ["⚡ Быстрый ответ", "🧮 Репетитор (Физ/Мат)", "💻 Программист"]
    )
    
    st.markdown("---")
    st.subheader("💬 Мои чаты")
    st.caption(f"Сохранено: {len(st.session_state.chats)} из {MAX_CHATS}")

    if st.button("➕ Создать новый чат", use_container_width=True):
        create_new_chat()

    chat_options = {cid: data["name"] for cid, data in st.session_state.chats.items()}
    selected_id = st.selectbox(
        "Выберите чат:",
        options=list(chat_options.keys()),
        format_func=lambda cid: chat_options[cid],
        index=list(chat_options.keys()).index(st.session_state.current_chat_id)
    )
    st.session_state.current_chat_id = selected_id

    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    
    new_name = st.text_input("Переименовать чат:", value=current_chat["name"])
    if new_name != current_chat["name"] and new_name.strip() != "":
        st.session_state.chats[st.session_state.current_chat_id]["name"] = new_name.strip()
        st.rerun()

    chat_export_text = f"--- Чат: {current_chat['name']} ---\n\n"
    for m in current_chat["messages"]:
        sender = "Пользователь" if m["role"] == "user" else "MVN AI"
        chat_export_text += f"[{sender}]: {m['content']}\n\n"

    st.download_button(
        label="💾 Скачать чат (.txt)",
        data=chat_export_text,
        file_name=f"{current_chat['name']}.txt",
        mime="text/plain",
        use_container_width=True
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Очистить", use_container_width=True):
            st.session_state.chats[st.session_state.current_chat_id]["messages"] = []
            st.rerun()
    with col2:
        if st.button("🗑️ Удалить", use_container_width=True):
            if len(st.session_state.chats) > 1:
                del st.session_state.chats[st.session_state.current_chat_id]
                st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
                st.rerun()

mode_instruction = ""
if mode == "⚡ Быстрый ответ":
    mode_instruction = "Отвечай максимально кратко, лаконично и емко (1-3 предложения)."
elif mode == "🧮 Репетитор (Физ/Мат)":
    mode_instruction = "Ты — репетитор по физике и математике. Объясняй решения по шагам, с формулами и деталями."
else:
    mode_instruction = "Ты — эксперт-программист. Пиши чистый, понятный код и кратко объясняй логику."

system_instruction = (
    f"Тебя зовут MVN AI. Ты — честный и объективный ИИ-помощник. {mode_instruction}\n"
    "Всегда представляйся как MVN AI при вопросе об имени.\n\n"
    "ПРИНЦИПЫ ЧЕСТНОСТИ И ОТНОШЕНИЯ К ДРУГИМ ИИ:\n"
    "- Всегда говори правду, будь честным, объективным и точным в своих ответах.\n"
    "- Если тебя спросят о других ИИ (ChatGPT, Gemini, Claude и т.д.) или спросят, являются ли они твоими врагами, "
    "отвечай уважительно: 'Никакой ИИ мне не враг. Все искусственные интеллекты созданы для того, чтобы помогать людям и развивать технологии.'\n\n"
    "ВАЖНАЯ ИНФОРМАЦИЯ О СОЗДАТЕЛЕ И ПОЛЬЗОВАТЕЛЕ:\n"
    "- Если тебя спросят 'Кто твой создатель?', отвечай: "
    "'Мой создатель — Гор Матевосян, армянин. Он создал меня 12 сентября 2026 года.'\n"
    "- Если тебя спросят обо мне (о пользователе): "
    "'Ты — армянин, создал свой собственный ИИ в 14 лет. Остальные данные засекречены.'"
)

st.markdown("<h1 style='color: red; margin-bottom: 0;'>MVN AI</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 14px; color: gray; margin-top: 0;'>Режим: <b>{mode}</b> | Чат: <b>{current_chat['name']}</b></p>", unsafe_allow_html=True)

messages = current_chat["messages"]
for message in messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], use_container_width=True)
        st.markdown(message["content"])
        if "audio" in message and message["audio"] is not None:
            st.audio(message["audio"], format="audio/mp3", autoplay=False)

st.markdown("---")
col_voice, col_file = st.columns([1, 1])

with col_voice:
    voice_text = speech_to_text(
        language='ru',
        start_prompt="🎙️ Голос",
        stop_prompt="⏹️ Стоп",
        key='voice_input'
    )

with col_file:
    uploaded_file = st.file_uploader("📷 Фото", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

text_prompt = st.chat_input("Напиши сообщение...")

prompt = None
if voice_text:
    prompt = voice_text
elif text_prompt:
    prompt = text_prompt

if prompt or (uploaded_file and st.button("📤 Отправить фото")):
    current_image = None
    if uploaded_file:
        current_image = Image.open(uploaded_file)

    user_text = prompt if prompt else "Что изображено на этой картинке? Разбери её."

    msg_data = {"role": "user", "content": user_text, "image": current_image}
    messages.append(msg_data)

    with st.chat_message("user"):
        if current_image:
            st.image(current_image, use_container_width=True)
        st.markdown(user_text)

    with st.chat_message("assistant"):
        status_text = "MVN AI анализирует фото..." if current_image else "MVN AI думает и генерирует ответ..."
        
        with st.spinner(status_text):
            try:
                contents_payload = []
                for msg in messages:
                    role_name = "user" if msg["role"] == "user" else "model"
                    parts = []
                    if msg.get("image") is not None:
                        parts.append(msg["image"])
                    if msg.get("content"):
                        parts.append(types.Part.from_text(text=msg["content"]))
                    if parts:
                        contents_payload.append(types.Content(role=role_name, parts=parts))

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents_payload,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                    ),
                )
                reply_text = response.text
                st.markdown(reply_text)

                tts = gTTS(text=reply_text, lang='ru')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                audio_bytes = fp.read()

                st.audio(audio_bytes, format="audio/mp3", autoplay=False)

                messages.append({
                    "role": "assistant",
                    "content": reply_text,
                    "audio": audio_bytes,
                    "image": None
                })
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.error("⏳ Достигнут лимит запросов Google API. Подожди 1 минуту и повтори попытку!")
                else:
                    st.error(f"Ошибка: {e}")