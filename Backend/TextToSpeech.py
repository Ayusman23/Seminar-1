import pygame
import asyncio
import edge_tts
import os
import random
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-JennyNeural")  # ✅ Default voice if not set

pygame.init()

async def TextToAudioFile(text) -> str:
    """Generate an audio file from text using edge_tts."""
    file_path = os.path.abspath("Data/speech.mp3")

    if os.path.exists(file_path):
        os.remove(file_path)

    try:
        print("[DEBUG] Generating speech...")  # ✅ Debugging
        communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
        await communicate.save(file_path)

        while not os.path.exists(file_path):
            await asyncio.sleep(0.1)

        print(f"[DEBUG] Speech file created: {file_path}")  # ✅ Debugging
        return file_path

    except Exception as e:
        print(f"[ERROR] TTS generation failed: {e}")
        return ""



def play_audio(file_path):
    """Play the generated audio file."""
    if not os.path.exists(file_path):
        print(f"[ERROR] Audio file not found: {file_path}")
        return

    try:
        pygame.mixer.quit()
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        print("[DEBUG] Playing audio...")  # ✅ Debugging
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except pygame.error as e:
        print(f"[ERROR] Pygame error: {e}")

    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()



def TTS(text):
    """Convert text to speech synchronously."""
    try:
        print(f"[DEBUG] TTS received text: {text}")  # ✅ Debugging
        file_path = asyncio.run(TextToAudioFile(text))
        
        if file_path and os.path.exists(file_path):
            print(f"[DEBUG] Speech file generated: {file_path}")  # ✅ Debugging
            play_audio(file_path)
        else:
            print("[ERROR] Speech file not generated.")

    except Exception as e:
        print(f"[ERROR] TTS Failed: {e}")


if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        TTS(user_input)
