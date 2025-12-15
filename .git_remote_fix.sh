#!/bin/bash
# Quick fix script for GitHub authentication issues
# Run this if you get 403 permission errors

echo "Switching remote to SSH..."
git remote set-url origin git@github.com:pornima1supervity/AIBA.git

echo "Verifying remote configuration..."
git remote -v

echo ""
echo "✅ Remote switched to SSH. You can now push with:"
echo "   git push origin main"

