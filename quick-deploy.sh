#!/bin/bash
# Script nhanh để deploy - chỉ cần chạy lệnh này

# Stop và xóa container cũ
sudo docker stop vanna-agents 2>/dev/null || true
sudo docker rm vanna-agents 2>/dev/null || true

# Pull image mới nhất
sudo docker pull trungnguyen131/vanna-agents:latest

# Chạy container mới
sudo docker run -d \
  --name vanna-agents \
  -p 3001:3001 \
  -e GOOGLE_API_KEY=AIzaSyDBEjSG_AFbyRHcAk4npxiKknqxu-9c0lU \
  -e MSSQL_CONNECTION_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=103.124.92.168;DATABASE=TestAI;UID=dev;PWD=Trung@1122" \
  --restart unless-stopped \
  trungnguyen131/vanna-agents:latest

echo "✓ Container đã được khởi động!"
echo "Kiểm tra: sudo docker ps --filter 'name=vanna-agents'"
echo "Logs: sudo docker logs -f vanna-agents"

