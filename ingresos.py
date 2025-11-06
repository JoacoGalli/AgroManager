"""
Módulo de gestión de ingresos con comparativa de gastos
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
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

matplotlib.use('Agg')
from datetime import datetime

import matplotlib.pyplot as plt
from kivy.clock import Clock

import database
from matplotlib_wrapper import MatplotlibWidget


class IngresosScreen(MDScreen):
    """Pantalla de gestión de ingresos"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'ingresos'
        self.dialog = None
        self.categoria_menu = None
        self.selected_categoria = 'agro'
        self.graph_canvas = None
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Ingresos",
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
            text="Agregar Ingreso",
            size_hint=(1, None),
            height=dp(50),
            on_press=self.show_add_dialog
        )
        self.main_content.add_widget(btn_add)
        
        # Card para el gráfico comparativo
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
            text="Últimos Ingresos Registrados",
            halign='left',
            font_style='H6',
            size_hint_y=None,
            height=dp(40)
        )
        self.main_content.add_widget(titulo_lista)
        
        # Lista de ingresos
        self.ingresos_list = MDList()
        self.main_content.add_widget(self.ingresos_list)
        
        scroll.add_widget(self.main_content)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        # Cargar datos al iniciar
        Clock.schedule_once(lambda dt: self.load_data(), 0.5)
    
    def go_back(self):
        self.manager.current = 'dashboard'
    
    def load_data(self):
        """Cargar ingresos y gráfico"""
        self.load_ingresos()
        self.load_comparison_graph()
    
    def load_ingresos(self):
        """Cargar lista de ingresos"""
        self.ingresos_list.clear_widgets()
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM ingresos 
            ORDER BY fecha DESC
            LIMIT 20
        ''')
        
        ingresos = cursor.fetchall()
        
        for ingreso in ingresos:
            fecha_obj = datetime.strptime(ingreso['fecha'], '%Y-%m-%d')
            item = TwoLineListItem(
                text=f"{ingreso['concepto']} - ${ingreso['monto']:,.0f}",
                secondary_text=f"{ingreso['categoria'].title()} | {fecha_obj.strftime('%d/%m/%Y')}"
            )
            self.ingresos_list.add_widget(item)
        
        if not ingresos:
            self.ingresos_list.add_widget(TwoLineListItem(text="No hay ingresos registrados"))
    
    def load_comparison_graph(self):
        """Cargar gráfico comparativo ingresos vs gastos"""
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Total ingresos
        cursor.execute('SELECT SUM(monto) FROM ingresos')
        total_ingresos = cursor.fetchone()[0] or 0
        
        # Total gastos
        cursor.execute('SELECT SUM(monto) FROM gastos')
        total_gastos = cursor.fetchone()[0] or 0
        
        # Limpiar card anterior
        self.graph_card.clear_widgets()
        
        if total_ingresos == 0 and total_gastos == 0:
            label = MDLabel(
                text="No hay datos financieros para mostrar",
                halign='center',
                valign='middle'
            )
            self.graph_card.add_widget(label)
            return
        
        # Crear gráfico comparativo
        plt.close('all')
        fig = plt.figure(figsize=(6, 4), facecolor='white')
        ax = fig.add_subplot(111)
        categorias = ['Ingresos', 'Gastos', 'Balance']
        valores = [total_ingresos, total_gastos, total_ingresos - total_gastos]
        colores = ['#4CAF50', '#F44336', '#2196F3' if valores[2] >= 0 else '#FF9800']
        
        bars = ax.bar(categorias, valores, color=colores, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.set_title('Comparación Financiera', fontsize=12, fontweight='bold', pad=10)
        ax.set_ylabel('Monto ($)', fontsize=10)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(axis='y', alpha=0.3)
        
        # Agregar valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'${abs(height):,.0f}',
                    ha='center', va='bottom' if height >= 0 else 'top',
                    fontsize=9, fontweight='bold')
        
        fig.tight_layout()
        
        # Agregar widget al card
        self.graph_canvas = MatplotlibWidget(fig)
        self.graph_card.add_widget(self.graph_canvas)
    
    def show_add_dialog(self, *args):
        """Mostrar diálogo para agregar ingreso"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        content.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        self.concepto_field = MDTextField(hint_text="Concepto", size_hint_y=None, height=dp(50))
        self.monto_field = MDTextField(hint_text="Monto", input_filter='float', size_hint_y=None, height=dp(50))
        self.descripcion_field = MDTextField(hint_text="Descripción", size_hint_y=None, height=dp(50))
        
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
            title="Agregar Ingreso",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_press=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_press=self.save_ingreso),
            ],
        )
        self.dialog.open()
    
    def show_categoria_menu(self, button):
        """Mostrar menú de categorías"""
        menu_items = [
            {
                "text": "Agro",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="agro": self.select_categoria(x)
            },
            {
                "text": "Ganadería",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="ganadería": self.select_categoria(x)
            },
            {
                "text": "Otros",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="otros": self.select_categoria(x)
            },
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
        if self.categoria_menu:
            self.categoria_menu.dismiss()
    
    def save_ingreso(self, *args):
        """Guardar ingreso"""
        if not self.concepto_field.text or not self.monto_field.text:
            return
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ingresos (categoria, concepto, monto, fecha, descripcion)
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