# 📝 The Novelist - AI-Powered Writing Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.6+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

A powerful desktop application for writers that provides AI-powered analysis of grammar, style, and repetitions in Italian texts.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Contributing](#contributing)

</div>

---

## ✨ Features

### 📖 **Grammar Analysis**
- Real-time grammatical error detection
- Contextual suggestions for corrections
- Supports Italian language rules
- Powered by LanguageTool API

### 🔄 **Repetition Detection**
- Identifies overused words
- Visual frequency bars
- Excludes stop words automatically
- Helps improve vocabulary diversity

### ✍️ **Style Analysis**
- Sentence length evaluation
- Lexical diversity metrics
- Readability scoring (Gulpease index)
- Part-of-speech composition analysis

### 🎨 **Modern UI**
- Clean, professional interface
- Resizable panels
- Real-time word/character counter
- Non-blocking analysis with progress indicators

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/the-novelist.git
cd the-novelist
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download Italian Language Model
```bash
python -m spacy download it_core_news_sm
```

### Step 5: Run the Application
```bash
python main.py
```

---

## 📦 Project Structure
```
TheNovelist/
│
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
│
├── analisi/                     # Analysis modules
│   ├── __init__.py
│   ├── grammatica.py           # Grammar analyzer
│   ├── ripetizioni.py          # Repetition analyzer
│   └── stile.py                # Style analyzer
│
├── ui/                         # User interface
│   ├── __init__.py
│   ├── finestra_principale.py  # Main window
│   ├── pannelli.py             # Custom panels
│   └── stili.py                # Styles and colors
│
├── workers/                    # Background workers
│   ├── __init__.py
│   └── analisi_thread.py       # Analysis thread
│
└── utils/                      # Utilities (future)
    └── __init__.py
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **PySide6** | Desktop GUI framework (Qt for Python) |
| **spaCy** | Natural Language Processing |
| **LanguageTool** | Grammar and spell checking |
| **textstat** | Readability metrics |
| **Python 3.9+** | Core programming language |

---

## 📖 Usage

1. **Write Your Text**: Use the left editor panel to write or paste your text
2. **Analyze**: Click one of the analysis buttons in the header:
   - 📖 **Grammar**: Check for grammatical errors
   - 🔄 **Repetitions**: Find overused words
   - ✍️ **Style**: Evaluate writing style and readability
3. **Review Results**: Results appear in the corresponding panel on the right
4. **Improve**: Use suggestions to enhance your writing

### Example Workflow
```
1. Write draft text in editor
2. Click "Grammar" → Fix errors
3. Click "Repetitions" → Find synonyms for overused words
4. Click "Style" → Adjust sentence length and complexity
5. Repeat until satisfied
```

---

## 🗺️ Roadmap

### Current Version (v1.0)
- [x] Grammar analysis with LanguageTool
- [x] Repetition detection
- [x] Style metrics (readability, diversity)
- [x] Modern resizable UI

### Planned Features (v1.1)
- [ ] Save/Load projects
- [ ] Export analysis to PDF
- [ ] Synonym suggestions on word selection
- [ ] Character database for fiction writers
- [ ] Dark mode theme
- [ ] Multi-language support (EN, ES, FR, DE)

### Future Ideas (v2.0+)
- [ ] AI-powered character generation (using Ollama)
- [ ] Plot structure analyzer
- [ ] Writing statistics dashboard
- [ ] Cloud sync for projects
- [ ] Collaboration features
- [ ] Plugin system

---

## 🤝 Contributing

Contributions are welcome! This project aims to be a collaborative international effort.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines

- Write clean, documented code
- Follow PEP 8 style guidelines
- Add docstrings to all functions/classes
- Test your changes thoroughly
- Update README if adding new features

### Areas for Contribution

- 🌍 **Translations**: Add support for more languages
- 🎨 **UI/UX**: Improve interface design
- 🧠 **AI Features**: Implement new analysis algorithms
- 📝 **Documentation**: Improve docs and tutorials
- 🐛 **Bug Fixes**: Report and fix bugs

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LanguageTool** - For grammar checking API
- **spaCy** - For NLP capabilities
- **Qt/PySide6** - For the GUI framework
- All contributors who help improve this project

---

## 📧 Contact

- **Project Maintainer**: [Your Name](https://github.com/yourusername)
- **Issues**: [GitHub Issues](https://github.com/yourusername/the-novelist/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/the-novelist/discussions)

---

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/the-novelist&type=Date)](https://star-history.com/#yourusername/the-novelist&Date)

---

<div align="center">

Made with ❤️ by writers, for writers

[Report Bug](https://github.com/yourusername/the-novelist/issues) • [Request Feature](https://github.com/yourusername/the-novelist/issues)

</div>
```

## **📄 Crea anche LICENSE (MIT)**
```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.