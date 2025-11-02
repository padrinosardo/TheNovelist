# TheNovelist - Istruzioni per Beta Tester (Windows)

Benvenuto/a nel programma di beta testing di **TheNovelist**!

Queste istruzioni ti guideranno nell'installazione e nell'utilizzo dell'applicazione.

---

## 📋 Requisiti di Sistema

- **Windows**: 10 o 11 (64-bit)
- **RAM**: Minimo 4 GB (consigliati 8 GB)
- **Spazio disco**: Circa 1 GB libero
- **Processore**: Intel/AMD dual-core o superiore

---

## 📥 Installazione

### Metodo 1: Da ZIP (Standard)

1. **Scarica** il file `TheNovelist.zip` che ti è stato inviato

2. **Decomprimi** il file ZIP:
   - Click destro sul file → "Estrai tutto..."
   - Scegli una destinazione (es. `C:\Program Files\TheNovelist\`)
   - Oppure semplicemente nella cartella Download

3. **Apri** la cartella estratta `TheNovelist`
   - Troverai il file `TheNovelist.exe` e altre cartelle/file

4. **Opzionale**: Crea un collegamento sul Desktop
   - Click destro su `TheNovelist.exe`
   - "Invia a" → "Desktop (crea collegamento)"

### Metodo 2: Da Installer (se fornito)

1. **Scarica** il file `TheNovelist-Setup.exe`

2. **Esegui** l'installer con doppio click

3. **Segui** la procedura guidata:
   - Accetta licenza
   - Scegli cartella installazione
   - Click su "Installa"

4. L'installer creerà automaticamente collegamenti sul Desktop e nel menu Start

---

## 🚀 Primo Avvio

### Importante: Windows Defender SmartScreen

Poiché TheNovelist non è firmato con un certificato di code signing, Windows potrebbe mostrare un avviso di sicurezza **solo al primo avvio**.

#### Cosa Fare

1. **Doppio click** su `TheNovelist.exe`

2. Potrebbe apparire **"Windows ha protetto il PC"**:
   - Click su **"Ulteriori informazioni"**
   - Click su **"Esegui comunque"**

![SmartScreen Warning](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-defender-smartscreen/images/smartscreen-warning.png)

3. Se l'antivirus chiede conferma, seleziona **"Consenti"**

### Avvii Successivi

Dopo il primo avvio, potrai aprire TheNovelist normalmente con doppio click!

---

## ✅ Verifica Installazione

Al primo avvio, TheNovelist:

1. ✅ Mostrerà la finestra principale
2. ✅ Caricherà i modelli linguistici (può richiedere alcuni secondi)
3. ✅ Sarà pronto per creare o aprire progetti

Se vedi la finestra principale, l'installazione è andata a buon fine!

---

## 🎯 Cosa Testare

Come beta tester, ti chiediamo di esplorare queste funzionalità:

### Funzionalità Principali

- [ ] **Creazione Progetto**: Crea un nuovo progetto di scrittura
- [ ] **Gestione Capitoli e Scene**: Aggiungi, modifica, riordina capitoli e scene
- [ ] **Editor di Testo**: Scrivi e formatta il testo
- [ ] **Comandi AI**: Prova i comandi AI personalizzati (#DESCRIZIONE, #DIALOGO, ecc.)
- [ ] **Template AI**: Testa diversi template per generi (Thriller, Fantasy, Romance, ecc.)
- [ ] **Analisi Linguistica**: Usa gli strumenti di analisi grammaticale
- [ ] **Export**: Esporta in PDF, DOCX, Markdown
- [ ] **Salvataggio/Apertura**: Salva e riapri progetti

### Aspetti da Valutare

1. **Performance**: L'app è fluida o ci sono rallentamenti?
2. **Stabilità**: Ci sono crash o comportamenti anomali?
3. **Usabilità**: L'interfaccia è intuitiva?
4. **Bug**: Hai riscontrato errori o malfunzionamenti?
5. **Funzionalità**: Manca qualcosa di importante?

---

## 🐛 Come Segnalare Bug

Quando trovi un problema:

1. **Descrivi** cosa stavi facendo
2. **Specifica** cosa ti aspettavi che succedesse
3. **Indica** cosa è successo invece
4. **Allega** screenshot se possibile
5. **Includi** informazioni sul tuo sistema:
   - Versione Windows (es. Windows 11 22H2)
   - RAM installata
   - Screenshot errore (se presente)

### Dove Segnalare

Invia i bug via:
- **Email**: [email fornita dall'autore]
- **GitHub Issues**: [se disponibile]
- **Modulo Feedback**: [se disponibile]

---

## 📁 Dove Vengono Salvati i Dati

TheNovelist salva i tuoi dati in:

- **Progetti**: Scegli tu la posizione (es. Documenti\TheNovelist\)
- **Configurazioni**: `%APPDATA%\TheNovelist\`
- **Log**: `%USERPROFILE%\.thenovelist\logs\` (utili per debug)

Per accedere rapidamente:
- Premi `Win+R`
- Digita `%APPDATA%\TheNovelist`
- Premi Invio

---

## ❓ Problemi Comuni

### L'app non si apre

**Problema**: Doppio click non fa nulla
**Soluzione**:
1. Verifica che hai estratto tutto il contenuto del ZIP (non solo l'exe)
2. Prova a eseguire come Amministratore (click destro → "Esegui come amministratore")
3. Controlla che l'antivirus non abbia bloccato file

### "Impossibile trovare VCRUNTIME140.dll"

**Problema**: Errore DLL mancante
**Soluzione**:
1. Scarica e installa [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Riavvia il computer
3. Riprova ad aprire TheNovelist

### Windows Defender blocca l'app

**Problema**: L'antivirus quarantena TheNovelist.exe
**Soluzione**:
1. Apri **Windows Security**
2. "Protezione da virus e minacce" → "Cronologia protezione"
3. Trova TheNovelist → "Azioni" → "Consenti"
4. Aggiungi un'esclusione per la cartella TheNovelist

### L'app si blocca al caricamento

**Problema**: Rimane sulla schermata di caricamento
**Soluzione**:
1. Chiudi l'app (Task Manager → TheNovelist → "Termina attività")
2. Elimina: `%APPDATA%\TheNovelist\`
3. Riapri l'app

### Firewall chiede permessi

**Problema**: Windows Firewall chiede di consentire l'accesso alla rete
**Soluzione**:
- Seleziona **"Consenti l'accesso"** (necessario per funzionalità AI)

---

## 💡 Suggerimenti Utili

### Scorciatoie da Tastiera

- **Ctrl+N**: Nuovo progetto
- **Ctrl+O**: Apri progetto
- **Ctrl+S**: Salva
- **Ctrl+Z**: Annulla
- **Ctrl+Y**: Ripeti

### Best Practices

- **Salva frequentemente**: Usa Ctrl+S regolarmente
- **Backup**: Fai backup dei tuoi progetti importanti
- **Antivirus**: Aggiungi TheNovelist alle eccezioni per evitare rallentamenti
- **Feedback**: Più feedback dai, migliore diventa l'app!

### Performance

Per prestazioni ottimali:
- Chiudi programmi non necessari durante l'uso
- Assicurati di avere almeno 2 GB di RAM libera
- L'app può essere lenta al primo avvio (caricamento modelli)

---

## 🔒 Sicurezza

### È Sicuro?

**Sì!** TheNovelist è sicuro:
- ✅ Nessun malware
- ✅ Nessun virus
- ✅ Codice sorgente verificato

Windows mostra avvisi perché:
- ❌ Non è firmato con certificato Microsoft (costano $300+/anno)
- ❌ È nuovo e non ancora diffuso

Puoi verificare la sicurezza:
1. Scansiona con il tuo antivirus
2. Carica su [VirusTotal.com](https://www.virustotal.com)

---

## 📞 Supporto

Per qualsiasi domanda o problema:

- **Documentazione**: [link se disponibile]
- **FAQ**: [link se disponibile]
- **Contatto**: [email/form dell'autore]

---

## 🙏 Grazie!

Il tuo contributo come beta tester è fondamentale per migliorare TheNovelist.

Ogni bug segnalato, ogni suggerimento, ogni feedback ci aiuta a creare un'app migliore per tutti gli scrittori.

**Buona scrittura!** ✍️

---

## 🛠️ Informazioni Tecniche (Avanzate)

### Requisiti Completi

- Python runtime embedded (incluso)
- Qt Framework (incluso)
- spaCy + modello italiano (incluso)
- Circa 600 MB totali

### Disinstallazione

**Metodo ZIP**:
- Elimina semplicemente la cartella TheNovelist
- Opzionalmente elimina: `%APPDATA%\TheNovelist\`

**Metodo Installer**:
- Pannello di controllo → "Disinstalla un programma"
- Seleziona TheNovelist → "Disinstalla"

---

_Versione 1.0.0 Beta - Ultima modifica: Novembre 2024_
