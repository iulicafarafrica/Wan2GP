#!/bin/bash

echo "Building Cover Studio Frontend..."

cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Building production bundle..."
npm run build

if [ -d "build" ]; then
    echo "✓ Frontend built successfully!"
    echo "Build output: $(pwd)/build"
else
    echo "✗ Build failed!"
    exit 1
fi
