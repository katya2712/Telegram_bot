import os

from groq import Groq

CONTEXT_LENGTH = 6

if os.getenv('RELEASE') is not None:
    GROQ_KEY = os.environ['GROQ_KEY']
else:
    with open('secrets/groq.key') as file:
        GROQ_KEY = file.readline()

client = Groq(api_key=GROQ_KEY)


def get_response(messages):
    if len(messages) > CONTEXT_LENGTH:
        messages = messages[-CONTEXT_LENGTH:]
    response = client.chat.completions.create(model='llama3-70b-8192', messages=messages, temperature=0)
    return response
