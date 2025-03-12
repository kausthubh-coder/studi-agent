import json
import logging
from typing import List, Dict, Any, Optional

# Import with compatibility for both running directly and as part of package
try:
    # When running from within the agent directory
    from openai_client import OpenAIClient
    from canvas_client import CanvasClient
    from config import DEFAULT_SYSTEM_PROMPT, MAX_CONTEXT_LENGTH
except ImportError:
    # When running as part of the agent package
    from agent.openai_client import OpenAIClient
    from agent.canvas_client import CanvasClient
    from agent.config import DEFAULT_SYSTEM_PROMPT, MAX_CONTEXT_LENGTH

# Set up logging
logger = logging.getLogger("canvas_agent")
logger.setLevel(logging.DEBUG)

class CanvasAgent:
    """
    Canvas AI Agent with MCP (Monitor, Control, Plan) architecture
    """
    
    def __init__(self, debug=False):
        """
        Initialize the Canvas agent with dependencies and context
        
        Args:
            debug: Whether to enable debug mode
        """
        self.debug = debug
        self.openai = OpenAIClient()
        self.canvas = CanvasClient(debug=debug)
        self.context = []
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        
        if self.debug:
            print("DEBUG: CanvasAgent initialized with debug mode enabled")
        
        # Available tools for the agent
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_courses",
                    "description": "Get a list of courses the user is enrolled in",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_course_details",
                    "description": "Get detailed information about a specific course",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "course_id": {
                                "type": "integer",
                                "description": "The ID of the course to retrieve"
                            }
                        },
                        "required": ["course_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_assignments",
                    "description": "Get assignments for a specific course",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "course_id": {
                                "type": "integer",
                                "description": "The ID of the course to retrieve assignments for"
                            }
                        },
                        "required": ["course_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_assignment_summary",
                    "description": "Get a summary of important assignments (late and upcoming) across all courses",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "max_courses": {
                                "type": "integer",
                                "description": "Maximum number of courses to check (default: 5)",
                                "default": 5
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_upcoming_assignments",
                    "description": "Get assignments that are due in the next X days for a course",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "course_id": {
                                "type": "integer",
                                "description": "The ID of the course"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to look ahead (default: 14)",
                                "default": 14
                            }
                        },
                        "required": ["course_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_late_assignments",
                    "description": "Get assignments that are past due and not submitted for a course",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "course_id": {
                                "type": "integer",
                                "description": "The ID of the course"
                            }
                        },
                        "required": ["course_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_assignment_details",
                    "description": "Get comprehensive details about a specific assignment, including instructions, files, and submission requirements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "course_id": {
                                "type": "integer",
                                "description": "The ID of the course"
                            },
                            "assignment_id": {
                                "type": "integer",
                                "description": "The ID of the assignment"
                            }
                        },
                        "required": ["course_id", "assignment_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_assignment",
                    "description": "Find an assignment by name or keyword in a specific course",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "course_id": {
                                "type": "integer",
                                "description": "The ID of the course"
                            },
                            "name_pattern": {
                                "type": "string",
                                "description": "Full or partial name of the assignment to find (case insensitive)"
                            }
                        },
                        "required": ["course_id", "name_pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_profile",
                    "description": "Get the current user's profile information",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    async def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response
        
        Args:
            message: User's message
            
        Returns:
            Agent's response
        """
        try:
            # Add user message to context
            self.context.append({"role": "user", "content": message})
            
            # Maintain context length
            if len(self.context) > MAX_CONTEXT_LENGTH:
                self.context = self.context[-MAX_CONTEXT_LENGTH:]
            
            if self.debug:
                print(f"DEBUG: Processing user message: {message}")
            
            # Generate response from OpenAI with tools
            response = await self.openai.generate_with_tools(
                system_prompt=self.system_prompt,
                messages=self.context,
                tools=self.tools
            )
            
            # Handle function calls if present
            result = response["content"]
            if response["tool_calls"]:
                if self.debug:
                    print(f"DEBUG: Tool calls detected: {response['tool_calls']}")
                try:
                    result = await self._handle_tool_calls(response["tool_calls"])
                except Exception as e:
                    # If tool call handling fails, return the error as part of the response
                    if self.debug:
                        print(f"DEBUG: Error handling tool calls: {str(e)}")
                    logger.error(f"Error handling tool calls: {str(e)}")
                    result = f"I tried to retrieve information from Canvas, but encountered an error: {str(e)}\n\nPlease check your Canvas API configuration and ensure the server is running."
            
            # Add assistant response to context
            self.context.append({"role": "assistant", "content": result})
            
            return result
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"I'm sorry, I encountered an error while processing your message: {str(e)}"
    
    async def _handle_tool_calls(self, tool_calls) -> str:
        """
        Handle function calls from the assistant
        
        Args:
            tool_calls: List of tool calls from the OpenAI response
            
        Returns:
            Result of function execution as a string
        """
        results = []
        errors = []
        
        # Flag to track if we'll have a large response
        large_response = False
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if self.debug:
                print(f"DEBUG: Handling tool call: {function_name}")
                print(f"DEBUG: Tool arguments: {function_args}")
            
            try:
                # Execute the appropriate function based on name
                if function_name == "get_courses":
                    result = await self.canvas.get_courses()
                    # Only send concise information to avoid token issues
                    simplified_result = []
                    for course in result:
                        simplified_result.append({
                            "id": course.get("id"),
                            "name": course.get("name")
                        })
                    results.append(f"Courses: {json.dumps(simplified_result, indent=2)}")
                
                elif function_name == "get_course_details":
                    course_id = function_args.get("course_id")
                    result = await self.canvas.get_course(course_id)
                    results.append(f"Course Details: {json.dumps(result, indent=2)}")
                
                elif function_name == "get_assignments":
                    course_id = function_args.get("course_id")
                    result = await self.canvas.get_assignments(course_id)
                    
                    # This could be a large response, so mark it
                    if len(result) > 10:
                        large_response = True
                        
                    # Simplify to reduce token usage
                    simplified_result = []
                    for assignment in result[:15]:  # Limit to 15 assignments
                        simplified_result.append({
                            "id": assignment.get("id"),
                            "name": assignment.get("name"),
                            "due_at": assignment.get("due_at"),
                            "points_possible": assignment.get("points_possible"),
                            "submitted": assignment.get("submitted", False)
                        })
                    results.append(f"Assignments: {json.dumps(simplified_result, indent=2)}")
                
                elif function_name == "get_assignment_summary":
                    max_courses = function_args.get("max_courses", 5)
                    result = await self.canvas.get_assignment_summary(max_courses=max_courses)
                    results.append(f"Assignment Summary: {json.dumps(result, indent=2)}")
                
                elif function_name == "get_upcoming_assignments":
                    course_id = function_args.get("course_id")
                    days = function_args.get("days", 14)
                    result = await self.canvas.get_upcoming_assignments(course_id, days)
                    
                    # Simplify to reduce token usage
                    simplified_result = []
                    for assignment in result:
                        simplified_result.append({
                            "id": assignment.get("id"),
                            "name": assignment.get("name"),
                            "due_at": assignment.get("due_at"),
                            "points_possible": assignment.get("points_possible")
                        })
                    results.append(f"Upcoming Assignments: {json.dumps(simplified_result, indent=2)}")
                
                elif function_name == "get_late_assignments":
                    course_id = function_args.get("course_id")
                    result = await self.canvas.get_late_assignments(course_id)
                    
                    # Simplify to reduce token usage
                    simplified_result = []
                    for assignment in result:
                        simplified_result.append({
                            "id": assignment.get("id"),
                            "name": assignment.get("name"),
                            "due_at": assignment.get("due_at"),
                            "points_possible": assignment.get("points_possible")
                        })
                    results.append(f"Late Assignments: {json.dumps(simplified_result, indent=2)}")
                
                elif function_name == "get_assignment_details":
                    course_id = function_args.get("course_id")
                    assignment_id = function_args.get("assignment_id")
                    result = await self.canvas.get_assignment_details(course_id, assignment_id)
                    results.append(f"Assignment Details: {json.dumps(result, indent=2)}")
                
                elif function_name == "find_assignment":
                    course_id = function_args.get("course_id")
                    name_pattern = function_args.get("name_pattern")
                    result = await self.canvas.find_assignment_by_name(course_id, name_pattern)
                    if result:
                        results.append(f"Found Assignment: {json.dumps(result, indent=2)}")
                    else:
                        results.append(f"No assignment found matching '{name_pattern}' in course {course_id}")
                
                elif function_name == "get_user_profile":
                    result = await self.canvas.get_user_profile()
                    results.append(f"User Profile: {json.dumps(result, indent=2)}")
            except Exception as e:
                error_msg = f"Error executing {function_name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                if self.debug:
                    print(f"DEBUG: {error_msg}")
        
        # Add function results to context
        for result in results:
            self.context.append({"role": "function", "name": function_name, "content": result})
        
        # If there were errors, add them to context as well
        if errors:
            error_content = "Errors encountered:\n" + "\n".join(errors)
            self.context.append({"role": "function", "name": "error_report", "content": error_content})
        
        # If we detected a potentially large response, use a more targeted system prompt
        # to make the final response more concise
        target_system_prompt = self.system_prompt
        if large_response:
            target_system_prompt = self.system_prompt + "\nGive very concise responses. Focus on only the most important information. Summarize details rather than listing everything."
            
        # Get final response with function results
        final_response = await self.openai.generate_response(
            system_prompt=target_system_prompt,
            messages=self.context
        )
        
        return final_response
    
    def reset_context(self):
        """Reset the conversation context"""
        if self.debug:
            print("DEBUG: Resetting conversation context")
        self.context = [] 