import os
import streamlit as st
import google.genai as genai

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

def translate_news_to_chinese(news_list):
    if not news_list:
        return "No news found."

    # Format the input list for the prompt
    news_input = "\n".join([f"{i+1}. {text}" for i, text in enumerate(news_list)])
    
    prompt = f"""
Please translate the following news into Chinese. The results should be 1-to-1 matching the input order and do not generate duplicated output. Make it easy to understand and make one line space between every news that got translated into Chinese. Please do not elaborate or expand further on the contents, just translate every single one and mark every news in numeric order from 1 to the total number of news.

News content:
{news_input}
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Translation failed: {str(e)}"

def save_translation_to_txt(content, date_obj):
    """Saves the content to a .txt file named by date."""
    filename = f"translation_{date_obj.strftime('%Y-%m-%d')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename