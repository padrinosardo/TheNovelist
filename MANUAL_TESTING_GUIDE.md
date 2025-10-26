# The Novelist - Manual Testing Guide

## 🎯 Test Checklist Overview

- [ ] Application startup
- [ ] New project creation
- [ ] Manuscript editing
- [ ] Character creation
- [ ] Character editing
- [ ] Image management
- [ ] Project saving
- [ ] Project loading
- [ ] Analysis tools
- [ ] Character deletion
- [ ] UI navigation
- [ ] Menu functionality

---

## 🚀 Test 1: Application Startup

### Steps:
1. Open terminal in project directory
2. Run: `python main.py`

### Expected Results:
- ✅ Application window opens without errors
- ✅ Window title: "The Novelist"
- ✅ Menu bar visible: File | Edit | View | Tools | Help
- ✅ Sidebar shows: "No project open"
- ✅ Workspace shows manuscript editor (empty)
- ✅ Status bar: "Ready - Create or open a project to start"

### What to Check:
- No Python errors in terminal
- All UI elements render correctly
- Window is resizable

---

## 🆕 Test 2: Create New Project

### Steps:
1. Click **File → New Project** (or press Ctrl+N)
2. Enter project title: `My First Novel`
3. Click OK
4. Enter author name: `Your Name`
5. Click OK
6. Choose save location: `test_novel.tnp`
7. Click Save

### Expected Results:
- ✅ Dialog appears asking for title
- ✅ Dialog appears asking for author
- ✅ File dialog appears with `.tnp` extension
- ✅ Project created successfully
- ✅ Window title changes to: "The Novelist - My First Novel"
- ✅ Sidebar shows:
  ```
  📁 My First Novel
  ├─ 📄 Manuscript (selected)
  └─ 👤 Characters
  ```
- ✅ Status bar: "Created new project: My First Novel"
- ✅ File `test_novel.tnp` created on disk

### What to Check:
- File actually exists in chosen location
- Window title updated
- Tree structure correct

---

## ✍️ Test 3: Write Manuscript Text

### Steps:
1. Make sure "Manuscript" is selected in sidebar
2. Click in the text editor area
3. Type some text (at least 3-4 paragraphs), for example:

```
Chapter 1: The Beginning

It was a dark and stormy night when Detective Marco Rossi received
the phone call that would change his life forever. The rain hammered
against the windows of his small office, creating a rhythmic backdrop
to the woman's desperate voice on the other end of the line.

"Detective Rossi, you have to help me," she pleaded. "My sister has
disappeared, and the police won't listen. They say she's just run away,
but I know better. I know something terrible has happened."

Marco grabbed his notebook and pen, ready to take down the details.
Little did he know that this case would lead him down a rabbit hole
of corruption, betrayal, and long-buried secrets.
```

### Expected Results:
- ✅ Text appears in editor
- ✅ Word/character counter updates (bottom right of editor)
- ✅ Window title shows asterisk: "The Novelist - My First Novel *"
- ✅ No lag when typing

### What to Check:
- Text is editable
- Cursor position correct
- Modified indicator (*) appears

---

## 💾 Test 4: Save Project

### Steps:
1. Click **File → Save Project** (or press Ctrl+S)
2. Wait for status bar message

### Expected Results:
- ✅ Status bar: "Project saved successfully"
- ✅ Asterisk (*) removed from window title: "The Novelist - My First Novel"
- ✅ No error dialogs

### What to Check:
- File modification time updated on disk
- No errors in terminal

---

## 👤 Test 5: Add First Character

### Steps:
1. Click on **"👤 Characters"** in sidebar
2. Right-click on "Characters" → Select **"Add New Character"**
   OR click the **"+ New Character"** button in the workspace
3. Enter character name: `Marco Rossi`
4. Click OK

### Expected Results:
- ✅ Dialog asks for character name
- ✅ View switches to Character Detail form
- ✅ Form shows:
  - Name field filled with "Marco Rossi"
  - Empty description field
  - Empty image gallery
- ✅ Sidebar updated:
  ```
  📁 My First Novel *
  ├─ 📄 Manuscript
  └─ 👤 Characters
     └─ 📷 Marco Rossi
  ```
- ✅ Window title shows asterisk (modified)

### What to Check:
- Character appears in tree
- Detail view loaded
- Modified indicator active

---

## 📝 Test 6: Edit Character Details

### Steps:
1. Make sure Marco Rossi character detail is open
2. In the **Description** field, type:

