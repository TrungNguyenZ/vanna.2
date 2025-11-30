"""Script test đơn giản để chạy Vanna agent."""

import asyncio
from vanna import Agent, AgentConfig, MockLlmService
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, RequestContext, User
from vanna.integrations.local.agent_memory import DemoAgentMemory


class SimpleUserResolver(UserResolver):
    """Simple user resolver for demo."""

    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(
            id="test_user",
            email="test@example.com",
            group_memberships=["user"],
        )


async def main():
    """Test agent."""
    print("Dang khoi tao Vanna Agent...")
    
    # Tạo agent
    llm_service = MockLlmService(
        response_content="Xin chao! Toi la Vanna AI assistant. Toi co the giup ban tao SQL queries tu ngon ngu tu nhien."
    )
    
    tool_registry = ToolRegistry()
    user_resolver = SimpleUserResolver()
    agent_memory = DemoAgentMemory(max_items=1000)
    
    agent = Agent(
        llm_service=llm_service,
        tool_registry=tool_registry,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
        config=AgentConfig(
            stream_responses=True,
            include_thinking_indicators=True,
        ),
    )
    
    print("Agent da duoc khoi tao thanh cong!")
    print("\n" + "="*50)
    
    # Tạo request context
    request_context = RequestContext(
        cookies={},
        headers={},
        remote_addr="127.0.0.1",
    )
    
    # Gửi message
    user_message = "Xin chao! Ban co the gioi thieu ve minh khong?"
    print(f"User: {user_message}\n")
    print("Agent: ", end="", flush=True)
    
    response_parts = []
    async for component in agent.send_message(
        request_context=request_context,
        message=user_message,
        conversation_id="test_conv_1",
    ):
        if hasattr(component, "content") and component.content:
            print(component.content, end="", flush=True)
            response_parts.append(component.content)
    
    print("\n" + "="*50)
    
    if response_parts:
        print(f"\nAgent da phan hoi thanh cong!")
    else:
        print(f"\nAgent khong co phan hoi (co the do MockLlmService)")
    
    print("\nTest hoan tat!")


if __name__ == "__main__":
    asyncio.run(main())

