# TheNovelist - Build Instructions

Questa guida spiega come creare eseguibili standalone di TheNovelist per Mac e Windows, da distribuire ai beta tester.

## 📋 Prerequisiti

### Per Mac
- macOS 10.13 o superiore
- Python 3.8 o superiore
- Xcode Command Line Tools: `xcode-select --install`

### Per Windows
- Windows 10 o superiore
- Python 3.8 o superiore (scaricabile da [python.org](https://www.python.org/downloads/))
- Assicurati che Python sia nel PATH

## 🔨 Build per Mac

### Metodo 1: Script Automatico (Consigliato)

```bash
cd /path/to/TheNovelist
./build_mac.sh
```

Lo script eseguirà automaticamente:
1. ✅ Verifica versione Python
2. ✅ Crea/attiva virtual environment
3. ✅ Installa dipendenze
4. ✅ Scarica modello spaCy italiano
5. ✅ Pulisce build precedenti
6. ✅ Crea bundle .app

**Output**: `dist/TheNovelist.app`

### Metodo 2: Manuale

```bash
# 1. Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Installa dipendenze
pip install -r requirements.txt
pip install pyinstaller
python -m spacy download it_core_news_sm

# 3. Build
pyinstaller TheNovelist.spec
```

### Test dell'App Mac

```bash
# Avvia l'applicazione per testare
open dist/TheNovelist.app
```

### Creare DMG per Distribuzione (Opzionale)

```bash
# Installa create-dmg
brew install create-dmg

# Crea DMG
create-dmg \
  --volname "TheNovelist" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "TheNovelist.app" 200 190 \
  --hide-extension "TheNovelist.app" \
  --app-drop-link 600 185 \
  "TheNovelist.dmg" \
  "dist/"
```

## 🔨 Build per Windows

### Metodo 1: Script Automatico (Consigliato)

```cmd
cd C:\path\to\TheNovelist
build_windows.bat
```

Lo script eseguirà automaticamente gli stessi passaggi della versione Mac.

**Output**: `dist\TheNovelist\TheNovelist.exe` + tutte le librerie necessarie

### Metodo 2: Manuale

```cmd
REM 1. Setup virtual environment
python -m venv venv
venv\Scripts\activate.bat

REM 2. Installa dipendenze
pip install -r requirements.txt
pip install pyinstaller
python -m spacy download it_core_news_sm

REM 3. Build
pyinstaller TheNovelist.spec
```

### Test dell'Exe Windows

```cmd
dist\TheNovelist\TheNovelist.exe
```

### Creare Installer per Distribuzione (Opzionale)

Usa [Inno Setup](https://jrsoftware.org/isdl.php) per creare un installer professionale:

1. Scarica e installa Inno Setup
2. Crea uno script `.iss` che punta a `dist\TheNovelist\`
3. Compila per ottenere un file `.exe` di installazione

## 📦 Distribuzione ai Beta Tester

### Mac
**Opzione A - App Bundle** (più semplice)
1. Comprimi `TheNovelist.app` in un file ZIP
2. Invia ai tester con istruzioni:
   - Scarica e decomprimi
   - Trascina TheNovelist.app nella cartella Applicazioni
   - Al primo avvio, click destro → Apri (per bypassare Gatekeeper)

**Opzione B - DMG** (più professionale)
1. Crea DMG come sopra
2. Invia il file `.dmg` ai tester
3. I tester possono montare il DMG e trascinare l'app nelle Applicazioni

### Windows
**Opzione A - Cartella Compressa** (più semplice)
1. Comprimi l'intera cartella `dist\TheNovelist` in un file ZIP
2. Invia ai tester con istruzioni:
   - Scarica e decomprimi in una cartella
   - Esegui `TheNovelist.exe`

**Opzione B - Installer** (più professionale)
1. Crea installer con Inno Setup
2. Invia il file `.exe` installer
3. I tester eseguono l'installer che configura tutto automaticamente

## ⚠️ Note Importanti

### Dimensioni
Le build saranno piuttosto grandi (~400-500 MB) a causa di:
- PySide6 (Qt framework)
- spaCy + modello linguistico italiano
- language-tool-python

### Firma del Codice

**Mac**: Per evitare problemi con Gatekeeper:
- Build non firmata: i tester devono fare click destro → Apri la prima volta
- Build firmata: richiede Apple Developer Account ($99/anno) e certificato

**Windows**: Per evitare avvisi SmartScreen:
- Build non firmata: Windows mostrerà avviso "Unknown publisher"
- Build firmata: richiede certificato di code signing (~$100-300/anno)

### File di Configurazione

L'applicazione salva le configurazioni utente in:
- **Mac**: `~/Library/Application Support/TheNovelist/`
- **Windows**: `%APPDATA%\TheNovelist\`

### Log e Debug

Se i tester riscontrano problemi, possono:
1. **Mac**: Aprire Console.app e filtrare per "TheNovelist"
2. **Windows**: Eseguire da terminale per vedere output

## 🐛 Risoluzione Problemi

### "Module not found" dopo build
- Aggiungi il modulo a `hiddenimports` in `TheNovelist.spec`
- Ricompila

### Resources non trovate
- Verifica che `resources/` sia nella lista `datas` dello spec
- Controlla che il path sia corretto nel codice

### App troppo grande
- Rimuovi dipendenze non necessarie da `requirements.txt`
- Aggiungi moduli non usati a `excludes` nello spec
- Usa UPX compression (già abilitato)

### Windows Defender/Antivirus blocca l'exe
- Normale per exe non firmati
- Aggiungi eccezione nell'antivirus
- Oppure firma il codice

## 📝 Checklist Pre-Distribuzione

Prima di distribuire ai tester, verifica:

- [ ] Build completata senza errori
- [ ] App si avvia correttamente
- [ ] Tutti i template AI sono inclusi in `resources/ai_templates/`
- [ ] Modello spaCy italiano funziona
- [ ] È possibile creare/aprire/salvare progetti
- [ ] Tutte le funzionalità principali funzionano
- [ ] Scritte istruzioni chiare per i tester
- [ ] Preparato canale per raccogliere feedback (email, form, GitHub issues)

## 🚀 Comandi Rapidi

### Mac - Build e Test Completo
```bash
./build_mac.sh && open dist/TheNovelist.app
```

### Windows - Build e Test Completo
```cmd
build_windows.bat && dist\TheNovelist\TheNovelist.exe
```

## 📞 Supporto

Per problemi con la build, controllare:
1. [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
2. [PySide6 Deployment Guide](https://doc.qt.io/qtforpython-6/deployment.html)
3. Log di build in `build/TheNovelist/`
