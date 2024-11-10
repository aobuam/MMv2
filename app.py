import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from render import bot_msg_container_html_template, user_msg_container_html_template
from utils import semantic_search
import prompts
from pinecone import Pinecone

# Set up OpenAI API client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize Pinecone
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pc.Index(st.secrets["PINECONE_INDEX_NAME"])

# Set page configuration for wide mode
st.set_page_config(layout="wide")

# CSS pour réduire la marge au-dessus de la page
st.markdown("""
    <style>
    /* Réduit la marge en haut de la page */
    .main > div:first-child {
        padding-top: 10px; /* Ajustez cette valeur pour réduire davantage l'espace */
    }
    </style>
""", unsafe_allow_html=True)


# CSS for rounded images, centering buttons, and reduced spacing
st.markdown("""
    <style>
    .rounded-image {
        border-radius: 15px;
    }
    .center-buttons {
        display: flex;
        justify-content: center;
        margin-top: 10px;  /* Reduced top margin */
    }
    .section-title {
        margin-top: 5px;  /* Reduced space above section title */
        margin-bottom: 5px;  /* Reduced space below section title */
    }
    .navigation-buttons {
        margin-top: 10px;  /* Reduced margin between carousel and navigation buttons */
    }
    .chatbot-header {
        margin-top: 10px;  /* Reduced margin between buttons and chatbot header */
    }
    </style>
""", unsafe_allow_html=True)

# Display section title with reduced spacing
st.markdown("<h3 class='section-title'>Explorez nos ressources</h3>", unsafe_allow_html=True)

# List of cards data
cards = [
    {"title": "SchoolMaker GPT", "image": "https://media.licdn.com/dms/image/v2/C4E0BAQEj1DkU-8VdtQ/company-logo_200_200/company-logo_200_200/0/1654766423629/schoolmaker_logo?e=2147483647&v=beta&t=9nJbyWSEZkZJ_jh5-RWUmNg6CwoPNkIt0oe4D5CQnUY"},
    {"title": "YouTube Mania GPT", "image": "https://lh3.googleusercontent.com/k2Vw-rykiufJIydl9cB0rY5BAHpAJRcgVbF-AvlJZNYW0_57StDE8hpcWAYDwjpKgs_rUX9W-sMkoqCxf-r4mDEq4l5dcW3yt9wu=w274"},
    {"title": "École des Copywriters GPT", "image": "https://lh3.googleusercontent.com/zbBHJ5GJpGiEzai9k3BR855-gI17FLRyfR9WBsHMLdnQV1t3YZVGPj1l0qnEFcVp5RZlfna3jpE9lvWjiLovnDusi34PrEKNs8w=w274"},
    {"title": "Méthode des 90 jours GPT", "image": "https://lh3.googleusercontent.com/7yIocV0NcUw5wIsPNwvLO3RpXlCgyTk6dGqguxfdLTwSZGMfunWlicziTnXScQI2c4GANwVti6_VmPBAKv2ZDA=w263"},
    {"title": "Copywriting Mania GPT", "image": "https://lh3.googleusercontent.com/U72_sLnxqs2SiBVlTJ6TNwNp7naH2PeopVbsl7_kk2KdaBVyO7GSiRnJoeIYv9735cUVjUO1OKvStjdbUeS_N-w=w263"},
    {"title": "Le Délic GPT", "image": "https://lh3.googleusercontent.com/Rh9uaJ1tbXir3049xk5TiS2qjNlVBZCDHAocNDbGEq9iiUVr4TVXXGRxfNiaNR20-IVH8Moq5ccLi2hktRjdmw=w263"},
    {"title": "La Solution GPT", "image": "https://lh3.googleusercontent.com/j3i4iwwqfFFwC-S5PVzwFdGN8pgFM-5R4hvE-tdCpGZJqWDoI3LcJ5s-v-L44N9OepdMn4vBMsZGxtSmEuQoyg=s0"},
    {"title": "Le Tremplin GPT", "image": "https://lh3.googleusercontent.com/vbnmWOhLBH-0XEEh-cqYoMv_z-pYBZ6vuCAUoyoVYkyllAeTN1oIhtY3hZCC2SVGIYzJhBf-h6rrgZnM6ZnxMWsfL6rDtW-mMGLt=w274"},
    {"title": "La Fusée GPT", "image": "https://lh3.googleusercontent.com/eCpmOKzPsBVo6FBnMf5klC9ZQLyERveeI9dJ9-_ua2NON_w7SLqmH2Db5K2dgdPw2h2i9_YzYncWZSJCT9qgAu6puw8tUcAT9u9V=w274"},
    {"title": "Le Système GPT", "image": "https://lh3.googleusercontent.com/W2Ly4R_AILehVEMsCQjbe08gtounyVKeiyCPK9MWipJOebCjWEUQ73Y1Ypohas5gbhCaqDYN5OtwOzPCQIKJZw=w263"},
]

