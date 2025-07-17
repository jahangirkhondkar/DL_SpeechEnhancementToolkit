# A Comparative Evaluation of Deep Learning Models for Speech Enhancement in Real-world Noisy Environments**
This is the pre-print version [https://arxiv.org/abs/2506.15000](https://arxiv.org/abs/2506.15000)
# Abstract:
Speech enhancement, particularly denoising, is vital in improving the intelligibility and quality of speech signals for real-world applications, especially in noisy environments. While prior research has introduced various deep learning models for this purpose, many struggle to balance noise suppression, perceptual quality, and speaker-specific feature preservation, leaving a critical research gap in their comparative performance evaluation. This study benchmarks three state-of-the-art models—Wave-U-Net, CMGAN, and U-Net—on diverse datasets such as SpEAR, VPQAD, and Clarkson datasets. These models were chosen due to their relevance in the literature and code accessibility. The evaluation reveals that U-Net achieves high noise suppression with SNR improvements of +71.96\% on SpEAR, +64.83\% on VPQAD, and +364.2\% on the Clarkson dataset. CMGAN outperforms in perceptual quality, attaining the highest PESQ scores of 4.04 on SpEAR and 1.46 on VPQAD, making it well-suited for applications prioritizing natural and intelligible speech. Wave-U-Net balances these attributes with improvements in speaker-specific feature retention, evidenced by VeriSpeak score gains of +10.84\% on SpEAR and +27.38\% on VPQAD. This research indicates how advanced methods can optimize trade-offs between noise suppression, perceptual quality, and speaker recognition. The findings may contribute to advancing voice biometrics, forensic audio analysis, telecommunication, and speaker verification in challenging acoustic conditions.

# Result

1. The waveform comparison of a common subject across all three models is-

**Wave-U-Net**   <img width="900" height="600" alt="image" src="https://github.com/user-attachments/assets/e48f27b3-19cb-4529-a501-8f4a46989258" />

**CMGAN**        <img width="900" height="600" alt="image" src="https://github.com/user-attachments/assets/99ad39bc-01f1-4504-adb0-78c657ed8cd5" />

**U-Net**        <img width="900" height="600" alt="image" src="https://github.com/user-attachments/assets/decef45e-b48c-41e1-9d7e-b352e7171a98" />


# Contacts
Please contact _mkhondka@charlotte.edu_ or open an issue for any questions or suggestions.


# Acknowledgments

**Original Source for the Wave-U-Net:**
https://github.com/f90/Wave-U-Net

**Original Source for the CMGAN:**
https://github.com/ruizhecao96/CMGAN

**Original Source for the U-Net**
https://github.com/vbelz/Speech-enhancement

