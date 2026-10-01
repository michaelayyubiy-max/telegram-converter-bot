#!/usr/bin/env bash
set -e

echo "🚀 Telegram Universal Converter Bot - Avtomatik o'rnatish..."

# Update packages
apt-get update && apt-get install -y python3 python3-pip python3-venv ffmpeg git curl

# Create virtual environment if needed
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup systemd service
cp converter_bot.service /etc/systemd/system/converter_bot.service
systemctl daemon-reload
systemctl enable converter_bot
systemctl restart converter_bot

echo "✅ Bot serverda 24/7 rejimda muvaffaqiyatli ishga tushdi!"
systemctl status converter_bot --no-pager
