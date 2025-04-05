# 💻✨ Web Scrapping AI Agent 🕸️🤖 <img src="https://img.shields.io/badge/AI%20Powered-OpenAI-blue.svg" alt="AI Powered Badge"/> <img src="https://img.shields.io/badge/Library-ScrapeGraphAI-brightgreen.svg" alt="ScrapeGraphAI Badge"/>

Tired of tedious manual web scraping? 😩 Let AI do the heavy lifting! 💪

This awesome Streamlit app deploys an intelligent **AI Agent** to fetch exactly the data you need from *any* website. Just point it to a URL, tell it what you want, and watch the magic happen! ✨

Powered by **OpenAI's** powerful language models (GPT-3.5-turbo or GPT-4 🧠) and the clever **scrapegraphai** library, getting web data has never been easier or smarter. 🚀

---

## ✨ Features That Make Scraping a Breeze ✨

*   **🌐 Universal Website Scraping:** Point, click, and scrape! Provide any URL and let the agent loose.
*   **🤖 AI-Powered Intelligence:** Leverages OpenAI's advanced LLMs to understand the website structure and your request, extracting data intelligently. No complex CSS selectors needed!
*   **🎯 Targeted Data Extraction:** You're in control! Tell the AI *exactly* what information you need (e.g., "Extract all product names and prices," "Summarize the main points of the article," "Find the contact email").
*   **⚙️ Model Selection:** Choose your weapon! Opt for the speed of GPT-3.5-turbo or the power of GPT-4 for more complex tasks.
*   **🎈 Simple & Interactive UI:** Built with Streamlit for a smooth and user-friendly experience.

---

## ⚙️ Requirements: Gear Up for AI Scraping! ⚙️

Make sure you have the following ready:

*   **🐍 Python 3.x**
*   **🔑 OpenAI API Key:** You'll need this to grant the AI agent access to OpenAI's models. Get yours from [OpenAI Platform](https://platform.openai.com/api-keys).
*   **📦 Python Libraries:** All necessary libraries are listed in `requirements.txt`.

---

## 🚀 Get Started in Minutes! 🚀

Follow these simple steps to launch your Web Scrapping AI Agent:

1.  **Clone the Code Base:** Grab the project files. 💾
    ```bash
    git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
    ```

2.  **Navigate to the Project Directory:** Enter the agent's lair. 📂
    ```bash
    cd awesome-llm-apps/advanced_tools_frameworks/web_scrapping_ai_agent
    ```

3.  **Install the Magic Wand (Dependencies):** Let pip install the required libraries. ✨
    ```bash
    pip install -r requirements.txt
    ```

4.  **Have Your OpenAI API Key Ready:** Keep your secret key handy! 🔑 You'll enter it directly into the app.

5.  **Run the Streamlit App:** Launch the interface and start scraping! ▶️
    ```bash
    streamlit run ai_scrapper.py
    ```

    Your browser should pop open with the app ready to go! 🎉

---

## 🤔 How it Works: The AI Magic Explained ✨

Curious about what happens behind the curtain?

1.  **🔑 Enter API Key:** You securely provide your OpenAI API Key via the Streamlit interface.
2.  **🧠 Select Model:** Choose between the speedy GPT-3.5-turbo or the powerful GPT-4.
3.  **🔗 Provide URL:** Tell the agent which website to target.
4.  **🎯 Define Task:** Enter your specific instruction (the "user prompt") telling the AI what data you want extracted.
5.  **🛠️ Create SmartScraperGraph:** The app uses `scrapegraphai` to create an intelligent scraping workflow (`SmartScraperGraph`) configured with your URL, prompt, and chosen OpenAI model.
6.  **🕸️➡️🤖 AI Scrapes & Processes:** The `SmartScraperGraph` intelligently navigates the website, identifies the relevant information based on your prompt using the LLM's understanding, and extracts it.
7.  **📊 Results Displayed:** Voilà! The extracted data is neatly presented back to you within the Streamlit app.

---

**Happy Scraping! Let the AI handle the boring stuff. 😉**