```
Detective Marco Rossi is a 42-year-old private investigator based in Milan.
He has a troubled past, having left the police force under mysterious
circumstances five years ago.

Physical Appearance:
- Tall, about 6'1"
- Dark, graying hair
- Piercing blue eyes
- Usually wears a worn leather jacket

Personality:
- Cynical but with a heart of gold
- Brilliant investigator
- Struggles with alcohol
- Haunted by past mistakes

Background:
- Former police detective
- Divorced, one daughter he rarely sees
- Lives in a small apartment above a bookstore
```

3. Click **"💾 Save Changes"** button

### Expected Results:
- ✅ Dialog: "Character updated successfully!"
- ✅ Click OK
- ✅ No errors
- ✅ Description saved

### What to Check:
- Save confirmation appears
- No data loss

---

## 🖼️ Test 7: Add Character Image

### Steps:

**Option A - Using "Add Image" button:**
1. Click **"+ Add Image"** button in image gallery
2. Select an image file (PNG, JPG, etc.) from your computer
3. Click Open

**Option B - Using Drag & Drop:**
1. Open your file manager
2. Find an image file
3. Drag it into the "Drag & drop images here" area

### Expected Results:
- ✅ Image appears as thumbnail in gallery
- ✅ Drop zone disappears (if it was visible)
- ✅ Remove button appears under thumbnail
- ✅ Message: "Character updated successfully!" (or similar)
- ✅ Sidebar shows asterisk (modified)

### What to Check:
- Image displays correctly
- Can add multiple images
- Remove button works (click it to test, then re-add)

---

## 👥 Test 8: Add Second Character

### Steps:
1. Click **"← Back to Characters"** button
2. Click **"+ New Character"** button
3. Enter name: `Elena Marchetti`
4. Click OK
5. Add description:

```
Elena Marchetti is the missing woman's sister who hired Marco to investigate.

Physical Appearance:
- Mid-30s
- Long dark hair
- Elegant and well-dressed
- Striking resemblance to her sister

Personality:
- Strong-willed and determined
- Protective of her family
- Hiding something about her past
- Becomes Marco's ally in the investigation
```

6. Click **"💾 Save Changes"**
7. Optionally add an image

### Expected Results:
- ✅ View switches to characters list showing both:
  ```
  [Marco Rossi card]  [Elena Marchetti card]
  ```
- ✅ Detail view for Elena opens
- ✅ Save successful
- ✅ Sidebar updated:
  ```
  📁 My First Novel *
  ├─ 📄 Manuscript
  └─ 👤 Characters
     ├─ 📷 Marco Rossi
     └─ 📷 Elena Marchetti
  ```

### What to Check:
- Both characters visible in tree
- Both characters show in grid view
- Can switch between characters by clicking

---

## 💾 Test 9: Save Project with Characters

### Steps:
1. Press **Ctrl+S** (or File → Save Project)
2. Wait for confirmation

### Expected Results:
- ✅ Status bar: "Project saved successfully"
- ✅ Asterisk removed from title
- ✅ File size of `test_novel.tnp` increased (check in file manager)

### What to Check:
- File modified time updated
- File size larger than before

---

## 📂 Test 10: Close and Reopen Project

### Steps:
1. Click **File → Close Project**
2. Confirm if asked
3. Verify project closed:
   - Window title: "The Novelist"
   - Sidebar: "No project open"
   - Editor empty
4. Click **File → Open Project**
5. Select `test_novel.tnp`
6. Click Open

### Expected Results:
- ✅ Project loads successfully
- ✅ Manuscript text restored exactly as written
- ✅ Both characters appear in sidebar
- ✅ Character descriptions preserved
- ✅ Character images restored (if added)
- ✅ Status bar: "Opened: My First Novel"

### What to Check:
- ALL data restored correctly
- Images display properly
- No data loss

---

## 🔍 Test 11: Grammar Analysis

### Steps:
1. Click on **"📄 Manuscript"** in sidebar
2. Make sure there's text in the editor
3. Press **F7** (or Tools → Grammar Check)
4. Wait for analysis to complete

### Expected Results:
- ✅ Progress bar appears at bottom
- ✅ Status: "Grammar analysis in progress..."
- ✅ After completion:
  - Progress bar disappears
  - Grammar panel on right shows results
  - Errors highlighted in text (if any)
  - Status: "Grammar analysis completed"

### What to Check:
- Analysis completes without errors
- Results displayed in right panel
- No application freeze during analysis

**Note:** Grammar check requires internet connection for LanguageTool API.

---

## 🔄 Test 12: Repetitions Analysis

### Steps:
1. Ensure manuscript is visible
2. Press **F8** (or Tools → Repetitions Analysis)
3. Wait for analysis

### Expected Results:
- ✅ Progress bar appears
- ✅ Status: "Repetitions analysis in progress..."
- ✅ Results show in "Repetitions" panel:
  - List of repeated words
  - Frequency bars
  - Word counts
