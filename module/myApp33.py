
import streamlit as st
import random

today = random.randint(900, 1200)
yesterday = 1000

st.metric("오늘 매출", today, today - yesterday)
