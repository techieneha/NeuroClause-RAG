# Vercel Deployment (Alternative)
# Note: Vercel is better for frontend, but can work with FastAPI using serverless functions

from fastapi import FastAPI
from mangum import Mangum
from api.main import app

# Wrap FastAPI app for serverless deployment
handler = Mangum(app)
