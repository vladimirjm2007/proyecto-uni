import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sys

# --- 1. MODELO (MODELO): Lógica de Negocio y Datos ---

class ModeloBancario:
    """
    Gestiona el estado de las cuentas y contiene la lógica de negocio (reglas bancarias).
    """
    
    def __init__(self):
        # Datos iniciales de las cuentas (persistencia en memoria)
        self.CUENTAS = {
            'usuario1': {
                'contrasena': 'clave1',
                'nombre_propietario': 'Usuario Uno (Alto Saldo)',
                'saldo': 10000.00,
                'deuda_actual': 0.00,
                'limite_credito': 2000.00,
                'transacciones': []
            },
            'usuario2': {
                'contrasena': 'clave2',
                'nombre_propietario': 'Usuario Dos (Deudor)',
                'saldo': 500.00,
                'deuda_actual': 500.00,
                'limite_credito': 1500.00,
                'transacciones': []
            }
        }
        self.id_cuenta_actual = None
        self.TASA_DEUDA_PLANA = 0.08 # Tasa fija del 8% sobre el monto del crédito solicitado

    def obtener_datos_cuenta(self):
        """Devuelve los datos de la cuenta actualmente logueada."""
        if self.id_cuenta_actual:
            return self.CUENTAS[self.id_cuenta_actual]
        return None

    def formatear_moneda(self, valor):
        """Formatea un número a un string de moneda USD."""
        return f"${valor:,.2f}"

    def _crear_transaccion(self, id_cuenta, tipo, monto, saldo_final, deuda_final, exito=True):
        """Crea un objeto de transacción y lo añade al historial."""
        cuenta = self.CUENTAS[id_cuenta]
        tx = {
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': tipo,
            'monto': float(monto),
            'saldo_final': float(saldo_final),
            'deuda_final': float(deuda_final),
            'exito': exito
        }
        cuenta['transacciones'].insert(0, tx) # Añadir al principio
        cuenta['transacciones'] = cuenta['transacciones'][:30] # Limitar historial
        return tx

    def iniciar_sesion(self, id_usuario, contrasena):
        """Autentica al usuario usando id_usuario y contrasena."""
        if id_usuario in self.CUENTAS and self.CUENTAS[id_usuario]['contrasena'] == contrasena:
            self.id_cuenta_actual = id_usuario
            return True, f"Inicio de sesión exitoso como {self.CUENTAS[id_usuario]['nombre_propietario']}."
        return False, "Error: Usuario o contraseña incorrectos."

    def cerrar_sesion(self):
        """Cierra la sesión de la cuenta actual."""
        self.id_cuenta_actual = None

    def solicitar_credito(self, monto):
        """
        Permite solicitar un crédito. La deuda es el monto más el 8% fijo.
        """
        if not self.id_cuenta_actual:
            return False, "Error: No hay cuenta activa."
        
        cuenta = self.CUENTAS[self.id_cuenta_actual]
        
        if monto <= 0:
            return False, "El monto del crédito debe ser positivo."

        # Regla: Solo se puede pedir crédito si la deuda es cero
        if cuenta['deuda_actual'] > 0:
            return False, f"Ya tienes una deuda pendiente de {self.formatear_moneda(cuenta['deuda_actual'])}. Debes pagarla completamente para solicitar un nuevo crédito."

        # Calcular la deuda total con el cargo del 8%
        cargo_fijo = monto * self.TASA_DEUDA_PLANA
        deuda_total_a_pagar = monto + cargo_fijo
        
        # El monto solicitado (principal) no debe exceder el límite de crédito
        if monto > cuenta['limite_credito']:
            return False, f"El monto solicitado excede tu límite de crédito de {self.formatear_moneda(cuenta['limite_credito'])}."
            
        # Ejecutar el crédito
        cuenta['saldo'] += monto
        cuenta['deuda_actual'] += deuda_total_a_pagar # La deuda aumenta con el 8%
        
        self._crear_transaccion(self.id_cuenta_actual, 'Crédito Recibido', monto, cuenta['saldo'], cuenta['deuda_actual'])
        
        mensaje = (f"Crédito aprobado y depositado: {self.formatear_moneda(monto)}.\n"
                   f"Cargo Fijo (8%): {self.formatear_moneda(cargo_fijo)}.\n"
                   f"Deuda total a pagar: {self.formatear_moneda(deuda_total_a_pagar)}")
                   
        return True, mensaje

    def realizar_transferencia(self, id_destino, monto):
        """Realiza una transferencia de la cuenta actual a id_destino."""
        if not self.id_cuenta_actual:
            return False, "Error: No hay cuenta activa."
        
        id_origen = self.id_cuenta_actual
        cuenta_origen = self.CUENTAS[id_origen]
        
        # Validaciones
        if id_origen == id_destino:
            return False, "No puedes transferir dinero a tu propia cuenta."
        if id_destino not in self.CUENTAS:
            return False, f"Error: La cuenta destino '{id_destino}' no existe."
        if monto <= 0:
            return False, "El monto de la transferencia debe ser positivo."
        if cuenta_origen['saldo'] < monto:
            return False, f"Saldo insuficiente para transferir {self.formatear_moneda(monto)}."

        # Ejecutar la transferencia
        cuenta_destino = self.CUENTAS[id_destino]
        
        # Débito en origen
        cuenta_origen['saldo'] -= monto
        self._crear_transaccion(id_origen, f"Transferencia Enviada a {id_destino}", -monto, cuenta_origen['saldo'], cuenta_origen['deuda_actual'])
        
        # Crédito en destino
        cuenta_destino['saldo'] += monto
        self._crear_transaccion(id_destino, f"Transferencia Recibida de {id_origen}", monto, cuenta_destino['saldo'], cuenta_destino['deuda_actual'])
        
        return True, f"Transferencia de {self.formatear_moneda(monto)} a '{id_destino}' exitosa."


    def ejecutar_transaccion(self, accion, monto):
        """Función fachada para ejecutar la acción bancaria (Depósito, Retiro, PagoDeuda)."""
        if not self.id_cuenta_actual:
            return False, "Error: No hay cuenta activa."
        
        cuenta = self.CUENTAS[self.id_cuenta_actual]
        
        if monto <= 0:
            return False, "El monto debe ser positivo."
        
        if accion == 'deposito':
            cuenta['saldo'] += monto
            self._crear_transaccion(self.id_cuenta_actual, 'Depósito', monto, cuenta['saldo'], cuenta['deuda_actual'])
            return True, f"Depósito exitoso de {self.formatear_moneda(monto)}."

        elif accion == 'retiro':
            limite_credito_disponible = cuenta['limite_credito'] - cuenta['deuda_actual']
            fondos_disponibles = cuenta['saldo'] + limite_credito_disponible

            if fondos_disponibles < monto:
                return False, "Fondos de cuenta y límite de crédito insuficientes."
            
            mensaje_tx = f"Retiro exitoso de {self.formatear_moneda(monto)}."
            tipo_tx = 'Retiro'
            monto_log = monto # Monto positivo para el registro

            if cuenta['saldo'] >= monto:
                cuenta['saldo'] -= monto
            else:
                necesario_credito = monto - cuenta['saldo']
                cuenta['saldo'] = 0.00 
                # NOTA: Al retirar usando crédito, la deuda actual SOLO AUMENTA por el principal retirado.
                # El 8% de interés solo se aplica al pedir el préstamo inicial completo.
                cuenta['deuda_actual'] += necesario_credito 
                tipo_tx = 'Retiro (Usando Crédito)'
                mensaje_tx = (f"Retiro de {self.formatear_moneda(monto)} exitoso. "
                              f"Se usaron {self.formatear_moneda(necesario_credito)} de la línea de crédito.")

            self._crear_transaccion(self.id_cuenta_actual, tipo_tx, monto_log, cuenta['saldo'], cuenta['deuda_actual'])
            return True, mensaje_tx

        elif accion == 'pagar_deuda':
            if cuenta['deuda_actual'] == 0:
                return False, "No tienes deuda de crédito para pagar."
            
            if cuenta['saldo'] < monto:
                return False, "Saldo insuficiente para pagar la deuda."
            
            # El monto a pagar no puede ser mayor que la deuda
            monto_pagado = min(monto, cuenta['deuda_actual'])
            
            cuenta['saldo'] -= monto_pagado
            cuenta['deuda_actual'] -= monto_pagado
            
            self._crear_transaccion(self.id_cuenta_actual, 'Pago Deuda', -monto_pagado, cuenta['saldo'], cuenta['deuda_actual'])
            return True, f"Pago de deuda exitoso de {self.formatear_moneda(monto_pagado)}."
        
        return False, "Acción desconocida."

    def aplicar_ciclo_periodico(self):
        """
        Aplica el ciclo periódico: Impuesto Fijo ($2.50) + Pago mínimo del 10% de la deuda.
        """
        if not self.id_cuenta_actual:
            return False, "Error: No hay cuenta activa."
            
        cuenta = self.CUENTAS[self.id_cuenta_actual]
        
        monto_impuesto = 2.50
        pago_minimo_deuda = 0.0
        
        # 1. Calcular el pago mínimo de deuda (10%) si existe deuda
        if cuenta['deuda_actual'] > 0:
            pago_minimo_deuda = round(0.10 * cuenta['deuda_actual'], 2) # Redondear a dos decimales
        
        # 2. Sumar el impuesto fijo
        pago_total_requerido = monto_impuesto + pago_minimo_deuda
        
        # 3. Verificar saldo para el pago total
        if cuenta['saldo'] >= pago_total_requerido:
            # Aplicar cargos
            cuenta['saldo'] -= pago_total_requerido
            
            # Aplicar pago de deuda (si aplica)
            if pago_minimo_deuda > 0:
                cuenta['deuda_actual'] -= pago_minimo_deuda
                tipo_tx = 'Ciclo (Impuestos + Pago Deuda)'
            else:
                tipo_tx = 'Ciclo (Impuestos)'
                
            self._crear_transaccion(self.id_cuenta_actual, tipo_tx, -pago_total_requerido, cuenta['saldo'], cuenta['deuda_actual'])
            
            # Generar mensaje de resumen
            resumen_mensaje = [f"Ciclo Periódico Aplicado (Total: {self.formatear_moneda(pago_total_requerido)}):"]
            if pago_minimo_deuda > 0:
                 resumen_mensaje.append(f"- {self.formatear_moneda(pago_minimo_deuda)} (Pago Mínimo Deuda 10%)")
            resumen_mensaje.append(f"- {self.formatear_moneda(monto_impuesto)} (Impuesto Fijo)")
            
            return True, "\n".join(resumen_mensaje)
            
        else:
            # Saldo insuficiente.
            self._crear_transaccion(self.id_cuenta_actual, 'Ciclo Fallido', -pago_total_requerido, cuenta['saldo'], cuenta['deuda_actual'], exito=False)
            
            # Generar mensaje de advertencia
            resumen_mensaje = [f"ADVERTENCIA: Ciclo Fallido. Saldo insuficiente para cubrir el total de {self.formatear_moneda(pago_total_requerido)}."]
            if pago_minimo_deuda > 0:
                 resumen_mensaje.append(f"-> Mínimo Deuda requerido: {self.formatear_moneda(pago_minimo_deuda)}")
            resumen_mensaje.append(f"-> Impuesto Fijo requerido: {self.formatear_moneda(monto_impuesto)}")
            
            return False, "\n".join(resumen_mensaje)

