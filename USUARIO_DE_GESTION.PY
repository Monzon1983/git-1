import uuid
import datetime
import qrcode # Necesitarías instalar esta librería: pip install qrcode

# --- 1. Autenticación y Autorización de Usuario ---

class User:
    """Representa a un usuario del sistema con rol y credenciales."""
    def __init__(self, username, password, role):
        self.username = username
        self.password = password # En un sistema real, la contraseña debe ser hasheada
        self.role = role # Ej: 'admin', 'vendedor', 'almacen'

    def __repr__(self):
        return f"User(username='{self.username}', role='{self.role}')"

class AuthSystem:
    """Simula el sistema de autenticación y autorización."""
    def __init__(self):
        self.users = {} # {username: User_object}
        self.current_user = None

    def register_user(self, username, password, role):
        """Historia de Usuario: Registro de Nuevo Usuario"""
        if username in self.users:
            print(f"Error: El usuario '{username}' ya existe.")
            return False
        new_user = User(username, password, role)
        self.users[username] = new_user
        print(f"Usuario '{username}' registrado con rol '{role}'.")
        return True

    def login(self, username, password):
        """Historia de Usuario: Inicio de Sesión Seguro"""
        user = self.users.get(username)
        if user and user.password == password: # Simplicado: no hay hashing
            self.current_user = user
            print(f"Login exitoso para '{username}' como '{user.role}'.")
            return True
        print("Error: Credenciales inválidas.")
        self.current_user = None
        return False

    def logout(self):
        self.current_user = None
        print("Sesión cerrada.")

    def has_permission(self, required_role):
        """Simula la verificación de permisos basada en el rol."""
        if not self.current_user:
            return False
        # Para roles más complejos, se usaría un sistema de permisos detallado
        if self.current_user.role == 'admin':
            return True # El admin tiene todos los permisos
        return self.current_user.role == required_role

# --- 2. Gestión de Ventas de Productos ---

class Product:
    """Representa un producto en el inventario."""
    def __init__(self, product_id, name, description, price, cost, stock):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price # Precio de venta
        self.cost = cost   # Costo de adquisición (para cálculo de ganancias)
        self.stock = stock

    def __repr__(self):
        return f"Product(ID:{self.product_id}, {self.name}, Stock:{self.stock}, Price:{self.price})"

class Sale:
    """Representa una transacción de venta."""
    def __init__(self, sale_id, products_sold, total_amount, seller_id, sale_date=None, payment_method="Efectivo"):
        self.sale_id = sale_id
        self.products_sold = products_sold # Lista de {'product': Product, 'quantity': int}
        self.total_amount = total_amount
        self.seller_id = seller_id
        self.sale_date = sale_date if sale_date else datetime.datetime.now()
        self.payment_method = payment_method
        self.tracking_id = None # Para el seguimiento de envío
        self.qr_data = None     # Para el código QR

    def calculate_profit(self):
        """Calcula la ganancia para esta venta específica."""
        total_cost_sold = sum(item['product'].cost * item['quantity'] for item in self.products_sold)
        return self.total_amount - total_cost_sold

    def __repr__(self):
        return f"Sale(ID:{self.sale_id}, Total:${self.total_amount:.2f}, Seller:{self.seller_id})"

class SalesManagement:
    """Gestiona productos y ventas."""
    def __init__(self):
        self.products = {} # {product_id: Product_object}
        self.sales = [] # Lista de Sale_objects
        self.next_sale_id = 1

    def add_product(self, product_id, name, description, price, cost, stock):
        """Simula la adición de productos al catálogo."""
        if product_id in self.products:
            print(f"Error: Producto con ID '{product_id}' ya existe.")
            return False
        self.products[product_id] = Product(product_id, name, description, price, cost, stock)
        print(f"Producto '{name}' agregado.")
        return True

    def record_sale(self, product_quantities, seller_id):
        """Historia de Usuario: Registro de Nueva Venta"""
        products_for_sale = []
        total_amount = 0
        for prod_id, quantity in product_quantities.items():
            product = self.products.get(prod_id)
            if not product:
                print(f"Error: Producto con ID '{prod_id}' no encontrado.")
                return None
            if product.stock < quantity:
                print(f"Error: Stock insuficiente para '{product.name}'. Disponible: {product.stock}, Solicitado: {quantity}.")
                return None
            
            products_for_sale.append({'product': product, 'quantity': quantity})
            total_amount += product.price * quantity

        # Si todo está bien, actualiza el stock y crea la venta
        for item in products_for_sale:
            item['product'].stock -= item['quantity']
        
        sale_id = f"VNT-{self.next_sale_id:05d}"
        new_sale = Sale(sale_id, products_for_sale, total_amount, seller_id)
        self.sales.append(new_sale)
        self.next_sale_id += 1
        print(f"Venta '{sale_id}' registrada por el vendedor '{seller_id}'. Total: ${total_amount:.2f}")
        return new_sale

    def generate_invoice(self, sale_id):
        """Historia de Usuario: Generación de Factura/Recibo"""
        sale = next((s for s in self.sales if s.sale_id == sale_id), None)
        if sale:
            print(f"\n--- FACTURA/RECIBO para Venta ID: {sale.sale_id} ---")
            print(f"Fecha: {sale.sale_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Vendedor: {sale.seller_id}")
            print("Productos:")
            for item in sale.products_sold:
                prod = item['product']
                qty = item['quantity']
                print(f"  - {prod.name} (x{qty}) @ ${prod.price:.2f} = ${prod.price * qty:.2f}")
            print(f"Total: ${sale.total_amount:.2f}")
            print("--- FIN FACTURA ---\n")
            return True
        print(f"Error: Venta con ID '{sale_id}' no encontrada.")
        return False

