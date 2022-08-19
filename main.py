from sys import exit
import os
import random
import time
from selenium.webdriver.common.keys import Keys

from helpers.scraper import Scraper
from helpers.utility import formatted_time, data_countdown, countdown, execution_time
from helpers.files import read_csv, read_txt, write_to_csv, write_to_txt, read_contact_info
from helpers.numbers import formatted_number_with_comma, numbers_within_text, str_to_int

def search(searchLocation):
    searchInput = d.element_send_keys(searchLocation, '#search-box-input', clear_input=True)
    d.sleep(10, 15)
    lis = d.find_elements('ul[class^="HomepageDropdown"] li', loop_count=2)
    for li in lis:
        if searchLocation.lower() in li.text.lower():
            d.element_click(element=li)
            break
    d.sleep(7, 10)
    
def collect_property_links(page):
    d.sleep(6, 7)
    resultDiv = d.find_element('ul[class^="SearchPage__SearchResults"]', loop_count=5)
    properties = d.find_elements('li[class^="SearchPage__Result"]', ref_element=resultDiv)
    links = []
    for property in properties:
        a = d.find_element('a', ref_element=property, wait_element_time=1)
        href = a.get_attribute('href')
        links.append(href)
    print(f'Page: {page}, Length of data: {len(links)}')
    return links
        
def login():
    username = contact_info['loginEmail']
    password = contact_info['loginPassword']
    signInBtn = d.find_element('a[href="/auth/authenticate"]', loop_count=3)
    d.element_click(element=signInBtn)
    d.sleep(3, 4)
    usernameInput = d.element_send_keys(username, '#username', loop_count=3)
    passwordInput = d.element_send_keys(password, '#password')
    submitBtn = d.element_click('input.login__button')
    d.sleep(3, 4)
    return True

def contact_property(href):    
    d.go_to_page(href)
    d.sleep(3, 4)
    emailBtn = d.find_element('button[aria-label="Email Agent"]', loop_count=3)
    if emailBtn:
        d.element_click(element=emailBtn)
        d.sleep(3, 4)
        nameInput = d.find_element('#input-wrapper-name input')
        d.sleep(1.5, 2)
        if nameInput and nameInput.get_attribute('value').strip() != contact_info['name']:
            d.sleep(1, 1.2)
            try:
                d.element_send_keys(contact_info['name'], '#input-wrapper-name input')
            except:
                d.element_send_keys(contact_info['name'], '#input-wrapper-name input')
            d.sleep(0.5, 1)
            try:
                d.element_send_keys(contact_info['email'], '#input-wrapper-email input')
            except:
                d.element_send_keys(contact_info['email'], '#input-wrapper-email input')
            d.sleep(0.5, 1)
            try:
                d.element_send_keys(contact_info['message'], '#message')
            except:
                d.element_send_keys(contact_info['message'], '#message')
                
            d.element_click('input[displayname="Cash"]')
            saveReply = d.find_element('#saveReply')
            if saveReply:
                d.element_click(element=saveReply)
        
        d.sleep(1, 1.5)
        d.element_click('button[data-testid="submit-button"]')
        
        # Confirmation
        confirm = d.find_element('div[data-testid="alert-message"]', exit_on_missing_element=False, wait_element_time=10)
        if confirm and confirm.text == "Your enquiry has been sent":
            return True

    return False
    
def main():
    d.element_click('button[data-tracking="cc-accept"]', exit_on_missing_element=False)
    # Login things
    d.sleep(5, 6)
    try:    
        isLoggedIn = d.find_elements('button[data-testid="top-level-nav-item"]', loop_count=3)[3]
    except:
        isLoggedIn = login()
    
    d.sleep(6, 8)
    search(contact_info['searchLocation'])

    page = 1
    count = 0
    while True:
        links = collect_property_links(page)
        pagination_text = d.find_element('p[data-testid="pagination-results"]').text
        
        # visit links
        for href in links:
            if [href] in prev_data:
                continue
            isSuccess = contact_property(href)
            if isSuccess:
                count += 1
                data_countdown(f'{count} contact info filled')
                prev_data.append([href])
                write_to_csv(prev_data, file_name='filled_properties.csv')
            d.sleep(1, 2)
        
        #Pagination
        d.sleep(1, 2)
        last_result = numbers_within_text(pagination_text)
        if last_result[1] == last_result[2]:
            break    
        else:
            nextUrl = f'https://www.daft.ie/property-for-sale/cork-city?pageSize=20&from={page * 20}'
            d.go_to_page(nextUrl)
            page += 1
            d.sleep(7, 10)
    
    return count

if __name__ == "__main__":
    START_TIME = time.time()


    # Global variables
    contact_info = read_contact_info('contact_info.txt', '=')
    prev_data = read_csv('filled_properties.csv')
    
    url = 'https://www.daft.ie/'
    d = Scraper(url, exit_on_missing_element=False)
    d.print_executable_path()

    count = main()
    
    
    # Footer for reporting
    execution_time(START_TIME, f'{count} contact filled')

    # Finally Close the browser
    input('Press any key to exit the browser...')
    d.driver.quit()
