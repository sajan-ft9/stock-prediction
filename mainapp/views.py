from django.shortcuts import render
from .models import News

def get_driver():
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = Chrome(executable_path='D:\jupyter\stockforecast\chromedriver.exe', options=chrome_options)
    return driver

# Create your views here.
def index(request):
    title = News.objects.values_list('title')
    data = {
        'title': title
    }
    return render(request,'index.html', data)

def news(request):

    import time
    ts = time.time()
    try:
        db_exp_time = News.objects.values('expiry').latest('id')
        if (ts < db_exp_time['expiry']):
            db_data = News.objects.all().order_by('-id').values()
            send_news = {
                'news':db_data
            }
            return render(request, 'news.html', send_news)
            
        else:    


            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait
            
            driver = get_driver()
            
            try:
                driver.get('https://merolagani.com/NewsList.aspx/')

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_divData > .btn-block"))).click()
                time.sleep(2)


            except:
                data = {
                    'news': None
                }
                driver.quit()
                return render(request, 'news.html', data)

            # gets image src
            img = driver.find_elements(By.CSS_SELECTOR, '.media-wrap > a > img')
            
            img_data = []
            for i in img:
                img_data.append(i.get_attribute('src'))

            # get single news href
            hrefs = driver.find_elements(By.CSS_SELECTOR, '.media-wrap > a')
            single_news_href_data = []
            for i in hrefs:
                single_news_href_data.append(i.get_attribute('href'))


            # code to read news data from HTML
            news_link = driver.find_elements(By.CLASS_NAME, 'media-body')
            news_titledate_data = []
            for i in news_link:
                news_titledate_data.append(i.text.replace("\n", "<br>"))


            news_data = []
            for i in range(len(news_titledate_data)):
                news_data.append({'title': news_titledate_data[i], 'link': single_news_href_data[i], 'image':img_data[i]})

                
            # data = {
            #     'news':news_data,
            # }
            driver.quit()

            if(len(news_data) == 16):
                expiry_time = ts + 600
                News.objects.all().delete()
                for i in news_data:
                    
                    add_news = News(title=i['title'], image=i['image'], link = i['link'],expiry=expiry_time)
                    add_news.save()
                

                db_data = News.objects.all().order_by('-id').values()
                data = {
                    'news': db_data
                }
                
                return render(request, 'news.html', data)
            else:
                data = {
                    'news': None
                }
                return render(request, 'news.html', data)

    except:
        db_exp_time={'expiry': 100}
        

        if (ts < db_exp_time['expiry']):
            db_data = News.objects.all().order_by('-id').values()
            send_news = {
                'news':db_data
            }
            return render(request, 'news.html', send_news)
            
        else:    


            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait
            
            driver = get_driver()
            
            try:
                driver.get('https://merolagani.com/NewsList.aspx/')

                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_divData > .btn-block"))).click()
                time.sleep(2)


            except:
                data = {
                    'news': None
                }
                driver.quit()
                return render(request, 'news.html', data)

            # gets image src
            img = driver.find_elements(By.CSS_SELECTOR, '.media-wrap > a > img')
            
            img_data = []
            for i in img:
                img_data.append(i.get_attribute('src'))

            # get single news href
            hrefs = driver.find_elements(By.CSS_SELECTOR, '.media-wrap > a')
            single_news_href_data = []
            for i in hrefs:
                single_news_href_data.append(i.get_attribute('href'))


            # code to read news data from HTML
            news_link = driver.find_elements(By.CLASS_NAME, 'media-body')
            news_titledate_data = []
            for i in news_link:
                news_titledate_data.append(i.text.replace("\n", "<br>"))


            news_data = []
            for i in range(len(news_titledate_data)):
                news_data.append({'title': news_titledate_data[i], 'link': single_news_href_data[i], 'image':img_data[i]})

                
            # data = {
            #     'news':news_data,
            # }
            driver.quit()

            if(len(news_data) == 16):
                expiry_time = ts + 600
                News.objects.all().delete()
                for i in news_data:
                    add_news = News(title=i['title'], image=i['image'], link = i['link'],expiry=expiry_time)
                    add_news.save()
                
                db_data = News.objects.all().order_by('-id').values()
                data = {
                    'news': db_data
                }
                return render(request, 'news.html', data)
            else:
                data = {
                    'news': None
                }
                return render(request, 'news.html', data)


def single_news(request, id):
    from selenium.webdriver.common.by import By

    driver = get_driver()
    db_data = News.objects.values('link').get(id=id)
    link = db_data['link']
    driver.get(link)

    content = driver.find_elements(By.CSS_SELECTOR, '.media-content')

    news_data = []

    for i in content:
        print(i.text)
        news_data.append(i.text.replace("\n", "<br>"))

    data = {
        'news': news_data 
    }
    driver.quit()
    return render(request, 'single_news.html', data)


def about(request):
    import time
    ts = time.time()

    # expiry_time = News.objects.values('id','expiry').latest('id')
    # link_db = News.objects.values_list('link')
    # if News.objects.filter(link="")
        # print("NIce")
    # print(link_db)
    
    return render(request, 'about.html')