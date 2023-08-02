from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time
import random

import os
import sys
import numpy as np

def checkResults(browser, pageNum):
    print(f"Checking results for page {pageNum}...")
    options = Options()
    options.add_argument("--headless") # disable window pop-up
    browser = webdriver.Firefox(options=options)
    browser.get(f"https://www.linkedin.com/search/results/people/?keywords=recruiter%20ibm&origin=CLUSTER_EXPANSION&page={pageNum}&sid=Yx3")
    try:
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, f"/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[1]/section/h2")) # No Results Found Page
        )
        browser.close()
        return False
    except:
        browser.close()
        return True
    
def parseHrefs(browser):
    allValidHrefs = []
    findHref = browser.find_elements('class name', 'app-aware-link')
    prevHref = ""
    for i in range(len(findHref)):
        if "/in/" in findHref[i].get_attribute('href') and findHref[i].get_attribute('href') != prevHref:
            if findHref[i].get_attribute('href')[28] == "A":
                continue
            allValidHrefs.append(findHref[i].get_attribute('href'))
            prevHref = findHref[i].get_attribute('href')
        else:
            continue
    return allValidHrefs



credentialsFile = 'logincredentials.json'

if os.path.isfile(credentialsFile):
    with open(credentialsFile, 'r') as file:
        loginCredentials = json.load(file)
else:
    linkedInCredential1 = input("Enter your LinkedIn email or phone number: ")
    linkedInCredential2 = input("Enter your LinkedIn password: ")
    loginCredentials = {"email/phone": linkedInCredential1, "password": linkedInCredential2}
    
    with open(credentialsFile, 'w') as file:
        file.write(json.dumps(loginCredentials, indent=4))

emailphone = loginCredentials["email/phone"]
password = loginCredentials["password"]

companies = input("Enter desired companies (separated by commas): ").split(",") # Ask user for desired companies

# options = Options()
# options.add_argument("--headless") # disable window pop-up

# initialize browser
for company in range(len(companies)):
    try:
        browser = webdriver.Firefox()
        browser.get(f"https://www.linkedin.com/search/results/people/?keywords=recruiter%20{companies[company]}&origin=CLUSTER_EXPANSION&sid=Yx3")
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/p/a"))
            )
            browser.find_element('xpath', '/html/body/div[1]/main/div/p/a').click()
        except:
            print("No sign in button found.")
            browser.quit()

        time.sleep(2)

        credential1Box = browser.find_element('xpath','//*[@id="username"]')
        credential1Box.click()
        credential1Box.send_keys(emailphone)

        credential2Box = browser.find_element('xpath','//*[@id="password"]')
        credential2Box.click()
        credential2Box.send_keys(password)

        browser.find_element('xpath','/html/body/div/main/div[2]/div[1]/form/div[3]/button').click() #sign in button

        currentPage = 1

        while checkResults(browser, currentPage):
            browser.get(f"https://www.linkedin.com/search/results/people/?keywords=recruiter%20ibm&origin=CLUSTER_EXPANSION&page={currentPage}&sid=Yx3")

            listOfHrefs = parseHrefs(browser)

            outfile = open(f"{companies[company].upper()}_recruiters.txt", "w+")

            for i in listOfHrefs:
                urlID = ''.join(i.split("in/")[1].split("?")[0])
                outfile.write("URLID: " + urlID + "\nLink to Profile: " + i + " \n\n")

            # companyname = companies[company].lower()
            # neededRole = ['recruiter', 'recruiting', 'lead', 'talent', 'acquisition', companyname]

            # searchRecruiters = browser.find_elements('class name', 'entity-result__primary-subtitle')
            # searchRecruitersRole = browser.find_elements('class name', 'entity-result__summary')

            # for role in range(len(searchRecruiters)):
            #     roleDesc = searchRecruiters[role].text.lower().split()
            #     currentLen = len(roleDesc)

            #     if f"at {companyname}" in searchRecruiters[role].text.lower() or f"at {companyname}" in searchRecruitersRole[role].text.lower():
            #         if f"at {companyname}" not in searchRecruiters[role].text.lower() and f"at {companyname}" in searchRecruitersRole[role].text.lower():
            #             print(searchRecruitersRole[role].text)
            #             continue
            #         yset = set(neededRole)
            #         roleDesc[:] = [x for x in roleDesc if x not in yset]
            #         if currentLen-len(roleDesc) >= 2:
            #             print(searchRecruiters[role].text)
            
            currentPage += 1
    except Exception as e:
        print(e)
        browser.quit()
    browser.quit()
    break
