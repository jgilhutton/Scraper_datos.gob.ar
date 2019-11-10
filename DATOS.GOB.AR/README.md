# Scraper de datasets de la página https://datos.gob.ar/

El script se encarga de descargar las bases de datos que encuentre, en base a un criterio de búsqueda o grupo seleccionado.

# Modo de uso:

```
  MAX_FILE_SIZE = 1024  # MiB
  OUTPUT_DIRECTORY = './datasets/'
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
```
- Opción "-s" de consola: Haciendo `python Scraper.py -s "temperatura"` hará una búsqueda de la palabra "temperatura" y descargará todas las db relevantes. Si no se le pasan argumentos, descargará los grupos.
- Opción "-b" de consola: Haciendo `python Scraper.py -b -s "temperatura"` solo mostrará los archivos sin descargarlos.
- Opción "-g de consola: Haciendo `python Scraper.py -s "enfermedad" -g "heal"` buscará el término "enfermedad" en los datasets que pertenezcan al grupo de salud.
- MAX_FILE_SIZE: Maximo tamaño, en megabytes, que deben tener los archivos .csv a descargar. Cualquier archivo que sobrepase esa cantidad de información será salteado y el programa avisará en pantalla.
- OUTPUT_DIRECTORY: Carpeta donde va a ir a parar la información. El programa salteará las bases de datos ya descargadas.
- GRUPOS: Estos son los grupos que ofrece el sitio datos.gob.ar. Si estan todos en False y no se proporcionó ningún término de búsqueda o grupo, la busqueda se efectuará para todos los grupos, caso contrario, el programa buscará solamente en los grupos que sean seteados como True.

# Requerimientos:

- Python > 3.5
-     modulos:
      - requests
      - bs4

# TODO:

- Lograr que el script sea asincrónico o multithreading

# Aviso sobre peticiones inseguras:

Si el script no puede verificar el certificado SSL del sitio web al que se conecta, avisará en pantalla y procederá a repetir la petición sin verificar el certificado. Si esto no es deseable, pueden modificar el script. De todas maneras, estamos bajando solo archivos csv y de sitios oficiales... qué puede malir sal no?

# Bug reports

Por favor, si encuentran algún error en el script, abran un issue en este repositorio o manden un mail a jgilhutton@gmail.com. Tengan en cuenta que este script fue creado en unas pocas horas.
