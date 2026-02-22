import streamlit as st
from datetime import date
from markdown import markdown
import get_news
from translator import translate_news_to_chinese, save_translation_to_txt
import re

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

default_date = date.today()
selected_date = st.date_input(
    "Date / 日期:",
    default_date
)

# Initialize session state variables
if "news_data" not in st.session_state:
    st.session_state.news_data = None
if "display_titles" not in st.session_state:
    st.session_state.display_titles = None
if "txt_content" not in st.session_state:
    st.session_state.txt_content = None
if "button_label" not in st.session_state:
    st.session_state.button_label = None

col_start, col_download, col_spacer = st.columns([2, 3, 5])

with col_start:
    start_btn = st.button("Start", type="primary")

dl_placeholder = col_download.empty()

# get news
if start_btn:
    captured_urls = []
    orig_markdown = st.markdown
    orig_write = st.write
    orig_divider = st.divider
    
    def catch_output(*args, **kwargs):
        for arg in args:
            # clean and store URLs
            urls = re.findall(r'(https?://[^\s\)<>\]\[\'"]+)', str(arg))
            for found_url in urls:
                if found_url not in captured_urls:
                    captured_urls.append(found_url)
                    
    st.markdown = catch_output
    st.write = catch_output

    with st.spinner(f"FETCHING NEWS ON {selected_date} ......"):
        try:
            news_es = get_news.from_energystorage(selected_date)
            news_ek = get_news.from_electrek(selected_date)
            all_news_en = news_es + news_ek
        except Exception as e:
            orig_write(f"Fetch Error: {e}")
            all_news_en = []
        finally:
            st.markdown = orig_markdown
            st.write = orig_write
            st.divider = orig_divider

    if not all_news_en:
        st.warning(f"NO NEWS ON {selected_date} - PLEASE CHANGE THE DATE")
        st.session_state.news_data = None
    else:
        processed_news = []
        for i, item in enumerate(all_news_en):
            raw_text = str(item)
            
            url = captured_urls[i] if i < len(captured_urls) else ""
            
            if not url:
                url_match = re.search(r'(https?://[^\s\)<>\]\[\'"]+)', raw_text)
                if url_match:
                    url = url_match.group(1)
            
            clean_title = raw_text
            if url:
                clean_title = clean_title.replace(url, "")
            
            # Cleanup residual markdown links
            clean_title = clean_title.replace("**", "")
            clean_title = re.sub(r'\[\s*\]\(\s*\)', '', clean_title)
            clean_title = clean_title.strip()
            
            processed_news.append({"title": clean_title, "url": url})

        display_titles = []
        if lang_choice == "中文":
            with st.spinner("翻译中，请等待 ......"):
                titles_to_translate = [n["title"] for n in processed_news]
                translated_data = translate_news_to_chinese(titles_to_translate)
                
                if isinstance(translated_data, str):
                    # split numbered list
                    split_items = re.split(r'\n?\d+\.\s*', translated_data)
                    display_titles = [p.strip() for p in split_items if p.strip()]
                else:
                    display_titles = translated_data
        else:
            display_titles = [n["title"] for n in processed_news]

        download_lines = []
        for i, news_item in enumerate(processed_news):
            title_to_show = display_titles[i] if i < len(display_titles) else news_item["title"]
            download_lines.append(f"{i+1}. {title_to_show}")

        txt_content = "\n\n".join(download_lines)
        button_label = "下载 中文.txt" if lang_choice == "中文" else "Download English.txt"
        
        # Save to Session State
        st.session_state.news_data = processed_news
        st.session_state.display_titles = display_titles
        st.session_state.txt_content = txt_content
        st.session_state.button_label = button_label

if st.session_state.news_data:
    dl_placeholder.download_button(
        label=st.session_state.button_label,
        data=st.session_state.txt_content,
        file_name=f"news_{selected_date}_{lang_choice.lower()}.txt",
        mime="text/plain"
    )

    for i, news_item in enumerate(st.session_state.news_data):
        title_to_show = st.session_state.display_titles[i] if i < len(st.session_state.display_titles) else news_item["title"]
        url = news_item["url"]

        st.markdown(f"**{title_to_show}**")
        if url:
            st.markdown(url)
        st.divider()