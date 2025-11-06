"""
Wrapper simple para matplotlib que funciona con Kivy
Alternativa a kivy-garden.matplotlib
"""

from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO


class MatplotlibWidget(Image):
    """Widget simple que muestra un gráfico de matplotlib"""
    
    def __init__(self, figure, **kwargs):
        super().__init__(**kwargs)
        self.figure = figure
        self.draw()
    
    def draw(self):
        """Renderizar el gráfico como imagen"""
        # Guardar el gráfico en un buffer
        buf = BytesIO()
        self.figure.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Cargar como textura de Kivy
        core_image = CoreImage(buf, ext='png')
        self.texture = core_image.texture
        
        # Cerrar buffer
        buf.close()