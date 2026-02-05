import asyncio
from websocket_download import download_file

async def main():
    # if you are the server:
    await download_file("tcn-server-env", "docker_files", "./.env") # .env file
    await download_file("tcn-server-compose", "docker_files", "./compose.yml") # compose file
    # if you are the client:
    #await download_file("tcn-client-env", "docker_files", "./.env") # .env file
    #await download_file("tcn-client-compose", "docker_files", "./compose.yml") # compose file

    #await download_file("tcn-client-env", "docker_files", "./.env") # .env file
    #await download_file("tcn-client-compose", "docker_files", "./compose.yml") # compose file

if __name__ == "__main__":
    asyncio.run(main())