def svm_model(company):
    import pandas as pd
    from sklearn.svm import SVR
    import numpy as np

    # Read csv file
    df = pd.read_csv(company)

    # Convert the Date column to a datetime object
    df['Date'] = pd.to_datetime(df['Date'])

    # Sort the dataframe by date
    df = df.sort_values('Date')

    # Convert '--' to 0 in the 'Percent Change' column
    df['Percent Change'] = df['Percent Change'].replace('--', 0)

    # Convert 'Percent Change' column to float
    df['Percent Change'] = df['Percent Change'].astype(float)

    # Create features and target variables
    X = df[['Open', 'High', 'Low', 'Percent Change']]
    y = df['Close']

    # Create an SVR model
    svr = SVR()

    # Fit the model
    svr.fit(X, y)

    # Forecast close prices for the upcoming week
    last_day = df['Date'].max()
    forecast_dates = pd.date_range(start=last_day + pd.Timedelta(days=1), periods=7, freq='D')
    forecast_features = df[['Open', 'High', 'Low', 'Percent Change']].tail(1).values

    predictions = []
    for _ in range(7):
        prediction = svr.predict(forecast_features)[0]
        predictions.append(prediction)
        forecast_features = np.roll(forecast_features, -1, axis=0)
        forecast_features[-1] = [df['Open'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1], predictions[-1]]

    # Create a DataFrame for the predictions
    df_predictions = pd.DataFrame(predictions, columns=['close_price'])
    df_predictions['date'] = forecast_dates

    # Print the dataframe
    print(df_predictions)
    return df_predictions