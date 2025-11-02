# TheNovelist - Guida Completa alla Distribuzione

Questa guida spiega il processo completo per distribuire TheNovelist ai beta tester.

---

## 📋 Checklist Pre-Distribuzione

Prima di distribuire, assicurati di aver completato:

- [ ] ✅ Tutti i test manuali passati
- [ ] ✅ Nessun bug critico noto
- [ ] ✅ Build funzionanti su Mac e Windows
- [ ] ✅ Istruzioni per tester pronte
- [ ] ✅ Modulo feedback preparato
- [ ] ✅ Canale di comunicazione stabilito (email, Discord, ecc.)

---

## 🍎 Distribuzione Mac

### Passo 1: Build

```bash
# Dalla directory del progetto
./build_mac.sh
```

Output: `dist/TheNovelist.app`

### Passo 2: Test Build

```bash
# Testa l'app
open dist/TheNovelist.app

# Verifica:
# - L'app si apre correttamente
# - Funzionalità principali funzionano
# - Nessun crash immediato
```

### Passo 3: Crea DMG (Opzionale ma Consigliato)

#### Metodo A: Script Automatico

```bash
./create_dmg.sh
```

Output: `TheNovelist.dmg`

#### Metodo B: Manuale

```bash
# Crea cartella temporanea
mkdir -p dmg_temp
cp -R dist/TheNovelist.app dmg_temp/
ln -s /Applications dmg_temp/Applications

# Crea DMG
hdiutil create -volname "TheNovelist" -srcfolder dmg_temp -ov -format UDZO TheNovelist.dmg

# Pulizia
rm -rf dmg_temp
```

### Passo 4: Prepara Pacchetto Distribuzione

```bash
# Crea cartella distribuzione
mkdir -p distribution/mac

# Opzione A: Solo DMG (consigliato)
cp TheNovelist.dmg distribution/mac/

# Opzione B: ZIP dell'app
cd dist
zip -r ../distribution/mac/TheNovelist.zip TheNovelist.app
cd ..

# Copia istruzioni
cp TESTER_INSTRUCTIONS_MAC.md distribution/mac/
cp BETA_FEEDBACK_TEMPLATE.md distribution/mac/
```

### Passo 5: Distribuzione

1. **Upload su Cloud Storage**:
   - Google Drive, Dropbox, OneDrive, ecc.
   - Crea link condivisibile

2. **Email ai Tester**:
   ```
   Oggetto: TheNovelist Beta - Invito Testing Mac

   Ciao [Nome],

   Grazie per aver accettato di testare TheNovelist!

   Download: [link DMG o ZIP]
   Istruzioni: [link PDF o include nel messaggio]

   Cosa testare:
   - [Lista priorità]

   Scadenza feedback: [data]

   Per segnalazioni: [email/form]

   Grazie!
   ```

---

## 🪟 Distribuzione Windows

### Passo 1: Build su Windows

```cmd
REM Esegui su macchina Windows
build_windows.bat
```

Output: `dist\TheNovelist\TheNovelist.exe` + librerie

### Passo 2: Test Build

```cmd
REM Testa l'exe
dist\TheNovelist\TheNovelist.exe

REM Verifica:
REM - L'app si apre correttamente
REM - Funzionalità principali funzionano
REM - Nessun crash immediato
```

### Passo 3: Crea ZIP

```cmd
REM Comprimi cartella distribuzione
cd dist
powershell Compress-Archive -Path TheNovelist -DestinationPath TheNovelist-Windows.zip
```

### Passo 4: Crea Installer (Opzionale)

Con **Inno Setup**:

