"""
Script para generar imágenes de mapas para la documentación de geodompy.
Ejecutar desde la raíz del proyecto: python docs/scripts/generate_map_images.py
"""
import os
import sys

# Añadir el directorio raíz al path para importar geodompy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import pandas as pd
import geodompy as gd

# Directorio de salida para las imágenes
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'maps')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_fig(name: str, dpi: int = 150):
    """Guardar figura actual y cerrar."""
    path = os.path.join(OUTPUT_DIR, f'{name}.png')
    plt.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Generada: {path}")

def main():
    print("Generando imágenes de mapas para documentación...")
    print("-" * 50)
    
    # 1. Mapa básico con datos de provincias - autodetección de fill
    datos_prov = pd.DataFrame({
        'provincia': ['Santo Domingo', 'Santiago', 'La Vega', 'Puerto Plata', 
                      'San Cristóbal', 'La Romana'],
        'poblacion': [2500000, 1000000, 400000, 350000, 550000, 250000]
    })
    
    # Sin especificar fill - se detecta automáticamente
    gd.map(datos_prov)
    save_fig('basic_map')
    
    # 2. Mapa personalizado con paleta de colores
    gd.map(
        datos_prov,
        fill='poblacion',
        cmap='YlOrRd',
        title='Población por Provincia',
        figsize=(12, 10),
        edgecolor='black',
        linewidth=0.5
    )
    save_fig('custom_map')
    
    # 3. Mapa con datos categóricos
    datos_cat = pd.DataFrame({
        'provincia': ['Santo Domingo', 'Santiago', 'La Vega', 'Puerto Plata'],
        'categoria': ['Alta', 'Alta', 'Media', 'Baja']
    })
    
    gd.map(datos_cat, fill='categoria', cmap='Set2')
    save_fig('categorical_map')
    
    # 4. Mapa con map_data() y matplotlib - también autodetecta
    map_df = gd.map_data(datos_prov)
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    map_df.plot(
        column='poblacion',
        ax=ax,
        cmap='Blues',
        legend=True
    )
    ax.set_title('Población por Provincia (usando map_data)', fontsize=14)
    ax.axis('off')
    plt.tight_layout()
    save_fig('map_data_example')
    
    print("-" * 50)
    print("¡Todas las imágenes generadas correctamente!")

if __name__ == '__main__':
    main()
