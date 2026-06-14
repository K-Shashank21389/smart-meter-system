from sklearn.linear_model import LinearRegression

def predict_next_reading(readings):

    x = [[i] for i in range(len(readings))]
    y = readings

    model = LinearRegression()
    model.fit(x, y)

    prediction = model.predict([[len(readings)]])

    return round(prediction[0], 2)