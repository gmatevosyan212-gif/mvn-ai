import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="MVN AI", page_icon="🤖")

st.title("🤖 MVN AI")
st.write("Ваш умный ИИ-помощник")

# Настройка API ключа из Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Пожалуйста, добавьте GEMINI_API_KEY в Secrets приложения.")

# Инициализация модели
model = genai.GenerativeModel("gemini-1.5-flash")

# История сообщений
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение истории
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле для ввода от пользователя
if prompt := st.chat_input("Задайте вопрос..."):
    safe_prompt = str(prompt)

    st.session_state.messages.append({"role": "user", "content": safe_prompt})
    with st.chat_message("user"):
        st.markdown(safe_prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(safe_prompt)
            st.markdown(response.text)
            st.session_state.messages.append(
                {"role": "assistant", "content": response.text}
            )
        except Exception as e:
            st.error(f"Ошибка при получении ответа: {e}")
