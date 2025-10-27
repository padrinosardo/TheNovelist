"""
Statistics Manager - Manages writing statistics and sessions
"""
import json
import os
from datetime import datetime
from typing import Optional
from models.writing_stats import WritingSession, ProjectStats


class StatisticsManager:
    """
    Manages writing statistics for a project

    Tracks writing sessions, calculates statistics,
    and persists data to statistics.json
    """

    def __init__(self):
        self.stats = ProjectStats()
        self.current_session_active = False
        self.session_start_time: Optional[datetime] = None
        self.session_start_word_count: int = 0
        self.session_start_char_count: int = 0

    def start_session(self, current_word_count: int, current_char_count: int):
        """
        Start a new writing session

        Args:
            current_word_count: Current word count in manuscript
            current_char_count: Current character count
        """
        if self.current_session_active:
            return  # Session already active

        self.current_session_active = True
        self.session_start_time = datetime.now()
        self.session_start_word_count = current_word_count
        self.session_start_char_count = current_char_count

    def end_session(self, current_word_count: int, current_char_count: int):
        """
        End the current writing session and save statistics

        Args:
            current_word_count: Current word count in manuscript
            current_char_count: Current character count
        """
        if not self.current_session_active or not self.session_start_time:
            return

        # Calculate session statistics
        end_time = datetime.now()
        duration = end_time - self.session_start_time
        minutes = int(duration.total_seconds() / 60)

        # Only save if session lasted at least 1 minute
        if minutes < 1:
            self.current_session_active = False
            return

        words_written = max(0, current_word_count - self.session_start_word_count)
        chars_written = max(0, current_char_count - self.session_start_char_count)

        # Create session record
        session = WritingSession(
            session_date=self.session_start_time.strftime('%Y-%m-%d'),
            words_written=words_written,
            characters_written=chars_written,
            time_spent_minutes=minutes,
            start_time=self.session_start_time.strftime('%H:%M:%S'),
            end_time=end_time.strftime('%H:%M:%S')
        )

        # Add to stats
        self.stats.add_session(session)

        # Reset session
        self.current_session_active = False
        self.session_start_time = None

    def update_manuscript_stats(self, text: str):
        """
        Update manuscript statistics (words, characters, paragraphs, sentences)

        Args:
            text: Current manuscript text
        """
        if not text:
            self.stats.total_words = 0
            self.stats.total_characters = 0
            self.stats.total_paragraphs = 0
            self.stats.total_sentences = 0
            return

        # Count words
        words = text.split()
        self.stats.total_words = len(words)

        # Count characters (excluding whitespace)
        self.stats.total_characters = len(text.replace(' ', '').replace('\n', ''))

        # Count paragraphs (separated by double newlines or single newline)
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        self.stats.total_paragraphs = len(paragraphs)

        # Count sentences (rough estimate by counting . ! ?)
        sentence_endings = text.count('.') + text.count('!') + text.count('?')
        self.stats.total_sentences = max(1, sentence_endings)

    def set_daily_goal(self, words: int):
        """
        Set daily writing goal

        Args:
            words: Target words per day
        """
        self.stats.daily_goal = max(0, words)

    def set_weekly_goal(self, words: int):
        """
        Set weekly writing goal

        Args:
            words: Target words per week
        """
        self.stats.weekly_goal = max(0, words)

    def get_stats(self) -> ProjectStats:
        """
        Get current project statistics

        Returns:
            ProjectStats: Current statistics
        """
        return self.stats

    def get_last_7_days_data(self) -> list:
        """
        Get writing data for last 7 days (for visualization)

        Returns:
            List of dicts with date, words, and time for each day
        """
        today = datetime.now().date()
        data = []

        for i in range(6, -1, -1):  # 6 days ago to today
            target_date = today - __import__('datetime').timedelta(days=i)
            date_str = target_date.strftime('%Y-%m-%d')

            # Get sessions for this day
            day_sessions = [s for s in self.stats.sessions if s.session_date == date_str]
            day_words = sum(s.words_written for s in day_sessions)
            day_time = sum(s.time_spent_minutes for s in day_sessions)

            data.append({
                'date': target_date.strftime('%b %d'),
                'date_full': date_str,
                'words': day_words,
                'time': day_time
            })

        return data

    def save_statistics(self, project_dir: str):
        """
        Save statistics to statistics.json in project directory

        Args:
            project_dir: Path to project directory (temp dir)
        """
        stats_file = os.path.join(project_dir, 'statistics.json')

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats.to_dict(), f, indent=2, ensure_ascii=False)

    def load_statistics(self, project_dir: str):
        """
        Load statistics from statistics.json in project directory

        Args:
            project_dir: Path to project directory (temp dir)
        """
        stats_file = os.path.join(project_dir, 'statistics.json')

        if not os.path.exists(stats_file):
            # No statistics file yet, use defaults
            self.stats = ProjectStats()
            return

        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.stats = ProjectStats.from_dict(data)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, start fresh
            self.stats = ProjectStats()

    def reset_session(self):
        """Reset current session without saving"""
        self.current_session_active = False
        self.session_start_time = None
        self.session_start_word_count = 0
        self.session_start_char_count = 0

    def is_session_active(self) -> bool:
        """Check if a writing session is currently active"""
        return self.current_session_active
