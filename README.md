# Esperimenti DPSP

Il progetto confronta algoritmi di pianificazione per droni su percorsi unidirezionali e bidirezionali. La metrica principale è il makespan. Per ogni istanza con ottimo certificato, il CSV registra anche il rapporto `ρ = makespan dell'algoritmo / makespan ottimo`.

## Struttura del progetto

| Percorso | Contenuto |
|---|---|
| `algoritmi/` | REC, Heap-Based, Bi-Alg, App-N, OPT-NN e le funzioni condivise |
| `ilp/` | Modelli ILP per DPSP, DPSP-N e DPSP-NN |
| `esperimenti.py` | Avvio e ripresa di tutti gli scenari |
| `algoritmi_benchmark.py` | Caricamento degli algoritmi configurabili dal runner |
| `grafici_esperimenti.py` | Generazione dei grafici a partire dal CSV |
| `alg_test.py` | Esempio di esecuzione di REC e Heap-Based unidirezionale |

## Installazione

Esegui i comandi dalla cartella che contiene questo README. Se usi già un ambiente Python con PuLP, HiGHS e Matplotlib, puoi continuare a usare quello. Per creare un ambiente separato su Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "pulp>=2.8,<4" highspy matplotlib
```

## Scenari

| Scenario | Algoritmi | Modello di riferimento |
|---|---|---|
| `dpsp_bi` | Heap-Based bidirezionale, Bi-Alg | ILP |
| `dpsp_n_uni` | App-N | ILP-N |
| `dpsp_n_bi` | App-N bidirezionale | ILP-N |
| `dpsp_nn_bi` | Solo risoluzione esatta | ILP-NN |
| `dpsp_uni` | REC, Heap-Based unidirezionale | ILP |
| `dpsp_nn_uni` | OPT-NN | ILP-NN |

Il benchmark usa HiGHS con 12 thread. La griglia predefinita usa `n = 5, 10, 15` droni, `m = 10, 20, 30, 40` archi, 33 repliche per combinazione ammessa e il seme 42. Nei modelli con capacità dei vertici le partenze sono distinte e le combinazioni con `n > m` sono escluse. Nei due scenari unidirezionali aggiunti per REC e OPT-NN, tutti i droni sono disponibili dallo slot 1. Negli altri scenari la disponibilità è generata tra gli slot 1 e 5.

## Avviare o riprendere gli esperimenti

Per eseguire l'intera griglia e generare i grafici al termine:

```bash
python -u esperimenti.py --output risultati_finali.csv && \
python grafici_esperimenti.py risultati_finali.csv --output grafici_finali_highs
```

Il runner crea un nuovo CSV e si ferma se il file di destinazione esiste già. Per recuperare le repliche complete da un'esecuzione precedente e calcolare quelle mancanti, usa la stessa griglia e lo stesso seme con un nome nuovo per l'uscita:

```bash
python -u esperimenti.py --riprendi-da risultati_finali.csv \
  --output risultati_ripresa.csv
```

Il riepilogo finale indica quante repliche sono state recuperate e quante calcolate. Per impostazione predefinita il risolutore può lavorare senza limite di tempo. Con `--timeout 1800` imponi un limite di 30 minuti per istanza (ovviamente per certificare l'ottimo bisogna eseguirlo senza timeout a meno di essere particolarmente fortunati). Aggiungi `--log-solver` per vedere il log di HiGHS o `--threads N` per scegliere il numero di thread. Usa `python esperimenti.py --help` per vedere tutte le opzioni.

## Generare i grafici da un CSV esistente

Se hai già il CSV finale unito, copialo nella cartella del progetto e genera i grafici direttamente:

```bash
python grafici_esperimenti.py risultati_finali.csv --output grafici_finali_highs
```

Il programma usa le righe con `ρ` valorizzato. Ogni scenario di confronto produce due PNG, uno al variare di `n` e uno al variare di `m`. I numeri tra parentesi indicano quante istanze contribuiscono alla media. Lo scenario `dpsp_nn_bi` registra esiti e tempi nel CSV. Ha solo il modello esatto e quindi non produce grafici di confronto.

## Archiviare i risultati

Conserva il CSV finale, i grafici e i log delle esecuzioni. Se hai riunito risultati ottenuti con CBC e HiGHS, documenta la provenienza dei tempi prima di usarli in un confronto prestazionale. Puoi spostare le vecchie versioni degli script e i CSV intermedi in una cartella di archivio separata dal codice in uso.
