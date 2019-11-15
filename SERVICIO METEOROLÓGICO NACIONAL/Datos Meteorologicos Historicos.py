import requests
from time import strptime,strftime, mktime, localtime
from re import findall
url = 'https://ssl.smn.gob.ar/dpd/descarga_opendata.php?file=observaciones/datohorario{}.txt'
print('Fecha Inicio:> xx/xx/xx\r',end='Fecha Inicio:> ')
fechaInicio = input()
fechaInicioTupla = strptime(fechaInicio,'%d/%m/%y')
print('Fecha Fin:> xx/xx/xx\r',end='Fecha Fin:> ')
fechaFin = input()
fechaFinTupla = strptime(fechaFin,'%d/%m/%y')

indice = ''
datos = []
dia = 86400
now = mktime(fechaInicioTupla)
while now <= mktime(fechaFinTupla):
	fecha = strftime('%Y%m%d',localtime(now))
	fechaRe = strftime('%d%m%Y',localtime(now))
	data = requests.get(url.format(fecha)).text.split('\r\n')
	if not indice:
		indice = '\n'.join(data[:2])
	datos += data[2:]
	now += dia
	
with open('Datos Meteorologicos {} hasta {}.txt'.format(fechaInicio.replace('/','-'), fechaFin.replace('/','-')),'w') as d:
	d.write(indice+'\n')
	d.write('\n'.join(datos))
