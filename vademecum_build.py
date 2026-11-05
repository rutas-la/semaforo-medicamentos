"""Lee 'Table 1' (Nivel 1 – versión 2026) y genera vademecum.json con el nombre para pacientes."""
import json, re, sys
import pandas as pd

def conc_txt(c):
    c = str(c or "").strip()
    if c in ("", "nan"):
        return ""
    if re.fullmatch(r"0?\.\d+", c):                      # 0.005 -> 0,5 %
        v = float(c) * 100
        return (f"{v:.2f}".rstrip("0").rstrip(".")).replace(".", ",") + "%"
    return re.sub(r"\s+", " ", c).replace(" / ", "/")

# nombres de droga reordenados o corregidos para que el paciente los reconozca
DROGA = {
    "Fólico, ácido": "Ácido fólico", "Tióctico, ácido": "Ácido tióctico", "Valproico, ácido": "Ácido valproico",
    "Ursodesoxicólico, Acido": "Ácido ursodesoxicólico", "Hierro, fumarato": "Fumarato ferroso",
    "Hierro, sulfato": "Sulfato ferroso", "Hierro, sulfato + fólico, ácido": "Sulfato ferroso + ácido fólico",
    "Isosorbide, dinitrato": "Dinitrato de isosorbide", "Isosorbide, mononitrato": "Mononitrato de isosorbide",
    "Litio, carbonato": "Carbonato de litio", "Ipratropio, bromuro": "Bromuro de ipratropio",
    "Haloperidol, decanoato": "Haloperidol decanoato", "Clonazepan": "Clonazepam", "Diazepan": "Diazepam",
    "Bisacodilio": "Bisacodilo", "Ezetmibe": "Ezetimibe", "Metil dopa": "Metildopa",
    "Amoxicilina/Ac. Clavulánico": "Amoxicilina + ácido clavulánico", "Losartan potásico": "Losartán",
    "Aspirina": "Aspirina (ácido acetilsalicílico)", "Butilhioscina": "Butilhioscina (hioscina)",
    "Insulina humana de acción intermedia (NPH)": "Insulina NPH",
    "Insulina humana de acción rápida ( Corriente)": "Insulina corriente",
    "Salmeterol y fluticasona propionato": "Salmeterol + fluticasona",
    "Sulfadiazina de plata+ Vitamina A + Lidocaína": "Sulfadiazina de plata + vitamina A + lidocaína",
    "Vitamina B, complejo Vit.B1 + Vit.B2 + Vit. B6 +Vit. B12": "Complejo vitamínico B",
    "Vitamina B, complejo Vit.B1 + Vit.B2 + Vit. B6 +Vit. B13": "Complejo vitamínico B",
    "Cotrimoxazol": "Cotrimoxazol (trimetoprima + sulfametoxazol)",
}
# concentraciones largas -> forma corta
CONC = [
    (r"Trimetoprima 40 mg \+ Sulfametoxazol 200", "40/200 mg/5 ml"),
    (r"Trimetoprima 80 mg", "80/400 mg"), (r"Trimetoprima 160 mg", "160/800 mg"),
    (r"Budesonida 160", "160/4,5 mcg"), (r"Salmeterol 25", "25/125 mcg"),
    (r"Salmeterol 50 - Fluticasona 250", "50/250 mcg"), (r"Salmeterol 50 - Fluticasona 500", "50/500 mcg"),
    (r"Levodopa 200", "200/50 mg"), (r"Levodopa 250", "250/25 mg"),
    (r"Hidroclorotiazida 50", "50/5 mg"), (r"Loratadina 10", "10/0,6 mg"),
    (r"Hierro, sulfato 525", "525/0,35 mg"), (r"Metronidazol 500 mg \+ Nistatina", "500 mg/100.000 UI"),
    (r"Tinindazol 200 mg \+ Mebendazol 200 mg / 5", "200/200 mg/5 ml"), (r"Tinindazol 200", "200/200 mg"),
    (r"^De 1 g", ""), (r"6 mg ACETATO", "6 + 6 mg/ml"), (r"Betametasona 0,1", ""),
    (r"Permetrina 2,50", ""), (r"Cada 0,6 ml", ""), (r"Vit.B1 15", ""), (r"Hidroxicobalamina", ""),
    (r"Cada 100 ml : 25 mg", "400 UI por gota"), (r"Cada 100 ml: Tobramicina", "0,3% + 0,1%"),
    (r"De 3,5 g de Sodio", ""), (r"100 UI/ml x 3 ml", "100 UI/ml"), (r"100 UI/ml x 10 ml", "100 UI/ml"),
    (r"^1 gr \+ 60 UI", ""), (r"^ap[oó]sitos", ""),
]
FORMA = {"comprimido lp": "comprimido de liberación prolongada", "cápsula lp": "cápsula de liberación prolongada",
         "solución p/nebulizar": "solución para nebulizar", "cápsulas ( polvo para inhalar)": "cápsulas para inhalar",
         "tipo aerospacer.": "tipo aerospacer", "unidad": "", "ungüento oftalmico": "ungüento oftálmico",
         "aposito": "apósito", "lapicera prellenada": "lapicera", "frasco ampolla": "frasco ampolla"}

def build(xlsx):
    df = pd.read_excel(xlsx, "Table 1", header=None, dtype=str)
    out = []
    for _, r in df.iloc[6:].iterrows():
        v = [str(x).strip() for x in r.tolist() if str(x).strip() not in ("", "nan")]
        if not v or v == ["STOCK"]:
            continue
        droga = v[0]; forma = v[1] if len(v) > 1 else ""; conc = conc_txt(v[2]) if len(v) > 2 else ""
        for pat, rep in CONC:
            if re.search(pat, conc):
                conc = rep; break
        d = DROGA.get(droga, droga)
        f = FORMA.get(forma.lower(), forma.lower())
        nombre = re.sub(r"\s+", " ", " ".join(x for x in (d, conc, f) if x)).strip()
        out.append({"n": nombre[:1].upper() + nombre[1:], "droga": droga, "forma": forma, "conc": v[2] if len(v) > 2 else ""})
    return out

if __name__ == "__main__":
    items = build(sys.argv[1])
    json.dump(items, open("vademecum.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(len(items))
