"""
Elenco degli operatori (campo "Bandiera" dell'anagrafica) presenti nel dataset di lavoro,
cioè impianti stradali con prezzi di benzina o gasolio nel primo semestre 2026.

Per ogni bandiera: numero di impianti distinti, impianti medi al giorno e quota sul totale.
Output: output/elenco_operatori.csv
"""
import pandas as pd

from comune import DIR_INTERMEDI, DIR_OUTPUT


def main():
    d = pd.read_pickle(DIR_INTERMEDI / "prezzi_benzina_gasolio.pkl")
    impianti = d.groupby("bandiera", observed=True)["idImpianto"].nunique()
    al_giorno = (d.groupby(["bandiera", "data"], observed=True)["idImpianto"].nunique()
                 .groupby(level=0, observed=True).mean())
    elenco = pd.DataFrame({"impianti_distinti": impianti,
                           "impianti_medi_giorno": al_giorno.round(0).astype(int)})
    elenco["quota_%"] = (elenco["impianti_medi_giorno"] / elenco["impianti_medi_giorno"].sum() * 100).round(2)
    elenco = elenco.sort_values("impianti_medi_giorno", ascending=False)

    DIR_OUTPUT.mkdir(exist_ok=True)
    elenco.to_csv(DIR_OUTPUT / "elenco_operatori.csv")
    print(f"Bandiere distinte: {len(elenco)}\n")
    with pd.option_context("display.max_rows", None):
        print(elenco)


if __name__ == "__main__":
    main()
