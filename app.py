"""Meridian portfolio committee workbench. Start with: streamlit run app.py"""

import streamlit as st

from lab13_mandate import render


st.set_page_config(page_title="Meridian Portfolio Committee", page_icon="◈", layout="wide")
st.markdown("""<style>
  .block-container{max-width:1180px;padding-top:2rem}
  h1,h2,h3{color:#19324a}
  [data-testid="stMetricValue"]{color:#19324a}
  .callout{padding:1rem 1.2rem;background:#eaf2ef;border-left:4px solid #568d78;margin:.8rem 0 1.5rem}
  .warningbox{padding:1rem 1.2rem;background:#f8f0e2;border-left:4px solid #c7a35f;margin:.8rem 0 1.5rem}
  .small{font-size:.85rem;color:#64748b}
</style>""", unsafe_allow_html=True)

render()
