from bs4 import BeautifulSoup as bs
from re import compile, sub, search
from os.path import isfile, isdir
from os import mkdir
from ssl import SSLError, SSLCertVerificationError
from sys import argv
import requests

if '-s' in argv:
    try:
        SEARCH_TERM = argv[argv.index('-s')+1]
    except:
        print('Daaaaale boludo... qué te venís a hacer el Q&A aquí. Gil')
        exit()
else:
    SEARCH_TERM = ''
MAX_FILE_SIZE = 10  # MiB
OUTPUT_DIRECTORY = './datasets/' + sub('[^\w\d-]+','_',SEARCH_TERM) + '/'
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


def getPage(url, method='GET'):
    try:
        if method == 'GET':
            page = requests.get(url, allow_redirects=True)
        elif method == 'HEAD':
            page = requests.head(url,allow_redirects=True)
    except SSLError:
        salir("""Existen problemas con la configuracion SSL de la maquina.
        Editar el archivo /etc/ssl y bajarle el nivel de seguridad
            tal como se detalla en el siguiente link:
            https://stackoverflow.com/questions/55680224/how-to-fix-requests-exceptions-sslerror""")
    except (SSLCertVerificationError, requests.exceptions.SSLError):
        if method == 'GET':
            page = requests.get(url, allow_redirects=True, verify=False)
        elif method == 'HEAD':
            page = requests.head(url, allow_redirects=True, verify=False)
    return page.text if method == 'GET' else page


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
    divs = soup.find_all('div',{'class':'pkg-container'})
    for div in divs:
        csvs = [y for y in [x['href'] for x in div.find_all('a')] if y.startswith('http')]
        if len(csvs) == 1:
            csv = csvs[0]
            if not search('^https?://',csv):
                csv = 'https://' + csv
        else:
            yield None
            continue
        yield csv


def createCsv(fileName, data):
    with open(OUTPUT_DIRECTORY+fileName, 'w') as csv:
        csv.write(data)


def checkFile(link):
    head = getPage(link,method='HEAD')
    try:
        fileName = search('(?<=/)[^/]+?\.\w{3}$', link).group()
    except:
        fileName = search('(?<=filename=).+', head.headers['Content-disposition']).group()
    try:
        size = head.headers['Content-Range'].split('/')[-1]
    except KeyError:
        return -1, 'Desconocido', True, fileName
    if size.isnumeric():
        size = int(size)
    sizeInKiB = size / 1024
    sizeInMiB = sizeInKiB / 1024
    if sizeInMiB < 1:
        if sizeInKiB > MAX_FILE_SIZE * 1024:
            return sizeInKiB, 'KiB', False, fileName
        else:
            return sizeInKiB, 'KiB', True, fileName
    elif sizeInMiB > MAX_FILE_SIZE:
        return sizeInMiB, 'MiB', False, fileName
    else:
        return sizeInMiB, 'MiB', True, fileName


def createDirectory():
    if not isdir(OUTPUT_DIRECTORY):
        try:
            mkdir('./datasets')
        except:
            pass
        finally:
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
            for csvLink in getDataCsv(dsSoup):
                if not csvLink:
                    continue
                sizeCsv, unidad, aceptable, fileName = checkFile(csvLink)
                if isfile(OUTPUT_DIRECTORY + fileName + '.csv'):
                    print('Se saltea {}.'.format(fileName).ljust(100, '.'), 'Ya existe el archivo')
                    continue
                if not sizeCsv:
                    print('Se saltea {}.'.format(fileName).ljust(100, '.'), 'Problemas con headers')
                    continue
                if not aceptable:
                    print('Se saltea {}.'.format(fileName).ljust(100, '.'),
                          'Supera los {}{} ({})'.format(round(MAX_FILE_SIZE, 2), unidad,
                                                        round(sizeCsv, 2)))
                    continue
                print(fileName.ljust(100, '.'), round(sizeCsv, 2), unidad)
                data = getPage(csvLink)
                createCsv(fileName, data)


main()
