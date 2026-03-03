from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
import os
import uuid
import sqlite3
from models.database import hash_password
from models.recommendation import get_outfit_recommendations, build_outfit_prompt
from models.ai_service import generate_outfit_image, get_style_advice

user_bp = Blueprint('user', __name__, url_prefix='/user')


def allowed_file(filename, app):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def db_connection(app):
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


# ─── AUTH ────────────────────────────────────────────────────────────────────

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        gender   = request.form.get('gender', '')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('user/register.html')

        db = db_connection(current_app._get_current_object())
        try:
            db.execute(
                'INSERT INTO users (name, email, password, gender) VALUES (?, ?, ?, ?)',
                (name, email, hash_password(password), gender)
            )
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('user.login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'error')
        finally:
            db.close()

    return render_template('user/register.html')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        db = db_connection(current_app._get_current_object())
        user = db.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, hash_password(password))
        ).fetchone()
        db.close()

        if user:
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            session['user_role'] = 'user'
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('user/login.html')


@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@user_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('user.login'))

    db = db_connection(current_app._get_current_object())
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    orders = db.execute('''
        SELECT o.*, p.name as product_name, p.image as product_image, v.brand_name
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN vendors  v ON o.vendor_id  = v.id
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    ''', (session['user_id'],)).fetchall()

    generated_rows = db.execute('''
        SELECT g.*, p.name as product_name
        FROM generated_outfits g
        JOIN products p ON g.product_id = p.id
        WHERE g.user_id = ?
        ORDER BY g.created_at DESC LIMIT 12
    ''', (session['user_id'],)).fetchall()
    db.close()

    # Convert to plain dicts so Jinja2 .get() works everywhere
    generated = [dict(r) for r in generated_rows]

    return render_template('user/dashboard.html', user=user, orders=orders, generated=generated)


# ─── PROFILE ─────────────────────────────────────────────────────────────────

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('user.login'))

    db = db_connection(current_app._get_current_object())

    if request.method == 'POST':
        height    = request.form.get('height')
        weight    = request.form.get('weight')
        chest     = request.form.get('chest')
        waist     = request.form.get('waist')
        hips      = request.form.get('hips')
        body_type = request.form.get('body_type')
        skin_tone = request.form.get('skin_tone')

        profile_image_path = None
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename, current_app._get_current_object()):
                ext      = file.filename.rsplit('.', 1)[1].lower()
                filename = f"user_{session['user_id']}_{uuid.uuid4().hex[:8]}.{ext}"
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                profile_image_path = filename

        if profile_image_path:
            db.execute(
                '''UPDATE users SET height=?, weight=?, chest=?, waist=?, hips=?,
                   body_type=?, skin_tone=?, profile_image=? WHERE id=?''',
                (height, weight, chest, waist, hips, body_type, skin_tone,
                 profile_image_path, session['user_id'])
            )
        else:
            db.execute(
                '''UPDATE users SET height=?, weight=?, chest=?, waist=?, hips=?,
                   body_type=?, skin_tone=? WHERE id=?''',
                (height, weight, chest, waist, hips, body_type, skin_tone, session['user_id'])
            )
        db.commit()
        flash('Profile updated successfully!', 'success')

    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()
    return render_template('user/profile.html', user=user)


# ─── RECOMMENDATIONS ─────────────────────────────────────────────────────────

@user_bp.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('user.login'))

    db = db_connection(current_app._get_current_object())
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    rec_data = None
    products  = []

    if request.method == 'POST':
        occasion = request.form.get('occasion', '')
        climate  = request.form.get('climate', '')
        budget   = request.form.get('budget', '')

        user_data = {
            'gender':    user['gender'] or 'unisex',
            'height':    user['height'],
            'weight':    user['weight'],
            'chest':     user['chest'],
            'waist':     user['waist'],
            'hips':      user['hips'],
            'body_type': user['body_type'] or '',
            'skin_tone': user['skin_tone'] or '',
            'occasion':  occasion,
            'climate':   climate,
            'budget':    budget
        }

        rec_data = get_outfit_recommendations(user_data)

        query  = '''SELECT p.*, v.brand_name FROM products p
                    JOIN vendors v ON p.vendor_id = v.id
                    WHERE p.status = 'active' '''
        params = []

        if user['gender'] and user['gender'] != 'unisex':
            query += " AND (p.gender = ? OR p.gender = 'unisex')"
            params.append(user['gender'])
        if occasion:
            query += " AND (p.occasion = ? OR p.occasion = 'all')"
            params.append(occasion)
        if budget:
            query += " AND p.price <= ?"
            params.append(float(budget))

        query += " ORDER BY p.created_at DESC LIMIT 20"
        products = db.execute(query, params).fetchall()

    db.close()
    return render_template('user/recommendations.html', user=user, rec_data=rec_data, products=products)


# ─── PRODUCTS ────────────────────────────────────────────────────────────────

