#!/usr/bin/env python3
"""
Project quick start script
This script will check dependencies and start the application for the learning platform project.
"""

import sys
import subprocess
import os
import pathlib


ROOT = pathlib.Path(__file__).resolve().parent
BACKEND = ROOT / 'backend'
REQUIREMENTS = BACKEND / 'requirements.txt'
ENV_FILE = ROOT / '.env'
INIT_MONGO = BACKEND / 'init-mongo.js'
RUN_PY = BACKEND / 'run.py'


def check_python_version():
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def check_requirements():
    """Ensure required packages from requirements.txt are installed."""
    if not REQUIREMENTS.exists():
        print(f"⚠️  {REQUIREMENTS} not found — skipping automatic install")
        return True

    # Read requirements file
    with open(REQUIREMENTS, 'r', encoding='utf8') as f:
        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]

    missing = []
    for pkg in lines:
        name = pkg.split('==')[0]
        try:
            __import__(name.replace('-', '_'))
            print(f"✅ {name} is importable")
        except Exception:
            missing.append(pkg)
            print(f"❌ {name} not importable")

    if missing:
        print('\n📦 Installing missing packages from requirements.txt...')
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
            print('✅ Requirements installed successfully')
            return True
        except subprocess.CalledProcessError as e:
            print('❌ Failed to install requirements:', e)
            return False

    return True


def create_env_file():
    if ENV_FILE.exists():
        print(f"✅ {ENV_FILE.name} exists")
        return True

    print(f"📄 Creating {ENV_FILE.name} with sensible defaults...")
    content = f"""# Environment for learning_platform backend
MONGO_URI=mongodb://localhost:27017/learning_platform
JWT_SECRET_KEY=jwt-secret-change-in-production
FLASK_ENV=development
PORT=5000
# Optional: GEMINI_API_KEY=your-gemini-key-here
"""
    ENV_FILE.write_text(content, encoding='utf8')
    print(f"✅ {ENV_FILE.name} created — please review and update secrets (API keys, JWT secrets)")
    return True


def check_mongo_shell():
    """Check whether `mongo` shell is available to run init-mongo.js"""
    try:
        subprocess.check_call(['mongo', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def initialize_mongodb():
    if not INIT_MONGO.exists():
        print(f"⚠️  {INIT_MONGO.name} not found — skipping DB init script")
        return True

    if not check_mongo_shell():
        print('⚠️  `mongo` shell not found on PATH — skipping automatic DB initialization')
        print('   You can initialize MongoDB manually by running:')
        print(f"   mongo < {INIT_MONGO}")
        return True

    print('🗄️  Initializing MongoDB using init-mongo.js...')
    try:
        subprocess.check_call(['mongo', str(INIT_MONGO)])
        print('✅ MongoDB initialized')
        return True
    except subprocess.CalledProcessError as e:
        print('❌ MongoDB initialization failed:', e)
        return False


def start_application():
    if not RUN_PY.exists():
        print(f"❌ Entry point {RUN_PY} not found")
        return

    print('🚀 Starting backend application...')
    print('📱 Open your browser to: http://localhost:5000')
    print('⏹️  Press Ctrl+C to stop the server')
    print('-' * 60)

    try:
        subprocess.check_call([sys.executable, str(RUN_PY)])
    except KeyboardInterrupt:
        print('\n👋 Application stopped')
    except subprocess.CalledProcessError as e:
        print('❌ Failed to start application:', e)


def main():
    print('Learning Platform - Quick Start')
    print('=' * 60)

    checks = [
        ('Python Version', check_python_version),
        ('Requirements', check_requirements),
        ('.env file', create_env_file),
        ('MongoDB Initialization', initialize_mongodb),
    ]

    for name, fn in checks:
        print(f"\n{name}:")
        if not fn():
            print(f"❌ {name} failed. Fix the issue and re-run this script.")
            return

    print('\n✅ All checks passed — launching application')
    start_application()


if __name__ == '__main__':
    main()
