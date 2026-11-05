"""Cruza el nombre simplificado de SIGEHOS con el vademécum de Nivel 1."""
import json, re, unicodedata
from pathlib import Path

def n(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()

SIN = {  # palabra -> droga canónica
    "aspirina": "acetilsalicilico", "acetilsalicilico": "acetilsalicilico", "butilhioscina": "hioscina", "hioscina": "hioscina",
    "cotrimoxazol": "trimetoprima", "trimetoprima-sulfametoxazol": "trimetoprima", "trimetoprima": "trimetoprima",
    "fumarato": "fumarato ferroso", "sulfato": "sulfato ferroso", "losartan": "losartan",
    "dinitrato": "dinitrato isosorbide", "mononitrato": "mononitrato isosorbide", "isosorbide": None,
    "divalproato": "divalproato", "valproato": "valproato magnesio", "complejo": "vitamina b",
    "diclofenac": "diclofenac", "diclofenaco": "diclofenac", "levotiroxina": "levotiroxina",
    "nitrofurantoina": "nitrofurantoina", "isoniacida": "isoniazida", "clonazepan": "clonazepam", "diazepan": "diazepam",
}

def droga_key(nombre):
    t = n(nombre)
    t = re.sub(r"\(.*?\)", " ", t)
    w = [x for x in re.split(r"[ ,/+]+", t) if x and not re.match(r"^\d", x)]
    if not w: return ""
    if w[0] == "acido" and len(w) > 1: return "acido " + w[1]
    if w[0] == "insulina": return "insulina " + ("nph" if "nph" in t else "corriente")
    if w[0] in ("carbonato",) and "litio" in t: return "litio"
    if w[0] in ("carbonato",) and "calcio" in t: return "carbonato calcio" + (" d3" if "d3" in t else "")
    if w[0] == "sulfato" and "folico" in t: return "sulfato ferroso + folico"
    if w[0] == "vitamina" or w[0] == "vitaminas": return "vitamina " + " ".join(w[1:3])
    k = SIN.get(w[0], w[0])
    combo = "+" in t or " y " in t
    if combo and w[0] not in ("cotrimoxazol", "trimetoprima-sulfametoxazol", "trimetoprima"):
        k += " +" + (w[1] if len(w) > 1 else "")
    return k

def numero(nombre):
    t = n(nombre).replace(".", "").replace(",", ".")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(mg|mcg|ug|g|ui|%)?", t)
    if not m: return None
    v = float(m.group(1)); u = m.group(2) or ""
    if u == "g" and v < 10: v *= 1000
    return round(v, 3)

def familia(nombre):
    t = n(nombre)
    if re.search(r"aerosol|inhalar", t): return "inh"
    if re.search(r"nebulizar", t): return "neb"
    if re.search(r"oftalm|colirio", t): return "oft"
    if re.search(r"crema|unguento|locion|emulsion|gel|aposito", t): return "top"
    if re.search(r"ovulo|vaginal", t): return "vag"
    if re.search(r"inyectable|ampolla|cartucho|lapicera|vial", t): return "iny"
    if re.search(r"gotas|suspension|jarabe|solucion|elixir|sobre", t): return "liq"
    if re.search(r"liberacion prolongada", t): return "lp"
    return "sol"

def clave(nombre):
    return (droga_key(nombre), numero(nombre), familia(nombre))

# Ajustes manuales: nombre simplificado de SIGEHOS -> nombre del vademécum (None = no está en el vademécum)
MANUAL = {
    "Amoxicilina + ácido clavulánico 875/125 mg comprimido": "Amoxicilina + ácido clavulánico 850 mg + 125 mg comprimido",
    "Betametasona 0,6 mg/ml gotas": "Betametasona 0,5 mg/ml gotas orales",
    "Budesonida 160 mcg + formoterol 4,5 mcg aerosol para inhalar": "Budesonida + formoterol 160/4,5 mcg aerosol",
    "Carbonato de calcio 1,25 g comprimido masticable": "Carbonato de calcio 500 mg comprimido",
    "Cloranfenicol 10 mg ungüento": "Cloranfenicol + Colagenasa ungüento dérmico",
    "Isosorbida dinitrato 5 mg comprimido sublingual": "Dinitrato de isosorbide 5 mg comprimido sublingual",
    "Isosorbida mononitrato 20 mg comprimido": "Mononitrato de isosorbide 20 mg comprimido",
    "Lanceta automatica medi safe": "Lancetas",
    "Tira reactiva accu chek": "Tiras reactivas para determinación de glucemia",
    "Aguja subcutanea 32 g": "Agujas para lapicera",
    "Aerospacer": "Aerocámara tipo aerospacer",
    "Levodopa 200 mg + benserazida 50 mg comprimido": "Levodopa + benserazida 200/50 mg comprimido",
    "Levodopa 250 mg + carbidopa 25 mg comprimido": "Levodopa + carbidopa 250/25 mg comprimido",
    "Mebendazol 2% suspensión oral": "Mebendazol 100 mg/5 ml suspensión",
    "Metronidazol 500 mg + nistatina óvulo vaginal": "Metronidazol + nistatina 500 mg/100.000 UI óvulo",
    "Paracetamol 10% gotas": "Paracetamol 100 mg/ml gotas orales",
    "Salmeterol 25 mcg + fluticasona 125 mcg aerosol para inhalar": "Salmeterol + fluticasona 25/125 mcg aerosol",
    "Sulfato ferroso 125 mg/ml gotas": "Sulfato ferroso 12,5 g/100ml gotas orales",
    "Sulfato ferroso 125 mg/ml solución oral": "Sulfato ferroso 12,5 g/100ml gotas orales",
    "Trimetoprima-sulfametoxazol 200/40 mg/5 ml jarabe": "Cotrimoxazol (trimetoprima + sulfametoxazol) 40/200 mg/5 ml suspensión",
    "Trimetoprima-sulfametoxazol 800/160 mg comprimido": "Cotrimoxazol (trimetoprima + sulfametoxazol) 160/800 mg comprimido",
    "Ácido acetilsalicílico 100 mg comprimido": "Aspirina (ácido acetilsalicílico) 100 mg comprimido",
    "Ácido valproico 400 mg comprimido gastrorresistente": "Valproato de magnesio 400 mg comprimido",
    "Ácido valproico 500 mg comprimido gastrorresistente": "Divalproato de sodio 500 mg comprimido",
    "Fenitoína 100 mg cápsula": "Fenitoína sódica 100 mg comprimido",
    "Insulina NPH 100 UI/ml inyectable": "Insulina NPH 100 UI/ml lapicera",
    "Insulina corriente 100 UI/ml inyectable": "Insulina corriente 100 UI/ml cartucho",
    "Sulfadiazina de plata + lidocaína + vitamina A crema": "Sulfadiazina de plata + vitamina A + lidocaína crema",
}

def mapear(sig_nombres, vademecum):
    """Devuelve {nombre SIGEHOS: nombre vademécum o None}."""
    vk = {}
    for v in vademecum:
        vk.setdefault(clave(v["n"]), []).append(v["n"])
    res, directos = {}, set()
    pendientes_lp = []
    for s in sig_nombres:
        if s in MANUAL:
            res[s] = MANUAL[s]; directos.add(MANUAL[s]); continue
        k = clave(s)
        m = vk.get(k)
        if m:
            res[s] = m[0]; directos.add(m[0])
        elif k[2] == "lp":
            pendientes_lp.append((s, k))
        else:
            res[s] = None
    # una presentación de liberación prolongada solo cubre la entrada del vademécum si no hay otra que la cubra
    for s, k in pendientes_lp:
        m = vk.get((k[0], k[1], "sol"))
        res[s] = m[0] if m and m[0] not in directos else None
    return res
