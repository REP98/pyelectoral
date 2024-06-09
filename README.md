# PyElectoral
Librería Python, que permite la consulta de cédulas del [CNE](http://www.cne.gob.ve) de forma fácil y rápida, además permite la carga desde varias fuentes como "JSON", "Excel", "CSV" y "TXT".


## Instalación
Puedes instalar el paquete PyElectoral desde el instalador [PIP](https://pypi.org/)

```shell
$ pip install pyElectoral
```
### Dependecias
PyElectoral Depende de los paquetes 

+ re
+ requests
+ bs4

adicional a esto tenemos dependencias opcionales que son:

+ csv
+ json
+ openpyxl

## Uso

su Uso es muy simple:
```Python
import pyElectoral

c = pyElectoral.CNE()
r: list = c.query("V", 123456789)
print(r)
```

Este ejemeplo imprimiria una clase `ResponseData` con toda la información obtenida de la cédula dada.

La Clase CNE posee los siguietnes Metodos Públicos:
Método `query(nat: str, dni: str|int) -> ResponseData`:
Es el responsable de buscar las cédulas en el [CNE](http://www.cne.gob.ve) y retornar la clase ResposeData con la Información dada
Método `as_dict()->dict`: Convierte el `ResponseData` en un `Dict` Python
Método `set_dict(data: dict) -> None`: `pyElectoral.CNE` usa fraces para poder parcear datos en el registro Electoral y Asi deteminar su estatus este Método permite cambiar los diccionarios de palabras a buscar.
Método `get_dict() -> dict`: Retorna los diccionarios que se usan para buscar en el [CNE](http://www.cne.gob.ve)

Tambien ofrece una propiedad que conserva los ultimos resultados obtenidos
`pyElectoral.CNE.result` es un parametro que contiene el ultimo `ResponseData` Obtenido

Adicional a esta clase Tambien existen otras clases insternas que nos facilitara a la hora de crear o consultar nuestras Cédulas, vistie la Wiki para información.

## Datos Importantes

Es importante destacar que los datos que se obtienen con esta libreria son de dominio publicos al cual cualquiera tiene acceso desde el portar oficial [CNE](http://www.cne.gob.ve), mas sin embargo no me hago responsable por el uso que se le de tanto a esta herramietna como a la información obtenida a travez de ello.

## Licencia
[MIT](LICENSES)