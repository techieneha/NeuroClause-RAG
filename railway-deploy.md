# Railway.app Deployment
# Railway offers free tier with 500 hours/month

# 1. Install Railway CLI
# npm install -g @railway/cli

# 2. Login and deploy
# railway login
# railway deploy

# railway.toml configuration (create this file)
[build]
  builder = "nixpacks"

[deploy]
  startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
  restartPolicyType = "never"

[env]
  TEAM_TOKEN = "your_hackrx_token_here"
  PYTHONPATH = "/app"