# --- 3. Seguimiento de Envío, Código QR y Palabras de Tracking ---

class ShippingManagement:
    """Gestiona el seguimiento de envíos."""
    def __init__(self):
        self.tracking_data = {} # {tracking_id: {'sale_id': sale_id, 'status': 'Preparado', 'history': []}}

    def generate_tracking_info(self, sale):
        """Historia de Usuario: Generación de Código QR y Palabra de Tracking"""
        tracking_id = str(uuid.uuid4())[:8].upper() # Genera un ID de tracking corto
        tracking_word = "ENVIOPR" + str(len(self.tracking_data) + 1).zfill(4) # Una palabra de tracking simple

        qr_content = f"ID Pedido: {sale.sale_id}\nTracking: {tracking_id}\nURL: [TuDominio.com/tracking?id={tracking_id}]"
        
        # Simula la generación de QR (en un sistema real se guardaría como imagen)
        img = qrcode.make(qr_content)
        # img.save(f"qr_pedido_{sale.sale_id}.png") # Descomentar para guardar imagen
        
        sale.tracking_id = tracking_id
        sale.qr_data = qr_content # Almacena el contenido del QR
        self.tracking_data[tracking_id] = {
            'sale_id': sale.sale_id,
            'tracking_word': tracking_word,
            'status': 'Preparado',
            'history': [{'timestamp': datetime.datetime.now(), 'status': 'Preparado'}]
        }
        print(f"Info de tracking generada para Venta ID {sale.sale_id}: QR Content='{qr_content[:30]}...', Tracking ID: '{tracking_id}', Palabra de Tracking: '{tracking_word}'")
        return tracking_id, tracking_word, qr_content

    def update_tracking_status(self, tracking_id, new_status):
        """Historia de Usuario: Actualización de Estado de Envío mediante QR o Tracking"""
        data = self.tracking_data.get(tracking_id)
        if data:
            data['status'] = new_status
            data['history'].append({'timestamp': datetime.datetime.now(), 'status': new_status})
            print(f"Tracking ID '{tracking_id}' actualizado a '{new_status}'.")
            return True
        print(f"Error: Tracking ID '{tracking_id}' no encontrado.")
        return False

    def get_tracking_status(self, tracking_id_or_word):
        """Historia de Usuario: Consulta de Estado de Envío por el Cliente"""
        for tid, data in self.tracking_data.items():
            if tid == tracking_id_or_word or data['tracking_word'] == tracking_id_or_word.upper():
                print(f"\n--- ESTADO DEL ENVÍO para Tracking ID: {tid} ({data['tracking_word']}) ---")
                print(f"Estado Actual: {data['status']}")
                print("Historial:")
                for entry in data['history']:
                    print(f"  - {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}: {entry['status']}")
                print("--- FIN ESTADO DE ENVÍO ---\n")
                return data
        print(f"Error: No se encontró información de seguimiento para '{tracking_id_or_word}'.")
        return None

# --- 4. Datos del Vendedor, Balance, Ganancias y Comisiones ---

