# AI Character Assistant System

Sistema di assistenza AI per lo sviluppo collaborativo dei personaggi.

## Architettura

```
managers/ai/
├── ai_provider.py          # Classe base astratta per provider AI
├── claude_provider.py      # Implementazione Claude (Anthropic)
├── ai_manager.py          # Factory e gestione configurazione
└── README.md              # Questa documentazione
```

## Provider Supportati

### Claude (Anthropic) ✅ Implementato
- Modello: `claude-3-5-sonnet-20241022`
- API Key richiesta
- Ottima qualità per narrativa creativa

### OpenAI (GPT-4/3.5) 🚧 Prossimamente
- Modelli: `gpt-4`, `gpt-3.5-turbo`
- API Key richiesta

### Ollama (Locale) 🚧 Prossimamente
- Modelli: `llama2`, `mistral`, etc.
- Esecuzione locale, privacy totale
- Gratuito ma richiede hardware potente

## Configurazione

### File di Configurazione

La configurazione è salvata in: `~/.thenovelist/ai_config.json`

```json
{
  "active_provider": "claude",
  "providers": {
    "claude": {
      "api_key": "your-api-key-here",
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }
}
```

### Impostare API Key

#### Metodo 1: Variabile d'ambiente
```bash

export ANTHROPIC_API_KEY="x-api-key: REDACTED"
```

#### Metodo 2: Tramite AIManager (programmatico)
```python
from managers.ai import AIManager

ai_manager = AIManager()
ai_manager.update_provider_config('claude', {
    'api_key': 'your-key-here'
})
```

#### Metodo 3: UI Settings (da implementare)
- Aprire Settings → AI Configuration
- Selezionare provider
- Inserire API key
- Salvare

## Utilizzo

### Esempio Base

```python
from managers.ai import AIManager, AIMessage

# Inizializza manager
ai_manager = AIManager()

# Crea conversazione
messages = [
    AIMessage(
        role='user',
        content='Aiutami a sviluppare un personaggio per un thriller...'
    )
]

# Genera risposta
response = ai_manager.generate_for_character(messages)

if response.success:
    print(response.content)
    print(f"Token usati: {response.usage}")
else:
    print(f"Errore: {response.error}")
```

### Conversazione Multi-Turn

```python
# Prima interazione
messages = [AIMessage(role='user', content='Contesto narrativo...')]
response1 = ai_manager.generate_for_character(messages)

# Aggiungi alla cronologia
messages.append(AIMessage(role='assistant', content=response1.content))
messages.append(AIMessage(role='user', content='Dettagli aggiuntivi...'))

# Seconda interazione (mantiene contesto)
response2 = ai_manager.generate_for_character(messages)
```

### Salvare Cronologia in Character

```python
from models.character import Character

# Crea personaggio
character = Character(name="Dr. Anna Rossi")

# Salva conversazione
character.ai_conversation_history = [msg.to_dict() for msg in messages]

# Il salvataggio avviene automaticamente tramite CharacterManager
```

## System Prompt

Il sistema usa un prompt specializzato per lo sviluppo personaggi:

- Assistente esperto in character development
- Domande chiarificatrici su contesto e genere
- Suggerimenti dettagliati per: fisica, psicologia, background
- Formato strutturato per facile applicazione
- Tono collaborativo

## Struttura Dati

### AIMessage

```python
@dataclass
class AIMessage:
    role: str          # 'user' | 'assistant' | 'system'
    content: str       # Testo del messaggio
    timestamp: str     # ISO format
    metadata: dict     # Metadati opzionali
```

### AIResponse

```python
@dataclass
class AIResponse:
    content: str       # Contenuto generato
    success: bool      # True se successo
    error: str         # Messaggio errore (se success=False)
    usage: dict        # Token usage: {input_tokens, output_tokens}
    metadata: dict     # Metadati provider-specific
```

## Test

### Test Manuale

```bash
# Imposta API key
export ANTHROPIC_API_KEY="your-key-here"

# Esegui test
python test_ai_character_assistant.py
```

Output atteso:
- Inizializzazione AI Manager ✓
- Configurazione provider ✓
- Prima interazione con AI ✓
- Seconda interazione (conversazione) ✓
- Salvataggio cronologia ✓

## Costi e Limiti

### Claude (Anthropic)
- Pricing: https://www.anthropic.com/pricing
- Claude 3.5 Sonnet: ~$3/$15 per 1M token (input/output)
- Conversazione tipica: ~1000-3000 token = $0.05-0.15

### Best Practices
- Usare temperature 0.7 per bilanciare creatività e coerenza
- Max tokens 2000 è sufficiente per dettagli completi
- Salvare cronologia per evitare ripetizioni costose
- Permettere rigenerazione selettiva di singoli aspetti

## Roadmap

### Step 1: ✅ Sistema Base (Corrente)
- [x] Architettura provider astratta
- [x] Claude provider
- [x] AI Manager
- [x] Estensione Character model
- [x] Test script

### Step 2: 🚧 Provider Aggiuntivi
- [ ] OpenAI provider
- [ ] Ollama provider (locale)
- [ ] Test per tutti i provider

### Step 3: 🚧 UI Dialog
- [ ] Character AI Assistant Dialog
- [ ] Chat-like interface
- [ ] Apply suggestions to fields
- [ ] Conversation history viewer

### Step 4: 🚧 Integration
- [ ] Pulsante in CharacterDetailView
- [ ] Settings UI per API keys
- [ ] Error handling e feedback
- [ ] Usage tracking

### Step 5: 🚧 Advanced Features
- [ ] Template per diversi tipi di personaggi
- [ ] Export conversazione AI
- [ ] Rigenerazione selettiva
- [ ] Batch character generation

## Troubleshooting

### "anthropic package not installed"
```bash
pip install anthropic
```

### "No AI provider available"
- Verificare API key configurata
- Verificare connessione internet
- Controllare logs in `~/.thenovelist/logs/`

### "Rate limit exceeded"
- Anthropic ha rate limits per piano
- Attendere qualche secondo tra richieste
- Considerare upgrade piano API

## Supporto

Per problemi o domande:
1. Controllare logs in `~/.thenovelist/logs/app.log`
2. Verificare configurazione in `~/.thenovelist/ai_config.json`
3. Eseguire test script per diagnostica
