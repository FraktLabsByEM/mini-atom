import json
import random
import string
from datetime import datetime

import ollama
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

# Model name
model = "llama3.2:3b-instruct-q8_0"

# Server instance
app = Flask(__name__)
CORS(app)

# Function to convert date string into timestamp
def string2timestamp(text_date):
    """
    Convert string date into timestamp
    Args:
        text_date (str): String date given by ollama

    Returns:
        int: Timestamp
    """
    # Limit to 26 chars
    cleaned = text_date[:26]
    # Create date from string
    dt = datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S.%f")
    # Return timestamp
    return dt.timestamp()

@app.route("/v1/completions", methods=["POST"])
def completions():
    """
    Params:
    - model
    - prompt
    - temperature
    - stream
    - max_tokens
    - top_p
    Return:
    - id
    - object
    - created
    - model
    - choices
    - usage
    """
    try:
        # Retrieve params object
        params = request.get_json()
        #Retrieve each param
        prompt = params.get("prompt") or None
        stream = str(params.get("stream") or "").lower() in ["1", "true", "yes", "on"]
        res_id = ''.join(random.choices(string.ascii_letters, k=10))
        
        if not prompt:
            return jsonify({ "error": "Param \"prompt\" is required." }), 301
        
        # Validate stream response
        if stream:
            def iterator():
                # Request prediction
                stream_response = ollama.generate(
                    model=model,
                    prompt=prompt,
                    stream=True
                )
                count = 0
                # Execute callback with each chunk received
                for chunk in stream_response:
                    
                    #Build openai like object
                    res = {
                        "id": "chatcmpl-" + res_id + str(count),
                        "created": string2timestamp(chunk.created_at),
                        "object": "completion.chunk",
                        "model": "atom-v1-mini",
                        "choices": [
                            {
                                "delta": {
                                    "role": "assistant",
                                    "content": chunk.response
                                },
                                "finish_reason": chunk.done_reason,
                                "index": count
                            }
                        ]
                    }
                    # Update chunk count
                    count += 1
                    # Return processed chunk
                    yield f"data: {json.dumps(res, separators=(',',':'), ensure_ascii=False)}\n\n"
                
                yield f"data: [DONE]"
                  
            # Execute iterator
            return Response(stream_with_context(iterator()),mimetype='text/event-stream')
        else:
            try:
                # Request prediction
                response = ollama.generate(
                    model=model,
                    prompt=prompt
                )
                # Build openai like response
                return jsonify({
                        "id": "chatcmpl-" + res_id ,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "index": 0,
                                "logprobs": None,
                                "text": response.response
                            }
                        ],
                        "created": string2timestamp(response.created_at),
                        "model": "atom-v1-mini",
                        "object": "text_completion",
                        "usage": {
                            "prompt_tokens": response.prompt_eval_count,
                            "completion_tokens": response.eval_count,
                            "total_tokens": response.prompt_eval_count + response.eval_count
                        }
                    }), 200
            except Exception as err:
                return jsonify({ "error": str(err) }), 301
    except Exception as err:
        return jsonify({ "error": err }), 200
    
@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    """
    Params:
    - model
    - messages
    - temperature
    - stream
    - max_tokens
    - top_p
    - stop
    Return:
    - id
    - object
    - created
    - model
    - choices
    - usage
    """
    print("chat_completions")
    try:
     # Retrieve params object
        params = request.get_json()
        #Retrieve each param
        messages = params.get("messages") or None
        stream = str(params.get("stream") or "").lower() in ["1", "true", "yes", "on"]
        res_id = ''.join(random.choices(string.ascii_letters, k=10))
        
        if not messages:
            return jsonify({ "error": "Param \"messages\" is required." }), 301
        
        # Validate stream response
        if stream:
            def iterator():
                # Request prediction
                stream_response = ollama.chat(
                    model=model,
                    messages=messages,
                    stream=True
                )
                count = 0
                # Execute callback with each chunk received
                for chunk in stream_response:
                    print(chunk)
                    #Build openai like object
                    res = {
                        "id": "chatcmpl-" + res_id + str(count),
                        "created": string2timestamp(chunk.created_at),
                        "object": "completion.chunk",
                        "model": "atom-v1-mini",
                        "choices": [
                            {
                                "delta": {
                                    "role": "assistant",
                                    "content": chunk.message.content
                                },
                                "finish_reason": chunk.done_reason,
                                "index": count
                            }
                        ]
                    }
                    # Update chunk count
                    count += 1
                    # Return processed chunk
                    yield f"data: {json.dumps(res, separators=(',',':'), ensure_ascii=False)}\n\n"
                
                yield f"data: [DONE]"
                  
            # Execute iterator
            return Response(stream_with_context(iterator()),mimetype='text/event-stream')
        else:
            try:
                # Request prediction
                response = ollama.chat(
                    model=model,
                    messages=messages
                )
                print(response)
                # Build openai like response
                return jsonify({
                        "id": "chatcmpl-" + res_id ,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "index": 0,
                                "logprobs": None,
                                "message": {
                                    "role": "assistant",
                                    "content": response.message.content
                                }
                            }
                        ],
                        "created": string2timestamp(response.created_at),
                        "model": "atom-v1-mini",
                        "object": "text_completion",
                        "usage": {
                            "prompt_tokens": response.prompt_eval_count,
                            "completion_tokens": response.eval_count,
                            "total_tokens": response.prompt_eval_count + response.eval_count
                        }
                    }), 200
            except Exception as err:
                return jsonify({ "error": str(err) }), 301
    except Exception as err:
        return jsonify({ "error": err }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2866)