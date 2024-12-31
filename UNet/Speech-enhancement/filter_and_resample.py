import os
import numpy as np
import librosa
import librosa.display
import tensorflow as tf
import matplotlib.pyplot as plt

# Paths
checkpoint_path = "/home/lab2208/UNet/Speech-enhancement/weights/model_best.h5"
input_audio_dir = "/media/lab2208/New Volume/Organized Voice data HDD/Collection 6 to 17 Raw/Collection 6 Raw"
output_audio_dir = "/media/lab2208/New Volume/Organized Voice data HDD/UNet/Filtered"

os.makedirs(output_audio_dir, exist_ok=True)

# Load model
model = tf.keras.models.load_model(checkpoint_path)

# Function to preprocess audio into spectrogram
def preprocess_audio_to_spectrogram(audio, sr, target_shape=(128, 128)):
    mel_spectrogram = librosa.feature.melspectrogram(
        y=audio, sr=sr, n_fft=1024, hop_length=256, n_mels=target_shape[0]
    )
    log_mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)
    log_mel_spectrogram = log_mel_spectrogram[:target_shape[0], :target_shape[1]]
    return log_mel_spectrogram[..., np.newaxis]

# Process each audio file
for file_name in os.listdir(input_audio_dir):
    if file_name.endswith('.wav'):
        input_file_path = os.path.join(input_audio_dir, file_name)

        # Load and resample audio
        audio, sr = librosa.load(input_file_path, sr=16000)  # Resample to 16kHz
        spectrogram = preprocess_audio_to_spectrogram(audio, sr)

        # Add batch dimension for prediction
        spectrogram_input = np.expand_dims(spectrogram, axis=0)

        # Predict
        filtered_spectrogram = model.predict(spectrogram_input)
        filtered_spectrogram = np.squeeze(filtered_spectrogram)  # Remove batch dimension

        # Save filtered spectrogram back to audio
        reconstructed_audio = librosa.feature.inverse.mel_to_audio(
            librosa.db_to_power(filtered_spectrogram), sr=16000, hop_length=256
        )
        output_file_path = os.path.join(output_audio_dir, f"filtered_{file_name}")
        librosa.output.write_wav(output_file_path, reconstructed_audio, sr=16000)

print(f"Filtering completed. Files saved in {output_audio_dir}")

