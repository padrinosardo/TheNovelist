# 🚀 The Novelist - Quick Start Guide

## Launch the Application

```bash
cd /Users/antoniocaria/PycharmProjects/TheNovelist
python main.py
```

---

## ✅ What to Test (5 Minutes)

### 1. Create Your First Project (1 min)
- **File → New Project** (or Ctrl+N)
- Title: `My Test Novel`
- Author: Your name
- Save as: `test_novel.tnp`
- ✅ Window title should show: "The Novelist - My Test Novel"

### 2. Write Something (1 min)
- Type some text in the editor
- Notice the `*` appears (unsaved changes)
- **File → Save** (or Ctrl+S)
- ✅ `*` disappears
- ✅ In 5 minutes you'll see "Auto-saved at HH:MM" in status bar

### 3. Test Undo/Redo (30 sec)
- Type something
- Press **Ctrl+Z** (undo)
- Press **Ctrl+Y** (redo)
- ✅ Text should undo and redo

### 4. Add a Character (2 min)
- Click **"👤 Characters"** in left sidebar
- Click **"+ New Character"** button
- Name: `Mario Rossi`
- Description: Type anything (e.g., "A detective...")
- Click **"+ Add Image"** button
  - Select any image from your computer
  - ✅ Image appears as thumbnail
- Click **"💾 Save Changes"**
- ✅ Character saved

### 5. Test Recent Projects (1 min)
- **File → Close Project**
- **File → Open Recent**
- ✅ You should see "test_novel.tnp"
- Click it
- ✅ Project reopens with your text and character intact!

---

## 🎯 Key Features to Explore

### Menu Bar
- **File:** New, Open, Open Recent, Save, Save As, Close
- **Edit:** Undo, Redo, Cut, Copy, Paste
- **View:** Toggle Sidebar (Ctrl+B), Toggle Analysis (Ctrl+P)
- **Tools:** Grammar Check (F7), Repetitions (F8), Style (F9)

### Sidebar Navigation
- **📄 Manuscript** - Text editor view
- **👤 Characters** - Character list
  - Click a character → Edit details
  - Right-click → Add/Delete

### Character Features
- **Multiple images** per character
- **Drag & drop** images directly
- **Auto-save** when you click Save
- **Delete** with confirmation

### Auto-save
- Saves every **5 minutes** automatically
- Shows "Auto-saved at HH:MM" indicator
- Only saves if you made changes

---

## 🐛 If Something Doesn't Work

### Check Console Output
Look at the terminal where you ran `python main.py` for any errors.

### Common Issues

**Images not loading?**
- Make sure you're using supported formats: PNG, JPG, JPEG, GIF, BMP
- Try drag & drop instead of "+ Add Image" button

**Can't open project?**
- Check the file exists
- Make sure it's a `.tnp` file
- Try creating a new one

**Auto-save not working?**
- Wait 5 minutes after making changes
- Make sure a project is open
- Look for the indicator in bottom-right of status bar

---

## 📋 Full Testing

For complete testing instructions, see: **`MANUAL_TESTING_GUIDE.md`**

For implementation details, see: **`IMPLEMENTATION_SUMMARY.md`**

---

## 🎉 You're Ready!

The Novelist v2.0 is ready for use. Enjoy writing! ✍️
