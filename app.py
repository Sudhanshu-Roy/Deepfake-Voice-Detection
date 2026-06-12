import streamlit as st
import tempfile

from src.predict import predict_audio

st.set_page_config(
    page_title="Deepfake Voice Detector",
    layout="centered"
)

st.title("Deepfake Voice Detector")

st.write(
    "Upload a WAV audio file and the model will determine whether it is REAL or FAKE."
)

uploaded_file = st.file_uploader(
    "Choose an audio file",
    type=["wav"]
)

if uploaded_file is not None:

    st.audio(uploaded_file)

    if st.button("Predict"):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as tmp_file:

            tmp_file.write(
                uploaded_file.read()
            )

            temp_path = tmp_file.name

        prediction, confidence = predict_audio(
            temp_path
        )

        st.subheader("Prediction")

        st.success(
            f"{prediction}"
        )

        st.metric(
            "Confidence",
            f"{confidence*100:.2f}%"
        )