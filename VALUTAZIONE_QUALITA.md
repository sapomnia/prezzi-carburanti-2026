# Valutazione della Qualità del Codice e degli Output

**Progetto**: Analisi Prezzi Medi Carburanti – Primo Semestre 2026 (MIMIT)  
**Data valutazione**: Settembre 2026  
**Autore valutazione**: Antigravity Assistant  

---

## 1. Sintesi Esecutiva

La qualità complessiva dell'infrastruttura software e degli output generati all'interno del progetto è **eccellente**. 

Il flusso di lavoro adotta standard elevati tipici del data journalism computazionale e dell'analisi dati avanzata:
- **Codice compatto, idiomatico e modulare**, organizzato in una pipeline sequenziale a passaggi numerati (`01_` $\rightarrow$ `05_`);
- **Robustezza metodologica** nel trattamento di anomalie, outlier e specificità dei dati grezzi ministeriali;
- **Accuratezza geografica** tramite riconciliazione rigorosa tra le anagrafiche del MIMIT e le classificazioni provinciali e comunali Istat (inclusa la transizione amministrativa della Sardegna);
- **Output di livello professionale**, in particolare il file Excel [`output/prezzi_medi_carburanti_S1_2026.xlsx`](output/prezzi_medi_carburanti_S1_2026.xlsx), formattato secondo linee guida editoriali precise (tipizzazione dati, allineamenti, larghezze colonne dinamiche, blocco intestazione).

---

## 2. Scheda di Valutazione per Dimensione

| Dimensione | Punteggio | Sintesi |
|---|:---:|---|
| **Architettura e Modularità** | **9 / 10** | Pipeline sequenziale chiara, separazione delle utilità e configurazioni comuni in `comune.py`, tracciabilità completa dal dato grezzo al report. |
| **Robustezza e Gestione Errori** | **9.5 / 10** | Parser custom specifico per risolvere il disallineamento dei delimitatori `\|` nei CSV ministeriali; normalizzazione delle stringhe e gestione delle omonimie comunali. |
| **Efficienza e Prestazioni** | **8 / 10** | Ottimizzazione dell'uso della memoria tramite tipi `Categorical` su oltre 12 milioni di record; persistenza intermedia tramite `pickle` funzionale ma migliorabile con formati standard a colonne (Parquet). |
| **Data Quality e Verificabilità** | **9.5 / 10** | Controlli di integrità tramite asserzioni programmatiche (nessun giorno perso su 181, completezza di tutte le combinazioni operatore/prodotto e delle 110 province Istat); isolamento trasparente dei record anomali. |
| **Qualità e Fruibilità degli Output** | **9.5 / 10** | Output immediatamente pubblicabili o integrabili in visualizzazioni, privi di valori nulli o incongruenze di tipo; fogli Excel curati al millesimo. |

---

## 3. Analisi Dettagliata dei Componenti del Codice

### 3.1 [`comune.py`](comune.py) – Utilità Condivise, Parsing e Stili
- **Parser custom resiliente (`leggi_anagrafica`)**:  
  Nei file open data del MIMIT, alcuni campi di testo libero (come `Nome Impianto` o la ragione sociale del `Gestore`) contengono illegittimamente il carattere separatore `|` (es. link o doppi nomi). Il parser implementato risolve il problema scansionando da destra i campi geografici/posizionali certi e identificando la posizione di `Tipo Impianto` (`Stradale` o `Autostradale`). Questo garantisce l'estrazione corretta al 100% di tutti i 23.998 record dell'anagrafica senza righe scartate per errore di parsing.
- **Configurazione tipografica Excel (`scrivi_foglio`)**:  
  L'utilizzo di `openpyxl` è accurato: applicazione del font (Arial 10), congelamento del riquadro intestazione (`A2`), formati numerici espliciti (`0.000` per i prezzi a millesimo, `0.0` per percentuali, `@` come testo per salvaguardare gli zeri non significativi nei codici Istat provinciali come `008` o `031`).

