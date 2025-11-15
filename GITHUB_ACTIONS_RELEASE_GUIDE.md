# 🚀 Guida: Release Automatiche Multi-Piattaforma con GitHub Actions

## ✅ Cosa È Stato Implementato

Il tuo progetto **TheNovelist** ora supporta build automatiche per **3 sistemi operativi** direttamente su GitHub!

### File Creati/Aggiornati

1. **`.github/workflows/release.yml`** - Workflow GitHub Actions completo
2. **`build_linux.sh`** - Script build per Linux
3. **`TheNovelist.spec`** - Già configurato per multi-OS (con fix per macOS)

### Sistemi Operativi Supportati

- 🍎 **macOS** - File DMG pronto per installazione
- 🪟 **Windows** - File ZIP con eseguibile
- 🐧 **Linux** - File tar.gz con eseguibile

---

## 🎯 Come Creare una Release

È **semplicissimo**! Bastano 3 comandi:

```bash
# 1. Committa le modifiche
git add .
git commit -m "feat: Nuove funzionalità per v1.0.0"

# 2. Crea un tag di versione
git tag v1.0.0

# 3. Pusha il tag su GitHub
git push origin v1.0.0
```

### ✨ Cosa Succede Automaticamente

Dopo `git push origin v1.0.0`, GitHub Actions:

1. **Avvia 3 build in parallelo** su macchine virtuali:
   - `macos-latest` → Compila TheNovelist.dmg
   - `windows-latest` → Compila TheNovelist-Windows.zip
   - `ubuntu-latest` → Compila TheNovelist-Linux.tar.gz

2. **Durata totale**: ~15-20 minuti (in parallelo!)

3. **Crea automaticamente la Release** su GitHub con:
   - I 3 file pronti per il download
   - Note di rilascio generate automaticamente
   - Istruzioni di installazione in italiano

---

## 📋 Monitorare il Progresso

### Dove Vedere le Build

1. Vai su GitHub: `https://github.com/[tuo-username]/TheNovelist`
2. Clicca su **Actions** (barra in alto)
3. Vedrai il workflow "Build and Release Multi-Platform" in esecuzione

### Stati Possibili

- 🟡 **Giallo (in corso)** - Build in esecuzione
- 🟢 **Verde (successo)** - Build completata, release creata!
- 🔴 **Rosso (fallito)** - Errore durante la build

---

## 📦 Dove Trovare i File

Dopo una build successful, i file saranno disponibili in **2 posti**:

### 1. Artifacts (Temporanei - 90 giorni)

- Tab **Actions** → Clicca sul workflow → Scroll down → **Artifacts**
- Utile per testing pre-release

### 2. Releases (Permanenti)

- Tab **Releases** (sidebar destra) → Ultima release
- **Gli utenti scaricheranno da qui!**
- Link diretto: `https://github.com/[tuo-username]/TheNovelist/releases/latest`

---

## 🎨 Esempio di Release Creata

Quando crei `v1.0.0`, GitHub creerà automaticamente:

```
## TheNovelist v1.0.0

### 📥 Download per il tuo Sistema Operativo:

- 🍎 macOS: TheNovelist.dmg - Aprire e trascinare nella cartella Applicazioni
- 🪟 Windows: TheNovelist-Windows.zip - Estrarre ed eseguire TheNovelist.exe
- 🐧 Linux: TheNovelist-Linux.tar.gz - Estrarre ed eseguire TheNovelist/TheNovelist

### ✨ Novità in questa versione
[Note generate automaticamente da GitHub]

---

Requisiti minimi:
- macOS 11+, Windows 10+, o Linux (Ubuntu 20.04+)
- 4GB RAM
- 1GB spazio su disco
```

---

## 🔧 Convenzioni per i Tag

Usa **Semantic Versioning**: `vMAGGIORE.MINORE.PATCH`

### Esempi

- `v1.0.0` - Prima release pubblica
- `v1.1.0` - Nuove features (compatibile)
- `v1.1.1` - Bug fix
- `v2.0.0` - Breaking changes

### Quando Incrementare

- **MAGGIORE** (v2.0.0): Cambiamenti incompatibili
- **MINORE** (v1.1.0): Nuove funzionalità compatibili
- **PATCH** (v1.0.1): Bug fix

