
# -*- coding: utf-8 -*-

#Created on Thu Nov 22 17:31:36 2018

#@author: �\�ѷ�  m610107005

import json
import os

import time
import schedule
import datetime
import tkinter as tk
import threading

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException



#------------------------------------------------------------------------------
running=1

# Load Account Information from json
with open(os.getcwd() + "/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
#------------------------------------------------------------------------------
def AutoSign(status):

    print (datetime.date.today())
    
    chromedriver_autoinstaller.install()
    option = Options().add_argument('--headless')
    chrome = webdriver.Chrome(options=option)
    chrome.get("https://hr2sys.tmu.edu.tw/tmu_planhum_full/login_full_duty.aspx")
    
    account = chrome.find_element(by=By.NAME, value="UserName").clear()
    account.send_keys(config['username'])  #---------------------------<<<<<<ID
    
    password = chrome.find_element(by=By.NAME, value="Password").clear()
    password.send_keys(config['password']) #------------------------<<<<<<PW
    
    
    #elem.send_keys(Keys.TAB);
    if status == 'login':
        chrome.find_element(by=By.NAME, value='LoginButton').click()
    else:
        chrome.find_element(by=By.NAME, value='logoutbtn').click()
    
    try:
        print(chrome.find_element(by=By.CLASS_NAME, value='red-text').text)
    except NoSuchElementException:
        print(chrome.find_element(by=By.CLASS_NAME, value='form-group').text)

    chrome.close()
    print ('-----------------------------------------------------')


#------------------------------------------------------------------------------
def stop():
    global running
    running=0
    buttonEnd.configure(state='disabled')

    if buttonStart['text'] == 'start':
        print('error')
        buttonEnd.configure(state='disabled')
    else:
        buttonStart['text'] = 'start'
        buttonStart.configure(state='normal')

def t():
    def start():
        schedule.every().monday.at(config['signin']).do(AutoSign, 'login') 
        schedule.every().monday.at(config['signout']).do(AutoSign, 'logout')
    
        schedule.every().tuesday.at(config['signin']).do(AutoSign, 'login') 
        schedule.every().tuesday.at(config['signout']).do(AutoSign, 'logout')
    
        schedule.every().wednesday.at(config['signin']).do(AutoSign, 'login') 
        schedule.every().wednesday.at(config['signout']).do(AutoSign, 'logout')
        
        schedule.every().thursday.at(config['signin']).do(AutoSign, 'login') 
        schedule.every().thursday.at(config['signout']).do(AutoSign, 'logout')
    
        schedule.every().friday.at(config['signin']).do(AutoSign, 'login') 
        schedule.every().friday.at(config['signout']).do(AutoSign, 'logout')    
    
        if buttonStart['text'] == 'start':
            buttonStart['text'] = 'processing...'
            global running
            running=1
        else:
            buttonStart['text'] = 'start'    
            
        if buttonStart['text']=='processing...':
            buttonStart.configure(state='disabled')
            buttonEnd.configure(state='normal')
            
        else:
            buttonStart.configure(state='normal')
            buttonEnd.configure(state='disabled')
    
        while running:
            print('processing...')
            schedule.run_pending()
            time.sleep(20)  

    t = threading.Thread(target = start)
    t.start()

#------------------------------------------------------------------------------
window=tk.Tk()
window.title("TMU AutoSigner")
window.geometry('300x150')
window.resizable(False, False)

label1=tk.Label(window, text="Welcome to TMU AutoSigner")
label1.pack()

buttonStart = tk.Button(window, text='start', width=15,height=2 , command=t)
buttonStart.pack()

buttonEnd = tk.Button(window, text='stop', width=15, height=2, command=stop, state='disabled')
buttonEnd.pack()

window.mainloop()