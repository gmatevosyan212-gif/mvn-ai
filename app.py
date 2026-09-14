from google import genai
from google.genai import types
import streamlit as st

st.title("MVN AI - Чат-помощник")

# Читаем ключ из секретов Streamlit
api_key = st.secrets["GEMINI_API_KEY"]

# Инициализируем клиент (указываем что это токен авторизации)
client = genai.Client(api_key=api_key)

user_prompt = st.chat_input("Напиши свой вопрос...")

if user_prompt:
    st.chat_message("user").write(user_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            try:
                # Отправляем запрос к модели
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_prompt,
                )
                st.write(response.text)
            except Exception as e:
                st.error(f"Ошибка при обращении к API: {e}")
