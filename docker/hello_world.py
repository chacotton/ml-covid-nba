import time

if __name__ == '__main__':
    with open('./hello_world.txt', 'w') as f:
        f.write('Hello World\n')
        f.write(f'Time: {time.time()}')
