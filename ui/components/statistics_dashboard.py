"""
Statistics Dashboard Component
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QProgressBar, QScrollArea,
                               QSpinBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from models.writing_stats import ProjectStats


class StatisticsDashboard(QWidget):
    """
    Dashboard for displaying writing statistics

    Shows project stats, daily progress, session history, and goals
    """

    # Signals
    refresh_requested = Signal()
    daily_goal_changed = Signal(int)
    weekly_goal_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Header with title and refresh button
        header_layout = QHBoxLayout()
        title = QLabel("📊 Statistics Dashboard")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_button)

        main_layout.addLayout(header_layout)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        # Top row: Project Stats and Today's Stats
        top_row = QHBoxLayout()
        top_row.addWidget(self._create_project_stats_card())
        top_row.addWidget(self._create_today_stats_card())
        content_layout.addLayout(top_row)

        # Sessions list
        content_layout.addWidget(self._create_sessions_card())

        # Goals panel
        content_layout.addWidget(self._create_goals_card())

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_project_stats_card(self) -> QGroupBox:
        """Create project statistics card"""
        card = QGroupBox("📚 Project Statistics")
        card.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Total words
        self.total_words_label = QLabel("Total Words: 0")
        self.total_words_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3;")
        layout.addWidget(self.total_words_label)

        # Characters
        self.total_chars_label = QLabel("Characters: 0")
        layout.addWidget(self.total_chars_label)

        # Paragraphs
        self.total_paragraphs_label = QLabel("Paragraphs: 0")
        layout.addWidget(self.total_paragraphs_label)

        # Sentences
        self.total_sentences_label = QLabel("Sentences: 0")
        layout.addWidget(self.total_sentences_label)

        layout.addSpacing(10)

        # Sessions count
        self.total_sessions_label = QLabel("Writing Sessions: 0")
        self.total_sessions_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.total_sessions_label)

        # Total time
        self.total_time_label = QLabel("Total Time: 0h 0m")
        layout.addWidget(self.total_time_label)

        card.setLayout(layout)
        return card

    def _create_today_stats_card(self) -> QGroupBox:
        """Create today's statistics card"""
        card = QGroupBox("📝 Today's Writing")
        card.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Today's words
        self.today_words_label = QLabel("Words Written: 0")
        self.today_words_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(self.today_words_label)

        # Today's time
        self.today_time_label = QLabel("Time Spent: 0 min")
        layout.addWidget(self.today_time_label)

        layout.addSpacing(10)

        # Daily goal label
        self.daily_goal_label = QLabel("Daily Goal: 1000 words")
        self.daily_goal_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.daily_goal_label)

        # Progress bar
        self.daily_progress_bar = QProgressBar()
        self.daily_progress_bar.setMinimum(0)
        self.daily_progress_bar.setMaximum(100)
        self.daily_progress_bar.setValue(0)
        self.daily_progress_bar.setTextVisible(True)
        self.daily_progress_bar.setFormat("%p%")
        self.daily_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.daily_progress_bar)

        self.daily_progress_label = QLabel("0 / 1000 words")
        self.daily_progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.daily_progress_label.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(self.daily_progress_label)

        card.setLayout(layout)
        return card

    def _create_sessions_card(self) -> QGroupBox:
        """Create sessions history card"""
        card = QGroupBox("📅 Writing Sessions (Last 7 Days)")
        card.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Container for session bars
        self.sessions_container = QWidget()
        self.sessions_layout = QVBoxLayout(self.sessions_container)
        self.sessions_layout.setSpacing(8)
        self.sessions_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.sessions_container)

        # Week summary
        self.week_summary_label = QLabel("This Week: 0 words | 0h 0m | Avg: 0 words/day")
        self.week_summary_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #555; margin-top: 10px;")
        self.week_summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.week_summary_label)

        card.setLayout(layout)
        return card

    def _create_goals_card(self) -> QGroupBox:
        """Create goals setting card"""
        card = QGroupBox("🎯 Goals & Targets")
        card.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Daily goal setting
        daily_layout = QHBoxLayout()
        daily_layout.addWidget(QLabel("Daily Goal:"))
        self.daily_goal_spin = QSpinBox()
        self.daily_goal_spin.setMinimum(0)
        self.daily_goal_spin.setMaximum(10000)
        self.daily_goal_spin.setValue(1000)
        self.daily_goal_spin.setSuffix(" words")
        daily_layout.addWidget(self.daily_goal_spin)
        daily_set_btn = QPushButton("Set")
        daily_set_btn.clicked.connect(lambda: self.daily_goal_changed.emit(self.daily_goal_spin.value()))
        daily_layout.addWidget(daily_set_btn)
        daily_layout.addStretch()
        layout.addLayout(daily_layout)

        # Weekly goal setting
        weekly_layout = QHBoxLayout()
        weekly_layout.addWidget(QLabel("Weekly Goal:"))
        self.weekly_goal_spin = QSpinBox()
        self.weekly_goal_spin.setMinimum(0)
        self.weekly_goal_spin.setMaximum(50000)
        self.weekly_goal_spin.setValue(7000)
        self.weekly_goal_spin.setSuffix(" words")
        weekly_layout.addWidget(self.weekly_goal_spin)
        weekly_set_btn = QPushButton("Set")
        weekly_set_btn.clicked.connect(lambda: self.weekly_goal_changed.emit(self.weekly_goal_spin.value()))
        weekly_layout.addWidget(weekly_set_btn)
        weekly_layout.addStretch()
        layout.addLayout(weekly_layout)

        # Weekly progress
        self.weekly_goal_label = QLabel("This Week: 0 / 7000 words (0%)")
        self.weekly_goal_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.weekly_goal_label)

        self.weekly_progress_bar = QProgressBar()
        self.weekly_progress_bar.setMinimum(0)
        self.weekly_progress_bar.setMaximum(100)
        self.weekly_progress_bar.setValue(0)
        self.weekly_progress_bar.setTextVisible(True)
        self.weekly_progress_bar.setFormat("%p%")
        self.weekly_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #FF9800;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.weekly_progress_bar)

        card.setLayout(layout)
        return card

    def update_statistics(self, stats: ProjectStats):
        """
        Update dashboard with new statistics

        Args:
            stats: ProjectStats object with current data
        """
        self.stats = stats

        # Update project stats
        self.total_words_label.setText(f"Total Words: {stats.total_words:,}")
        self.total_chars_label.setText(f"Characters: {stats.total_characters:,}")
        self.total_paragraphs_label.setText(f"Paragraphs: {stats.total_paragraphs}")
        self.total_sentences_label.setText(f"Sentences: {stats.total_sentences}")
        self.total_sessions_label.setText(f"Writing Sessions: {stats.total_sessions}")

        hours = stats.total_time_minutes // 60
        minutes = stats.total_time_minutes % 60
        self.total_time_label.setText(f"Total Time: {hours}h {minutes}m")

        # Update today's stats
        today_words = stats.get_today_words()
        today_time = stats.get_today_time()
        self.today_words_label.setText(f"Words Written: {today_words:,}")
        self.today_time_label.setText(f"Time Spent: {today_time} min")

        # Update daily progress
        self.daily_goal_label.setText(f"Daily Goal: {stats.daily_goal:,} words")
        daily_progress = stats.get_daily_progress_percent()
        self.daily_progress_bar.setValue(daily_progress)
        self.daily_progress_label.setText(f"{today_words:,} / {stats.daily_goal:,} words")

        # Update goal spinboxes
        self.daily_goal_spin.setValue(stats.daily_goal)
        self.weekly_goal_spin.setValue(stats.weekly_goal)

        # Update weekly progress
        week_words = stats.get_week_words()
        weekly_progress = stats.get_weekly_progress_percent()
        self.weekly_goal_label.setText(f"This Week: {week_words:,} / {stats.weekly_goal:,} words ({weekly_progress}%)")
        self.weekly_progress_bar.setValue(weekly_progress)

        # Update sessions list
        self._update_sessions_list(stats)

        # Update week summary
        week_time = stats.get_week_time()
        week_hours = week_time // 60
        week_minutes = week_time % 60
        avg_words_per_day = week_words // 7 if week_words > 0 else 0
        self.week_summary_label.setText(
            f"This Week: {week_words:,} words | {week_hours}h {week_minutes}m | Avg: {avg_words_per_day:,} words/day"
        )

    def _update_sessions_list(self, stats: ProjectStats):
        """Update the sessions list for last 7 days"""
        # Clear existing widgets
        while self.sessions_layout.count():
            child = self.sessions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get last 7 days data
        from datetime import datetime, timedelta
        today = datetime.now().date()

        for i in range(6, -1, -1):  # 6 days ago to today
            target_date = today - timedelta(days=i)
            date_str = target_date.strftime('%Y-%m-%d')
            display_date = target_date.strftime('%b %d')

            # Get sessions for this day
            day_sessions = [s for s in stats.sessions if s.session_date == date_str]
            day_words = sum(s.words_written for s in day_sessions)
            day_time = sum(s.time_spent_minutes for s in day_sessions)

            # Create session bar
            session_widget = self._create_session_bar(display_date, day_words, day_time, stats.daily_goal)
            self.sessions_layout.addWidget(session_widget)

    def _create_session_bar(self, date: str, words: int, time: int, goal: int) -> QWidget:
        """Create a single session bar"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Date label
        date_label = QLabel(date)
        date_label.setFixedWidth(60)
        date_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(date_label)

        # Progress bar
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(goal if goal > 0 else 1000)
        progress.setValue(min(words, goal if goal > 0 else 1000))
        progress.setTextVisible(False)
        progress.setFixedHeight(20)

        # Color based on progress
        if words == 0:
            color = "#E0E0E0"
        elif words >= goal:
            color = "#4CAF50"
        else:
            color = "#2196F3"

        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f5f5f5;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)
        layout.addWidget(progress, 1)

        # Stats label
        stats_label = QLabel(f"{words:,} words ({time} min)")
        stats_label.setFixedWidth(150)
        stats_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(stats_label)

        return widget

    def clear_statistics(self):
        """Clear all statistics display"""
        self.stats = None
        self.total_words_label.setText("Total Words: 0")
        self.total_chars_label.setText("Characters: 0")
        self.total_paragraphs_label.setText("Paragraphs: 0")
        self.total_sentences_label.setText("Sentences: 0")
        self.total_sessions_label.setText("Writing Sessions: 0")
        self.total_time_label.setText("Total Time: 0h 0m")
        self.today_words_label.setText("Words Written: 0")
        self.today_time_label.setText("Time Spent: 0 min")
        self.daily_progress_bar.setValue(0)
        self.daily_progress_label.setText("0 / 1000 words")
        self.weekly_progress_bar.setValue(0)
        self.week_summary_label.setText("This Week: 0 words | 0h 0m | Avg: 0 words/day")

        # Clear sessions list
        while self.sessions_layout.count():
            child = self.sessions_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
