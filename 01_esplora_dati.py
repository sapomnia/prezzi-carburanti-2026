"""
Esplorazione preliminare dei dati MIMIT (anagrafica impianti e prezzo alle 8).

Stampa:
- i valori di "Tipo Impianto" (per individuare gli impianti autostradali)
- i valori di "descCarburante" (per isolare benzina e gasolio "base")
- le bandiere presenti (per decidere eventuali raggruppamenti in "Pompe bianche")
"""
import pandas as pd

from comune import file_anagrafica, file_prezzi, leggi_anagrafica, leggi_prezzi


def main():
    f_ana, f_prz = file_anagrafica(), file_prezzi()
    print(f"File anagrafica: {len(f_ana)}  |  file prezzi: {len(f_prz)}")

    # Anagrafica: unione di tutti i giorni, un record per impianto (ultimo visto)
    ana = pd.concat([leggi_anagrafica(f) for f in f_ana], ignore_index=True)
    ana = ana.drop_duplicates("idImpianto", keep="last")
    print(f"\nImpianti distinti nel semestre: {len(ana)}")
    print("\nTipo Impianto:\n", ana["Tipo Impianto"].value_counts(dropna=False))
    print("\nBandiere (numero impianti):")
    with pd.option_context("display.max_rows", None):
        print(ana["Bandiera"].value_counts(dropna=False))

    # Prezzi: descrizioni carburante sull'intero semestre
    carb = pd.Series(dtype="int64")
    for f in f_prz:
        carb = carb.add(leggi_prezzi(f)["descCarburante"].value_counts(), fill_value=0)
    print("\ndescCarburante (righe nel semestre):")
    with pd.option_context("display.max_rows", None):
        print(carb.sort_values(ascending=False).astype(int))


if __name__ == "__main__":
    main()
