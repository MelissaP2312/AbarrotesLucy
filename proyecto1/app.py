from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import torchaudio
import tensorflow as tf
import torch
import numpy as np
from transformers import Wav2Vec2Processor, TFWav2Vec2ForCTC
from pydub import AudioSegment
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'ogg', 'flac', 'm4a'}

# Modelo en español
MODEL_NAME = "jonatasgrosman/wav2vec2-large-xlsr-53-spanish"
with app.app_context():
    processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
    model = TFWav2Vec2ForCTC.from_pretrained(MODEL_NAME, from_pt=True)  # Cargar en TensorFlow

TARGET_SAMPLE_RATE = 16000

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def procesar_audio(file_path):
    try:
        # Conversión a WAV con FFmpeg
        if not file_path.lower().endswith('.wav'):
            audio = AudioSegment.from_file(file_path)
            wav_path = os.path.splitext(file_path)[0] + '.wav'
            audio.export(
                wav_path, 
                format='wav',
                parameters=["-ac", "1", "-ar", str(TARGET_SAMPLE_RATE)]
            )
            file_path = wav_path

        # Cargar audio con torchaudio
        waveform, orig_sample_rate = torchaudio.load(file_path)
        
        # Convertir a mono
        if waveform.size(0) > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
            
        # Resamplear si es necesario
        if orig_sample_rate != TARGET_SAMPLE_RATE:
            resampler = torchaudio.transforms.Resample(
                orig_freq=orig_sample_rate,
                new_freq=TARGET_SAMPLE_RATE
            )
            waveform = resampler(waveform)
            
        # Normalización segura
        max_val = torch.max(torch.abs(waveform))
        if max_val > 0:
            waveform = waveform / max_val
        else:
            raise ValueError("Audio silencioso o sin señal")
            
        # Convertir a numpy array para TensorFlow
        audio_array = waveform.squeeze().numpy()

        # Transcripción con TensorFlow
        input_values = processor(
            audio_array, 
            sampling_rate=TARGET_SAMPLE_RATE, 
            return_tensors="tf"
        ).input_values
        
        logits = model(input_values).logits
        predicted_ids = tf.argmax(logits, axis=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
        
        return transcription

    except Exception as e:
        app.logger.error(f"Error en procesar_audio: {str(e)}")
        raise RuntimeError(f"Error de procesamiento: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"error": "No se proporcionó un archivo de audio"}), 400
        return redirect(url_for('index'))
    
    file = request.files['audio']
    if file.filename == '':
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"error": "Nombre de archivo vacío"}), 400
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"error": "Formato de archivo no soportado"}), 400
        return "Formato de archivo no soportado", 400
    
    try:
        # Guardar archivo temporal
        filename = file.filename
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Procesar y transcribir
        transcription = procesar_audio(upload_path)
        
        # Limpieza de archivos
        temp_files = {
            upload_path,
            os.path.splitext(upload_path)[0] + '.wav'
        }
        
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as e:
                    app.logger.warning(f"Error eliminando {f}: {str(e)}")
        
        # Determinar el tipo de respuesta
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"transcription": transcription})
        else:
            return render_template('index.html', 
                                transcription=transcription,
                                error=None)
    
    except Exception as e:
        app.logger.error(f"Error general: {str(e)}\n{traceback.format_exc()}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({"error": str(e)}), 500
        return render_template('index.html', 
                            transcription=None,
                            error=f"Error: {str(e)}"), 500

@app.route('/send-message', methods=['POST'])
def send_message():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    mensaje = request.form.get('mensaje')
    
    # Aquí puedes agregar la lógica para enviar el mensaje (por ejemplo, guardar en una base de datos o enviar un correo electrónico)
    
    return "Mensaje enviado con éxito"

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)