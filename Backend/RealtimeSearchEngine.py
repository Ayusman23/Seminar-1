from googlesearch import search
from groq import Client
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("Groq API key is missing. Please check your .env file.")

client = Client(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}, which has real-time up-to-date information from the internet.
*** Provide answers in a professional way, ensuring proper grammar, punctuation, and clarity. ***
*** Just answer the question from the provided data in a professional way. ***"""

# Load chat log file or create a new one
chatlog_path = r"Data\ChatLog.json"

if not os.path.exists(chatlog_path):
    with open(chatlog_path, "w") as f:
        dump([], f)

def load_chat_history():
    """Loads chat history from the JSON file."""
    with open(chatlog_path, "r") as f:
        return load(f)

def save_chat_history(messages):
    """Saves chat history to the JSON file."""
    with open(chatlog_path, "w") as f:
        dump(messages, f, indent=4)

def GoogleSearch(query):
    """Performs a Google search and returns the top 5 results."""
    try:
        results = list(search(query, num_results=5))
        if not results:
            return "No search results found."

        Answer = f"The search results for '{query}' are:\n[start]\n"
        for idx, url in enumerate(results, start=1):
            Answer += f"{idx}. {url}\n"
        Answer += "[end]"

        return Answer
    except Exception as e:
        return f"Error retrieving search results: {e}"

def AnswerModifier(Answer):
    """Removes extra spaces or empty lines in the answer."""
    return "\n".join(line.strip() for line in Answer.split("\n") if line.strip())

def Information():
    """Returns real-time date and time information."""
    current_date_time = datetime.datetime.now()
    return f"""Use This Real-time Information if needed:
Day: {current_date_time.strftime("%A")}
Date: {current_date_time.strftime("%d")}
Month: {current_date_time.strftime("%B")}
Year: {current_date_time.strftime("%Y")}
Time: {current_date_time.strftime("%H")} hours, {current_date_time.strftime("%M")} minutes, {current_date_time.strftime("%S")} seconds.
"""

def RealtimeSearchEngine(prompt):
    """Handles chatbot interaction with real-time search capabilities."""
    messages = load_chat_history()  # Load chat history once

    messages.append({"role": "user", "content": prompt})

    search_results = GoogleSearch(prompt)  # Perform Google search

    system_chatbot = [
        {"role": "system", "content": System},
        {"role": "system", "content": Information()},
        {"role": "system", "content": search_results}
    ]

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=system_chatbot + messages,  # Use temporary system messages
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""

    for chunk in completion:
        if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = AnswerModifier(Answer.replace("<\\s>", "").strip())

    messages.append({"role": "assistant", "content": Answer})  # Append AI response to chat log

    save_chat_history(messages)  # Save updated chat log

    return Answer

if __name__ == "__main__":
    while True:
        try:
            prompt = input("Enter your query: ").strip()
            if prompt.lower() in ["exit", "quit"]:
                print("Exiting chat...")
                break
            print(RealtimeSearchEngine(prompt))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