# --- 2. VISTA (VISTA): Interfaz Gráfica con Tkinter ---

class VistaBancaria(tk.Tk):
    """
    Crea y gestiona la interfaz gráfica (GUI) usando Tkinter.
    """
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.title("Simulador Bancario MVC")
        self.geometry("800x650")
        self.resizable(True, True)
        
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)

        self.frames = {}
        self._crear_widgets()
        self.mostrar_frame("PantallaInicioSesion")

    def _crear_widgets(self):
        """Crea las pantallas de Inicio de Sesión y la Aplicación Principal."""
        
        for F in (PantallaInicioSesion, PantallaAppPrincipal):
            nombre_pagina = F.__name__
            frame = F(padre=self.contenedor, controlador=self.controlador)
            self.frames[nombre_pagina] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_frame(self, nombre_pagina):
        """Muestra el frame solicitado y lo trae al frente."""
        frame = self.frames[nombre_pagina]
        frame.tkraise()
        if nombre_pagina == "PantallaAppPrincipal":
            self.controlador.actualizar_vista()

    def actualizar_vista_app_principal(self, datos):
        """Llama al método de actualización de la pantalla principal."""
        self.frames["PantallaAppPrincipal"].actualizar_pantalla(datos)

class PantallaInicioSesion(tk.Frame):
    """
    Pantalla para el ingreso de credenciales.
    """
    def __init__(self, padre, controlador):
        tk.Frame.__init__(self, padre)
        self.controlador = controlador
        self.config(bg="#f4f7f9")
        
        frame_login = tk.Frame(self, bg="#ffffff", padx=40, pady=40, bd=2, relief=tk.RIDGE)
        frame_login.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(frame_login, text="INICIO DE SESIÓN BANCARIO", font=('Arial', 18, 'bold'), fg="#1a237e", bg="#ffffff").pack(pady=10)
        
        # Usuario
        tk.Label(frame_login, text="Usuario (ID):", font=('Arial', 12), bg="#ffffff").pack(pady=5)
        self.entrada_usuario = tk.Entry(frame_login, width=30, font=('Arial', 12))
        self.entrada_usuario.pack(pady=5)
        
        # Contraseña
        tk.Label(frame_login, text="Contraseña:", font=('Arial', 12), bg="#ffffff").pack(pady=5)
        self.entrada_contrasena = tk.Entry(frame_login, show="*", width=30, font=('Arial', 12))
        self.entrada_contrasena.pack(pady=5)
        
        # Botón
        tk.Button(frame_login, text="INGRESAR", command=self.intentar_iniciar_sesion, 
                  bg="#3f51b5", fg="white", font=('Arial', 12, 'bold'), width=20).pack(pady=20)
        
        tk.Label(frame_login, text="Usuarios de prueba: usuario1, usuario2\nContraseñas: clave1, clave2", 
                 font=('Arial', 10), fg="#757575", bg="#ffffff").pack(pady=5)

    def intentar_iniciar_sesion(self):
        """Recoge las credenciales y llama al controlador."""
        usuario = self.entrada_usuario.get().strip().lower()
        contrasena = self.entrada_contrasena.get()

        success, mensaje = self.controlador.iniciar_sesion(usuario, contrasena)

        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.controlador.vista.mostrar_frame("PantallaAppPrincipal")
        else:
            messagebox.showerror("Error de Login", mensaje)
            self.entrada_contrasena.delete(0, tk.END)

