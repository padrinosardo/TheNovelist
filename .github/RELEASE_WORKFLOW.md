# GitHub Actions - Automatic Release Workflow

Questo documento spiega come utilizzare il workflow automatico per creare release di TheNovelist.

## Come Funziona

Il workflow GitHub Actions `.github/workflows/release.yml` si attiva automaticamente quando viene creato un **tag di versione** nel formato `v*.*.*` (es. `v1.0.0`, `v2.1.3`).

### Processo Automatico

Quando crei un tag di versione:

1. ✅ **Build**: Compila l'applicazione macOS usando `build_mac.sh`
2. ✅ **DMG**: Crea il file DMG di distribuzione usando `create_dmg.sh`
3. ✅ **Release**: Crea automaticamente una GitHub Release con:
   - File DMG allegato
   - Note di rilascio generate automaticamente
   - Tag version

## Come Creare una Release

### Metodo 1: Da Terminale (Consigliato)

```bash
# 1. Assicurati che tutti i commit siano pushati
git status
git push

# 2. Crea un tag di versione (es. v2.0.0)
git tag v2.0.0

# 3. Pusha il tag su GitHub
git push origin v2.0.0
```

**Nota**: Usa il formato `v<major>.<minor>.<patch>` (es. `v2.0.0`, `v2.1.0`, `v2.1.1`)

### Metodo 2: Da GitHub Web Interface

1. Vai su **Releases** nella pagina GitHub del repository
2. Clicca su **"Draft a new release"**
3. In **"Choose a tag"**, inserisci un nuovo tag (es. `v2.0.0`)
4. GitHub chiederà di crearlo: clicca **"Create new tag on publish"**
5. Compila titolo e descrizione (opzionale)
6. Clicca **"Publish release"**

### Metodo 3: Da PyCharm

1. Apri **Git → New Tag** dal menu
2. Inserisci il nome del tag (es. `v2.0.0`)
3. Click su **Create Tag**
4. Pusha il tag: **Git → Repository → Push**
5. Seleziona **"Push Tags"** nella finestra di dialogo

## Monitorare il Build

Dopo aver creato il tag:

1. Vai su **Actions** nella pagina GitHub
2. Vedrai il workflow **"Build and Release"** in esecuzione
3. Il processo richiede ~10-15 minuti
4. Una volta completato, la release sarà disponibile in **Releases**

## Struttura della Release

Ogni release include:

```
TheNovelist v2.0.0
├── TheNovelist.dmg (asset scaricabile)
├── Source code (zip)
├── Source code (tar.gz)
└── Release notes (auto-generate da commit)
```

## Versioning

Segui il **Semantic Versioning** (SemVer):

- **MAJOR** (v2.0.0 → v3.0.0): Breaking changes
- **MINOR** (v2.0.0 → v2.1.0): Nuove feature
- **PATCH** (v2.0.0 → v2.0.1): Bug fixes

### Esempi

- `v2.0.0` - Prima release completa (tutte le 4 milestone)
- `v2.1.0` - Aggiunta di nuove funzionalità
- `v2.0.1` - Fix di bug minori

## Troubleshooting

### Il workflow non parte

- ✅ Verifica che il tag inizi con `v` (es. `v2.0.0`, non `2.0.0`)
- ✅ Controlla che il tag sia stato pushato: `git push origin v2.0.0`
- ✅ Verifica nella tab **Actions** se ci sono errori

### Build fallisce

- Controlla i log in **Actions → Build and Release → [workflow run]**
- Verifica che `requirements.txt` sia aggiornato
- Assicurati che tutti i file necessari siano committati

### DMG non viene creato

- Il workflow usa `create-dmg` di Homebrew
- Se fallisce, usa il metodo fallback con `hdiutil`
- Verifica i log di build nella sezione "Create DMG"

## Note

- **Build Time**: Il processo completo richiede circa 10-15 minuti
- **Cache**: Le dipendenze Python vengono cachate per velocizzare i build successivi
- **macOS Only**: Attualmente il workflow supporta solo macOS
- **Storage**: Ogni artifact viene conservato per 90 giorni

## Per Aggiungere Windows/Linux

Il workflow può essere esteso per supportare altre piattaforme:

```yaml
strategy:
  matrix:
    os: [macos-latest, windows-latest, ubuntu-latest]
```

Richiederà script di build specifici per ogni piattaforma.
