"""
MCP Server (stdio) for Cursor integration
"""
import sys
import json
from typing import Optional

from .handlers import MCPHandler


class MCPServer:
    """
    MCP Server that communicates via stdio (stdin/stdout).
    This is what Cursor connects to.
    """
    
    def __init__(self):
        """Initialize server with handler"""
        self.handler = MCPHandler()
        self.running = False
    
    def parse_line(self, line: str) -> dict:
        """
        Parse JSON from input line.
        
        Args:
            line: Input line from stdin
            
        Returns:
            Parsed JSON as dict
        """
        return json.loads(line.strip())
    
    def format_response(self, response: dict) -> str:
        """
        Format response as JSON line.
        
        Args:
            response: Response dict
            
        Returns:
            JSON string with newline
        """
        return json.dumps(response) + "\n"
    
    def process_request(self, line: str) -> str:
        """
        Process a single request line.
        
        Args:
            line: Input JSON line
            
        Returns:
            Output JSON line
        """
        try:
            request = self.parse_line(line)
            response = self.handler.handle_request(request)
            return self.format_response(response)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            return self.format_response(error_response)
    
    def run_once(self):
        """
        Process a single request from stdin.
        Useful for testing.
        """
        line = sys.stdin.readline()
        if line:
            response = self.process_request(line)
            sys.stdout.write(response)
            sys.stdout.flush()
    
    def run(self):
        """
        Main server loop.
        Reads from stdin, writes to stdout.
        """
        self.running = True
        
        # Log startup (to stderr so it doesn't interfere with protocol)
        sys.stderr.write("MCP-AIDev server starting...\n")
        sys.stderr.flush()
        
        try:
            while self.running:
                line = sys.stdin.readline()
                
                if not line:
                    # EOF - client disconnected
                    break
                
                if not line.strip():
                    continue
                
                response = self.process_request(line)
                sys.stdout.write(response)
                sys.stdout.flush()
                
        except KeyboardInterrupt:
            sys.stderr.write("Server shutting down...\n")
        except Exception as e:
            sys.stderr.write(f"Server error: {e}\n")
        finally:
            self.running = False
            sys.stderr.write("MCP-AIDev server stopped.\n")
            sys.stderr.flush()


def main():
    """Entry point for MCP server"""
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main()

