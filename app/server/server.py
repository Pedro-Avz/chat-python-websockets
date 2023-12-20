import asyncio
import websockets
import json

clients = set()

async def handle_client(websocket, path):
    try:
        username_message = await websocket.recv()
        parsed_username_message = json.loads(username_message)
        username = parsed_username_message['username']
        clients.add((websocket, username))
        print(f"Nova conexão de {username}")

        async for message in websocket:
            await broadcast(username, message)
    finally:
        # Certificar-se de que a conexão ainda está presente no conjunto antes de removê-la
        if (websocket, username) in clients:
            clients.remove((websocket, username))
            # Enviar mensagem de desconexão para os outros clientes
            await broadcast_server_message(f"{username} se desconectou do chat")


async def broadcast(sender_username, message):
    formatted_message = f"{sender_username}: {message}"

    # Criar uma cópia do conjunto para evitar o erro "Set changed size during iteration"
    clients_copy = clients.copy()

    for client, client_username in clients_copy:
        try:
            if client_username == sender_username:
                await client.send(f"Você: {message}")
            else:
                await client.send(formatted_message)
        except:
            clients.remove((client, client_username))
            await broadcast_server_message(f"{client_username} se desconectou do chat")


async def broadcast_server_message(message):
    for client, _ in clients:
        try:
            await client.send(f"{message}")
        except:
            pass 


async def main():
    server = await websockets.serve(handle_client, "localhost", 8080)
    print("Servidor iniciado. Aguardando conexões...")

    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())