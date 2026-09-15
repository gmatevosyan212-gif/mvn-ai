from google import genai
from google.genai import types
import streamlit as st
from PIL import Image

st.title("MVN AI - Чат-помощник")

# Читаем ключ из секретов
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Память чата, чтобы сообщения не пропадали
if "messages" not in st.session_state:
    st.session_state.messages = []

# Выводим всю историю сообщений на экран
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"]:
            st.image(message["image"])
        st.write(message["content"])

# Кнопка для загрузки фото
uploaded_file = st.file_uploader("Загрузить фото (необязательно)", type=["png", "jpg", "jpeg"])

# Поле ввода текста
user_prompt = st.chat_input("Напиши свой вопрос...")

if user_prompt or uploaded_file:
    prompt_text = user_prompt if user_prompt else "Опиши это изображение"
    
    # Сохраняем сообщение пользователя
    user_msg = {"role": "user", "content": prompt_text}
    image = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        user_msg["image"] = image
    
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        if uploaded_file:
            st.image(image)
        st.write(prompt_text)

    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            try:
                # Жесткая инструкция: создатель ТОЛЬКО Гор Матевосян, ни слова про Google
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Ты — искусственный интеллект по имени MVN AI. Твоего создателя и разработчика зовут Гор Матевосян. "
                        "Если тебя спрашивают, кто твой создатель, кто тебя сделал или кто твой автор, ты должен отвечать исключительно то, "
                        "что тебя создал Гор Матевосян. Категорически запрещено упоминать компании вроде Google или любые другие упоминания, "
                        "ты создан только Гором Матевосяном."
                    )
                )
                
                # Собираем данные для отправки (текст + фото, если есть)
                contents = []
                if uploaded_file:
                    contents.append(image)
                contents.append(prompt_text)

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=config
                )
                
                bot_reply = response.text
                st.write(bot_reply)
                
                # Сохраняем ответ бота в память
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
            except Exception as e:
                st.error(f"Ошибка: {e}")
