FROM python:3.6-alpine
WORKDIR /easy_budget_tgbot
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]