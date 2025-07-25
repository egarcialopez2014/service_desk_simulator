#!/usr/bin/env python3
"""
Launch script for the Click & Collect Queue Simulation System.
"""
import subprocess
import sys
import os


def main():
    """Launch the Streamlit web application."""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Streamlit app
    app_path = os.path.join(script_dir, "app", "main.py")
    
    # Path to the Python executable in the virtual environment
    python_path = os.path.join(script_dir, ".venv", "bin", "python")
    
    # Check if virtual environment exists
    if not os.path.exists(python_path):
        print("Virtual environment not found!")
        print("Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if Streamlit app exists
    if not os.path.exists(app_path):
        print(f"Streamlit app not found at: {app_path}")
        sys.exit(1)
    
    print("🚀 Launching Click & Collect Queue Simulation System...")
    print("📱 The web interface will open in your browser at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    try:
        # Launch Streamlit
        subprocess.run([
            python_path, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down the simulation system...")
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
