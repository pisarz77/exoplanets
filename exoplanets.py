import pandas as pd
import plotly.express as px

# Wczytanie danych z pliku CSV
df = pd.read_csv("exoplanets.csv", comment='#', low_memory=False)

# Przygotowanie danych
df = df.dropna(subset=['pl_orbincl', 'pl_orbsmax'])  # Usuwanie wierszy z brakującymi danymi
df = df[df['pl_orbsmax'] < 10]  # Ograniczenie do egzoplanet z mniejszymi orbitami dla lepszej wizualizacji

# Tworzenie interaktywnej mapy
fig = px.scatter(
    df,
    x='pl_orbsmax',
    y='pl_orbincl',
    color='discoverymethod',
    hover_name='pl_name',
    title='Interaktywna mapa egzoplanet',
    labels={
        'pl_orbsmax': 'Półoś wielka orbity (AU)',
        'pl_orbincl': 'Nachylenie orbity (stopnie)',
        'discoverymethod': 'Metoda odkrycia'
    },
    width=1000,
    height=800
)

# Dodanie filtrów
fig.update_layout(
    updatemenus=[
        dict(
            buttons=list([
                dict(label="Wszystkie metody odkrycia", method="update", args=[{"visible": [True] * len(df['discoverymethod'].unique())}]),
                dict(label="Tranzyt", method="update", args=[{"visible": [True if method == 'Transit' else False for method in df['discoverymethod'].unique()]}]),
                dict(label="Prędkość radialna", method="update", args=[{"visible": [True if method == 'Radial Velocity' else False for method in df['discoverymethod'].unique()]}]),
            ]),
            direction="down",
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.1,
            yanchor="top"
        ),
    ],
    annotations=[
        dict(
            text="Instrukcja: Wybierz metodę odkrycia z menu, aby filtrować egzoplanety.",
            align='left',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=0.05,
            y=1.15,
            bordercolor='black',
            borderwidth=1
        )
    ]
)

# Dodanie opisu osi i legendy
fig.update_xaxes(title_text='Półoś wielka orbity (AU) - odległość egzoplanety od gwiazdy')
fig.update_yaxes(title_text='Nachylenie orbity (stopnie) - kąt nachylenia orbity do linii widzenia')
fig.update_layout(legend_title_text='Metoda odkrycia')

# Wyświetlenie mapy
fig.show()
