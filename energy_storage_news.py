import streamlit as st
from datetime import date
from markdown import markdown
import get_news
from translator import translate_news_to_chinese, save_translation_to_txt

st.title(":mailbox: Energy Storage & EV News")
st.markdown(markdown(), unsafe_allow_html=True)

lang_choice = st.selectbox(
    "Language / 语言:",
    options=["English", "Chinese"],
    index=0
)

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
            all_news_en = news_es + news_ek

            if not all_news_en:
                st.warning(f"NO NEWS ON {selected_date} - PLEASE CHANGE THE DATE")
            else:
                display_text = ""

                if lang_choice == "Chinese":
                    display_text = translate_news_to_chinese(all_news_en)
                else:
                    display_text = "\n\n".join([f"{i+1}. {item}" for i, item in enumerate(all_news_en)])

                st.download_button(
                    label=f"Download {lang_choice} .txt",
                    data=display_text,
                    file_name=f"news_{selected_date}_{lang_choice.lower()}.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"Error: {e}")