---

## ⚙️ Configurazione Avanzata (Opzionale)

### Modificare il Workflow

File: `.github/workflows/release.yml`

#### Cambiare la versione Python

```yaml
python-version: '3.9'  # Cambia in '3.10', '3.11', etc.
```

#### Aggiungere step personalizzati

Puoi aggiungere step prima o dopo la build:

```yaml
- name: Run tests
  run: pytest tests/

- name: Build documentation
  run: mkdocs build
```

### Build Manuale (Senza Tag)

Puoi anche triggerare il workflow manualmente:

1. Vai su **Actions**
2. Seleziona workflow
3. Clicca **Run workflow** → **Run workflow**

---

## 🐛 Troubleshooting

### Build Fallita su macOS

**Problema**: `create-dmg` non trova l'app

**Soluzione**: Verifica che `build_mac.sh` completi senza errori

### Build Fallita su Windows

**Problema**: Modulo non trovato

**Soluzione**: Aggiungi il modulo a `requirements.txt`

### Build Fallita su Linux

**Problema**: Librerie mancanti

**Soluzione**: Aggiungi le librerie in `.github/workflows/release.yml` → step "Install system dependencies"

```yaml
sudo apt-get install -y \
  libxcb-xinerama0 \
  [altra-libreria]
```

---

## 📊 Limitazioni GitHub Actions (Free Tier)

### Minuti Disponibili

- **Free account**: 2,000 minuti/mese
- **Ogni release**: ~60 minuti totali (20 min × 3 OS)
- **Release possibili**: ~33 release/mese

### Moltiplicatori di Minuti

- macOS: 10× (20 min reali = 200 min contati)
- Windows: 2× (20 min reali = 40 min contati)
- Linux: 1× (20 min reali = 20 min contati)

**Totale per release**: ~260 minuti contati

---

## 🎯 Best Practices

### 1. Test Localmente Prima

```bash
# macOS
./build_mac.sh

# Linux (su VM Ubuntu)
./build_linux.sh

# Windows (su VM Windows)
pyinstaller TheNovelist.spec
```

### 2. Usa Pre-Release per Testing

```bash
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

Poi marca come "Pre-release" su GitHub.

### 3. Mantieni un CHANGELOG

File `CHANGELOG.md`:

```markdown
## [1.0.0] - 2025-01-15
### Added
- Feature X
- Feature Y

### Fixed
- Bug Z
```

---

## 📚 Prossimi Passi

### Ottimizzazioni Possibili

1. **Code Signing**
   - macOS: Notarizzazione Apple
   - Windows: Certificato di firma codice

2. **Installer Nativi**
   - Windows: Inno Setup (`.exe` installer)
   - Linux: AppImage (file singolo eseguibile)
   - macOS: DMG già implementato ✅

3. **Cache Dipendenze**
   - Già implementato con `cache: 'pip'` ✅

4. **Testing Automatico**
   - Aggiungi `pytest` prima della build

---

## ✅ Checklist Prima Release

- [ ] Tutti i test passano localmente
- [ ] `requirements.txt` aggiornato
- [ ] Versione aggiornata in `TheNovelist.spec`
- [ ] CHANGELOG.md aggiornato
- [ ] Tag creato con nome corretto (`v*.*.*`)
- [ ] Push del tag a GitHub
- [ ] Monitorare Actions per errori
- [ ] Verificare Release creata
- [ ] Testare download e installazione

---

## 🆘 Supporto

### Log delle Build

Per vedere i log dettagliati:

1. **Actions** → Clicca sul workflow run
2. Clicca su un job (es. "build-macos")
3. Espandi ogni step per vedere l'output

### Modifiche al Workflow

Dopo modifiche a `.github/workflows/release.yml`:

```bash
git add .github/workflows/release.yml
git commit -m "ci: Update workflow"
git push
```

Poi crea un nuovo tag per testare.

---

## 🎉 Congratulazioni!

Hai ora un sistema di build e release completamente automatizzato!

**Prossimo comando**:

```bash
git tag v1.0.0 && git push origin v1.0.0
```

E guarda la magia accadere! 🚀
