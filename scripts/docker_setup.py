#!/usr/bin/env python3
"""
Docker Setup Script

This script helps set up and run your Galion system using Docker.
It creates the necessary configuration files and provides commands
to build and run the entire stack.
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")

def print_success(text: str):
    """Print a success message."""
    print(f"✅ {text}")

def print_error(text: str):
    """Print an error message."""
    print(f"❌ {text}")

def print_info(text: str):
    """Print an info message."""
    print(f"ℹ️  {text}")

def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print_success(f"{description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def check_docker():
    """Check if Docker is installed and running."""
    print_header("DOCKER CHECK")

    # Check if Docker is installed
    if not run_command("docker --version", "Checking Docker installation"):
        print_error("Docker is not installed. Please install Docker first:")
        print_info("Windows: https://docs.docker.com/desktop/install/windows/")
        print_info("macOS: https://docs.docker.com/desktop/install/mac/")
        print_info("Linux: https://docs.docker.com/engine/install/")
        return False

    # Check if Docker daemon is running
    if not run_command("docker info", "Checking Docker daemon"):
        print_error("Docker daemon is not running. Please start Docker Desktop or the Docker service.")
        return False

    # Check Docker Compose
    if not run_command("docker-compose --version", "Checking Docker Compose"):
        print_error("Docker Compose is not available. Please install Docker Compose.")
        return False

    print_success("Docker environment is ready!")
    return True

def setup_environment():
    """Set up environment variables."""
    print_header("ENVIRONMENT SETUP")

    env_file = Path("../../deployment/env.example")
    target_env = Path("../../deployment/.env")

    if not env_file.exists():
        print_error("Environment template not found!")
        return False

    if target_env.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print_info("Skipping environment setup")
            return True

    try:
        shutil.copy(env_file, target_env)
        print_success("Environment file created")

        print_info("Please edit the .env file with your actual values:")
        print_info("Required: OPENAI_API_KEY")
        print_info("Optional: Database and Redis URLs")

        # Try to open the file for editing
        try:
            if sys.platform == "win32":
                os.startfile(target_env)
            elif sys.platform == "darwin":
                subprocess.run(["open", target_env])
            else:
                subprocess.run(["xdg-open", target_env])
        except:
            pass  # Ignore if we can't open the file

        return True

    except Exception as e:
        print_error(f"Environment setup failed: {e}")
        return False

def build_images():
    """Build Docker images."""
    print_header("BUILDING DOCKER IMAGES")

    os.chdir("../../deployment")

    if not run_command("docker-compose build", "Building Docker images"):
        return False

    print_success("Docker images built successfully!")
    return True

def start_services():
    """Start all services."""
    print_header("STARTING SERVICES")

    os.chdir("../../deployment")

    if not run_command("docker-compose up -d", "Starting services"):
        return False

    print_success("Services started successfully!")
    return True

def run_initialization():
    """Run system initialization inside container."""
    print_header("SYSTEM INITIALIZATION")

    # Wait a moment for services to be ready
    print_info("Waiting for services to be ready...")
    run_command("sleep 10", "Waiting")

    # Run initialization script
    init_command = "docker-compose exec -T backend python scripts/init_system.py"
    if not run_command(init_command, "Running system initialization"):
        return False

    print_success("System initialization completed!")
    return True

def run_tests():
    """Run basic tests."""
    print_header("RUNNING TESTS")

    # Run basic tests
    test_command = "docker-compose exec -T backend python scripts/test_basic.py"
    if not run_command(test_command, "Running basic tests"):
        return False

    print_success("Tests completed successfully!")
    return True

def show_status():
    """Show current status of services."""
    print_header("SERVICE STATUS")

    os.chdir("../../deployment")

    print_info("Container status:")
    run_command("docker-compose ps", "Checking container status")

    print_info("Service logs (last 20 lines):")
    run_command("docker-compose logs --tail=20", "Checking service logs")

def show_next_steps():
    """Show next steps for the user."""
    print_header("🎉 SETUP COMPLETE!")

    print("Your Galion autonomous agent system is now running with Docker!")
    print("\n" + "="*60)
    print("ACCESS POINTS:")
    print("🌐 Frontend:    http://localhost")
    print("📚 API Docs:    http://localhost:8010/docs")
    print("🔍 Health:      http://localhost:8010/health")
    print("📊 Monitoring:  http://localhost:8010/monitoring/status")
    print("🎛️  Grafana:     http://localhost:9090 (admin/admin)")
    print("📈 Prometheus:  http://localhost:9090")
    print("="*60)

    print("\nNEXT STEPS:")
    print("1. 📝 Edit your .env file with actual API keys")
    print("2. 🔄 Test the system: docker-compose exec backend python scripts/test_basic.py")
    print("3. 🎯 Try examples: docker-compose exec backend python scripts/example_usage.py")
    print("4. 📊 Check monitoring: http://localhost:8010/monitoring/status")
    print("5. 🚀 Submit your first task via API or frontend")

    print("\nUSEFUL COMMANDS:")
    print("🐳 View logs:        docker-compose logs -f")
    print("🔄 Restart service:  docker-compose restart backend")
    print("⏹️  Stop all:        docker-compose down")
    print("🧹 Clean up:         docker-compose down -v --rmi all")

    print("\n💡 PRO TIPS:")
    print("• Use 'docker-compose logs -f backend' to monitor agent activity")
    print("• Check 'docker stats' for resource usage")
    print("• Scale services: docker-compose up -d --scale backend=3")
    print("• Backup data: docker-compose exec db pg_dump > backup.sql")

def main():
    """Main setup function."""
    print("🐳 GALION DOCKER SETUP")
    print("="*60)
    print("This script will set up your Galion system using Docker.")
    print("Make sure Docker Desktop is running before proceeding!")
    print("="*60)

    # Change to scripts directory
    os.chdir(Path(__file__).parent)

    success = True

    # Step 1: Check Docker
    if not check_docker():
        success = False

    # Step 2: Setup environment
    if success and not setup_environment():
        success = False

    # Step 3: Build images
    if success and not build_images():
        success = False

    # Step 4: Start services
    if success and not start_services():
        success = False

    # Step 5: Initialize system
    if success and not run_initialization():
        success = False

    # Step 6: Run tests
    if success and not run_tests():
        success = False

    # Show status
    show_status()

    # Show next steps
    if success:
        show_next_steps()
    else:
        print_error("Setup completed with errors. Please check the output above.")
        print_info("You can try running individual steps again.")

    return success

def cleanup():
    """Clean up Docker resources."""
    print_header("DOCKER CLEANUP")

    os.chdir("../../deployment")

    print("⚠️  This will remove all containers, volumes, and images!")
    response = input("Are you sure? (y/N): ")

    if response.lower() == 'y':
        run_command("docker-compose down -v --rmi all", "Cleaning up Docker resources")
        run_command("docker system prune -f", "Removing unused Docker resources")
        print_success("Cleanup completed!")
    else:
        print_info("Cleanup cancelled")

def show_help():
    """Show help information."""
    print("🐳 Galion Docker Setup Script")
    print("="*40)
    print("Usage:")
    print("  python docker_setup.py         # Full setup")
    print("  python docker_setup.py cleanup # Clean up Docker resources")
    print("  python docker_setup.py help    # Show this help")
    print("")
    print("Commands:")
    print("  setup    - Full Docker setup and initialization")
    print("  cleanup  - Remove all Docker resources")
    print("  help     - Show this help message")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "cleanup":
            cleanup()
        elif command == "help":
            show_help()
        else:
            print_error(f"Unknown command: {command}")
            show_help()
    else:
        try:
            success = main()
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup interrupted by user.")
            sys.exit(1)
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            sys.exit(1)
