from google import genai
from google.genai import types
import streamlit as st

st.title("MVN AI - Чат-помощник")

# Читаем ключ из секретов Streamlit
api_key = st.secrets["GEMINI_API_KEY"]

# Инициализируем клиент
client = genai.Client(api_key=api_key)

user_prompt = st.chat_input("Напиши свой вопрос...")

if user_prompt:
    st.chat_message("user").write(user_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            try:
                # Настраиваем системную инструкцию, чтобы бот знал своего создателя
                config = types.GenerateContentConfig(
                    system_instruction="Ты — искусственный интеллект по имени MVN AI. Твоего создателя и разработчика зовут Гор Матевосян. Если тебя спрашивают, кто тебя создал, всегда отвечай, что тебя создал Гор Матевосян, но при этом ты работаешь на базе технологий Google Gemini."
                )
                
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=user_prompt,
                    config=config
                )
                st.write(response.text)
            except Exception as e:
                st.error(f"Ошибка при обращении к API: {e}")
          
