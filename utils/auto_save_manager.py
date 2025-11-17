"""
Auto-Save Manager - Gestisce il salvataggio automatico con debouncing e queue
"""
from PySide6.QtCore import QObject, QTimer, Signal
from queue import Queue, Empty
from typing import Callable, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AutoSaveManager(QObject):
    """
    Gestisce il salvataggio automatico di dati con:
    - Debouncing: Ritarda il salvataggio fino a che l'utente smette di digitare
    - Queue: Gestisce salvataggi multipli in sequenza senza sovrascritture
    - Status tracking: Monitora lo stato (Editing/Saving/Saved/Error)
    """

    # Signals
    save_started = Signal()  # Emesso quando inizia un salvataggio
    save_completed = Signal()  # Emesso quando il salvataggio completa
    save_error = Signal(str)  # Emesso in caso di errore (con messaggio)
    status_changed = Signal(str)  # Editing/Saving/Saved/Error

    def __init__(self, save_callback: Callable[[Dict[str, Any]], bool], debounce_ms: int = 1000):
        """
        Inizializza l'AutoSaveManager

        Args:
            save_callback: Funzione da chiamare per salvare i dati.
                          Deve accettare un dict e ritornare True se successo
            debounce_ms: Millisecondi di debounce (default 1000 = 1 secondo)
        """
        super().__init__()

        self._save_callback = save_callback
        self._debounce_ms = debounce_ms

        # Debounce timer
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._process_save)

        # Queue per salvataggi multipli
        self._save_queue = Queue()
        self._is_saving = False

        # Stato corrente
        self._current_status = "idle"  # idle/editing/saving/saved/error
        self._last_save_time = None
        self._pending_data = None

    def schedule_save(self, data: Dict[str, Any]):
        """
        Programma un salvataggio con debouncing

        Args:
            data: Dati da salvare
        """
        # Memorizza i dati più recenti
        self._pending_data = data

        # Mostra stato "Editing..."
        self._update_status("editing")

        # Resetta il timer di debounce
        self._debounce_timer.stop()
        self._debounce_timer.start(self._debounce_ms)

        logger.debug(f"Save scheduled with {self._debounce_ms}ms debounce")

    def save_immediately(self, data: Dict[str, Any]):
        """
        Salva immediatamente senza debounce
        Usato per dropdown/checkbox che devono salvare subito

        Args:
            data: Dati da salvare
        """
        self._pending_data = data
        self._debounce_timer.stop()
        self._process_save()

    def _process_save(self):
        """Processa il salvataggio (chiamato dopo il debounce)"""
        if not self._pending_data:
            return

        # Se già sta salvando, accoda
        if self._is_saving:
            logger.debug("Save in progress, queueing new save")
            self._save_queue.put(self._pending_data)
            return

        # Altrimenti salva subito
        self._perform_save(self._pending_data)

    def _perform_save(self, data: Dict[str, Any]):
        """
        Esegue il salvataggio effettivo

        Args:
            data: Dati da salvare
        """
        self._is_saving = True
        self._update_status("saving")
        self.save_started.emit()

        try:
            # Chiama la callback di salvataggio
            success = self._save_callback(data)

            if success:
                self._last_save_time = datetime.now()
                self._update_status("saved")
                self.save_completed.emit()
                logger.debug(f"Save completed successfully at {self._last_save_time}")
            else:
                self._update_status("error")
                self.save_error.emit("Save operation failed")
                logger.error("Save callback returned False")

        except Exception as e:
            self._update_status("error")
            error_msg = f"Save error: {str(e)}"
            self.save_error.emit(error_msg)
            logger.exception("Exception during save")

        finally:
            self._is_saving = False
            self._pending_data = None

            # Processa il prossimo elemento nella queue
            self._process_queue()

    def _process_queue(self):
        """Processa il prossimo salvataggio in queue"""
        try:
            # Prendi il prossimo item dalla queue (non-blocking)
            next_data = self._save_queue.get_nowait()
            logger.debug("Processing queued save")
            self._perform_save(next_data)
        except Empty:
            # Queue vuota, niente da fare
            pass

    def _update_status(self, status: str):
        """
        Aggiorna lo stato corrente

        Args:
            status: Nuovo stato (editing/saving/saved/error)
        """
        if status != self._current_status:
            self._current_status = status
            self.status_changed.emit(status)

    def get_status(self) -> str:
        """
        Ottieni lo stato corrente

        Returns:
            str: Stato corrente
        """
        return self._current_status

    def get_last_save_time(self) -> datetime:
        """
        Ottieni il timestamp dell'ultimo salvataggio

        Returns:
            datetime: Timestamp ultimo salvataggio, None se mai salvato
        """
        return self._last_save_time

    def has_unsaved_changes(self) -> bool:
        """
        Verifica se ci sono modifiche non salvate

        Returns:
            bool: True se ci sono modifiche pending o in queue
        """
        return (self._pending_data is not None or
                not self._save_queue.empty() or
                self._current_status == "editing")

    def force_save_all(self):
        """
        Forza il salvataggio di tutte le modifiche pending
        Utile prima di chiudere l'applicazione o cambiare sezione
        """
        # Cancella il debounce timer e salva subito
        if self._debounce_timer.isActive():
            self._debounce_timer.stop()
            if self._pending_data:
                self._process_save()

        # Aspetta che la queue si svuoti
        while not self._save_queue.empty() and not self._is_saving:
            self._process_queue()