@user_bp.route('/products')
def products():
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('user.login'))

    db       = db_connection(current_app._get_current_object())
    user     = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    category = request.args.get('category', '')
    gender   = request.args.get('gender', '')
    search   = request.args.get('search', '')

    query  = '''SELECT p.*, v.brand_name FROM products p
                JOIN vendors v ON p.vendor_id = v.id
                WHERE p.status = 'active' '''
    params = []

    if category:
        query += " AND p.category = ?"
        params.append(category)
    if gender:
        query += " AND (p.gender = ? OR p.gender = 'unisex')"
        params.append(gender)
    if search:
        query += " AND (p.name LIKE ? OR p.description LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])

    query += " ORDER BY p.created_at DESC"
    products = db.execute(query, params).fetchall()
    db.close()

    return render_template('user/products.html', user=user, products=products,
                           category=category, gender=gender, search=search)


# ─── PRODUCT DETAIL ──────────────────────────────────────────────────────────

@user_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('user.login'))

    db = db_connection(current_app._get_current_object())
    product = db.execute('''
        SELECT p.*, v.brand_name, v.name as vendor_name
        FROM products p JOIN vendors v ON p.vendor_id = v.id
        WHERE p.id = ? AND p.status = 'active'
    ''', (product_id,)).fetchone()

    # Redirect first if not found (before additional queries)
    if not product:
        db.close()
        flash('Product not found.', 'error')
        return redirect(url_for('user.products'))

    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    # Previously generated outfit for this exact product
    generated_row = db.execute('''
        SELECT * FROM generated_outfits
        WHERE user_id = ? AND product_id = ?
        ORDER BY created_at DESC LIMIT 1
    ''', (session['user_id'], product_id)).fetchone()
    db.close()

    # Convert sqlite3.Row → plain dict so Jinja2 .get() works
    generated = dict(generated_row) if generated_row else None

    return render_template('user/product_detail.html',
                           product=product, user=user, generated=generated)


# ─── AI VIRTUAL TRY-ON ───────────────────────────────────────────────────────

@user_bp.route('/visualize/<int:product_id>', methods=['POST'])
def visualize_outfit(product_id):
    if 'user_id' not in session or session.get('user_role') != 'user':
        return jsonify({'success': False, 'error': 'Not logged in'})

    db      = db_connection(current_app._get_current_object())
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    user    = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if not product or not user:
        db.close()
        return jsonify({'success': False, 'error': 'Product or user not found'})

    user_data = {
        'gender':    user['body_type'] or 'person',
        'body_type': user['body_type'] or '',
        'skin_tone': user['skin_tone'] or '',
        'height':    user['height']    or 165,
        'weight':    user['weight']    or 60,
        'occasion':  product['occasion'] if product['occasion'] else 'casual',
        'climate':   product['climate']  if product['climate']  else 'moderate',
        'budget':    ''
    }

    rec_data = get_outfit_recommendations(user_data)
    product_data = {
        'name':     product['name'],
        'color':    product['color']    or '',
        'category': product['category'] or ''
    }
    prompt = build_outfit_prompt(user_data, product_data, rec_data)

    # Build image paths
    product_image_path = None
    if product['image']:
        product_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product['image'])

    user_image_path = None
    if user['profile_image']:
        user_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user['profile_image'])

    weights_dir = current_app.config.get('FASHN_WEIGHTS_DIR')

    # --- Virtual Try-On via FASHN VTON 1.5 ---
    result = generate_outfit_image(
        prompt=prompt,
        product_image_path=product_image_path,
        user_image_path=user_image_path,
        weights_dir=weights_dir
    )

    if result.get('success'):
        gen_folder = current_app.config['GENERATED_FOLDER']
        os.makedirs(gen_folder, exist_ok=True)
        filename = f"gen_{session['user_id']}_{product_id}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(gen_folder, filename)

        with open(filepath, 'wb') as f:
            f.write(result['image_data'])

        db.execute(
            'INSERT INTO generated_outfits (user_id, product_id, prompt, generated_image) VALUES (?, ?, ?, ?)',
            (session['user_id'], product_id, prompt, filename)
        )
        db.commit()
        db.close()

        # Rule-based style advice — fully offline
        advice_result = get_style_advice(user_data, product['name'])

        return jsonify({
            'success':   True,
            'image_url': url_for('static', filename=f'generated/{filename}'),
            'advice':    advice_result.get('advice', ''),
            'prompt':    prompt
        })
    else:
        db.close()
        return jsonify({'success': False, 'error': result.get('error', 'Generation failed')})


# ─── PLACE ORDER ─────────────────────────────────────────────────────────────

@user_bp.route('/order/<int:product_id>', methods=['GET', 'POST'])
def place_order(product_id):
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('user.login'))

    db      = db_connection(current_app._get_current_object())
    product = db.execute(
        'SELECT * FROM products WHERE id = ? AND status = "active"', (product_id,)
    ).fetchone()

    if not product:
        db.close()
        flash('Product not found.', 'error')
        return redirect(url_for('user.products'))

    if request.method == 'POST':
        quantity    = int(request.form.get('quantity', 1))
        address     = request.form.get('address', '').strip()
        total_price = product['price'] * quantity

        if not address:
            flash('Delivery address is required.', 'error')
        else:
            db.execute(
                '''INSERT INTO orders (user_id, product_id, vendor_id, quantity, total_price, address)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (session['user_id'], product_id, product['vendor_id'],
                 quantity, total_price, address)
            )
            db.commit()
            db.close()
            flash('Order placed successfully!', 'success')
            return redirect(url_for('user.dashboard'))

    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()
    return render_template('user/order.html', product=product, user=user)