class FinancialReporting:
    """Genera reportes financieros."""
    def __init__(self, sales_manager):
        self.sales_manager = sales_manager
        self.commission_rate = 0.05 # Ejemplo: 5% de comisión

    def get_seller_performance(self, seller_id):
        """Historia de Usuario: Visualización de Datos del Vendedor"""
        seller_sales = [s for s in self.sales_manager.sales if s.seller_id == seller_id]
        total_sales_amount = sum(s.total_amount for s in seller_sales)
        total_commission = total_sales_amount * self.commission_rate
        print(f"\n--- Rendimiento del Vendedor: {seller_id} ---")
        print(f"Total de Ventas Realizadas: {len(seller_sales)}")
        print(f"Monto Total de Ventas: ${total_sales_amount:.2f}")
        print(f"Comisión Acumulada (a {self.commission_rate*100}%): ${total_commission:.2f}")
        print("--- FIN RENDIMIENTO ---\n")
        return {'total_sales_amount': total_sales_amount, 'total_commission': total_commission}

    def get_sales_balance(self, start_date, end_date):
        """Historia de Usuario: Consulta del Balance de Venta por Período"""
        sales_in_period = [s for s in self.sales_manager.sales if start_date <= s.sale_date <= end_date]
        total_revenue = sum(s.total_amount for s in sales_in_period)
        total_cost_of_goods_sold = sum(s.total_amount - s.calculate_profit() for s in sales_in_period)
        
        gross_profit = total_revenue - total_cost_of_goods_sold
        profit_percentage = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

        print(f"\n--- Balance de Ventas ({start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}) ---")
        print(f"Ingresos Totales: ${total_revenue:.2f}")
        print(f"Costo Total de Bienes Vendidos: ${total_cost_of_goods_sold:.2f}")
        print(f"Ganancia Bruta: ${gross_profit:.2f}")
        print(f"Porcentaje de Ganancia Bruta: {profit_percentage:.2f}%")
        print("--- FIN BALANCE ---\n")
        return {'revenue': total_revenue, 'cost': total_cost_of_goods_sold, 'profit': gross_profit, 'profit_percentage': profit_percentage}

    def get_commission_for_seller(self, seller_id, start_date, end_date):
        """Historia de Usuario: Cálculo y Visualización de Comisiones de Venta"""
        seller_sales_in_period = [s for s in self.sales_manager.sales if s.seller_id == seller_id and start_date <= s.sale_date <= end_date]
        total_sales_amount = sum(s.total_amount for s in seller_sales_in_period)
        commission = total_sales_amount * self.commission_rate
        print(f"Comisión para {seller_id} entre {start_date.strftime('%Y-%m-%d')} y {end_date.strftime('%Y-%m-%d')}: ${commission:.2f}")
        return commission

# --- 5. RANKING de Producto Más y Menos Vendido ---

class ProductAnalytics:
    """Analiza el rendimiento de los productos."""
    def __init__(self, sales_manager):
        self.sales_manager = sales_manager

    def get_product_sales_counts(self, start_date=None, end_date=None):
        """Calcula el total de unidades vendidas por producto."""
        product_sales_counts = {}
        sales_to_consider = self.sales_manager.sales
        if start_date and end_date:
            sales_to_consider = [s for s in sales_to_consider if start_date <= s.sale_date <= end_date]

        for sale in sales_to_consider:
            for item in sale.products_sold:
                product_id = item['product'].product_id
                quantity = item['quantity']
                product_sales_counts[product_id] = product_sales_counts.get(product_id, 0) + quantity
        return product_sales_counts

    def get_top_n_sold_products(self, n=5, start_date=None, end_date=None):
        """Historia de Usuario: Visualización de Ranking de Productos Más Vendidos"""
        product_sales_counts = self.get_product_sales_counts(start_date, end_date)
        sorted_products = sorted(product_sales_counts.items(), key=lambda item: item[1], reverse=True)
        
        print(f"\n--- Ranking de Productos Más Vendidos ({start_date.strftime('%Y-%m-%d') if start_date else 'Siempre'} a {end_date.strftime('%Y-%m-%d') if end_date else 'Ahora'}) ---")
        for i, (prod_id, count) in enumerate(sorted_products[:n]):
            prod_name = self.sales_manager.products[prod_id].name
            print(f"{i+1}. {prod_name} (ID: {prod_id}): {count} unidades vendidas.")
        print("--- FIN RANKING ---\n")
        return sorted_products[:n]

    def get_least_n_sold_products(self, n=5, start_date=None, end_date=None):
        """Historia de Usuario: Visualización de Ranking de Productos Menos Vendidos"""
        product_sales_counts = self.get_product_sales_counts(start_date, end_date)
        # Asegurarse de incluir productos que no se hayan vendido
        all_product_ids = set(self.sales_manager.products.keys())
        for prod_id in all_product_ids:
            if prod_id not in product_sales_counts:
                product_sales_counts[prod_id] = 0

        sorted_products = sorted(product_sales_counts.items(), key=lambda item: item[1])
        
        print(f"\n--- Ranking de Productos Menos Vendidos ({start_date.strftime('%Y-%m-%d') if start_date else 'Siempre'} a {end_date.strftime('%Y-%m-%d') if end_date else 'Ahora'}) ---")
        for i, (prod_id, count) in enumerate(sorted_products[:n]):
            prod_name = self.sales_manager.products[prod_id].name
            print(f"{i+1}. {prod_name} (ID: {prod_id}): {count} unidades vendidas.")
        print("--- FIN RANKING ---\n")
        return sorted_products[:n]

