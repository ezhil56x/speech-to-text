### Speech-to-Text

1. Start whisper docker container with the following command
```
docker run -d -p 5005:5005 --name whisper-cpu --restart always ezhil56x/whisper-cpu-server
```

2. Go to client directory and create a virtual environment
```
cd client
python -m venv venv
```

3. Activate the virtual environment
```
source venv/bin/activate
```

4. Install the required packages
```
pip install -r requirements.txt
```

5. Run the client
```
python speech-to-text.py
```

6. Instead of typing the text, you can hold the F9 key to record your voice and release it to stop recording. The transcribed text will be displayed in the text area.