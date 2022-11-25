from collections import namedtuple
import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
import shelve


def get_coords(b):
    params = {
        'q': f"{b.replace(' ', '+').lower()}+campo+grande+mato+grosso+do+sul+brasil",
        'format': 'jsonv2'
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


def format_num(num):
    i, f = str(num).split('.')
    i = format(int(i), ',d').replace(',', '.')
    return ','.join([i, f])


df = pd.read_csv('casas_formatado.csv')

url = 'https://nominatim.openstreetmap.org/search.php'

bairros = df.bairro.unique()

bairros_cords = {}
coords = namedtuple('Coordenadas', 'lat long')
not_found = []

for bairro in bairros:
    print(f'Obtendo dados do bairro: {bairro}')
    r_json = get_coords(bairro)
    if r_json:
        r_json = r_json[0]
        bairros_cords[bairro] = coords(lat=r_json['lat'], long=r_json['lon'])

for bairro in np.setdiff1d(df.bairro.values, np.array([key for key in bairros_cords.keys()])):
    print(f'Buscando coordenadas do bairro: {bairro}')
    name = bairro
    if bairro.startswith('Jardim'):
        bairro = bairro.lstrip('Jardim ')
    elif bairro.startswith('Conjunto Hab.'):
        bairro = bairro.lstrip('Conjunto Hab. ')
    elif bairro.startswith('Conjunto Res.'):
        bairro = bairro.lstrip('Conjunto Res. ')
    r_json = get_coords(bairro)
    if r_json:
        r_json = r_json[0]
        bairros_cords[name] = coords(lat=r_json['lat'], long=r_json['lon'])

df2 = df[df.bairro.isin(
    np.intersect1d(df.bairro.values, np.array([key for key in bairros_cords.keys()]))
)].copy()

contagem = df2.value_counts(subset='bairro').reset_index().rename(mapper={0: 'total'}, axis=1)

valor_medio = df2.iloc[:, [2, 6]].groupby(by='bairro')['valor'].mean().reset_index()

m = folium.Map(location=[-20.4640173, -54.6162947], zoom_start=12)

marker_cluster = MarkerCluster().add_to(m)

html = """
<h2>{}</h2>
<p>Preço médio das casas:</p>
<h3>{}</h3>
""".format

for row in valor_medio.itertuples(index=False):
    folium.Marker(
        location=[bairros_cords[row.bairro].lat, bairros_cords[row.bairro].long],
        popup=html(row.bairro, format_num(round(row.valor, 2))),
        icon=folium.Icon(color="blue", prefix='fa', icon="fa-home")
    ).add_to(marker_cluster)

m.save('distribuicao_casas.html')

data = []
for row in valor_medio.itertuples(index=False):
    data.append(
        [bairros_cords[row.bairro].lat, bairros_cords[row.bairro].long, round(row.valor, 2)]
    )
m = folium.Map(location=[-20.4640173, -54.6162947], zoom_start=12)

HeatMap(data).add_to(m)
m.save('heatmap_preco.html')

data = []
for row in contagem.itertuples(index=False):
    data.append(
        [bairros_cords[row.bairro].lat, bairros_cords[row.bairro].long, row.total]
    )
m = folium.Map(location=[-20.4640173, -54.6162947], zoom_start=12)

HeatMap(data).add_to(m)
m.save('heatmap_tota_casa_bairro.html')

shelfFile = shelve.open('coordenadas_bairro')
shelfFile['coordenadas'] = {k: list(v) for k, v in bairros_cords.items()}
shelfFile.close()
