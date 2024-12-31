import argparse
import os
import torch
import torchaudio
import soundfile as sf
from models.generator import TSCNet
from utils import power_compress, power_uncompress
import torch.cuda.amp as amp

def enhance_audio(model, audio_path, output_path, n_fft=400, hop=100, segment_len=16000):
    """Enhance a given noisy audio file using the provided model."""
    # Load the noisy audio
    noisy, sr = torchaudio.load(audio_path)
    assert sr == 16000, "Sampling rate must be 16 kHz"
    
    # Split audio into smaller segments
    length = noisy.size(-1)
    segments = []
    for start in range(0, length, segment_len):
        end = min(start + segment_len, length)
        segments.append(noisy[:, start:end])
    
    enhanced_segments = []
    for segment in segments:
        # Move the segment to GPU
        segment = segment.cuda()
        
        # Normalization
        c = torch.sqrt(segment.size(-1) / torch.sum((segment**2.0), dim=-1))
        segment = torch.transpose(segment, 0, 1)
        segment = torch.transpose(segment * c, 0, 1)
        
        # Pad the segment if necessary
        seg_length = segment.size(-1)
        if seg_length < n_fft:
            padding_len = n_fft - seg_length
            segment = torch.nn.functional.pad(segment, (0, padding_len))
        
        # Generate STFT of the segment
        noisy_spec = torch.stft(segment, n_fft, hop, window=torch.hamming_window(n_fft).cuda(), onesided=True)
        noisy_spec = power_compress(noisy_spec).permute(0, 1, 3, 2)
        
        # Use mixed precision to save memory
        with amp.autocast():
            # Apply the model to get the enhanced segment
            est_real, est_imag = model(noisy_spec)
        
        est_real, est_imag = est_real.permute(0, 1, 3, 2), est_imag.permute(0, 1, 3, 2)
        est_spec_uncompress = power_uncompress(est_real, est_imag).squeeze(1)
        est_audio = torch.istft(est_spec_uncompress, n_fft, hop, window=torch.hamming_window(n_fft).cuda(), onesided=True)
        
        # Re-normalize and truncate to original length
        est_audio = est_audio / c
        est_audio = torch.flatten(est_audio)[:seg_length].detach().cpu().numpy()
        
        enhanced_segments.append(est_audio)
        
        # Free GPU memory
        del segment, noisy_spec, est_real, est_imag, est_spec_uncompress, est_audio
        torch.cuda.empty_cache()
    
    # Concatenate all enhanced segments
    enhanced_audio = torch.cat([torch.tensor(segment) for segment in enhanced_segments], dim=0).numpy()
    
    # Save the enhanced audio
    sf.write(output_path, enhanced_audio, sr)

def main(args):
    # Load the model
    model = TSCNet(num_channel=64, num_features=args.n_fft // 2 + 1).cuda()
    model.load_state_dict(torch.load(args.model_path))
    model.eval()

    # Prepare output directory
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Enhance all audio files in the input directory
    for file_name in os.listdir(args.input_dir):
        input_audio = os.path.join(args.input_dir, file_name)
        output_audio = os.path.join(args.output_dir, file_name)
        enhance_audio(model, input_audio, output_audio, n_fft=args.n_fft, hop=args.hop, segment_len=args.segment_len)
        print(f"Enhanced audio saved to {output_audio}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, required=True, help='Path to the trained model checkpoint')
    parser.add_argument('--input_dir', type=str, required=True, help='Path to the input noisy audio directory')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory where enhanced audio will be saved')
    parser.add_argument('--n_fft', type=int, default=400, help='FFT size')
    parser.add_argument('--hop', type=int, default=100, help='Hop length for STFT')
    parser.add_argument('--segment_len', type=int, default=16000, help='Length of each audio segment for processing')
    args = parser.parse_args()
    main(args)

