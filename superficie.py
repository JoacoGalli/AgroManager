"""
Módulo de gestión de superficie y stock ganadero
"""

import matplotlib
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from kivy.clock import Clock

import database
from matplotlib_wrapper import MatplotlibWidget


class SuperficieScreen(MDScreen):
    """Pantalla de gestión de superficie y ganado"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'superficie'
        self.graph_canvas = None
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Superficie y Stock",
            elevation=3,
            md_bg_color=(0.2, 0.6, 0.8, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # ScrollView principal
        scroll = ScrollView()
        self.main_content = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10),
            size_hint_y=None
        )
        self.main_content.bind(minimum_height=self.main_content.setter('height'))
        
        # Botón agregar
        btn_add = MDRaisedButton(
            text="Agregar Cultivo",
            size_hint=(1, None),
            height=dp(50),
            on_press=self.show_add_cultivo_dialog
        )
        self.main_content.add_widget(btn_add)
        
        # Card para el gráfico
        self.graph_card = MDCard(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(350),
            padding=dp(10),
            elevation=2
        )
        self.main_content.add_widget(self.graph_card)
        
        # Título de la lista
        titulo_lista = MDLabel(
            text="Cultivos y Superficie",
            halign='left',
            font_style='H6',
            size_hint_y=None,
            height=dp(40)
        )
        self.main_content.add_widget(titulo_lista)
        
        # Lista de cultivos
        self.superficie_list = MDList()
        self.main_content.add_widget(self.superficie_list)
        
        scroll.add_widget(self.main_content)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        # Cargar datos al iniciar
        Clock.schedule_once(lambda dt: self.load_data(), 0.5)
    
    def go_back(self):
        self.manager.current = 'dashboard'
    
    def load_data(self):
        """Cargar superficie y gráfico"""
        self.load_superficie()
        self.load_distribution_graph()
    
    def load_superficie(self):
        """Cargar lista de cultivos y superficie"""
        self.superficie_list.clear_widgets()
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Total de hectáreas
        cursor.execute('SELECT SUM(hectareas) FROM superficie')
        total_ha = cursor.fetchone()[0] or 0
        
        # Cultivos
        cursor.execute('SELECT * FROM superficie ORDER BY hectareas DESC')
        cultivos = cursor.fetchall()
        
        for cultivo in cultivos:
            porcentaje = (cultivo['hectareas'] / total_ha * 100) if total_ha > 0 else 0
            
            item = ThreeLineListItem(
                text=f"{cultivo['cultivo']} - {cultivo['hectareas']:.1f} ha",
                secondary_text=f"Porcentaje: {porcentaje:.1f}%",
                tertiary_text=f"Siembra: {cultivo['fecha_siembra'] or 'N/A'} | Cosecha: {cultivo['fecha_cosecha'] or 'N/A'}"
            )
            self.superficie_list.add_widget(item)
        
        if not cultivos:
            self.superficie_list.add_widget(
                ThreeLineListItem(text="No hay cultivos registrados")
            )
        
        # Agregar información de ganado
        cursor.execute('SELECT * FROM ganado')
        ganado = cursor.fetchall()
        
        if ganado:
            for animal in ganado:
                item = ThreeLineListItem(
                    text=f"{animal['tipo']} - {animal['cantidad']} cabezas",
                    secondary_text=f"Categoría: {animal['categoria'] or 'N/A'}",
                    tertiary_text=f"Registro: {animal['fecha_registro']}"
                )
                self.superficie_list.add_widget(item)
    
    def load_distribution_graph(self):
        """Cargar gráfico de distribución de cultivos"""
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT cultivo, hectareas FROM superficie')
        datos = cursor.fetchall()
        
        # Limpiar card anterior
        self.graph_card.clear_widgets()
        
        if not datos:
            label = MDLabel(
                text="No hay cultivos para mostrar",
                halign='center',
                valign='middle'
            )
            self.graph_card.add_widget(label)
            return
        
        cultivos = [d['cultivo'] for d in datos]
        hectareas = [d['hectareas'] for d in datos]
        
        # Crear gráfico de torta
        plt.close('all')
        fig = plt.figure(figsize=(6, 4), facecolor='white')
        ax = fig.add_subplot(111)
        colors = ['#66BB6A', '#FFA726', '#42A5F5', '#AB47BC', '#26C6DA']
        wedges, texts, autotexts = ax.pie(hectareas, labels=cultivos, autopct='%1.1f%%', 
                                           startangle=90, colors=colors[:len(cultivos)])
        ax.set_title('Distribución de Superficie por Cultivo', fontsize=12, fontweight='bold', pad=10)
        
        # Hacer el texto más legible
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        fig.tight_layout()
        
        # Agregar widget al card
        self.graph_canvas = MatplotlibWidget(fig)
        self.graph_card.add_widget(self.graph_canvas)
    
    def show_add_cultivo_dialog(self, *args):
        """Mostrar diálogo para agregar cultivo"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        content.add_widget(Widget(size_hint_y=None, height=dp(30)))
        
        self.cultivo_field = MDTextField(
            hint_text="Cultivo (ej: Soja, Maíz, Trigo)",
            size_hint_y=None,
            height=dp(50)
        )
        
        self.hectareas_field = MDTextField(
            hint_text="Hectáreas",
            input_filter='float',
            size_hint_y=None,
            height=dp(50)
        )
        
        self.fecha_siembra_field = MDTextField(
            hint_text="Fecha de siembra (YYYY-MM-DD)",
            size_hint_y=None,
            height=dp(50)
        )
        
        self.fecha_cosecha_field = MDTextField(
            hint_text="Fecha de cosecha (YYYY-MM-DD)",
            size_hint_y=None,
            height=dp(50)
        )
        
        content.add_widget(self.cultivo_field)
        content.add_widget(self.hectareas_field)
        content.add_widget(self.fecha_siembra_field)
        content.add_widget(self.fecha_cosecha_field)
        
        self.dialog = MDDialog(
            title="Agregar Cultivo",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_press=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_press=self.save_cultivo),
            ],
        )
        self.dialog.open()
    
    def save_cultivo(self, *args):
        """Guardar cultivo"""
        if not self.cultivo_field.text or not self.hectareas_field.text:
            return
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO superficie (cultivo, hectareas, fecha_siembra, fecha_cosecha)
            VALUES (?, ?, ?, ?)
        ''', (
            self.cultivo_field.text,
            float(self.hectareas_field.text),
            self.fecha_siembra_field.text or None,
            self.fecha_cosecha_field.text or None
        ))
        
        conn.commit()
        self.dialog.dismiss()
        
        # Recargar datos y gráfico
        self.load_data()