import board
import displayio
import framebufferio
import rgbmatrix
import gifio
import time
import busio

displayio.release_displays()

# MATRIX SETUP
matrix = rgbmatrix.RGBMatrix(
    width=64,
    height=32,
    bit_depth=1,
    rgb_pins=[
        board.MTX_R1, board.MTX_G1, board.MTX_B1,
        board.MTX_R2, board.MTX_G2, board.MTX_B2
    ],
    addr_pins=[
        board.MTX_ADDRA, board.MTX_ADDRB,
        board.MTX_ADDRC, board.MTX_ADDRD
    ],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
)

display = framebufferio.FramebufferDisplay(matrix)

# UART for TFmini-S LiDAR
uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=0.0)

def read_lidar():
    if uart.in_waiting >= 9:
        if uart.read(1) == b'\x59':
            if uart.read(1) == b'\x59':
                data = uart.read(7)
                if data and len(data) >= 7:
                    distance = data[0] + (data[1] << 8)
                    return distance
    return None

# GIF SETUP
gif = gifio.OnDiskGif("/my_animation.gif")
tile = displayio.TileGrid(
    gif.bitmap,
    pixel_shader=displayio.ColorConverter(
        input_colorspace=displayio.Colorspace.RGB565_SWAPPED
    )
)
group = displayio.Group()
group.append(tile)
display.root_group = group

current_distance = 300.0  
SMOOTHING = 0.4           
last_print_time = 0
MAX_DIST = 250  

# MAIN LOOP
while True:
    dist = read_lidar()
    if dist is not None and 10 <= dist <= 400:
        current_distance = (SMOOTHING * dist) + ((1.0 - SMOOTHING) * current_distance)

    if time.monotonic() - last_print_time > 0.5:
        print(f"Distance: {int(current_distance)} cm")
        last_print_time = time.monotonic()

    # Freeze if outside active range
    if current_distance >= MAX_DIST:
        time.sleep(0.1)
        continue  

    gif.next_frame()
    time.sleep(0.05)