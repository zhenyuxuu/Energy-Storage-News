import re
from datetime import date
import streamlit as st
from markdown import markdown
import get_news
import translator

col_title, col_lang = st.columns([4, 1])

with col_title:
    st.header(":mailbox: Energy Storage & EV News")
    st.markdown(markdown(), unsafe_allow_html=True)

with col_lang:
    lang_choice = st.selectbox(
        "Language / 语言:",
        options=["English", "中文"],
        index=0
    )

selected_date = st.date_input("Date / 日期:", date.today())

# Session State
session_keys = ["raw_news", "display_news", "download_news", "button_label"]
for key in session_keys:
    if key not in st.session_state:
        st.session_state[key] = None


col_start, col_download, col_spacer = st.columns([2, 3, 5])

with col_start:
    start_btn = st.button("Start / 开始", type="primary")

dl_placeholder = col_download.empty()

if start_btn:
    with st.spinner(f"FETCHING NEWS ON {selected_date} ......"):
        try:
            news_es = get_news.from_energystorage(selected_date)
            news_ek = get_news.from_electrek(selected_date)
            
            all_news = news_es + news_ek
        except Exception as e:
            st.error(f"Fetch Error: {e}")
            all_news = []

    if not all_news:
        st.warning(f"NO NEWS ON {selected_date} - PLEASE CHANGE THE DATE")
        st.session_state.news_data = None
    else:
        display_news = []
        if lang_choice == "中文":
            with st.spinner("翻译中，请等待 ......"):
                news_en = [n.get("summary", "") for n in all_news]
                news_cn = translator.to_chinese(news_en)

                split_news = re.split(r'(?:^|\n)\s*\d+\.\s*', news_cn)
                display_news = [p.strip() for p in split_news if p.strip()]
        else:
            display_news = [n.get("summary", "") for n in all_news]

        formatted_news = [f"{i+1}. {news_item}" for i, news_item in enumerate(display_news)]

        # Update Session State
        st.session_state.raw_news = all_news
        st.session_state.display_news = display_news
        st.session_state.download_news = "\n\n".join(formatted_news)
        st.session_state.button_label = "下载全部新闻" if lang_choice == "中文" else "Download All News"

if st.session_state.raw_news:
    dl_placeholder.download_button(
        label=st.session_state.button_label,
        data=st.session_state.download_news,
        file_name=f"news_{selected_date}_{lang_choice.lower()}.txt",
        mime="text/plain"
    )

    for i, news_item in enumerate(st.session_state.raw_news):
        display_news_item = st.session_state.display_news[i]
            
        url = news_item["url"]

        st.markdown(f"**{display_news_item}**")
        if url:
            st.markdown(url)
        st.divider()