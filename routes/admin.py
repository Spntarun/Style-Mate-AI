from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import sqlite3
from models.database import hash_password

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def db_connection(app):
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = db_connection(current_app._get_current_object())
        admin = db.execute(
            'SELECT * FROM admins WHERE email = ? AND password = ?',
            (email, hash_password(password))
        ).fetchone()
        db.close()
        
        if admin:
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['name']
            session['admin_role'] = 'admin'
            flash('Welcome, Administrator!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@admin_bp.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    
    total_users = db.execute('SELECT COUNT(*) as c FROM users').fetchone()['c']
    total_vendors = db.execute('SELECT COUNT(*) as c FROM vendors WHERE status = "approved"').fetchone()['c']
    pending_vendors = db.execute('SELECT COUNT(*) as c FROM vendors WHERE status = "pending"').fetchone()['c']
    total_products = db.execute('SELECT COUNT(*) as c FROM products WHERE status = "active"').fetchone()['c']
    total_orders = db.execute('SELECT COUNT(*) as c FROM orders').fetchone()['c']
    total_revenue = db.execute('SELECT SUM(total_price) as r FROM orders WHERE status != "cancelled"').fetchone()['r'] or 0
    
    recent_orders = db.execute('''
        SELECT o.*, u.name as user_name, p.name as product_name, v.brand_name
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        JOIN vendors v ON o.vendor_id = v.id
        ORDER BY o.created_at DESC LIMIT 5
    ''').fetchall()
    
    pending_vendor_list = db.execute(
        'SELECT * FROM vendors WHERE status = "pending" ORDER BY created_at DESC'
    ).fetchall()
    
    db.close()
    return render_template('admin/dashboard.html',
                           total_users=total_users, total_vendors=total_vendors,
                           pending_vendors=pending_vendors, total_products=total_products,
                           total_orders=total_orders, total_revenue=total_revenue,
                           recent_orders=recent_orders, pending_vendor_list=pending_vendor_list)

@admin_bp.route('/users')
def users():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    db.close()
    flash('User deleted.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/vendors')
def vendors():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    vendor_list = db.execute('SELECT * FROM vendors ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin/vendors.html', vendors=vendor_list)

@admin_bp.route('/vendor/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    db.execute('UPDATE vendors SET status = "approved" WHERE id = ?', (vendor_id,))
    db.commit()
    db.close()
    flash('Vendor approved!', 'success')
    return redirect(url_for('admin.vendors'))

@admin_bp.route('/vendor/reject/<int:vendor_id>', methods=['POST'])
def reject_vendor(vendor_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    db.execute('UPDATE vendors SET status = "rejected" WHERE id = ?', (vendor_id,))
    db.commit()
    db.close()
    flash('Vendor rejected.', 'info')
    return redirect(url_for('admin.vendors'))

@admin_bp.route('/vendor/delete/<int:vendor_id>', methods=['POST'])
def delete_vendor(vendor_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    db.execute('DELETE FROM vendors WHERE id = ?', (vendor_id,))
    db.commit()
    db.close()
    flash('Vendor deleted.', 'info')
    return redirect(url_for('admin.vendors'))

@admin_bp.route('/products')
def products():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    products = db.execute('''
        SELECT p.*, v.brand_name FROM products p
        JOIN vendors v ON p.vendor_id = v.id
        ORDER BY p.created_at DESC
    ''').fetchall()
    db.close()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/product/toggle/<int:product_id>', methods=['POST'])
def toggle_product(product_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    product = db.execute('SELECT status FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if product:
        new_status = 'inactive' if product['status'] == 'active' else 'active'
        db.execute('UPDATE products SET status = ? WHERE id = ?', (new_status, product_id))
        db.commit()
        flash(f'Product {new_status}.', 'success')
    
    db.close()
    return redirect(url_for('admin.products'))

@admin_bp.route('/orders')
def orders():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    orders = db.execute('''
        SELECT o.*, u.name as user_name, p.name as product_name, v.brand_name
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
        JOIN vendors v ON o.vendor_id = v.id
        ORDER BY o.created_at DESC
    ''').fetchall()
    db.close()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/sales')
def sales():
    if 'admin_id' not in session:
        return redirect(url_for('admin.login'))
    
    db = db_connection(current_app._get_current_object())
    
    monthly_sales = db.execute('''
        SELECT strftime('%Y-%m', created_at) as month,
               COUNT(*) as orders,
               SUM(total_price) as revenue
        FROM orders WHERE status != 'cancelled'
        GROUP BY month ORDER BY month DESC LIMIT 12
    ''').fetchall()
    
    top_vendors = db.execute('''
        SELECT v.brand_name, COUNT(o.id) as orders, SUM(o.total_price) as revenue
        FROM orders o
        JOIN vendors v ON o.vendor_id = v.id
        WHERE o.status != 'cancelled'
        GROUP BY v.id ORDER BY revenue DESC LIMIT 5
    ''').fetchall()
    
    category_sales = db.execute('''
        SELECT p.category, COUNT(o.id) as orders, SUM(o.total_price) as revenue
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.status != 'cancelled'
        GROUP BY p.category ORDER BY revenue DESC
    ''').fetchall()
    
    db.close()
    return render_template('admin/sales.html', monthly_sales=monthly_sales,
                           top_vendors=top_vendors, category_sales=category_sales)
