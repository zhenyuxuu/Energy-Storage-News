import streamlit as st
from datetime import date
from markdown import markdown
import get_news

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
        except:
            st.warning(f"NO NEWS ON {selected_date} - PLEASE CHANGE THE DATE")