# Initialize the carousel index in session state
if "carousel_index" not in st.session_state:
    st.session_state.carousel_index = 0

# Functions to handle carousel navigation
def next_cards():
    if st.session_state.carousel_index < len(cards) - 4:
        st.session_state.carousel_index += 4

def previous_cards():
    if st.session_state.carousel_index > 0:
        st.session_state.carousel_index -= 4

# Display 4 cards side by side
current_cards = cards[st.session_state.carousel_index:st.session_state.carousel_index + 4]
card_columns = st.columns(4)
for i, card in enumerate(current_cards):
    with card_columns[i]:
        # Encapsule l'image et le bouton dans un conteneur centré
        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="{card['image']}" style="width:150px; border-radius: 10px; margin-bottom: 10px;">
                <button style="padding: 5px 20px; margin-top: 10px; border: 1px solid #888888; background-color: transparent; color: black; border-radius: 5px;">
                    Ask {card['title']}
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )

# Left and right aligned navigation buttons using columns with additional margin for alignment
col1, col_spacer, col2 = st.columns([1, 4, 1])

# Bouton "Précédent" dans la colonne de gauche avec marge pour alignement
with col1:
    if st.session_state.carousel_index > 0:
        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)  # Ajout de marge verticale pour l'alignement
        st.button("<< Précédent", on_click=previous_cards)

# Espace entre les boutons
with col_spacer:
    st.write("")

# Bouton "Suivant" dans la colonne de droite
with col2:
    if st.session_state.carousel_index < len(cards) - 4:
        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)  # Ajout de marge verticale pour l'alignement
        st.button("Suivant >>", on_click=next_cards)

# Chatbot functionality with reduced margin
st.markdown("<h2 class='chatbot-header'>Marketing Mania GPT - Basé sur les vidéos de Stan</h2>", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

def construct_messages(history):
    messages = [{"role": "system", "content": prompts.system_message}]
    for entry in history:
        role = "user" if entry["is_user"] else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    return messages

def generate_response():
    st.session_state.history.append({
        "message": st.session_state.prompt,
        "is_user": True
    })
    search_results = semantic_search(st.session_state.prompt, index, top_k=3)
    context = ""
    for i, (title, transcript) in enumerate(search_results):
        context += f"Snippet from: {title}\n {transcript}\n\n"
    query_with_context = prompts.human_template.format(
        query=st.session_state.prompt,
        context=context
    )
    messages = construct_messages(st.session_state.history)
    messages.append({"role": "user", "content": query_with_context})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    bot_response = response.choices[0].message.content
    st.session_state.history.append({
        "message": bot_response,
        "is_user": False
    })
    st.session_state.prompt = ""

user_prompt = st.text_input(
    "Posez votre question :",
    key="prompt",
    placeholder="ex: 'Comment maximiser mes abonnés ?'",
    on_change=generate_response
)

for i in range(len(st.session_state.history) - 1, -1, -2):
    if i > 0 and st.session_state.history[i - 1]["is_user"]:
        st.write(
            user_msg_container_html_template.replace("$MSG", st.session_state.history[i - 1]["message"]),
            unsafe_allow_html=True
        )
    if i < len(st.session_state.history) and not st.session_state.history[i]["is_user"]:
        st.write(
            bot_msg_container_html_template.replace("$MSG", st.session_state.history[i]["message"]),
            unsafe_allow_html=True
        )
