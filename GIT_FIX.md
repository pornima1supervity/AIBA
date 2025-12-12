# Fix GitHub Authentication Error

## Problem
You're getting a 403 error because you're authenticated with GitHub account `Pornimaiitkgp` but trying to push to repository owned by `pornima1supervity`.

## Solutions

### Option 1: Use SSH Instead of HTTPS (Recommended)

1. **Change remote URL to SSH:**
   ```bash
   cd /Users/pornimagaikwad/Downloads/AIBA
   git remote set-url origin git@github.com:pornima1supervity/AIBA.git
   ```

2. **Set up SSH key** (if not already done):
   ```bash
   # Check if you have SSH key
   ls -la ~/.ssh/id_rsa.pub
   
   # If not, generate one:
   ssh-keygen -t ed25519 -C "pgaikwad@supervity.ai"
   
   # Add to GitHub:
   cat ~/.ssh/id_rsa.pub
   # Copy the output and add it to GitHub Settings > SSH Keys
   ```

3. **Test SSH connection:**
   ```bash
   ssh -T git@github.com
   ```

4. **Try pushing again:**
   ```bash
   git push -u origin main
   ```

### Option 2: Use Personal Access Token

1. **Create a Personal Access Token:**
   - Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `repo` permissions
   - Copy the token

2. **Update remote URL with token:**
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/pornima1supervity/AIBA.git
   ```

3. **Or use credential helper:**
   ```bash
   git config --global credential.helper osxkeychain
   # When prompted, use your GitHub username and the token as password
   ```

### Option 3: Clear Stored Credentials

1. **Clear macOS Keychain:**
   ```bash
   # Remove old credentials
   git credential-osxkeychain erase
   host=github.com
   protocol=https
   # Press Enter twice
   ```

2. **Or use GitHub CLI:**
   ```bash
   # Install GitHub CLI if not installed
   brew install gh
   
   # Authenticate
   gh auth login
   ```

### Option 4: Switch to Correct GitHub Account

If `pornima1supervity` is your correct account:

1. **Log out of current GitHub session:**
   ```bash
   # Clear credentials
   git credential-osxkeychain erase
   host=github.com
   protocol=https
   ```

2. **Log in with correct account:**
   - Use GitHub Desktop app, or
   - Use `gh auth login` command

## Quick Fix (Try This First)

```bash
cd /Users/pornimagaikwad/Downloads/AIBA

# Switch to SSH
git remote set-url origin git@github.com:pornima1supervity/AIBA.git

# Try pushing
git push -u origin main
```

If SSH doesn't work, you'll need to set up SSH keys first (see Option 1).

