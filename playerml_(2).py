import streamlit as st
from PIL import Image
import json
import re
import requests
import tensorflow as tf 
import google.generativeai as genai

# MODEL DOWNLOAD & LOAD (just after imports)
url = "
https://huggingface.co/ieeeAB/chess_model.h5/resolve/main/chess_model.h5" 
response = requests.get(url)
with open("chess_model.h5", "wb") as f:
    f.write(response.content)

model = tf.keras.models.load_model("chess_model.h5")
# Gemini API setup
genai.configure(api_key="AIzaSyD_ttXOxFAW6KTEzMWz8QyEcdH9cWUza-k")  # Replace this!
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Gemini logic
def get_gemini_insight(image):
    prompt = """
You are a chess engine assistant. Given the image of a chess board, analyze it and provide this output in pure JSON format:

{
  "leader": "<White/Black/Equal>",
  "white_score": <int>,
  "black_score": <int>,
  "leading_by": <int>,
  "suggestion": "<1-2 sentence strategic advice>"
}

Examples:

Example 1:
Board: White has all pieces, Black lost queen and rook
Output:
{
  "leader": "White",
  "white_score": 38,
  "black_score": 24,
  "leading_by": 14,
  "suggestion": "White should trade pieces and simplify into a winning endgame."
}

Example 2:
Board: Black has queen and 2 rooks, White lost both rooks
Output:
{
  "leader": "Black",
  "white_score": 26,
  "black_score": 36,
  "leading_by": 10,
  "suggestion": "Black should maintain pressure and avoid unnecessary trades."
}

Now analyze this board and return only the JSON:
"""
    response = model.generate_content([prompt, image])
    clean_response = re.sub(r"```json|```", "", response.text).strip()
    try:
        return json.loads(clean_response)
    except:
        return {
            "leader": "Unknown",
            "white_score": 0,
            "black_score": 0,
            "leading_by": 0,
            "suggestion": "Parsing failed. Check board clarity."
        }

# Streamlit UI
st.set_page_config(page_title="Chess Scoreboard", layout="centered")
st.title("♟️ Real-Time Chess Scoreboard")

image = st.camera_input("📸 Capture the current board position")

if image:
    board_img = Image.open(image)
    result = get_gemini_insight(board_img)

    col1, col2 = st.columns(2)
    col1.metric("White (You)", result["white_score"])
    col2.metric("Black (Friend)", result["black_score"])

    st.markdown(f"""
    ### 🏆 Leader: {result['leader']}
    > _{result['suggestion']}_
    """)

