# 🥗 NutriMind

**NutriMind** is an intelligent **health and nutrition management application** that helps you take control of your dietary habits. With personalized meal planning, nutritional tracking, and progress visualization, NutriMind makes building a healthier lifestyle simple and interactive.

---

## 📑 Table of Contents

* [✨ Features](#-features)
* [🖼 Screenshots](#-screenshots)
* [🏗 Architecture](#-architecture)
* [⚙️ Installation](#️-installation)

  * [Backend Setup](#backend-setup)
  * [Frontend Setup](#frontend-setup)
* [🚀 Usage](#-usage)
* [📂 Directory Structure](#-directory-structure)
* [🤝 Contributing](#-contributing)
* [📜 License](#-license)
* [📬 Contact](#-contact)

---

## ✨ Features

* 🍽 **Daily Nutrition Tracking** – Log meals, snacks, and drinks to monitor calorie & nutrient intake.
* 🥦 **Personalized Meal Plans** – Generate meal plans tailored to your health goals and dietary needs.
* 📊 **Progress Visualization** – Interactive charts & reports to track progress over time.
* 🎯 **Goal Setting** – Define and achieve personalized health objectives.
* 💻 **Interactive Web Interface** – Clean and intuitive UI for seamless user experience.
* ⚡ **FastAPI Backend** – Scalable API to handle requests, manage data, and process user input.

---

## 🖼 Screenshots

### 📌 User Interface

![UI Screenshot](./assets/ui.png)

### 📌 Generated Meal Plan

![Output Screenshot](./assets/output.png)

---

## 🏗 Architecture

NutriMind is structured into two main components:

### 🔹 Backend (FastAPI)

* `server.py` – API server to handle requests.
* `model/` – Data models & logic for user management.
* `requirements.txt` – Dependencies list.

### 🔹 Frontend (HTML/CSS/JS)

* `index.html` – Entry point for the web app.
* `assets/` – Styles, scripts, and images.

---

## ⚙️ Installation

### Backend Setup

```bash
# Navigate to backend folder
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python server.py
```

### Frontend Setup

```bash
# Navigate to frontend folder
cd frontend

# Launch the app by opening index.html in your browser
open index.html   # macOS
start index.html  # Windows
```

---

## 🚀 Usage

1. Start the backend server at `http://localhost:8000`.
2. Open the frontend (`index.html`) in your browser.
3. Create an account or log in.
4. Start logging meals, setting goals, and monitoring progress!

---

## 📂 Directory Structure

```bash
NutriMind/
├── backend/
│   ├── model/            # Data models & logic
│   ├── server.py         # FastAPI server
│   ├── requirements.txt  # Backend dependencies
├── frontend/
│   ├── index.html        # Web app entry point
│   ├── assets/           # Styles, scripts, images
├── assets/
│   ├── ui.png            # UI screenshot
│   ├── output.png        # Meal plan screenshot
├── LICENSE               # License file
├── README.md             # Documentation
```

---

## 🤝 Contributing

We welcome contributions! 🚀

1. Fork the repo
2. Create a branch:

   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:

   ```bash
   git commit -m "Added feature-name"
   ```
4. Push to branch:

   ```bash
   git push origin feature-name
   ```
5. Submit a pull request

---

## 📜 License

This project is licensed under the **MIT License** – see [LICENSE](LICENSE) for details.

---

## 📬 Contact

👤 Maintainer: [**royxlead**](https://github.com/royxlead)
💡 Ideas, suggestions, or feedback are always welcome!
