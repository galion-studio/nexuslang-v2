#!/usr/bin/env python3
"""
Quick Launch Script for Nexus Lang V2 Scientific Dashboard
==========================================================

This script provides an easy way to start the scientific knowledge enhancement
dashboard with all the amazing AI capabilities.

Usage:
    python launch_dashboard.py

Or make it executable and run:
    chmod +x launch_dashboard.py
    ./launch_dashboard.py

Features:
- Interactive web-based scientific query interface
- Real-time system monitoring
- Multi-agent collaboration visualization
- Complete transparency and audit trails
- Performance metrics dashboard

Requirements:
- Python 3.8+
- Optional: Flask (pip install flask) for enhanced features
- If Flask not available, uses built-in HTTP server

Author: Nexus Lang V2 Team
Date: November 2025
"""

import sys
import os
import subprocess
import time

def check_requirements():
    """Check if required modules are available."""
    print("[CHECK] Checking requirements...")

    try:
        import psutil
        print("[OK] psutil available")
    except ImportError:
        print("[WARN] psutil not available - installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])

    try:
        import flask
        print("[OK] Flask available - enhanced dashboard features enabled")
        return True
    except ImportError:
        print("[WARN] Flask not available - using basic HTTP server")
        print("[TIP] For enhanced features, install Flask: pip install flask")
        return False

def launch_dashboard():
    """Launch the scientific dashboard."""
    print()
    print(">>> Nexus Lang V2 - Scientific Knowledge Enhancement Dashboard")
    print("=" * 70)
    print()
    print("EXTREMELY DEEP understanding of how laws work and how history works")
    print()
    print("🎯 Dashboard Features:")
    print("  • 🧠 Interactive Scientific Query Interface")
    print("  • 🤝 Multi-Agent Collaboration Visualization")
    print("  • 📊 Complete Transparency & Audit Trails")
    print("  • 📈 Real-Time System Monitoring")
    print("  • 🔬 First Principles Reasoning Demo")
    print("  • 🌐 External Knowledge Integration Display")
    print()
    print("🎊 Sample Queries to Try:")
    print("  • 'Explain the photoelectric effect using first principles'")
    print("  • 'How does quantum mechanics influence chemical bonding?'")
    print("  • 'Prove that √2 is irrational using first principles'")
    print("  • 'What is the mechanism of organic substitution reactions?'")
    print("  • 'Derive the Schrödinger equation from fundamental principles'")
    print()

    # Check if dashboard script exists
    dashboard_script = os.path.join(os.path.dirname(__file__), "scientific_dashboard.py")
    if not os.path.exists(dashboard_script):
        print(f"❌ Dashboard script not found: {dashboard_script}")
        return False

    try:
        print("🔄 Starting dashboard server...")
        print()

        # Launch the dashboard
        result = subprocess.run([
            sys.executable,
            dashboard_script
        ], cwd=os.path.dirname(__file__))

        return result.returncode == 0

    except KeyboardInterrupt:
        print()
        print("🛑 Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")
        return False

def show_post_launch_info():
    """Show information after successful launch."""
    print()
    print("🎉 Dashboard launched successfully!")
    print()
    print("🌐 Access the dashboard at:")
    print("   📊 Main Dashboard: http://localhost:8080")
    print("   🔬 Interactive Demo: http://localhost:8080/demo")
    print("   📈 System Monitor: http://localhost:8080/monitor")
    print()
    print("🎯 What you can do:")
    print("   • Ask complex scientific questions")
    print("   • See multi-agent collaboration in action")
    print("   • Explore complete reasoning transparency")
    print("   • Monitor system performance in real-time")
    print("   • Experience first principles scientific AI")
    print()
    print("🔬 The Scientific AI Revolution is here!")
    print("   Nexus Lang V2 understands how laws work and how history works")
    print("   with EXTREMELY DEEP scientific reasoning capabilities.")
    print()
    print("=" * 70)

def main():
    """Main launch function."""
    print(">>> Nexus Lang V2 Scientific Dashboard Launcher")
    print("=" * 50)

    # Check requirements
    flask_available = check_requirements()

    if not flask_available:
        print()
        print("💡 Tip: Install Flask for the full dashboard experience:")
        print("   pip install flask")
        print("   (Then re-run this launcher)")
        print()

    # Launch dashboard
    success = launch_dashboard()

    if success:
        show_post_launch_info()
    else:
        print()
        print("❌ Dashboard launch failed!")
        print("🔍 Check the error messages above for details.")
        print()
        print("🆘 Troubleshooting:")
        print("   • Ensure Python 3.8+ is installed")
        print("   • Try: pip install psutil")
        print("   • For full features: pip install flask")
        print("   • Check that no other service is using port 8080")
        print()
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
