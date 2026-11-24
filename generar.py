#!/usr/bin/env python3
"""Genera index.html (app autocontenida) a partir de datos.json, plantilla.html y los PDF.

Para cada precedente:
  1. localiza su PDF en "Precedentes Sunafil/<año>/" por número y año;
  2. extrae del PDF (con pdftotext) el texto de los fundamentos que el punto resolutivo declara precedente;
  3. valida la estructura de datos.json y escribe index.html con todo incrustado.

Requiere pdftotext (poppler). En macOS: brew install poppler.
"""
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE_PDF = AQUI.parent / "Precedentes Sunafil"
NUM_RE = re.compile(r"(\d{3})\s*-\s*(\d{4})")


def nfc(texto: str) -> str:
    return unicodedata.normalize("NFC", texto)


def indexar_pdfs() -> dict:
    """{'2024-001': Path(...)} para cada PDF de la base."""
    mapa = {}
    for pdf in sorted(BASE_PDF.rglob("*.pdf")):
        anio = pdf.parent.name
        m = NUM_RE.search(nfc(pdf.name))
        if not m or not anio.isdigit():
            sys.exit(f"No se pudo leer número/año de: {pdf}")
        clave = f"{anio}-{m.group(1)}"
        if clave in mapa:
            sys.exit(f"Dos PDF para {clave}: {mapa[clave]} y {pdf.name}")
        mapa[clave] = pdf
    return mapa


