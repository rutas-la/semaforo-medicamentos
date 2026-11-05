"""Simplifica el genérico de SIGEHOS a: droga + concentración + forma farmacéutica."""
import re, unicodedata

def _n(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()

FORMAS = [
    (r"capsula de liberacion prolongada", "cápsula de liberación prolongada"),
    (r"liberacion prolongada|accion prolongada|liberacion osmotica", "comprimido de liberación prolongada"),
    (r"masticable", "comprimido masticable"),
    (r"sublingual", "comprimido sublingual"),
    (r"desleible|bucodispersable", "comprimido bucodispersable"),
    (r"dispersable", "comprimido dispersable"),
    (r"gastrorresistente|cubierta enterica", "comprimido gastrorresistente"),
    (r"comprimido vaginal", "comprimido vaginal"),
    (r"ovulo", "óvulo vaginal"),
    (r"parche", "parche transdérmico"),
    (r"chicle", "chicle"),
    (r"nebulizar", "gotas para nebulizar"),
    (r"aerosol|disparo|inhalacion|dosis", "aerosol para inhalar"),
    (r"spray", "spray"),
    (r"inyectable|vial|ampolla|cartucho|lapicera de 3", "inyectable"),
    (r"unguento", "ungüento"),
    (r"crema", "crema"),
    (r"jarabe", "jarabe"),
    (r"suspension", "suspensión oral"),
    (r"gotas|gotero|solucion oral pediatrica", "gotas"),
    (r"solucion oftalmica|tobramicina", "colirio"),
    (r"solucion", "solución oral"),
    (r"capsula", "cápsula"),
    (r"comprimido|tableta|\[u\]|\bu\b", "comprimido"),
]

SALES = r"\b(como|clorhidrato|clorhirato|sodica|sodico|sodio|potasico|maleato|besilato|fumarato|sulfato de|trihidrato|dihidrato|calcica|anhidra|cinc protamina|sal|n butilbromuro|de plata)\b"

# Nombres que las reglas no resuelven bien (clave: genérico normalizado contiene el texto)
OVERRIDES = [
    ("salmeterol + fluticasona", "Salmeterol 25 mcg + fluticasona 125 mcg aerosol para inhalar"),
    ("budesonida 160 microgramos", "Budesonida 160 mcg + formoterol 4,5 mcg aerosol para inhalar"),
    ("betametasona + gentamicina + miconazol", "Betametasona + gentamicina + miconazol crema"),
    ("cianocobalamina 10 microgramos", "Complejo vitamínico B comprimido"),
    ("vitamina a + c + d", "Vitaminas A + C + D gotas"),
    ("sulfadiazina de plata", "Sulfadiazina de plata + lidocaína + vitamina A crema"),
    ("etambutol 275 mg, isoniazida 75 mg", "Rifampicina + isoniazida + pirazinamida + etambutol comprimido"),
    ("dolutegravir", "Dolutegravir 50 mg + lamivudina 300 mg + tenofovir 300 mg comprimido"),
    ("hierro, sulfato + folico", "Sulfato ferroso 525 mg + ácido fólico 0,35 mg comprimido"),
    ("hierro, sulfato cada 0,6 ml", "Sulfato ferroso 125 mg/ml gotas"),
    ("sulfato ferroso 125 mg/ml", "Sulfato ferroso 125 mg/ml solución oral"),
    ("hierro, fumarato", "Fumarato ferroso 330 mg comprimido"),
    ("calcio, carbonato + colecalciferol", "Carbonato de calcio + vitamina D3 comprimido masticable"),
    ("carbonato de calcio 1,25 g", "Carbonato de calcio 1,25 g comprimido masticable"),
    ("levodopa + benserazida", "Levodopa 200 mg + benserazida 50 mg comprimido"),
    ("levodopa 250 mg + carbidopa", "Levodopa 250 mg + carbidopa 25 mg comprimido"),
    ("amoxicilina + clavulanico, acido cada 5 ml", "Amoxicilina + ácido clavulánico 250/62,5 mg/5 ml suspensión oral"),
    ("amoxicilina + clavulanico, acido amoxicilina", "Amoxicilina + ácido clavulánico 875/125 mg comprimido"),
    ("amoxicilina cada 5 ml: amoxicilina ( como trihidrato) 500", "Amoxicilina 500 mg/5 ml suspensión oral"),
    ("amoxicilina cada 5 ml: amoxicilina ( como trihidrato) 250", "Amoxicilina 250 mg/5 ml suspensión oral"),
    ("sulfametoxazol + trimetoprima de 200/40", "Trimetoprima-sulfametoxazol 200/40 mg/5 ml jarabe"),
    ("sulfametoxazol + trimetoprima sulfametoxazol 800", "Trimetoprima-sulfametoxazol 800/160 mg comprimido"),
    ("metronidazol + nistatina", "Metronidazol 500 mg + nistatina óvulo vaginal"),
    ("articaina", "Articaína + epinefrina inyectable"),
    ("prometazina", "Prometazina 25 mg comprimido"),
    ("penicilina g benzatinica", "Penicilina G benzatínica 2.400.000 UI inyectable"),
    ("insulina isofana", "Insulina NPH 100 UI/ml inyectable"),
    ("insulina humana nph", "Insulina NPH 100 UI/ml inyectable"),
    ("insulina humana recombinante (corriente)", "Insulina corriente 100 UI/ml inyectable"),
    ("calcitriol", "Calcitriol 0,25 mcg cápsula"),
    ("cefalexina 500 mg/5 ml", "Cefalexina 500 mg/5 ml suspensión oral"),
    ("metronidazol de 125 mg/5 ml", "Metronidazol 125 mg/5 ml suspensión oral"),
    ("valproico, acido de 250 mg cada 5 ml", "Ácido valproico 250 mg/5 ml jarabe"),
    ("difenhidramina clorhidrato de 2,5 mg/ml", "Difenhidramina 2,5 mg/ml jarabe"),
    ("ibuprofeno al 2 %", "Ibuprofeno 2% suspensión oral"),
    ("mebendazol al 2 %", "Mebendazol 2% suspensión oral"),
    ("paracetamol al 10 %", "Paracetamol 10% gotas"),
    ("vitamina d (ergocalciferol)", "Vitamina D 1,64 mg/ml gotas"),
    ("betametasona 0.6 mg/ml", "Betametasona 0,6 mg/ml gotas"),
    ("budesonide budesonide 0,1 %", "Budesonida 0,1% gotas para nebulizar"),
    ("budesonide budesonide 200", "Budesonida 200 mcg aerosol para inhalar"),
    ("budesonida 200 microgramos", "Budesonida 200 mcg aerosol para inhalar"),
    ("salbutamol", "Salbutamol 100 mcg aerosol para inhalar"),
    ("fluticasona de 125", "Fluticasona 125 mcg aerosol para inhalar"),
    ("lidocaina 100 mg/1 g", "Lidocaína 10% spray"),
    ("nicotina libera", "Nicotina parche transdérmico"),
    ("metoclopramida al 0,2", "Metoclopramida 0,2% gotas"),
    ("metoclopramida al 0,5", "Metoclopramida 0,5% gotas"),
    ("miconazol 20 mg/g", "Miconazol 2% crema"),
    ("mupirocina (como mupirocina calcica)", "Mupirocina 2% crema"),
    ("gentamicina (como sulfato", "Gentamicina 0,1% crema"),
    ("clotrimazol de 0,1 g", "Clotrimazol 100 mg comprimido vaginal"),
    ("adrenalina", "Adrenalina 1 mg/ml inyectable"),
    ("tobramicina", "Tobramicina 0,3% colirio"),
    ("quetiapina (como fumarato de quetiapina) 200", "Quetiapina 200 mg comprimido de liberación prolongada"),
]

def _cap(s):
    return s[:1].upper() + s[1:]

def simplificar(gen):
    raw = _n(gen)
    for k, v in OVERRIDES:
        if _n(k) in raw:
            return v
    forma = ""
    for pat, nombre in FORMAS:
        if re.search(pat, raw):
            forma = nombre
            break
    t = re.sub(r"\[[^\]]*\]", " ", raw)
    t = re.sub(r"producto que contiene exactamente", " ", t)
    m = re.search(r"\d", t)
    droga = t[: m.start()] if m else t
    resto = t[m.start():] if m else ""
    droga = re.sub(SALES, " ", droga)
    droga = re.sub(r"\b(de|al|en)\b", " ", droga)
    droga = re.sub(r"[.,()]", " ", droga)
    droga = re.sub(r"\s+", " ", droga).strip()
    # "folico acido" -> "acido folico"
    pal = droga.split()
    if len(pal) == 2 and pal[1] == "acido":
        droga = f"acido {pal[0]}"
    conc = ""
    c = re.search(r"(\d+(?:[.,]\d+)?)\s*(miligramos|microgramos|gramos?|mg|mcg|ug|g|ui|%)", resto)
    if c:
        num = c.group(1).replace(".", ",")
        u = {"miligramos": "mg", "microgramos": "mcg", "ug": "mcg", "gramo": "g", "gramos": "g", "ui": "UI"}.get(c.group(2), c.group(2))
        if u == "g" and num == "1":
            num, u = "1000", "mg"
        conc = f"{num} {u}" if u != "%" else f"{num}%"
    acentos = {"acido": "ácido", "folico": "fólico", "acetilsalicilico": "acetilsalicílico", "tioctico": "tióctico",
               "valproico": "valproico", "ursodeoxicolico": "ursodesoxicólico", "losartan": "losartán",
               "fenitoina": "fenitoína", "nitrofurantoina": "nitrofurantoína", "isoniacida": "isoniazida",
               "glimepiride": "glimepirida", "simvastatin": "simvastatina", "diclofenac": "diclofenaco", "isosorbide": "isosorbida", "bupropion": "bupropión",
               "levofloxacino": "levofloxacina", "allopurinol": "alopurinol", "clorhirato": ""}
    droga = " ".join(acentos.get(p, p) for p in droga.split())
    out = " ".join(x for x in (droga, conc, forma) if x)
    return _cap(re.sub(r"\s+", " ", out).strip())
