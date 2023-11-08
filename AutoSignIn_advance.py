import os
import pip
import json

import schedule
import tkinter as tk
from tkinter import scrolledtext
import QuantLib as ql

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class AutoSignIn():

    def initialize(self):
        # Upgrade package of work-calendar
        # pip.main(['install', '--upgrade', "QuantLib"])
        # Download chromedriver automatically
        chromedriver_autoinstaller.install()

        # Load Account Information from json
        with open(os.getcwd() + "/config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)

        # Initial work-calendar
        self.cal = ql.Taiwan()
        # Add custom Holiday
        for i in self.config['holiday']:
            self.cal.addHoliday(ql.DateParser.parseFormatted(i, '%Y/%m/%d'))
        for i in self.config['workday']:
            self.cal.removeHoliday(ql.DateParser.parseFormatted(i, '%Y/%m/%d'))

    def sched(self):
        schedule.run_pending()
        # Schedule Start
        self.job = self.window.after(20000, self.sched)

    def start(self):
        self.initialize()
        self.buttonStart['text'] = 'processing...'
        self.buttonStart.configure(state='disabled')
        self.buttonStop.configure(state='normal')
        # Schedule Start
        schedule.every().day.at(self.config["signin"]).do(self.sign, 'login')
        schedule.every().day.at(self.config["signout"]).do(self.sign, 'logout')
        self.sched()
        
    def sign(self, status):
        if ( self.cal.isBusinessDay(ql.Date.todaysDate()) ):
            option = Options().add_argument('--headless')
            chrome = webdriver.Chrome(options=option)
            chrome.get("https://hr2sys.tmu.edu.tw/tmu_planhum_full/login_full_duty.aspx")
            chrome.maximize_window()
            # Setting login information
            account = chrome.find_element(By.ID, "UserName")
            account.clear()
            account.send_keys(self.config['username'])  # ID
            password = chrome.find_element(By.ID, "Password")
            password.clear()
            password.send_keys(self.config['password']) # password

            if status == 'login':
                chrome.find_element(by=By.ID, value='LoginButton').click()
            else:
                chrome.find_element(by=By.ID, value='logoutbtn').click()

            try:
                print(chrome.find_element(by=By.CLASS_NAME, value='red-text').text)
            except NoSuchElementException:
                print(chrome.find_element(by=By.CLASS_NAME, value='form-group').text)

            chrome.close()

    def stop(self):
        self.buttonStart['text'] = 'Start'
        self.buttonStop.configure(state='disabled')
        self.buttonStart.configure(state='normal')
        
        if self.job is not None:
            self.window.after_cancel(self.job)
        self.job = None

        schedule.clear()
    
    def search(self):
        try:
            # Validate input format
            start = ql.DateParser.parseFormatted(self.startDate.get(), "%Y/%m/%d")
            end = ql.DateParser.parseFormatted(self.endDate.get(), "%Y/%m/%d")
            self.warningText.config(text="")
            holidayList = ql.Calendar.holidayList(self.cal, start, end)

            # Clear search text box
            self.daysList.config(state="normal")
            self.daysList.delete('1.0', tk.END)
            
            i = 0
            for day in holidayList:
                if(i == 2):
                    i = 0
                    self.daysList.insert(tk.END, day.ISO() + "\n")
                else:
                    self.daysList.insert(tk.END, day.ISO() + "     ")
                    i += 1
            self.daysList.config(state="disabled")
        except:
            self.warningText.config(text="Input formatted : YYYY/MM/DD", fg='#f00')

    def __init__(self):
        self.initialize()
        self.window = tk.Tk()
        self.window.title("TMU AutoSigner")
        self.window.geometry('300x300')
        self.window.resizable(False, False)  # Fix windows

        # Show text 
        label1 = tk.Label(self.window, text="Welcome to TMU AutoSigner", font=("Helvetica bold", 13))
        label1.grid(column=0, row=0, columnspan=4)
        # Start button
        self.buttonStart = tk.Button(self.window, text='Start', width=8, height=1, command=self.start)
        self.buttonStart.grid(column=0, row=1, columnspan=2)
        # Stop button
        self.buttonStop = tk.Button(self.window, text='Stop', width=8, height=1, command=self.stop, state='disabled')
        self.buttonStop.grid(column=2, row=1, columnspan=2)
        # Divider text
        spliteLine = tk.Label(self.window, text="-----  Search Holidays Exclude Weekends -----")
        spliteLine.grid(column=0, row=2, columnspan=4)
        # Warning text
        self.warningText = tk.Label(self.window, text="")
        self.warningText.grid(column=0, row=3, columnspan=4)
        # Start date input box
        startLabel = tk.Label(self.window, text="from:")
        startLabel.grid(column=0, row=4)
        self.startDate = tk.Entry(self.window, width=10)
        self.startDate.grid(column=1, row=4)
        # End date input box
        endLabel = tk.Label(self.window, text="to:")
        endLabel.grid(column=2, row=4)
        self.endDate = tk.Entry(self.window, width=10)
        self.endDate.grid(column=3, row=4)
        # Search button
        self.buttonSearch = tk.Button(self.window, text='Search Holidays', width=10, height=1, command=self.search)
        self.buttonSearch.grid(column=0, row=5, columnspan=4)
        
        # text box
        self.daysList = scrolledtext.ScrolledText(self.window, width=40, height=10)
        self.daysList.grid(column=0, row=6, columnspan=4, pady = 10)
        self.daysList.insert(tk.END, "No result")
        
        self.window.mainloop()

AutoSignIn()