from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# User agent for web scraping
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Applewebkit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

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
    """Generates content using AI and saves it to a file, then opens it in Notepad."""

    def OpenNotepad(File):
        """Opens the given file in Notepad."""
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriteAI(prompt):
        """Generates content using the Groq API."""
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stop=None
        )

        Answer = completion.choices[0].message.content if completion.choices else ""

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer}) 
        return Answer

    # Remove "Content" from topic if present
    Topic = Topic.replace("Content", "").strip()
    ContentByAI = ContentWriteAI(Topic)

    # Create a directory if it doesn't exist
    os.makedirs("Data", exist_ok=True)

    file_path = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    # Open the generated file in Notepad
    OpenNotepad(file_path)
    return True
def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def OpenApp(app, sess=requests.session()):

    try:
        appopen(app,match_closet=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return[]
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]
        
        def search_google(query):
            url = "https://www.google.com/search?q={query}"
            headers= {"User-Agent": useragent}
            responce = sess.get(url,hesders=headers)

            if response.Status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
            return None
        html = search_google(app)

        if html:
            link = extract_links(html)[0]
            webopen(link)

        return True
    
def CloseApp(app):

    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False
        
def System(command):

    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume mute")

    def volume_down():
        keyboard.press_and_release("volume mute")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            if "open it" in command:
                pass
            
            if "open file" == command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startwith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        elif command.startswith("googlr search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        elif command.startwith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        elif command.startswith("syatem "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"No Function Found. For {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation commands:

    async for result in TranslateAndExecute(commands):
        pass

    return True