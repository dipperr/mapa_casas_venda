from collections import Counter
import numpy as np
import pandas as pd
import re
import requests
import warnings

warnings.filterwarnings('ignore')


def format_area(col):
    df[col] = df[col].apply(
        lambda x: x.rstrip('m² ') if x is not None else x
    )
    df[col] = df[col].apply(
        lambda x: x.replace('.', '').replace(',', '.') if x is not None else x
    )


df1 = pd.read_csv('dados/casas.csv')
df2 = pd.read_csv('dados/casas2.csv')

if not df1.columns.difference(df2.columns).empty:
    raise Exception('Datasests com colunas diferentes!!!')

df = pd.concat([df1, df2])
df.reset_index(drop=True, inplace=True)

del df1
del df2

print(df.info())

df.drop(labels=['condomínio', 'iptu', 'cidade/uf'], axis=1, inplace=True)
df.iloc[:, 0:7] = df.iloc[:, 0:7].replace(np.nan, None)

print(df.head())

lista_descri = []
for i in range(df.shape[0]):
    if df.loc[i, 'descricao'] is not None:
        for item in df.loc[i, 'descricao'].split(','):
            lista_descri.append(item.lstrip('1234567890 ').lower())

print(Counter(lista_descri).most_common()[:15])

descricao = []
indices = set()
for indice in range(df.shape[0]):
    if df.loc[indice, 'descricao'] is not None:
        a = {}
        for item in df.loc[indice, 'descricao'].split(','):
            if item[0].isnumeric():
                if 'vaga' in item.lower():
                    a['vaga'] = re.search(r'(\d+)', item).group()
                elif 'quarto' in item.lower():
                    a['quarto'] = re.search(r'(\d+)', item).group()
                elif 'suíte' in item.lower():
                    a['suite'] = re.search(r'(\d+)', item).group()
                elif 'wc social' in item.lower():
                    a['wc_social'] = re.search(r'(\d+)', item).group()

        if a:
            descricao.append(a)
            indices.add(indice)
df = df.merge(
    pd.DataFrame(descricao, index=indices),
    how='left', left_index=True, right_index=True
)

descricao = []
indices = set()
for indice in range(df.shape[0]):
    if df.loc[indice, 'descricao'] is not np.nan:
        a = {}
        try:
            for item in df.loc[indice, 'descricao'].split(','):
                if item.strip().lower() == 'piscina':
                    a['piscina'] = True
                elif item.strip().lower() == 'asfalto':
                    a['asfalto'] = True
        except AttributeError:
            print(indice)
            break
        if a:
            descricao.append(a)
            indices.add(indice)

df = df.merge(
    pd.DataFrame(descricao, index=indices),
    how='left', left_index=True, right_index=True
)

df.iloc[:, 7:11] = df.iloc[:, 7:11].replace(np.nan, 0)
df.iloc[:, 11:] = df.iloc[:, 11:].replace(np.nan, False)
df.iloc[:, 11:] = df.iloc[:, 11:].applymap(lambda x: int(x))

format_area('área_total')
format_area('área_construída')

df.valor = df.valor.str.lstrip('R$')
df.valor = df.valor.str.replace('.', '').str.replace(',', '.')

df.drop(labels='descricao', axis=1, inplace=True)

df.iloc[:, 3:6] = df.iloc[:, 3:6].astype(float)
df.iloc[:, 6:] = df.iloc[:, 6:].astype(int)

df.to_csv('casas_formatado.csv', index=False)
