from google import genai
from google.genai import types


client = genai.Client(
    api_key="AIzaSyCn5ubu9I3LxuAksQBOzhv3ztuohKVrb1Q"
)

response =client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="{system_instruction}"),

        contents="{contents}"
    
)
print(response.text)

