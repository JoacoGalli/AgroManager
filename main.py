"""
AgroManager - Sistema de Gestión Agropecuaria
Aplicación móvil y desktop con Kivy/KivyMD
Autor: Sistema AgroManager
Versión: 1.0
"""

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar

import cheques
import database
import gastos
import ingresos
import margenes
import mercado
import proveedores
import superficie
import tambo


class DashboardCard(MDCard):
    """Tarjeta personalizada para el dashboard"""
    def __init__(self, title, value, icon, screen_name, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint = (None, None)
        self.size = (dp(160), dp(140))
        self.elevation = 3
        self.radius = [dp(15)]
        self.md_bg_color = (0.2, 0.6, 0.8, 1)
        self.screen_name = screen_name
        
        # Icono
        icon_btn = MDIconButton(
            icon=icon,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5}
        )
        icon_btn.disabled = True
        
        # Título
        title_lbl = MDLabel(
            text=title,
            halign='center',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style='Caption',
            size_hint_y=None,
            height=dp(20)
        )
        
        # Valor
        value_lbl = MDLabel(
            text=str(value),
            halign='center',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style='H6',
            bold=True
        )
        
        self.add_widget(icon_btn)
        self.add_widget(title_lbl)
        self.add_widget(value_lbl)


class DashboardScreen(MDScreen):
    """Pantalla principal con resumen de métricas"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dashboard'
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="AgroManager - Dashboard",
            elevation=3,
            md_bg_color=(0.2, 0.6, 0.8, 1)
        )
        layout.add_widget(toolbar)
        
        # ScrollView para las tarjetas
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(15),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Título de sección
        welcome = MDLabel(
            text="Gestión Integral del Establecimiento",
            halign='left',
            font_style='H6',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(welcome)
        
        # Grid de tarjetas - Fila 1
        grid1 = GridLayout(
            cols=2,
            spacing=dp(15),
            size_hint_y=None,
            height=dp(150)
        )
        
        # Cargar datos del dashboard
        db = database.DatabaseManager()
        cheques_proximos = db.get_cheques_proximos()
        total_gastos = db.get_total_gastos_mes()
        total_ingresos = db.get_total_ingresos_mes()
        
        card1 = DashboardCard(
            "Cheques Próximos",
            len(cheques_proximos),
            "bank-check",
            "cheques"
        )
        card1.bind(on_press=lambda x: self.navigate_to('cheques'))
        
        card2 = DashboardCard(
            "Gastos del Mes",
            f"${total_gastos:,.0f}",
            "cash-minus",
            "gastos"
        )
        card2.bind(on_press=lambda x: self.navigate_to('gastos'))
        
        grid1.add_widget(card1)
        grid1.add_widget(card2)
        content.add_widget(grid1)
        
        # Grid de tarjetas - Fila 2
        grid2 = GridLayout(
            cols=2,
            spacing=dp(15),
            size_hint_y=None,
            height=dp(150)
        )
        
        card3 = DashboardCard(
            "Ingresos del Mes",
            f"${total_ingresos:,.0f}",
            "cash-plus",
            "ingresos"
        )
        card3.bind(on_press=lambda x: self.navigate_to('ingresos'))
        
        card4 = DashboardCard(
            "Proveedores",
            db.get_total_proveedores(),
            "account-group",
            "proveedores"
        )
        card4.bind(on_press=lambda x: self.navigate_to('proveedores'))
        
        grid2.add_widget(card3)
        grid2.add_widget(card4)
        content.add_widget(grid2)
        
        # Grid de tarjetas - Fila 3
        grid3 = GridLayout(
            cols=2,
            spacing=dp(15),
            size_hint_y=None,
            height=dp(150)
        )
        
        card5 = DashboardCard(
            "Superficie",
            f"{db.get_superficie_total()} ha",
            "nature",
            "superficie"
        )
        card5.bind(on_press=lambda x: self.navigate_to('superficie'))
        
        card6 = DashboardCard(
            "Márgenes",
            "Ver análisis",
            "chart-line",
            "margenes"
        )
        card6.bind(on_press=lambda x: self.navigate_to('margenes'))
        
        grid3.add_widget(card5)
        grid3.add_widget(card6)
        content.add_widget(grid3)
        
        # Grid de tarjetas - Fila 4
        grid4 = GridLayout(
            cols=2,
            spacing=dp(15),
            size_hint_y=None,
            height=dp(150)
        )
        
        card7 = DashboardCard(
            "Mercado",
            "Precios",
            "chart-bell-curve-cumulative",
            "mercado"
        )
        card7.bind(on_press=lambda x: self.navigate_to('mercado'))
        
        card8 = DashboardCard(
            "Tambo",
            "Producción",
            "cow",
            "tambo"
        )
        card8.bind(on_press=lambda x: self.navigate_to('tambo'))
        
        grid4.add_widget(card7)
        grid4.add_widget(card8)
        content.add_widget(grid4)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def navigate_to(self, screen_name):
        """Navegar a una pantalla específica"""
        self.manager.current = screen_name


class AgroManagerApp(MDApp):
    """Aplicación principal"""
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Inicializar base de datos
        db = database.DatabaseManager()
        db.init_db()
        
        # Screen Manager
        sm = MDScreenManager()
        
        # Agregar pantallas
        sm.add_widget(DashboardScreen())
        sm.add_widget(cheques.ChequesScreen())
        sm.add_widget(proveedores.ProveedoresScreen())
        sm.add_widget(gastos.GastosScreen())
        sm.add_widget(ingresos.IngresosScreen())
        sm.add_widget(margenes.MargenesScreen())
        sm.add_widget(superficie.SuperficieScreen())
        sm.add_widget(mercado.MercadoScreen())
        sm.add_widget(tambo.TamboScreen())
        
        return sm


if __name__ == '__main__':
    AgroManagerApp().run()