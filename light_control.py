import Sasha_code.flux_led_v3 as flux_led
import time
import colorsys

ips = ['test']
strobe_state = False
jump_state = False
color_memory = []
force = False
delay = 100
# get the IP addresses of the controllers on your local network
GLOBAL_BRIGHTNESS = 0.1

bulbs = {}


def get_bulb(ip):
    global bulbs
    if ip not in bulbs:
        bulbs[ip] = flux_led.WifiLedBulb(ip)
    return bulbs[ip]


def search_for_lights():

    global ips, color_memory
    try:
        scanner = flux_led.BulbScanner()
        scanner.scan(timeout=2)
        bulb_info_list = scanner.getBulbInfo()
        # we have a list of buld info dicts
        addrs = []
        if len(bulb_info_list) > 0:
            for b in bulb_info_list:
                addrs.append(b['ipaddr'])
        print('Found {} controllers'.format(len(addrs)))
        ips = addrs
        color_memory = [[] for _ in range(len(ips))]
    except Exception as e:

        import traceback
        traceback.print_exc()

        # quit so that I don't hold port 48899. if that doesn't work:
        # sudo lsof -i:48899
        # sudo kill -9 <pid>
        # quit()


def set_colors(colors):
    global color_memory, force, delay

    new_colors = [True for memory, color in zip(colors, color_memory)
                  if color != memory[0]]
    if not force and not any(new_colors):
        return

    for color, ip, memory in zip(colors, ips, color_memory):
        color = [val % 255 for val in color]
        h, s, v = colorsys.rgb_to_hsv(*color)
        color = colorsys.hsv_to_rgb(h, s, v * GLOBAL_BRIGHTNESS)
        color = [int(val) for val in color]

        print("Handle IP [{}]:".format(ip))
        if not force and (memory and color == memory[0]):
            # todo this is an important line - it controls the texture of tails
            memory.insert(0, color)
            del memory[5:]
            continue
        try:

            bulb = get_bulb(ip)
            # use mutation operations to save this.
            memory.insert(0, color)
            print(memory)
            del memory[5:]
            if jump_state:
                print('jump')
                bulb.setCustomPattern(memory, delay, 'jump')
            elif strobe_state:
                print('strobe')
                bulb.setCustomPattern(memory, delay, 'strobe')
            else:
                bulb.setRgb(*color)

            time.sleep(0.05)

        except Exception as e:
            print("Unable to connect to bulb at [{}]: {}".format(ip, e))
            continue
    force = False


def number_of_lights():
    return len(ips)


def main():
    global jump_state
    search_for_lights()
    strobe_state = True
    print(f" found {number_of_lights()} leds!")
    set_colors([[255, 0, 0] for _ in ips])
    time.sleep(0.5)
    set_colors([[0, 255, 0] for _ in ips])
    time.sleep(0.5)
    set_colors([[0, 0, 255] for _ in ips])
    time.sleep(0.5)
    set_colors([[255, 255, 0] for _ in ips])
    time.sleep(0.5)
    set_colors([[0, 255, 255] for _ in ips])

if __name__ == '__main__':
    main()
