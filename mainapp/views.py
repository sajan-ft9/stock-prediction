from django.shortcuts import render
from .models import News
import csv
from django.conf import settings
import statistics
import plotly.graph_objs as go
from plotly.offline import plot
from .forms import CSVUploadForm


def pred_show(request):
    return render(request,'predict.html')

def predict(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import mean_squared_error, r2_score
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense

        csv_file = request.FILES['csv_file']

        # Load the data from the CSV file
        data = pd.read_csv(csv_file)

        # Remove the 'Symbol' attribute
        data = data.drop('Symbol', axis=1)

        # Convert 'Date' column to datetime format
        data['Date'] = pd.to_datetime(data['Date'])

        # Preprocess the data
        X = data.drop(['Close', 'Date'], axis=1)
        y = data['Close']

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Reshape the input data for LSTM
        X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
        X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))

        # Build the LSTM model
        model = Sequential()
        model.add(LSTM(50, activation='relu', input_shape=(X_train_lstm.shape[1], X_train_lstm.shape[2])))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')

        # Train the LSTM model
        model.fit(X_train_lstm, y_train, epochs=50, batch_size=32, verbose=0)

        model.save('lstm_model.h5')

        # Ask the user for a date to predict the close price
        user_date = input("Enter the date (in the format YYYY-MM-DD) for which you want to predict the close price: ")

        # Convert the user date to datetime
        user_date = pd.to_datetime(user_date)

        # Find the row index corresponding to the user date
        user_date_index = data[data['Date'] == user_date].index[0]

        # Get the attributes for the user date
        user_data = data.drop(['Close', 'Date'], axis=1).loc[user_date_index].values.reshape(1, -1)

        # Scale the user data
        user_data_scaled = scaler.transform(user_data)

        # Reshape the user data for LSTM
        user_data_lstm = user_data_scaled.reshape((user_data_scaled.shape[0], 1, user_data_scaled.shape[1]))

        # Predict the close price for the user date
        predicted_close_price = model.predict(user_data_lstm)

        print("Predicted Close Price:", predicted_close_price[0][0])

        # Predict on the test set
        y_pred_lstm = model.predict(X_test_lstm)

        # Reshape y_pred_lstm
        y_pred_lstm = y_pred_lstm.reshape((y_pred_lstm.shape[0],))

        # Inverse scale the predictions
        y_pred_lstm = scaler.inverse_transform(X_test_scaled)[:, 0]

        # Calculate RMSE
        rmse_lstm = np.sqrt(mean_squared_error(y_test, y_pred_lstm))
        print("Root Mean Squared Error (RMSE):", rmse_lstm)

        # Calculate MSE
        mse_lstm = mean_squared_error(y_test, y_pred_lstm)
        print("Mean Squared Error (MSE):", mse_lstm)

        # Calculate R2 score
        r2_lstm = r2_score(y_test, y_pred_lstm)
        print("R2 Score:", r2_lstm)

        data = {
            'close_price': predicted_close_price,
            'rmse': rmse_lstm,
            'mse': mse_lstm,
            'r2': r2_lstm
        }
    return render(request, 'done.html', data)




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
