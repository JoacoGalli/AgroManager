"""
Módulo de gestión de gastos con gráficos
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import TwoLineListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.widget import Widget
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from kivy.clock import Clock
import database
from matplotlib_wrapper import MatplotlibWidget


class GastosScreen(MDScreen):
    """Pantalla de gestión de gastos"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'gastos'
        self.dialog = None
        self.categoria_menu = None
        self.selected_categoria = 'agro'
        self.graph_canvas = None
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Gastos",
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
            text="Agregar Gasto",
            size_hint=(1, None),
            height=dp(50),
            on_press=self.show_add_dialog
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
            text="Últimos Gastos Registrados",
            halign='left',
            font_style='H6',
            size_hint_y=None,
            height=dp(40)
        )
        self.main_content.add_widget(titulo_lista)
        
        # Lista de gastos
        self.gastos_list = MDList()
        self.main_content.add_widget(self.gastos_list)
        
        scroll.add_widget(self.main_content)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        # Cargar datos al iniciar
        Clock.schedule_once(lambda dt: self.load_data(), 0.5)
    
    def go_back(self):
        self.manager.current = 'dashboard'
    
    def load_data(self):
        """Cargar gastos y gráfico"""
        self.load_gastos()
        self.load_graph()
    
    def load_gastos(self):
        """Cargar lista de gastos"""
        self.gastos_list.clear_widgets()
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM gastos 
            ORDER BY fecha DESC
            LIMIT 20
        ''')
        
        gastos = cursor.fetchall()
        
        for gasto in gastos:
            fecha_obj = datetime.strptime(gasto['fecha'], '%Y-%m-%d')
            item = TwoLineListItem(
                text=f"{gasto['concepto']} - ${gasto['monto']:,.0f}",
                secondary_text=f"{gasto['categoria'].title()} | {fecha_obj.strftime('%d/%m/%Y')}"
            )
            self.gastos_list.add_widget(item)
        
        if not gastos:
            self.gastos_list.add_widget(TwoLineListItem(text="No hay gastos registrados"))
    
    def load_graph(self):
        """Cargar gráfico de gastos"""
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Obtener gastos por categoría
        cursor.execute('''
            SELECT categoria, SUM(monto) as total
            FROM gastos
            GROUP BY categoria
        ''')
        
        datos = cursor.fetchall()
        
        # Limpiar card anterior
        self.graph_card.clear_widgets()
        
        if not datos:
            label = MDLabel(
                text="No hay datos de gastos para mostrar",
                halign='center',
                valign='middle'
            )
            self.graph_card.add_widget(label)
            return
        
        categorias = [d['categoria'].title() for d in datos]
        montos = [d['total'] for d in datos]
        
        # Crear gráfico
        plt.close('all')
        fig = plt.figure(figsize=(6, 4), facecolor='white')
        ax = fig.add_subplot(111)
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#95E1D3', '#F38181']
        wedges, texts, autotexts = ax.pie(montos, labels=categorias, autopct='%1.1f%%', 
                                           startangle=90, colors=colors[:len(categorias)])
        ax.set_title('Distribución de Gastos por Categoría', fontsize=12, fontweight='bold', pad=10)
        
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
    
    def show_add_dialog(self, *args):
        """Mostrar diálogo para agregar gasto"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(Widget(size_hint_y=None, height=dp(20)))

        
        self.concepto_field = MDTextField(hint_text="Concepto", size_hint_y=None, height=dp(50))
        self.monto_field = MDTextField(hint_text="Monto", input_filter='float', size_hint_y=None, height=dp(50))
        self.descripcion_field = MDTextField(hint_text="Descripción", size_hint_y=None, height=dp(50))
        
        # Botón de categoría
        self.categoria_button = MDRaisedButton(
            text="Categoría: Agro",
            size_hint=(1, None),
            height=dp(50),
            on_press=self.show_categoria_menu
        )
        
        content.add_widget(self.concepto_field)
        content.add_widget(self.monto_field)
        content.add_widget(self.categoria_button)
        content.add_widget(self.descripcion_field)
        
        self.dialog = MDDialog(
            title="Agregar Gasto",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_press=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_press=self.save_gasto),
            ],
        )
        self.dialog.open()
    
    def show_categoria_menu(self, button):
        """Mostrar menú de categorías"""
        menu_items = [
            {"text": "Agro", "on_release": lambda x="agro": self.select_categoria(x)},
            {"text": "Ganadería", "on_release": lambda x="ganadería": self.select_categoria(x)},
            {"text": "Otros", "on_release": lambda x="otros": self.select_categoria(x)},
        ]
        
        self.categoria_menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=4,
        )
        self.categoria_menu.open()
    
    def select_categoria(self, categoria):
        """Seleccionar categoría"""
        self.selected_categoria = categoria
        self.categoria_button.text = f"Categoría: {categoria.title()}"
        self.categoria_menu.dismiss()
    
    def save_gasto(self, *args):
        """Guardar gasto"""
        if not self.concepto_field.text or not self.monto_field.text:
            return
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO gastos (categoria, concepto, monto, fecha, descripcion)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            self.selected_categoria,
            self.concepto_field.text,
            float(self.monto_field.text),
            datetime.now().strftime('%Y-%m-%d'),
            self.descripcion_field.text
        ))
        
        conn.commit()
        self.dialog.dismiss()
        
        # Recargar datos y gráfico
        self.load_data()