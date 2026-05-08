import streamlit as st
import os
from generator import generate_code
from dependency_manager import detectar_dependencias, instalar_dependencias, validar_codigo
from runner import save_app, run_app

# Configuración de la página
st.set_page_config(page_title="StreamlitForge", page_icon="⚡", layout="wide")

# Inicialización del estado de la sesión
if "historial" not in st.session_state:
    st.session_state.historial = []
if "codigo_actual" not in st.session_state:
    st.session_state.codigo_actual = ""
if "iteracion" not in st.session_state:
    st.session_state.iteracion = 0
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "nombre_archivo" not in st.session_state:
    st.session_state.nombre_archivo = "mi_app_generada"
if "status_dependencias" not in st.session_state:
    st.session_state.status_dependencias = {}

# Sidebar
with st.sidebar:
    st.title("⚡ StreamlitForge")
    st.markdown("---")
    
    descripcion = st.text_area(
        "Describe tu app:",
        placeholder="Ej: Quiero una app que lea un CSV y me muestre un dashboard con gráficas de barras y una tabla filtrable por columna...",
        height=200
    )
    
    nombre_archivo = st.text_input("Nombre del archivo:", value=st.session_state.nombre_archivo)
    if nombre_archivo != st.session_state.nombre_archivo:
        st.session_state.nombre_archivo = nombre_archivo

    # Manejo de API Key (Solo OpenRouter)
    secrets_key = st.secrets.get("OPENROUTER_API_KEY", "")

    if secrets_key:
        st.success("✅ API Key de OpenRouter detectada en secrets")
        st.session_state.api_key = secrets_key
    else:
        api_key_manual = st.text_input("OpenRouter API Key:", type="password", value=st.session_state.api_key)
        if api_key_manual:
            st.session_state.api_key = api_key_manual

    if st.button("🔨 Generar aplicación", use_container_width=True):
        if not descripcion:
            st.warning("Por favor describe la aplicación.")
        elif not st.session_state.api_key:
            st.warning("Por favor ingresa tu API Key de OpenRouter o configúrala en secrets.")
        else:
            with st.spinner("Generando código con Gemini 3.1 Flash-Lite..."):
                codigo = generate_code(descripcion, st.session_state.api_key)
                if codigo:
                    st.session_state.codigo_actual = codigo
                    st.session_state.iteracion += 1
                    # Validar y detectar dependencias
                    es_valido, msg = validar_codigo(codigo)
                    if es_valido:
                        deps = detectar_dependencias(codigo)
                        st.session_state.deps_detectadas = deps
                        # No instalamos automáticamente para dar control, o podemos hacerlo
                        st.session_state.status_dependencias = {d: "⏳ Pendiente" for d in deps}
                    else:
                        st.error(msg)

# Panel Principal
if st.session_state.codigo_actual:
    tab1, tab2, tab3, tab4 = st.tabs(["💻 Código generado", "📦 Dependencias", "📟 Consola", "🚀 Vista previa"])
    
    with tab1:
        st.subheader("Editor de Código")
        try:
            from streamlit_ace import st_ace
            nuevo_codigo = st_ace(
                value=st.session_state.codigo_actual,
                language="python",
                theme="monokai",
                key="editor"
            )
        except ImportError:
            nuevo_codigo = st.text_area("Código (Instala streamlit-ace para resaltado):", value=st.session_state.codigo_actual, height=400)
            st.info("Tip: pip install streamlit-ace para una mejor experiencia de edición.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Guardar cambios"):
                st.session_state.codigo_actual = nuevo_codigo
                st.success("Cambios guardados localmente.")
        with col2:
            if st.button("🔄 Validar Sintaxis"):
                valido, msg = validar_codigo(nuevo_codigo)
                if valido: st.success(msg)
                else: st.error(msg)

    with tab2:
        st.subheader("Gestión de Librerías")
        deps = detectar_dependencias(st.session_state.codigo_actual)
        if deps:
            st.write("Librerías externas detectadas:")
            for d in deps:
                status = st.session_state.status_dependencias.get(d, "⏳ Detectada")
                st.write(f"- {d}: {status}")
            
            if st.button("📥 Instalar dependencias detectadas"):
                with st.status("Instalando paquetes...", expanded=True) as status_box:
                    resultados = instalar_dependencias(deps)
                    for pkg, res in resultados.items():
                        if res["exito"]:
                            st.session_state.status_dependencias[pkg] = "✅ Instalada"
                            st.write(f"✅ {pkg} instalada correctamente")
                        else:
                            st.session_state.status_dependencias[pkg] = "❌ Error"
                            st.write(f"❌ Error instalando {pkg}")
                    status_box.update(label="Instalación completada", state="complete")
        else:
            st.info("No se detectaron dependencias externas adicionales.")

    with tab3:
        st.subheader("Salida de Instalación / Errores")
        if "resultados" in locals():
            for pkg, res in resultados.items():
                st.markdown(f"**{pkg}**")
                if res["output"]: st.code(res["output"])
                if res["error"]: st.code(res["error"], language="bash")
        else:
            st.write("La consola está vacía.")

    with tab4:
        st.subheader("Ejecución")
        ruta = save_app(st.session_state.codigo_actual, st.session_state.nombre_archivo)
        
        col_exec, col_dl = st.columns(2)
        
        with col_exec:
            st.markdown("### 🚀 Ejecución Local")
            st.info("Este botón solo funciona si estás corriendo StreamlitForge localmente.")
            if st.button("▶️ Ejecutar aplicación", type="primary", use_container_width=True):
                exito, msg = run_app(ruta)
                if exito:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(f"Error al ejecutar: {msg}")
        
        with col_dl:
            st.markdown("### 📥 Descargar")
            st.info("Usa este botón si estás en Streamlit Cloud o quieres llevarte el archivo.")
            st.download_button(
                label="💾 Descargar archivo .py",
                data=st.session_state.codigo_actual,
                file_name=st.session_state.nombre_archivo + ".py",
                mime="text/x-python",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("""
        ### Cómo correr tu app descargada:
        1. Instala streamlit: `pip install streamlit`
        2. Instala las dependencias necesarias (ver pestaña **📦 Dependencias**)
        3. Ejecuta: `streamlit run {nombre}.py`
        """.format(nombre=st.session_state.nombre_archivo))

    # Ciclo de refinamiento
    st.markdown("---")
    st.subheader("¿Qué ajustes quieres hacerle?")
    cambio = st.text_input("Describe el cambio (ej: 'Agrega un botón para exportar a Excel')", key="input_refinamiento")
    if st.button("🚀 Aplicar cambio"):
        if not cambio:
            st.warning("Describe qué quieres cambiar.")
        else:
            with st.spinner("Refinando código con Gemini 3.1 Flash-Lite..."):
                nuevo_codigo = generate_code(cambio, st.session_state.api_key, current_code=st.session_state.codigo_actual)
                if nuevo_codigo:
                    st.session_state.codigo_actual = nuevo_codigo
