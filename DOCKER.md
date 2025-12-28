# Hướng dẫn Build và Push Docker Image lên Docker Hub

## Yêu cầu

- Docker đã được cài đặt
- Tài khoản Docker Hub
- Đã đăng nhập Docker Hub

## Các bước

### 1. Đăng nhập Docker Hub

```bash
docker login
```

Nhập username và password của Docker Hub.

### 2. Build Docker Image

#### Cách 1: Build với tag mặc định

```bash
docker build -t your-dockerhub-username/vanna-agents:latest .
```

#### Cách 2: Build với version tag

```bash
docker build -t your-dockerhub-username/vanna-agents:2.0.1 .
docker build -t your-dockerhub-username/vanna-agents:latest .
```

#### Cách 3: Build với nhiều tags

```bash
docker build \
  -t your-dockerhub-username/vanna-agents:2.0.1 \
  -t your-dockerhub-username/vanna-agents:latest \
  .
```

**Lưu ý:** Thay `your-dockerhub-username` bằng username Docker Hub của bạn.

### 3. Kiểm tra Image đã build

```bash
docker images | grep vanna-agents
```

### 4. Test Image local (optional)

```bash
# Chạy container với environment variables
docker run -d \
  --name vanna-test \
  -p 3001:3001 \
  -e GOOGLE_API_KEY=your_api_key \
  -e MSSQL_CONNECTION_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=..." \
  your-dockerhub-username/vanna-agents:latest

# Kiểm tra logs
docker logs vanna-test

# Kiểm tra health
curl http://localhost:3001

# Dừng và xóa container test
docker stop vanna-test
docker rm vanna-test
```

### 5. Push Image lên Docker Hub

#### Push latest tag

```bash
docker push your-dockerhub-username/vanna-agents:latest
```

#### Push version tag

```bash
docker push your-dockerhub-username/vanna-agents:2.0.1
```

#### Push tất cả tags

```bash
docker push your-dockerhub-username/vanna-agents --all-tags
```

### 6. Sử dụng Image từ Docker Hub

Sau khi push, người khác có thể pull và sử dụng:

```bash
# Pull image
docker pull your-dockerhub-username/vanna-agents:latest

# Chạy container
docker run -d \
  --name vanna-agents \
  -p 3001:3001 \
  -e GOOGLE_API_KEY=your_api_key \
  -e MSSQL_CONNECTION_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=..." \
  your-dockerhub-username/vanna-agents:latest
```

## Sử dụng Docker Compose

### 1. Cập nhật docker-compose.yml

Sửa `your-dockerhub-username` trong file `docker-compose.yml`:

```yaml
image: your-dockerhub-username/vanna-agents:latest
```

### 2. Tạo file .env

```bash
GOOGLE_API_KEY=your_api_key
MSSQL_CONNECTION_STRING=DRIVER={ODBC Driver 17 for SQL Server};SERVER=...;DATABASE=...;UID=...;PWD=...
GEMINI_MODEL=gemini-2.5-pro
```

### 3. Chạy với Docker Compose

```bash
# Build và chạy
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng
docker-compose down
```

## Build Script tự động

Tạo file `build-and-push.sh`:

```bash
#!/bin/bash

# Cấu hình
DOCKERHUB_USERNAME="your-dockerhub-username"
IMAGE_NAME="vanna-agents"
VERSION="2.0.1"

# Build image
echo "Building Docker image..."
docker build \
  -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION} \
  -t ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest \
  .

# Kiểm tra build thành công
if [ $? -eq 0 ]; then
  echo "✓ Build successful!"
  
  # Push images
  echo "Pushing to Docker Hub..."
  docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
  docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest
  
  if [ $? -eq 0 ]; then
    echo "✓ Push successful!"
    echo ""
    echo "Image available at:"
    echo "  docker pull ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
  else
    echo "✗ Push failed!"
    exit 1
  fi
else
  echo "✗ Build failed!"
  exit 1
fi
```

Chạy script:

```bash
chmod +x build-and-push.sh
./build-and-push.sh
```

## Troubleshooting

### Lỗi: Permission denied

```bash
# Thêm user vào docker group
sudo usermod -aG docker $USER
# Logout và login lại
```

### Lỗi: Build fails - Node modules

```bash
# Xóa cache và build lại
docker build --no-cache -t your-dockerhub-username/vanna-agents:latest .
```

### Lỗi: Push fails - Authentication

```bash
# Đăng nhập lại
docker logout
docker login
```

### Lỗi: ODBC Driver not found

Image đã bao gồm unixodbc. Nếu vẫn lỗi, kiểm tra connection string.

## Multi-arch Build (Optional)

Để build cho nhiều kiến trúc (ARM, x86_64):

```bash
# Cài đặt buildx
docker buildx create --use

# Build và push cho nhiều platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t your-dockerhub-username/vanna-agents:latest \
  --push \
  .
```

## Best Practices

1. **Sử dụng version tags**: Luôn tag với version cụ thể, không chỉ `latest`
2. **Scan image**: Sử dụng `docker scan` để kiểm tra vulnerabilities
3. **Optimize size**: Image đã được optimize với multi-stage build
4. **Health check**: Image đã có health check built-in
5. **Environment variables**: Sử dụng `.env` file hoặc Docker secrets cho production

## Ví dụ Production Deployment

```bash
# Pull latest image
docker pull your-dockerhub-username/vanna-agents:latest

# Chạy với production config
docker run -d \
  --name vanna-agents-prod \
  --restart unless-stopped \
  -p 3001:3001 \
  --env-file .env.production \
  -v /path/to/data:/app/data \
  your-dockerhub-username/vanna-agents:latest
```

