import os
import subprocess
import webbrowser
import requests
import keyboard
import asyncio
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq

# Ensure the AppOpener Data folder exists
app_opener_data_path = os.path.join(
    os.path.dirname(__file__), "..", ".venv", "lib", "site-packages", "AppOpener", "Data"
)

os.makedirs(app_opener_data_path, exist_ok=True)
app_names_temp_path = os.path.join(app_opener_data_path, "app_names_temp.json")

if not os.path.exists(app_names_temp_path):
    with open(app_names_temp_path, "w") as f:
        f.write("{}")  # Creates an empty JSON file

try:
    from AppOpener import close, open as appopen
except ImportError:
    print("[bold red]Error: AppOpener not installed![/bold red]")
    print("Try running: pip install AppOpener")
    exit(1)

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# User agent for web scraping
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Applewebkit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System chatbot message
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {os.getenv('USERNAME', 'User')}, You're a content writer. You have to write content like a letter."
}]

messages = []

def GoogleSearch(Topic):
    """Performs a Google search using pywhatkit."""
    search(Topic)
    return True

def Content(Topic):
    """Generates AI content, saves to a file, and opens it in Notepad."""
    
    def OpenNotepad(File):
        """Opens the given file in Notepad."""
        subprocess.Popen(['notepad.exe', File])

    def ContentWriteAI(prompt):
        """Generates AI content using Groq API."""
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7
        )

        Answer = completion.choices[0].message.content if completion.choices else ""
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    # Clean up the topic name
    Topic = Topic.replace("Content", "").strip()
    ContentByAI = ContentWriteAI(Topic)

    # Ensure the Data directory exists
    os.makedirs("Data", exist_ok=True)

    file_path = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(file_path)
    return True

def YoutubeSearch(Topic):
    """Performs a YouTube search."""
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    """Plays a video on YouTube."""
    playonyt(query)
    return True


def OpenApp(app):
    """Opens an application or searches Google if it fails."""
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print(f"[bold yellow]Warning:[/bold yellow] Couldn't open {app}. Searching on Google...")
        webopen(f"https://www.google.com/search?q={app}")
        return False

def CloseApp(app):
    """Closes an application if possible."""
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False
        
def System(command):
    """Controls system volume and settings."""
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down")
    }

    if command in actions:
        actions[command]()
        return True
    return False

async def TranslateAndExecute(commands: list[str]):
    """Translates and executes commands asynchronously."""
    funcs = []

    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))

        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))

        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))

        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))

        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))

        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search ")))

        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))

        else:
            print(f"No function found for: {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        yield result

async def Automation(commands):
    """Executes automation tasks asynchronously."""
    async for result in TranslateAndExecute(commands):
        pass
    return True
