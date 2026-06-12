import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    BatchNormalization,
    Dropout,
    Flatten,
    Dense
)

from src.preprocess import (
    preprocess_audio
)

def build_model():
    model_2 = Sequential()

    model_2.add(Conv2D(32, (3,3),activation='relu', padding='same', input_shape=(128, 32, 1)))
    model_2.add(BatchNormalization())
    model_2.add(MaxPooling2D(2,2))

    model_2.add(Conv2D(64, (3,3),activation='relu', padding='same'))
    model_2.add(BatchNormalization())
    model_2.add(MaxPooling2D(2,2))

    model_2.add(Conv2D(128, (3,3),activation='relu', padding='same'))
    model_2.add(BatchNormalization())
    model_2.add(MaxPooling2D(2,2))

    model_2.add(Conv2D(256, (3,3),activation='relu', padding='same'))
    model_2.add(BatchNormalization())
    model_2.add(MaxPooling2D(2,2))

    model_2.add(Flatten())

    model_2.add(Dense(128, activation='relu'))
    model_2.add(Dropout(0.4))

    model_2.add(Dense(64, activation='relu'))
    model_2.add(Dropout(0.4))

    model_2.add(Dense(1, activation='sigmoid'))

    return model_2


model = build_model()

model.load_weights(
    "models\weights_best_2.weights.h5"
)

def predict_audio(file_path):

    X = preprocess_audio(
        file_path
    )

    probabilities = model.predict(
        X,
        verbose=0
    )

    average_probability = np.mean(
        probabilities
    )

    prediction = (
        "FAKE"
        if average_probability > 0.5
        else "REAL"
    )

    confidence = (
        average_probability
        if prediction == "FAKE"
        else 1 - average_probability
    )

    return (
        prediction,
        confidence
    )