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
        chrome_options.add_experimental_option("prefs", {
            "download.prompt_for_download": True,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        driver = Chrome(options=chrome_options)
        try:

            driver.get('https://nepsealpha.com/nepse-data')

            time.sleep(30)


            select_click = driver.find_element(By.CSS_SELECTOR, '#vue_app_content > div.page.page_margin_top > div > div > div > form > div > div > div:nth-child(4) > span > span.selection > span')
            select_click.click()

            select_input = driver.find_element(By.CSS_SELECTOR, 'body > span > span > span.select2-search.select2-search--dropdown > input')
            select_input.send_keys(company)
            select_input.send_keys(Keys.ENTER)

            start_date = driver.find_element(By.CSS_SELECTOR, '#vue_app_content > div.page.page_margin_top > div > div > div > form > div > div > div:nth-child(2) > input')
            start_date.send_keys("10/10/2013")

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
            
        except:
             
            data ={
                'error': 1
            }
            
            return render(request,'data.html', data)
            

        return render(request,'data.html')





def predict(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        model = request.POST.get('model')
        print(model)
        if(model == 'LSTM'):
            from .lstm2 import lstm_model
            csv_file = request.FILES['csv_file']
            result = lstm_model(csv_file)
            result_dict = {
                'prediction' : result[0].to_dict(),
                'train_rmse' : result[1],
                'test_rmse' : result[2],
                'train_r2' : result[3],
                'test_r2' : result[4],
            }
        
        elif(model == 'BLSTM'):
            from .bilstm2 import bilstm_model
            csv_file = request.FILES['csv_file']
            result = bilstm_model(csv_file)
            result_dict = {
                'prediction' : result[0].to_dict(),
                'train_rmse' : result[1],
                'test_rmse' : result[2],
                'train_r2' : result[3],
                'test_r2' : result[4],
            }
        
        elif(model == 'SVM'):
            from .svm import svm_model
            csv_file = request.FILES['csv_file']
            result = svm_model(csv_file)
            result_dict = {
                'prediction' : result[0].to_dict(),
                'train_rmse' : result[1],
                'test_rmse' : result[2],
                'train_r2' : result[3],
                'test_r2' : result[4],
            }


        return JsonResponse({'data': result_dict})
    
    return render(request, 'predict.html')
    


def lstm_saved(company):
    import pandas as pd
    import os
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import load_model
    import numpy as np
        
    if(company == 0):
        model_path = os.path.join(os.path.dirname(__file__), 'akpllstm.h5')
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'akpl.csv'))
        
    if(company == 1):
        model_path = os.path.join(os.path.dirname(__file__), 'ntclstm.h5')
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'ntc.csv'))
    if(company == 2):
        model_path = os.path.join(os.path.dirname(__file__), 'akplbilstm.h5')
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'akpl.csv'))
    if(company == 3):
        model_path = os.path.join(os.path.dirname(__file__), 'ntcbilstm.h5')
        df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'ntc.csv'))

     # Convert the Date column to a datetime object
    df['Date'] = pd.to_datetime(df['Date'])

    # Sort the dataframe by date
    df = df.sort_values('Date')

    # Convert '--' to 0 in the 'Percent Change' column
    df['Percent Change'] = df['Percent Change'].replace('--', 0)

    # Convert columns to float
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Percent Change'] = df['Percent Change'].astype(float)

    # Extract the 'Close' column for prediction
    data = df['Close'].values.reshape(-1, 1)



    # Scale the data using Min-Max Scaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)


    saved_model = load_model(model_path)

    last_week_data = scaled_data[-7:, :]
    last_week_data = np.reshape(last_week_data, (1, 7, 1))
    predictions = saved_model.predict(last_week_data)
    predictions = scaler.inverse_transform(predictions)
    predicted_close_prices = predictions[0]

    last_date = df['Date'].iloc[-1]
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(days=1), periods=7, freq='D')
    df_predictions = pd.DataFrame({'close_price': predicted_close_prices.flatten(), 'date': forecast_dates})
    print(df_predictions)
    return df_predictions
    


def saved_predict(request):
    if request.method == 'POST':
        
        model = request.POST.get('model')
        company = request.POST.get('company')
        print(model)
        print(company)

        if(model == 'LSTM'):
            if company == '0':
                result = lstm_saved(0)
                result_dict = result.to_dict()

            elif company == '1':
                result = lstm_saved(1)
                result_dict = result.to_dict()
        
        elif(model == 'BLSTM'):
            if company == '0':
                result = lstm_saved(2)
                result_dict = result.to_dict()
            elif company == '1':
                result = lstm_saved(3)
                result_dict = result.to_dict()


        return JsonResponse({'data':result_dict})
    
    return render(request, 'saved_predict.html')
    



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

    driver = Chrome(options=chrome_options)
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
