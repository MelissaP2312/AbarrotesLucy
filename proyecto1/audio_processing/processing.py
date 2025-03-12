import torchaudio
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

def process_audio(file_path):
    # Cargar el modelo pre-entrenado de Wav2Vec2
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

    # Cargar el audio con torchaudio
    waveform, sample_rate = torchaudio.load(file_path)

    # Re-muestreo a la tasa de muestreo del modelo si es necesario
    target_sample_rate = 16000  # El modelo Wav2Vec2 espera un audio a 16kHz
    if sample_rate != target_sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        waveform = resampler(waveform)
    
    # Preprocesar el audio para la entrada del modelo
    inputs = processor(waveform, sampling_rate=target_sample_rate, return_tensors="pt", padding=True)

    # Realizar la inferencia para transcribir el audio
    with torch.no_grad():
        logits = model(input_values=inputs.input_values).logits

    # Obtener la predicción de las palabras (el modelo devuelve un logaritmo de probabilidades)
    predicted_ids = torch.argmax(logits, dim=-1)

    # Decodificar las predicciones de vuelta a texto
    transcription = processor.decode(predicted_ids[0])

    # Devolver la transcripción
    return {'transcription': transcription}
