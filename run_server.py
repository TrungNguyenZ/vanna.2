"""Script để chạy Vanna server với FastAPI."""

from vanna.examples.mock_quickstart import create_demo_agent
from vanna.servers.fastapi import VannaFastAPIServer

if __name__ == "__main__":
    print("Dang khoi tao agent...")
    agent = create_demo_agent()
    print("Agent da duoc khoi tao!")
    
    print("\nDang khoi dong FastAPI server...")
    print("Server se chay tai: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("\nNhan Ctrl+C de dung server\n")
    
    server = VannaFastAPIServer(agent)
    server.run(host="0.0.0.0", port=8000)



