from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename
from models.database import hash_password

vendor_bp = Blueprint('vendor', __name__, url_prefix='/vendor')

def db_connection(app):
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename, app):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@vendor_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        brand_name = request.form.get('brand_name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        db = db_connection(current_app._get_current_object())
        try:
            db.execute(
                '''INSERT INTO vendors (name, email, password, brand_name, phone, address)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (name, email, hash_password(password), brand_name, phone, address)
            )
            db.commit()
            flash('Registration successful! Wait for admin approval.', 'success')
            return redirect(url_for('vendor.login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'error')
        finally:
            db.close()
    
    return render_template('vendor/register.html')

@vendor_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = db_connection(current_app._get_current_object())
        vendor = db.execute(
            'SELECT * FROM vendors WHERE email = ? AND password = ?',
            (email, hash_password(password))
        ).fetchone()
        db.close()
        
        if vendor:
            if vendor['status'] != 'approved':
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('vendor.login'))
            session['vendor_id'] = vendor['id']
            session['vendor_name'] = vendor['name']
            session['vendor_role'] = 'vendor'
            flash(f'Welcome, {vendor["brand_name"]}!', 'success')
            return redirect(url_for('vendor.dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    
    return render_template('vendor/login.html')

@vendor_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@vendor_bp.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor.login'))
    
    db = db_connection(current_app._get_current_object())
    vendor = db.execute('SELECT * FROM vendors WHERE id = ?', (session['vendor_id'],)).fetchone()
    products = db.execute('SELECT * FROM products WHERE vendor_id = ? ORDER BY created_at DESC LIMIT 5', 
                          (session['vendor_id'],)).fetchall()
    
    total_products = db.execute('SELECT COUNT(*) as c FROM products WHERE vendor_id = ?', 
                                (session['vendor_id'],)).fetchone()['c']
    total_orders = db.execute('SELECT COUNT(*) as c FROM orders WHERE vendor_id = ?', 
                              (session['vendor_id'],)).fetchone()['c']
    total_revenue = db.execute('SELECT SUM(total_price) as r FROM orders WHERE vendor_id = ? AND status != "cancelled"', 
                               (session['vendor_id'],)).fetchone()['r'] or 0
    
    recent_orders = db.execute('''
        SELECT o.*, u.name as user_name, p.name as product_name
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        WHERE o.vendor_id = ?
        ORDER BY o.created_at DESC LIMIT 5
    ''', (session['vendor_id'],)).fetchall()
    
    db.close()
    return render_template('vendor/dashboard.html', vendor=vendor, products=products,
                           total_products=total_products, total_orders=total_orders,
                           total_revenue=total_revenue, recent_orders=recent_orders)

@vendor_bp.route('/products')
def products():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor.login'))
    
    db = db_connection(current_app._get_current_object())
    products = db.execute('SELECT * FROM products WHERE vendor_id = ? ORDER BY created_at DESC', 
                          (session['vendor_id'],)).fetchall()
    db.close()
    return render_template('vendor/products.html', products=products)

@vendor_bp.route('/product/add', methods=['GET', 'POST'])
def add_product():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        gender = request.form.get('gender')
        price = request.form.get('price')
        size = request.form.get('size')
        color = request.form.get('color')
        occasion = request.form.get('occasion')
        climate = request.form.get('climate')
        body_type = request.form.get('body_type')
        skin_tone = request.form.get('skin_tone')
        stock = request.form.get('stock', 0)
        
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename, current_app._get_current_object()):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"product_{session['vendor_id']}_{uuid.uuid4().hex[:10]}.{ext}"
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                image_filename = filename
        
        db = db_connection(current_app._get_current_object())
        db.execute('''
            INSERT INTO products (vendor_id, name, description, category, gender, price, 
                                  size, color, occasion, climate, body_type, skin_tone, image, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['vendor_id'], name, description, category, gender, price,
              size, color, occasion, climate, body_type, skin_tone, image_filename, stock))
        db.commit()
        db.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('vendor.products'))
    
    return render_template('vendor/add_product.html')