# --- Demo de uso ---
if __name__ == "__main__":
    auth_sys = AuthSystem()
    sales_sys = SalesManagement()
    shipping_sys = ShippingManagement()
    finance_reports = FinancialReporting(sales_sys)
    product_analytics = ProductAnalytics(sales_sys)

    # Autenticación y Autorización
    print("--- Demostración de Autenticación y Autorización ---")
    auth_sys.register_user("admin_user", "admin123", "admin")
    auth_sys.register_user("juan_vendedor", "pass4juan", "vendedor")
    auth_sys.register_user("ana_almacen", "pass4ana", "almacen")

    auth_sys.login("admin_user", "admin123")
    print(f"¿Admin puede registrar usuarios? {auth_sys.has_permission('admin')}")
    auth_sys.logout()

    auth_sys.login("juan_vendedor", "pass4juan")
    print(f"¿Vendedor puede registrar usuarios? {auth_sys.has_permission('admin')}")
    print(f"¿Vendedor puede hacer ventas? {auth_sys.has_permission('vendedor')}")
    auth_sys.logout()
    print("-" * 50)

    # Gestión de Productos y Ventas
    print("\n--- Demostración de Gestión de Productos y Ventas ---")
    sales_sys.add_product("P001", "Laptop Gamer", "Potente laptop para juegos", 1200.00, 900.00, 10)
    sales_sys.add_product("P002", "Teclado Mecánico", "Teclado RGB", 80.00, 50.00, 20)
    sales_sys.add_product("P003", "Mouse Inalámbrico", "Mouse ergonómico", 30.00, 15.00, 30)
    sales_sys.add_product("P004", "Monitor Curvo 27", "Monitor de alta resolución", 350.00, 250.00, 5)

    # Realizar ventas
    auth_sys.login("juan_vendedor", "pass4juan") # Simula login del vendedor
    if auth_sys.current_user and auth_sys.has_permission('vendedor'):
        print("\nRealizando ventas...")
        sale1 = sales_sys.record_sale({"P001": 1, "P002": 2}, auth_sys.current_user.username)
        sale2 = sales_sys.record_sale({"P003": 5}, auth_sys.current_user.username)
        # Venta con stock insuficiente
        sales_sys.record_sale({"P004": 10}, auth_sys.current_user.username)
        sale3 = sales_sys.record_sale({"P004": 2, "P002": 1}, auth_sys.current_user.username)
        
        if sale1: sales_sys.generate_invoice(sale1.sale_id)
        if sale2: sales_sys.generate_invoice(sale2.sale_id)
    auth_sys.logout()
    print("-" * 50)

    # Seguimiento de Envío y QR
    print("\n--- Demostración de Seguimiento de Envío y QR ---")
    if sale1:
        auth_sys.login("ana_almacen", "pass4ana") # Simula login del personal de almacén
        if auth_sys.current_user and auth_sys.has_permission('almacen'):
            tracking_id1, tracking_word1, qr_data1 = shipping_sys.generate_tracking_info(sale1)
            shipping_sys.update_tracking_status(tracking_id1, "En Ruta")
            shipping_sys.update_tracking_status(tracking_id1, "Entregado")
        auth_sys.logout()

        # Cliente consulta el estado
        print("\n--- Cliente consulta estado de envío ---")
        shipping_sys.get_tracking_status(tracking_id1)
        shipping_sys.get_tracking_status(tracking_word1) # Usando la palabra de tracking
    print("-" * 50)

    # Datos del Vendedor, Balance, Ganancias y Comisiones
    print("\n--- Demostración de Reportes Financieros ---")
    auth_sys.login("admin_user", "admin123")
    if auth_sys.current_user and auth_sys.has_permission('admin'):
        finance_reports.get_seller_performance("juan_vendedor")
        
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        # Asegurarse de que las ventas estén dentro de un rango de fechas realista para la demo
        # En una aplicación real, las fechas de venta serían dinámicas o fijadas a mano para pruebas
        
        # Simulamos que las ventas ocurrieron hoy
        finance_reports.get_sales_balance(yesterday, today + datetime.timedelta(days=1))
        finance_reports.get_commission_for_seller("juan_vendedor", yesterday, today + datetime.timedelta(days=1))
    auth_sys.logout()
    print("-" * 50)

    # Ranking de Productos
    print("\n--- Demostración de Ranking de Productos ---")
    auth_sys.login("admin_user", "admin123")
    if auth_sys.current_user and auth_sys.has_permission('admin'):
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        product_analytics.get_top_n_sold_products(3, yesterday, today + datetime.timedelta(days=1))
        product_analytics.get_least_n_sold_products(3, yesterday, today + datetime.timedelta(days=1))
    auth_sys.logout()
    print("-" * 50)
    