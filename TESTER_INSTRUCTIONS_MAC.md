# TheNovelist - Istruzioni per Beta Tester (Mac)

Benvenuto/a nel programma di beta testing di **TheNovelist**!

Queste istruzioni ti guideranno nell'installazione e nell'utilizzo dell'applicazione.

---

## 📋 Requisiti di Sistema

- **macOS**: 10.13 (High Sierra) o superiore
- **RAM**: Minimo 4 GB (consigliati 8 GB)
- **Spazio disco**: Circa 1 GB libero
- **Processore**: Intel o Apple Silicon (M1/M2/M3)

---

## 📥 Installazione

### Metodo 1: Da DMG (Consigliato)

1. **Scarica** il file `TheNovelist.dmg` che ti è stato inviato

2. **Apri** il file DMG facendo doppio click
   - Si aprirà una finestra con l'icona di TheNovelist e un'icona Applications

3. **Trascina** l'icona TheNovelist nella cartella Applications
   - Questo copierà l'app nella tua cartella Applicazioni

4. **Espelli** il DMG cliccando sul pulsante espelli nel Finder

### Metodo 2: Da ZIP

1. **Scarica** il file `TheNovelist.zip`

2. **Decomprimi** facendo doppio click sul file ZIP

3. **Trascina** `TheNovelist.app` nella cartella `/Applications`

---

## 🚀 Primo Avvio

### Importante: Bypassing Gatekeeper

Poiché TheNovelist non è firmato con un certificato Apple Developer, dovrai seguire questi passaggi **solo al primo avvio**:

#### Metodo Consigliato

1. Vai nella cartella **Applicazioni**
2. **Click destro** (o Control+Click) su TheNovelist.app
3. Seleziona **"Apri"** dal menu
4. Apparirà un avviso di sicurezza → Click su **"Apri"**

![Gatekeeper Warning](https://support.apple.com/library/content/dam/edam/applecare/images/en_US/macos/Catalina/macos-catalina-system-preferences-security-privacy-general-open-anyway.jpg)

#### Metodo Alternativo (se il precedente non funziona)

1. Prova ad aprire l'app normalmente (doppio click)
2. Apparirà un messaggio di blocco
3. Vai in **Preferenze di Sistema** → **Sicurezza e Privacy**
4. Nella scheda **Generali**, vedrai un messaggio su TheNovelist
5. Click su **"Apri comunque"**
6. Conferma cliccando **"Apri"** nella finestra di dialogo

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
   - Versione macOS (es. macOS 14.2 Sonoma)
   - Modello Mac (es. MacBook Pro M1 2021)

### Dove Segnalare

Invia i bug via:
- **Email**: [email fornita dall'autore]
- **GitHub Issues**: [se disponibile]
- **Modulo Feedback**: [se disponibile]

---

## 📁 Dove Vengono Salvati i Dati

TheNovelist salva i tuoi dati in:

- **Progetti**: Scegli tu la posizione (es. Documenti/TheNovelist/)
- **Configurazioni**: `~/Library/Application Support/TheNovelist/`
- **Log**: `~/.thenovelist/logs/` (utili per debug)

---

## ❓ Problemi Comuni

### L'app non si apre

**Problema**: Doppio click non funziona
**Soluzione**: Usa click destro → Apri (vedi sezione Primo Avvio)

### "L'applicazione è danneggiata"

**Problema**: macOS dice che l'app è danneggiata
**Soluzione**:
```bash
# Apri Terminale e esegui:
xattr -cr /Applications/TheNovelist.app
```
Poi riprova ad aprire

### L'app si blocca al caricamento

**Problema**: Rimane sulla schermata di caricamento
**Soluzione**:
1. Forza chiusura (Cmd+Option+Esc)
2. Elimina: `~/Library/Application Support/TheNovelist/`
3. Riapri l'app

### Modelli linguistici non si caricano

**Problema**: Errori relativi a spaCy o modelli italiani
**Soluzione**: Contatta il team di sviluppo con il file di log

---

## 💡 Suggerimenti Utili

### Scorciatoie da Tastiera

- **Cmd+N**: Nuovo progetto
- **Cmd+O**: Apri progetto
- **Cmd+S**: Salva
- **Cmd+Z**: Annulla
- **Cmd+Shift+Z**: Ripeti

### Best Practices

- **Salva frequentemente**: Usa Cmd+S regolarmente
- **Backup**: Fai backup dei tuoi progetti importanti
- **Feedback**: Più feedback dai, migliore diventa l'app!

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

_Versione 1.0.0 Beta - Ultima modifica: Novembre 2024_
