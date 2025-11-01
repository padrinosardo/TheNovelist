"""
AI Command Parser - Parsing e gestione comandi AI custom

Riconosce pattern #comando, sostituisce variabili nei template, e genera testo help.
"""
import re
from typing import Optional, Dict, List


class AICommandParser:
    """
    Parser per comandi AI custom.

    Gestisce:
    - Riconoscimento pattern #comando
    - Filtro comandi per context type
    - Sostituzione variabili nei template
    - Generazione testo help
    """

    # Pattern per riconoscere comandi: #comando o #comando args
    COMMAND_PATTERN = re.compile(r'^#(\w+)(?:\s+(.*))?$')

    # Variabili disponibili per ogni context type
    CONTEXT_VARIABLES = {
        'Scene': [
            ('scene_content', 'Contenuto completo della scena'),
            ('scene_title', 'Titolo della scena'),
            ('chapter_title', 'Titolo del capitolo'),
            ('word_count', 'Numero di parole nella scena'),
            ('selected_text', 'Testo selezionato nell\'editor')
        ],
        'Character': [
            ('character_name', 'Nome del personaggio'),
            ('character_description', 'Descrizione del personaggio'),
            ('selected_text', 'Testo selezionato')
        ],
        'Location': [
            ('location_name', 'Nome del luogo'),
            ('location_description', 'Descrizione del luogo'),
            ('location_type', 'Tipo di luogo'),
            ('selected_text', 'Testo selezionato')
        ],
        'Note': [
            ('note_title', 'Titolo della nota'),
            ('note_content', 'Contenuto della nota'),
            ('note_tags', 'Tags della nota (separati da virgola)'),
            ('selected_text', 'Testo selezionato')
        ]
    }

    def parse_command(self, text: str) -> Optional[Dict]:
        """
        Riconosce pattern #comando e estrae nome comando e argomenti

        Args:
            text: Testo input (es: "#sinossi" o "#espandi questo testo")

        Returns:
            Dict con 'command' e 'args', oppure None se non è un comando
        """
        match = self.COMMAND_PATTERN.match(text.strip())
        if not match:
            return None

        command_name = match.group(1).lower()
        args = match.group(2) or ""

        return {
            'command': command_name,
            'args': args.strip()
        }

    def get_available_commands(self, context_type: str, project_commands: List[Dict]) -> List[Dict]:
        """
        Filtra comandi disponibili per un context type specifico

        Args:
            context_type: Tipo di contesto ('Scene', 'Character', 'Location', 'Note')
            project_commands: Lista di comandi del progetto

        Returns:
            Lista di comandi filtrati per il context_type e abilitati
        """
        available = []

        for cmd in project_commands:
            # Salta comandi disabilitati
            if not cmd.get('enabled', True):
                continue

            # Filtra per context_type
            context_types = cmd.get('context_types', [])
            if context_type in context_types:
                available.append(cmd)

        return available

    def find_command(self, command_name: str, commands: List[Dict]) -> Optional[Dict]:
        """
        Cerca un comando per nome nella lista

        Args:
            command_name: Nome del comando da cercare
            commands: Lista di comandi dove cercare

        Returns:
            Comando trovato o None
        """
        for cmd in commands:
            if cmd.get('name', '').lower() == command_name.lower():
                return cmd
        return None

    def replace_variables(self, template: str, variables: Dict[str, str]) -> str:
        """
        Sostituisce variabili {variable} nel template con valori reali

        Args:
            template: Template con variabili (es: "Testo: {scene_content}")
            variables: Dizionario con valori delle variabili

        Returns:
            Template con variabili sostituite
        """
        result = template

        # Sostituisci ogni variabile trovata
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            result = result.replace(placeholder, str(var_value))

        return result

    def get_help_text(self, commands: List[Dict], context_type: str) -> str:
        """
        Genera testo help con lista comandi disponibili

        Args:
            commands: Lista di comandi disponibili
            context_type: Tipo di contesto corrente

        Returns:
            Testo formattato con lista comandi e variabili disponibili
        """
        if not commands:
            return "Nessun comando AI disponibile per questo contesto.\n\n" \
                   "Puoi definire comandi personalizzati in **Project Info > AI Commands**."

        # Header
        help_text = f"# Comandi AI Disponibili ({context_type})\n\n"
        help_text += "Digita un comando preceduto da # per usarlo. Esempi:\n\n"

        # Lista comandi
        for cmd in commands:
            help_text += f"**#{cmd['name']}**\n"
            help_text += f"  {cmd['description']}\n\n"

        # Variabili disponibili
        help_text += "\n## Variabili Disponibili\n\n"
        help_text += "I comandi possono usare queste variabili:\n\n"

        variables = self.CONTEXT_VARIABLES.get(context_type, [])
        for var_name, var_desc in variables:
            help_text += f"- `{{{var_name}}}` - {var_desc}\n"

        help_text += "\n---\n"
        help_text += "*Puoi gestire i comandi in **Project Info > AI Commands***"

        return help_text

    def get_variables_for_context(self, context_type: str) -> List[tuple]:
        """
        Ottiene la lista di variabili disponibili per un context type

        Args:
            context_type: Tipo di contesto

        Returns:
            Lista di tuple (nome_variabile, descrizione)
        """
        return self.CONTEXT_VARIABLES.get(context_type, [])

    def validate_template(self, template: str, context_type: str) -> tuple[bool, str]:
        """
        Valida un template verificando che usi solo variabili valide

        Args:
            template: Template da validare
            context_type: Tipo di contesto

        Returns:
            Tuple (is_valid, error_message)
        """
        # Estrai tutte le variabili usate nel template
        pattern = re.compile(r'\{(\w+)\}')
        used_variables = set(pattern.findall(template))

        # Ottieni variabili valide per questo context
        valid_variables = {var[0] for var in self.get_variables_for_context(context_type)}

        # Verifica variabili invalide
        invalid_variables = used_variables - valid_variables

        if invalid_variables:
            invalid_list = ', '.join(f"{{{var}}}" for var in invalid_variables)
            return False, f"Variabili non valide per {context_type}: {invalid_list}"

        return True, ""
