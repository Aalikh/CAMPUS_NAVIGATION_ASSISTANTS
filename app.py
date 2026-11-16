"""Campus Navigation Assistant - Streamlit web app (Aurora theme).   Run:  streamlit run app.py"""
import streamlit as st
import streamlit.components.v1 as components
from html import escape
from navigator import (PLACES, NODES, CATEGORIES, COLORS, ROUTE_COLOR, places_in,
                       get_directions, map_svg)
import gps

try:                                   # real browser GPS (pip install streamlit-geolocation)
    from streamlit_geolocation import streamlit_geolocation
except ImportError:
    streamlit_geolocation = None

st.set_page_config(page_title="Campus Navigation Assistant", page_icon="🧭", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&family=Outfit:wght@300;400;500;600&display=swap');
html, body, [class*="css"], .stApp, .stApp p, .stApp label {font-family:'Outfit',system-ui,sans-serif;}
.stApp {background:
  radial-gradient(700px 480px at 12% -5%, rgba(182,156,255,.38), transparent 60%),
  radial-gradient(650px 460px at 92% 8%, rgba(255,143,184,.26), transparent 60%),
  radial-gradient(700px 520px at 60% 105%, rgba(126,240,208,.20), transparent 60%),
  #0e0b1f;
  background-attachment:fixed; color:#f1ecff;}
.block-container {padding-top:1.6rem; max-width:1100px;}
#MainMenu, footer, header {visibility:hidden;}
.hero {padding:26px 4px 10px;}
.hero small {color:#bfb3f2;font-size:.9rem;letter-spacing:.02em;font-weight:300;}
.hero h1 {font-family:Fraunces,Georgia,serif;font-weight:500;font-size:3.1rem;line-height:1.08;margin:12px 0 10px;color:#fbf8ff;padding:0;max-width:15ch;}
.hero p {color:#cfc6f5;max-width:54ch;margin:0;font-size:1.08rem;font-weight:300;}
.glass {background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);border-radius:24px;padding:24px;
        backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);box-shadow:0 20px 50px -24px rgba(0,0,0,.6);color:#f1ecff;}
.glass h3 {font-family:Fraunces,Georgia,serif;font-weight:500;font-size:1.3rem;margin:0 0 14px;color:#fbf8ff;padding:0;line-height:1.3;}
.fact {display:inline-block;background:rgba(182,156,255,.16);border:1px solid rgba(182,156,255,.32);color:#e3d9ff;font-size:.82rem;padding:4px 13px;border-radius:999px;margin:0 8px 8px 0;}
.step {position:relative;padding:0 0 20px 50px;color:#f1ecff;font-weight:300;line-height:1.55;}
.step .n {position:absolute;left:0;top:0;width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#b69cff,#ff8fb8);
          color:#1a1033;display:grid;place-items:center;font:600 .9rem Outfit,sans-serif;}
.step.end .n {background:linear-gradient(135deg,#7ef0d0,#b7ffe9);}
.step:not(.last):after {content:"";position:absolute;left:16px;top:40px;bottom:4px;width:1px;background:linear-gradient(#b69cff66,transparent);}
.note {display:block;font-size:.84rem;color:#a99fd6;margin-top:3px;}
.arrive {background:rgba(126,240,208,.10);border:1px solid rgba(126,240,208,.30);border-radius:16px;padding:12px 14px;}
.arrive b {font-family:Fraunces,Georgia,serif;font-weight:500;font-size:1.05rem;}
.gps-h {font-family:Fraunces,Georgia,serif;font-weight:500;font-size:1.3rem;color:#fbf8ff;margin:26px 0 6px;padding:0;}
.legend span {display:inline-block;margin-right:16px;font-size:.82rem;color:#bfb3f2;}
.legend i {display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px;vertical-align:0;}
/* widgets */
.stApp label p, .stApp [data-testid="stWidgetLabel"] p {color:#cfc6f5 !important;font-weight:400;font-size:.9rem;}
div[data-baseweb="select"] > div {background:rgba(255,255,255,.08) !important;border:1px solid rgba(255,255,255,.16) !important;border-radius:16px !important;color:#f1ecff !important;min-height:48px;}
div[data-baseweb="select"] svg {fill:#cfc6f5;}
.stButton > button {background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);color:#f1ecff;border-radius:999px;height:48px;font-size:1.2rem;transition:all .2s;}
.stButton > button:hover {border-color:#b69cff;color:#fff;background:rgba(182,156,255,.2);}
button[kind="pills"], button[kind="pillsActive"], [data-testid="stPills"] button {border-radius:999px !important;font-family:Outfit,sans-serif;}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><small>CODE STORM 2026 &nbsp;/&nbsp; Dept. of AI &amp; Data Science, Takshashila University</small>
<h1>Find your way around campus.</h1>
<p>Choose where you are and where you need to be. You get simple walking steps, the floor and room, and landmarks to look for.</p></div>""",
            unsafe_allow_html=True)

names = list(PLACES)
st.session_state.setdefault("frm", "Main Gate")
st.session_state.setdefault("to", "AI & DS Department Lab")


def swap():
    st.session_state.frm, st.session_state.to = st.session_state.to, st.session_state.frm


def set_start(place):
    st.session_state.frm = place


st.write("")
if hasattr(st, "pills"):
    cat = st.pills("Quick access", CATEGORIES, default="All", selection_mode="single") or "All"
else:
    cat = st.radio("Quick access", CATEGORIES, horizontal=True)
options = places_in(cat)
if st.session_state.to not in options:          # keep the current choice selectable
    options = [st.session_state.to] + options

c1, c2, c3 = st.columns([5, 1, 5], vertical_alignment="bottom")
c1.selectbox("I am at (type to search)", names, key="frm")
c2.button("⇄", on_click=swap, help="Swap start and destination", use_container_width=True)
c3.selectbox("I want to go to (type to search)", options, key="to")

frm, to = st.session_state.frm, st.session_state.to
d = get_directions(frm, to)

# ------------------------------------------------------------------ GPS
st.markdown('<h3 class="gps-h">Live GPS</h3>', unsafe_allow_html=True)
fix = None                                                    # (lat, lon, accuracy)
g1, g2 = st.columns([1, 2.2], gap="large", vertical_alignment="center")
with g1:
    st.markdown('<span class="note">Tap the button and allow location access.</span>', unsafe_allow_html=True)
    if streamlit_geolocation:
        raw = streamlit_geolocation()
        if raw and raw.get("latitude") is not None:
            fix = (raw["latitude"], raw["longitude"], raw.get("accuracy"))
    else:
        st.info("Install the GPS add-on: pip install streamlit-geolocation")
    with st.expander("No GPS signal? Simulate a location"):
        demo = st.selectbox("Pretend I am standing near", ["(off)"] + [n["n"] for n in NODES.values()], key="demo")
        pasted = st.text_input("Or paste coordinates (lat, lon)", placeholder="12.2402, 79.6503")
        if pasted and gps.parse_coordinates(pasted):
            fix = (*gps.parse_coordinates(pasted), 10)
        elif demo != "(off)":
            node = next(n for n in NODES.values() if n["n"] == demo)
            fix = (node["lat"] + 0.00004, node["lon"] + 0.00003, 10)   # a few metres from the building
with g2:
    if fix:
        lat, lon, acc = fix
        here = gps.locate(lat, lon, acc)
        guide = gps.guidance(lat, lon, to)
        h = '<div class="glass"><h3>Your position</h3>'
        if here["on_campus"]:
            h += f'<span class="fact">Near {escape(here["name"])}</span><span class="fact">{here["distance"]} m away</span>'
        else:
            h += f'<span class="fact">Off campus ({here["distance"]} m from the nearest building)</span>'
        if acc is not None:
            h += f'<span class="fact">GPS accuracy about {round(acc)} m</span>'
        h += '<div style="height:6px"></div>'
        if here["weak"]:
            h += '<span class="note">Weak signal. Move outdoors for a better fix.</span>'
        if guide["arrived"]:
            h += f'<div class="arrive"><b>You have reached {escape(to)}.</b></div>'
        else:
            h += f'<div>{escape(to)} is about <b>{guide["metres"]} m</b> to the <b>{guide["direction"]}</b> of you.</div>'
        st.markdown(h + "</div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        label = f"Start from {here['place']}" if here["on_campus"] else "Start from Main Gate"
        b1.button(label, on_click=set_start, args=(here["place"],), use_container_width=True)
        b2.link_button("Open in Google Maps", guide["maps_url"], use_container_width=True)
    else:
        st.markdown('<div class="glass"><h3>Where am I?</h3>Allow location access, or simulate a location, and the app finds the nearest building, '
                    'shows a "You" dot on the map and starts your route from there. Browsers only share GPS on HTTPS or localhost.</div>',
                    unsafe_allow_html=True)
you = gps.to_map_xy(fix[0], fix[1]) if fix else None
st.write("")

left, right = st.columns([1, 1.1], gap="large")
with left:
    h = f'<div class="glass"><h3>{escape(frm)} to {escape(to)}</h3>'
    h += f'<span class="fact">{"About %d min walk" % d["minutes"] if d["metres"] else "Same building"}</span>'
    if d["metres"]:
        h += f'<span class="fact">{d["metres"]} m</span>'
    h += f'<span class="fact">{escape(d["building"])}</span><span class="fact">{d["floor"]}</span><div style="height:10px"></div>'
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
    legend += f'<span><i style="background:{ROUTE_COLOR}"></i>Your route</span>'
    components.html(
        "<style>@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500&family=Outfit:wght@300;400&display=swap');"
        "body{margin:0;font-family:Outfit,sans-serif;color:#f1ecff}"
        "h3{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:1.3rem;margin:4px 4px 12px}"
        ".legend span{display:inline-block;margin-right:16px;font-size:13px;color:#bfb3f2}"
        ".legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px}</style>"
        f'<h3>Campus layout</h3>{map_svg(d["nodes"], you=you)}<div class="legend" style="padding:12px 4px">{legend}</div>',
        height=470)

st.caption("Sample data for the prototype. Edit NODES, EDGES and PLACES in navigator.py to use your real campus.")
