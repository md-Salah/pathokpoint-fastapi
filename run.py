import os

if __name__ == "__main__":
    os.system("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --reload")
    