# Scraper de datasets de la página https://inpres.gob.ar/

El script se encarga de descargar toda la base de datos de sismos.
El servidor donde está alojado el sitio del INPRES es una verdadera basura. Esperen tiempos de respuesta elevados.

# Modo de uso:

```
  START_PAGE = 2
```
- START_PAGE: La primera página se usa para conseguir la cookie. A partir de ahí, busca empezando por esta página
- Los ids de los sismos empiezan desde el 1 siendo el más nuevo. Si quieren unir dos bases de datos que fueron conseguidas en dos tiradas, deben homogeinizar la columna de id, asi no quedan frames repetidos. Ok... ni yo entendí eso.
# Requerimientos:

- Python > 3.5
-     modulos:
      - requests
      - bs4

# TODO:

- Lograr que el script sea asincrónico o multithreading

# Aviso sobre peticiones inseguras:

El sitio no soporta HTTPS, asi que verán ustedes si un hacker le cambia las magnitudes a los sismos.... re peligroso no? ¬¬

# Bug reports

Por favor, si encuentran algún error en el script, abran un issue en este repositorio o manden un mail a jgilhutton@gmail.com. Tengan en cuenta que este script fue creado en unas pocas horas.
