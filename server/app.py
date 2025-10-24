#!/usr/bin/env python
# ...existing code...
import asyncio
from websockets import serve
import http
import os
import signal

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

# accept both old/new websockets handler signatures
async def handler(websocket, path=None):
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

# health check used by websockets' process_request hook
def process_request(path, request_headers):
    if path == "/healthz":
        return (http.HTTPStatus.OK, [("Content-Type", "text/plain")], b"OK\n")
    return None

# --- plain TCP bridge handler ---
async def handle_plain_tcp(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info('peername')
    print("Plain TCP client connected:", peer)
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            try:
                line = data.decode(errors='replace').rstrip('\r\n')
            except Exception:
                line = repr(data)
            print(f"TCP received from {peer}: {line}")
            await broadcast(line)
    except Exception as e:
        print("Plain TCP handler error:", e)
    finally:
        writer.close()
        await writer.wait_closed()
        print("Plain TCP client disconnected:", peer)
# --- end bridge ---

async def main():
    port = int(os.environ.get("PORT", "2028"))

    # start websocket server (bind all interfaces)
    ws_server = await serve(handler, "0.0.0.0", port, process_request=process_request)
    print(f"WebSocket server listening on ws://0.0.0.0:{port}")

    # start plain TCP server for raw STM32 connections (e.g. port 2029)
    tcp_server = await asyncio.start_server(handle_plain_tcp, "0.0.0.0", 2029)
    sa = tcp_server.sockets[0].getsockname()
    print(f"Plain TCP server listening on {sa}")

    # (optional) safe signal handler registration on Unix only
    try:
        loop = asyncio.get_running_loop()
        if hasattr(loop, "add_signal_handler"):
            try:
                loop.add_signal_handler(signal.SIGTERM, ws_server.close)
            except Exception:
                pass
    except Exception:
        pass

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