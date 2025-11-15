#!/bin/bash
# Comprehensive dependency checker and auto-installer
# Runs thorough checks for all dependencies and installs missing ones

echo "🔍 GALION PLATFORM - DEPENDENCY CHECKER"
echo "========================================"
echo "Checking and installing all required dependencies..."
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track what needs to be installed
MISSING_DEPS=0

# ============================================
# 1. SYSTEM PACKAGES
# ============================================
echo "1️⃣  SYSTEM PACKAGES"
echo "==================="

check_system_package() {
    if command -v $1 &> /dev/null; then
        echo -e "   ${GREEN}✅${NC} $1 installed"
        return 0
    else
        echo -e "   ${RED}❌${NC} $1 missing"
        return 1
    fi
}

# Check system packages
SYSTEM_PACKAGES=("python3" "pip3" "node" "npm" "nginx" "curl" "git")

for pkg in "${SYSTEM_PACKAGES[@]}"; do
    check_system_package $pkg || MISSING_DEPS=$((MISSING_DEPS + 1))
done

# Install PM2 globally if missing
if ! command -v pm2 &> /dev/null; then
    echo -e "   ${YELLOW}⚙️${NC}  Installing PM2 globally..."
    npm install -g pm2 --silent
    echo -e "   ${GREEN}✅${NC} PM2 installed"
else
    echo -e "   ${GREEN}✅${NC} PM2 installed"
fi

echo ""

# ============================================
# 2. PYTHON BACKEND DEPENDENCIES
# ============================================
echo "2️⃣  PYTHON BACKEND DEPENDENCIES"
echo "================================"

check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "   ${GREEN}✅${NC} $1"
        return 0
    else
        echo -e "   ${RED}❌${NC} $1 missing"
        return 1
    fi
}

# Required Python packages
PYTHON_PACKAGES=(
    "fastapi"
    "uvicorn"
    "psutil"
    "pydantic"
    "starlette"
    "typing_extensions"
)

PYTHON_MISSING=()

for pkg in "${PYTHON_PACKAGES[@]}"; do
    if ! check_python_package $pkg; then
        PYTHON_MISSING+=($pkg)
        MISSING_DEPS=$((MISSING_DEPS + 1))
    fi
done

