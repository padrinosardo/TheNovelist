"""
Stili CSS per l'applicazione
"""


class Colori:
    """Palette di colori dell'applicazione"""

    # Colori principali
    PRIMARIO = "#2196F3"
    SECONDARIO = "#4CAF50"
    ACCENTO = "#FF9800"
    PERICOLO = "#f44336"
    VIOLA = "#9C27B0"
    GRIGIO = "#607D8B"

    # Colori di sfondo
    SFONDO = "#f0f0f0"
    SFONDO_SCURO = "#e0e0e0"

    # Colori testo
    TESTO = "#333333"
    TESTO_CHIARO = "#666666"


class Stili:
    """Stili CSS per i widget"""

    @staticmethod
    def bottone(colore_base):
        """
        Genera stile per bottoni

        Args:
            colore_base: Colore base del bottone (hex)

        Returns:
            str: Stile CSS
        """
        return f"""
            QPushButton {{
                background-color: {colore_base};
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {colore_base}dd;
            }}
            QPushButton:pressed {{
                background-color: {colore_base}aa;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """

    @staticmethod
    def header():
        """Stile per l'header dell'applicazione"""
        return f"background-color: {Colori.SFONDO}; padding: 10px;"

    @staticmethod
    def gruppo():
        """Stile per QGroupBox"""
        return "QGroupBox { font-weight: bold; font-size: 17px; }"

    @staticmethod
    def progress_bar():
        """Stile per la barra di progresso"""
        return """
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """


# Stili preconfigurati per bottoni comuni
STILE_BTN_GRAMMATICA = Stili.bottone(Colori.PRIMARIO)
STILE_BTN_RIPETIZIONI = Stili.bottone(Colori.ACCENTO)
STILE_BTN_STILE = Stili.bottone(Colori.SECONDARIO)
STILE_BTN_PULISCI = Stili.bottone(Colori.PERICOLO)
STILE_BTN_PERSONAGGI = Stili.bottone(Colori.VIOLA)