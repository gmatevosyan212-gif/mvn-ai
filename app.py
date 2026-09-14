from google import genai
import streamlit as st

st.title("MVN AI - Чат-помощник")

# Инициализируем клиента с новым ключом AQ... через официальную библиотеку
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Поле ввода текста от пользователя
user_prompt = st.chat_input("Напиши свой вопрос...")

if user_prompt:
    st.chat_message("user").write(user_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            # Отправляем запрос новой библиотекой (модель использует быстрый Flash)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
            )
            st.write(response.text)
