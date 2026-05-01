# 🧬 AllergenAI — Multi-Label Allergen Risk Assessment for Unpackaged Foods

> AI-powered food allergen detection using Google Gemini Vision Language Model

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-Vision_API-4285F4?style=flat&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00ffb4?style=flat)

🔗 **Live Demo:** [allergenai.streamlit.app](https://ayeshaazulfiqar-ai-based-food-allergen-detection-usi-app-69ljzw.streamlit.app/)

---

## 📌 Overview

**AllergenAI** is an intelligent web application that performs real-time, multi-label allergen risk assessment on unpackaged foods. Simply upload a food photo or enter a list of ingredients — the system identifies the dish and returns probability scores for 12 major allergens, including hidden allergens that are not immediately obvious.

Built as an academic project exploring the application of Vision Language Models (VLMs) in food safety and healthcare technology.

---

## 🎯 Problem Statement

Over 1 in 10 people worldwide suffer from food allergies. For individuals with dietary restrictions, consuming unpackaged food — such as restaurant meals, street food, or homemade dishes — poses a serious daily risk. Unlike packaged products, unpackaged foods have no standardised allergen labelling, leaving allergy-sufferers to guess.

AllergenAI addresses this gap by providing an instant, AI-powered allergen risk report for any food item.

---

## ✨ Features

- 🖼️ **Image Analysis** — Upload a food photo and AI identifies the dish and detects allergens visually
- 📝 **Ingredient Text Analysis** — Paste a list of ingredients for precise allergen detection
- ⚡ **Combined Mode** — Use both image and text together for maximum accuracy
- 🔍 **Detects 12 Major Allergens**:
  - 🥛 Milk &nbsp; 🥚 Egg &nbsp; 🥜 Peanut &nbsp; 🌰 Tree Nuts &nbsp; 🌾 Wheat/Gluten &nbsp; 🫘 Soy
  - 🐟 Fish &nbsp; 🦐 Shellfish &nbsp; 🌿 Sesame &nbsp; 🌼 Mustard &nbsp; 🥬 Celery &nbsp; 🦪 Molluscs
- 📊 **Visual Risk Gauges** — Per-allergen probability scores (0–100%) with colour-coded severity indicators
- 🏷️ **Dish Identification** — Automatically recognises and names the food item from an image
- ⚠️ **Hidden Allergen Detection** — Flags indirect allergens such as soy in sauces or milk in butter
- 🌑 **Dark-themed Professional UI** — Clean, modern interface built with Streamlit

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| AI Model | Google Gemini Vision (`gemini-flash-lite-latest`) |
| Image Processing | Pillow (PIL) |
| Language | Python 3.10+ |
| API Client | google-genai |

---

## 📁 Project Structure

```
AllergenAI/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/allergenai.git
cd allergenai
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a Free Gemini API Key
- Go to [aistudio.google.com](https://aistudio.google.com)
- Sign in with your Google account
- Click **Get API Key** → **Create API Key**
- Copy your key (starts with `AIza...`)

### 4. Run the App
```bash
streamlit run app.py
```

### 5. Use the App
- Enter your Gemini API key in the sidebar
- Choose a tab: **Image**, **Ingredients**, or **Both**
- Upload a food photo or enter ingredients
- Click **Analyse** and view your allergen risk report

---

## 📊 How It Works

```
User Input (Image / Text / Both)
            │
            ▼
  Google Gemini Vision API
  (gemini-flash-lite-latest)
            │
            ▼
  Structured JSON Response
  {
    dish_name,
    description,
    detected_allergens,
    allergen_risk { label: score },
    confidence,
    warning
  }
            │
            ▼
  Visual Risk Dashboard
  (Gauge meters + alerts)
```

The system prompts Gemini with a carefully engineered instruction set that forces structured JSON output, ensuring consistent parsing and display across all food types.

---

## 🖼️ Screenshots

![AllergenAI App](screenshot.png)

> 🔗 Try it live: [allergenai.streamlit.app](https://ayeshaazulfiqar-ai-based-food-allergen-detection-usi-app-69ljzw.streamlit.app/)

---

## ⚕️ Disclaimer

> This tool is for **informational purposes only**. AllergenAI is not a medical device and should not be used as a substitute for professional medical or dietary advice. Always verify allergen information with a certified food specialist or medical professional before consumption, especially for severe allergies.

---

## 🔮 Future Work

- [ ] Fine-tune a custom VLM on South Asian cuisine datasets
- [ ] Support for regional unpackaged foods (Pakistani, Indian cuisine)
- [ ] Mobile app version for on-the-go scanning
- [ ] Restaurant dashboard for allergen compliance management
- [ ] Integration with food delivery platforms
- [ ] Multilingual support (Urdu, Hindi, Arabic)

---

## 👤 Author

**Ayesha Zulfiqar**
- LinkedIn: [ayeshazulfiqar4](https://www.linkedin.com/in/ayeshazulfiqar4)
- GitHub: [ayeshaazulfiqar](https://github.com/ayeshaazulfiqar)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <b>Built with ☕ and Python</b><br>
  <i>If this helped you, give it a ⭐ on GitHub!</i>
</div>