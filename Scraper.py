from bs4 import BeautifulSoup as bs
from re import compile, sub, search
from os.path import isfile, isdir
from os import mkdir
from ssl import SSLError, SSLCertVerificationError
import requests

SEARCH_TERM = 'SUBE'
MAX_FILE_SIZE = 1024  # MiB
OUTPUT_DIRECTORY = './datasets/' + sub('[^\w\d-]+','.',SEARCH_TERM) + '/'
GRUPOS = {
    'Agroganadreia, pesca y forestacion':   ('agri',False),
    'Asuntos internacionales':              (None,False),
    'Ciencia y tecnologia':                 ('tech',False),
    'Economia y finanzas':                  ('econ',False),
    'Educacion, cultura y deportes':        ('educ',False),
    'Energia':                              ('ener',False),
    'Gobierno y sector publico':            ('gove',False),
    'Justicia, seguridad y legales':        ('just',False),
    'Medio ambiente':                       ('envi',False),
    'Poblacion y sociedad':                 (None,False),
    'Regiones y ciudades':                  (None,False),
    'Salud':                                ('heal',False),
    'Transporte':                           ('tran',False),
}

datasetLandingPage = 'https://datos.gob.ar/'


def getPage(url):
    try:
        page = requests.get(url, allow_redirects=True)
    except (SSLCertVerificationError, requests.exceptions.SSLError):
        page = requests.get(url, allow_redirects=True, verify=False)
    return page.text


def salir(mensaje=''):
    print(mensaje)
    input('Enter para terminar...')
    exit()


def getSearchStr():
    if SEARCH_TERM:
        searchStr = 'q={}&sort=metadata_modified+desc'.format(SEARCH_TERM)
        return searchStr
    buscarEstosGrupos = []
    searchStr = ''
    for grupo in GRUPOS:
        if all(GRUPOS[grupo]):
            buscarEstosGrupos.append(GRUPOS[grupo][0])
    if not buscarEstosGrupos:
        return ''
    searchStr = 'groups='+'&groups='.join(buscarEstosGrupos)
    return searchStr

def getNumeroDePaginas(soup):
    linkToPaginas = soup.find_all(href=compile('(?<=/dataset\?page=)\d+'))
    paginas = [int(x.text) for x in linkToPaginas if x.text.isdigit()]
    if not paginas:
        return 1
    pags = max(paginas)
    return pags


def getLinksParaDatasets(soup):
    linkToDatasets = soup.find_all('a', href=compile('/dataset/.+'))
    for x in linkToDatasets:
        yield datasetLandingPage + x['href']


def getDataCsv(soup):
    divs = filter(lambda x: (x.has_attr('class') and x['class'] == ['pkg-container']), soup.find_all('div'))
    for div in divs:
        csvs = div.find_all(href=compile('.+\.(?:csv$|php)'))
        nombres = div.find_all('h3')
        if len(csvs) == 1:
            csv = [x['href'] for x in csvs][0]
            if not search('^https?://',csv):
                csv = 'https://' + csv
        else:
            yield None, None
            continue
        if len(nombres) == 1:
            nombre = [x.text for x in nombres][0]
            regex = '[^\w\d-]+'
            nombre = sub(regex, '_', nombre)
        else:
            yield None, None
        yield (nombre, csv)


def createCsv(fileName, data):
    with open(OUTPUT_DIRECTORY+fileName + '.csv', 'w') as csv:
        csv.write(data)


def checkFileSize(link):
    try:
        head = requests.head(link, allow_redirects=True)
    except SSLError:
        salir("""Existen problemas con la configuracion SSL de la maquina.
Editar el archivo /etc/ssl y bajarle el nivel de seguridad
    tal como se detalla en el siguiente link:
    https://stackoverflow.com/questions/55680224/how-to-fix-requests-exceptions-sslerror""")
    except (SSLCertVerificationError,requests.exceptions.SSLError):
        head = requests.head(link, allow_redirects=True, verify=False)
    try:
        size = head.headers['Content-Range'].split('/')[-1]
    except KeyError:
        if not link.endswith('csv') and 'php' in link:
            return -1, 'Desconocido', True
        else:
            return None,None,False
    if size.isnumeric():
        size = int(size)
    sizeInKiB = size / 1024
    sizeInMiB = sizeInKiB / 1024
    if sizeInMiB < 1:
        if sizeInKiB > MAX_FILE_SIZE * 1024:
            return sizeInKiB, 'KiB', False
        else:
            return sizeInKiB, 'KiB', True
    elif sizeInMiB > MAX_FILE_SIZE:
        return sizeInMiB, 'MiB', False
    else:
        return sizeInMiB, 'MiB', True


def createDirectory():
    if not isdir(OUTPUT_DIRECTORY):
        mkdir(OUTPUT_DIRECTORY)


def main():
    createDirectory()
    searchStr = getSearchStr()
    url = datasetLandingPage + 'dataset?' + searchStr
    if SEARCH_TERM:
        print('Buscando "{}"... '.format(SEARCH_TERM),end='')
    else:
        print('Buscando en los grupos... ',end='')
    landing = getPage(url)
    if '\nNo se encontraron resultados' in landing:
        salir('No se obtuvieron resultados para la busqueda:\n\t"{}"'.format(searchStr))
    else:
        print('OK')
    soup = bs(landing, 'html.parser')
    cantidadDePaginas = getNumeroDePaginas(soup)
    for pag in range(1, cantidadDePaginas + 1):
        print('Pagina:', pag)
        url = datasetLandingPage + 'dataset?' + searchStr + '&page=%d' % pag
        pagina = getPage(url)
        soup = bs(pagina, 'html.parser')
        for dataSetLink in getLinksParaDatasets(soup):
            datasetPage = getPage(dataSetLink)
            dsSoup = bs(datasetPage, 'html.parser')
            for fileName, csvLink in getDataCsv(dsSoup):
                if not fileName:
                    continue
                if isfile(OUTPUT_DIRECTORY + fileName + '.csv'):
                    print('Se saltea {}.'.format(fileName).ljust(100, '.'), 'Ya existe el archivo')
                    continue
                sizeCsv, unidad, aceptable = checkFileSize(csvLink)
                if not sizeCsv:
                    print('Se saltea {}.'.format(fileName).ljust(100, '.'), 'Problemas con headers')
                    continue
                if not aceptable:
                    print('Se saltea {}.'.format(fileName).ljust(100, '.'),
                          'Supera los {}{} ({})'.format(round(MAX_FILE_SIZE, 2), unidad,
                                                        round(sizeCsv, 2)))
                    continue
                print(fileName.ljust(100, '.'), round(sizeCsv, 2), unidad)
                try:
                    data = requests.get(csvLink, allow_redirects=True).text
                except (SSLCertVerificationError, requests.exceptions.SSLError):
                    data = requests.get(csvLink, allow_redirects=True, verify=False).text
                createCsv(fileName, data)


main()
