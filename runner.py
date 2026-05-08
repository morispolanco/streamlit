import subprocess
import os
import sys

def run_app(file_path: str):
    """Ejecuta la aplicación de Streamlit en un proceso separado."""
    # Asegurar ruta absoluta
    file_path = os.path.abspath(file_path)
    
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", file_path]
        
        if sys.platform == "win32":
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            subprocess.Popen(
                cmd,
                start_new_session=True
            )
        return True, f"Lanzando aplicación: {os.path.basename(file_path)}"
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
