#  AI Virtual Pet

An interactive AI-powered virtual pet that lives on your desktop and brings fun, comfort, and a bit of education to your daily routine. The pet chats with you, responds emotionally to your messages, and includes interactive modes like feeding, head-patting, and a built-in focus timer for study sessions.

 **Demo Video**: [https://www.youtube.com/watch?v=_CRIVEHTFRA](https://www.youtube.com/watch?v=_CRIVEHTFRA)

---

##  Features
- **Emotion-Aware Chat**: AI pet responds to what you say and adjusts its mood in real time.
- **Mood Score & Expression**: Pet animations reflect mood changes based on your interactions.
- **Two Chat Modes**: Switch between standard AI assistant mode and emotional pet mode.
- **Focus Mode**: Timer-based study mode where both you and the pet concentrate together.
- **Interactive Features**: Petting, feeding, and play mode all affect the pet's mood.
- **Transparent & Draggable**: Always-on-top pet window with transparent background.
- **Independent Chat Window**: Chat separately while keeping the pet on screen.

---

##  Dependencies
- **Python 3.8+**
- `PyQt5` (GUI framework)
- `google-generativeai` (for AI interactions)
- `python-dotenv` (for API key management)

---

##  Image Assets
The animated pet images are from the open-source **VPet** project:  
 **[VPet GitHub Repository](https://github.com/LorisYounger/VPet)**

---

##  Setup
### Step 1: Navigate into the Python project folder
```bash
cd python
```

### Step 2: Create a virtual environment
```bash
python -m venv venv
```

### Step 3: Activate the virtual environment
#### Windows
```bash
venv\Scripts\activate
```
#### macOS/Linux
```bash
source venv/bin/activate
```

### Step 4: Install required packages
```bash
pip install -r requirements.txt
```

### Step 5: Set your API Key
A `.env.example` file is included to show the correct format.  
Rename it to `.env` and add your own Google Gemini API key.

### Step 6: Run the application
```bash
python deskpet.py
```

---

## 💬 Contact
Email: [lj662244@gmail.com]  
GitHub: [https://github.com/ym2244/AI-virtual-pet](https://github.com/ym2244/AI-virtual-pet)

---
