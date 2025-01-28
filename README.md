# iNexus Writer Pro

iNexus Writer Pro è un'applicazione avanzata per la generazione di contenuti basata su AI, ispirata dal progetto [AgentWrite](https://github.com/samwit/agent_tutorials/tree/main/agent_write) e arricchita con una moderna interfaccia grafica Streamlit.

## 🌟 Caratteristiche Principali

- **Interfaccia Utente Moderna**: UI intuitiva e responsive realizzata con Streamlit
- **Generazione Strutturata**: Pianificazione automatica e generazione di contenuti in più fasi
- **Monitoraggio Real-time**: Visualizzazione in tempo reale del progresso di generazione
- **Sistema di Revisione**: Possibilità di richiedere miglioramenti e modifiche al contenuto generato
- **Esportazione Markdown**: Salvataggio automatico dei contenuti in formato markdown
- **Supporto Multilingua**: Generazione nativa di contenuti in italiano

## 🛠️ Architettura

L'applicazione è strutturata in tre nodi principali:

1. **Planning Node**: 
   - Genera un piano strutturato per l'articolo
   - Valida il formato e la struttura del piano
   - Definisce il conteggio parole per ogni sezione

2. **Writing Node**:
   - Genera il contenuto seguendo il piano
   - Monitora il conteggio parole
   - Mantiene la coerenza tra le sezioni

3. **Saving Node**:
   - Salva il contenuto in formato markdown
   - Gestisce i metadata del documento
   - Organizza i file in una struttura ordinata

## 🚀 Funzionalità

- **Pianificazione Intelligente**: Generazione automatica di una struttura articolata per l'articolo
- **Scrittura Progressiva**: Generazione del contenuto sezione per sezione
- **Monitoraggio Avanzato**: Progress bar e log in tempo reale
- **Sistema di Feedback**: Possibilità di richiedere modifiche e miglioramenti
- **Gestione Sessioni**: Mantenimento dello stato tra le sessioni
- **UI Responsive**: Interfaccia adattiva e user-friendly

## 💻 Requisiti Tecnici

- Python 3.11+
- Streamlit
- Docker (per il deployment)
- API key per il modello LLM scelto

## 🔧 Configurazione

1. Creare un file `.env` con:
```
ANTHROPIC_API_KEY=your_key_here
```

2. Installare le dipendenze:
```bash
pip install -r requirements.txt
```

3. Avviare l'applicazione:
```bash
streamlit run run.py
```

## 🐳 Deployment con Docker

```bash
docker-compose up -d
```

## 🎨 Personalizzazione

L'interfaccia grafica può essere personalizzata modificando:
- `static/style.css` per lo stile
- Le stringhe nell'UI per il testo
- I parametri di generazione nel file di configurazione

## 📝 Note

- L'applicazione è ottimizzata per la generazione di contenuti in italiano
- Il sistema di revisione permette miglioramenti iterativi
- I contenuti vengono salvati automaticamente in formato markdown

## 🔗 Credits

Ispirato dal progetto [AgentWrite](https://github.com/samwit/agent_tutorials/tree/main/agent_write) e esteso con funzionalità aggiuntive e interfaccia grafica moderna.

## 📄 Licenza

Tutti i diritti riservati © 2024 iNexus