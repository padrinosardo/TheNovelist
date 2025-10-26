# TheNovelist - Project Documentation

## Overview
TheNovelist is an AI-powered desktop writing assistant specifically designed for Italian texts. It provides real-time analysis of grammar, style, and word repetitions to help writers improve their work.

## Technology Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Core language | 3.9+ |
| PySide6 | Desktop GUI framework (Qt for Python) | Latest |
| spaCy | Natural Language Processing | Latest |
| LanguageTool | Grammar and spell checking API | Latest |
| textstat | Readability metrics calculation | Latest |

## Architecture Overview

### Core Components
- **Desktop Application**: Built with PySide6 (Qt for Python)
- **NLP Engine**: spaCy with Italian model (`it_core_news_sm`)
- **Grammar Checking**: LanguageTool API (requires internet connection)
- **Async Processing**: QThread for non-blocking analysis operations
- **Target Language**: Italian (primary), with plans for multi-language support

### Design Principles
1. **Non-blocking UI**: All heavy analysis operations run in background threads
2. **Modular Analysis**: Each analysis type (grammar, repetitions, style) is independent
3. **Clean Separation**: UI, analysis logic, and workers are clearly separated
4. **Extensibility**: Easy to add new analysis modules

## Project Structure

```
TheNovelist/
│
├── main.py                      # Application entry point
├── requirements.txt              # Python dependencies
├── PROJECT.md                    # This file
│
├── analisi/                      # Analysis modules
│   ├── __init__.py
│   ├── grammatica.py            # Grammar analysis using LanguageTool
│   ├── ripetizioni.py           # Word repetition detection
│   └── stile.py                 # Style metrics (readability, diversity)
│
├── ui/                           # User interface components
│   ├── __init__.py
│   ├── finestra_principale.py   # Main window with editor and panels
│   ├── pannelli.py              # Custom panel widgets
│   └── stili.py                 # Color schemes and styling constants
│
├── workers/                      # Background processing
│   ├── __init__.py
│   └── analisi_thread.py        # QThread wrapper for analysis
│
└── utils/                        # Utility functions
    └── __init__.py
```

## Coding Standards

### Python Style
- **PEP 8**: Strictly follow PEP 8 style guidelines
- **Docstrings**: All functions and classes must have docstrings
- **Type Hints**: Use type hints where possible for better code clarity
- **Naming Conventions**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### Threading Rules
- **Never block the UI thread** for operations taking >100ms
- Use `workers.analisi_thread` pattern for all analysis operations
- Always emit signals to communicate back to UI thread
- Handle errors gracefully in worker threads

### UI Patterns
- **Layout**: Main window uses `QSplitter` with editor (left) and analysis panels (right)
- **Custom Panels**: All panels inherit from `QWidget` and use predefined styles
- **Colors**: Defined centrally in `ui/stili.py`
- **Progress Indicators**: Show when analysis is running
- **Signal/Slot**: Use Qt's signal/slot mechanism for component communication

## Analysis Flow

Standard workflow for any analysis operation:

1. User clicks analysis button (Grammar/Repetitions/Style)
2. UI shows progress indicator
3. `analisi_thread.py` creates background worker
4. Worker executes appropriate analysis module
5. Worker emits signal with results
6. UI receives signal and updates corresponding panel
7. Progress indicator hidden

### Example Pattern
```python
# In UI component
self.worker = AnalysisWorker(self.text, analysis_type='grammar')
self.worker.finished.connect(self.on_analysis_complete)
self.worker.start()

# Worker emits signal when done
# UI updates in main thread
def on_analysis_complete(self, results):
    self.update_panel(results)
```

## Current Features

### ✅ Implemented
- **Grammar Analysis**: Real-time grammatical error detection with LanguageTool
- **Repetition Detection**: Identifies overused words with visual frequency bars
- **Style Metrics**: 
  - Sentence length evaluation
  - Lexical diversity (Type-Token Ratio)
  - Readability scoring (Gulpease index for Italian)
  - Part-of-speech composition analysis
- **Modern UI**: Clean, professional interface with resizable panels
- **Word/Character Counter**: Real-time statistics in editor

### 🚧 In Development
- Save/Load project files
- Export analysis to PDF
- Dark mode theme

