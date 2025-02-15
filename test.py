import pandas as pd
import requests

# Pobranie danych z NASA Exoplanet Archive
url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+ps&format=csv"
response = requests.get(url)
data = response.content.decode('utf-8')

# Zapisanie danych do pliku CSV
with open("exoplanets.csv", "w") as file:
    file.write(data)

# Wczytanie danych do DataFrame
df = pd.read_csv("exoplanets.csv", comment='#')

# Wyświetlenie pierwszych kilku wierszy i nazw kolumn
print(df.head())
print(df.columns)
