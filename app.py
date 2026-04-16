import streamlit as st
import streamlit.components.v1 as components
import json
import os

# Configuración inicial de la página
st.set_page_config(layout="wide", page_title="SGA - Proceso HCl", page_icon="🏭")

st.title("Sistema de Gestión Ambiental: Proceso HCl (Sección 2)")
st.markdown("Haz clic sobre los equipos resaltados en el diagrama para consultar su matriz de aspectos ambientales, normas aplicables y análisis de riesgos.")

# 1. Base de Datos del Sistema de Gestión (SGA)
# IMPORTANTE: Las claves ("B-110", "C-110") DEBEN coincidir exactamente con los atributos 'id' dentro de tu archivo diagrama.svg (<g id="C-110">)
db_sga = {
    "C-110": {
        "equipo": "Intercambiador de Calor C-110",
        "aspecto_ambiental": "Potencial fuga de gases ácidos (Cl2/HCl) a la atmósfera.",
        "normas_aplicables": "NOM-028-STPS-2012, NOM-010-STPS-2014",
        "what_if": "¿Qué pasa si hay ruptura de tubos? -> Contaminación cruzada y presurización. Salvaguarda: PSV y sistema de enclavamiento."
    },
    "B-110": {
        "equipo": "Tanque de Almacenamiento B-110",
        "aspecto_ambiental": "Riesgo de derrame de solución ácida al suelo.",
        "normas_aplicables": "NOM-005-STPS-1998, NOM-052-SEMARNAT-2005",
        "what_if": "¿Qué pasa si falla el control de nivel? -> Derrame. Salvaguarda: Dique de contención y alarma de alto nivel (LAHH)."
    },
    "W-110": {
        "equipo": "Columna / Lavador W-110",
        "aspecto_ambiental": "Generación de efluentes líquidos corrosivos.",
        "normas_aplicables": "NOM-001-SEMARNAT-2021",
        "what_if": "¿Qué pasa si se interrumpe el flujo de agua? -> Emisión de gases no tratados. Salvaguarda: Válvula de falla abierta y enclavamiento de bomba."
    }
    # Agrega el resto de tus equipos e instrumentos aquí...
}

# 2. Carga del archivo SVG
svg_path = "diagrama.svg"

try:
    with open(svg_path, "r", encoding="utf-8") as file:
        svg_content = file.read()
except FileNotFoundError:
    st.error(f"Error: No se encontró el archivo '{svg_path}' en el directorio. Asegúrate de subirlo a GitHub.")
    st.stop()

# 3. Inyección de HTML, CSS y JavaScript
# Convertimos el diccionario de Python a JSON para que JS pueda leerlo
sga_json = json.dumps(db_sga)

# Creamos un bloque HTML que contiene el SVG y la lógica interactiva
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Contenedor relativo para posicionar el tooltip */
        .svg-container {{
            position: relative;
            width: 100%;
            height: 800px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: white;
            overflow: auto;
        }}
        
        /* Estilos base para el SVG */
        svg {{
            width: 100%;
            height: 100%;
        }}

        /* Estilo para los equipos que tienen datos (cursor interactivo) */
        .interactivo {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .interactivo:hover {{
            filter: drop-shadow(0px 0px 8px rgba(0, 114, 206, 0.8));
            opacity: 0.8;
        }}

        /* Diseño del Tooltip (Tarjeta de información flotante) */
        #sga-tooltip {{
            position: absolute;
            display: none;
            background-color: rgba(255, 255, 255, 0.95);
            border-left: 5px solid #005A9C;
            padding: 15px;
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            pointer-events: none; /* Evita que el tooltip interfiera con los clicks */
            font-family: Arial, sans-serif;
            font-size: 14px;
            max-width: 350px;
            z-index: 1000;
        }}
        
        .tooltip-title {{ font-weight: bold; font-size: 16px; color: #333; margin-bottom: 8px; border-bottom: 1px solid #ccc; padding-bottom: 4px;}}
        .tooltip-section {{ margin-bottom: 6px; }}
        .tooltip-label {{ font-weight: bold; color: #555; }}
    </style>
</head>
<body>

    <div class="svg-container" id="container">
        <div id="sga-tooltip"></div>
        
        {svg_content}
    </div>

    <script>
        // Cargar los datos desde Python
        const sgaData = {sga_json};
        const tooltip = document.getElementById('sga-tooltip');
        const container = document.getElementById('container');

        // Iterar sobre los datos y buscar los elementos SVG por ID
        Object.keys(sgaData).forEach(id => {{
            const element = document.getElementById(id);
            if (element) {{
                // Añadir clase para estilos CSS
                element.classList.add('interactivo');

                // Evento al pasar el mouse (Click opcional, hover es más amigable en P&IDs)
                element.addEventListener('click', (e) => {{
                    const data = sgaData[id];
                    
                    // Construir el contenido HTML de la tarjeta
                    tooltip.innerHTML = `
                        <div class="tooltip-title">${{data.equipo}}</div>
                        <div class="tooltip-section"><span class="tooltip-label">Aspecto Ambiental:</span> ${{data.aspecto_ambiental}}</div>
                        <div class="tooltip-section"><span class="tooltip-label">Normativas:</span> ${{data.normas_aplicables}}</div>
                        <div class="tooltip-section"><span class="tooltip-label">Análisis What-If:</span> ${{data.what_if}}</div>
                    `;
                    
                    // Mostrar y posicionar el tooltip cerca del cursor
                    tooltip.style.display = 'block';
                    
                    // Ajuste de coordenadas relativas al contenedor
                    const rect = container.getBoundingClientRect();
                    let x = e.clientX - rect.left + 15;
                    let y = e.clientY - rect.top + 15;
                    
                    tooltip.style.left = x + 'px';
                    tooltip.style.top = y + 'px';
                }});
                
                // Ocultar al mover el mouse fuera del equipo
                element.addEventListener('mouseleave', () => {{
                    tooltip.style.display = 'none';
                }});
            }}
        }});
    </script>
</body>
</html>
"""

# 4. Renderizar el componente en Streamlit
components.html(html_code, height=850, scrolling=False)
