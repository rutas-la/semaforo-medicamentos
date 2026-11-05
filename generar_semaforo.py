"""
Genera la página del Semáforo de Medicamentos a partir de los reportes del sistema.

Entradas (exportadas a Excel desde el sistema):
  - Listado de Stock (Agrupado, Activos y Con Stock tildados)
  - Consulta de movimientos (Desde = 90 días atrás o más)

Uso:
  python generar_semaforo.py --stock "Listado de Stock.xlsx" --movimientos "Consulta de movimientos.xlsx" --salida index.html
  python generar_semaforo.py --ejemplo --salida index.html      (datos de ejemplo)

Criterio del semáforo (días de cobertura = stock / consumo diario promedio):
  rojo     -> stock <= 0
  amarillo -> cobertura < DIAS_AMARILLO
  verde    -> cobertura >= DIAS_AMARILLO, o hay stock y no hubo consumo en el período
"""
import argparse, json, re, sys, unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

# ---------------- Configuración ----------------
DIAS_AMARILLO = 15          # menos de esto = stock bajo
DIAS_CONSUMO = 90           # ventana para el consumo promedio
# Tipos de movimiento que cuentan como consumo/dispensa (se buscan como texto, sin acentos)
TIPOS_CONSUMO = ["egreso", "salida", "consumo", "dispens", "entrega"]
# Palabras en el genérico/descripción para excluir de la página (descartables, etc.)
EXCLUIR = ["jeringa", "aguja", "gasa", "guante", "cateter", "sonda", "apósito", "aposito",
           "algodon", "algodón", "venda", "tira reactiva", "lanceta", "barbijo", "descartable"]
TZ = timezone(timedelta(hours=-3))
# ------------------------------------------------

AQUI = Path(__file__).resolve().parent


