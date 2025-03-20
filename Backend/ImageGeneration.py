import tensorflow.lite as tflite
import numpy as np
import cv2  # If you're processing images
import os
import asyncio
import requests
from dotenv import load_dotenv
from random import randint
from io import BytesIO
from PIL import Image

# ✅ Load environment variables
load_dotenv()

# ✅ Ensure the Data folder exists
os.makedirs("Data", exist_ok=True)

# ✅ API Details
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_KEY = os.getenv("HuggingFaceAPIKey")  # Ensure this is set in your .env file

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ✅ Debugging: Ensure API Key is loaded
if not API_KEY:
    print("[ERROR] API key is missing. Check your .env file.")
    exit(1)

# ✅ Load the TensorFlow Lite model
interpreter = tflite.Interpreter(model_path="your_model.tflite")

# ✅ Allocate tensors
interpreter.allocate_tensors()

# ✅ Fix dynamic tensor issue
input_details = interpreter.get_input_details()
for i in range(len(input_details)):
    shape = input_details[i]['shape']
    if -1 in shape:  # Check for dynamic tensors
        shape = [1 if dim == -1 else dim for dim in shape]  # Replace -1 with static size (1)
        interpreter.resize_tensor_input(input_details[i]['index'], shape)

# ✅ Reallocate tensors after resizing
interpreter.allocate_tensors()
print("[INFO] Model loaded successfully, ready to generate images.")

async def query(payload):
    """Sends a request to Hugging Face API asynchronously and ensures response is valid."""
    try:
        print(f"[INFO] Sending request to API: {payload}")
        response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            print("[INFO] Image generated successfully!")
            return response.content  # ✅ FIX: Ensure this is image data
        elif response.status_code == 400:
            print("[ERROR] Bad request. Check if the prompt is valid.")
        elif response.status_code == 403:
            print("[ERROR] Authentication failed. Check your API key or model access.")
        elif response.status_code == 429:
            print("[ERROR] Rate limit exceeded. Retrying in 10 seconds...")
            await asyncio.sleep(10)
            return await query(payload)  # Retry request
        else:
            print(f"[ERROR] Failed to fetch image. Status Code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
    
    return None

async def generate_image(prompt: str):
    """Generates an image using Hugging Face API and saves it properly."""
    payload = {"inputs": prompt}

    print(f"[INFO] Requesting image generation for: {prompt}")
    image_data = await query(payload)

    if image_data:
        filename = f"Data/{prompt.replace(' ', '_')}_{randint(1000, 9999)}.jpg"

        # ✅ FIX: Ensure the response is actually an image
        try:
            image = Image.open(BytesIO(image_data))
            image.save(filename)
            print(f"[INFO] Image saved: {filename}")
            return filename
        except Exception as e:
            print(f"[ERROR] Failed to process image: {e}")
            return None
    else:
        print("[ERROR] No image data received.")
        return None

def open_image(image_path):
    """Opens the generated image immediately after creation."""
    try:
        img = Image.open(image_path)
        print(f"[INFO] Opening image: {image_path}")
        img.show()  # ✅ Opens the image automatically
    except IOError:
        print(f"[ERROR] Unable to open {image_path}")

async def GenerateImage(prompt: str):
    """Runs the image generation process asynchronously and then opens the image."""
    image_path = await generate_image(prompt)
    if image_path:
        open_image(image_path)  # ✅ Opens the image automatically

async def monitor_file():
    """Continuously monitors the file for changes and triggers image generation."""
    file_path = r"Frontend/Files/ImageGeneration.data"

    while True:
        try:
            if not os.path.exists(file_path):
                await asyncio.sleep(1)
                continue

            with open(file_path, "r") as f:
                data = f.read().strip()

            if not data or data == "False,False":
                await asyncio.sleep(1)
                continue

            Prompt, Status = data.split(",")

            if Status == "True":
                print(f"[INFO] Generating Image for: {Prompt}")
                await GenerateImage(prompt=Prompt)

                # ✅ Reset the file so it can receive new requests
                with open(file_path, "w") as f:
                    f.write("False,False")
                print("[INFO] Image generation complete. Waiting for new requests.")

            await asyncio.sleep(1)

        except Exception as e:
            print(f"[ERROR] Exception in file monitoring: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(monitor_file())
