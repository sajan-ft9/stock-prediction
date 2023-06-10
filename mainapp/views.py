from django.shortcuts import render
from .models import News
import csv
from django.conf import settings
import statistics
import plotly.graph_objs as go
from plotly.offline import plot
from .forms import CSVUploadForm
from django.http import JsonResponse






def auto_download(request):
    if request.method == 'POST':
        company = request.POST.get('company')
        from selenium.webdriver import Chrome
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        import time
        from selenium.webdriver.common.keys import Keys


        chrome_options = Options()
        # chrome_options.add_experimental_option("prefs", {
        #     "download.prompt_for_download": True,
        #     "download.directory_upgrade": True,
        #     "safebrowsing.enabled": True
        # })

        driver = Chrome(executable_path='D:\jupyter\stockforecast\chromedriver.exe', options=chrome_options)

        driver.get('https://nepsealpha.com/nepse-data')



        select_click = driver.find_element(By.CSS_SELECTOR, '#vue_app_content > div.page.page_margin_top > div > div > div > form > div > div > div:nth-child(4) > span > span.selection > span')
        select_click.click()

        select_input = driver.find_element(By.CSS_SELECTOR, 'body > span > span > span.select2-search.select2-search--dropdown > input')
        select_input.send_keys(company)
        select_input.send_keys(Keys.ENTER)

        start_date = driver.find_element(By.CSS_SELECTOR, '#vue_app_content > div.page.page_margin_top > div > div > div > form > div > div > div:nth-child(2) > input')
        start_date.send_keys("07/01/2013")

        filter_button = driver.find_element(By.CSS_SELECTOR, '#vue_app_content > div.page.page_margin_top > div > div > div > form > div > div > div:nth-child(5) > button')
        filter_button.click()
        time.sleep(3)

        csv_button = driver.find_element(By.CSS_SELECTOR, '#result-table_wrapper > div.dt-buttons > button.dt-button.buttons-csv.buttons-html5.btn.btn-outline-secondary.btn-sm')
        csv_button.click()

        time.sleep(5)
        driver.quit()
        import os
        import subprocess

        # Get the user's download folder path
        download_folder = os.path.expanduser("~\\Downloads")

        # Open the download folder in Windows Explorer
        subprocess.Popen(f'explorer "{download_folder}"')

        return render(request,'data.html')





def predict(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        model = request.POST.get('model')
        print(model)
        if(model == 'LSTM'):
            from .lstm import lstm_model
            csv_file = request.FILES['csv_file']
            result = lstm_model(csv_file)
            result_dict = result.to_dict()
        
        elif(model == 'BLSTM'):
            from .bilstm import bilstm_model
            csv_file = request.FILES['csv_file']
            result = bilstm_model(csv_file)
            result_dict = result.to_dict()

        return JsonResponse({'data': result_dict})
    
    return render(request, 'predict.html')
    


def data_download(request):
    return render(request, 'data.html')








def visualize_csv_form(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            reader = csv.reader(csv_file.read().decode('utf-8').splitlines())
            header = next(reader)  # Skip the header row
            data = list(reader)

            # Extract column data
            dates = [row[1] for row in data]  # Assuming the date column is at index 1
            close_prices = [float(row[5]) for row in data]  # Assuming the close price column is at index 5

            # Calculate statistical data
            minimum = min(close_prices)
            maximum = max(close_prices)
            average = statistics.mean(close_prices)
            variance = statistics.variance(close_prices)
            median = statistics.median(close_prices)

            chart_data = go.Scatter(x=dates, y=close_prices, mode='lines', name='Close Prices')
            layout = go.Layout(title='Close Prices Over Time', xaxis=dict(title='Date'), yaxis=dict(title='Close Price'))
            fig = go.Figure(data=[chart_data], layout=layout)
            plot_div = plot(fig, output_type='div')

            return render(request, 'visualization.html', {'form': form, 'plot_div': plot_div, 'minimum': minimum, 'maximum': maximum, 'average': average, 'variance': variance, 'median': median})
    else:
        form = CSVUploadForm()

    return render(request, 'visualization.html', {'form': form})













def get_driver():
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = Chrome(executable_path='D:\jupyter\stockforecast\chromedriver.exe', options=chrome_options)
    return driver

# Create your views here.

def index(request):
    return render(request,'index.html')














def news(request):

    import time
    ts = time.time()
    try:
        db_exp_time = News.objects.values('expiry').latest('id')
        if (ts < db_exp_time['expiry']):
            db_data = News.objects.all().order_by('id').values()
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
                expiry_time = ts + 9000
                News.objects.all().delete()
                for i in news_data:
                    
                    add_news = News(title=i['title'], image=i['image'], link = i['link'],expiry=expiry_time)
                    add_news.save()
                

                db_data = News.objects.all().order_by('id').values()
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
            db_data = News.objects.all().order_by('id').values()
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
                expiry_time = ts + 9000
                News.objects.all().delete()
                for i in news_data:
                    add_news = News(title=i['title'], image=i['image'], link = i['link'],expiry=expiry_time)
                    add_news.save()
                
                db_data = News.objects.all().order_by('id').values()
                data = {
                    'news': db_data
                }
                return render(request, 'news.html', data)
            else:
                data = {
                    'news': None
                }
                return render(request, 'news.html', data)
