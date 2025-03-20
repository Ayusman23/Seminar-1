from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os
import json

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey is not set in the .env file.")

client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}, with real-time information access.
*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Reply only in English, even if the question is in Hindi. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# Function to get real-time information (Used once in system prompt)
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return f"please use this real-time information if needed,\n" \
           f"Day: {current_date_time.strftime('%A')}\n" \
           f"Date: {current_date_time.strftime('%d')}\n" \
           f"Month: {current_date_time.strftime('%B')}\n" \
           f"Year: {current_date_time.strftime('%Y')}\n" \
           f"Time: {current_date_time.strftime('%H')} hours : {current_date_time.strftime('%M')} minutes : {current_date_time.strftime('%S')} seconds.\n"

SystemChatBot = [
    {"role": "system", "content": System + "\n" + RealtimeInformation()}
]

# Chat log file path
chatlog_path = r"Data/ChatLog.json"

# Ensure chat log file exists
if not os.path.exists(chatlog_path):
    with open(chatlog_path, "w") as f:
        json.dump([], f)

# Function to clean response
def AnswerModifier(Answer):
    """Removes unnecessary blank lines from AI response."""
    return "\n".join(line for line in Answer.split("\n") if line.strip())

# Chatbot function
def ChatBot(Query):
    """Sends the user's query to the chatbot and returns the AI's response."""
    try:
        # Load chat history safely
        with open(chatlog_path, "r") as f:
            content = f.read().strip()
            message = json.loads(content) if content else []

    except json.JSONDecodeError:
        print("ChatLog.json is corrupted. Resetting file.")
        message = []
        with open(chatlog_path, "w") as f:
            json.dump([], f)

    # Append user query
    message.append({"role": "user", "content": Query})

    Answer = ""  # Initialize Answer

    try:
        # Generate completion using the model
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + message,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            stream=True  # Streaming response
        )

        # Handle streamed response properly
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content  # Corrected attribute access

        # Clean response
        Answer = Answer.replace("<\\s>", "").strip()

        # Append AI response to chat history
        message.append({"role": "assistant", "content": Answer})

        # Save updated chat history
        with open(chatlog_path, "w") as f:
            json.dump(message, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        error_message = f"Error in ChatBot function: {e}"
        print(error_message)
        return "An error occurred. Please try again."

# Main loop
if __name__ == "__main__":
    while True:
        try:
            user_input = input("Enter Your Question: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting chat...")
                break
            print(ChatBot(user_input))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
