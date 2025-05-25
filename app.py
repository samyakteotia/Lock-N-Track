from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from XOR_Encrypt.encrypt_decrypt import encrypt_file_with_password, decrypt_file_with_password_attempts
from Huffman.compress_decompress import compress_file, decompress_file
from version_control.vcs import init_vcs, snapshot, revert_to_snapshot
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super-secure-key-123'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed_files'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bin'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None

@app.route('/')
def index():
    return render_template('index.html')

# ... (previous imports remain the same) ...

@app.route('/process', methods=['POST'])
def process_file():
    operation = request.form.get('operation')
    file = request.files.get('file')
    password = request.form.get('password')
    hash_digest = request.form.get('hash_digest')
    
    try:
        # Validate file requirements
        if operation in ['encrypt', 'decrypt', 'compress', 'decompress']:
            if not file or file.filename == '':
                flash('Please select a file for this operation')
                return redirect(url_for('index'))
            
            if not allowed_file(file.filename):
                flash('Invalid file type')
                return redirect(url_for('index'))
            
            filepath = save_file(file)
            if not filepath:
                flash('Error saving file')
                return redirect(url_for('index'))

        # Process operations
        if operation == 'encrypt':
            if not password:
                flash('Password is required for encryption')
                return redirect(url_for('index'))
            
            output_filename = f"encrypted_{file.filename}"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            
            # Copy and encrypt
            shutil.copyfile(filepath, output_path)
            encrypt_file_with_password(output_path, password)
            
            return render_template('result.html',
                               message="File encrypted successfully!",
                               filename=output_filename,
                               operation=operation)

        elif operation == 'decrypt':
            if not password:
                flash('Password is required for decryption')
                return redirect(url_for('index'))
            
            # Handle filename
            orig_filename = file.filename
            if orig_filename.startswith('encrypted_'):
                orig_filename = orig_filename[len('encrypted_'):]
            output_filename = f"decrypted_{orig_filename}"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            
            # Create temp file
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{file.filename}")
            shutil.copyfile(filepath, temp_path)
            
            try:
                # Attempt decryption
                decrypt_file_with_password_attempts(temp_path, password)
                
                # If successful, move to processed files
                shutil.move(temp_path, output_path)
                
                return render_template('result.html',
                                   message="File decrypted successfully!",
                                   filename=output_filename,
                                   operation=operation)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                flash('Decryption failed: Incorrect password or corrupted file')
                return redirect(url_for('index'))

        elif operation == 'compress':
            output_filename = f"compressed_{file.filename}.bin"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            
            # Compress file
            compress_file(filepath, output_path)
            
            return render_template('result.html',
                               message="File compressed successfully!",
                               filename=output_filename,
                               operation=operation)

        elif operation == 'decompress':
            # Handle filename
            orig_filename = file.filename
            if orig_filename.startswith('compressed_'):
                orig_filename = orig_filename[len('compressed_'):]
            if orig_filename.endswith('.bin'):
                orig_filename = orig_filename[:-4]
            output_filename = f"decompressed_{orig_filename}"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            
            # Decompress file
            try:
                decompress_file(filepath, output_path)
                return render_template('result.html',
                                   message="File decompressed successfully!",
                                   filename=output_filename,
                                   operation=operation)
            except Exception as e:
                flash('Decompression failed: File may not be compressed')
                return redirect(url_for('index'))

        elif operation == 'init_vcs':
            init_vcs()
            return render_template('result.html',
                               message="Version control system initialized successfully!",
                               operation=operation)

        elif operation == 'snapshot':
            snapshot('.')
            return render_template('result.html',
                               message="Snapshot created successfully!",
                               operation=operation)

        elif operation == 'revert':
            if not hash_digest:
                flash('Snapshot hash is required')
                return redirect(url_for('index'))
            try:
                revert_to_snapshot(hash_digest)
                return render_template('result.html',
                                   message=f"Successfully reverted to snapshot {hash_digest}",
                                   operation=operation)
            except Exception as e:
                flash(f"Revert failed: {str(e)}")
                return redirect(url_for('index'))

    except Exception as e:
        flash(f'Operation failed: {str(e)}')
        return redirect(url_for('index'))

# ... (rest of the file remains the same) ...

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)