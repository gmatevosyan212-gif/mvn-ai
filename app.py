import streamlit as st
import google.generativeai as genai
import requests
import base64

# 1. Настройка страницы Streamlit
st.set_page_config(
    page_title="MVN AI",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 MVN AI")
st.caption("Ваш умный ИИ-помощник")

# 2. Проверка и подключение API-ключа Gemini из Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Ошибка: API-ключ не найден! Добавьте GEMINI_API_KEY в Secrets на сайте Streamlit.")
    st.stop()

# 3. Настройка системной инструкции и инициализация актуальной модели
SYSTEM_PROMPT = """
Ты — MVN AI, универсальный, продвинутый и автономный ИИ-ассистент.
Отвечай структурированно, понятно, вежливо и максимально полно на любые вопросы пользователя.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# 4. Инициализация истории чата в сессии
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Отображение сохранённых сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"])

# 6. Обработка ввода пользователя
if prompt := st.chat_input("Задайте вопрос..."):
    # Отображаем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ответ ИИ
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Проверка запроса на генерацию изображений
        image_keywords = ["нарисуй", "сгенерируй", "создай картинку", "draw", "image", "картинка"]
        if any(keyword in prompt.lower() for keyword in image_keywords):
            try:
                with st.spinner("Генерирую изображение..."):
                    clean_prompt = prompt.replace(" ", "%20")
                    img_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=800&height=800&nologo=true"
                    res = requests.get(img_url)
                    
                    if res.status_code == 200:
                        st.image(res.content, caption=f"Запрос: {prompt}")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Вот изображение по вашему запросу: **{prompt}**",
                            "image": res.content
                        })
                    else:
                        st.error("Не удалось сгенерировать картинку. Попробуйте другой запрос.")
            except Exception as e:
                st.error(f"Ошибка при генерации картинки: {e}")
        else:
            # Текстовый генератор через Gemini 1.5 Flash
            try:
                with st.spinner("MVN AI думает..."):
                    # Формируем историю для модели
                    formatted_history = []
                    for msg in st.session_state.messages[:-1]:
                        if "content" in msg and msg["content"]:
                            role = "user" if msg["role"] == "user" else "model"
                            formatted_history.append({"role": role, "parts": [msg["content"]]})
                    
                    chat = model.start_chat(history=formatted_history)
                    response = chat.send_message(prompt)
                    
                    message_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Ошибка подключения к Gemini API: {e}")
