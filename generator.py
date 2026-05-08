import os
import streamlit as st
from openai import OpenAI

SYSTEM_PROMPT = """Eres un experto desarrollador de aplicaciones Streamlit. 
Tu única salida es código Python puro, sin explicaciones, sin bloques markdown, sin texto antes o después del código.

REGLAS DE GENERACIÓN:
1. Siempre incluye `import streamlit as st` al inicio
2. Usa `st.set_page_config(page_title="...", layout="wide")` como primera línea ejecutable
3. Organiza la UI con sidebar para controles y área principal para resultados
4. Incluye manejo de errores con `st.error()` para inputs inválidos
5. Si el usuario pide leer archivos, usa `st.file_uploader()`
6. Si necesitas datos de ejemplo, GENERA datos sintéticos realistas con Python puro (no uses datasets externos que requieran descarga)
7. Incluye `st.spinner()` en operaciones que puedan tardar
8. Agrega docstring al inicio del archivo explicando qué hace la app
9. El código debe funcionar al correr `streamlit run archivo.py` sin configuración adicional
10. MANEJO DE API KEYS: Si la app requiere una API key (OpenAI, OpenRouter, etc.), intenta leerla de `st.secrets`. Si no existe, DEBES incluir un `st.sidebar.text_input(..., type="password")` para que el usuario la ingrese manualmente y usar ese valor. NUNCA la dejes hardcodeada.

FORMATO DE RESPUESTA:
Solo código Python. Nada más.
"""

def generate_code(prompt: str, api_key: str, current_code: str = "") -> str:
    """Llama a OpenRouter (Gemini 3.1 Flash-Lite) para generar o modificar el código."""
    
    if current_code:
        user_message = f"CÓDIGO ACTUAL:\n{current_code}\n\nCAMBIO SOLICITADO:\n{prompt}\n\nModifica el código para incorporar el cambio. Devuelve el código completo modificado, no solo el fragmento cambiado."
    else:
        user_message = f"Crea una aplicación Streamlit que haga lo siguiente:\n\n{prompt}\n\nGenera el código completo y funcional."

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        response = client.chat.completions.create(
            model="google/gemini-3.1-flash-lite",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            extra_headers={
                "HTTP-Referer": "https://streamlitforge.com",
                "X-Title": "StreamlitForge",
            }
        )
        code = response.choices[0].message.content

        # Limpiar markdown si el LLM ignoró las instrucciones
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
            
        return code.strip()
    except Exception as e:
        st.error(f"Error llamando a la API de OpenRouter: {str(e)}")
        return ""
