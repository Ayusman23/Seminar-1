from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables
env_vars = dotenv_values(".env")
Inputlanguage = env_vars.get("InputLanguage", "en")  # Default to English if not set

# Define HTML Code for Speech Recognition
HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = "{Inputlanguage}";
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;
            }};

            recognition.onend = function() {{
                console.log("Recognition ended.");
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
            output.innerHTML = "";
        }}
    </script>
</body>
</html>'''

# Save HTML file
data_dir = os.path.join(os.getcwd(), "Data")
os.makedirs(data_dir, exist_ok=True)  # Ensure the Data directory exists
html_file_path = os.path.join(data_dir, "Voice.html")

with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Configure Selenium WebDriver
chrome_options = Options()
User_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={User_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# Remove `--headless=new` to allow interaction

# Setup WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define paths
temp_dir_path = os.path.abspath("Frontend/Files")
os.makedirs(temp_dir_path, exist_ok=True)  # Ensure the directory exists

# Function to update assistant status
def SetAssistantStatus(status):
    status_file = os.path.join(temp_dir_path, "Status.data")
    with open(status_file, "w", encoding="utf-8") as file:
        file.write(status)

# Function to clean and format queries
def QueryModifier(query):
    if not query:
        return ""

    new_query = query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words and query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words and query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Function to translate text
def UniversalTranslator(text):
    try:
        return mt.translate(text, "en", "auto").capitalize()
    except Exception as e:
        print(f"Translation error: {e}")
        return text.capitalize()

# Speech recognition function
def SpeechRecognition():
    driver.get(f"file:///{html_file_path}")
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            text = driver.find_element(By.ID, "output").text
            if text:
                driver.find_element(By.ID, "end").click()
                
                if Inputlanguage.lower() == "en" or "en" in Inputlanguage.lower():
                    return QueryModifier(text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(text))
            time.sleep(0.5)  # Prevent CPU overuse
        except Exception as e:
            print(f"Speech recognition error: {e}")
            time.sleep(0.5)

# Main loop
if __name__ == "__main__":
    while True:
        try:
            recognized_text = SpeechRecognition()
            print(recognized_text)
        except KeyboardInterrupt:
            print("\nExiting...")
            driver.quit()
            break
        except Exception as e:
            print(f"Error: {e}")
