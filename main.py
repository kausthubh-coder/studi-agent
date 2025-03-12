import asyncio
import argparse
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

# Import with compatibility for both running directly and as part of package
try:
    # When running from within the agent directory
    from agent import CanvasAgent  # try absolute import first
    from config import OPENAI_API_KEY, CANVAS_ACCESS_TOKEN
except ImportError:
    # When running as part of the agent package
    import agent  # make sure agent is found as a package
    from agent.agent import CanvasAgent
    from agent.config import OPENAI_API_KEY, CANVAS_ACCESS_TOKEN

def print_welcome():
    """Print welcome message and basic instructions"""
    print("\n======================================================")
    print("  Welcome to Canvas Assistant - Terminal Interface")
    print("======================================================")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'reset' to clear the conversation history")
    print("Type 'help' to see these instructions again")
    print("======================================================\n")

async def validate_environment():
    """Validate required environment variables are set"""
    missing_vars = []
    
    if not OPENAI_API_KEY:
        missing_vars.append("OPENAI_API_KEY")
    
    if not CANVAS_ACCESS_TOKEN:
        missing_vars.append("CANVAS_ACCESS_TOKEN")
    
    if missing_vars:
        logger.error("Missing required environment variables")
        print("Error: The following required environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in a .env file or in your environment.")
        print("Example .env file format:")
        print("OPENAI_API_KEY=your_openai_api_key")
        print("CANVAS_ACCESS_TOKEN=your_canvas_token")
        sys.exit(1)

async def main_loop(debug=False):
    """
    Main conversation loop with the Canvas agent
    
    Args:
        debug: Whether to enable debug mode
    """
    # Validate environment variables
    await validate_environment()
    
    # Initialize agent with debug flag
    agent = CanvasAgent(debug=debug)
    
    # Print welcome message
    print_welcome()
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("> ")
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit"]:
                print("Thank you for using Canvas Assistant. Goodbye!")
                break
            
            # Check for reset command
            if user_input.lower() == "reset":
                agent.reset_context()
                print("Conversation history has been reset.")
                continue
            
            # Check for help command
            if user_input.lower() == "help":
                print_welcome()
                continue
            
            # Process user input and get response
            print("Processing...")
            response = await agent.process_message(user_input)
            
            # Print agent response
            print("\nCanvas Assistant:")
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user. Exiting...")
            break
            
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}", exc_info=True)
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again or type 'exit' to quit.")

def main():
    """Entry point function"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Canvas Assistant Terminal Interface")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        args = parser.parse_args()
        
        # Set logging level based on debug flag
        if args.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
            print("Debug mode enabled. Verbose logging will be displayed.")
        
        # Run the main loop with debug flag
        asyncio.run(main_loop(debug=args.debug))
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 