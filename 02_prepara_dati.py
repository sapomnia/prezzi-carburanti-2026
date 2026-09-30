"""
Costruisce il dataset di lavoro (formato lungo) per il primo semestre 2026.

Per ogni giorno:
1. legge il file "prezzo alle 8" e l'anagrafica dello stesso giorno;
2. tiene solo i carburanti "Benzina" e "Gasolio" (escluse le versioni speciali/premium);
3. associa a ogni impianto bandiera e tipo impianto dall'anagrafica del giorno;
4. esclude gli impianti autostradali (Tipo Impianto == "Autostradale").

Output: dati_intermedi/prezzi_benzina_gasolio.pkl
"""
import pandas as pd

from comune import DIR_INTERMEDI, data_da_nome, file_anagrafica, file_prezzi, leggi_anagrafica, leggi_prezzi

CARBURANTI = {"Benzina": "Benzina", "Gasolio": "Diesel"}


def main():
    anagrafiche = {data_da_nome(f): f for f in file_anagrafica()}
    blocchi, log = [], []

    for f_prz in file_prezzi():
        giorno = data_da_nome(f_prz)
        prz = leggi_prezzi(f_prz)
        prz = prz[prz["descCarburante"].isin(CARBURANTI)]
        ana = leggi_anagrafica(anagrafiche[giorno]).drop_duplicates("idImpianto")

        df = prz.merge(ana[["idImpianto", "Bandiera", "Tipo Impianto"]], on="idImpianto", how="left")
        senza_ana = df["Tipo Impianto"].isna().sum()
        autostrada = (df["Tipo Impianto"] == "Autostradale").sum()
        df = df[df["Tipo Impianto"] == "Stradale"]

        df = pd.DataFrame({
            "data": pd.Timestamp(giorno),
            "idImpianto": df["idImpianto"],
            "bandiera": df["Bandiera"],
            "prodotto": df["descCarburante"].map(CARBURANTI),
            "isSelf": df["isSelf"],
            "prezzo": df["prezzo"].astype(float),
            "dtComu": pd.to_datetime(df["dtComu"], format="%d/%m/%Y %H:%M:%S"),
        })
        blocchi.append(df)
        log.append((giorno, len(prz), autostrada, senza_ana, len(df)))
        print(f"{giorno}: righe benzina/gasolio {len(prz):>6}  autostradali {autostrada:>5}  "
              f"senza anagrafica {senza_ana:>4}  tenute {len(df):>6}")

    tutto = pd.concat(blocchi, ignore_index=True)
    tutto["bandiera"] = tutto["bandiera"].astype("category")
    tutto["prodotto"] = tutto["prodotto"].astype("category")
    DIR_INTERMEDI.mkdir(exist_ok=True)
    tutto.to_pickle(DIR_INTERMEDI / "prezzi_benzina_gasolio.pkl")
    pd.DataFrame(log, columns=["data", "righe_benzina_gasolio", "autostradali",
                               "senza_anagrafica", "tenute"]).to_csv(
        DIR_INTERMEDI / "log_preparazione.csv", index=False)
    print(f"\nTotale righe: {len(tutto):,}")


if __name__ == "__main__":
    main()