- ✅ Status: "Repetitions analysis completed"

### What to Check:
- Common words identified
- Frequency counts accurate
- Visual bars display

---

## ✍️ Test 13: Style Analysis

### Steps:
1. Ensure manuscript is visible
2. Press **F9** (or Tools → Style Analysis)
3. Wait for analysis

### Expected Results:
- ✅ Progress bar appears
- ✅ Status: "Style analysis in progress..."
- ✅ Results show in "Style" panel:
  - Sentence length statistics
  - Readability score (Gulpease index)
  - Lexical diversity
  - Part-of-speech breakdown
- ✅ Status: "Style analysis completed"

### What to Check:
- Statistics calculated
- Metrics displayed clearly
- No errors

---

## 🗑️ Test 14: Delete Character

### Steps:
1. Click on **"👤 Characters"** in sidebar
2. Click on one character card (e.g., Elena Marchetti)
3. Click **"🗑️ Delete Character"** button
4. Confirm deletion in dialog

### Expected Results:
- ✅ Confirmation dialog appears
- ✅ After confirming:
  - Character removed from sidebar tree
  - View switches to characters list
  - Only remaining character(s) visible
  - Character's images deleted from project
- ✅ Window shows asterisk (modified)

### What to Check:
- Character completely removed
- Images deleted
- Other characters unaffected

---

## 🧭 Test 15: Navigation & View Switching

### Steps:
1. Click **"📄 Manuscript"** in sidebar
2. Verify manuscript view appears
3. Click **"👤 Characters"** in sidebar
4. Verify characters list appears
5. Click on a character in the tree
6. Verify character detail appears
7. Click **"← Back to Characters"**
8. Verify characters list appears

### Expected Results:
- ✅ All view switches work smoothly
- ✅ No lag or freezing
- ✅ Correct view displayed each time
- ✅ Data preserved when switching

### What to Check:
- Smooth transitions
- No data loss between views
- Selection highlighting in tree

---

## 📋 Test 16: Menu Keyboard Shortcuts

### Test these shortcuts:

| Shortcut | Action | Expected Result |
|----------|--------|----------------|
| Ctrl+N | New Project | New project dialog opens |
| Ctrl+O | Open Project | File dialog opens |
| Ctrl+S | Save Project | Project saves |
| Ctrl+W | Close Project | Project closes (ask if unsaved) |
| Ctrl+B | Toggle Sidebar | Sidebar hides/shows |
| Ctrl+P | Toggle Analysis | Analysis panels hide/show |
| F7 | Grammar Check | Grammar analysis starts |
| F8 | Repetitions | Repetitions analysis starts |
| F9 | Style | Style analysis starts |

### What to Check:
- All shortcuts work
- No conflicts with system shortcuts

---

## 💾 Test 17: Save As

### Steps:
1. Have a project open with some data
2. Click **File → Save Project As**
3. Enter new filename: `test_novel_copy.tnp`
4. Click Save

### Expected Results:
- ✅ File saved with new name
- ✅ Window title updates to new project name
- ✅ Current project now points to new file
- ✅ Original file still exists separately

### What to Check:
- Both files exist
- Working on new file now
- Original file unchanged

---

## 🎨 Test 18: View Toggles

### Steps:
1. Press **Ctrl+B** (Toggle Sidebar)
2. Verify sidebar disappears
3. Press **Ctrl+B** again
4. Verify sidebar reappears
5. Go to manuscript view
6. Press **Ctrl+P** (Toggle Analysis Panels)
7. Verify analysis panels disappear
8. Press **Ctrl+P** again
9. Verify panels reappear

### Expected Results:
- ✅ Sidebar toggles on/off
- ✅ Workspace expands/contracts accordingly
- ✅ Analysis panels toggle on/off
- ✅ Editor expands/contracts accordingly
- ✅ No layout glitches

---

## ⚠️ Test 19: Unsaved Changes Warning

### Steps:
1. Open or create a project
2. Make a change (edit text or character)
3. **Don't save**
4. Try to close project (File → Close Project)

### Expected Results:
- ✅ Dialog appears:
  - "Do you want to save changes before continuing?"
  - Options: Save / Discard / Cancel
- ✅ Clicking **Save**: saves and closes
- ✅ Clicking **Discard**: closes without saving
- ✅ Clicking **Cancel**: stays in project

### Repeat for:
- File → New Project (with unsaved changes)
- File → Open Project (with unsaved changes)
- Closing window (X button)

### What to Check:
- Warning appears when expected
- All three options work correctly
- No data loss if saved

---

## 🎭 Test 20: Multiple Characters Management

