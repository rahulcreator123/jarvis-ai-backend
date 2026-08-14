# Jarvis Cloud Backend

This backend is the secure bridge between the Android app and the online AI provider.

## Deploy to Render

1. Push this project to GitHub.
2. Create a new Web Service in Render from the repository.
3. Render can use `render.yaml` automatically, or set:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the secret environment variable `OPENAI_API_KEY` in Render.
5. After deployment, open:
   `https://YOUR-SERVICE.onrender.com/health`
6. Your Android endpoint is:
   `https://YOUR-SERVICE.onrender.com/chat`
7. In the Android app Settings, replace the placeholder backend URL with that HTTPS `/chat` URL.

## Local testing

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

For an Android emulator use `http://10.0.2.2:8000/chat` only for local development. A physical phone should use the deployed HTTPS URL.
