#!/usr/bin/env python3
"""
V2 Deployment Webhook for RunPod
Simple HTTP-based deployment system (no SSH needed)
"""

from flask import Flask, request, jsonify
import subprocess
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_DIR = "/nexuslang-v2"
BRANCH = "clean-nexuslang"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "deployment-webhook",
        "version": "2.0"
    })

@app.route('/deploy', methods=['POST'])
def deploy():
    """
    Deploy endpoint - pulls latest code and restarts services
    Call this from your laptop to deploy
    """
    try:
        logger.info("Deployment started...")
        
        # Step 1: Pull latest code
        logger.info("Pulling latest code from GitHub...")
        os.chdir(PROJECT_DIR)
        
        result = subprocess.run(
            ["git", "fetch", "origin"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        result = subprocess.run(
            ["git", "checkout", BRANCH],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        result = subprocess.run(
            ["git", "pull", "origin", BRANCH],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        logger.info(f"Git pull result: {result.stdout}")
        
        # Step 2: Install backend dependencies
        logger.info("Installing backend dependencies...")
        result = subprocess.run(
            ["pip3", "install", "-q", "fastapi", "uvicorn", "psutil", "pydantic", "python-multipart"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Step 3: Restart PM2 services
        logger.info("Restarting services...")
        subprocess.run(["pm2", "delete", "all"], capture_output=True)
        
        # Start backend
        os.chdir(f"{PROJECT_DIR}/v2/backend")
        subprocess.run([
            "pm2", "start", "python3",
            "--name", "galion-backend",
            "--", "main_simple.py",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], capture_output=True)
        
        # Start frontends
        for app_name, port in [("galion-studio", 3001), ("galion-app", 3003), ("developer-platform", 3002)]:
            app_dir = f"{PROJECT_DIR}/{app_name}"
            if os.path.exists(app_dir):
                os.chdir(app_dir)
                subprocess.run([
                    "pm2", "start", "npm",
                    "--name", app_name,
                    "--", "run", "dev",
                    "--", "-p", str(port)
                ], capture_output=True)
        
        subprocess.run(["pm2", "save"], capture_output=True)
        
        # Get status
        status_result = subprocess.run(
            ["pm2", "status"],
            capture_output=True,
            text=True
        )
        
        logger.info("Deployment completed successfully!")
        
        return jsonify({
            "status": "success",
            "message": "Deployment completed",
            "pm2_status": status_result.stdout
        })
        
    except subprocess.TimeoutExpired:
        logger.error("Deployment timeout")
        return jsonify({
            "status": "error",
            "message": "Deployment timeout"
        }), 500
        
    except Exception as e:
        logger.error(f"Deployment error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """Get service status"""
    try:
        result = subprocess.run(
            ["pm2", "jlist"],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            "status": "success",
            "services": result.stdout
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/logs', methods=['GET'])
def logs():
    """Get recent logs"""
    service = request.args.get('service', 'all')
    lines = request.args.get('lines', '50')
    
    try:
        result = subprocess.run(
            ["pm2", "logs", service, "--lines", lines, "--nostream"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return jsonify({
            "status": "success",
            "logs": result.stdout
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Run on port 7000 (will be exposed by RunPod)
    app.run(host='0.0.0.0', port=7000, debug=False)

