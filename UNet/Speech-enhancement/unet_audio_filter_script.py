import argparse
import os
import numpy as np
import librosa
import tensorflow as tf
import soundfile as sf
from model_unet import unet
from data_tools import audio_to_magnitude_db_and_phase, magnitude_db_and_phase_to_audio, scaled_in, inv_scaled_ou

def resize_spectrogram(spectrogram, target_shape):
    """Resize the spectrogram to match the target shape by cropping or padding."""
    current_shape = spectrogram.shape

    # Pad or crop along both dimensions to match the target shape
    if current_shape[0] < target_shape[0]:
        pad_height = target_shape[0] - current_shape[0]
        pad_top = pad_height // 2
        pad_bottom = pad_height - pad_top
        spectrogram = np.pad(spectrogram, ((pad_top, pad_bottom), (0, 0)), mode='constant')
    elif current_shape[0] > target_shape[0]:
        crop_start = (current_shape[0] - target_shape[0]) // 2
        spectrogram = spectrogram[crop_start:crop_start + target_shape[0], :]

    if current_shape[1] < target_shape[1]:
        pad_width = target_shape[1] - current_shape[1]
        pad_left = pad_width // 2
        pad_right = pad_width - pad_left
        spectrogram = np.pad(spectrogram, ((0, 0), (pad_left, pad_right)), mode='constant')
    elif current_shape[1] > target_shape[1]:
        crop_start = (current_shape[1] - target_shape[1]) // 2
        spectrogram = spectrogram[:, crop_start:crop_start + target_shape[1]]

    return spectrogram

def filter_audio(model, audio_path, output_path, sample_rate=16000, n_fft=255, hop_length_fft=63):
    """Filter a given noisy audio file using the provided model."""
    # Load the noisy audio
    noisy_audio, sr = librosa.load(audio_path, sr=sample_rate)
    assert sr == sample_rate, f"Expected sampling rate of {sample_rate}, but got {sr}"

    # Convert audio to spectrogram (magnitude and phase)
    magnitude_db, phase = audio_to_magnitude_db_and_phase(n_fft, hop_length_fft, noisy_audio)
    
    # Resize the spectrogram to match the model's expected input shape
    target_shape = (128, 128)
    magnitude_db_resized = resize_spectrogram(magnitude_db, target_shape)

    # Scale input to match the model's training distribution
    X_in = scaled_in(magnitude_db_resized)
    X_in = X_in.reshape(1, X_in.shape[0], X_in.shape[1], 1)  # Add batch and channel dimensions

    # Predict the denoised spectrogram using the model
    X_pred = model.predict(X_in)
    X_pred = np.squeeze(X_pred)  # Remove batch dimension

    # Inverse scaling to get the original distribution of the spectrogram
    X_denoised_db = inv_scaled_ou(X_pred)
    
    # Reconstruct the audio from the denoised spectrogram and original phase (no resizing of phase)
    denoised_audio = magnitude_db_and_phase_to_audio(len(noisy_audio), hop_length_fft, X_denoised_db, phase)

    # Save the filtered audio
    sf.write(output_path, denoised_audio, sample_rate)

def main(args):
    # Load the model
    model = unet()
    model.load_weights(args.model_path)

    # Prepare output directory
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Filter all audio files in the input directory
    for file_name in os.listdir(args.input_dir):
        if file_name.endswith('.wav'):
            input_audio = os.path.join(args.input_dir, file_name)
            output_audio = os.path.join(args.output_dir, f"filtered_{file_name}")
            filter_audio(model, input_audio, output_audio, sample_rate=args.sample_rate, n_fft=args.n_fft, hop_length_fft=args.hop_length_fft)
            print(f"Filtered audio saved to {output_audio}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, required=True, help='Path to the trained model weights')
    parser.add_argument('--input_dir', type=str, required=True, help='Path to the input noisy audio directory')
    parser.add_argument('--output_dir', type=str, help='Directory where filtered audio will be saved')
    parser.add_argument('--sample_rate', type=int, default=16000, help='Sample rate of audio files')
    parser.add_argument('--n_fft', type=int, default=255, help='FFT size used for spectrogram')
    parser.add_argument('--hop_length_fft', type=int, default=63, help='Hop length for FFT')
    args = parser.parse_args()

    # Set default input and output directories based on user-provided location
    if not args.output_dir:
        if args.input_dir == '/media/lab2208/New Volume/Organized Voice data HDD/VPQAD_Cafeteria_raw_TD/noisy':
            args.output_dir = '/media/lab2208/New Volume/Organized Voice data HDD/VPQAD_Cafeteria_raw_TD/filtered'
        else:
            args.output_dir = os.path.join(os.path.dirname(args.input_dir), 'filtered')

    main(args)

