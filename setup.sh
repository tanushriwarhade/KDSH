#!/bin/bash
# Setup script for KDSH 2026 submission

echo "=========================================="
echo "KDSH 2026 - Setup Script"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment (optional)
read -p "Create virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo ""
    echo "WARNING: GOOGLE_API_KEY not set"
    echo "Please set your API key:"
    echo "  export GOOGLE_API_KEY='your-key-here'"
    echo ""
    echo "Get FREE key at: https://makersuite.google.com/app/apikey"
    echo ""
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To run the solution:"
echo "  python main.py"
echo ""
echo "To run with sample data:"
echo "  python main.py --sample"
echo ""