### Steps:
1. Create at least 3-4 characters
2. Add different descriptions to each
3. Add images to some (not all)
4. Navigate between characters:
   - Click in tree
   - Click cards in list view
5. Edit descriptions
6. Add/remove images
7. Save project
8. Close and reopen

### Expected Results:
- ✅ All characters display correctly
- ✅ Character cards show properly in grid (3 per row)
- ✅ Images display correctly (or placeholder if none)
- ✅ Navigation smooth
- ✅ All data persists after reload

---

## 📊 Test 21: Character Images - Edge Cases

### Test these scenarios:

**A. Multiple images per character:**
1. Add 3-4 images to one character
2. Verify all display as thumbnails
3. Remove middle image
4. Add another image
5. Save and reload

**B. Large images:**
1. Add a very large image (e.g., 5000x3000 pixels)
2. Verify it's resized properly in thumbnail
3. No memory issues

**C. Invalid files:**
1. Try to drag a .txt file
2. Should show error: "Please drop an image file"

**D. Missing images:**
1. Save project with images
2. Manually delete image from extracted ZIP
3. Reopen project
4. Should show placeholder instead of crash

---

## 🏁 Test 22: Complete Workflow

### Full end-to-end test:

1. ✅ Start application
2. ✅ Create new project
3. ✅ Write 5+ paragraphs of text
4. ✅ Create 3 characters with descriptions
5. ✅ Add images to at least 2 characters
6. ✅ Run grammar analysis
7. ✅ Run repetitions analysis
8. ✅ Run style analysis
9. ✅ Save project
10. ✅ Close application completely
11. ✅ Restart application
12. ✅ Open saved project
13. ✅ Verify all data intact:
    - Manuscript text
    - All 3 characters
    - All descriptions
    - All images
    - Analysis results cleared (expected)
14. ✅ Make edits to manuscript
15. ✅ Edit one character
16. ✅ Delete one character
17. ✅ Save project
18. ✅ Reload project
19. ✅ Verify changes persisted

---

## 📝 Test Results Template

Use this to track your testing:

```
Date: _______________
Tester: _______________

Test Results:
[ ] Test 1: Application Startup - PASS / FAIL
[ ] Test 2: Create New Project - PASS / FAIL
[ ] Test 3: Write Manuscript Text - PASS / FAIL
[ ] Test 4: Save Project - PASS / FAIL
[ ] Test 5: Add First Character - PASS / FAIL
[ ] Test 6: Edit Character Details - PASS / FAIL
[ ] Test 7: Add Character Image - PASS / FAIL
[ ] Test 8: Add Second Character - PASS / FAIL
[ ] Test 9: Save Project with Characters - PASS / FAIL
[ ] Test 10: Close and Reopen Project - PASS / FAIL
[ ] Test 11: Grammar Analysis - PASS / FAIL
[ ] Test 12: Repetitions Analysis - PASS / FAIL
[ ] Test 13: Style Analysis - PASS / FAIL
[ ] Test 14: Delete Character - PASS / FAIL
[ ] Test 15: Navigation & View Switching - PASS / FAIL
[ ] Test 16: Menu Keyboard Shortcuts - PASS / FAIL
[ ] Test 17: Save As - PASS / FAIL
[ ] Test 18: View Toggles - PASS / FAIL
[ ] Test 19: Unsaved Changes Warning - PASS / FAIL
[ ] Test 20: Multiple Characters Management - PASS / FAIL
[ ] Test 21: Character Images - Edge Cases - PASS / FAIL
[ ] Test 22: Complete Workflow - PASS / FAIL

Issues Found:
1. _________________________________________
2. _________________________________________
3. _________________________________________

Notes:
_____________________________________________
_____________________________________________
```

---

## 🐛 Known Issues to Watch For

If you encounter these, let me know:

1. **Images not loading**: Check if temp directory exists and has correct permissions
2. **Analysis stuck**: LanguageTool requires internet connection
3. **Window doesn't resize properly**: Check Qt installation
4. **Characters not updating in tree**: Try clicking "Back" and reopening
5. **ZIP file corrupted**: Check disk space and file permissions

---

## 🎯 Critical Tests (Must Pass)

These are the absolute minimum that must work:

1. ✅ Application starts without errors
2. ✅ Can create new project
3. ✅ Can write and save text
4. ✅ Can add character
5. ✅ Can edit character
6. ✅ Can save project
7. ✅ Can reopen project with all data intact
8. ✅ No data loss at any point

---

## 📞 Reporting Issues

If you find issues, please report:
- Which test failed
- Exact steps to reproduce
- Error messages (if any)
- Screenshots (if UI issue)
- Console output (from terminal)

Good luck with testing! 🚀
