"""
Módulo de cálculo de márgenes de producción
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.widget import Widget
from kivymd.uix.list import ThreeLineListItem, MDList
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from datetime import datetime
import database


class MargenCard(MDCard):
    """Tarjeta de resumen de margen"""
    def __init__(self, titulo, valor, color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(5)
        self.size_hint = (1, None)
        self.height = dp(80)
        self.elevation = 2
        self.md_bg_color = color
        
        titulo_lbl = MDLabel(
            text=titulo,
            halign='left',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style='Caption'
        )
        
        valor_lbl = MDLabel(
            text=valor,
            halign='left',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style='H5',
            bold=True
        )
        
        self.add_widget(titulo_lbl)
        self.add_widget(valor_lbl)


class MargenesScreen(MDScreen):
    """Pantalla de análisis de márgenes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'margenes'
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Márgenes de Producción",
            elevation=3,
            md_bg_color=(0.2, 0.6, 0.8, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # Contenido
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Resumen de indicadores
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Calcular totales
        cursor.execute('SELECT SUM(monto) FROM ingresos')
        total_ingresos = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(monto) FROM gastos')
        total_gastos = cursor.fetchone()[0] or 0
        
        margen_total = total_ingresos - total_gastos
        porcentaje_margen = (margen_total / total_ingresos * 100) if total_ingresos > 0 else 0
        
        # Tarjetas de resumen
        card1 = MargenCard(
            "Ingresos Totales",
            f"${total_ingresos:,.0f}",
            (0.2, 0.7, 0.3, 1)
        )
        content.add_widget(card1)
        
        card2 = MargenCard(
            "Gastos Totales",
            f"${total_gastos:,.0f}",
            (0.9, 0.3, 0.3, 1)
        )
        content.add_widget(card2)
        
        card3 = MargenCard(
            "Margen Neto",
            f"${margen_total:,.0f}",
            (0.2, 0.5, 0.8, 1)
        )
        content.add_widget(card3)
        
        card4 = MargenCard(
            "Rentabilidad",
            f"{porcentaje_margen:.1f}%",
            (0.6, 0.4, 0.8, 1)
        )
        content.add_widget(card4)
        
        # Cálculo por hectárea
        cursor.execute('SELECT SUM(hectareas) FROM superficie')
        total_hectareas = cursor.fetchone()[0] or 1
        
        margen_por_ha = margen_total / total_hectareas if total_hectareas > 0 else 0
        
        card5 = MargenCard(
            f"Margen por Hectárea ({total_hectareas:.0f} ha)",
            f"${margen_por_ha:,.0f}/ha",
            (0.3, 0.6, 0.7, 1)
        )
        content.add_widget(card5)
        
        # Botón para calcular margen personalizado
        btn_calcular = MDRaisedButton(
            text="Calcular Margen Específico",
            size_hint=(1, None),
            height=dp(50),
            on_press=self.show_margin_calculator
        )
        content.add_widget(btn_calcular)
        
        # Análisis por categoría
        titulo_cat = MDLabel(
            text="Análisis por Categoría",
            halign='left',
            font_style='H6',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(titulo_cat)
        
        # Ingresos por categoría
        cursor.execute('''
            SELECT categoria, SUM(monto) as total
            FROM ingresos
            GROUP BY categoria
        ''')
        ingresos_cat = cursor.fetchall()
        
        # Gastos por categoría
        cursor.execute('''
            SELECT categoria, SUM(monto) as total
            FROM gastos
            GROUP BY categoria
        ''')
        gastos_cat = cursor.fetchall()
        
        # Crear diccionarios para cálculo
        ing_dict = {row['categoria']: row['total'] for row in ingresos_cat}
        gas_dict = {row['categoria']: row['total'] for row in gastos_cat}
        
        # Mostrar análisis por categoría
        categorias = set(list(ing_dict.keys()) + list(gas_dict.keys()))
        
        self.analisis_list = MDList()
        for cat in categorias:
            ing = ing_dict.get(cat, 0)
            gas = gas_dict.get(cat, 0)
            margen = ing - gas
            
            item = ThreeLineListItem(
                text=f"{cat.title()}",
                secondary_text=f"Ingresos: ${ing:,.0f} | Gastos: ${gas:,.0f}",
                tertiary_text=f"Margen: ${margen:,.0f}"
            )
            self.analisis_list.add_widget(item)
        
        content.add_widget(self.analisis_list)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def go_back(self):
        self.manager.current = 'dashboard'
    
    def show_margin_calculator(self, *args):
        """Mostrar calculadora de margen personalizada"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        content.add_widget(Widget(size_hint_y=None, height=dp(30)))

        
        self.producto_field = MDTextField(
            hint_text="Producto/Cultivo",
            size_hint_y=None,
            height=dp(50)
        )
        
        self.cantidad_field = MDTextField(
            hint_text="Cantidad (ha/kg/unidades)",
            input_filter='float',
            size_hint_y=None,
            height=dp(50)
        )
        
        self.costo_field = MDTextField(
            hint_text="Costo Total",
            input_filter='float',
            size_hint_y=None,
            height=dp(50)
        )
        
        self.ingreso_field = MDTextField(
            hint_text="Ingreso Total",
            input_filter='float',
            size_hint_y=None,
            height=dp(50)
        )
        
        content.add_widget(self.producto_field)
        content.add_widget(self.cantidad_field)
        content.add_widget(self.costo_field)
        content.add_widget(self.ingreso_field)
        
        self.calc_dialog = MDDialog(
            title="Calcular Margen",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_press=lambda x: self.calc_dialog.dismiss()),
                MDRaisedButton(text="CALCULAR", on_press=self.calculate_margin),
            ],
        )
        self.calc_dialog.open()
    
    def calculate_margin(self, *args):
        """Calcular y guardar margen"""
        if not all([
            self.producto_field.text,
            self.cantidad_field.text,
            self.costo_field.text,
            self.ingreso_field.text
        ]):
            return
        
        cantidad = float(self.cantidad_field.text)
        costo = float(self.costo_field.text)
        ingreso = float(self.ingreso_field.text)
        margen = ingreso - costo
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO margenes (tipo, cultivo_producto, hectareas_cantidad, costo_total, ingreso_total, margen, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'personalizado',
            self.producto_field.text,
            cantidad,
            costo,
            ingreso,
            margen,
            datetime.now().strftime('%Y-%m-%d')
        ))
        
        conn.commit()
        
        # Mostrar resultado
        resultado = f"""
Producto: {self.producto_field.text}
Cantidad: {cantidad}
Costo Total: ${costo:,.0f}
Ingreso Total: ${ingreso:,.0f}
Margen: ${margen:,.0f}
Margen Unitario: ${margen/cantidad:,.2f}
        """
        
        result_dialog = MDDialog(
            title="Resultado del Cálculo",
            text=resultado,
            buttons=[
                MDRaisedButton(text="OK", on_press=lambda x: result_dialog.dismiss())
            ],
        )
        
        self.calc_dialog.dismiss()
        result_dialog.open()