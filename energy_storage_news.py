import streamlit as st
from datetime import date
from markdown import markdown
import get_news
from translator import translate_news_to_chinese, save_translation_to_txt

st.title(":mailbox: Energy Storage & EV News")
st.markdown(markdown(), unsafe_allow_html=True)

default_date = date.today()
selected_date = st.date_input(
    "Which date are you interested?",
    default_date
)

# get news
if st.button("Start", type="primary"):
    with st.spinner(f"FETCHING NEWS ON {selected_date} ......"):
        try:
            news_es = get_news.from_energystorage(selected_date)
            news_ek = get_news.from_electrek(selected_date)
            all_news = news_es + news_ek

            if not all_news:
                st.warning(f"NO NEWS ON {selected_date} - PLEASE CHANGE THE DATE")
            else:
                with st.spinner("Translating and saving to local..."):
                    chinese_translation = translate_news_to_chinese(all_news)
                    
                    file_name = save_translation_to_txt(chinese_translation, selected_date)
                
                st.header("中文摘要 (Chinese Summary)")
                st.markdown(chinese_translation)

        except Exception as e:
            st.error(f"Error: {e}")