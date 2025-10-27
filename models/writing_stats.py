"""
Writing Statistics data models
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class WritingSession:
    """
    Represents a single writing session

    Attributes:
        session_date: Date of the session (YYYY-MM-DD format)
        words_written: Number of words written in this session
        characters_written: Number of characters written
        time_spent_minutes: Time spent writing in minutes
        start_time: Session start time (HH:MM:SS format)
        end_time: Session end time (HH:MM:SS format)
    """
    session_date: str
    words_written: int
    characters_written: int
    time_spent_minutes: int
    start_time: str
    end_time: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_date': self.session_date,
            'words_written': self.words_written,
            'characters_written': self.characters_written,
            'time_spent_minutes': self.time_spent_minutes,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WritingSession':
        """Create WritingSession from dictionary"""
        return cls(
            session_date=data.get('session_date', ''),
            words_written=data.get('words_written', 0),
            characters_written=data.get('characters_written', 0),
            time_spent_minutes=data.get('time_spent_minutes', 0),
            start_time=data.get('start_time', ''),
            end_time=data.get('end_time', '')
        )


@dataclass
class ProjectStats:
    """
    Aggregated statistics for a project

    Attributes:
        total_words: Total word count in manuscript
        total_characters: Total character count
        total_paragraphs: Number of paragraphs
        total_sentences: Number of sentences
        total_sessions: Number of writing sessions
        total_time_minutes: Total time spent writing
        daily_goal: Target words per day
        weekly_goal: Target words per week
        sessions: List of all writing sessions
    """
    total_words: int = 0
    total_characters: int = 0
    total_paragraphs: int = 0
    total_sentences: int = 0
    total_sessions: int = 0
    total_time_minutes: int = 0
    daily_goal: int = 1000
    weekly_goal: int = 7000
    sessions: List[WritingSession] = field(default_factory=list)

    def get_avg_words_per_session(self) -> float:
        """Calculate average words per session"""
        if self.total_sessions == 0:
            return 0.0
        return round(self.total_words / self.total_sessions, 1)

    def get_avg_time_per_session(self) -> int:
        """Calculate average time per session in minutes"""
        if self.total_sessions == 0:
            return 0
        return round(self.total_time_minutes / self.total_sessions)

    def get_today_sessions(self) -> List[WritingSession]:
        """Get sessions from today"""
        today = datetime.now().strftime('%Y-%m-%d')
        return [s for s in self.sessions if s.session_date == today]

    def get_week_sessions(self) -> List[WritingSession]:
        """Get sessions from last 7 days"""
        today = datetime.now().date()
        week_sessions = []

        for session in self.sessions:
            try:
                session_date = datetime.strptime(session.session_date, '%Y-%m-%d').date()
                days_diff = (today - session_date).days
                if 0 <= days_diff <= 6:
                    week_sessions.append(session)
            except ValueError:
                continue

        return week_sessions

    def get_today_words(self) -> int:
        """Get total words written today"""
        return sum(s.words_written for s in self.get_today_sessions())

    def get_today_time(self) -> int:
        """Get total time spent today in minutes"""
        return sum(s.time_spent_minutes for s in self.get_today_sessions())

    def get_week_words(self) -> int:
        """Get total words written this week"""
        return sum(s.words_written for s in self.get_week_sessions())

    def get_week_time(self) -> int:
        """Get total time spent this week in minutes"""
        return sum(s.time_spent_minutes for s in self.get_week_sessions())

    def get_daily_progress_percent(self) -> int:
        """Get today's progress towards daily goal (0-100)"""
        if self.daily_goal == 0:
            return 0
        progress = (self.get_today_words() / self.daily_goal) * 100
        return min(100, int(progress))

    def get_weekly_progress_percent(self) -> int:
        """Get this week's progress towards weekly goal (0-100)"""
        if self.weekly_goal == 0:
            return 0
        progress = (self.get_week_words() / self.weekly_goal) * 100
        return min(100, int(progress))

    def add_session(self, session: WritingSession):
        """Add a new writing session"""
        self.sessions.append(session)
        self.total_sessions += 1
        self.total_time_minutes += session.time_spent_minutes

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_words': self.total_words,
            'total_characters': self.total_characters,
            'total_paragraphs': self.total_paragraphs,
            'total_sentences': self.total_sentences,
            'total_sessions': self.total_sessions,
            'total_time_minutes': self.total_time_minutes,
            'daily_goal': self.daily_goal,
            'weekly_goal': self.weekly_goal,
            'sessions': [s.to_dict() for s in self.sessions]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProjectStats':
        """Create ProjectStats from dictionary"""
        sessions_data = data.get('sessions', [])
        sessions = [WritingSession.from_dict(s) for s in sessions_data]

        return cls(
            total_words=data.get('total_words', 0),
            total_characters=data.get('total_characters', 0),
            total_paragraphs=data.get('total_paragraphs', 0),
            total_sentences=data.get('total_sentences', 0),
            total_sessions=data.get('total_sessions', 0),
            total_time_minutes=data.get('total_time_minutes', 0),
            daily_goal=data.get('daily_goal', 1000),
            weekly_goal=data.get('weekly_goal', 7000),
            sessions=sessions
        )
