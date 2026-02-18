#!/bin/bash

# Verification script for Wan2GP Audio Studio Frontend

echo "=========================================="
echo "Verifying Audio Frontend Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check function
check() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
        ((ERRORS++))
    fi
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Checking prerequisites..."
echo ""

# Check Node.js
command -v node &> /dev/null
check "Node.js installed" $?

# Check npm
command -v npm &> /dev/null
check "npm installed" $?

echo ""
echo "Checking project files..."
echo ""

# Check package.json
[ -f "package.json" ]
check "package.json exists" $?

# Check vite config
[ -f "vite.config.js" ]
check "vite.config.js exists" $?

# Check tailwind config
[ -f "tailwind.config.js" ]
check "tailwind.config.js exists" $?

# Check index.html
[ -f "index.html" ]
check "index.html exists" $?

echo ""
echo "Checking source files..."
echo ""

# Check main files
[ -f "src/main.jsx" ]
check "src/main.jsx exists" $?

[ -f "src/App.jsx" ]
check "src/App.jsx exists" $?

[ -f "src/index.css" ]
check "src/index.css exists" $?

echo ""
echo "Checking components..."
echo ""

[ -f "src/components/AudioUploader.jsx" ]
check "AudioUploader component" $?

[ -f "src/components/WaveSurferPlayer.jsx" ]
check "WaveSurferPlayer component" $?

[ -f "src/components/JobProgress.jsx" ]
check "JobProgress component" $?

[ -f "src/components/ConfigForm.jsx" ]
check "ConfigForm component" $?

[ -f "src/components/ErrorNotification.jsx" ]
check "ErrorNotification component" $?

[ -f "src/components/LoadingSpinner.jsx" ]
check "LoadingSpinner component" $?

echo ""
echo "Checking hooks..."
echo ""

[ -f "src/hooks/useAudioUpload.js" ]
check "useAudioUpload hook" $?

[ -f "src/hooks/useJobManager.js" ]
check "useJobManager hook" $?

echo ""
echo "Checking services..."
echo ""

[ -f "src/services/api.js" ]
check "API service" $?

echo ""
echo "Checking utilities..."
echo ""

[ -f "src/utils/cn.js" ]
check "cn utility" $?

echo ""
echo "Checking dependencies..."
echo ""

if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} node_modules exists"
    
    # Check key dependencies
    [ -d "node_modules/react" ]
    check "React installed" $?
    
    [ -d "node_modules/wavesurfer.js" ]
    check "Wavesurfer.js installed" $?
    
    [ -d "node_modules/vite" ]
    check "Vite installed" $?
    
    [ -d "node_modules/tailwindcss" ]
    check "Tailwind CSS installed" $?
else
    echo -e "${YELLOW}!${NC} node_modules not found (run 'npm install')"
    ((ERRORS++))
fi

echo ""
echo "Checking configuration..."
echo ""

# Check if Vite config has correct proxy
grep -q "8000" vite.config.js
check "Vite proxy configured for port 8000" $?

# Check if API service points to correct URL
grep -q "8000" src/services/api.js
check "API service configured for port 8000" $?

echo ""
echo "=========================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All checks passed! ✓${NC}"
    echo ""
    echo "You can now start the frontend with:"
    echo "  npm run dev"
    echo ""
    echo "Or start both backend and frontend with:"
    echo "  ../start_audio_studio.sh"
else
    echo -e "${RED}Found $ERRORS error(s) ✗${NC}"
    echo ""
    echo "Please fix the errors above before starting the frontend."
fi

echo "=========================================="
