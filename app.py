"""Campus Navigation Assistant - Streamlit web app.   Run:  streamlit run app.py"""
import streamlit as st
import streamlit.components.v1 as components
from html import escape
from navigator import (PLACES, NODES, CATEGORIES, COLORS, places_in,
                       get_directions, map_svg)

st.set_page_config(page_title="Campus Navigation Assistant", page_icon="🧭", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700&family=Sora:wght@500;600;700&display=swap');
html, body, [class*="css"], .stApp {font-family:'Nunito Sans',system-ui,sans-serif;}
.stApp {background:#eef3f9;}
.block-container {padding-top:1.2rem; max-width:1100px;}
#MainMenu, footer, header {visibility:hidden;}
.hero {background:radial-gradient(900px 300px at 85% -20%,rgba(18,179,214,.35),transparent 60%),#0b1f3a;
       color:#fff;border-radius:20px;padding:30px 30px 40px;margin-bottom:-6px;}
.hero small {color:#9fd8e8;font-size:.85rem;}
.hero h1 {font-family:Sora,sans-serif;font-size:2.4rem;line-height:1.15;margin:10px 0 8px;color:#fff;padding:0;}
.hero p {color:#c8d6ea;max-width:56ch;margin:0;font-size:1.05rem;}
.panel {background:#fff;border-radius:20px;box-shadow:0 12px 32px -14px rgba(11,31,58,.35);padding:22px;color:#17294a;}
.panel h3 {font-family:Sora,sans-serif;font-size:1.15rem;margin:0 0 12px;color:#17294a;}
.fact {display:inline-block;background:#e5f6fb;color:#0a6f88;font-weight:700;font-size:.82rem;padding:5px 12px;border-radius:999px;margin:0 8px 8px 0;}
.step {position:relative;padding:0 0 18px 48px;color:#17294a;}
.step .n {position:absolute;left:0;top:0;width:32px;height:32px;border-radius:50%;background:#0b1f3a;color:#fff;
          display:grid;place-items:center;font:700 .9rem Sora,sans-serif;}
.step.end .n {background:#12a46e;}
.step:not(.last):after {content:"";position:absolute;left:15px;top:36px;bottom:4px;width:2px;background:#dbe4f0;}
.note {display:block;font-size:.84rem;color:#5a6a85;margin-top:2px;}
.arrive {background:#e9f8f1;border-radius:12px;padding:10px 12px;}
.legend span {display:inline-block;margin-right:14px;font-size:.82rem;color:#5a6a85;}
.legend i {display:inline-block;width:12px;height:12px;border-radius:4px;margin-right:6px;vertical-align:-1px;}
div[data-baseweb="select"] > div {border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><small>CODE STORM 2026 &nbsp;|&nbsp; Dept. of AI &amp; Data Science, Takshashila University</small>
<h1>Find your way around campus.</h1>
<p>Choose where you are and where you need to be. You get simple walking steps, the floor and room, and landmarks to look for.</p></div>""",
            unsafe_allow_html=True)

names = list(PLACES)
st.session_state.setdefault("frm", "Main Gate")
st.session_state.setdefault("to", "AI & DS Department Lab")


def swap():
    st.session_state.frm, st.session_state.to = st.session_state.to, st.session_state.frm


st.write("")
cat = st.radio("Quick access", CATEGORIES, horizontal=True)
options = places_in(cat)
if st.session_state.to not in options:          # keep current choice selectable
    options = [st.session_state.to] + options

c1, c2, c3 = st.columns([5, 1, 5], vertical_alignment="bottom")
c1.selectbox("I am at (type to search)", names, key="frm")
c2.button("⇄", on_click=swap, help="Swap start and destination", use_container_width=True)
c3.selectbox("I want to go to (type to search)", options, key="to")

frm, to = st.session_state.frm, st.session_state.to
d = get_directions(frm, to)

left, right = st.columns([1, 1.1], gap="large")
with left:
    h = f'<div class="panel"><h3>{escape(frm)} to {escape(to)}</h3>'
    h += f'<span class="fact">{"About %d min walk" % d["minutes"] if d["metres"] else "Same building"}</span>'
    if d["metres"]:
        h += f'<span class="fact">{d["metres"]} m</span>'
    h += f'<span class="fact">{escape(d["building"])}</span><span class="fact">{d["floor"]}</span><div style="height:8px"></div>'
    for i, s in enumerate(d["steps"], 1):
        note = f'<span class="note">{escape(s["note"])}</span>' if s["note"] else ""
        h += f'<div class="step"><div class="n">{i}</div>{escape(s["text"])}{note}</div>'
    if frm != to:
        h += (f'<div class="step end last"><div class="n">&#10003;</div><div class="arrive"><b>You have arrived: {escape(to)}</b>'
              f'<span class="note">{escape(d["building"])}, {d["floor"]}, {escape(d["room"])}<br>Look for: {escape(d["cue"])}</span></div></div>')
    st.markdown(h + "</div>", unsafe_allow_html=True)

with right:
    legend = "".join(f'<span><i style="background:{COLORS[k]}"></i>{n}</span>'
                     for k, n in (("academic", "Academic"), ("labs", "Labs"), ("student", "Student facilities"), ("admin", "Admin")))
    legend += '<span><i style="background:#f5a524"></i>Your route</span>'
    st.markdown('<div class="panel"><h3>Campus layout</h3></div>', unsafe_allow_html=True)
    components.html(f'<div style="padding:4px">{map_svg(d["nodes"])}</div>'
                    f'<div style="font:13px Nunito Sans,sans-serif;color:#5a6a85;padding:6px 4px">{legend}</div>', height=420)

st.caption("Sample data for the prototype. Edit NODES, EDGES and PLACES in navigator.py to use your real campus.")
