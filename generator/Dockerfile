FROM python:3.12-slim

WORKDIR /app

COPY generator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY generator /app/generator

CMD ["python", "-m", "generator.gerar_dados"]
