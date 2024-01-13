import os
import subprocess
import requests
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.mouse_button import MouseButton
from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import argparse
import pandas as pd
import hashlib

class Colors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    ORANGE = "\033[33m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

# MLX API variables
MLX_BASE = "https://api.multilogin.com"
MLX_LAUNCHER = "https://launcher.mlx.yt:45001/api/v1"
LOCALHOST = "http://127.0.0.1"
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

list=[]

parser = argparse.ArgumentParser(description='Process data based on form input.')
parser.add_argument('--number', type=int, help='Number of keywords')
parser.add_argument('--keywords', type=str, help='Keywords separated by comma')
parser.add_argument('--email', type=str, help='your mlx email address')
parser.add_argument('--password', type=str, help='your mlx password, no md5 hash')
parser.add_argument('--profileid', type=str, help='your mlx profile')
parser.add_argument('--folderid', type=str, help='the folder your profile is in')
parser.add_argument('--browsertype', type=str, help='mimic or stealthfox')
parser.add_argument('--ostype', type=str, help='windows, mac or linux')

args = parser.parse_args()

number_of_keywords = args.number
keywords = args.keywords.split(',') if args.keywords else []
username = args.email
password = args.password
profile_id = args.profileid
folder_id = args.folderid
browsertype = args.browsertype
os_type = args.ostype

