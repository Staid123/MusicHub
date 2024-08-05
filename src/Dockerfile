FROM python:3.10

# Установка системных зависимостей
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание директории для приложения и установка рабочей директории
RUN mkdir /music_app
WORKDIR /music_app

# Копирование кода приложения
COPY . .

# Установка зависимостей Python
RUN pip install -r requirements.txt


# Открытие портов
EXPOSE 8000


# Команда по умолчанию для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]