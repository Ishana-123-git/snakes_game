# 🐍 Advanced Snake Game (Python + Pygame)

An advanced and feature-rich **Snake Game** built using **Python** and **Pygame**, featuring multiple game modes, AI opponent, power-ups, obstacles, high-score saving, and a polished UI.

---

## 🚀 Features

### 🎮 Game Modes
- **Classic Mode** – Traditional Snake; eat food and grow.
- **AI Battle Mode** – Compete with an AI snake using BFS pathfinding.
- **Obstacle Challenge** – Navigate around obstacles; difficulty increases every level.

---

## 🧠 AI Opponent
- Intelligent AI using **Breadth-First Search (BFS)**  
- Competes for food  
- Avoids walls, obstacles, and snakes  

---

## ⚡ Power-Ups
| Power-Up | Color | Effect |
|----------|--------|--------|
| ⚡ Speed Boost | Cyan | Snake moves faster |
| 🟣 Slow Down | Purple | Reduces speed |
| ⭐ Double Points | Yellow | 2× points |
| 🔥 Invincibility | Orange | Temporary immunity |

---

## 🧱 Obstacles
- Auto-generated in Obstacle Mode  
- Gets harder each level  

---

## 📊 High Scores
- Stored in **snake_scores.json**  
- Separate scores for each mode:  
  - Classic  
  - AI Battle  
  - Obstacle Challenge  

---

## 🕹️ Controls

| Key | Action |
|-----|--------|
| ↑ ↓ ← → | Move |
| Enter | Select |
| ESC | Pause / Back |
| Close Window | Quit |

---

## 📦 Installation

### 1️⃣ Install Python
Ensure Python 3.8+ is installed.

### 2️⃣ Install Pygame
pip install pygame

### 3️⃣ Run the Game
python snake_game.py

---

## 📁 Project Structure
│── snake_game.py
│── snake_scores.json
│── README.md

---

## 🧠 How the AI Works
- Finds shortest path with **BFS**
- Avoids:
  - Walls 🧱
  - Obstacles 🚧
  - Its own body 🟦
  - Player snake 🟩
- Uses fallback movement when no path exists

---

## 🏆 Scoring
- 🍎 Food = **10 points**
- ⭐ Double Points = **20 points**
- High scores saved automatically

---

## 🔧 Technical Highlights
- Fully **Object-Oriented**
- Clean modules for:
  - Input handling  
  - Rendering  
  - AI logic  
  - Power-ups  
  - Collision detection  

---

## 🎯 Future Enhancements
- Multiplayer  
- A* or Reinforcement Learning AI  
- Themes / Skins  
- Sound effects & music  
- Settings menu  

---

## ❤️ Contributions
Feel free to fork and improve the project!

---

