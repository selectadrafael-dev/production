#!/bin/bash

echo "Installing Playwright browser..."
pip install playwright
python -m playwright install chromium
echo "Playwright setup complete"