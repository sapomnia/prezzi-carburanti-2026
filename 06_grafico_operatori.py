"""
Grafico interattivo per la newsletter mappine: prezzo medio giornaliero self di benzina e diesel
per operatore (stessi dati del foglio "Per operatore"), con

- la media delle altre bandiere (tutti gli impianti che non appartengono all'operatore scelto),
  calcolata sui prezzi dei singoli impianti e non come media delle medie: ogni impianto pesa uno;
- la linea del price cap (1,99 €/l benzina, 2,19 €/l diesel).

Inserisce i dati nel modello grafico/modello_grafico.html e scrive docs/grafico_prezzi_operatori.html,
un file autonomo pronto per GitHub Pages e per l'incorporamento con iframe.
"""
import json

import pandas as pd

from comune import BASE, FILE_XLSX, ORDINE_OPERATORI, ORDINE_PRODOTTI, PRICE_CAP, carica_dati

MODELLO = BASE / "grafico" / "modello_grafico.html"
FILE_HTML = BASE / "docs" / "grafico_prezzi_operatori.html"
SEGNAPOSTO = "/*__DATI__*/null"


def main():
    d = carica_dati()
    per_op = d.groupby(["prodotto", "operatore", "data"], observed=True)["prezzo"].agg(["sum", "count"])
    totale = d.groupby(["prodotto", "data"], observed=True)["prezzo"].agg(["sum", "count"])

    giorni = pd.date_range("2026-01-01", "2026-06-30")
    serie = {}
    for prodotto in ORDINE_PRODOTTI:
        tot = totale.loc[prodotto].reindex(giorni)
        serie[prodotto] = {}
        for op in ORDINE_OPERATORI:
            s = per_op.loc[(prodotto, op)].reindex(giorni)
            assert s.notna().all().all(), f"Giorni mancanti: {prodotto} {op}"
            media = s["sum"] / s["count"]
            altri = (tot["sum"] - s["sum"]) / (tot["count"] - s["count"])
            serie[prodotto][op] = {"op": media.round(3).tolist(), "altri": altri.round(3).tolist()}

    # Controllo: le medie per operatore coincidono con il foglio "Per operatore" dell'Excel
    foglio = pd.read_excel(FILE_XLSX, sheet_name="Per operatore")
    for r in foglio.sample(300, random_state=1).itertuples(index=False):
        i = giorni.get_loc(pd.Timestamp(r[0]))
        assert abs(serie[r[2]][r[1]]["op"][i] - r[3]) < 1e-9, f"Differenza con l'Excel: {r}"

    dati = {"date": [g.strftime("%Y-%m-%d") for g in giorni], "operatori": ORDINE_OPERATORI,
            "prodotti": ORDINE_PRODOTTI, "priceCap": PRICE_CAP, "serie": serie}
    html = MODELLO.read_text(encoding="utf-8")
    assert SEGNAPOSTO in html
    FILE_HTML.parent.mkdir(exist_ok=True)
    FILE_HTML.write_text(html.replace(SEGNAPOSTO, json.dumps(dati, ensure_ascii=False, separators=(",", ":"))),
                         encoding="utf-8")
    print(f"Scritto {FILE_HTML} ({FILE_HTML.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
