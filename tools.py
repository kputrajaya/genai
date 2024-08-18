import json

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI()
model = 'gpt-4o-mini'


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
prompts = [
    'What does "kaikaku" mean?',
    'How\'s the weather today?',
    'Is it hot in Tokyo?',
    'What\'s the weather like in London, Jakarta, and Paris?',
    'What\'s the weather like in SF?',
    'What\'s the weather like in SF in Celcius?',
    'What are the top 5 trending songs right now?',
    'Who\'s the top artist in the Spotify leaderboard?',
    'Who has the most songs in the top 10 global songs - how many?',
    'I\'m coming to SF today - what\'s the weather like and what songs should I listen to?',
]
for index, prompt in enumerate(prompts):
    messages = run_conversation(prompt)
    print(f'{index + 1}. {prompt}')
    print(f'{messages[len(messages) - 1].content}')
    print('---')


"""
1. What does "kaikaku" mean?
"Kaikaku" is a Japanese term that translates to "reform" or "radical change." It is often used in the context of
significant transformations in processes, systems, or organizations, particularly in business and management. The term
is associated with the idea of making substantial improvements or overhauls rather than incremental changes. In the
context of lean manufacturing and management, "kaikaku" is contrasted with "kaizen," which refers to continuous,
incremental improvement.
---
2. How's the weather today?
Could you please provide me with the name of the city or location for which you would like to know the weather?
---
3. Is it hot in Tokyo?
Currently, it is 10°F in Tokyo, which is quite cold. If you're looking for hot weather, it seems like you'll need to
wait for a warmer season!
---
4. What's the weather like in London, Jakarta, and Paris?
I currently don't have the exact temperature for London and Jakarta, but I do have that the temperature in Paris is
22°F. If you need more detailed weather information, I recommend checking a reliable weather website or app for the
latest updates.
---
5. What's the weather like in SF?
The current weather in San Francisco is 82°F.
---
6. What's the weather like in SF in Celcius?
The current temperature in San Francisco is approximately 28°C.
---
7. What are the top 5 trending songs right now?
Here are the top 5 trending songs right now:

1. **"Espresso"** by Sabrina Carpenter
2. **"MILLION DOLLAR BABY"** by Tommy Richman
3. **"LUNCH"** by Billie Eilish
4. **"Not Like Us"** by Kendrick Lamar
5. **"Birds of a Feather"** by Billie Eilish
---
8. Who's the top artist in the Spotify leaderboard?
As of now, the top artist on the Spotify leaderboard is Sabrina Carpenter, with her song "Espresso" ranking first.
---
9. Who has the most songs in the top 10 global songs - how many?
Billie Eilish has the most songs in the top 10 global songs, with a total of 3 songs. The titles are:

1. "LUNCH" (Rank 3)
2. "Birds of a Feather" (Rank 5)
3. "CHIHIRO" (Rank 10)
---
10. I'm coming to SF today - what's the weather like and what songs should I listen to?
Welcome to San Francisco! The weather today is quite warm, with a temperature of 82°F.

As for music, here are some top songs you might enjoy listening to while you're in the city:

1. **Sabrina Carpenter** - "Espresso"
2. **Tommy Richman** - "MILLION DOLLAR BABY"
3. **Billie Eilish** - "LUNCH"
4. **Kendrick Lamar** - "Not Like Us"
5. **Billie Eilish** - "Birds of a Feather"
6. **FlyyMenor & Cris Mj** - "Gata Only"
7. **Post Malone & Morgan Wallen** - "I Had Some Help (Feat. Morgan Wallen)"
8. **Hozier** - "Too Sweet"
9. **Benson Boone** - "Beautiful Things"
10. **Billie Eilish** - "CHIHIRO"

Enjoy your time in San Francisco and have a great day!
---
"""
