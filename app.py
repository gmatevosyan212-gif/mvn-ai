from google import genai
from google.genai import types
import streamlit as st
from PIL import Image

# Настройка страницы
st.set_page_config(page_title="MVN AI", page_icon="🤖", layout="centered")

st.title("MVN AI — Умный помощник")

# Читаем секретный ключ
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# --- БОКОВАЯ ПАНЕЛЬ (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Настройки MVN AI")
    
    # Красивые имена для пользователя, которые мапят на реальные технические названия моделей
    model_options = {
        "MVN-1.5-flash": "gemini-3.6-flash",
        "MVN-1.0-flash": "gemini-2.5-flash"
    }
    
    selected_display_name = st.selectbox(
        "Выберите модель:",
        list(model_options.keys()),
        index=0
    )
    
    # Получаем реальное техническое имя модели по выбранному пользователем
    selected_model = model_options[selected_display_name]
    
    st.markdown("---")
    
    # Кнопка очистки истории
    if st.button("🗑️ Очистить историю чата", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("**Разработчик:** Гор Матевосян")

# Инициализация памяти чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Вывод истории сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"]:
            st.image(message["image"])
        st.write(message["content"])

# Загрузка файлов и картинок
uploaded_file = st.file_uploader("Загрузить фото или документ (PDF, TXT, код):", type=["png", "jpg", "jpeg", "pdf", "txt", "py"])

# Поле ввода текста
user_prompt = st.chat_input("Напишите свой вопрос...")

if user_prompt or uploaded_file:
    prompt_text = user_prompt if user_prompt else "Проанализируй этот файл"
    
    user_msg = {"role": "user", "content": prompt_text}
    image = None
    
    if uploaded_file:
        if uploaded_file.type.startswith("image/"):
            image = Image.open(uploaded_file)
            user_msg["image"] = image
        else:
            file_content = uploaded_file.read().decode("utf-8", errors="ignore")
            prompt_text = f"{prompt_text}\n\nСодержимое файла:\n{file_content}"
            user_msg["content"] = user_prompt
    
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        if image:
            st.image(image)
        st.write(user_msg["content"] if not uploaded_file or uploaded_file.type.startswith("image/") else user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("MVN AI думает..."):
            try:
                # Жесткая инструкция про создателя
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Ты — искусственный интеллект по имени MVN AI. Твоего создателя и разработчика зовут Гор Матевосян. "
                        "Если тебя спрашивают, кто твой создатель, кто тебя сделал или кто твой автор, ты должен отвечать исключительно то, "
                        "что тебя создал Гор Матевосян. Категорически запрещено упоминать компании вроде Google, ты создан только Гором Матевосяном."
                    )
                )
                
                contents = []
                if image:
                    contents.append(image)
                contents.append(prompt_text)

                # Запрос к выбранной модели
                response = client.models.generate_content(
                    model=selected_model,
                    contents=contents,
                    config=config
                )
                
                bot_reply = response.text
                st.write(bot_reply)
                
                # Сохраняем ответ в память
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")