### 📋 Planned Features
- Synonym suggestions on word selection
- Character database for fiction writers
- AI-powered character generation (using Ollama)
- Plot structure analyzer
- Writing statistics dashboard
- Multi-language support (EN, ES, FR, DE)
- Cloud sync for projects
- Collaboration features
- Plugin system

## Current Limitations

1. **Language**: Only Italian language is currently supported
2. **Internet Required**: LanguageTool API requires active internet connection
3. **No Persistence**: Projects cannot be saved/loaded yet (high priority TODO)
4. **Single User**: No collaboration or cloud features
5. **Theme**: Only light mode available

## Dependencies Management

### Installing Dependencies
```bash
pip install -r requirements.txt
python -m spacy download it_core_news_sm
```

### Key Dependencies
- `PySide6`: Qt framework for Python (GUI)
- `spacy`: NLP processing
- `language-tool-python`: Grammar checking
- `textstat`: Readability calculations
- `it_core_news_sm`: Italian language model for spaCy

## Testing Approach

### Current State
- Manual testing only
- Test each feature after implementation

### Future Plans
- Unit tests for analysis modules
- Integration tests for UI components
- Automated regression testing

## Configuration

### LanguageTool
- Uses public API endpoint by default
- Can be configured to use local LanguageTool server for better performance

### spaCy Model
- Italian model: `it_core_news_sm`
- Loaded once at application startup
- Used for tokenization, POS tagging, and lexical analysis

## UI Component Guidelines

### Creating New Panels
When adding new analysis panels:

1. Inherit from base panel class in `pannelli.py`
2. Use colors from `stili.py`
3. Implement clear visual hierarchy
4. Add loading states
5. Handle empty/error states gracefully

### Adding New Analysis
When implementing new analysis features:

1. Create new module in `analisi/` directory
2. Implement analysis function that takes text and returns results
3. Create worker in `workers/` if analysis is time-consuming
4. Add button in main window header
5. Create corresponding results panel
6. Update this documentation

## AI Integration Strategy

### Current AI Usage
- LanguageTool (rule-based + ML for grammar)
- spaCy (transformer-based NLP)

### Planned AI Features
- **Ollama Integration**: For character generation and creative suggestions
- **LLM-based Analysis**: For plot structure and narrative flow
- **Style Matching**: AI-powered style consistency checking

### AI Integration Principles
- Always provide option to disable AI features
- Cache AI responses when possible
- Handle API failures gracefully
- Never block UI waiting for AI responses
- Provide clear attribution for AI-generated content

## Performance Considerations

### Current Optimizations
- Lazy loading of spaCy model
- Background threading for analysis
- Efficient text processing with spaCy

### Known Performance Issues
- Large texts (>50k words) may slow down analysis
- LanguageTool API can be slow (consider local server)

### Future Optimizations
- Implement incremental analysis (only changed paragraphs)
- Add caching layer for repeated analysis
- Consider local LanguageTool server setup

## Internationalization (Future)

### Multi-language Support Plan
1. Separate UI strings from code
2. Use Qt's translation system
3. Add language selection in preferences
4. Support for: English, Spanish, French, German
5. Adapt analysis engines per language (spaCy models, LanguageTool)

## Contributing Guidelines

When contributing to this project:

1. **Code Quality**:
   - Follow all coding standards above
   - Add docstrings to all new functions/classes
   - Write clean, self-documenting code
   - Test thoroughly before submitting

2. **Git Workflow**:
   - Fork repository
   - Create feature branch: `git checkout -b feature/AmazingFeature`
   - Commit with clear messages: `git commit -m 'Add: Feature description'`
   - Push: `git push origin feature/AmazingFeature`
   - Open Pull Request

3. **Documentation**:
   - Update README.md if adding user-facing features
   - Update this PROJECT.md if changing architecture
   - Add inline comments for complex logic

4. **Areas for Contribution**:
   - 🌍 Translations: Add support for more languages
   - 🎨 UI/UX: Improve interface design
   - 🧠 AI Features: Implement new analysis algorithms
   - 📝 Documentation: Improve docs and tutorials
   - 🐛 Bug Fixes: Report and fix bugs

## License
MIT License - See LICENSE file for details

---

**Last Updated**: October 2025  
**Maintainer**: [@padrinosardo](https://github.com/padrinosardo)  
**Repository**: https://github.com/padrinosardo/TheNovelist