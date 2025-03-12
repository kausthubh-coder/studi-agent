import openai
import json
import logging
from typing import List, Dict, Any

# Import with compatibility for both running directly and as part of package
try:
    # When running from within the agent directory
    from config import OPENAI_API_KEY, OPENAI_MODEL
except ImportError:
    # When running as part of the agent package
    from agent.config import OPENAI_API_KEY, OPENAI_MODEL

# Set up logging
logger = logging.getLogger("openai_client")
logger.setLevel(logging.DEBUG)

class OpenAIClient:
    """Client for interacting with OpenAI API"""
    
    def __init__(self, debug=False):
        """
        Initialize the OpenAI client with API key from config
        
        Args:
            debug: Whether to enable debug mode
        """
        self.client = openai.Client(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.debug = debug
        
        logger.info(f"OpenAI client initialized with model: {self.model}")
        if self.debug:
            print(f"DEBUG: OpenAI client initialized with model: {self.model}")
        
    async def generate_response(self, 
                         system_prompt: str, 
                         messages: List[Dict[str, str]]) -> str:
        """
        Generate a response from OpenAI based on system prompt and message history
        
        Args:
            system_prompt: The system instructions for the assistant
            messages: List of message dictionaries with role and content
            
        Returns:
            The assistant's response as a string
        """
        try:
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
            
            if self.debug:
                print(f"DEBUG: Sending request to OpenAI with {len(full_messages)} messages")
                print(f"DEBUG: System prompt: {system_prompt[:100]}...")
            
            logger.debug(f"Generating response with {len(messages)} user messages")
            
            # Make request to OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=0.7,
            )
            
            # Extract and return the response text
            response_text = response.choices[0].message.content
            
            if self.debug:
                print(f"DEBUG: Received response from OpenAI ({len(response_text)} chars)")
            
            return response_text
            
        except Exception as e:
            # Handle API errors
            logger.error(f"Error calling OpenAI API: {str(e)}")
            if self.debug:
                print(f"DEBUG: Error calling OpenAI API: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    async def generate_with_tools(self, 
                          system_prompt: str, 
                          messages: List[Dict[str, str]],
                          tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a response with function calling capabilities
        
        Args:
            system_prompt: The system instructions for the assistant
            messages: List of message dictionaries
            tools: List of tool definitions
            
        Returns:
            The complete response object including potential function calls
        """
        try:
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
            
            if self.debug:
                print(f"DEBUG: Sending request to OpenAI with tools")
                print(f"DEBUG: Tool count: {len(tools)}")
            
            logger.debug(f"Generating response with tools ({len(tools)} tools available)")
            
            # Make request to OpenAI with tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=tools,
                temperature=0.7,
            )
            
            tool_calls = response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else None
            
            if self.debug and tool_calls:
                print(f"DEBUG: OpenAI response includes {len(tool_calls)} tool call(s)")
                for tc in tool_calls:
                    print(f"DEBUG: Tool call - {tc.function.name}")
            
            return {
                "content": response.choices[0].message.content,
                "tool_calls": tool_calls
            }
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API with tools: {str(e)}")
            if self.debug:
                print(f"DEBUG: Error calling OpenAI API with tools: {str(e)}")
            return {
                "content": f"I'm sorry, I encountered an error: {str(e)}",
                "tool_calls": None
            } 