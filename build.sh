#!/bin/bash
set -e

echo "Starting frontend build process..."

# Install Node.js if not present (Railway should have it via Nixpacks)
# Navigate to frontend directory and install dependencies
cd frontend
echo "Installing frontend dependencies..."
npm ci --legacy-peer-deps

# Build the frontend
echo "Building frontend for production..."
npm run build

echo "Frontend build complete!"
cd ..