class PantallaAppPrincipal(tk.Frame):
    """
    Pantalla principal de la aplicación bancaria con estado y transacciones.
    """
    def __init__(self, padre, controlador):
        tk.Frame.__init__(self, padre)
        self.controlador = controlador
        self.config(bg="#f4f7f9")
        
        main_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(main_frame, bg="#ffffff")
        header_frame.pack(fill='x', pady=10)
        tk.Label(header_frame, text="Mi Cuenta Bancaria", font=('Arial', 20, 'bold'), fg="#1a237e", bg="#ffffff").pack(side=tk.LEFT)
        tk.Button(header_frame, text="Cerrar Sesión", command=self.cerrar_sesion, bg="#ffcdd2", fg="#c62828").pack(side=tk.RIGHT)

        self._crear_seccion_resumen(main_frame)
        
        # Contenedor para Operaciones y Transferencias
        ops_container = tk.Frame(main_frame, bg="#ffffff")
        ops_container.pack(fill='x', pady=10)
        
        self._crear_seccion_transaccion(ops_container).pack(side=tk.LEFT, fill='x', expand=True, padx=10)
        self._crear_seccion_transferencia(ops_container).pack(side=tk.LEFT, fill='x', expand=True, padx=10)
        
        self._crear_seccion_historial(main_frame)
        
    def _crear_seccion_resumen(self, padre):
        """Crea las etiquetas para mostrar saldo y deuda."""
        resumen_frame = tk.LabelFrame(padre, text="Resumen General", font=('Arial', 12, 'bold'), bg="#e8eaf6", bd=2, relief=tk.SOLID, padx=15, pady=10)
        resumen_frame.pack(fill='x', pady=10)
        
        self.lbl_propietario = tk.Label(resumen_frame, text="Propietario: ", font=('Arial', 12), bg="#e8eaf6")
        self.lbl_saldo = tk.Label(resumen_frame, text="Saldo: ", font=('Arial', 16, 'bold'), fg="#388e3c", bg="#e8eaf6")
        self.lbl_deuda = tk.Label(resumen_frame, text="Deuda: ", font=('Arial', 14, 'bold'), fg="#d32f2f", bg="#e8eaf6")
        self.lbl_credito = tk.Label(resumen_frame, text="Límite Crédito: ", font=('Arial', 10), bg="#e8eaf6")
        
        self.lbl_propietario.pack(side=tk.LEFT, padx=10)
        self.lbl_saldo.pack(side=tk.LEFT, padx=30)
        self.lbl_deuda.pack(side=tk.LEFT, padx=30)
        self.lbl_credito.pack(side=tk.LEFT, padx=30)
        
        return resumen_frame

    def _crear_seccion_transaccion(self, padre):
        """Crea los campos y botones para Depósito, Retiro, Pago Deuda y Crédito."""
        tx_frame = tk.LabelFrame(padre, text="Operaciones de Cuenta y Crédito", font=('Arial', 12, 'bold'), padx=15, pady=10)
        
        # Fila 1: Monto para Operaciones
        tk.Label(tx_frame, text="Monto Operación:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entrada_monto_operacion = tk.Entry(tx_frame, width=15, font=('Arial', 12))
        self.entrada_monto_operacion.grid(row=0, column=1, padx=5, pady=5)
        
        # Fila 2: Transacciones Básicas
        tk.Button(tx_frame, text="Depósito", command=lambda: self.procesar_transaccion('deposito', self.entrada_monto_operacion), 
                  bg="#4caf50", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        tk.Button(tx_frame, text="Retiro/Gasto", command=lambda: self.procesar_transaccion('retiro', self.entrada_monto_operacion), 
                  bg="#ff9800", fg="white").grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Fila 3: Operaciones de Crédito
        tk.Button(tx_frame, text="Pagar Deuda", command=lambda: self.procesar_transaccion('pagar_deuda', self.entrada_monto_operacion), 
                  bg="#2196f3", fg="white").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        tk.Button(tx_frame, text="SOLICITAR CRÉDITO", command=lambda: self.procesar_solicitud_credito(self.entrada_monto_operacion), 
                  bg="#673ab7", fg="white").grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # Fila 4: Ciclo Periódico (Impuestos + Deuda Mínima)
        tk.Button(tx_frame, text="Aplicar Ciclo (Impuestos + 10% Deuda)", command=self.procesar_ciclo_periodico, 
                  bg="#9c27b0", fg="white").grid(row=3, column=0, columnspan=2, pady=10)
        
        return tx_frame

    def _crear_seccion_transferencia(self, padre):
        """Crea la sección específica para transferencias."""
        transf_frame = tk.LabelFrame(padre, text="Transferencias entre Cuentas", font=('Arial', 12, 'bold'), padx=15, pady=10)

        # Fila 1: Monto de Transferencia
        tk.Label(transf_frame, text="Monto a Transferir:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entrada_monto_transferencia = tk.Entry(transf_frame, width=15, font=('Arial', 12))
        self.entrada_monto_transferencia.grid(row=0, column=1, padx=5, pady=5)
        
        # Fila 2: Cuenta Destino
        tk.Label(transf_frame, text="ID Cuenta Destino:", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.entrada_destino = tk.Entry(transf_frame, width=15, font=('Arial', 12))
        self.entrada_destino.grid(row=1, column=1, padx=5, pady=5)

        # Botón de Transferencia
        tk.Button(transf_frame, text="TRANSFERIR DINERO", command=self.procesar_transferencia, 
                  bg="#00bcd4", fg="white").grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        tk.Label(transf_frame, text="Cuentas disponibles: usuario1, usuario2", 
                 font=('Arial', 8), fg="#757575").grid(row=3, column=0, columnspan=2)
        
        return transf_frame


    def _crear_seccion_historial(self, padre):
        """Crea el área de texto para mostrar el historial de transacciones."""
        historial_frame = tk.LabelFrame(padre, text="Historial de Movimientos (Últimas 30)", font=('Arial', 12, 'bold'), padx=15, pady=10)
        historial_frame.pack(fill='both', expand=True, pady=10)

        scrollbar = tk.Scrollbar(historial_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.texto_historial = tk.Text(historial_frame, height=15, wrap=tk.WORD, font=('Courier', 10), yscrollcommand=scrollbar.set)
        self.texto_historial.pack(fill='both', expand=True)
        scrollbar.config(command=self.texto_historial.yview)
        
    def _obtener_monto_valido(self, entrada_widget):
        """Intenta convertir el texto de un widget Entry a un flotante."""
        try:
            monto = float(entrada_widget.get())
            return monto
        except ValueError:
            messagebox.showerror("Error de Entrada", "Por favor, introduce un monto numérico válido.")
            return None
        
    def procesar_transaccion(self, accion, entrada_widget):
        """Recoge el monto y llama al controlador para ejecutar la transacción."""
        monto = self._obtener_monto_valido(entrada_widget)
        if monto is None: return

        self.controlador.ejecutar_transaccion(accion, monto)
        entrada_widget.delete(0, tk.END) # Limpiar campo

    def procesar_solicitud_credito(self, entrada_widget):
        """Recoge el monto y llama al controlador para solicitar crédito."""
        monto = self._obtener_monto_valido(entrada_widget)
        if monto is None: return

        if monto <= 0:
            messagebox.showerror("Error de Entrada", "El monto del crédito debe ser positivo.")
            return

        self.controlador.solicitar_credito(monto)
        entrada_widget.delete(0, tk.END) # Limpiar campo

    def procesar_transferencia(self):
        """Recoge el monto y destino y llama al controlador para transferir."""
        monto = self._obtener_monto_valido(self.entrada_monto_transferencia)
        if monto is None: return
        
        id_destino = self.entrada_destino.get().strip().lower()

        self.controlador.procesar_transferencia(id_destino, monto)
        self.entrada_monto_transferencia.delete(0, tk.END)
        self.entrada_destino.delete(0, tk.END)

    def procesar_ciclo_periodico(self):
        """Llama al controlador para ejecutar el ciclo periódico."""
        self.controlador.aplicar_ciclo_periodico()

    def actualizar_pantalla(self, datos):
        """Actualiza todas las etiquetas de la GUI con los datos del modelo."""
        if not datos:
            return

        fmt = self.controlador.modelo.formatear_moneda
        
        # 1. Resumen de cuenta
        id_actual = self.controlador.modelo.id_cuenta_actual
        self.lbl_propietario.config(text=f"Propietario: {datos['nombre_propietario']} (ID: {id_actual})")
        
        color_saldo = "#388e3c" if datos['saldo'] >= 0 else "#e53935"
        self.lbl_saldo.config(text=f"Saldo: {fmt(datos['saldo'])}", fg=color_saldo)
        
        color_deuda = "#d32f2f" if datos['deuda_actual'] > 0 else "#757575"
        self.lbl_deuda.config(text=f"Deuda Actual: {fmt(datos['deuda_actual'])}", fg=color_deuda)
        
        credito_disponible = datos['limite_credito'] - datos['deuda_actual']
        self.lbl_credito.config(text=f"Límite Crédito: {fmt(datos['limite_credito'])} (Disponible: {fmt(credito_disponible)})")

        # 2. Historial
        self.texto_historial.delete('1.0', tk.END)
        encabezado = f"{'Fecha':<20} | {'Tipo':<30} | {'Monto':<15} | {'Saldo Final':<15}\n"
        self.texto_historial.insert(tk.END, encabezado)
        self.texto_historial.insert(tk.END, "-" * 85 + "\n")
        
        if not datos['transacciones']:
            self.texto_historial.insert(tk.END, "Aún no hay transacciones.\n")
            return
            
        for tx in datos['transacciones']:
            monto_str = fmt(abs(tx['monto']))
            
            tipo_display = tx['tipo']
            if tx['tipo'].startswith('Transferencia Enviada'):
                monto_display = f"- {monto_str}"
                color_linea = "#c62828"
            elif tx['tipo'].startswith('Transferencia Recibida'):
                monto_display = f"+ {monto_str}"
                color_linea = "#388e3c"
            elif not tx['exito']:
                monto_display = f"[{monto_str}] FALLIDA"
                color_linea = "#f9a825"
            else:
                # Retiros y pagos de deuda se muestran como negativos o positivos
                monto_display = f"{monto_str}" if tx['monto'] > 0 else f"- {monto_str}"
                color_linea = "black"

            linea = f"{tx['fecha']:<20} | {tipo_display:<30} | {monto_display:<15} | {fmt(tx['saldo_final']):<15}\n"
            
            self.texto_historial.insert(tk.END, linea, color_linea)
            self.texto_historial.tag_config("#c62828", foreground="#c62828")
            self.texto_historial.tag_config("#388e3c", foreground="#388e3c")
            self.texto_historial.tag_config("#f9a825", foreground="#f9a825")
            self.texto_historial.tag_config("black", foreground="black")


    def cerrar_sesion(self):
        """Maneja el cierre de sesión."""
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que quieres cerrar la sesión?"):
            self.controlador.cerrar_sesion()
            self.controlador.vista.mostrar_frame("PantallaInicioSesion")

# --- 3. CONTROLADOR (CONTROLLER): Conexión entre Modelo y Vista ---

class ControladorBancario:
    """
    Controla el flujo de la aplicación, maneja la entrada del usuario
    y coordina las actualizaciones entre el Modelo y la Vista.
    """
    def __init__(self):
        self.modelo = ModeloBancario()
        self.vista = VistaBancaria(self)

    def ejecutar(self):
        """Inicia el bucle principal de la aplicación."""
        self.vista.mainloop()

    def iniciar_sesion(self, id_usuario, contrasena):
        """Intenta iniciar sesión en el modelo."""
        return self.modelo.iniciar_sesion(id_usuario, contrasena)

    def cerrar_sesion(self):
        """Cierra la sesión en el modelo."""
        self.modelo.cerrar_sesion()

    def actualizar_vista(self):
        """Fuerza a la vista a refrescarse con los datos actuales del modelo."""
        datos = self.modelo.obtener_datos_cuenta()
        self.vista.actualizar_vista_app_principal(datos)
        
    def ejecutar_transaccion(self, accion, monto):
        """Maneja el evento de transacción desde la Vista."""
        exito, mensaje = self.modelo.ejecutar_transaccion(accion, monto)
        
        if exito:
            messagebox.showinfo("Transacción Exitosa", mensaje)
            self.actualizar_vista()
        else:
            messagebox.showerror("Transacción Fallida", mensaje)

    def solicitar_credito(self, monto):
        """Maneja la solicitud de crédito desde la Vista."""
        exito, mensaje = self.modelo.solicitar_credito(monto)
        
        if exito:
            messagebox.showinfo("Crédito Aprobado", mensaje)
            self.actualizar_vista()
        else:
            messagebox.showerror("Crédito Denegado", mensaje)
            
    def procesar_transferencia(self, id_destino, monto):
        """Maneja el evento de transferencia desde la Vista."""
        exito, mensaje = self.modelo.realizar_transferencia(id_destino, monto)
        
        if exito:
            messagebox.showinfo("Transferencia Exitosa", mensaje)
            self.actualizar_vista() 
        else:
            messagebox.showerror("Transferencia Fallida", mensaje)


    def aplicar_ciclo_periodico(self):
        """Maneja el evento de ciclo periódico desde la Vista."""
        exito, mensaje = self.modelo.aplicar_ciclo_periodico()
        
        if exito:
            messagebox.showinfo("Ciclo Aplicado", mensaje)
            self.actualizar_vista()
        else:
            messagebox.showwarning("Advertencia", mensaje)

# --- PUNTO DE ENTRADA ---

if __name__ == "__main__":
    app = ControladorBancario()
    app.ejecutar()
