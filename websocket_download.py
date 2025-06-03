import asyncio
import websockets
import json

SERVER_ROOT = ""
SERVER_URI = SERVER_ROOT + "/ws/download"

async def download_file(remote_name, category, local_path):


    async with websockets.connect(SERVER_URI) as websocket:

        print("Just connected to server.")

        await websocket.send(json.dumps({
            "type": "start_download",
            "fileName": remote_name,
            "category": category
        }))

        file_stream = open(local_path, "wb")

        if not file_stream:
            return

        while True:
            response = await websocket.recv()
            message = json.loads(response)

            if message["type"] == "download_ready":
                print("yess")
                await websocket.send(json.dumps({
                    "type": "file_chunk"
                }))
                # print(f"Download started: {message['fileName']} with {message['total_chunks']} chunks")
            
            elif message["type"] == "file_chunk":
                chunk_data = message["chunk"].encode("latin1")
                file_stream.write(chunk_data)
                print(f"Received chunk {message['chunk_index']} - {message['progress']:.2f}%")

                # Request next chunk
                await websocket.send(json.dumps({
                    "type": "file_chunk"
                }))

            elif message["type"] == "download_complete":
                file_stream.close()
                # print(f"Download complete: {message['fileName']}")
                await websocket.send(json.dumps({
                    "type": "close_connection"
                }))
                break
            

