from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--headless")

driver = Chrome(executable_path='D:\jupyter\stockforecast\news\chromedriver.exe', options=chrome_options)

driver.get('https://nepsealpha.com/all-news?cid=1')

# code to read data from HTML
news_link = driver.find_elements(By.CSS_SELECTOR, 'h2 > a')
news_href = []
for i in news_link:
    news_href.append(i.get_attribute('href'))


data = []

print("xxxxxxxxxxxxxxxxxx")
i=0 
for each_news in news_href:

    driver.get(each_news)
    title = driver.find_element(By.CLASS_NAME, 'post_title').text 
    content = driver.find_element(By.CLASS_NAME, 'text').text

    data.append({'title':title, 'content':content})


driver.quit()

with open('news/News.txt', 'w', encoding="utf-8") as myfile:
    count = 1
    for i in data:
        myfile.write(f"{count}:\nTitle\n{i['title']}\nContent\n{i['content']}")
        count +=1

myfile.close()
