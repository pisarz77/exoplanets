import pyvo
import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Połączenie z TAP NASA Exoplanet Archive i pobranie danych z tabeli PSCompPars
service = pyvo.dal.TAPService("https://exoplanetarchive.ipac.caltech.edu/TAP/sync")
query = "SELECT TOP 1000 * FROM PSCompPars"  # pobieramy 1000 rekordów
job = service.search(query)
df = job.to_table().to_pandas()

# Wyświetlamy listę kolumn (dla diagnostyki)
print("Dostępne kolumny:", df.columns.tolist())

# Wstępna obróbka – usuwamy wiersze, w których brakuje kluczowych danych
# Używamy nazw kolumn zgodnych z PSCompPars: "ra", "dec", "discoverymethod", "pl_rade", "pl_orbper", "disc_year"
df = df.dropna(subset=["ra", "dec", "discoverymethod", "pl_rade", "pl_orbper", "disc_year"])

# Konwersja kolumn na wartości numeryczne
df["pl_rade"] = pd.to_numeric(df["pl_rade"], errors='coerce')
df["pl_orbper"] = pd.to_numeric(df["pl_orbper"], errors='coerce')
df["disc_year"] = pd.to_numeric(df["disc_year"], errors='coerce')

# Pobieramy unikalne metody odkrycia
discovery_methods = np.sort(df["discoverymethod"].dropna().unique())

# Ustalamy zakresy do filtrów
rade_min, rade_max = df["pl_rade"].min(), df["pl_rade"].max()
orbper_min, orbper_max = df["pl_orbper"].min(), df["pl_orbper"].max()
disc_year_min, disc_year_max = int(df["disc_year"].min()), int(df["disc_year"].max())

# Inicjalizacja aplikacji Dash
app = dash.Dash(__name__)
app.title = "Mapa egzoplanet"

app.layout = html.Div([
    html.H1("Interaktywna mapa egzoplanet"),
    html.P("Filtruj dane wg: metody odkrycia, promienia planety [R⊕], okresu orbitalnego [dni] oraz roku odkrycia."),
    
    html.Div([
        html.Label("Metoda odkrycia:"),
        dcc.Dropdown(
            id="method-dropdown",
            options=[{"label": m, "value": m} for m in discovery_methods],
            value=discovery_methods.tolist(),  # domyślnie wszystkie
            multi=True
        )
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Promień planety [R⊕]:"),
        dcc.RangeSlider(
            id="rade-slider",
            min=rade_min, max=rade_max, step=0.1,
            value=[rade_min, rade_max],
            marks={round(x,1): str(round(x,1)) for x in np.linspace(rade_min, rade_max, num=5)}
        )
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 20px'}),
    
    html.Div([
        html.Label("Okres orbitalny [dni]:"),
        dcc.RangeSlider(
            id="orbper-slider",
            min=orbper_min, max=orbper_max, step=1,
            value=[orbper_min, orbper_max],
            marks={int(x): str(int(x)) for x in np.linspace(orbper_min, orbper_max, num=5)}
        )
    ], style={'width': '48%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Rok odkrycia:"),
        dcc.RangeSlider(
            id="disc-year-slider",
            min=disc_year_min, max=disc_year_max, step=1,
            value=[disc_year_min, disc_year_max],
            marks={year: str(year) for year in range(disc_year_min, disc_year_max+1, max(1, (disc_year_max-disc_year_min)//5))}
        )
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '20px 20px'}),
    
    dcc.Graph(id="sky-map"),
    
    html.P("Oś X: RA [°] | Oś Y: Dec [°]", style={'textAlign': 'center'})
])

# Callback – aktualizacja wykresu w zależności od wybranych filtrów
@app.callback(
    Output("sky-map", "figure"),
    [Input("method-dropdown", "value"),
     Input("rade-slider", "value"),
     Input("orbper-slider", "value"),
     Input("disc-year-slider", "value")]
)
def update_map(selected_methods, rade_range, orbper_range, disc_year_range):
    filtered_df = df[
        (df["discoverymethod"].isin(selected_methods)) &
        (df["pl_rade"] >= rade_range[0]) & (df["pl_rade"] <= rade_range[1]) &
        (df["pl_orbper"] >= orbper_range[0]) & (df["pl_orbper"] <= orbper_range[1]) &
        (df["disc_year"] >= disc_year_range[0]) & (df["disc_year"] <= disc_year_range[1])
    ]
    
    # Tworzymy wykres scatter: RA vs Dec, z informacjami na hover
    fig = px.scatter(
        filtered_df,
        x="ra",
        y="dec",
        hover_data=["pl_name", "discoverymethod", "pl_rade", "pl_orbper", "disc_year"],
        labels={
            "ra": "Right Ascension [°]",
            "dec": "Declination [°]",
            "pl_name": "Nazwa planety",
            "discoverymethod": "Metoda odkrycia",
            "pl_rade": "Promień [R⊕]",
            "pl_orbper": "Okres [dni]",
            "disc_year": "Rok odkrycia"
        },
        title=f"Egzoplanety: {len(filtered_df)} wyników"
    )
    fig.update_layout(transition_duration=500)
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)