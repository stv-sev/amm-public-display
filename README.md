# AMM Public Display – Live Rangliste

Öffentliche Live-Rangliste für Publikum. Liest ausschliesslich von Supabase.

## Deployment auf Streamlit Cloud

1. Diesen Ordner als eigenes GitHub-Repository pushen
2. app.streamlit.io → New app → Repo auswählen
3. Secrets konfigurieren:

```toml
SUPABASE_URL = "https://DEIN-PROJEKT-ID.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Ablauf am Wettkampf

```
Kampfrichter → Haupt-Tool (lokal, SQLite)
                    │
                    ├── Auto-Push nach jeder Note (Hintergrund)
                    └── 📡 "Rotation publizieren" Button
                              │
                         Supabase/PostgreSQL
                              │
                    Public Display (Streamlit Cloud)
                         Publikum weltweit
```

## Features

- 🤸 Gesamtrangliste (alle Turner nach Total)
- 🔩 Gerät-Rangliste (pro Gerät, Tab-Ansicht)
- 🏅 Team-Rangliste (nur bei Team-Wettkampf)
- 🔄 Auto-Refresh alle 10 Sekunden
- 📱 Responsive (Mobile-freundlich)
