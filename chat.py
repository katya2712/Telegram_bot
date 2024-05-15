import os

from groq import Groq

# Глубина контекста в диалоге с ботом
# 13 это 6 пар вопрос-ответ и текущий вопрос
CONTEXT_LENGTH = 13

# Персонификация бота
ROLE = [{'role': 'system',
         'content': 'Ты говоришь на русском языке'}]

if os.getenv('RELEASE') is not None:
    GROQ_KEY = os.environ['GROQ_KEY']
else:
    with open('secrets/groq.key') as file:
        GROQ_KEY = file.readline()

client = Groq(api_key=GROQ_KEY)


def get_response(messages: list):
    if len(messages) > CONTEXT_LENGTH:
        messages = messages[-CONTEXT_LENGTH:]
    print(messages)
    response = client.chat.completions.create(model='llama3-70b-8192',
                                              messages=ROLE + messages,
                                              temperature=0)
    messages.append({"role": 'assistant', "content": response.choices[0].message.content})
    return messages
