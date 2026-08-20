FROM python:3.12-slim
WORKDIR /app

# 部署版本标识（构建时注入，供 /api/version 返回）
ARG APP_VERSION=1.6.0
ARG APP_BUILD_TIME=unknown
ENV APP_VERSION=$APP_VERSION
ENV APP_BUILD_TIME=$APP_BUILD_TIME

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
