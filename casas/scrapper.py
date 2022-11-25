from bs4 import BeautifulSoup
import bs4
import pandas as pd
import requests
import re
import time


class Scraping:
    """Um scraper para pegar informações de casas a venda do tipo terrea
    no municipio de campo grande mato grosso do sul. as informações são
    pegas no site do infoimoveis
    """

    def __init__(self):
        self.url = 'https://www.infoimoveis.com.br/busca/venda/casa-terrea/ms/campo-grande'
        self.lista_casas = []

    def obter_pagina(self, url, pagina=None):
        headers = {'user-agent': 'Mozilla/5.0'}
        if pagina is None:
            r = requests.get(url, headers=headers)
        else:
            r = requests.get(url, headers=headers, params={'pagina': pagina})
        r.raise_for_status()
        return BeautifulSoup(r.text, 'html.parser')

    def listagem(self, bs):
        listagem = bs.find('div', {'id': 'listagemV2'}).ul

        links_casas = []

        for item in listagem.find_all('li', {'class': 'li-item'}):
            if item.find('a', {'href': re.compile('^https://www.infoimoveis.*')}) is not None:
                a = item.find('a', {'href': re.compile('^(https://www.infoimoveis*)')})
                links_casas.append(a['href'])
        return links_casas

    def dados_casa(self, bs, dict_casa):
        dados_imovel = bs.find('div', {'class': 'dados-imovel'}).table
        dados_imovel = [item for item in dados_imovel.children if isinstance(item, bs4.element.Tag)]
        for item in dados_imovel:
            dict_casa[item.td.get_text().lower().replace(' ', '_')] = item.td.next_sibling.get_text()
        return dict_casa

    def valor_casa(self, bs, dict_casa):
        try:
            valor = (
                bs.find('div', {'class': 'valor-imovel'})
                .find('div', {'class': 'wrap-valor'})
                .find('span', {'class': 'valor'})
                .get_text()
            ).replace('\xa0', '')
        except AttributeError:
            dict_casa['valor'] = None
        else:
            dict_casa['valor'] = valor
        return dict_casa

    def descricao_casa(self, bs, dict_casa):
        try:
            descricao = []

            for item in bs.find('div', {'class': 'descricao'}).ul:
                if isinstance(item, bs4.element.Tag):
                    descricao.append(item.get_text().strip(chr(8226)).strip())
        except (AttributeError, TypeError):
            dict_casa['descricao'] = None
        else:
            dict_casa['descricao'] = ','.join(descricao)
        return dict_casa

    def scraping(self, pagina):
        bs = self.obter_pagina(self.url, pagina)
        links_casas = self.listagem(bs)

        for link in links_casas:
            print(f'Buscando {link}')
            dict_casa = {}
            bs_casa = self.obter_pagina(link)
            dict_casa = self.dados_casa(bs_casa, dict_casa)
            dict_casa = self.valor_casa(bs_casa, dict_casa)
            dict_casa = self.descricao_casa(bs_casa, dict_casa)
            self.lista_casas.append(dict_casa)
            time.sleep(2)

    def iniciar(self, inicio, fim):
        """recebe o número da pagina de inicio e da pagina final"""
        for i in range(inicio, fim):
            print(f'Pagina{i}')
            self.scraping(i)
            time.sleep(1)


scraping = Scraping()
scraping.iniciar(1, 446)
