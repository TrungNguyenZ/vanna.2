# MongoDB Integration

Tích hợp MongoDB để lưu lịch sử chat và quản lý training data cho Vanna Agents.

## Tính năng

1. **Lưu lịch sử chat vào MongoDB**: Tự động lưu tất cả các cuộc trò chuyện vào MongoDB
2. **Quản lý Training Data**: 
   - Training data mặc định (default)
   - Training data từ chat (from_chat)
3. **API CRUD cho Training Data**: Thêm, sửa, xóa, tìm kiếm training data
4. **Sử dụng Training Data trong AI**: AI sẽ tự động sử dụng training data trước khi trả lời

## Cài đặt

Thêm `pymongo` vào dependencies (đã được thêm vào `pyproject.toml`):

```bash
pip install pymongo
```

## Cấu hình

### 1. Cấu hình MongoDB qua biến môi trường

Tạo file `.env` trong thư mục gốc của project và thêm các biến sau:

```bash
# Option 1: Sử dụng connection string (khuyến nghị)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=vanna

# Option 2: Sử dụng các tham số riêng lẻ

# Trường hợp 1: MongoDB không có authentication (local development)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE_NAME=vanna
# Không cần MONGODB_USERNAME và MONGODB_PASSWORD

# Trường hợp 2: MongoDB có authentication
# MONGODB_HOST=localhost
# MONGODB_PORT=27017
# MONGODB_USERNAME=your_username
# MONGODB_PASSWORD=your_password
# MONGODB_DATABASE_NAME=vanna
```

**Ví dụ các connection string:**
- Local MongoDB (không auth): `mongodb://localhost:27017/`
- Local MongoDB (có auth): `mongodb://username:password@localhost:27017/`
- MongoDB Atlas: `mongodb+srv://username:password@cluster.mongodb.net/`
- MongoDB với database: `mongodb://localhost:27017/vanna`

**Lưu ý:** Nếu MongoDB của bạn không có authentication (thường là trường hợp local development), bạn chỉ cần:
- `MONGODB_HOST` và `MONGODB_PORT` (hoặc `MONGODB_CONNECTION_STRING`)
- `MONGODB_DATABASE_NAME`
- **KHÔNG CẦN** `MONGODB_USERNAME` và `MONGODB_PASSWORD`

### 2. Thiết lập MongoDB Connection trong code

```python
from vanna.integrations.mongodb import MongoDBConnection
import os
from dotenv import load_dotenv

# Load biến môi trường từ .env file
load_dotenv()

# Sử dụng connection string từ biến môi trường
mongo_connection = MongoDBConnection(
    # Không cần truyền tham số, sẽ tự động đọc từ biến môi trường
    # connection_string=os.getenv("MONGODB_CONNECTION_STRING"),
    # database_name=os.getenv("MONGODB_DATABASE_NAME", "vanna"),
)

# Hoặc truyền trực tiếp
mongo_connection = MongoDBConnection(
    connection_string="mongodb://localhost:27017/",
    database_name="vanna",
)
```

**Lưu ý:** Nếu không truyền tham số nào, `MongoDBConnection` sẽ tự động đọc từ biến môi trường theo thứ tự ưu tiên:
1. Connection string từ `MONGODB_CONNECTION_STRING`
2. Các tham số riêng lẻ từ `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`
3. Mặc định: `mongodb://localhost:27017/`

### 3. Tạo Stores

```python
from vanna.integrations.mongodb.chat_store import MongoChatStore
from vanna.integrations.mongodb.training_store import MongoTrainingStore

chat_store = MongoChatStore(mongo_connection)
training_store = MongoTrainingStore(mongo_connection)
```

### 4. Tạo Training Data Context Enhancer

```python
from vanna.core.enhancer.training_data_enhancer import TrainingDataContextEnhancer

training_enhancer = TrainingDataContextEnhancer(training_store)
```

### 5. Cấu hình Agent với MongoDB

