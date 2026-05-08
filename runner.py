import subprocess
import os
import sys

def run_app(file_path: str):
    """Ejecuta la aplicación de Streamlit en un proceso separado."""
    try:
        if sys.platform == "win32":
            # En Windows usamos CREATE_NEW_CONSOLE para que se vea la terminal si se desea,
            # o simplemente Popen para que corra en segundo plano.
            subprocess.Popen(
                ["streamlit", "run", file_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            subprocess.Popen(
                ["streamlit", "run", file_path],
                start_new_session=True
            )
        return True, "Lanzando aplicación..."
    except Exception as e:
        return False, str(e)

def save_app(codigo: str, nombre: str) -> str:
    """Guarda el código en la carpeta de apps generadas."""
    os.makedirs("apps_generadas", exist_ok=True)
    # Sanitizar nombre
    nombre = nombre.strip().replace(" ", "_").replace(".py", "") + ".py"
    ruta = os.path.join("apps_generadas", nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(codigo)
    return ruta
