from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sys
import os
import asyncio
import json
import logging
import threading
from queue import Queue, Empty
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.customer_chatbot import create_customer_chatbot, create_human_proxy
from agents.financial_advisor import run_conversation_financial_advisor
from agents.boss_manager import create_boss_human_loop
from orchestrator_direct import run_conversation_boss_manager

# Create required directories if they don't exist
os.makedirs("webapp/static", exist_ok=True)
os.makedirs("webapp/templates", exist_ok=True)

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

# Templates
templates = Jinja2Templates(directory="webapp/templates")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global variables for message handling
message_queue = Queue()
response_queue = Queue()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        # Create agents
        customer_chatbot = create_customer_chatbot()
        human_proxy = create_human_proxy()
        
        # Send initial welcome message
        welcome_msg = "Hello, I'm here to help you with your financial goals and recommend you products that may suit you best."
        await websocket.send_text(json.dumps({
            "type": "bot",
            "agent": "customer_chatbot",
            "content": welcome_msg
        }))

        def get_human_input(prompt):
            # Debug: Log the incoming prompt
            logging.info(f"Raw prompt received: {prompt}")
            
            # Split the prompt into sections by the separator
            sections = prompt.split("--------------------------------------------------------------------------------")
            bot_message = None
            
            # Process each section to find the most recent bot message
            for section in reversed(sections):  # Process sections in reverse to get the most recent message
                if not section.strip():
                    continue
                
                lines = section.strip().split('\n')
                for i, line in enumerate(lines):
                    if "FinGenie_Customer_Bot (to human_proxy):" in line:
                        # Get the next non-empty line as the message
                        for j in range(i + 1, len(lines)):
                            potential_message = lines[j].strip()
                            if potential_message and not potential_message.startswith("Replying as") and not potential_message.startswith(">>>>>>>> USING AUTO REPLY"):
                                bot_message = potential_message
                                break
                        if bot_message:  # If we found a message, break out of the outer loop
                            break
                if bot_message:  # If we found a message, break out of the sections loop
                    break
            
            # Debug: Log the extracted bot message
            logging.info(f"Extracted bot message: {bot_message}")
            
            # If we found a message and it's not empty
            if bot_message:
                logging.info(f"Sending bot message to queue: {bot_message}")
                message_queue.put({
                    "type": "bot",
                    "agent": "customer_chatbot",
                    "content": bot_message
                })
            else:
                logging.warning("No valid bot message found in the conversation")
            
            # Then send the input prompt
            message_queue.put({
                "type": "input_prompt",
                "content": "Please provide your response:"
            })
            
            # Wait for and return the response
            return response_queue.get()

        # Override get_human_input with our version
        human_proxy.get_human_input = get_human_input
        
        # Create a thread for running the chat
        def run_chat():
            try:
                result = customer_chatbot.initiate_chat(
                    human_proxy,
                    message=welcome_msg,
                    summary_prompt="Summarize the details of the customer's profile including information about their income, savings, and goals. Do not add any introductory phrases.",
                    summary_method="reflection_with_llm"
                )
                message_queue.put(("DONE", result))
            except Exception as e:
                logging.error(f"Error in chat thread: {str(e)}")
                message_queue.put(("ERROR", str(e)))

        chat_thread = threading.Thread(target=run_chat)
        chat_thread.start()

        # Main event loop for handling WebSocket messages
        while True:
            try:
                # Check for prompts from the chat thread
                try:
                    message = message_queue.get_nowait()
                    if isinstance(message, tuple):
                        status, content = message
                        if status == "ERROR":
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "content": f"Error in chat process: {content}"
                            }))
                            break
                        elif status == "DONE":
                            customer_profile = content.summary if hasattr(content, 'summary') else str(content)
                            
                            # Step 2: Financial Advisor Analysis
                            await websocket.send_text(json.dumps({
                                "type": "status",
                                "content": "Analyzing profile with Financial Advisor..."
                            }))
                            
                            advisor_result = await asyncio.to_thread(run_conversation_financial_advisor)
                            
                            # Step 3: Boss Manager Review
                            await websocket.send_text(json.dumps({
                                "type": "status",
                                "content": "Getting final approval from Boss Manager..."
                            }))
                            
                            final_result = await asyncio.to_thread(run_conversation_boss_manager, advisor_result)
                            
                            # Send final results
                            await websocket.send_text(json.dumps({
                                "type": "bot",
                                "agent": "system",
                                "content": "Based on our analysis, here are the final recommendations:"
                            }))
                            
                            await websocket.send_text(json.dumps({
                                "type": "bot",
                                "agent": "financial_advisor",
                                "content": f"Financial Analysis:\n{advisor_result}"
                            }))
                            
                            await websocket.send_text(json.dumps({
                                "type": "bot",
                                "agent": "boss_manager",
                                "content": f"Final Approved Recommendations:\n{final_result.summary if hasattr(final_result, 'summary') else str(final_result)}"
                            }))
                            break
                    else:
                        # It's either a bot message or input prompt
                        # Debug: Log the message being sent
                        logging.info(f"Sending message to websocket: {message}")
                        await websocket.send_text(json.dumps(message))
                        # Add a small delay to ensure messages are processed in order
                        await asyncio.sleep(0.1)
                except Empty:
                    pass

                # Check for user messages
                try:
                    user_message = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                    logging.info(f"Received message: {user_message}")
                    response_queue.put(user_message)
                except asyncio.TimeoutError:
                    pass

            except WebSocketDisconnect:
                logging.info("WebSocket disconnected")
                break
            except Exception as e:
                logging.error(f"Error in WebSocket loop: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": f"Error occurred: {str(e)}"
                }))
                break

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": f"Error occurred: {str(e)}"
            }))
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 