import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

if __name__ == '__main__':
    page_url = "https://www.govtrack.us/congress/members/current"

    driver = webdriver.Firefox()
    driver.get(page_url)
    time.sleep(2)
    htmlPage = driver.find_element(By.TAG_NAME, "html")
    anchor_container = htmlPage.find_element(By.CLASS_NAME, "results")
    anchor_list = anchor_container.find_elements(By.TAG_NAME, "a")
    link_list = []

    while len(anchor_list) <= 539:
        anchor_list = anchor_container.find_elements(By.TAG_NAME, "a")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        if len(anchor_list) == 539:
            break

    for a in anchor_list:
        data = {
            "link": a.get_attribute("href"),
            "image": "",
            "first_name": "",
            "last_name": "",
            "title": "",
            "state": "",
            "district": "",
            "party": ""
        }
        link_list.append(data)

    for data in link_list:
        driver.get(data["link"])
        time.sleep(2)
        html = driver.find_element(By.TAG_NAME, "html")

        header_div = html.find_element(By.CLASS_NAME, "h1-multiline")
        headerElements = header_div.find_elements(By.XPATH, '*')
        title_and_name = headerElements[0].text.split()
        district_string = headerElements[1].text.split()

        if len(title_and_name) < 4:
            data["first_name"] = title_and_name[1]
            data["last_name"] = title_and_name[2]
        else:
            data["first_name"] = title_and_name[1]
            data["last_name"] = title_and_name[2] + " " + title_and_name[3]

        if title_and_name[0].__contains__("Rep"):
            data["title"] = "Representative"
            if headerElements[1].text.__contains__("North") or headerElements[1].text.__contains__("South") or \
                    headerElements[1].text.__contains__("New"):
                state_and_district = district_string[-4:]
                data["district"] = state_and_district[2]
                data["state"] = (state_and_district[0] + " " + state_and_district[1])[:-2]
            else:
                state_and_district = district_string[-3:]
                data["district"] = state_and_district[1]
                data["state"] = state_and_district[0]
        else:
            data["title"] = "Senator"
            if headerElements[1].text.__contains__("North") or headerElements[1].text.__contains__("South") or \
                    headerElements[1].text.__contains__("New"):
                state_list = district_string[-4:]
                data["state"] = state_list[2] + " " + state_list[3]
            else:
                state_list = district_string[-3:]
                data["state"] = state_list[2]

        summary_div = html.find_element(By.ID, "track_panel_base")
        if summary_div.text.__contains__("Democrat"):
            data["party"] = "Democrat"
        else:
            data["party"] = "Republican"

        content_div = html.find_element(By.ID, "content")
        try:
            content_div.find_element(By.CLASS_NAME, "photo")
        except:
            print("")
            continue

        pic_div = content_div.find_element(By.CLASS_NAME, "photo")
        img = pic_div.find_element(By.TAG_NAME, "img")
        data["image"] = img.get_attribute("src")

    json_object = json.dumps(link_list, indent=4)

    # Writing to sample.json
    with open("sample.json", "w") as outfile:
        outfile.write(json_object)
    driver.close()
