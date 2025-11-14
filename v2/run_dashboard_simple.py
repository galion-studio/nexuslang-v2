#!/usr/bin/env python3
"""
Simple Dashboard Runner for Nexus Lang V2 Scientific Knowledge Enhancement
==========================================================================

Direct launcher for the scientific dashboard without dependency installation.

This script assumes required dependencies are already available or will
gracefully fall back to basic functionality.

Usage:
    python run_dashboard_simple.py

Features:
- Web-based scientific query interface
- Real-time system monitoring
- Multi-agent collaboration demo
- Transparency visualization
- First principles reasoning showcase

Author: Nexus Lang V2 Team
Date: November 2025
"""

import sys
import os

def main():
    """Launch the scientific dashboard."""
    print(">>> Nexus Lang V2 - Scientific Knowledge Enhancement Dashboard")
    print("=" * 70)
    print()
    print("EXTREMELY DEEP understanding of how laws work and how history works")
    print()

    # Check if dashboard script exists
    dashboard_script = os.path.join(os.path.dirname(__file__), "scientific_dashboard.py")
    if not os.path.exists(dashboard_script):
        print(f"[ERROR] Dashboard script not found: {dashboard_script}")
        print("Please ensure scientific_dashboard.py is in the same directory.")
        return 1

    print("[INFO] Launching scientific dashboard...")
    print()

    try:
        # Import and run the dashboard
        sys.path.insert(0, os.path.dirname(__file__))

        # Try to import required modules gracefully
        try:
            import psutil
            psutil_available = True
        except ImportError:
            print("[WARN] psutil not available - using mock system metrics")
            psutil_available = False

        try:
            from flask import Flask
            flask_available = True
            print("[OK] Flask available - full dashboard features enabled")
        except ImportError:
            flask_available = False
            print("[WARN] Flask not available - using basic HTTP server")
            print("[TIP] Install Flask for enhanced features: pip install flask")

        # Import and run the dashboard
        from scientific_dashboard import ScientificDashboard
        import asyncio

        print()
        print("[TARGET] Dashboard Features:")
        print("  * Interactive Scientific Query Interface")
        print("  * Multi-Agent Collaboration Visualization")
        print("  * Complete Transparency & Audit Trails")
        print("  * Real-Time System Monitoring")
        print("  * First Principles Reasoning Demo")
        print("  * External Knowledge Integration Display")
        print()

        dashboard = ScientificDashboard()

        if flask_available:
            print("[WEB] Starting enhanced Flask server...")
        else:
            print("[WEB] Starting basic HTTP server...")

        print()
        print("[ACCESS] Open your browser to:")
        print("  Main Dashboard: http://localhost:8080")
        print("  Interactive Demo: http://localhost:8080/demo")
        print("  System Monitor: http://localhost:8080/monitor")
        print()
        print("[SAMPLE] Try these queries:")
        print("  * 'Explain the photoelectric effect using first principles'")
        print("  * 'How does quantum mechanics influence chemical bonding?'")
        print("  * 'Prove that √2 is irrational'")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 70)

        # Run the dashboard
        asyncio.run(dashboard.start_server())

    except KeyboardInterrupt:
        print()
        print("[STOP] Dashboard stopped by user")
        return 0
    except Exception as e:
        print()
        print(f"[ERROR] Failed to launch dashboard: {e}")
        print()
        print("[HELP] Troubleshooting:")
        print("  * Ensure Python 3.8+ is installed")
        print("  * Check that port 8080 is not in use")
        print("  * For full features, install Flask: pip install flask")
        print("  * The basic HTTP server should still work without Flask")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
