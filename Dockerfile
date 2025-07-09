FROM python:3.13.2-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget unzip default-jre fonts-liberation \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 \
    libnspr4 libnss3 libxcomposite1 libxdamage1 libxrandr2 xdg-utils libu2f-udev \
    libvulkan1 gnupg ca-certificates gcc g++ make \
    unixodbc-dev libpq-dev libsqlite3-dev libsasl2-dev libssl-dev libffi-dev \
    libkrb5-dev libodbc1 odbcinst && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ODBC driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Set up app
WORKDIR /app
COPY . /app

ENV PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    python -m playwright install --with-deps

# Install Allure CLI
RUN wget https://github.com/allure-framework/allure2/releases/download/2.33.0/allure-2.33.0.tgz && \
    tar -xzf allure-2.33.0.tgz && \
    mv allure-2.33.0 /opt/allure && \
    ln -s /opt/allure/bin/allure /usr/local/bin/allure

# Non-root user
RUN useradd -m pwuser && chown -R pwuser:pwuser /app /opt/ms-playwright
USER pwuser

ENV DB_USER="" \
    DB_PASS="" \
    RUN_ENV="" \
    PATH="/home/pwuser/.local/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright

CMD ["sh", "-c", "pytest -m $SUITE_TYPE"]
