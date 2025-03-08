from google import genai

# Create a Gemini client instance for reuse
client = genai.Client(api_key='KEY_HERE')

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Hello, world!",
)

print(response.text)