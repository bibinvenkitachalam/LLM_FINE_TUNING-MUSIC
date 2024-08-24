from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for
import os
import music21

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

def convert_text_to_notes(text, note_duration=0.5):
    words = text.split()
    notes = []
    for word in words:
        # Convert each word to a MIDI note number (arbitrarily mapped)
        note_value = sum(ord(char) for char in word) % 128
        notes.append(note_value)
    return notes

def convert_sequence_to_score(sequence, note_duration=0.5):
    score = music21.stream.Score()
    part = music21.stream.Part()

    for pitch in sequence:
        note = music21.note.Note(pitch)
        note.quarterLength = note_duration
        part.append(note)

    score.append(part)
    return score

def show_and_save_score(score, output_midi_file='generated_music21.mid'):
    midi_file_path = os.path.join(app.config['UPLOAD_FOLDER'], output_midi_file)
    mf = music21.midi.translate.music21ObjectToMidiFile(score)
    mf.open(midi_file_path, 'wb')
    mf.write()
    mf.close()
    return midi_file_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_music():
    prompt = request.form.get('prompt')
    note_sequence = convert_text_to_notes(prompt)
    score = convert_sequence_to_score(note_sequence)
    midi_file_path = show_and_save_score(score)

    # Redirect to the download page
    return redirect(url_for('download_file', filename=os.path.basename(midi_file_path)))

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
