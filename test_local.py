import requests

url = "https://a81dd2665663a5d36c.gradio.live/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

history = []

while True:
    user_message = input("> ")
    history.append({"role": "user", "content": user_message})
    data = {
        "mode": "chat",
        "character": "Example",
        "messages": history
    }

    response = requests.post(url, headers=headers, json=data, verify=False)
    print(response)
    assistant_message = response.json()['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": assistant_message})
    print(assistant_message)