@vendor_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'vendor_id' not in session:
        return redirect(url_for('vendor.login'))
    
    db = db_connection(current_app._get_current_object())
    product = db.execute('SELECT * FROM products WHERE id = ? AND vendor_id = ?',
                         (product_id, session['vendor_id'])).fetchone()
    
    if not product:
        flash('Product not found.', 'error')
        db.close()
        return redirect(url_for('vendor.products'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        gender = request.form.get('gender')
        price = request.form.get('price')
        size = request.form.get('size')
        color = request.form.get('color')
        occasion = request.form.get('occasion')
        climate = request.form.get('climate')
        body_type = request.form.get('body_type')
        skin_tone = request.form.get('skin_tone')
        stock = request.form.get('stock', 0)
        
        image_filename = product['image']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename, current_app._get_current_object()):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"product_{session['vendor_id']}_{uuid.uuid4().hex[:10]}.{ext}"
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                image_filename = filename
        
        db.execute('''
            UPDATE products SET name=?, description=?, category=?, gender=?, price=?,
                size=?, color=?, occasion=?, climate=?, body_type=?, skin_tone=?, image=?, stock=?
            WHERE id = ? AND vendor_id = ?
        ''', (name, description, category, gender, price, size, color, occasion,
              climate, body_type, skin_tone, image_filename, stock, product_id, session['vendor_id']))
        db.commit()
        db.close()
        flash('Product updated!', 'success')
        return redirect(url_for('vendor.products'))

    db.close()
    return render_template('vendor/edit_product.html', product=product)

@vendor_bp.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'vendor_id' not in session:
        return redirect(url_for('vendor.login'))
    
    db = db_connection(current_app._get_current_object())
    db.execute('UPDATE products SET status = "deleted" WHERE id = ? AND vendor_id = ?',
               (product_id, session['vendor_id']))
    db.commit()
    db.close()
    flash('Product deleted.', 'success')
    return redirect(url_for('vendor.products'))

@vendor_bp.route('/orders')
def orders():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor.login'))
    
    db = db_connection(current_app._get_current_object())
    orders = db.execute('''
        SELECT o.*, u.name as user_name, u.email as user_email, p.name as product_name, p.image as product_image
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        WHERE o.vendor_id = ?
        ORDER BY o.created_at DESC
    ''', (session['vendor_id'],)).fetchall()
    db.close()
    return render_template('vendor/orders.html', orders=orders)

@vendor_bp.route('/order/update/<int:order_id>', methods=['POST'])
def update_order(order_id):
    if 'vendor_id' not in session:
        return redirect(url_for('vendor.orders'))
    
    status = request.form.get('status')
    db = db_connection(current_app._get_current_object())
    db.execute('UPDATE orders SET status = ? WHERE id = ? AND vendor_id = ?',
               (status, order_id, session['vendor_id']))
    db.commit()
    db.close()
    flash('Order status updated!', 'success')
    return redirect(url_for('vendor.orders'))

@vendor_bp.route('/sales')
def sales():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor.login'))
    
    db = db_connection(current_app._get_current_object())
    
    monthly_sales = db.execute('''
        SELECT strftime('%Y-%m', created_at) as month,
               COUNT(*) as orders,
               SUM(total_price) as revenue
        FROM orders
        WHERE vendor_id = ? AND status != 'cancelled'
        GROUP BY month
        ORDER BY month DESC LIMIT 12
    ''', (session['vendor_id'],)).fetchall()
    
    top_products = db.execute('''
        SELECT p.name, p.category, COUNT(o.id) as sales_count, SUM(o.total_price) as revenue
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.vendor_id = ? AND o.status != 'cancelled'
        GROUP BY p.id
        ORDER BY sales_count DESC LIMIT 5
    ''', (session['vendor_id'],)).fetchall()
    
    total_revenue = db.execute(
        'SELECT SUM(total_price) as r FROM orders WHERE vendor_id = ? AND status != "cancelled"',
        (session['vendor_id'],)
    ).fetchone()['r'] or 0
    
    db.close()
    return render_template('vendor/sales.html', monthly_sales=monthly_sales,
                           top_products=top_products, total_revenue=total_revenue)
