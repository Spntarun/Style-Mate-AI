import os

# Base directory of the project (where this file lives)
_BASE = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY    = os.environ.get('SECRET_KEY', 'stylemate_secret_key_change_in_production')
    DATABASE      = os.path.join(_BASE, 'fashion_threads.db')
    UPLOAD_FOLDER = os.path.join(_BASE, 'static', 'uploads')
    GENERATED_FOLDER = os.path.join(_BASE, 'static', 'generated')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # FASHN VTON 1.5 weights directory
    # Default: <project_root>/fashn-weights  (auto-created by setup script)
    # Override via env:  set FASHN_WEIGHTS_DIR=D:\my-weights
    FASHN_WEIGHTS_DIR = os.environ.get(
        'FASHN_WEIGHTS_DIR',
        os.path.join(_BASE, 'fashn-weights')
    )
