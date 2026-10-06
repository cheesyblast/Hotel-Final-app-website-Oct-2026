#!/bin/bash
# ============================================
#  Kreation Hotels — Server Setup Script
#  Run on a fresh Ubuntu 22.04+ VPS
# ============================================

set -e

echo "═══════════════════════════════════════════"
echo "  Kreation Hotels — Server Setup"
echo "═══════════════════════════════════════════"

# ── 1. Install Docker ──
if ! command -v docker &> /dev/null; then
    echo "▸ Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "  ✓ Docker installed"
else
    echo "  ✓ Docker already installed"
fi

# ── 2. Install Docker Compose ──
if ! command -v docker compose &> /dev/null; then
    echo "▸ Installing Docker Compose..."
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin
    echo "  ✓ Docker Compose installed"
else
    echo "  ✓ Docker Compose already installed"
fi

# ── 3. Create project directory ──
PROJECT_DIR="/srv/kreation"
echo "▸ Setting up project at $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# ── 4. Create directory structure ──
mkdir -p crm/backend crm/frontend
mkdir -p website/backend website/frontend
mkdir -p nginx/ssl mongo/data

echo ""
echo "═══════════════════════════════════════════"
echo "  Directory structure created!"
echo "═══════════════════════════════════════════"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Copy your code files:"
echo "     CRM Backend:     cp -r /path/to/backend/*    $PROJECT_DIR/crm/backend/"
echo "     CRM Frontend:    cp -r /path/to/frontend/*   $PROJECT_DIR/crm/frontend/"
echo "     Website Backend:  cp -r /path/to/website-backend/*  $PROJECT_DIR/website/backend/"
echo "     Website Frontend: cp -r /path/to/website-frontend/* $PROJECT_DIR/website/frontend/"
echo ""
echo "  2. Copy deployment configs:"
echo "     cp docker-compose.yml .env.example Dockerfile* $PROJECT_DIR/"
echo "     cp nginx/*.conf $PROJECT_DIR/nginx/"
echo ""
echo "  3. Configure environment:"
echo "     cp .env.example .env"
echo "     nano .env"
echo ""
echo "  4. Start services:"
echo "     docker compose up -d --build"
echo ""
echo "  5. Setup SSL:"
echo "     sudo apt install certbot python3-certbot-nginx"
echo "     sudo certbot --nginx -d app.kreationhotels.com -d www.kreationhotels.com"
echo ""
echo "═══════════════════════════════════════════"
