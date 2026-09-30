# Prezzi medi di benzina e diesel – primo semestre 2026

Prezzo medio giornaliero self service di benzina e diesel in Italia dal 1° gennaio al 30 giugno 2026,
a livello nazionale e per operatore, calcolato a partire dagli open data del MIMIT
(Osservaprezzi carburanti: anagrafica degli impianti attivi e prezzo alle 8 del mattino).

## Metodologia

- **Fonte**: file giornalieri `anagrafica_impianti_attivi-AAAAMMGG.csv` e `prezzo_alle_8-AAAAMMGG.csv`.
  Ogni file prezzi è associato all'anagrafica dello stesso giorno; la data di riferimento è quella del file.
- **Impianti**: solo impianti stradali (esclusi quelli con `Tipo Impianto = Autostradale`).
- **Carburanti**: solo `Benzina` e `Gasolio` (quest'ultimo riportato come Diesel);
  escluse le versioni speciali/premium (Blue Diesel, HVO, V-Power, Hi-Q, ecc.).
- **Modalità**: solo prezzi self service (`isSelf = 1`).
- **Prezzi anomali**: scartati i prezzi fuori dall'intervallo 1–3 €/l (errori di inserimento,
  es. 1920 invece di 1,920); l'elenco è in `output/prezzi_scartati.csv`.
- **Media**: semplice tra gli impianti (ogni impianto pesa uno); i dati non contengono i volumi venduti.
- **Operatori** (campo `Bandiera`):
  - tenuti distinti: Agip Eni, Api-Ip, Pompe Bianche (come indicato nei dati), Q8, Esso, Tamoil;
  - *Grande distribuzione*: CONAD, Enercoop, Auchan, Iper Station, Carrefour, COOP;
  - *Altri operatori*: tutte le altre bandiere.
- **Price cap per provincia**: dall'anagrafica `anagrafica_impianti_attivi.csv` (estrazione del 28/09/2026),
  impianti stradali, quota di Agip Eni, Api-Ip e Q8 sul totale degli impianti di ogni provincia.
  Si usano le 110 province Istat attuali (`riferimenti/`): poiché il MIMIT usa ancora le vecchie sigle
  sarde (SS, NU, OR, CA, SU), gli impianti della Sardegna sono assegnati alla provincia tramite il comune.

## Struttura

| File | Cosa fa |
|---|---|
| `comune.py` | Percorsi, lettura robusta dei CSV (alcuni nomi impianto e gestori contengono il separatore `\|`), regole di calcolo (self, filtro 1–3 €/l, raggruppamento operatori) e stile Excel |
| `01_esplora_dati.py` | Esplorazione: tipi di impianto, carburanti, bandiere |
| `02_prepara_dati.py` | Unisce prezzi e anagrafica giorno per giorno, filtra carburanti e autostrade → `dati_intermedi/` |
| `03_elenco_operatori.py` | Elenco delle bandiere con numero di impianti → `output/elenco_operatori.csv` |
| `04_costruisci_excel.py` | Calcola le medie e scrive `output/prezzi_medi_carburanti_S1_2026.xlsx` (fogli 1-3) |
| `05_price_cap_province.py` | Quota provinciale delle bandiere con price cap → foglio 4 e `output/price_cap_province.csv` |
| `06_grafico_operatori.py` | Dati del grafico interattivo (operatore, media delle altre bandiere, price cap) → `docs/grafico_prezzi_operatori.html` |
| `07_giorni_sopra_cap.py` | Giorni in cui la media di ogni operatore ha superato il price cap → foglio 5 |
| `08_impianti_sopra_cap.py` | Superamenti del price cap sui singoli distributori → fogli 6 e 7 |
| `grafico/modello_grafico.html` | Modello HTML del grafico (palette mappine); lo script 06 vi inserisce i dati |
| `riferimenti/` | Elenchi Istat di comuni e province (codici aggiornati a febbraio 2026) |
| `VALUTAZIONE_QUALITA.md` | Valutazione del lavoro svolto (codice e output), effettuata con Gemini 3.8 Flash su Antigravity |

Il file Excel ha sette fogli:
- **Media nazionale**: Data, Benzina (€/l), Diesel (€/l);
- **Per operatore** (formato verticale): Data, Operatore, Prodotto, Prezzo medio (€/l);
- **Massimi per operatore**: Operatore, Prodotto, Prezzo medio massimo (€/l), Data. È il picco della media
  giornaliera di ciascun operatore nel semestre (in caso di parità, il primo giorno). Il massimo del singolo
  impianto non è usato perché i valori più alti sono prezzi di comodo (es. 2,999 €/l), non prezzi praticati;
- **Price cap per provincia**: Provincia, Codice Istat provincia, Impianti totali, Agip Eni, Api-Ip, Q8,
  Impianti con price cap, Quota price cap (%);
- **Giorni sopra il price cap**: per ogni operatore, i giorni in cui il prezzo medio del foglio "Per operatore"
  è stato superiore a 1,99 €/l (benzina) e a 2,19 €/l (diesel); un valore uguale al cap non conta;
- **Impianti sopra il cap**: lo stesso calcolo sui singoli distributori, per operatore e prodotto: impianti
  monitorati, impianti sopra il cap almeno un giorno e quota, giornate-impianto sopra il cap e quota,
  giorni medi sopra il cap per impianto (fra quelli che lo hanno superato);
- **Impianti sopra cap per giorno** (formato verticale): Data, Operatore, Prodotto, Impianti con prezzo,
  Impianti sopra il cap, Quota impianti sopra il cap (%).

Nel calcolo sui singoli distributori sono esclusi anche i prezzi pari o superiori a 2,90 €/l (380 prezzi):
sono valori segnaposto (soprattutto 2,999 €/l), mentre i prezzi reali più alti del semestre, ad esempio nelle
isole minori, restano sotto 2,80 €/l. L'elenco è in `output/prezzi_segnaposto_esclusi.csv`.

## Grafico interattivo

`docs/grafico_prezzi_operatori.html` è un file autonomo (dati inclusi) per la newsletter mappine:
prezzo medio giornaliero self per bandiera (default: Agip Eni, benzina), con menu per bandiera e carburante,
la media delle altre bandiere (calcolata sui singoli impianti che non appartengono alla bandiera scelta) e il
price cap (1,99 €/l benzina, 2,19 €/l diesel). L'asse verticale parte da 1,50 €/l, come indicato nel grafico.

Il grafico è pubblicato con GitHub Pages (cartella `docs/` del ramo `main`) e si incorpora così:

```html
<iframe src="https://sapomnia.github.io/prezzi-carburanti-2026/grafico_prezzi_operatori.html"
        title="Prezzi di benzina e diesel per bandiera" width="100%" height="900"
        style="border:0" loading="lazy"></iframe>
```

## Come riprodurre

I CSV grezzi (circa 1,3 GB) non sono nel repository: vanno scaricati dal sito MIMIT e messi nelle cartelle
`Anagrafica primo trimestre/`, `Anagrafica secondo trimestre/`, `Prezzi primo trimestre/`, `Prezzi secondo trimestre/`.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python 02_prepara_dati.py
.venv/bin/python 03_elenco_operatori.py
.venv/bin/python 04_costruisci_excel.py
.venv/bin/python 05_price_cap_province.py
.venv/bin/python 06_grafico_operatori.py
.venv/bin/python 07_giorni_sopra_cap.py
.venv/bin/python 08_impianti_sopra_cap.py
```
