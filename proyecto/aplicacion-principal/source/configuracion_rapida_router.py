#!/usr/bin/env  python3
import time, pyautogui, pyperclip
arr=[
    "conf t",
    "enable secret 12345678",
    "service password-encryption",
    "ip domain-name proyecto-final.com",
    "ip ssh rsa keypair-name 1234",
    "crypto key generate rsa usage-keys label 1234 modulus 1024",
    "ip ssh v 2",
    "ip ssh time-out 30",
    "ip ssh authentication-retries 3",
    "line vty 1 15",
    "password 1234",
    "login local",
    "transport input ssh telnet",
    "exit",
    "aaa new-model",
    "aaa authentication login default local",
    "aaa authentication enable default enable",
    "username admin privilege 15 password admin01",
    "end"
]

time.sleep(3)
for i in arr:
    if "-" in i:
        arr2=i.split("-")
        for j in range(len(arr2)):
            if j==len(arr2)-1:
                pyautogui.typewrite(arr2[j])
                pyautogui.press("enter")
            else:
                pyautogui.typewrite(arr2[j])
                time.sleep(2)
        arr2.clear()
    else:
        pyautogui.typewrite(i)
        pyautogui.press("enter")
    time.sleep(1)
