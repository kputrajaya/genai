import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI()
model = 'gpt-3.5-turbo'


def get_top_songs():
    return json.dumps([
        {'rank': 1, 'artist': ['Sabrina Carpenter'], 'title': 'Espresso'},
        {'rank': 2, 'artist': ['Tommy Richman'], 'title': 'MILLION DOLLAR BABY'},
        {'rank': 3, 'artist': ['Billie Eilish'], 'title': 'LUNCH'},
        {'rank': 4, 'artist': ['Kendrick Lamar'], 'title': 'Not Like Us'},
        {'rank': 5, 'artist': ['Billie Eilish'], 'title': 'Birds of a Feather'},
        {'rank': 6, 'artist': ['FlyyMenor', 'Cris Mj'], 'title': 'Gata Only'},
        {'rank': 7, 'artist': ['Post Malone', 'Morgan Wallen'], 'title': 'I Had Some Help (Feat. Morgan Wallen)'},
        {'rank': 8, 'artist': ['Hozier'], 'title': 'Too Sweet'},
        {'rank': 9, 'artist': ['Benson Boone'], 'title': 'Beautiful Things'},
        {'rank': 10, 'artist': ['Billie Eilish'], 'title': 'CHIHIRO'},
    ])


def get_current_weather(location):
    location_lower = location.lower()
    if 'tokyo' in location_lower:
        return json.dumps({'location': 'Tokyo', 'temperature': '10F'})
    elif 'san francisco' in location_lower:
        return json.dumps({'location': 'San Francisco', 'temperature': '82F'})
    elif 'paris' in location_lower:
        return json.dumps({'location': 'Paris', 'temperature': '22F'})
    else:
        return json.dumps({'location': location, 'temperature': None})


def run_conversation(prompt):
    # Generate first response
    messages = [{'role': 'user', 'content': prompt}]
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=messages,
        tools=[
            {
                'type': 'function',
                'function': {
                    'name': 'get_top_songs',
                    'description': 'Get top played songs globally from Spotify',
                },
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_current_weather',
                    'description': 'Get the current weather in a given location',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'location': {'type': 'string', 'description': 'The city or state, e.g. San Francisco'},
                        },
                        'required': ['location'],
                    },
                },
            },
        ],
        tool_choice='auto',
    )
    response_message = response.choices[0].message
    messages.append(response_message)

    # Return if no tools invoked
    if not response_message.tool_calls:
        return messages

    # Invoke tools
    tools_map = {
        'get_current_weather': get_current_weather,
        'get_top_songs': get_top_songs,
    }
    for tool_call in response_message.tool_calls:
        fn_name = tool_call.function.name
        fn_args = json.loads(tool_call.function.arguments)
        fn_response = tools_map[fn_name](**fn_args)
        messages.append({
            'role': 'tool',
            'tool_call_id': tool_call.id,
            'name': fn_name,
            'content': fn_response,
        })

    # Generate second (final) response
    second_response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=messages,
    )
    second_response_message = second_response.choices[0].message
    messages.append(second_response_message)

    return messages


# Run predefined prompts
prompts = [line.strip() for line in open('prompts.txt', 'r') if line]
for index, prompt in enumerate(prompts):
    messages = run_conversation(prompt)
    print(f'{index + 1}. {prompt}')
    print(f'{messages[len(messages) - 1].content}')
    print('---')
