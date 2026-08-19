from google import genai


def gemini(prompt: str):
    API_KEY = ""
    client = genai.Client(api_key=API_KEY)
    try:
        # Usamos 'gemini-3.5-flash'
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        print("¡Conexión Exitosa!\n")
        return response.text

    except Exception as e:
        return f"Existe un error con gemini. Intentalo mas tarde {e}"
