def lstm_model(company):

    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout

    # Read the CSV file
    df = pd.read_csv(company)

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


    # Define the training and testing data sizes
    train_size = int(len(scaled_data) * 0.8)
    test_size = len(scaled_data) - train_size

    # Split the data into training and testing sets
    train_data = scaled_data[:train_size, :]
    test_data = scaled_data[train_size:, :]


    def prepare_data(data, time_steps):
        X, y = [], []
        for i in range(len(data) - time_steps - 7):
            X.append(data[i:i + time_steps, 0])
            y.append(data[i + time_steps:i + time_steps + 7, 0])
        return np.array(X), np.array(y)

    # Define the number of time steps
    time_steps = 7

    # Prepare the training data
    X_train, y_train = prepare_data(train_data, time_steps)

    # Prepare the testing data
    X_test, y_test = prepare_data(test_data, time_steps)

    # Reshape the data for LSTM (samples, time_steps, features)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))


    model = Sequential()
    model.add(LSTM(units=100, return_sequences=True, input_shape=(time_steps, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=100, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=100))
    model.add(Dense(units=7))  # Output layer with 7 units for predicting 7 days ahead
    model.compile(optimizer='adam', loss='mean_squared_error')


    model.fit(X_train, y_train, epochs=100, batch_size=32)


    last_week_data = scaled_data[-time_steps:, :]
    last_week_data = np.reshape(last_week_data, (1, time_steps, 1))
    predictions = model.predict(last_week_data)
    predictions = scaler.inverse_transform(predictions)
    predicted_close_prices = predictions[0]


    last_date = df['Date'].iloc[-1]
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(days=1), periods=7, freq='D')
    df_predictions = pd.DataFrame({'close_price': predicted_close_prices.flatten(), 'date': forecast_dates})


    print(df_predictions)
    return df_predictions
