import ast
import sys
import subprocess
import os

def detectar_dependencias(codigo: str) -> list[str]:
    """Detecta imports del código y filtra los de la stdlib."""
    try:
        tree = ast.parse(codigo)
    except SyntaxError:
        return []
        
    imports = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    # Excluir stdlib y módulos propios
    stdlib = set(sys.stdlib_module_names)
    externos = imports - stdlib - {'streamlit', '__future__'}
    
    # Mapeo de nombres de import a nombres de paquete pip
    NOMBRE_PAQUETE = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'sklearn': 'scikit-learn',
        'bs4': 'beautifulsoup4',
        'yaml': 'PyYAML',
        'dotenv': 'python-dotenv',
        'dateutil': 'python-dateutil',
        'plotly': 'plotly',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'requests': 'requests',
        'yfinance': 'yfinance',
    }
    
    return [NOMBRE_PAQUETE.get(lib, lib) for lib in externos]

def instalar_dependencias(paquetes: list[str]):
    """Instala los paquetes usando pip."""
    resultados = {}
    for paquete in paquetes:
        try:
            resultado = subprocess.run(
                [sys.executable, "-m", "pip", "install", paquete],
                capture_output=True, text=True, check=False
            )
            resultados[paquete] = {
                "exito": resultado.returncode == 0,
                "output": resultado.stdout,
                "error": resultado.stderr
            }
        except Exception as e:
            resultados[paquete] = {
                "exito": False,
                "output": "",
                "error": str(e)
            }
    return resultados

def validar_codigo(codigo: str) -> tuple[bool, str]:
    """Valida si el código tiene errores de sintaxis."""
    try:
        ast.parse(codigo)
        return True, "✅ Sintaxis válida"
    except SyntaxError as e:
        return False, f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}"