```python
from vanna.core import Agent
from vanna.servers.base import ChatHandler
from vanna.servers.fastapi import VannaFastAPIServer

# Tạo agent với training data enhancer
agent = Agent(
    llm_service=...,
    tool_registry=...,
    user_resolver=...,
    agent_memory=...,
    llm_context_enhancer=training_enhancer,  # Sử dụng training data enhancer
)

# Tạo chat handler với MongoDB stores
chat_handler = ChatHandler(
    agent=agent,
    mongo_chat_store=chat_store,
    mongo_training_store=training_store,
)
```

### 6. Khởi tạo FastAPI Server

```python
server = VannaFastAPIServer(agent=agent, config={})
app = server.create_app()

# Cập nhật chat_handler trong routes
# (Cần cập nhật routes.py để sử dụng chat_handler với MongoDB stores)
```

## API Endpoints

### Training Data

- `POST /api/vanna/v2/training-data` - Tạo training data mới
- `GET /api/vanna/v2/training-data` - Liệt kê training data
- `GET /api/vanna/v2/training-data/{id}` - Lấy training data theo ID
- `PUT /api/vanna/v2/training-data/{id}` - Cập nhật training data
- `DELETE /api/vanna/v2/training-data/{id}` - Xóa training data

### Chat History

- `GET /api/vanna/v2/conversations` - Liệt kê conversations (đã có sẵn)
- `GET /api/vanna/v2/conversations/{id}` - Lấy conversation theo ID (đã có sẵn)

## Sử dụng trong Frontend

### Thêm Training Data từ Chat

Khi chat, người dùng có thể chọn checkbox "Lưu vào training data" để lưu cuộc trò chuyện vào training data.

### Request Format

```typescript
{
  message: "Câu hỏi của người dùng",
  conversation_id: "conv_abc123",
  request_id: "req_xyz789",
  save_to_training: true,  // Thêm option này
  metadata: {}
}
```

## Ví dụ

Xem file `examples/mongodb_integration_example.py` để biết cách sử dụng chi tiết.

## Cấu trúc Database

### Collection: `chat_history`

```json
{
  "_id": "ObjectId",
  "conversation_id": "conv_abc123",
  "user_id": "user_123",
  "messages": [
    {
      "role": "user",
      "content": "Câu hỏi",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Câu trả lời",
      "timestamp": "2024-01-01T00:00:01Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:01Z"
}
```

### Collection: `training_data`

```json
{
  "_id": "ObjectId",
  "question": "Câu hỏi",
  "sql": "SELECT * FROM ...",
  "answer": "Câu trả lời",
  "data_type": "default" | "from_chat",
  "conversation_id": "conv_abc123",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Cấu hình Docker

Nếu sử dụng Docker, thêm các biến môi trường MongoDB vào `docker-compose.yml`:

```yaml
environment:
  - MONGODB_CONNECTION_STRING=${MONGODB_CONNECTION_STRING:-mongodb://localhost:27017/}
  - MONGODB_DATABASE_NAME=${MONGODB_DATABASE_NAME:-vanna}
  - MONGODB_HOST=${MONGODB_HOST}
  - MONGODB_PORT=${MONGODB_PORT:-27017}
  - MONGODB_USERNAME=${MONGODB_USERNAME}
  - MONGODB_PASSWORD=${MONGODB_PASSWORD}
```

## Lưu ý

1. **Biến môi trường ưu tiên:** Nếu truyền tham số trực tiếp vào `MongoDBConnection()`, nó sẽ được ưu tiên hơn biến môi trường
2. **Connection string vs tham số riêng:** Nếu có cả `MONGODB_CONNECTION_STRING` và các tham số riêng lẻ, connection string sẽ được ưu tiên
3. **Training data enhancer:** Sẽ tự động tìm kiếm và thêm training data liên quan vào system prompt
4. **Chat history:** Được lưu tự động cho mọi cuộc trò chuyện khi có `mongo_chat_store` được cấu hình
5. **Training data từ chat:** Chỉ được lưu khi người dùng chọn checkbox "Lưu vào training data" trong UI
6. **python-dotenv:** Đảm bảo cài đặt `python-dotenv` để load biến môi trường từ file `.env`:
   ```bash
   pip install python-dotenv
   ```

