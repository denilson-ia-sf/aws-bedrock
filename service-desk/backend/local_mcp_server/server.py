import os
import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as types
from mcp.server.stdio import stdio_server

# Initialize the MCP Server for Active Directory Management
server = Server("active-directory-mcp")

# Mock Local Database to handle tests without a real Windows Domain Controller
MOCK_USERS = {
    "john.doe": {"cn": "John Doe", "mail": "john.doe@company.com", "status": "Active", "ou": "IT-Operations"},
    "jane.smith": {"cn": "Jane Smith", "mail": "jane.smith@company.com", "status": "Locked", "ou": "HR"}
}

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List the Active Directory toolset exposed to the LLM agent."""
    return [
        types.Tool(
            name="search_user",
            description="Searches for a specific user profile in the Active Directory or domain controller.",
            input_schema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The exact sAMAccountName or username to look up (e.g., 'john.doe')"}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="reset_user_password",
            description="Resets the domain password for a user account and forces a password change on next login.",
            input_schema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The target username requiring a credential reset"}
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="unlock_user",
            description="Unlocks a locked domain account in the Active Directory infrastructure.",
            input_schema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The username of the locked account to unlock"}
                },
                "required": ["username"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Execute the corresponding Active Directory infrastructure tool logic."""
    if not arguments:
        return [types.TextContent(type="text", text="Error: Missing arguments for tool operation.")]

    username = arguments.get("username", "").lower()
    
    # --- ACTIVE DIRECTORY MOCK/SIMULATION LOGIC ---
    # This ensures your chatbot runs smoothly on your laptop without errors
    if name == "search_user":
        if username in MOCK_USERS:
            user = MOCK_USERS[username]
            response_text = f"SUCCESS: Target user directory entry matched.\nCN: {user['cn']}\nEmail: {user['mail']}\nAccount Status: {user['status']}\nOrganizational Unit: {user['ou']}"
        else:
            response_text = f"ERROR: Directory search executed. User record '{username}' does not exist in Active Directory domain."
            
    elif name == "reset_user_password":
        if username in MOCK_USERS:
            response_text = f"SUCCESS: Temporary domain password generated and set for user '{username}'. Status updated to force password update upon network login change."
        else:
            response_text = f"ERROR: Security validation failed. Cannot perform password reset. User identity '{username}' not registered."
            
    elif name == "unlock_user":
        if username in MOCK_USERS:
            MOCK_USERS[username]["status"] = "Active"
            response_text = f"SUCCESS: Domain account controller constraint cleared. Account profile '{username}' is now fully Unlocked and Active."
        else:
            response_text = f"ERROR: Action terminated. Could not resolve user account context for string '{username}'."
            
    else:
        response_text = f"ERROR: Tool command context '{name}' not bound on this server instance."

    return [types.TextContent(type="text", text=response_text)]

async def main():
    # Run the server using lightweight standard input/output transport loop
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="active-directory-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
