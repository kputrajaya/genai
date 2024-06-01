import json

from dotenv import load_dotenv
from openai import OpenAI

from package import tools


load_dotenv()
client = OpenAI()
model = 'gpt-3.5-turbo'
temperature = 0
tools_def = [
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
          'location': {'type': 'string', 'description': 'The city and state, e.g. San Francisco, CA'},
        },
        'required': ['location'],
      },
    },
  },
]
tools_map = {
  'get_current_weather': tools.get_current_weather,
  'get_top_songs': tools.get_top_songs,
}


def run_conversation(prompt):
  # Generate first response
  messages = [{'role': 'user', 'content': prompt}]
  response = client.chat.completions.create(
      model=model,
      temperature=temperature,
      messages=messages,
      tools=tools_def,
      tool_choice='auto',
  )
  response_message = response.choices[0].message
  messages.append(response_message)

  # No tools invoked
  if not response_message.tool_calls:
    return messages

  # Invoke tools
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
    temperature=temperature,
    messages=messages,
  )
  second_response_message = second_response.choices[0].message
  messages.append(second_response_message)

  return messages


# Run predefined prompts
prompts = [line for line in open('prompts.txt', 'r') if line]
for index, prompt in enumerate(prompts):
  messages = run_conversation(prompt)
  print(f'#{index + 1}: {prompt}')
  print(f'{messages[len(messages) - 1].content}')
  print('---')
