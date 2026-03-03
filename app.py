from flask import Flask, render_template, redirect, url_for, session
import os
from config import Config
from models.database import init_db
from routes.user import user_bp
from routes.vendor import vendor_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(vendor_bp)
    app.register_blueprint(admin_bp)
    
    # Initialize database
    init_db(app)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