def norm(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def leer_excel(path):
    """Lee el Excel buscando la fila de encabezados (los reportes suelen traer títulos arriba)."""
    raw = pd.read_excel(path, header=None, dtype=object)
    for i in range(min(30, len(raw))):
        fila = [norm(x) for x in raw.iloc[i].tolist()]
        if any("codigo" in c for c in fila) and any(("descrip" in c) or ("generico" in c) for c in fila):
            df = raw.iloc[i + 1:].copy()
            df.columns = [norm(c) for c in raw.iloc[i].tolist()]
            return df.dropna(how="all")
    raise SystemExit(f"No encontré la fila de encabezados en {path}")


def col(df, *claves, obligatoria=True):
    for c in df.columns:
        if any(k in c for k in claves):
            return c
    if obligatoria:
        raise SystemExit(f"Falta una columna con alguno de: {claves}. Columnas: {list(df.columns)}")
    return None


def numero(x):
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(".", "").replace(",", ".") if re.search(r",\d+$", str(x)) else str(x).replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def excluido(texto):
    t = norm(texto)
    return any(norm(e) in t for e in EXCLUIR)


def procesar(stock_path, mov_path):
    st = leer_excel(stock_path)
    c_cod = col(st, "codigo")
    c_gen = col(st, "generico", obligatoria=False)
    c_desc = col(st, "descrip")
    c_stk = col(st, "stock", "existencia", "saldo", "cantidad")

    stock = {}
    for _, r in st.iterrows():
        cod = str(r[c_cod]).strip()
        if not cod or cod == "nan":
            continue
        gen = str(r[c_gen]).strip() if c_gen and not pd.isna(r[c_gen]) else ""
        desc = str(r[c_desc]).strip() if not pd.isna(r[c_desc]) else ""
        e = stock.setdefault(cod, {"gen": gen, "desc": desc, "stock": 0.0})
        e["stock"] += numero(r[c_stk])  # suma depósitos si el listado los separa

    consumo = {}
    if mov_path:
        mv = leer_excel(mov_path)
        m_cod = col(mv, "codigo")
        m_cant = col(mv, "cantidad")
        m_fecha = col(mv, "fecha")
        m_tipo = col(mv, "tipo")
        m_gen = col(mv, "generico", obligatoria=False)
        m_desc = col(mv, "descrip", obligatoria=False)
        mv["_f"] = pd.to_datetime(mv[m_fecha], dayfirst=True, errors="coerce")
        hasta = mv["_f"].max()
        desde = hasta - timedelta(days=DIAS_CONSUMO)
        for _, r in mv.iterrows():
            if pd.isna(r["_f"]) or r["_f"] < desde:
                continue
            if not any(t in norm(r[m_tipo]) for t in TIPOS_CONSUMO):
                continue
            cod = str(r[m_cod]).strip()
            consumo[cod] = consumo.get(cod, 0.0) + abs(numero(r[m_cant]))
            # medicamentos que se consumen pero hoy no figuran en stock -> sin stock
            if cod not in stock:
                stock[cod] = {"gen": str(r[m_gen]).strip() if m_gen and not pd.isna(r[m_gen]) else "",
                              "desc": str(r[m_desc]).strip() if m_desc and not pd.isna(r[m_desc]) else "",
                              "stock": 0.0}

    items = []
    for cod, e in stock.items():
        nombre = e["gen"] or e["desc"]
        if not nombre or excluido(nombre + " " + e["desc"]):
            continue
        diario = consumo.get(cod, 0.0) / DIAS_CONSUMO
        if e["stock"] <= 0:
            estado = "r"
        elif diario > 0 and e["stock"] / diario < DIAS_AMARILLO:
            estado = "a"
        else:
            estado = "v"
        items.append({"n": nombre.strip().capitalize() if nombre.isupper() else nombre.strip(),
                      "d": e["desc"] if e["desc"] and norm(e["desc"]) != norm(nombre) else "",
                      "e": estado})

    # un mismo genérico+presentación en varios códigos: queda el mejor estado
    orden = {"v": 0, "a": 1, "r": 2}
    unicos = {}
    for it in items:
        k = norm(it["n"] + "|" + it["d"])
        if k not in unicos or orden[it["e"]] < orden[unicos[k]["e"]]:
            unicos[k] = it
    return list(unicos.values())


EJEMPLO = [
    ("Enalapril", "10 mg comprimidos", "v"), ("Losartán", "50 mg comprimidos", "v"),
    ("Metformina", "850 mg comprimidos", "a"), ("Atorvastatina", "20 mg comprimidos", "v"),
    ("Levotiroxina", "100 mcg comprimidos", "v"), ("Omeprazol", "20 mg cápsulas", "v"),
    ("Amlodipina", "5 mg comprimidos", "r"), ("Hidroclorotiazida", "25 mg comprimidos", "v"),
    ("Insulina NPH", "100 UI/ml frasco ampolla", "a"), ("Salbutamol", "100 mcg aerosol", "v"),
    ("Clonazepam", "0,5 mg comprimidos", "v"), ("Carbamazepina", "200 mg comprimidos", "a"),
    ("Ácido acetilsalicílico", "100 mg comprimidos", "v"), ("Furosemida", "40 mg comprimidos", "v"),
    ("Glibenclamida", "5 mg comprimidos", "r"), ("Atenolol", "50 mg comprimidos", "v"),
    ("Sertralina", "50 mg comprimidos", "v"), ("Valproato de sodio", "500 mg comprimidos", "a"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stock")
    ap.add_argument("--movimientos")
    ap.add_argument("--salida", default="index.html")
    ap.add_argument("--plantilla", default=str(AQUI / "template.html"))
    ap.add_argument("--ejemplo", action="store_true")
    a = ap.parse_args()

    if a.ejemplo:
        items, ejemplo = [{"n": n, "d": d, "e": e} for n, d, e in EJEMPLO], True
    else:
        if not a.stock:
            sys.exit("Falta --stock")
        items, ejemplo = procesar(a.stock, a.movimientos), False
        if not items:
            sys.exit("El reporte no produjo ningún medicamento; no se publica para no dejar la página vacía.")

    data = {"actualizado": datetime.now(TZ).isoformat(timespec="minutes"), "ejemplo": ejemplo, "items": items}
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = Path(a.plantilla).read_text(encoding="utf-8").replace("/*__DATA__*/", js)
    Path(a.salida).write_text(html, encoding="utf-8")
    c = {k: sum(1 for i in items if i["e"] == k) for k in "var"}
    print(f"OK {len(items)} medicamentos | verde {c['v']} | amarillo {c['a']} | rojo {c['r']} -> {a.salida}")


if __name__ == "__main__":
    main()