### 3.2 [`01_esplora_dati.py`](01_esplora_dati.py) – Esplorazione Preliminare
- Isola le categorie essenziali (`Tipo Impianto`, `Bandiera`, `descCarburante`).
- Permette di verificare i volumi e decidere le regole di raggruppamento prima di impostare la trasformazione pesante.

### 3.3 [`02_prepara_dati.py`](02_prepara_dati.py) – Ingestione e Unione Giornaliera
- **Associazione giorno-per-giorno**:  
  Ogni file prezzi giornaliero viene unito all'anagrafica del rispettivo giorno. Questa scelta è metodologicamente ineccepibile poiché intercetta cambi di bandiera, aperture o chiusure di impianti avvenuti durante il semestre.
- **Filtraggio selettivo**:  
  Mantenimento dei soli carburanti primari standard (*Benzina* e *Gasolio*, escludendo additivati speciali, HVO, GNL, GPL, ecc.) e filtraggio degli impianti autostradali.
- **Ottimizzazione RAM**:  
  Conversione dei campi `bandiera` e `prodotto` a tipo categorico, riducendo l'impronta di memoria a 420 MB per oltre 12 milioni di righe.

### 3.4 [`03_elenco_operatori.py`](03_elenco_operatori.py) – Censimento Bandiere
- Calcola in maniera corretta sia gli impianti unici nel semestre, sia la media giornaliera di impianti attivi, sia la quota percentuale sul totale nazionale.
- Fornisce la fotografia strutturale della rete carburanti in Italia (314 bandiere individuate).

### 3.5 [`04_costruisci_excel.py`](04_costruisci_excel.py) – Aggregazione e Calcolo Medie
- **Filtro anomalie (outlier)**:  
  Scarta i prezzi inferiori a 1.0 €/l o superiori a 3.0 €/l (prezzi test, errori di battitura o mancata conversione decimali), archiviandoli in [`output/prezzi_scartati.csv`](output/prezzi_scartati.csv).
- **Logica dei massimi per operatore**:  
  Individua il picco massimo della **media giornaliera dell'operatore** e la relativa data (risolvendo le parità sulla prima occorrenza cronologica). Questa metrica è preferibile al massimo del singolo impianto, dove spesso compaiono prezzi civetta/segnaposto (es. 2,999 €/l).
- **Integrità garantita da `assert`**:  
  Blocca l'esecuzione se manca anche un solo giorno nel semestre o se non sono presenti tutte le combinazioni stabilite tra date, operatori e prodotti.

### 3.6 [`05_price_cap_province.py`](05_price_cap_province.py) – Riconciliazione Amministrativa
- **Risoluzione della discontinuità amministrativa sarda**:  
  Le sigle automobilistiche MIMIT per la Sardegna (SS, NU, OR, CA, SU) non rispecchiano le 8 province/città metropolitane previste dall'assetto Istat attuale. Il codice mappa ogni impianto sardo al codice UTS della provincia attraverso il codice Istat del comune di appartenenza.
- **Controllo di coerenza**:  
  Verifica che non vi siano impianti privi di assegnazione e che la corrispondenza comune-provincia per il resto d'Italia sia stabile (>95%).

---

## 4. Analisi di Qualità degli Output Prodotti

### 4.1 File Excel Principale: `output/prezzi_medi_carburanti_S1_2026.xlsx`
1. **Foglio 1 – "Media nazionale"** (181 righe):  
   Serie storica completa dal 01/01/2026 al 30/06/2026 per Benzina e Diesel self service. Medie coerenti con l'andamento macroeconomico di periodo.
2. **Foglio 2 – "Per operatore"** (2.896 righe):  
   Formato long/verticale ideale per analisi successive e importazione in software di Business Intelligence o visualizzazione dati (es. Flourish, Datawrapper, Tableau).
3. **Foglio 3 – "Massimi per operatore"** (16 righe):  
   Sintesi dei picchi registrati nel semestre (picchi benzina concentrati a fine maggio 2026; picchi diesel concentrati nella prima metà di aprile 2026).
4. **Foglio 4 – "Price cap per provincia"** (110 righe):  
   Ordinato per quota decrescente di impianti con price cap. 0 valori nulli.

