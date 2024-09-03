from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
client = OpenAI()
model = 'gpt-4o-mini'


def extract():
    system_prompt = """
      You are a receipt parser. This is an image of a receipt, with item breakdowns and grand totals at the bottom.
      You need to extract the total amount and the list of prices for each item line. Return it as a JSON object.
    """
    image_url = 'https://media-cdn.tripadvisor.com/media/photo-s/0b/ec/66/83/receipt-of-food-ordered.jpg'
    response = client.chat.completions.create(
      model=model,
      messages=[
        {
          'role': 'system',
          'content': system_prompt
        },
        {
          'role': 'user',
          'content': [
            {
              'type': 'image_url',
              'image_url': {
                'url': image_url,
              }
            },
          ],
        }
      ],
      response_format={
        'type': 'json_schema',
        'json_schema': {
          'name': 'receipt_response',
          'strict': True,
          'schema': {
            'type': 'object',
            'properties': {
              'total': {'type': 'number'},
              'items': {
                'type': 'array',
                'items': {'type': 'number'}
              }
            },
            'required': ['total', 'items'],
            'additionalProperties': False
          }
        }
      },
      max_tokens=1000
    )
    return response.choices[0].message.content


result = extract()
print(result)