# Function to connect the agent
def connect_agent():

    try:

        if os_type == "windows":
            username = os.getlogin()
            agent_path = f'C:\\Users\\{username}\\AppData\\Local\\Multilogin X\\agent.exe'
            agent_connection = subprocess.run([agent_path])

            if agent_connection.returncode == 0:
                print("\n" + Colors.GREEN + "[MLX STATUS] " + Colors.RESET + "Agent connected!")
            else:
                print(f"Failed to connect agent. Error {agent_connection.returncode}")

        elif os_type == "mac":
            agent_connection = subprocess.Popen(['open', '/Applications/mlx.app/'])
            agent_connection.wait()  
            
            return_code = agent_connection.returncode
            if return_code == 0:
                print("Agent connected")
            else:
                print(f"Failed to connect agent. Error {return_code}")

        elif os_type == "linux":
            path = "/opt/mlx/agent.bin"
            subprocess.Popen(['nohup', path, '&'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    
    except Exception as e:
            print(f"Can't open agent: {e}")

# MLX Signin function to retrieve the toke
def signin() -> str:

    signin_endpoint = f'{MLX_BASE}/user/signin'
    
    payload = {
        'email': username,
        'password': hashlib.md5(password.encode()).hexdigest()
    }

    r = requests.post(url=signin_endpoint, json=payload)

    if(r.status_code !=200):
        print(f'\nError during login: {r.text}\n')
    else:
        response = r.json()['data']
        token = response['token']
        print("Got token. Token is: " + token)
        return token
    
# Start profile and instantiate remote webdriver functions
def start_profile() -> webdriver:

    if browsertype == 'stealthfox':

        try:
            
            start_profile_endpoint = f'{MLX_LAUNCHER}/profile/f/{folder_id}/p/{profile_id}/start?automation_type=selenium'
            r = requests.get(url=start_profile_endpoint, headers=HEADERS)
            response = r.json()

            if(response['status']['message']=="downloading of core started"):
                try:
                    print("Browser core is still downloading. Will wait for 20 seconds and try again.")
                    time.sleep(20)
                    start_profile_endpoint = f'{MLX_LAUNCHER}/profile/f/{folder_id}/p/{profile_id}/start?automation_type=selenium'
                    r = requests.get(url=start_profile_endpoint, headers=HEADERS)
                    response = r.json()
                    selenium_port = response.get('status').get('message')
                    print("Selenium port is: " + selenium_port + "\n")
                    driver = webdriver.Remote(command_executor=f'{LOCALHOST}:{selenium_port}', options=Options())
                    return driver
                except:
                    print("Something went wrong during after the retry.")

            elif(r.status_code !=200 and response['status']['message']!="downloading of core started"):
                print(f'\nError while starting profile: {r.text}\n')
            else:
                print(f'\nProfile {profile_id} started.\n')
                selenium_port = response.get('status').get('message')
                print("Selenium port is: " + selenium_port + "\n")
                driver = webdriver.Remote(command_executor=f'{LOCALHOST}:{selenium_port}', options=Options())
                return driver
        except:
            print("Something has happened during the launching and instantiating process. Check.")

    elif browsertype == 'mimic':

        try:
            
            start_profile_endpoint = f'{MLX_LAUNCHER}/profile/f/{folder_id}/p/{profile_id}/start?automation_type=selenium'
            r = requests.get(url=start_profile_endpoint, headers=HEADERS)
            response = r.json()

            if(response['status']['message']=="downloading of core started"):
                try:
                    print("Browser core is still downloading. Will wait for 20 seconds and try again.")
                    time.sleep(20)
                    start_profile_endpoint = f'{MLX_LAUNCHER}/profile/f/{folder_id}/p/{profile_id}/start?automation_type=selenium'
                    r = requests.get(url=start_profile_endpoint, headers=HEADERS)
                    response = r.json()
                    selenium_port = response.get('status').get('message')
                    print("Selenium port is: " + selenium_port + "\n")
                    driver = webdriver.Remote(command_executor=f'{LOCALHOST}:{selenium_port}', options=ChromiumOptions())
                    return driver
                except:
                    print("Something went wrong during after the retry.")

            elif(r.status_code !=200 and response['status']['message']!="downloading of core started"):
                print(f'\nError while starting profile: {r.text}\n')
            else:
                print(f'\nProfile {profile_id} started.\n')
                selenium_port = response.get('status').get('message')
                print("Selenium port is: " + selenium_port + "\n")
                driver = webdriver.Remote(command_executor=f'{LOCALHOST}:{selenium_port}', options=ChromiumOptions())
                return driver
        except:
            print("Something has happened during the launching and instantiating process. Check.")
    else:
        print("Couldn't check browser type.")

def stop_profile() -> None:
    r = requests.get(f'{MLX_LAUNCHER}/profile/stop/p/{profile_id}', headers=HEADERS)

    if(r.status_code != 200):
        print(f'\nError when trying to stop profile: {r.text}\n')
    else:
        print(f'\nProfile {profile_id} stopped.\n')

def automation():

    driver = start_profile()

    final_list=[]
    list2=[]
    list3=[]

    ###########################SCROLLING TEST FUNCTION###################################

    def check_div_presence2(): # This is done so it does not break the code if div is not present
        try:
            div_element = driver.find_element(By.CSS_SELECTOR, "span.RVQdVd")
            return True
        except NoSuchElementException as e:
            print(Colors.RED + "'More results' button is not present." + Colors.RESET)
            return False
        
        #########################SCRILLING TEST FUNCTION###############################

    def create_sheet():
        num_columns = 3
        columns=["Keyword", "Number of companies", "Company name"]
        data = [final_list[i:i+num_columns] for i in range(0, len(final_list), num_columns)]
        df = pd.DataFrame(data, columns=columns)
        print("DataFrame:")
        print(df)
        df.to_excel('list-output.xlsx', index=False)

    for keyword in keywords:    
        try:
            print(f"Looking for the keyword" + Colors.ORANGE + f" '{keyword}' " + Colors.RESET + "now. Please wait a few seconds...\n")
            driver.get(f'https://www.google.com/search?q={keyword}')

            #########################SCROLLING TEST################################

            for _ in range(10): # scrolling to retrieve more results (there are sponsored content more over)
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)
                            try:
                                if check_div_presence2():
                                    div_element = driver.find_element(By.CSS_SELECTOR, "span.RVQdVd")
                                    ActionChains(driver).move_to_element(div_element).click().perform()
                                    time.sleep(1)
                                else:
                                    print("Scrolling ok.")
                            except Exception as z:
                                print(f"Something off with the div_presence2: {z}")


            #########################SCROLLING TEST################################
                                
            # get all elements from parent div
            parent_div = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.Aozhyc.Va3FIb.TElO2c.OSrXXb")))
            # store target child spans
            for element in (parent_div):
                aimed_span = element.find_element(By.CSS_SELECTOR, "span.OSrXXb")
                list2.append(aimed_span.text)
            # now we will have a list (list2) of all spans (including the ones with empty values)
            for element in list2:
                # now we will filter out does spans in list2 that has any empty values, and store them in list3
                if element is not None and element.strip() != "":
                    #list3.append(keyword)
                    #list3.append(len(list2))
                    list3.append(element)

            # now we have a list (list3) of all spans that has any value on it
            for i, filtered_element in enumerate(list3, start=1): # go through all objects from list3 and give it an index number
                print(f"Company {i}: {filtered_element}") # print index number and list3 object
                final_list.append(keyword) # send keyword to the final list on position 0
                final_list.append(len(list3)) # send total of objects in list3 to the final list on position 1
                final_list.append(filtered_element) # send object to the final list on position 2

                #print(aimed_span.text)
        except Exception as e:
            print(f"Something went wrong during the automation process: {e}")
    create_sheet()
    driver.quit()
    stop_profile()

connect_agent()
token = signin()
HEADERS.update({"Authorization": f'Bearer {token}'})
automation()
