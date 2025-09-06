# GitHub Repository Setup Instructions

### 1. Create Repository on GitHub
1. Go to https://github.com
2. Log in to your account
3. Click "New" or "+" → "New repository"
4. Fill in the details:
   - **Repository name**: `evm-wallet-django`
   - **Description**: `Django EVM Wallet with Squad Mechanics`
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** add README, .gitignore or license (they already exist)
5. Click "Create repository"

### 2. Connect Local Repository to GitHub
After creating the repository, GitHub will show commands. Execute them:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/evm-wallet-django.git

# Rename branch to main (modern standard)
git branch -M main

# Push code to GitHub
git push -u origin main
```

### 3. Alternative Method (if you have SSH keys)
```bash
# For SSH (if keys are configured)
git remote add origin git@github.com:YOUR_USERNAME/evm-wallet-django.git
git branch -M main
git push -u origin main
```

## 🔧 Additional Settings

### Default Branch Setup
After the first push, GitHub may suggest changing the default branch from `master` to `main`. Agree to this.

### Branch Protection Setup (optional)
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable "Require pull request reviews before merging"

## 📁 Repository Structure
After push, your repository will contain:
```
evm-wallet-django/
├── .gitignore
├── README.md
├── requirements.txt
├── manage.py
├── authentication/
├── wallet/
├── squad/
├── evm_wallet/
└── ...
```

## 🚀 After Setup
1. Clone repository on other machines: `git clone https://github.com/YOUR_USERNAME/evm-wallet-django.git`
2. Create `.env` file from `.env.example`
3. Install dependencies: `pip install -r requirements.txt`
4. Apply migrations: `python manage.py migrate`