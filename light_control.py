import Sasha_code.flux_led_v3 as flux_led
import time
ips = []
strobe_state = False
jump_state = False
color_memory = []
force = False
delay = 0.1
# get the IP addresses of the controllers on your local network

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
    except:
        # quit so that I don't hold port 48899. if that doesn't work:
        # sudo lsof -i:48899
        # sudo kill -9 <pid>
        quit()


def set_colors(colors):
    global color_memory, force, delay

    new_colors = [True for memory, color in zip(colors, color_memory)
                  if color != memory[0]]
    if not force and not any(new_colors):
        return

    for color, ip, memory in zip(colors, ips, color_memory):
        print("Handle IP [{}]:".format(ip))
        if not force and color == memory[0]:
            continue
        try:

            bulb = get_bulb(ip)
            memory = [color] + memory[:4]
            # todo when the knife switch is set it changes the way the light goes
            # this module should keep a color 'memory' that it plays
            # todo delay should be controllable
            # todo keep color memory
            # todo don't update needlessly if no change, to allow states to play
            if jump_state:
                bulb.setCustomPattern(memory, delay, 'jump')
            elif strobe_state:
                bulb.setCustomPattern(memory, delay, 'gradual')
            else:
                bulb.setRgb(*color)

            time.sleep(0.05)

        except Exception as e:
            print("Unable to connect to bulb at [{}]: {}".format(ip, e))
            continue
    force = False


def number_of_lights():
    return len(ips)

search_for_lights()
