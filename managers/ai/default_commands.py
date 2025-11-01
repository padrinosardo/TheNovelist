"""
Default AI Commands - Template comandi AI predefiniti

Questi comandi possono essere importati quando si crea un nuovo progetto.
Ogni utente può poi personalizzarli o aggiungerne di nuovi.
"""

# Comandi disponibili per le Scene
SCENE_COMMANDS = [
    {
        'name': 'sinossi',
        'description': 'Genera una sinossi concisa della scena',
        'prompt_template': '''Genera una sinossi concisa (massimo 100 parole) di questa scena:

**Capitolo**: {chapter_title}
**Scena**: {scene_title}
**Lunghezza**: {word_count} parole

**Contenuto**:
{scene_content}

Riassumi gli eventi principali, i personaggi coinvolti e il loro sviluppo narrativo.''',
        'enabled': True,
        'context_types': ['Scene']
    },
    {
        'name': 'espandi',
        'description': 'Espandi il testo con più dettagli narrativi',
        'prompt_template': '''Espandi questo testo aggiungendo più dettagli descrittivi, emozioni e atmosfera, mantenendo lo stesso stile narrativo:

{selected_text}

Se non c'è testo selezionato, espandi l'intera scena:
{scene_content}

Mantieni coerenza con il tono e lo stile del progetto.''',
        'enabled': True,
        'context_types': ['Scene', 'Character', 'Location', 'Note']
    },
    {
        'name': 'dialoghi',
        'description': 'Migliora i dialoghi rendendoli più naturali e incisivi',
        'prompt_template': '''Analizza e migliora i dialoghi in questa scena, rendendoli più naturali, caratterizzati e incisivi:

{scene_content}

Suggerimenti:
- Rendi il dialogo più naturale e realistico
- Caratterizza meglio le voci dei personaggi
- Elimina ridondanze o battute superflue
- Aumenta il sottotesto quando appropriato''',
        'enabled': True,
        'context_types': ['Scene']
    },
    {
        'name': 'tensione',
        'description': 'Aumenta la tensione narrativa della scena',
        'prompt_template': '''Analizza questa scena e suggerisci come aumentare la tensione narrativa:

**Scena**: {scene_title}
**Contenuto**:
{scene_content}

Fornisci suggerimenti specifici per:
- Aumentare la posta in gioco
- Creare più conflitto
- Usare tecniche di suspense
- Migliorare il ritmo''',
        'enabled': True,
        'context_types': ['Scene']
    },
    {
        'name': 'show',
        'description': 'Converti "telling" in "showing" (mostra, non dire)',
        'prompt_template': '''Identifica le parti di questa scena dove si usa "telling" e trasformale in "showing":

{scene_content}

Trasforma le descrizioni dirette in scene vivide che mostrano attraverso:
- Azioni concrete
- Dettagli sensoriali
- Dialoghi
- Linguaggio del corpo''',
        'enabled': True,
        'context_types': ['Scene']
    },
    {
        'name': 'ritmo',
        'description': 'Analizza e migliora il ritmo narrativo',
        'prompt_template': '''Analizza il ritmo di questa scena e suggerisci miglioramenti:

{scene_content}

Valuta:
- Equilibrio tra azione e riflessione
- Lunghezza delle frasi e paragrafi
- Alternanza tra scene lente e veloci
- Punti dove accelerare o rallentare''',
        'enabled': True,
        'context_types': ['Scene']
    }
]

# Comandi disponibili per i Personaggi
CHARACTER_COMMANDS = [
    {
        'name': 'approfondisci',
        'description': 'Approfondisci la caratterizzazione del personaggio',
        'prompt_template': '''Analizza questo personaggio e suggerisci approfondimenti:

**Nome**: {character_name}
**Descrizione attuale**:
{character_description}

Suggerisci:
- Dettagli psicologici più profondi
- Contraddizioni interessanti
- Paure e desideri nascosti
- Archi di trasformazione possibili''',
        'enabled': True,
        'context_types': ['Character']
    },
    {
        'name': 'conflitti',
        'description': 'Genera conflitti interni ed esterni per il personaggio',
        'prompt_template': '''Basandoti su questo personaggio, genera possibili conflitti narrativi:

**Nome**: {character_name}
**Descrizione**:
{character_description}

Suggerisci:
- 3 conflitti interni (psicologici, morali)
- 3 conflitti esterni (con altri personaggi, con l'ambiente)
- Come questi conflitti possono evolvere nella storia''',
        'enabled': True,
        'context_types': ['Character']
    }
]

# Comandi disponibili per i Luoghi
LOCATION_COMMANDS = [
    {
        'name': 'atmosfera',
        'description': 'Arricchisci la descrizione con dettagli atmosferici',
        'prompt_template': '''Arricchisci la descrizione di questo luogo con dettagli atmosferici e sensoriali:

**Luogo**: {location_name}
**Tipo**: {location_type}
**Descrizione attuale**:
{location_description}

Aggiungi:
- Dettagli visivi specifici
- Suoni, odori, temperature
- Atmosfera emotiva
- Elementi che lo rendono unico e memorabile''',
        'enabled': True,
        'context_types': ['Location']
    }
]

# Comandi disponibili per le Note
NOTE_COMMANDS = [
    {
        'name': 'sviluppa',
        'description': 'Sviluppa l\'idea in una nota più completa',
        'prompt_template': '''Sviluppa questa nota in modo più dettagliato e strutturato:

**Titolo**: {note_title}
**Contenuto**:
{note_content}
**Tags**: {note_tags}

Espandi l'idea con:
- Maggiori dettagli e implicazioni
- Possibili sviluppi
- Collegamenti con altri elementi della storia''',
        'enabled': True,
        'context_types': ['Note']
    }
]

# Comandi universali (disponibili ovunque)
UNIVERSAL_COMMANDS = [
    {
        'name': 'migliora',
        'description': 'Migliora il testo generale',
        'prompt_template': '''Migliora questo testo a livello stilistico:

{selected_text}

Se non c'è selezione, migliora tutto il contenuto disponibile.

Migliora:
- Chiarezza e leggibilità
- Varietà lessicale
- Efficacia narrativa
- Eliminazione di ridondanze''',
        'enabled': True,
        'context_types': ['Scene', 'Character', 'Location', 'Note']
    }
]


def get_default_commands_for_context(context_type: str) -> list:
    """
    Ottiene i comandi default appropriati per un tipo di contesto

    Args:
        context_type: Tipo di contesto ('Scene', 'Character', 'Location', 'Note')

    Returns:
        list: Lista di comandi default filtrati per quel contesto
    """
    all_commands = (
        SCENE_COMMANDS +
        CHARACTER_COMMANDS +
        LOCATION_COMMANDS +
        NOTE_COMMANDS +
        UNIVERSAL_COMMANDS
    )

    # Filtra per context_type
    return [cmd for cmd in all_commands if context_type in cmd['context_types']]


def get_all_default_commands() -> list:
    """
    Ottiene tutti i comandi default

    Returns:
        list: Lista completa di tutti i comandi default
    """
    return (
        SCENE_COMMANDS +
        CHARACTER_COMMANDS +
        LOCATION_COMMANDS +
        NOTE_COMMANDS +
        UNIVERSAL_COMMANDS
    )