def texto_pdf(pdf: Path) -> str:
    exe = shutil.which("pdftotext")
    if not exe:
        sys.exit("Falta pdftotext (poppler). En macOS: brew install poppler")
    salida = subprocess.run([exe, str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    return nfc(salida).replace("ﬁ", "fi").replace("ﬂ", "fl")


# ---------- extracción de fundamentos ----------

RUIDO = [
    r"Firmado por:.*?Fecha:\s*[\d/]+\s+[\d:]+",
    r"El Peruano\s+\w+,?\s+\d{1,2}\s+de\s+\w+\s+de\s+\d{4}",
    r"PRECEDENTES VINCULANTES\s*\(Constitucionales, Judiciales y Administrativos\)",
    r"\b\d{1,3}\s+PRECEDENTES VINCULANTES\b",
    r"PRECEDENTES VINCULANTES\s*\d{0,3}",
    r"forma virtual que permite tramitar sus publicaciones.*?editoraperu\.com\.pe\.",
    r"GERENCIA DE PUBLICACIONES OFICIALES",
    r"FUNDADO EL 22 DE OCTUBRE DE 1825.*?(?=\s[A-ZÁÉÍÓÚ]{4,}\s)",
    r"“AÑO[^”]*”",
]
RUIDO_RE = re.compile("|".join(RUIDO), re.S)
FIN_RE = re.compile(r"POR\s+TANTO|SE\s+RESUELVE|PRECEDENTE[S]?\s+(?:DE\s+)?(?:ADMINISTRATIVO\s+)?(?:DE\s+)?OBSERVANCIA|ACORD[ÓO]\s*:|IV\.\s*ACORD")


def numero_fundamento(texto: str):
    """'6.13' -> (6, 13); '11' -> (11,). Admite subnumerales como '6.5.14' o '6.23.1'."""
    return tuple(int(x) for x in texto.split("."))


def marcadores(cuerpo: str, esquema: str, minimo: tuple):
    """Marcadores de párrafo numerado, en orden creciente.

    Un marcador es válido solo si empieza línea o sigue a un cierre de oración: así no se confunde
    con una cita como "fundamentos 6.61, 6.69 y 6.70". La cadena arranca en el primer marcador
    menor o igual al primer fundamento citado y avanza con saltos pequeños.
    """
    # Algunas resoluciones escriben "6.63. Texto" y otras "6.63 Texto": el punto es opcional,
    # pero el párrafo siempre empieza con mayúscula, comilla o paréntesis.
    if esquema == "6":
        patron = re.compile(r"(?<![\d.])6\.(\d{1,2}(?:\.\d{1,2}){0,2})\.?\s+(?=[A-ZÁÉÍÓÚÑ“\"¿(])")
        valor = lambda m: (6,) + numero_fundamento(m.group(1))
        salto = lambda v, u: v[1] - u[1]
    else:
        patron = re.compile(r"(?<![\d.,])(\d{1,3})\.\s+(?=[A-ZÁÉÍÓÚÑ“\"¿(])")
        valor = lambda m: numero_fundamento(m.group(1))
        salto = lambda v, u: v[0] - u[0]
    fin_previo = re.compile(r"(\n|\x0c|[.;:)”\"])\s*$")
    result, ultimo = [], None
    for m in patron.finditer(cuerpo):
        if m.start() > 0 and not fin_previo.search(cuerpo[max(0, m.start() - 6):m.start()]):
            continue
        v = valor(m)
        if ultimo is None:
            if v > minimo:
                continue
        elif not (v > ultimo and 0 <= salto(v, ultimo) <= 3):
            continue
        result.append((v, m.start(), m.end()))
        ultimo = v
    return result


def _parrafo_suelto(cuerpo: str, esquema: str, clave: tuple):
    """Texto de un fundamento que no entró en la cadena principal (primera aparición válida)."""
    if esquema == "6":
        rx = lambda v: re.compile(r"(?<![\d.])6\." + re.escape(".".join(str(x) for x in v[1:])) + r"\.?\s+(?=[A-ZÁÉÍÓÚÑ“\"¿(])")
    else:
        rx = lambda v: re.compile(r"(?<![\d.,])" + str(v[0]) + r"\.\s+(?=[A-ZÁÉÍÓÚÑ“\"¿(])")
    fin_previo = re.compile(r"(\n|\x0c|[.;:)”\"])\s*$")
    for m in rx(clave).finditer(cuerpo):
        if m.start() > 0 and not fin_previo.search(cuerpo[max(0, m.start() - 6):m.start()]):
            continue
        sig = rx((clave[0],) + ((clave[1] + 1,) if esquema == "6" and len(clave) == 2 else ()) if esquema == "6" else (clave[0] + 1,)).search(cuerpo, m.end())
        fin = sig.start() if sig else len(cuerpo)
        trozo = cuerpo[m.end():fin]
        stop = FIN_RE.search(trozo)
        if stop:
            trozo = trozo[: stop.start()]
        trozo = RUIDO_RE.sub(" ", trozo)
        trozo = re.sub(r"-\n(?=[a-záéíóúñ])", "", trozo)
        return re.sub(r"\s+", " ", trozo).strip()
    return None


def fundamentos_precedente(texto: str, citados: list[str]):
    """Devuelve [(numero, parrafo)] para los fundamentos citados en el punto resolutivo."""
    if not citados:
        return []
    # Se escanea todo el documento: los fundamentos no siempre siguen a "VISTO" en el PDF.
    cuerpo = texto
    esquema = "6" if citados[0].startswith("6.") else "plano"
    marcas = marcadores(cuerpo, esquema, numero_fundamento(min(citados, key=numero_fundamento)))
    indice = {m[0]: k for k, m in enumerate(marcas)}
    salida = []
    for c in citados:
        clave = numero_fundamento(c)
        if clave not in indice:
            # respaldo: marcador suelto con las mismas reglas, hasta el siguiente número
            trozo = _parrafo_suelto(cuerpo, esquema, clave)
            salida.append((c, trozo))
            continue
        k = indice[clave]
        ini = marcas[k][2]
        fin = marcas[k + 1][1] if k + 1 < len(marcas) else len(cuerpo)
        trozo = cuerpo[ini:fin]
        stop = FIN_RE.search(trozo)
        if stop:
            trozo = trozo[: stop.start()]
        trozo = RUIDO_RE.sub(" ", trozo)
        trozo = re.sub(r"-\n(?=[a-záéíóúñ])", "", trozo)
        trozo = re.sub(r"\s+", " ", trozo).strip()
        salida.append((c, trozo))
    return salida


def numeros_citados(texto_fund: str) -> list[str]:
    """'6.13, 6.14 y 6.16' -> ['6.13','6.14','6.16']; '6.26 (literales ...)' -> ['6.26']."""
    texto_fund = re.sub(r"\(.*?\)", "", texto_fund)
    return re.findall(r"\d+(?:\.\d+)*", texto_fund)


# ---------- generación ----------

def contador_html(datos: dict) -> str:
    """Script de GoatCounter (contador de visitas) si datos.json tiene un código de cuenta."""
    codigo = (datos.get("contador", {}).get("goatcounter") or "").strip()
    if not codigo:
        return ""
    if not re.fullmatch(r"[a-z0-9-]{2,63}", codigo):
        sys.exit("contador.goatcounter debe tener solo letras minúsculas, números y guiones")
    return (f'<script data-goatcounter="https://{codigo}.goatcounter.com/count" async '
            f'src="//gc.zgo.at/count.js"></script>')


def pagina_sobre_la_base(plantilla: str, datos: dict) -> str:
    """Página aparte con las notas sobre la base; reutiliza el estilo de la app."""
    cabeza = plantilla[: plantilla.index("</style>") + len("</style>")]
    cabeza = cabeza.replace("<title>Precedentes de observancia obligatoria · SUNAFIL-TFL</title>",
                            "<title>Sobre la base de datos · SUNAFIL-TFL</title>")
    interpretativos = [p for p in datos["precedentes"] if not p["tipo"].startswith("Precedente")]
    from html import escape as e
    bloques = "".join(
        f"<p><strong>{e(p['id'])}</strong> · {e(p['titulo'])}. {e(p['criterio'])}</p>" for p in interpretativos
    ) or "<p>No hay.</p>"
    notas = "".join(f"<li>{e(n)}</li>" for n in datos["notas_base"])
    return f"""{cabeza}
<body>
<header>
  <h1>Sobre la <span class="acento">base de datos</span></h1>
</header>
<main>
  <p><a href="index.html">← Volver al buscador</a></p>
  <h2>Criterios interpretativos (no son precedentes)</h2>
  {bloques}
  <h2>Notas</h2>
  <ul>{notas}</ul>
</main>
</body>
</html>
"""


def main() -> None:
    datos = json.loads((AQUI / "datos.json").read_text(encoding="utf-8"))
    pdfs = indexar_pdfs()

    errores = []
    for p in datos["precedentes"]:
        if not p.get("temas"):
            errores.append(f"{p['id']}: sin temas")
        for ruta in p.get("temas", []):
            if len(ruta) != 3:
                errores.append(f"{p['id']}: cada tema debe tener 3 niveles: {ruta}")
            elif ruta[0] not in datos["temas_generales"]:
                errores.append(f"{p['id']}: tema general desconocido '{ruta[0]}'")
        if p["id"] not in pdfs:
            errores.append(f"{p['id']}: no hay PDF con ese número y año")
    if errores:
        sys.exit("Errores en datos.json:\n  " + "\n  ".join(errores))

    ids = Counter(p["id"] for p in datos["precedentes"])
    repetidos = [i for i, n in ids.items() if n > 1]
    if repetidos:
        sys.exit(f"IDs repetidos: {repetidos}")

    avisos = []
    for p in datos["precedentes"]:
        pdf = pdfs[p["id"]]
        # Copia con nombre simple dentro de la app (pdf/2024-001.pdf): la app se puede subir sola.
        destino = AQUI / "pdf" / f"{p['id']}.pdf"
        destino.parent.mkdir(exist_ok=True)
        if not destino.exists() or destino.stat().st_size != pdf.stat().st_size:
            shutil.copy2(pdf, destino)
        p["archivo"] = f"pdf/{p['id']}.pdf"
        p["archivo_nombre"] = f"Resolucion-{p['numero']}-SUNAFIL-TFL.pdf"
        if not p["tipo"].startswith("Precedente"):
            p["textos"] = []
            continue
        texto = texto_pdf(pdf)
        bloques = []
        for c, trozo in fundamentos_precedente(texto, numeros_citados(p["fundamentos"])):
            if trozo is None:
                avisos.append(f"{p['id']}: no se ubicó el fundamento {c}")
            else:
                bloques.append({"fundamento": c, "texto": trozo})
        p["textos"] = bloques
        if not bloques:
            avisos.append(f"{p['id']}: sin texto de fundamentos")

    plantilla = (AQUI / "plantilla.html").read_text(encoding="utf-8")
    if "__DATOS__" not in plantilla:
        sys.exit("La plantilla no contiene el marcador __DATOS__")
    html = plantilla.replace("__DATOS__", json.dumps(datos, ensure_ascii=False))
    html = html.replace("__CONTADOR__", contador_html(datos))
    (AQUI / "index.html").write_text(html, encoding="utf-8")
    (AQUI / "sobre-la-base.html").write_text(pagina_sobre_la_base(plantilla, datos), encoding="utf-8")

    precedentes = [p for p in datos["precedentes"] if p["tipo"].startswith("Precedente")]
    print(f"index.html generado: {len(precedentes)} precedentes, "
          f"{len(datos['precedentes']) - len(precedentes)} criterio(s) interpretativo(s).")
    print(f"PDF indexados: {len(pdfs)}. Sin entrada en datos.json: {sorted(set(pdfs) - set(ids)) or 'ninguno'}")
    for a in avisos:
        print("AVISO:", a)


if __name__ == "__main__":
    main()
