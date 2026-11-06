"""Mínimo para dispensar: unidades necesarias para entregar un tratamiento completo.
Si el stock está por debajo del mínimo, la página muestra "Sin stock" (rojo).
Acordado con farmacia CESAC 21 (06/11/2026). Para cambiar un valor, editar este archivo."""
import re, unicodedata

def _n(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()

# nombre del vademécum (o el comienzo del nombre) -> mínimo
MINIMOS = {
    # antibióticos: un tratamiento completo
    "Amoxicilina 500 mg comprimido": 21,
    "Amoxicilina 1000 mg comprimido": 14,
    "Amoxicilina + ácido clavulánico 850 mg + 125 mg comprimido": 14,
    "Amoxicilina + ácido clavulánico 1000 mg + 125 mg comprimido": 14,
    "Amoxicilina + ácido clavulánico 500 mg + 125 mg comprimido": 21,
    "Cefalexina 500 mg comprimido": 28,
    "Cefalexina 1000 mg comprimido": 14,
    "Cefadroxilo 500 mg comprimido": 14,
    "Cefuroxima 500 mg comprimido": 14,
    "Azitromicina 500 mg comprimido": 3,
    "Claritromicina 500 mg comprimido": 14,
    "Claritromicina 250 mg comprimido": 14,
    "Eritromicina 500 mg comprimido": 28,
    "Ciprofloxacina 500 mg comprimido": 14,
    "Levofloxacina 500 mg comprimido": 7,
    "Norfloxacina 400 mg comprimido": 14,
    "Ofloxacina 200 mg comprimido": 14,
    "Doxiciclina 100 mg comprimido": 14,
    "Metronidazol 500 mg comprimido": 21,
    "Nitrofurantoina 100 mg comprimido": 28,
    "Cotrimoxazol (trimetoprima + sulfametoxazol) 160/800 mg comprimido": 14,
    "Cotrimoxazol (trimetoprima + sulfametoxazol) 80/400 mg comprimido": 28,
    "Clindamicina 300 mg cápsula": 21,
    "Fenoximetilpenicilina 1500000 UI comprimido": 21,
    # suspensiones de antibióticos: 2 frascos
    "Amoxicilina 500 mg/5 ml suspensión": 2, "Amoxicilina 250 mg/5 ml suspensión": 2,
    "Amoxicilina + ácido clavulánico 250 + 62,5 mg/5 ml suspensión": 2,
    "Cefalexina 500 mg/5 ml suspensión": 2, "Cefalexina 250 mg/5 ml suspensión": 2,
    "Cefuroxima 125 mg/5 ml suspensión": 2, "Azitromicina 200 mg/5 ml suspensión": 2,
    "Claritromicina 125 mg/5 ml suspensión": 2, "Claritromicina 250 mg/5 ml suspensión": 2,
    "Eritromicina 200 mg/5 ml suspensión": 2, "Metronidazol 125 mg/5 ml suspensión": 2,
    "Nitrofurantoina 25 mg/5 ml suspensión": 2, "Fenoximetilpenicilina 300000 UI/5 ml suspensión": 2,
    "Cotrimoxazol (trimetoprima + sulfametoxazol) 40/200 mg/5 ml suspensión": 2,
    # insulinas: aproximadamente un mes de un paciente
    "Insulina NPH 100 UI/ml lapicera": 5, "Insulina NPH 100 UI/ml frasco ampolla": 5,
    "Insulina corriente 100 UI/ml cartucho": 5, "Insulina corriente 100 UI/ml frasco ampolla": 5,
    # tratamientos cortos (no crónicos): una dispensa
    "Fluconazol 150 mg comprimido": 1, "Fluconazol 100 mg comprimido": 7, "Fluconazol 200 mg comprimido": 7,
    "Ivermectina 6 mg comprimido": 4, "Mebendazol 200 mg comprimido": 6, "Mebendazol 100 mg comprimido": 6,
    "Mebendazol + tinidazol 200/200 mg comprimido": 4, "Tiabendazol 500 mg comprimido": 6,
    "Aciclovir 800 mg comprimido": 35, "Aciclovir 200 mg comprimido": 25,
    "Clotrimazol 100 mg óvulo": 6, "Metronidazol 500 mg óvulo": 7,
    "Metronidazol + nistatina 500 mg/100.000 UI óvulo": 10, "Nistatina 100.000 UI óvulo": 14,
    "Dimenhidrinato 50 mg comprimido": 10, "Loperamida 2 mg comprimido": 10,
    "Butilhioscina (hioscina) 10 mg comprimido": 10, "Domperidona 10 mg comprimido": 10,
    "Metoclopramida 10 mg comprimido": 10, "Carbón activado 250 mg comprimido": 10,
    "Paracetamol 500 mg comprimido": 10, "Paracetamol 1000 mg comprimido": 10,
    "Ibuprofeno 400 mg comprimido": 10, "Ibuprofeno 600 mg comprimido": 10,
    "Diclofenac sódico 50 mg comprimido": 10, "Diclofenac sódico 75 mg comprimido": 10,
    "Naproxeno 500 mg comprimido": 10, "Clonixinato de lisina 125 mg comprimido": 10,
    "Simeticona 200 mg comprimido": 10, "Prednisona 5 mg comprimido": 10,
    "Meprednisona 40 mg comprimido": 5, "Meprednisona 8 mg comprimido": 10,
    "Loratadina + Betametasona 10/0,6 mg comprimido": 10, "Difenhidramina 50 mg comprimido": 10,
    "Alendronato 70 mg comprimido": 4, "Metotrexato 2,5 mg comprimido": 4,
    "Metotrexato 7,5 mg comprimido": 4, "Metotrexato 10 mg comprimido": 4,
    "Dinitrato de isosorbide 5 mg comprimido sublingual": 10, "Lorazepam 2 mg comprimido sublingual": 10,
    "Sales de rehidratación oral sobre": 2,
}
_MIN = {_n(k): v for k, v in MINIMOS.items()}

def minimo(nombre_vademecum, familia):
    """familia: la de cruce.familia(). Comprimidos y cápsulas de uso crónico: 30 (un mes). Otras formas: 1 unidad."""
    v = _MIN.get(_n(nombre_vademecum))
    if v is not None:
        return v
    return 30 if familia in ("sol", "lp") else 1
