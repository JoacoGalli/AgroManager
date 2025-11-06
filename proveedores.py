"""
Módulo de gestión de proveedores y facturas
"""

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

import database


class ProveedoresScreen(MDScreen):
    """Pantalla de gestión de proveedores"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'proveedores'
        self.dialog = None
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Proveedores",
            elevation=3,
            md_bg_color=(0.2, 0.6, 0.8, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # Contenido
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Botón agregar
        btn_add = MDRaisedButton(
            text="Agregar Proveedor",
            pos_hint={'center_x': 0.5},
            size_hint=(0.9, None),
            height=dp(50),
            on_press=self.show_add_dialog
        )
        content.add_widget(btn_add)
        
        # Lista de proveedores
        self.proveedores_list = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.proveedores_list)
        content.add_widget(scroll)
        
        layout.add_widget(content)
        self.add_widget(layout)
        
        self.load_proveedores()
    
    def go_back(self):
        self.manager.current = 'dashboard'
    
    def load_proveedores(self):
        """Cargar lista de proveedores"""
        self.proveedores_list.clear_widgets()
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM proveedores ORDER BY nombre')
        proveedores = cursor.fetchall()
        
        for prov in proveedores:
            item = ThreeLineListItem(
                text=prov['nombre'],
                secondary_text=f"Rubro: {prov['rubro'] or 'N/A'}",
                tertiary_text=f"CUIT: {prov['cuit'] or 'N/A'} | Tel: {prov['telefono'] or 'N/A'}"
            )
            self.proveedores_list.add_widget(item)
        
        if not proveedores:
            self.proveedores_list.add_widget(
                ThreeLineListItem(text="No hay proveedores registrados")
            )
    
    def show_add_dialog(self, *args):
        """Mostrar diálogo para agregar proveedor"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        content.add_widget(Widget(size_hint_y=None, height=dp(70)))
        
        self.nombre_field = MDTextField(hint_text="Nombre", size_hint_y=None, height=dp(50))
        self.rubro_field = MDTextField(hint_text="Rubro", size_hint_y=None, height=dp(50))
        self.cuit_field = MDTextField(hint_text="CUIT", size_hint_y=None, height=dp(50))
        self.telefono_field = MDTextField(hint_text="Teléfono", size_hint_y=None, height=dp(50))
        self.email_field = MDTextField(hint_text="Email", size_hint_y=None, height=dp(50))
        self.direccion_field = MDTextField(hint_text="Dirección", size_hint_y=None, height=dp(50))
        
        content.add_widget(self.nombre_field)
        content.add_widget(self.rubro_field)
        content.add_widget(self.cuit_field)
        content.add_widget(self.telefono_field)
        content.add_widget(self.email_field)
        content.add_widget(self.direccion_field)
        
        self.dialog = MDDialog(
            title="Agregar Proveedor",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_press=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="GUARDAR", on_press=self.save_proveedor),
            ],
        )
        self.dialog.open()
    
    def save_proveedor(self, *args):
        """Guardar proveedor"""
        if not self.nombre_field.text:
            return
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO proveedores (nombre, rubro, cuit, telefono, email, direccion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            self.nombre_field.text,
            self.rubro_field.text,
            self.cuit_field.text,
            self.telefono_field.text,
            self.email_field.text,
            self.direccion_field.text
        ))
        
        conn.commit()
        self.dialog.dismiss()
        self.load_proveedores()