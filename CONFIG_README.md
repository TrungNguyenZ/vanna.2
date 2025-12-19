# Hướng dẫn cấu hình Vanna AI Server

## Giới thiệu

Project này sử dụng file `.env` để quản lý cấu hình cho AI model và database connections. Bạn có thể dễ dàng thay đổi AI provider (Anthropic, OpenAI, Gemini) và database (SQLite, PostgreSQL, MySQL, SQL Server) mà không cần sửa code.

## Cài đặt nhanh

### 1. Cài đặt dependencies cơ bản

```bash
pip install python-dotenv
```

### 2. Tạo file .env

Sao chép file mẫu và điền thông tin của bạn:

```bash
cp .env.example .env
```

### 3. Cấu hình AI Provider

Chọn một trong các AI providers sau:

#### Anthropic (Claude) - Mặc định
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5
```

Cài đặt package:
```bash
pip install anthropic
```

#### OpenAI (GPT)
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4
```

Cài đặt package:
```bash
pip install openai
```

#### Google Gemini
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=xxxxx
GEMINI_MODEL=gemini-pro
```

Cài đặt package:
```bash
pip install google-generativeai
```

### 4. Cấu hình Database

Chọn một trong các database sau:

#### SQLite (Mặc định - Đơn giản nhất)
```env
DB_TYPE=sqlite
SQLITE_DATABASE_PATH=./data/database.db
```

Không cần cài thêm package.

#### PostgreSQL
```env
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_SCHEMA=public
```

Cài đặt package:
```bash
pip install psycopg2-binary
```

#### MySQL
```env
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=your_database
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
```

Cài đặt package:
```bash
pip install pymysql
```

#### Microsoft SQL Server
```env
DB_TYPE=mssql
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=your_database
MSSQL_USER=your_username
MSSQL_PASSWORD=your_password
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
```

Cài đặt package:
```bash
pip install pyodbc
```

**Lưu ý**: Bạn cần cài đặt ODBC Driver trước:
- Windows: [Microsoft ODBC Driver](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- macOS: `brew install msodbcsql17`
- Linux: [Installation Guide](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

### 5. Cấu hình Server (Optional)

```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
```

## Chạy Server

Sau khi cấu hình xong, chạy lệnh:

```bash
python run_server.py
```

Server sẽ chạy tại: `http://localhost:8001`

## Ví dụ cấu hình đầy đủ

### Cấu hình 1: Claude + SQLite (Đơn giản nhất)
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5

DB_TYPE=sqlite
SQLITE_DATABASE_PATH=./data/database.db

SERVER_HOST=0.0.0.0
SERVER_PORT=8001
```

### Cấu hình 2: OpenAI + PostgreSQL
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4

DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=my_database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpass
POSTGRES_SCHEMA=public

SERVER_HOST=0.0.0.0
SERVER_PORT=8001
```

### Cấu hình 3: Gemini + MySQL
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=xxxxx
GEMINI_MODEL=gemini-pro

DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=my_database
MYSQL_USER=root
MYSQL_PASSWORD=mysecretpass

SERVER_HOST=0.0.0.0
SERVER_PORT=8001
```

## Troubleshooting

### Lỗi: "ANTHROPIC_API_KEY is not set"
Kiểm tra file `.env` và đảm bảo đã set API key:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Lỗi: Import Error
Cài đặt package tương ứng với provider/database bạn đang dùng. Xem phần "Cấu hình AI Provider" và "Cấu hình Database" ở trên.

### Lỗi: Database Connection
- Kiểm tra database đang chạy
- Kiểm tra thông tin kết nối (host, port, username, password)
- Kiểm tra firewall và network

## Bảo mật

**QUAN TRỌNG**: 
- File `.env` chứa thông tin nhạy cảm (API keys, passwords)
- File `.env` đã được thêm vào `.gitignore` để tránh commit lên Git
- **KHÔNG BAO GIỜ** commit file `.env` lên repository công khai
- Chỉ chia sẻ file `.env.example` (không chứa thông tin thật)