1. Scarica [Inno Setup](https://jrsoftware.org/isdl.php)

2. Crea script `installer.iss`:
   ```iss
   [Setup]
   AppName=TheNovelist
   AppVersion=1.0.0
   DefaultDirName={autopf}\TheNovelist
   DefaultGroupName=TheNovelist
   OutputDir=.
   OutputBaseFilename=TheNovelist-Setup

   [Files]
   Source: "dist\TheNovelist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

   [Icons]
   Name: "{group}\TheNovelist"; Filename: "{app}\TheNovelist.exe"
   Name: "{autodesktop}\TheNovelist"; Filename: "{app}\TheNovelist.exe"
   ```

3. Compila con Inno Setup Compiler

Output: `TheNovelist-Setup.exe`

### Passo 5: Prepara Pacchetto Distribuzione

```cmd
REM Crea cartella distribuzione
mkdir distribution\windows

REM Copia ZIP
copy dist\TheNovelist-Windows.zip distribution\windows\

REM Copia installer (se creato)
copy TheNovelist-Setup.exe distribution\windows\

REM Copia istruzioni
copy TESTER_INSTRUCTIONS_WINDOWS.md distribution\windows\
copy BETA_FEEDBACK_TEMPLATE.md distribution\windows\
```

### Passo 6: Distribuzione

Stesso processo del Mac: upload su cloud + email tester.

---

## 📧 Template Email per Tester

### Email Iniziale

```
Oggetto: Invito Beta Testing - TheNovelist

Ciao [Nome],

Sono entusiasta di invitarti al beta testing di TheNovelist, un assistente di scrittura creativa con AI!

🎯 COSA DEVI FARE:

1. Scarica l'app per il tuo sistema:
   - Mac: [link DMG]
   - Windows: [link ZIP/Installer]

2. Segui le istruzioni di installazione (allegate)

3. Testa l'app per almeno [X ore/giorni]

4. Compila il modulo feedback (allegato)

5. Segnala bug e suggerimenti

📅 TIMELINE:
- Inizio: [data]
- Scadenza feedback: [data]
- Durata test: [X settimane]

📝 FOCUS TESTING:
- Creazione e gestione progetti
- Comandi AI personalizzati
- Export documenti
- Stabilità generale

🐛 SEGNALAZIONE BUG:
[Email/Form/Discord/GitHub]

❓ SUPPORTO:
Se hai problemi con l'installazione o l'uso, contattami a [email]

🎁 RINGRAZIAMENTI:
[Eventuali incentivi: accesso gratuito versione finale, crediti, ecc.]

Grazie mille per il tuo contributo!

[Il tuo nome]

---

ALLEGATI:
- TheNovelist_[Mac/Windows].[dmg/zip]
- Istruzioni_Installazione.pdf
- Modulo_Feedback.pdf
```

### Email Reminder (metà testing)

```
Oggetto: TheNovelist Beta - Come va?

Ciao [Nome],

È passata circa metà del periodo di testing di TheNovelist.

Come sta andando? Hai avuto modo di testare l'app?

Reminder veloce:
✅ Testa funzionalità principali
✅ Segnala bug che incontri
✅ Compila feedback (scadenza: [data])

Hai domande o problemi? Scrivimi!

Grazie ancora,
[Il tuo nome]
```

### Email Finale

```
Oggetto: TheNovelist Beta - Ultimo giorno feedback!

Ciao [Nome],

Il periodo di beta testing sta per concludersi!

Se non l'hai ancora fatto, ti chiedo di:
1. ✅ Compilare il modulo feedback
2. ✅ Segnalare eventuali bug finali

Link modulo: [link]

I tuoi feedback sono stati preziosi per migliorare TheNovelist!

Cosa succede ora:
- Analizzerò tutti i feedback
- Correggerò i bug segnalati
- Implementerò i suggerimenti più richiesti
- Rilascerò la versione 1.0 finale

[Se previsto] Ti invierò accesso gratuito alla versione finale!

Grazie infinite per il tuo contributo!

[Il tuo nome]
```

---

## 📊 Gestione Feedback

### Organizzazione

Crea un sistema per tracciare i feedback:

1. **Spreadsheet** (Google Sheets/Excel):
   ```
   | Tester | OS | Bug/Feature | Priorità | Status | Note |
   |--------|----|-----------| ---------|--------|------|
   | Mario  | Mac| Crash su export| Alta  | Open   |      |
   ```

2. **GitHub Issues** (se pubblico/privato):
   - Tag: `bug`, `enhancement`, `question`
   - Milestone: `v1.0-beta`
   - Assegna priorità

3. **Trello/Notion/Asana**:
   - Board con colonne: To Do, In Progress, Testing, Done

### Prioritizzazione Bug

- **P0 - Critico**: App crasha, dati persi, non utilizzabile
  - Fixare immediatamente
- **P1 - Alto**: Funzionalità importante rotta
  - Fixare prima del rilascio
- **P2 - Medio**: Bug fastidioso ma workaround disponibile
  - Fixare se c'è tempo
- **P3 - Basso**: Problema minore/estetico
  - Backlog per versioni future

---

## 📈 Metriche da Tracciare

- **Tester attivi**: Quanti hanno scaricato/installato
- **Completamento feedback**: Quanti hanno compilato il modulo
- **Bug trovati**: Totale e per categoria
- **Crash rate**: Quanti crash segnalati
- **Funzionalità più usate**: Da log (se implementato)
- **Soddisfazione**: Media rating generale

---

## 🔄 Ciclo Iterativo

1. **Distribuisci** → 2. **Raccogli feedback** → 3. **Fixa bug** → 4. **Nuova build** → Ripeti

Per beta prolungati:
- Rilascia build aggiornate ogni 1-2 settimane
- Comunica changelog ai tester
- Ringrazia per feedback specifici implementati

---

## ✅ Checklist Post-Beta

Dopo il periodo di testing:

- [ ] Tutti i bug P0 e P1 risolti
- [ ] Feedback analizzato e prioritizzato
- [ ] Roadmap versioni future definita
- [ ] Changelog scritto
- [ ] Ringraziamenti inviati ai tester
- [ ] Decisione su lancio pubblico
- [ ] Marketing plan (se applicabile)

---

## 🎉 Lancio Finale

Quando sei pronto per v1.0:

1. **Build finale** con tutte le fix
2. **Test finale** approfondito
3. **Firma del codice** (se budget disponibile)
4. **Upload su distribuzione ufficiale**:
   - Website download
   - Mac App Store (richiede Apple Developer)
   - Microsoft Store (richiede account dev)
5. **Annuncio lancio**
6. **Supporto post-lancio**

---

## 📞 Supporto Durante Beta

Preparati a:
- Rispondere a domande tester (entro 24-48h)
- Fixare bug critici rapidamente
- Fornire workaround per problemi noti
- Mantenere comunicazione aperta e trasparente

---

## 💰 Considerazioni Costi (Opzionale)

Se vuoi professionalizzare la distribuzione:

- **Apple Developer**: $99/anno (firma codice Mac, App Store)
- **Microsoft Code Signing**: ~$100-300/anno
- **Servizi cloud**: Google Drive/Dropbox premium per file grandi
- **Tool gestione**: Trello/Notion/Linear (spesso hanno tier free)
- **Email service**: Se molti tester, usa Mailchimp/SendGrid

---

## 🚀 Ready to Ship?

Usa questa checklist finale:

```bash
# 1. Build entrambe le piattaforme
./build_mac.sh              # Su Mac
build_windows.bat           # Su Windows

# 2. Test rapido
open dist/TheNovelist.app
# dist\TheNovelist\TheNovelist.exe

# 3. Crea pacchetti distribuzione
./create_dmg.sh             # Mac
# Compress-Archive dist\TheNovelist  # Windows

# 4. Upload su cloud

# 5. Invia email ai tester

# 6. Monitora feedback

# 7. Itera!
```

---

**Buona distribuzione! 🚀**

_Per domande su questa guida, consulta BUILD.md o contatta il team di sviluppo._
