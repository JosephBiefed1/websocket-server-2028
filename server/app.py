# ...existing code...
#!/usr/bin/env python

import asyncio
from websockets import serve

# track connected clients
CONNECTED = set()

async def broadcast(message: str):
    dead = set()
    for ws in list(CONNECTED):
        try:
            await ws.send(message)
        except Exception:
            dead.add(ws)
    for d in dead:
        CONNECTED.discard(d)

async def handler(websocket):
    CONNECTED.add(websocket)
    addr = websocket.remote_address
    print(f"Client connected: {addr}")
    try:
        async for message in websocket:
            print(f"Received from {addr}: {message}")
            await broadcast(message)  # broadcast plain string to all clients
    except Exception as e:
        print("WebSocket handler error:", e)
    finally:
        CONNECTED.discard(websocket)
        print(f"Client disconnected: {addr}")

# --- added plain TCP bridge handler ---
async def handle_plain_tcp(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info('peername')
    print("Plain TCP client connected:", peer)
    try:
        while True:
            # read one line (STM32 currently sends "temperature : N\r\n")
            data = await reader.readline()
            if not data:
                break
            try:
                line = data.decode(errors='replace').rstrip('\r\n')
            except Exception:
                line = repr(data)
            print(f"TCP received from {peer}: {line}")
            # broadcast to websockets clients
            await broadcast(line)
    except Exception as e:
        print("Plain TCP handler error:", e)
    finally:
        writer.close()
        await writer.wait_closed()
        print("Plain TCP client disconnected:", peer)
# --- end added bridge ---

async def main():
    # start websocket server on 2028
    ws_server = await serve(handler, "0.0.0.0", 2028)
    print("WebSocket server listening on ws://0.0.0.0:2028")

    # start plain TCP server on 2029 (change STM32 DEST_PORT to 2029)
    tcp_server = await asyncio.start_server(handle_plain_tcp, "0.0.0.0", 2029)
    sa = tcp_server.sockets[0].getsockname()
    print(f"Plain TCP server listening on {sa}")

    try:
        await asyncio.Future()  # run forever
    finally:
        ws_server.close()
        await ws_server.wait_closed()
        tcp_server.close()
        await tcp_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
# ...existing code...