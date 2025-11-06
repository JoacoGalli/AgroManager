"""
Módulo de gestión de cheques
Permite cargar, visualizar y gestionar vencimientos de cheques
"""

from datetime import datetime

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

import database


class ChequesScreen(MDScreen):
    """Pantalla de gestión de cheques"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'cheques'
        self.dialog = None
        self.date_picker = None
        self.selected_date = None
        
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar con botón de volver
        toolbar = MDTopAppBar(
            title="Gestión de Cheques",
            elevation=3,
            md_bg_color=(0.2, 0.6, 0.8, 1),
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # Contenedor de contenido
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Botón para agregar cheque
        btn_add = MDRaisedButton(
            text="Agregar Cheque",
            pos_hint={'center_x': 0.5},
            size_hint=(0.9, None),
            height=dp(50),
            on_press=self.show_add_dialog
        )
        content.add_widget(btn_add)
        
        # Lista de cheques
        self.cheques_list = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.cheques_list)
        content.add_widget(scroll)
        
        layout.add_widget(content)
        self.add_widget(layout)
        
        # Cargar cheques al iniciar
        self.load_cheques()
    
    def go_back(self):
        """Volver al dashboard"""
        self.manager.current = 'dashboard'
    
    def load_cheques(self):
        """Cargar y mostrar lista de cheques"""
        self.cheques_list.clear_widgets()
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cheques 
            WHERE estado = 'pendiente'
            ORDER BY fecha_vencimiento
        ''')
        
        cheques = cursor.fetchall()
        hoy = datetime.now()
        
        for cheque in cheques:
            fecha_venc = datetime.strptime(cheque['fecha_vencimiento'], '%Y-%m-%d')
            dias_restantes = (fecha_venc - hoy).days
            
            # Determinar color según proximidad
            if dias_restantes < 0:
                color = (0.9, 0.2, 0.2, 1)  # Rojo - vencido
                estado_texto = "VENCIDO"
            elif dias_restantes <= 7:
                color = (0.9, 0.6, 0.2, 1)  # Naranja - próximo
                estado_texto = f"{dias_restantes} días"
            else:
                color = (0.2, 0.7, 0.2, 1)  # Verde - tranquilo
                estado_texto = f"{dias_restantes} días"
            
            item = TwoLineListItem(
                text=f"Ch. {cheque['numero']} - {cheque['banco']} - ${cheque['monto']:,.0f}",
                secondary_text=f"Vence: {fecha_venc.strftime('%d/%m/%Y')} - {estado_texto}",
                theme_text_color="Custom",
                text_color=color,
                on_press=lambda x, c=cheque: self.show_cheque_options(c)
            )
            self.cheques_list.add_widget(item)
        
        if not cheques:
            self.cheques_list.add_widget(
                OneLineListItem(text="No hay cheques pendientes")
            )
    
    def show_add_dialog(self, *args):
        """Mostrar diálogo para agregar cheque"""
        if not self.dialog:
            content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            content.bind(minimum_height=content.setter('height'))

            # Espaciador arriba
            content.add_widget(Widget(size_hint_y=None, height=dp(20)))
            
            self.numero_field = MDTextField(
                hint_text="Número de cheque",
                size_hint_y=None,
                height=dp(50)
            )
            
            self.banco_field = MDTextField(
                hint_text="Banco",
                size_hint_y=None,
                height=dp(50)
            )
            
            self.monto_field = MDTextField(
                hint_text="Monto",
                input_filter='float',
                size_hint_y=None,
                height=dp(50)
            )
            
            self.fecha_button = MDRaisedButton(
                text="Seleccionar fecha de vencimiento",
                size_hint=(1, None),
                height=dp(50),
                on_press=self.show_date_picker
            )
            
            content.add_widget(self.numero_field)
            content.add_widget(self.banco_field)
            content.add_widget(self.monto_field)
            content.add_widget(self.fecha_button)
            
            self.dialog = MDDialog(
                title="Agregar Cheque",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        on_press=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="GUARDAR",
                        on_press=self.save_cheque
                    ),
                ],
            )
        
        self.dialog.open()
    
    def show_date_picker(self, *args):
        """Mostrar selector de fecha"""
        if not self.date_picker:
            self.date_picker = MDDatePicker()
            self.date_picker.bind(on_save=self.on_date_selected)
        
        self.date_picker.open()
    
    def on_date_selected(self, instance, value, date_range):
        """Callback cuando se selecciona una fecha"""
        self.selected_date = value.strftime('%Y-%m-%d')
        self.fecha_button.text = f"Fecha: {value.strftime('%d/%m/%Y')}"
    
    def save_cheque(self, *args):
        """Guardar cheque en la base de datos"""
        if not all([
            self.numero_field.text,
            self.banco_field.text,
            self.monto_field.text,
            self.selected_date
        ]):
            return
        
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cheques (numero, banco, monto, fecha_vencimiento)
            VALUES (?, ?, ?, ?)
        ''', (
            self.numero_field.text,
            self.banco_field.text,
            float(self.monto_field.text),
            self.selected_date
        ))
        
        conn.commit()
        
        # Limpiar campos
        self.numero_field.text = ''
        self.banco_field.text = ''
        self.monto_field.text = ''
        self.selected_date = None
        self.fecha_button.text = "Seleccionar fecha de vencimiento"
        
        self.dialog.dismiss()
        self.load_cheques()
    
    def show_cheque_options(self, cheque):
        """Mostrar opciones para un cheque (marcar como cobrado, eliminar)"""
        menu_items = [
            {
                "text": "Marcar como cobrado",
                "on_release": lambda: self.mark_as_paid(cheque['id'])
            },
            {
                "text": "Eliminar",
                "on_release": lambda: self.delete_cheque(cheque['id'])
            }
        ]
        
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()
    
    def mark_as_paid(self, cheque_id):
        """Marcar cheque como cobrado"""
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cheques SET estado = 'cobrado' WHERE id = ?
        ''', (cheque_id,))
        
        conn.commit()
        self.menu.dismiss()
        self.load_cheques()
    
    def delete_cheque(self, cheque_id):
        """Eliminar cheque"""
        db = database.DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM cheques WHERE id = ?', (cheque_id,))
        conn.commit()
        self.menu.dismiss()
        self.load_cheques()