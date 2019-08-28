import asyncio

BUFSIZE = 2**30 # about 1 GB

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 13513)
    with open('data.csv', 'rb') as f:
        dat = f.read()

    print(f'Send: {message!r}')
    # writer.write(message.encode())
    writer.write(dat)

    data = await reader.read(BUFSIZE)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

asyncio.run(tcp_echo_client('Hello World!'))