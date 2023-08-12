def bilstm_model(company):

    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
    import matplotlib.pyplot as plt



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
    model.add(Bidirectional(LSTM(units=100, return_sequences=True), input_shape=(time_steps, 1)))
    model.add(Dropout(0.3))
    model.add(Bidirectional(LSTM(units=100, return_sequences=True)))
    model.add(Dropout(0.3))
    model.add(Bidirectional(LSTM(units=100)))
    model.add(Dense(units=7))  # Output layer with 7 units for predicting 7 days ahead
    model.summary()

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=32)

    loss = model.history.history['loss']
    plt.plot(loss)

    # Extract the training and validation loss from the history
    train_loss = model.history.history['loss']
    val_loss = model.history.history['val_loss']

    # Plot the training and validation loss
    plt.plot(train_loss, label='Training Loss')
    plt.plot(val_loss, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training and Validation Loss')
    plt.show()

    train_predict = model.predict(X_train)
    test_predict = model.predict(X_test)

    train_predict = scaler.inverse_transform(train_predict)
    test_predict = scaler.inverse_transform(test_predict)
    y_test = scaler.inverse_transform(y_test)
    y_train = scaler.inverse_transform(y_train)


    y_train_one_day = y_train[:, 0]
    train_predict_one_day = train_predict[:, 0]

    plt.plot(y_train_one_day, label='True Values')
    plt.plot(train_predict_one_day, label='Predictions')
    plt.legend()
    plt.show()

    y_test_one_day = y_test[:, 0]
    test_predict_one_day = test_predict[:, 0]

    plt.plot(y_test_one_day, label='True Values')
    plt.plot(test_predict_one_day, label='Predictions')
    plt.legend()
    plt.show()


    from sklearn.metrics import mean_absolute_error
    from sklearn.metrics import mean_squared_error,r2_score

    # Calculate RMSE and R2 for training data
    train_rmse = np.sqrt(mean_squared_error(y_train, train_predict))
    train_r2 = r2_score(y_train, train_predict)

    print("Training RMSE:", train_rmse)
    print("Training R2:", train_r2)

    # Calculate RMSE and R2 for testing data
    test_rmse = np.sqrt(mean_squared_error(y_test, test_predict))
    test_r2 = r2_score(y_test, test_predict)
    test_mae = mean_absolute_error(y_test, test_predict)
    print("Testing MAE:", test_mae)
    print("Testing RMSE:", test_rmse)
    print("Testing R2:", test_r2)


    last_week_data = scaled_data[-time_steps:, :]
    last_week_data = np.reshape(last_week_data, (1, time_steps, 1))
    predictions = model.predict(last_week_data)
    predictions = scaler.inverse_transform(predictions)
    predicted_close_prices = predictions[0]

    last_date = df['Date'].iloc[-1]
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(days=1), periods=7, freq='D')
    df_predictions = pd.DataFrame({'close_price': predicted_close_prices.flatten(), 'date': forecast_dates})

    print(df_predictions)

    # model.save(company.name.replace('.csv', 'bilstm.h5'))

    return df_predictions,train_rmse,test_rmse, train_r2, test_r2