# Buscador de precedentes de observancia obligatoria (SUNAFIL-TFL)

## Abrir la app
Haga doble clic en `index.html`. No necesita internet ni servidor.

## Qué hace
- **Explorar por temas:** tema general → subtema → tema específico → precedente. Un precedente puede aparecer en varios temas si la resolución tiene más de un origen.
- **Buscar por palabra o frase:** devuelve los precedentes relacionados, con el texto de sus fundamentos (el precedente en sí) y un botón para descargar la resolución completa en PDF. Si no hay coincidencias, indica que no existe ningún precedente relacionado. Admite filtro por año.

## Archivos
- `datos.json`: temas (uno o más por precedente), criterio, palabras clave y fundamentos de cada precedente. Es la única fuente que se edita a mano.
- `plantilla.html`: diseño y lógica de la app.
- `generar.py`: lee los PDF de `../Precedentes Sunafil/`, copia cada uno a `pdf/` con nombre simple (`2024-001.pdf`), extrae el texto de los fundamentos declarados precedente y genera `index.html`.
- `pdf/`: copia de las resoluciones que usan los botones de descarga. La app es autocontenida.

## Actualizar
1. Edite `datos.json`, o agregue PDF nuevos en la carpeta del año correspondiente.
2. Ejecute `python3 generar.py` (vuelve a copiar a `pdf/` solo lo que cambió) desde esta carpeta. Requiere `pdftotext` (en macOS: `brew install poppler`).
3. El script valida la estructura (tres niveles por tema, un PDF por precedente), extrae los textos y avisa si algún fundamento no se pudo ubicar.

## Importante
- Para subir la app a internet, suba la carpeta completa (`index.html` y `pdf/`). No necesita la carpeta `Precedentes Sunafil`.
- Los textos se extraen automáticamente del PDF. Si una resolución tiene un formato atípico, revise el texto mostrado contra el PDF.

## Notas sobre la base
- Se excluyó la Resolución 011-2023, que es una fe de erratas de la 005-2023.
- La Resolución 008-2023 es un Acuerdo que declara criterios interpretativos, no precedentes. Se muestra aparte.
- La Resolución 011-2022 incluye al final texto del precedente de la 012-2022. Conviene verificar la versión oficial.

## Contador de visitas (GoatCounter)

GitHub Pages no guarda visitas, así que el conteo lo hace un servicio externo: **GoatCounter** (gratuito para uso personal, sin cookies y sin pedir datos a los visitantes). La app funciona igual si no hay contador.

### Activarlo (una sola vez)
1. Entre a https://www.goatcounter.com y cree una cuenta.
2. Elija un código para su cuenta (por ejemplo `precedentes-sunafil`). Esa es la dirección de su panel: `https://precedentes-sunafil.goatcounter.com`.
3. En `datos.json`, en la sección `contador`, escriba ese código en `"goatcounter"`:
   ```json
   "contador": { "goatcounter": "precedentes-sunafil", ... }
   ```
4. Ejecute `python3 generar.py` y suba la carpeta a GitHub.

### Ver los datos
Abra su panel de GoatCounter. Ahí verá las visitas (vistas de página), los visitantes únicos por día y las páginas más consultadas.

### Notas
- GoatCounter cuenta **visitas**, no personas. Una misma persona que entra dos veces en un día puede aparecer como dos visitas, según el periodo que mire en el panel.
- Para desactivarlo, deje `"goatcounter": ""` y vuelva a ejecutar `python3 generar.py`.
- Si cambia el código, vuelva a ejecutar `python3 generar.py` antes de subir la carpeta.
