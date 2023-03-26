from django.shortcuts import render


def get_driver():
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = Chrome(executable_path='D:\jupyter\stockforecast\news\chromedriver.exe', options=chrome_options)
    return driver

# Create your views here.
def index(request):
    return render(request,'index.html')

def news(request):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    import time
    
    driver = get_driver()
    
    try:
        driver.get('https://merolagani.com/NewsList.aspx/')

        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-block"))).click()
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_divData > .btn-block"))).click()
        time.sleep(2)


    except:
        error = "An error occurred. Please try again later."
        data = {
            'news': None
        }
        return render(request, 'news.html', data)

    # button.click()

    img = driver.find_elements(By.CSS_SELECTOR, '.media-wrap > a > img')
    # if(len(img)!=16):
    #     get_news_healines()
    img_data = []
    for i in img:
        # print(i.get_attribute('src'))
        img_data.append(i.get_attribute('src'))

    hrefs = driver.find_elements(By.CSS_SELECTOR, '.media-wrap > a')
    single_news_href_data = []
    for i in hrefs:
        # print(i.get_attribute('href'))
        single_news_href_data.append(i.get_attribute('href'))


    # code to read data from HTML
    news_link = driver.find_elements(By.CLASS_NAME, 'media-body')
    news_titledate_data = []
    for i in news_link:
        # print(i.text)
        news_titledate_data.append(i.text.replace("\n", "<br>"))


    # print(len(news_link))
    # print(len(img))
    # print(len(hrefs))
    news_data = []
    for i in range(len(news_titledate_data)):
        news_data.append({'title': news_titledate_data[i], 'link': single_news_href_data[i], 'image':img_data[i]})

    # print(len(news_titledate_data), len(single_news_href_data), len(img_data))


    # driver.quit()

    # with open('news/Headlines.txt', 'w', encoding="utf-8") as myfile:
    #     count = 1
    #     for i in news:
    #         myfile.write(f"{count}:\nTitle\n{i['title']}\nLink\n{i['link']}\nImage\n{i['image']}\n")
    #         count +=1

    # myfile.close()
    print(len(news_data))
    # if(len(news_data)< 16):
    #     driver.quit()
    #     news(request)
        
    data = {
        'news':news_data,
    }

    return render(request, 'news.html', data)



def single_news(request, link):
    return render(request, 'single_news.html')
    # news,driver = get_news_healines()
    # print(news[0]['link'])
    # driver.get(news[0]['link'])
    # content = driver.find_elements(By.CSS_SELECTOR, '.media-content')

    # for i in content:
    #     print(i.text)

    # driver.quit()

