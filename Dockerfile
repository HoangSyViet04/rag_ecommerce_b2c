# image Python
FROM python:3.11-slim

# 2. Cài đặt các thư viện lõi của Linux và ODBC Driver cho SQL Server 
RUN apt-get update && apt-get install -y curl apt-transport-https gnupg2 unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18


# 3. Đặt thư mục làm việc
WORKDIR /app

# 4. Copy file cấu hình và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ source code vào Docker
COPY . .

# 6. Mở cổng 8000 ra ngoài
EXPOSE 8000

# 7. Lệnh khởi động Server
CMD ["uvicorn","src.api.main:app","--host","0.0.0.0","--port","8000"]

