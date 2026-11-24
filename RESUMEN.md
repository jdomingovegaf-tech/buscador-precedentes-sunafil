# Resumen de trabajo: buscador de precedentes SUNAFIL-TFL

Para retomar: lea este archivo, luego `README.md` (cómo generar la app) y `datos.json` (la clasificación).

## Estado actual
- **App:** `index.html` autocontenido (se abre con doble clic). Se genera con `python3 generar.py`.
- **Base:** 68 PDF en `../Precedentes Sunafil/` (2021–2025). Son 66 precedentes, 1 criterio interpretativo (2023-008, no es precedente) y 1 fe de erratas excluida (2023-011).
- **Copias de los PDF:** `pdf/` con nombres `AAAA-NNN.pdf` (48 MB). Los botones de descarga apuntan ahí, así que la carpeta `buscador-precedentes-sunafil/` se puede subir sola.
- **Publicación prevista:** GitHub Pages. Aún no se ha hecho commit ni push.
- **Contador:** GoatCounter, configurable en `datos.json` → `contador.goatcounter`. Vacío = sin contador. Falta crear la cuenta del usuario.
- **Marca:** aplicada desde `mi-marca/marca.md` (blanco, tinta `#212120`, navy `#243C54`, dorado `#B48444`, EB Garamond y Arial). Pie con nombre y LinkedIn (quitar si no se quiere).

## Estructura de la app
- **Explorar por temas:** 6 temas generales → subtemas → temas específicos → precedentes. Un precedente puede estar en varias rutas (`temas` es una lista de rutas de 3 niveles). Hay 82 rutas en total.
- **Buscar por palabra o frase:** busca en título, criterio, temas, palabras clave (coincidencia fuerte) y en el texto de los fundamentos (débil: cuenta si aparece 3+ veces). Tiene sinónimos (`SYN` en `plantilla.html`), raíz simple de plurales y filtro por año. Si no hay coincidencias: "No existe ningún precedente… relacionado con «…»".
- **Resultados:** muestran el texto de los fundamentos que el resolutivo declara precedente, resaltan términos y ofrecen descarga del PDF.
- **Página aparte:** `sobre-la-base.html` (criterio interpretativo y notas). Se enlaza desde el pie.

## Archivos clave
- `datos.json`: clasificación, criterios, palabras clave, fundamentos citados, nota del 2022-011, contador.
- `plantilla.html`: diseño y lógica (sin dependencias externas salvo Google Fonts).
- `generar.py`: extrae textos de los PDF con `pdftotext`, copia PDF a `pdf/`, valida y genera `index.html` y `sobre-la-base.html`.

## Decisiones tomadas (y por qué)
- Se excluyó la 011-2023 (fe de erratas) y la 008-2023 se trata como criterio interpretativo, porque su propio texto lo dice.
- La 2022-011 contiene al final texto de la 2022-012: se anota para verificar con El Peruano.
- Búsqueda con dos niveles de peso para evitar que una mención de paso devuelva un precedente.
- Sin modo oscuro: la guía de marca define fondo blanco.
- Se copiaron (no se movieron) los PDF: la carpeta `Precedentes Sunafil` se conserva como respaldo.

## Pendiente / ideas para mejorar
1. **Revisión visual en navegador real** (no se hizo): móvil, impresión y contraste.
2. **Revisar la clasificación temática** con criterio jurídico; algunas resoluciones con varios temas quizá deban ajustarse.
3. **Sinónimos y palabras clave:** ampliar `SYN` y las palabras de `datos.json` según las búsquedas reales.
4. **Texto de precedentes:** verificar a mano una muestra de extracciones (los 343 fundamentos se ubicaron, pero no todos se revisaron uno por uno).
5. **Publicación:** repositorio en GitHub, activar Pages, cuenta de GoatCounter, revisar la privacidad de los nombres de personas naturales que aparecen en algunas resoluciones.
6. **Marca:** si se descarga el manual oficial de formula100k.app, reemplazar los valores de `marca.md` en la plantilla.
7. **Actualizaciones:** nuevos PDF se agregan a la carpeta del año y se registran en `datos.json`; luego `python3 generar.py`.

## Cómo retomar
```
cd /Volumes/Trabajos/07_Proyectos_Apps/buscador-precedentes-sunafil
python3 generar.py
python3 -m http.server 8000   # y abrir http://localhost:8000
```
Requiere `pdftotext` (`brew install poppler`).
