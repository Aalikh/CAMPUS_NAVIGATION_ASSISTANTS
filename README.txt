Campus Navigation Assistant - CODE STORM 2026 (Problem 1.3), Python version

WEB APP (Streamlit)
  pip install -r requirements.txt
  streamlit run app.py

TERMINAL VERSION (no installation needed)
  python navigator.py

FILES
  navigator.py  campus data + route-finding logic + SVG map + terminal mode
  app.py        Streamlit web interface (Aurora dark theme)
  .streamlit/config.toml  theme colours

ADD YOUR REAL CAMPUS: edit NODES (buildings), EDGES (walkways + distance)
and PLACES (rooms, floors, cues) at the top of navigator.py.