### 4.2 File CSV di Supporto
- **`output/price_cap_province.csv`**:  
  Contiene le 110 province Istat con conteggi assoluti per operatore (Agip Eni, Api-Ip, Q8), totale impianti e quota percentuale calcolata a 1 decimale.
- **`output/elenco_operatori.csv`**:  
  Elenco esaustivo ordinato delle 314 bandiere presenti sul territorio nazionale con relative quote di mercato per punti vendita.
- **`output/prezzi_scartati.csv`**:  
  Traccia dettagliata di 177 prezzi anomali (es. battiture come `2099.0` €/l, valori test come `8.888` o `9.999`, prezzi sotto soglia come `0.141` €/l). Dimostra la pulizia dei dati senza perdita di tracciabilità.
- **`dati_intermedi/log_preparazione.csv`**:  
  Audit trail del semestre: 12.054.663 righe valide conservate, 306.303 righe di stazioni autostradali escluse, 0 record orfani di anagrafica.

---

## 5. Aree di Debolezza e Suggerimenti di Miglioramento

Sebbene il codice sia pienamente funzionante e pronto per la produzione, si evidenziano alcune migliorie architetturali:

### 1. Adozione di Apache Parquet al posto di Pickle
* **Stato attuale**: `02_prepara_dati.py` salva l'output intermedio in un file `.pkl` (420 MB).
* **Criticità**: Il formato `pickle` è dipendente dalla versione di Python/Pandas, non è interoperabile con altri tool e non è ottimizzato per letture parziali.
* **Miglioramento**: L'uso di `pyarrow` / Parquet (`to_parquet(..., compression="zstd")`) ridurrebbe le dimensioni del file su disco di circa il 60-70%, velocizzando l'I/O ed evitando vincoli di versione.

### 2. Allineamento metodologico tra script 03 e script 04
* **Stato attuale**:  
  - In `03_elenco_operatori.py` vengono inclusi tutti i punti vendita stradali, compresi 989 impianti che nel primo semestre 2026 hanno erogato solo servizio servito.  
  - In `04_costruisci_excel.py` viene invece applicato rigorosamente il filtro `isSelf == 1`.
* **Miglioramento**: Esplicitare nel file `03` se il censimento include anche gli impianti solo-servito oppure allineare il filtro `isSelf == 1` per rendere i totali di impianti identici tra i due script.

### 3. Scalabilità dell'accumulo in memoria in `02_prepara_dati.py`
* **Stato attuale**: Le righe giornaliere vengono accumulate in una lista `blocchi` e concatenate alla fine (`pd.concat(blocchi)`).
* **Miglioramento**: Con 181 giorni l'impronta è gestibile su computer moderni; tuttavia, estendendo l'analisi all'intero anno o a più anni, questo approccio rischia di saturare la RAM. Sarebbe preferibile scrivere direttamente su disco in modalità append/partizionata (es. una partizione Parquet per mese).

### 4. Nomenclatura dei file e modularità
* **Stato attuale**: I file iniziano con prefisso numerico (`01_...`, `05_...`), rendendo impossibile l'importazione diretta in Python standard senza ricorrere a `importlib`.
* **Miglioramento**: Riorganizzare la logica di business in moduli regolari (es. `src/analisi.py`, `src/geo.py`) lasciando gli script numerati come semplici file eseguibili (CLI runner).

### 5. Dipendenze e Version Pinning (`requirements.txt`)
* **Stato attuale**: Il file contiene solo `pandas` e `openpyxl` senza versioni specificate.
* **Miglioramento**: Fissare le versioni esatte (es. `pandas==2.2.x`, `openpyxl==3.1.x`, `pyarrow==15.x`) per garantire la piena riproducibilità dell'ambiente in futuro.

---

## 6. Conclusioni

Il codice esaminato si distingue per **rigore analitico, pulizia implementativa ed eccellente presentazione dei risultati**. Le scelte di data cleaning sono ben motivate ed evitano le tipiche trappole degli open data carburanti (outlier estremi, incoerenze geografiche e delimitatori spuri).
