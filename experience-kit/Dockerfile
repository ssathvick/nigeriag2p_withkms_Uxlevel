FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home experience
COPY . .
RUN mkdir -p /app/data && chown -R experience:experience /app
USER experience
ENV EXPERIENCE_DATABASE=/app/data/knowledge.sqlite
EXPOSE 18110
CMD ["gunicorn","--bind","0.0.0.0:18110","--workers","1","--threads","4","app:app"]
