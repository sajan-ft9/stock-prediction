def svm_model(company):
    import pandas as pd
    from sklearn.svm import SVR
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
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

    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create an SVR model
    svr = SVR()

    # Fit the model
    svr.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = svr.predict(X_test)


    # Calculate RMSE, MAE, and R2 for training set
    train_rmse = np.sqrt(mean_squared_error(y_train, svr.predict(X_train)))
    train_mae = mean_absolute_error(y_train, svr.predict(X_train))
    train_r2 = r2_score(y_train, svr.predict(X_train))

    # Calculate RMSE, MAE, and R2 for test set
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    test_mae = mean_absolute_error(y_test, y_pred)
    test_r2 = r2_score(y_test, y_pred)

    # Print evaluation metrics for training set
    print("Training RMSE:", train_rmse)
    print("Training MAE:", train_mae)
    print("Training R2:", train_r2)

    # Print evaluation metrics for test set
    print("Test RMSE:", test_rmse)
    print("Test MAE:", test_mae)
    print("Test R2:", test_r2)

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


    # import joblib
    # joblib.dump(svr, company.name.replace('.csv', 'svm.pkl'))


    return df_predictions,train_rmse, test_rmse, train_r2, test_r2
