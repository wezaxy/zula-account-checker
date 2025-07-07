import subprocess
import sys
import os

def install_requirements():
    print("⚡ Installing required packages...")
    
    requirements = [
        'aiohttp',
        'colorama'
    ]
    
    for package in requirements:
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            continue
    
    print("\n✨ All packages have been installed!")
    print("You can now run the checker by executing gui_zulu.py")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    install_requirements()
