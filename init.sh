#!/bin/bash

# Join main directory
cd /mini-atom

#Validate repo
if [ -d "/mini-atom/repo" ]; then
    source repo/bin/activate
else
    python -m venv repo
    source repo/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
fi

# Execute native ollama server

ollama serve &
sleep 5
echo Downloading model
# Download model
ollama pull llama3.2:3b-instruct-q8_0

# Execute python server
python llm-server.py &

tail -f /dev/null
