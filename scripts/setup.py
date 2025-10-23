#!/usr/bin/env python3
"""
Setup script for Shopify Product Upload System
Creates necessary directories and initializes the system
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories for the system"""
    directories = [
        'logs',
        'reports', 
        'backups',
        'data',
        'tests',
        'docs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path('.env')
    template_file = Path('config.env.example')
    
    if not env_file.exists() and template_file.exists():
        import shutil
        shutil.copy(template_file, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please update .env with your actual API credentials")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No template found, please create .env file manually")

def install_dependencies():
    """Install required Python packages"""
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print(f"❌ Error installing dependencies: {result.stderr}")
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")

def verify_structure():
    """Verify the project structure is correct"""
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'src/__init__.py',
        'src/core/__init__.py',
        'src/api/__init__.py',
        'src/utils/__init__.py',
        'src/reports/__init__.py',
        'src/config/__init__.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ Project structure verified")
        return True

def main():
    """Main setup function"""
    print("🚀 Setting up Shopify Product Upload System...")
    print("=" * 50)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Create .env file
    print("\n🔧 Setting up configuration...")
    create_env_file()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    install_dependencies()
    
    # Verify structure
    print("\n✅ Verifying project structure...")
    if verify_structure():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env file with your API credentials")
        print("2. Place your Excel files in the data/ directory")
        print("3. Run: python main.py data/your_products.xlsx")
    else:
        print("\n❌ Setup failed. Please check the project structure.")
        sys.exit(1)

if __name__ == "__main__":
    main()
