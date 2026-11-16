Campus Navigation Assistant - GPS edition (Python, Streamlit, Aurora theme)

RUN
  pip install -r requirements.txt
  streamlit run app.py
Terminal route finder:  python navigator.py
Terminal GPS test:      python gps.py 12.2400 79.6500 "AI & DS Department Lab"

GPS FEATURES
  - Live location: the location button in the app reads the browser/phone GPS.
  - Nearest building: matches your GPS fix to the closest campus building.
  - Start from here: one tap sets your starting point to where you really are.
  - "You" dot on the campus layout map.
  - Distance + compass direction to the destination, and a Google Maps walking link.
  - Off-campus detection (more than 250 m from every building).
  - Demo mode: "Simulate a location" or paste coordinates, for indoor/offline demos.

IMPORTANT NOTES
  - Browsers only share GPS on HTTPS or localhost. On a phone, open the app through
    Streamlit Community Cloud or an https tunnel (for example ngrok). A plain
    http://192.168.x.x link will not give GPS.
  - Replace the SAMPLE coordinates: set GPS_ORIGIN (Main Gate) in navigator.py, and for
    best accuracy add "lat" and "lon" to each building in NODES (Google Maps: right-click
    the building, copy the two numbers).

FILES
  app.py        web interface   |  navigator.py  campus data, routes, map
  gps.py        GPS helpers     |  .streamlit/config.toml  theme
