import kagglehub

path = kagglehub.dataset_download(
    "birdy654/deep-voice-deepfake-voice-recognition"
)

print("Dataset downloaded to:")
print(path)