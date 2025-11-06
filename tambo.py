"""
Módulo de gestión de producción tambera
Métricas de preñez, parición, destete, lactancia y producción
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.widget import Widget
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import ThreeLineListItem, MDList
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from kivy.clock import Clock
import database
from matplotlib_wrapper import MatplotlibWidget


class TamboMetricCard(MDCard):
    """Tarjeta de métrica tambera"""
    def __init__(self, titulo, valor, unidad="", color=(0.2, 0.6, 0.8, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(5)
        self.size_hint = (None, None)
        self.size = (dp(160), dp(120))
        self.elevation = 3
        self.md_bg_color = color
        
        titulo_lbl = MDLabel(
            text=titulo,
            halign='center',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style='Caption'
        )
        
        valor_lbl = MDLabel(
            text=str(valor),
            halign='center',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style='H4',
            bold=True
        )
        
        unidad_lbl = MDLabel(
            text=unidad,
            halign='center',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.7),
            font_style='Caption'
        )
        
        self.add_widget(titulo_lbl)
        self.add_widget(valor_lbl)
        self.add_widget(unidad_lbl)


class TamboScreen(MDScreen):
    """Pantalla de gestión de tambo"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'tambo'
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Gestión de Tambo",
            elevation=3,
            md_bg_color=(0.2, 0.6, 0.8, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # ScrollView
        scroll = ScrollView()
        self.content = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(15),
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        
        # Botones
        btn_box = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(10))
        
        btn_add = MDRaisedButton(
            text="Registrar Día",
            size_hint=(0.5, 1),
            on_press=self.show_add_dialog
        )
        
        btn_graph = MDRaisedButton(
            text="Ver Evolución",
            size_hint=(0.5, 1),
            on_press=self.show_evolution_graph
        )
        
        btn_box.add_widget(btn_add)
        btn_box.add_widget(btn_graph)
        self.content.add_widget(btn_box)
        
        # Métricas actuales
        self.metrics_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.metrics_container.bind(minimum_height=self.metrics_container.setter('height'))
        
        self.content.add_widget(self.metrics_container)
        
        # Historial
        titulo_historial = MDLabel(
            text="Historial de Registros",
            halign='left',
            font_style='H6',
            size_hint_y=None,
            height=dp(40)
        )
        self.content.add_widget(titulo_historial)
        
        self.historial_list = MDList()
        self.content.add_widget(self.historial_list)
        
        scroll.add_widget(self.content)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        self.load_tambo_data()
    
    def go_back(self):
        self.manager.current = 'dashboard'
    
    def load_tambo_data(self):
        """Cargar datos del tambo"""
        self.metrics_container.clear_widgets()
        self.historial_list.clear_widgets()
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Obtener último registro
        cursor.execute('SELECT * FROM tambo ORDER BY fecha DESC LIMIT 1')
        ultimo = cursor.fetchone()
        
        if ultimo:
            # Grid de métricas
            from kivy.uix.gridlayout import GridLayout
            
            grid1 = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(130))
            
            card1 = TamboMetricCard(
                "Producción Diaria",
                f"{ultimo['litros_producidos']:.0f}",
                "litros",
                (0.2, 0.7, 0.4, 1)
            )
            
            card2 = TamboMetricCard(
                "% Preñez",
                f"{ultimo['porcentaje_prenez']:.1f}",
                "%",
                (0.3, 0.6, 0.9, 1)
            )
            
            grid1.add_widget(card1)
            grid1.add_widget(card2)
            self.metrics_container.add_widget(grid1)
            
            grid2 = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(130))
            
            card3 = TamboMetricCard(
                "% Parición",
                f"{ultimo['porcentaje_paricion']:.1f}",
                "%",
                (0.9, 0.5, 0.2, 1)
            )
            
            card4 = TamboMetricCard(
                "% Destete",
                f"{ultimo['porcentaje_destete']:.1f}",
                "%",
                (0.6, 0.3, 0.8, 1)
            )
            
            grid2.add_widget(card3)
            grid2.add_widget(card4)
            self.metrics_container.add_widget(grid2)
            
            # Vacas en lactancia
            card5 = TamboMetricCard(
                "Vacas en Lactancia",
                f"{ultimo['vacas_lactancia']}",
                "cabezas",
                (0.2, 0.5, 0.7, 1)
            )
            card5.size_hint = (1, None)
            card5.height = dp(130)
            self.metrics_container.add_widget(card5)
        
        # Cargar historial
        cursor.execute('SELECT * FROM tambo ORDER BY fecha DESC LIMIT 10')
        registros = cursor.fetchall()
        
        for reg in registros:
            fecha_obj = datetime.strptime(reg['fecha'], '%Y-%m-%d')
            item = ThreeLineListItem(
                text=f"Producción: {reg['litros_producidos']:.0f} litros",
                secondary_text=f"Fecha: {fecha_obj.strftime('%d/%m/%Y')} | Vacas lactancia: {reg['vacas_lactancia']}",
                tertiary_text=f"Preñez: {reg['porcentaje_prenez']:.1f}% | Parición: {reg['porcentaje_paricion']:.1f}%"
            )
            self.historial_list.add_widget(item)
        
        if not registros:
            self.historial_list.add_widget(
                ThreeLineListItem(text="No hay registros de tambo")
            )
    
    def show_add_dialog(self, *args):
        """Mostrar diálogo para registrar día"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        content.add_widget(Widget(size_hint_y=None, height=dp(70)))
        
        self.litros_field = MDTextField(
            hint_text="Litros producidos",
            input_filter='float',
            size_hint_y=None,
            height=dp(50)
        )
        
        self.prenez_field = MDTextField(
            hint_text="% Preñez",
            input_filter='float',
            size_hint_y=None,
            height=dp(50)
        )
        
        self.paricion_field = MDTextField(
            hint_text="% Parición",
            input_filter='float',
            size_hint_y=None,
            height=dp(50)
        )
        
        self.destete_field = MDTextField(
            hint_text="% Destete",
            input_filter='float',
            size_hint_y=None,
            height=dp(50)
        )
        
        self.vacas_field = MDTextField(
            hint_text="Vacas en lactancia",
            input_filter='int',
            size_hint_y=None,
            height=dp(50)
        )
        
        self.observaciones_field = MDTextField(
            hint_text="Observaciones",
            size_hint_y=None,
            height=dp(50)
        )
        
        content.add_widget(self.litros_field)
        content.add_widget(self.prenez_field)
        content.add_widget(self.paricion_field)
        content.add_widget(self.destete_field)
        content.add_widget(self.vacas_field)
        content.add_widget(self.observaciones_field)
        
        self.dialog = MDDialog(
            title="Registrar Producción Diaria",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_press=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_press=self.save_registro),
            ],
        )
        self.dialog.open()
    
    def save_registro(self, *args):
        """Guardar registro de tambo"""
        if not self.litros_field.text:
            return
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tambo (fecha, litros_producidos, porcentaje_prenez, 
                             porcentaje_paricion, porcentaje_destete, 
                             vacas_lactancia, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            float(self.litros_field.text),
            float(self.prenez_field.text) if self.prenez_field.text else 0,
            float(self.paricion_field.text) if self.paricion_field.text else 0,
            float(self.destete_field.text) if self.destete_field.text else 0,
            int(self.vacas_field.text) if self.vacas_field.text else 0,
            self.observaciones_field.text
        ))
        
        conn.commit()
        self.dialog.dismiss()
        self.load_tambo_data()
    
    def show_evolution_graph(self, *args):
        """Mostrar gráfico de evolución de producción"""
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fecha, litros_producidos 
            FROM tambo 
            ORDER BY fecha DESC 
            LIMIT 30
        ''')
        
        datos = cursor.fetchall()
        
        if not datos:
            return
        
        # Invertir para mostrar cronológicamente
        datos = list(reversed(datos))
        
        fechas = [datetime.strptime(d['fecha'], '%Y-%m-%d').strftime('%d/%m') for d in datos]
        litros = [d['litros_producidos'] for d in datos]
        
        # Crear gráfico
        plt.close('all')
        fig = plt.figure(figsize=(8, 5), facecolor='white')
        ax = fig.add_subplot(111)
        ax.plot(fechas, litros, marker='o', linewidth=2, markersize=6, color='blue')
        ax.set_title('Evolución de Producción de Leche', fontsize=12, fontweight='bold')
        ax.set_xlabel('Fecha', fontsize=10)
        ax.set_ylabel('Litros', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas de fecha
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Agregar línea de promedio
        promedio = sum(litros) / len(litros)
        ax.axhline(y=promedio, color='red', linestyle='--', label=f'Promedio: {promedio:.0f}L', linewidth=2)
        ax.legend()
        
        fig.tight_layout()
        
        canvas = MatplotlibWidget(fig)
        
        graph_dialog = MDDialog(
            title="Evolución de Producción",
            type="custom",
            content_cls=canvas,
            size_hint=(0.95, 0.85),
            buttons=[
                MDFlatButton(text="CERRAR", on_press=lambda x: graph_dialog.dismiss())
            ],
        )
        graph_dialog.open()