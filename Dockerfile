FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Run your main.py script that starts both threads (data fetcher + Streamlit)
CMD ["python", "main.py"]
