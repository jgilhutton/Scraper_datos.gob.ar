import requests
from re import search
from bs4 import BeautifulSoup as bs

START_PAGE = 2
DATA = []


def getTabla(soup):
    tabla = []
    table = soup.find('table', {'id': 'sismos'})
    rows = table.find_all('tr', {'class': 'Estilo68'})
    for row in rows:
        cols = row.find_all('td')
        cols = [x.text for x in cols]
        tabla.append(cols)
    return tabla


def getNexPage(pageNo, pags, total):
    cookies = {'PHPSESSID': PHPSESSID}
    pag = requests.get(
        'http://contenidos.inpres.gob.ar/sismos_consultados.php?pagina={}&totpag={}&ctd={}'.format(pageNo, pags, total),
        cookies=cookies)
    return pag.text


def startSearchAndSetCookie():
    postData = {'datepicker': '01/01/1940',
                'datepicker2': '07/11/2019',
                'tilde1': 'checkbox',
                'hora_inicial': 'hh',
                'min_inicial': 'mm',
                'seg_inicial': 'ss',
                'hora_final': 'hh',
                'min_final': 'mm',
                'seg_final': 'ss',
                'long_inf': '',
                'long_sup': '',
                'lat_inf': '',
                'lat_sup': '',
                'provincia': '',
                'mercalli': '+I+',
                'grad1': '',
                'grad2': '',
                'boton': 'buscar', }
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
               'Referer': 'http://contenidos.inpres.gob.ar/buscar_sismo'}
    primeraPag = requests.post('http://contenidos.inpres.gob.ar/sismos', data=postData, headers=headers)
    cantidadSismos = search('\d+(?=s&iacute;smos encontrados)', primeraPag.text)
    if cantidadSismos:
        cantidadSismos = int(cantidadSismos.group())
    return primeraPag.text, primeraPag.cookies['PHPSESSID'], cantidadSismos


def toCsv():
    with open('Base de datos sismológica.csv', 'w', encoding='latin1') as csv:
        while True:
            data = yield
            data = '\n'.join(('^'.join(linea) for linea in data)) + '\n'
            csv.write(data)


csvDumper = toCsv()
csvDumper.send(None)
primeraPag, PHPSESSID, cantidadSismos = startSearchAndSetCookie()
totalPags = cantidadSismos // 30
soup = bs(primeraPag, 'html.parser')
parcial = getTabla(soup)
csvDumper.send(parcial[1:])
for i in range(START_PAGE, totalPags):
    print(i, '/', totalPags)
    nextPage = getNexPage(i, totalPags, cantidadSismos)
    soup = bs(nextPage, 'html.parser')
    parcial = getTabla(soup)
    csvDumper.send(parcial[1:])
csvDumper.close()
