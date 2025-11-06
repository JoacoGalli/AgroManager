"""
Módulo de consulta de precios de mercado
Obtiene valores actualizados de dólar, soja, carne, etc.
"""


import requests
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar


class PriceCard(MDCard):
    """Tarjeta para mostrar precio"""
    def __init__(self, titulo, valor, variacion="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(5)
        self.size_hint = (1, None)
        self.height = dp(100)
        self.elevation = 3
        self.md_bg_color = (0.95, 0.95, 0.95, 1)
        
        titulo_lbl = MDLabel(
            text=titulo,
            halign='left',
            font_style='Caption',
            theme_text_color="Secondary"
        )
        
        valor_lbl = MDLabel(
            text=valor,
            halign='left',
            font_style='H4',
            bold=True
        )
        
        if variacion:
            var_lbl = MDLabel(
                text=variacion,
                halign='left',
                font_style='Caption',
                theme_text_color="Custom",
                text_color=(0.2, 0.7, 0.2, 1) if '+' in variacion else (0.9, 0.2, 0.2, 1)
            )
            self.add_widget(titulo_lbl)
            self.add_widget(valor_lbl)
            self.add_widget(var_lbl)
        else:
            self.add_widget(titulo_lbl)
            self.add_widget(valor_lbl)


class MercadoScreen(MDScreen):
    """Pantalla de información de mercado"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'mercado'
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Precios de Mercado",
            elevation=3,
            md_bg_color=(0.2, 0.6, 0.8, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # ScrollView para contenido
        scroll = ScrollView()
        self.content = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(15),
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        
        # Botón actualizar
        btn_refresh = MDRaisedButton(
            text="Actualizar Precios",
            size_hint=(1, None),
            height=dp(50),
            on_press=self.update_prices
        )
        self.content.add_widget(btn_refresh)
        
        # Label de última actualización
        self.last_update_label = MDLabel(
            text="Última actualización: nunca",
            halign='center',
            font_style='Caption',
            size_hint_y=None,
            height=dp(30)
        )
        self.content.add_widget(self.last_update_label)
        
        # Contenedor para tarjetas de precios
        self.prices_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None
        )
        self.prices_container.bind(minimum_height=self.prices_container.setter('height'))
        self.content.add_widget(self.prices_container)
        
        scroll.add_widget(self.content)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        # Cargar precios iniciales
        Clock.schedule_once(lambda dt: self.update_prices(), 0.5)
    
    def go_back(self):
        self.manager.current = 'dashboard'
    
    def update_prices(self, *args):
        """Actualizar precios desde APIs"""
        self.prices_container.clear_widgets()
        
        # Mostrar mensaje de carga
        loading_label = MDLabel(
            text="Actualizando precios...",
            halign='center',
            size_hint_y=None,
            height=dp(40)
        )
        self.prices_container.add_widget(loading_label)
        
        # Obtener dólar blue
        try:
            response = requests.get('https://dolarapi.com/v1/dolares/blue', timeout=5)
            if response.status_code == 200:
                data = response.json()
                dolar_compra = data.get('compra', 0)
                dolar_venta = data.get('venta', 0)
                
                self.prices_container.clear_widgets()
                
                card_dolar = PriceCard(
                    "Dólar Blue",
                    f"Compra: ${dolar_compra:.2f} | Venta: ${dolar_venta:.2f}"
                )
                self.prices_container.add_widget(card_dolar)
        except Exception as e:
            self.prices_container.clear_widgets()
            error_label = MDLabel(
                text=f"Error al obtener dólar: {str(e)}",
                halign='center',
                size_hint_y=None,
                height=dp(40)
            )
            self.prices_container.add_widget(error_label)
        
        # Precios estimados (ya que las APIs de commodities pueden variar)
        # En producción, usar APIs reales de bolsas de cereales
        card_soja = PriceCard(
            "Soja (Chicago)",
            "U$S 450/tn",
            "Consultar fuente oficial"
        )
        self.prices_container.add_widget(card_soja)
        
        card_maiz = PriceCard(
            "Maíz (Chicago)",
            "U$S 200/tn",
            "Consultar fuente oficial"
        )
        self.prices_container.add_widget(card_maiz)
        
        card_trigo = PriceCard(
            "Trigo (Chicago)",
            "U$S 250/tn",
            "Consultar fuente oficial"
        )
        self.prices_container.add_widget(card_trigo)
        
        card_novillo = PriceCard(
            "Novillo (kg vivo)",
            "$1,800/kg",
            "Mercado de Liniers"
        )
        self.prices_container.add_widget(card_novillo)
        
        card_leche = PriceCard(
            "Leche",
            "$280/litro",
            "Precio promedio"
        )
        self.prices_container.add_widget(card_leche)
        
        # Nota informativa
        nota = MDLabel(
            text="Nota: Los precios de commodities son estimados. "
                 "Consulte fuentes oficiales como la Bolsa de Cereales, "
                 "Mercado de Liniers, etc. para valores actualizados.",
            halign='center',
            size_hint_y=None,
            height=dp(80),
            font_style='Caption',
            theme_text_color="Secondary"
        )
        self.prices_container.add_widget(nota)
        
        # Actualizar label de última actualización
        from datetime import datetime
        self.last_update_label.text = f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}"