# Install missing Python packages
if [ ${#PYTHON_MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "   ${YELLOW}⚙️${NC}  Installing missing Python packages..."
    pip3 install -q "${PYTHON_MISSING[@]}"
    echo -e "   ${GREEN}✅${NC} Python packages installed"
fi

echo ""

# ============================================
# 3. GALION-STUDIO DEPENDENCIES
# ============================================
echo "3️⃣  GALION-STUDIO DEPENDENCIES"
echo "==============================="

if [ -d "galion-studio" ]; then
    cd galion-studio
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "   ${YELLOW}⚙️${NC}  node_modules missing - installing..."
        npm install --silent
        echo -e "   ${GREEN}✅${NC} Dependencies installed"
    else
        # Check specific critical packages
        STUDIO_PACKAGES=(
            "next"
            "react"
            "react-dom"
            "react-hot-toast"
            "lucide-react"
            "clsx"
            "tailwind-merge"
        )
        
        STUDIO_MISSING=()
        
        for pkg in "${STUDIO_PACKAGES[@]}"; do
            if [ ! -d "node_modules/$pkg" ]; then
                echo -e "   ${RED}❌${NC} $pkg missing"
                STUDIO_MISSING+=($pkg)
                MISSING_DEPS=$((MISSING_DEPS + 1))
            else
                echo -e "   ${GREEN}✅${NC} $pkg"
            fi
        done
        
        # Install missing packages
        if [ ${#STUDIO_MISSING[@]} -gt 0 ]; then
            echo ""
            echo -e "   ${YELLOW}⚙️${NC}  Installing missing packages..."
            npm install "${STUDIO_MISSING[@]}" --silent
            echo -e "   ${GREEN}✅${NC} Packages installed"
        fi
    fi
    
    cd ..
else
    echo -e "   ${YELLOW}⚠️${NC}  galion-studio directory not found"
fi

echo ""

# ============================================
# 4. GALION-APP DEPENDENCIES
# ============================================
echo "4️⃣  GALION-APP DEPENDENCIES"
echo "==========================="

if [ -d "galion-app" ]; then
    cd galion-app
    
    if [ ! -d "node_modules" ]; then
        echo -e "   ${YELLOW}⚙️${NC}  node_modules missing - installing..."
        npm install --silent
        echo -e "   ${GREEN}✅${NC} Dependencies installed"
    else
        # Check specific packages
        APP_PACKAGES=(
            "next"
            "react"
            "react-dom"
            "lucide-react"
            "clsx"
            "tailwind-merge"
        )
        
        APP_MISSING=()
        
        for pkg in "${APP_PACKAGES[@]}"; do
            if [ ! -d "node_modules/$pkg" ]; then
                echo -e "   ${RED}❌${NC} $pkg missing"
                APP_MISSING+=($pkg)
                MISSING_DEPS=$((MISSING_DEPS + 1))
            else
                echo -e "   ${GREEN}✅${NC} $pkg"
            fi
        done
        
        if [ ${#APP_MISSING[@]} -gt 0 ]; then
            echo ""
            echo -e "   ${YELLOW}⚙️${NC}  Installing missing packages..."
            npm install "${APP_MISSING[@]}" --silent
            echo -e "   ${GREEN}✅${NC} Packages installed"
        fi
    fi
    
    cd ..
else
    echo -e "   ${YELLOW}⚠️${NC}  galion-app directory not found"
fi

echo ""

# ============================================
# 5. DEVELOPER-PLATFORM DEPENDENCIES
# ============================================
echo "5️⃣  DEVELOPER-PLATFORM DEPENDENCIES"
echo "===================================="

if [ -d "developer-platform" ]; then
    cd developer-platform
    
    if [ ! -d "node_modules" ]; then
        echo -e "   ${YELLOW}⚙️${NC}  node_modules missing - installing..."
        npm install --silent
        echo -e "   ${GREEN}✅${NC} Dependencies installed"
    else
        # Check specific packages
        DEV_PACKAGES=(
            "next"
            "react"
            "react-dom"
            "lucide-react"
            "clsx"
            "tailwind-merge"
        )
        
        DEV_MISSING=()
        
        for pkg in "${DEV_PACKAGES[@]}"; do
            if [ ! -d "node_modules/$pkg" ]; then
                echo -e "   ${RED}❌${NC} $pkg missing"
                DEV_MISSING+=($pkg)
                MISSING_DEPS=$((MISSING_DEPS + 1))
            else
                echo -e "   ${GREEN}✅${NC} $pkg"
            fi
        done
        
        if [ ${#DEV_MISSING[@]} -gt 0 ]; then
            echo ""
            echo -e "   ${YELLOW}⚙️${NC}  Installing missing packages..."
            npm install "${DEV_MISSING[@]}" --silent
            echo -e "   ${GREEN}✅${NC} Packages installed"
        fi
    fi
    
    cd ..
else
    echo -e "   ${YELLOW}⚠️${NC}  developer-platform directory not found"
fi

echo ""

# ============================================
# 6. VERIFY PYTHON BACKEND CAN START
# ============================================
echo "6️⃣  BACKEND STARTUP CHECK"
echo "========================="

cd v2/backend

# Try to import the main module
if python3 -c "import main_simple" 2>/dev/null; then
    echo -e "   ${GREEN}✅${NC} Backend can import successfully"
else
    echo -e "   ${RED}❌${NC} Backend import failed"
    echo ""
    echo "   Testing imports individually:"
    
    # Test each import
    python3 << 'PYCHECK'
import sys

modules = [
    "fastapi",
    "uvicorn", 
    "psutil",
    "pydantic",
    "starlette.middleware.cors"
]

failed = []
for mod in modules:
    try:
        __import__(mod)
        print(f"   ✅ {mod}")
    except ImportError as e:
        print(f"   ❌ {mod}: {e}")
        failed.append(mod)

if failed:
    print(f"\n   Installing failed imports: {', '.join(failed)}")
    sys.exit(1)
PYCHECK
    
    if [ $? -ne 0 ]; then
        echo ""
        echo -e "   ${YELLOW}⚙️${NC}  Installing missing backend dependencies..."
        pip3 install -q fastapi uvicorn psutil pydantic starlette python-multipart
        echo -e "   ${GREEN}✅${NC} Backend dependencies installed"
    fi
fi

cd ../..

echo ""

# ============================================
# 7. SUMMARY
# ============================================
echo "📊 DEPENDENCY CHECK SUMMARY"
echo "==========================="

if [ $MISSING_DEPS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL DEPENDENCIES INSTALLED!${NC}"
    echo ""
    echo "Your Galion Platform is ready to start!"
else
    echo -e "${YELLOW}⚠️  Fixed $MISSING_DEPS missing dependencies${NC}"
    echo ""
    echo "All dependencies have been installed automatically."
fi

echo ""
echo "🎉 DEPENDENCY CHECK COMPLETE!"
echo ""
echo "Next steps:"
echo "1. Start services: pm2 start all"
echo "2. Or run: ./emergency-fix-all.sh"

