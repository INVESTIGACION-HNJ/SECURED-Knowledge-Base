import asyncio
import websockets
import math
import json
import os

SERVER_ROOT = ""
SERVER_URI = SERVER_ROOT + "/ws/upload"
CHUNK_SIZE = 1024 * 64

async def upload_file(remote_name, category, local_path):


    async with websockets.connect(SERVER_URI) as websocket:

        print("Just connected to server.")

        file_stream = open(local_path, "rb")
        file_size = os.path.getsize(local_path)
        total_chunks = math.ceil(file_size / CHUNK_SIZE)


        await websocket.send(json.dumps({
            "type": "start_upload",
            "fileName": remote_name,
            "category": category,
            "totalChunks": total_chunks
        }))

        while True:
            response = await websocket.recv()
            message = json.loads(response)

            if message["type"] == "upload_progress":
                print("Progress: ", message["progress"])
                chunk = file_stream.read(CHUNK_SIZE)

                if not chunk:
                    await websocket.send(json.dumps({
                        "type": "end_upload",
                        "fileName": remote_name,
                    }))
                    continue

                text_chunk = chunk.decode("latin1")
                await websocket.send(json.dumps({
                    "type": "file_chunk",
                    "fileName": remote_name,
                    "chunk": text_chunk
                }))
                # print(f"Download started: {message['fileName']} with {message['total_chunks']} chunks")
            
            if message["type"] == "upload_complete":
                await websocket.send(json.dumps({
                    "type": "close_connection"
                }))
                break

        file_stream.close()
            

