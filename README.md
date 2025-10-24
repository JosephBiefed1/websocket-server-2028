* app.py runs two listeners:
  * WebSocket server on port 2028 (accepts browser WebSocket handshake from main.js).
  * Plain TCP server on port 2029 (accepts raw TCP from the STM32).
* STM32 (your C code) opens a plain TCP connection to the PC IP at port 2029 and sends lines like "temperature : 23\r\n".
* app.py’s TCP handler reads those lines (it uses reader.readline()), decodes them to strings, and calls broadcast(...).
* broadcast(...) sends text frames to all connected WebSocket clients (the websockets library packages them correctly).
* main.js has an open WebSocket to ws://`<pc-ip-or-hostname>`:2028. It receives those messages as ws message events, parses/formats them, and updates index.html.


This works for local communication
