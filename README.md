# 📚 Cardinal – A Spaced Repetition Flashcard App

**Cardinal** is a flashcard-based study tool designed to help users retain information more effectively through spaced repetition. Users can upload decks in JSON format, review cards one at a time, and optionally make their decks public so others can use them. The application is responsive and works well on both desktop and mobile devices.

---

## ✨ Distinctiveness and Complexity

Cardinal distinguishes itself from typical CS50W projects in several key ways:

- **Spaced Repetition Logic**  
  The core feature of Cardinal is a custom-built spaced repetition algorithm. Each user's performance on individual cards is tracked via the `UserCardData` model. The model stores review counts, streaks, timestamps, and uses a score-based system to calculate the optimal interval before a card should be reviewed again. This system encourages long-term retention and efficient studying.

- **User-Specific Review Scheduling**  
  The app doesn't just track whether a user got a card right or wrong — it adjusts the next appearance of each card dynamically based on their performance history. This logic introduces meaningful complexity in both model design and query handling.

- **Deck Creation via JSON Upload**  
  Instead of using a form to add one card at a time, users can upload a structured JSON file to generate a full deck. This workflow is particularly efficient and scalable for power users or AI-assisted deck generation — a distinct approach compared to the manual CRUD operations typically found in other CS50W projects.

---

## 🗂 File Descriptions

### Django Project Structure

#### `cardinal/`  
- `settings.py` – Project configuration and app registration  
- `urls.py` – Root URL routing  

#### `core/` (Main App)  
- `models.py` – Contains:
  - `User`: Custom user model  
  - `Deck`: Flashcard decks with an optional `is_public` flag  
  - `Card`: Individual flashcards linked to a deck  
  - `UserCardData`: Tracks spaced repetition metrics for each user–card pair  
- `views.py` – Core application logic:
  - User login, logout, and registration  
  - Deck creation via JSON upload  
  - Spaced repetition review view  
- `urls.py` – URL patterns for views  
- `templates/core/` – HTML Templates:
  - `layout.html`: Shared base layout  
  - `index.html`: Homepage  
  - `create.html`: Deck upload form  
  - `review.html`: Card-by-card spaced repetition view  
  - `deck.html`: View for public decks  
  - `login.html`, `register.html`: Authentication templates  

### Other Files
- `requirements.txt` – Lists dependencies (Django only)
- `README.md` – This file
- `db.sqlite3` – SQLite database (auto-generated)

---

## 🚀 How to Run the Application

Follow these steps to run the project locally:

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd cardinal
   python manage.py migrate
   python manage.py runserver