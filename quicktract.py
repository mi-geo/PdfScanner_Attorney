from openai import OpenAI
client = OpenAI()
OPENAI_API_KEY = "my_key"
response = client.responses.create(
    model="gpt-5.2",
    input="Write a short bedtime story about a unicorn."
)

print(response.output_text)

import os
os.environ.get("OPENAI_API_KEY")
os.environ

import sys
sys.executable