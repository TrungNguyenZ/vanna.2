#!/bin/bash

# Script để deploy Vanna Agents trên server Linux
# Sử dụng: bash deploy-server.sh

set -e

echo "=========================================="
echo "Deploy Vanna Agents trên Server Linux"
echo "=========================================="
echo ""

# Màu sắc
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

CONTAINER_NAME="vanna-agents"
IMAGE_NAME="trungnguyen131/vanna-agents:latest"
PORT="3001"

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker không được tìm thấy. Vui lòng cài đặt Docker.${NC}"
    exit 1
fi

# Kiểm tra và stop container cũ (nếu có)
echo -e "${YELLOW}[1/5] Kiểm tra container cũ...${NC}"
if sudo docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}  Container cũ đang tồn tại. Đang stop và xóa...${NC}"
    sudo docker stop ${CONTAINER_NAME} 2>/dev/null || true
    sudo docker rm ${CONTAINER_NAME} 2>/dev/null || true
    echo -e "${GREEN}  ✓ Đã xóa container cũ${NC}"
else
    echo -e "${GREEN}  ✓ Không có container cũ${NC}"
fi

# Kiểm tra port đang được sử dụng
echo ""
echo -e "${YELLOW}[2/5] Kiểm tra port ${PORT}...${NC}"
if sudo docker ps --filter "publish=${PORT}" --format "{{.Names}}" | grep -q .; then
    echo -e "${YELLOW}  Port ${PORT} đang được sử dụng. Đang stop container...${NC}"
    sudo docker ps --filter "publish=${PORT}" -q | xargs -r sudo docker stop
    echo -e "${GREEN}  ✓ Đã giải phóng port ${PORT}${NC}"
else
    echo -e "${GREEN}  ✓ Port ${PORT} đang trống${NC}"
fi

# Pull image mới nhất
echo ""
echo -e "${YELLOW}[3/5] Pull image mới nhất...${NC}"
sudo docker pull ${IMAGE_NAME}
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Đã pull image thành công${NC}"
else
    echo -e "${RED}  ✗ Pull image thất bại${NC}"
    exit 1
fi

# Chạy container mới
echo ""
echo -e "${YELLOW}[4/5] Chạy container mới...${NC}"

# Kiểm tra environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}  ✗ GOOGLE_API_KEY chưa được set${NC}"
    echo "  Vui lòng export GOOGLE_API_KEY=your_key"
    exit 1
fi

if [ -z "$MSSQL_CONNECTION_STRING" ]; then
    echo -e "${RED}  ✗ MSSQL_CONNECTION_STRING chưa được set${NC}"
    echo "  Vui lòng export MSSQL_CONNECTION_STRING='your_connection_string'"
    exit 1
fi

sudo docker run -d \
  --name ${CONTAINER_NAME} \
  -p ${PORT}:${PORT} \
  -e GOOGLE_API_KEY="${GOOGLE_API_KEY}" \
  -e MSSQL_CONNECTION_STRING="${MSSQL_CONNECTION_STRING}" \
  --restart unless-stopped \
  ${IMAGE_NAME}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Container đã được khởi động${NC}"
else
    echo -e "${RED}  ✗ Khởi động container thất bại${NC}"
    exit 1
fi

# Kiểm tra container đang chạy
echo ""
echo -e "${YELLOW}[5/5] Kiểm tra container...${NC}"
sleep 3
sudo docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${GREEN}=========================================="
echo -e "✓ Deploy thành công!"
echo -e "==========================================${NC}"
echo ""
echo "Container đang chạy tại:"
echo "  Web UI: http://localhost:${PORT}"
echo "  API Docs: http://localhost:${PORT}/docs"
echo ""
echo "Các lệnh hữu ích:"
echo "  Xem logs: sudo docker logs -f ${CONTAINER_NAME}"
echo "  Stop: sudo docker stop ${CONTAINER_NAME}"
echo "  Restart: sudo docker restart ${CONTAINER_NAME}"
echo "  Xem status: sudo docker ps --filter 'name=${CONTAINER_NAME}'"

