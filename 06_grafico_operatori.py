"""
Grafico interattivo per la newsletter mappine: prezzo medio giornaliero self di benzina e diesel
per operatore, confrontato con

- il prezzo medio nazionale (media di tutti gli impianti stradali, compresi quelli dell'operatore scelto);
- la linea del price cap (1,99 €/l benzina, 2,19 €/l diesel).

I dati si leggono dal file Excel: foglio "Per operatore" per le serie degli operatori e foglio
"Media nazionale" per il prezzo medio nazionale, così il grafico mostra esattamente i valori dell'Excel.

Inserisce i dati nel modello grafico/modello_grafico.html e scrive docs/grafico_prezzi_operatori.html,
un file autonomo pronto per GitHub Pages e per l'incorporamento con iframe.
"""
import json

import pandas as pd

from comune import BASE, FILE_XLSX, ORDINE_OPERATORI, ORDINE_PRODOTTI, PRICE_CAP

MODELLO = BASE / "grafico" / "modello_grafico.html"
FILE_HTML = BASE / "docs" / "grafico_prezzi_operatori.html"
SEGNAPOSTO = "/*__DATI__*/null"


def main():
    giorni = pd.date_range("2026-01-01", "2026-06-30")

    nazionale = pd.read_excel(FILE_XLSX, sheet_name="Media nazionale").set_index("Data").reindex(giorni)
    assert nazionale.notna().all().all(), "Giorni mancanti nel foglio Media nazionale"
    naz = {p: nazionale[f"{p} (€/l)"].round(3).tolist() for p in ORDINE_PRODOTTI}

    per_op = pd.read_excel(FILE_XLSX, sheet_name="Per operatore")
    tab = per_op.pivot_table(index="Data", columns=["Prodotto", "Operatore"], values="Prezzo medio (€/l)").reindex(giorni)
    serie = {p: {op: tab[(p, op)].round(3).tolist() for op in ORDINE_OPERATORI} for p in ORDINE_PRODOTTI}
    assert tab.notna().all().all(), "Giorni mancanti nel foglio Per operatore"

    dati = {"date": [g.strftime("%Y-%m-%d") for g in giorni], "operatori": ORDINE_OPERATORI,
            "prodotti": ORDINE_PRODOTTI, "priceCap": PRICE_CAP, "serie": serie, "nazionale": naz}
    html = MODELLO.read_text(encoding="utf-8")
    assert SEGNAPOSTO in html
    FILE_HTML.parent.mkdir(exist_ok=True)
    FILE_HTML.write_text(html.replace(SEGNAPOSTO, json.dumps(dati, ensure_ascii=False, separators=(",", ":"))),
                         encoding="utf-8")
    print(f"Scritto {FILE_HTML} ({FILE_HTML.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
