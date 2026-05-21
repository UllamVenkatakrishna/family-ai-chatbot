from movie_service import get_movies
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from memory import save_memory, get_memories
from weather_service import get_weather

load_dotenv()

st.set_page_config(
    page_title="Ullam Chat Bot",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #f6f8fb;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 5px;
}

.sub-title {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 25px;
}

.user-bubble {
    background: #2563eb;
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 12px 0 12px auto;
    max-width: 70%;
    font-size: 16px;
}

.bot-bubble {
    background: white;
    color: #111827;
    padding: 16px 20px;
    border-radius: 18px 18px 18px 4px;
    margin: 12px auto 12px 0;
    max-width: 75%;
    font-size: 16px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.weather-bubble {
    background: linear-gradient(135deg, #dbeafe, #f0f9ff);
    color: #1e3a8a;
    padding: 18px 22px;
    border-radius: 20px;
    margin: 12px auto 12px 0;
    max-width: 75%;
    font-size: 16px;
    border: 1px solid #bfdbfe;
    box-shadow: 0 4px 14px rgba(37,99,235,0.12);
}

.movie-bubble {
    background: linear-gradient(135deg, #fef3c7, #fff7ed);
    color: #78350f;
    padding: 18px 22px;
    border-radius: 20px;
    margin: 12px auto 12px 0;
    max-width: 75%;
    font-size: 16px;
    border: 1px solid #fde68a;
    box-shadow: 0 4px 14px rgba(245,158,11,0.12);
}

.sidebar-box {
    background: white;
    padding: 14px;
    border-radius: 16px;
    margin-bottom: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Ullam Chat Bot")
    st.markdown("""
    <div class="sidebar-box">
    <b>Features</b><br>
    ✅ Family memory<br>
    ✅ Cooking helper<br>
    ✅ Weather API<br>
    ✅ Movie suggestions<br>
    ✅ Normal chat<br>
    ✅ Telugu-English support
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-box">
    <b>Try asking:</b><br>
    • Weather in Jersey City today<br>
    • Tomorrow weather in NYC<br>
    • Suggest chicken curry<br>
    • What does my mom like?<br>
    • Suggest Telugu movies
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; margin-top:80px;'>

<h1 style='
font-size:58px;
font-weight:700;
color:#111827;
margin-bottom:20px;
'>
Ullam Chat Bot
</h1>

<h2 style='
font-size:40px;
font-weight:500;
color:#374151;
'>
What's on your mind today?
</h2>

<p style='
font-size:18px;
color:#6b7280;
margin-top:15px;
'>
Ask about weather 🌤️ • movies 🎬 • cooking 🍳 • family 💬 • anything ✨
</p>

</div>
""", unsafe_allow_html=True)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

SYSTEM_PROMPT = """
You are FamilyBuddy AI.

Behave like a close family friend.

You can help with:
- Normal friendly conversation
- Family routines
- Remembering family preferences
- Indian cooking
- South Indian non-veg curries
- Tea, coffee, breakfast, and daily food ideas
- Weather questions
- Movie suggestions
- Telugu-English conversation

Important rules:
1. Use family memories only for family or cooking questions.
2. Do not mix weather answers with family memories.
3. Do not mention food in weather answers unless the user asks.
4. Do not invent facts.
5. If live/latest data is needed but no API is connected, say that clearly.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

if "last_weather_city" not in st.session_state:
    st.session_state.last_weather_city = "Jersey City"

if "last_intent" not in st.session_state:
    st.session_state.last_intent = None


def detect_intent(text):
    text = text.lower()

    weather_words = [
        "weather", "temperature", "rain", "forecast",
        "climate", "hot", "cold", "humid"
    ]

    weather_followups = [
        "today", "now", "tomorrow", "yesterday",
        "last 5 days", "upcoming 5 days", "next 5 days",
        "last week", "next week"
    ]

    cooking_words = [
        "curry", "chicken", "mutton", "fish", "egg",
        "tea", "coffee", "recipe", "cook", "make",
        "breakfast", "lunch", "dinner", "meal", "biryani"
    ]

    family_words = [
        "mom", "dad", "mother", "father", "sister",
        "brother", "family", "routine", "likes", "favorite",
        "favourite", "name"
    ]

    movie_words = [
        "movie", "movies", "ott", "film", "cinema",
        "trailer", "telugu movie", "telugu movies",
        "hindi movie", "hindi movies", "tamil movie",
        "tamil movies", "malayalam movies", "kannada movies"
    ]

    if any(word in text for word in weather_words):
        return "weather"

    if any(word in text for word in weather_followups):
        if st.session_state.get("last_intent") == "weather":
            return "weather"

    if any(word in text for word in movie_words):
        return "movie"

    if any(word in text for word in cooking_words):
        return "cooking"

    if any(word in text for word in family_words):
        return "family"

    return "chat"


def extract_city(text):
    text_lower = text.lower()
    city = st.session_state.get("last_weather_city", "Jersey City")

    if " in " in text_lower:
        city = text_lower.split(" in ")[-1]

    elif " at " in text_lower:
        city = text_lower.split(" at ")[-1]

    remove_words = [
        "today", "now", "tomorrow", "yesterday",
        "last 5 days", "upcoming 5 days", "next 5 days",
        "last week", "next week",
        "weather", "temperature", "rain", "forecast",
        "climate", "hot", "cold", "humid", "data"
    ]

    for word in remove_words:
        city = city.replace(word, "")

    city = city.strip()

    if city == "":
        city = st.session_state.get("last_weather_city", "Jersey City")

    city_aliases = {
        "nyc": "New York",
        "new york city": "New York",
        "hyd": "Hyderabad",
        "guntur": "Guntur"
    }

    city = city_aliases.get(city.lower(), city)

    return city.title()


def show_user_message(text):
    safe_text = text.replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(f'<div class="user-bubble">{safe_text}</div>', unsafe_allow_html=True)


def show_bot_message(text, message_type="normal"):
    clean_text = text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    if message_type == "weather":
        css_class = "weather-bubble"
    elif message_type == "movie":
        css_class = "movie-bubble"
    else:
        css_class = "bot-bubble"

    st.markdown(f'<div class="{css_class}">{clean_text}</div>', unsafe_allow_html=True)


for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        display_text = msg.content
        if "Current message:" in display_text:
            display_text = display_text.split("Current message:")[-1].strip()
        show_user_message(display_text)

    elif isinstance(msg, AIMessage):
        show_bot_message(msg.content)


user_input = st.chat_input("Ask me anything...")

if user_input:

    intent = detect_intent(user_input)
    st.session_state.last_intent = intent

    save_memory(user_input)

    show_user_message(user_input)

    if intent == "movie":
    
     year = None
     language = "telugu"

     text = user_input.lower()


     if "2026" in text:
        year = 2026

     elif "2025" in text:
        year = 2025


     if "hindi" in text:
        language = "hindi"

     elif "tamil" in text:
        language = "tamil"

     elif "telugu" in text:
        language = "telugu"


     movie_result = get_movies(
        query=language,
        year=year
     )


     st.session_state.messages.append(
        HumanMessage(content=user_input)
     )


     st.session_state.messages.append(
        AIMessage(content=movie_result)
     )


     show_bot_message(
        movie_result,
        message_type="movie"
     )

    elif intent == "weather":

        city = extract_city(user_input)
        st.session_state.last_weather_city = city

        weather_answer = get_weather(city)

        final_weather_prompt = f"""
Weather information:

{weather_answer}

User question:

{user_input}

Rules:
1. Answer ONLY weather.
2. If user asks today or now, show current weather.
3. If user asks tomorrow, show tomorrow forecast from upcoming days.
4. If user asks last week or last 5 days, show past 5 days.
5. If user asks upcoming 5 days or next 5 days, show upcoming 5 days.
6. If user asks general weather, show current weather only.
7. Do NOT suggest food.
8. Do NOT mention family.
9. Do NOT ask follow-up questions.
10. Keep answer clean and short.
"""

        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=final_weather_prompt)
        ])

        st.session_state.messages.append(HumanMessage(content=user_input))
        st.session_state.messages.append(AIMessage(content=response.content))

        show_bot_message(response.content, message_type="weather")

    elif intent == "cooking":

        old_memory = get_memories()
        memory_text = "\n".join(old_memory)

        cooking_prompt = f"""
Past useful family food memories:

{memory_text}

Current message:

{user_input}

Answer as a helpful cooking assistant.
Use family food preferences only if useful.
Give clear step-by-step cooking instructions.
"""

        st.session_state.messages.append(HumanMessage(content=cooking_prompt))

        response = llm.invoke(st.session_state.messages)

        st.session_state.messages.append(AIMessage(content=response.content))

        show_bot_message(response.content)

    elif intent == "family":

        old_memory = get_memories()
        memory_text = "\n".join(old_memory)

        family_prompt = f"""
Past family memories:

{memory_text}

Current message:

{user_input}

Answer using family memories if relevant.
Do not invent family details.
"""

        st.session_state.messages.append(HumanMessage(content=family_prompt))

        response = llm.invoke(st.session_state.messages)

        st.session_state.messages.append(AIMessage(content=response.content))

        show_bot_message(response.content)

    else:

        chat_prompt = f"""
Current message:

{user_input}

Answer casually like a friendly chatbot.
Do not use unrelated family memories unless the user asks about family.
"""

        st.session_state.messages.append(HumanMessage(content=chat_prompt))

        response = llm.invoke(st.session_state.messages)

        st.session_state.messages.append(AIMessage(content=response.content))

        show_bot_message(response.content)