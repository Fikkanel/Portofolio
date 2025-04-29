from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci_rahasia_aplikasi_anda'  # Ganti dengan kunci rahasia yang kuat
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Pastikan folder uploads ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# File untuk menyimpan data
VIDEOS_FILE = 'data/videos.json'
PHOTOS_FILE = 'data/photos.json'
MESSAGES_FILE = 'data/messages.json'
ADMIN_FILE = 'data/admin.json'

# Pastikan folder data ada
os.makedirs('data', exist_ok=True)

# Inisialisasi file data jika belum ada
def init_data_files():
    if not os.path.exists(VIDEOS_FILE):
        with open(VIDEOS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(PHOTOS_FILE):
        with open(PHOTOS_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'w') as f:
            # Default admin username: admin, password: admin123
            json.dump({
                "username": "admin",
                "password": generate_password_hash("admin123")
            }, f)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_videos():
    with open(VIDEOS_FILE, 'r') as f:
        return json.load(f)

def save_videos(videos):
    with open(VIDEOS_FILE, 'w') as f:
        json.dump(videos, f, indent=4)

def get_photos():
    with open(PHOTOS_FILE, 'r') as f:
        return json.load(f)

def save_photos(photos):
    with open(PHOTOS_FILE, 'w') as f:
        json.dump(photos, f, indent=4)

def get_messages():
    with open(MESSAGES_FILE, 'r') as f:
        return json.load(f)

def save_message(message):
    messages = get_messages()
    messages.append(message)
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=4)

def get_photo_categories():
    photos = get_photos()
    categories = set()
    for photo in photos:
        if 'category' in photo:
            categories.add(photo['category'])
    return list(categories)

# Middleware for checking if user is logged in
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Silakan login terlebih dahulu', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Routes
@app.route('/')
def index():
    videos = get_videos()
    photos = get_photos()
    photo_categories = get_photo_categories()
    
    is_logged_in = 'logged_in' in session and session['logged_in']
    
    return render_template('index.html', 
                           videos=videos, 
                           photos=photos, 
                           photo_categories=photo_categories,
                           is_logged_in=is_logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        with open(ADMIN_FILE, 'r') as f:
            admin = json.load(f)
        
        if username == admin['username'] and check_password_hash(admin['password'], password):
            session['logged_in'] = True
            flash('Login berhasil!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password salah', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout berhasil', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    videos = get_videos()
    photos = get_photos()
    messages = get_messages()
    
    return render_template('admin/dashboard.html', 
                           videos=videos, 
                           photos=photos, 
                           messages=messages)

@app.route('/add-video', methods=['GET', 'POST'])
@login_required
def add_video():
    if request.method == 'POST':
        title = request.form.get('title')
        embed_url = request.form.get('embed_url')
        description = request.form.get('description')
        
        # Validasi input
        if not title or not embed_url:
            flash('Judul dan URL embed video wajib diisi', 'danger')
            return redirect(url_for('add_video'))
        
        # Konversi URL YouTube biasa ke format embed jika perlu
        if 'youtube.com/watch?v=' in embed_url:
            video_id = embed_url.split('v=')[1].split('&')[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be/' in embed_url:
            video_id = embed_url.split('youtu.be/')[1]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
        
        videos = get_videos()
        videos.append({
            'id': len(videos) + 1,
            'title': title,
            'embed_url': embed_url,
            'description': description,
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        save_videos(videos)
        flash('Video berhasil ditambahkan', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_video.html')

@app.route('/edit-video/<int:video_id>', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    videos = get_videos()
    video = None
    
    for v in videos:
        if v['id'] == video_id:
            video = v
            break
    
    if video is None:
        flash('Video tidak ditemukan', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        embed_url = request.form.get('embed_url')
        description = request.form.get('description')
        
        # Validasi input
        if not title or not embed_url:
            flash('Judul dan URL embed video wajib diisi', 'danger')
            return redirect(url_for('edit_video', video_id=video_id))
        
        # Konversi URL YouTube biasa ke format embed jika perlu
        if 'youtube.com/watch?v=' in embed_url:
            video_id_yt = embed_url.split('v=')[1].split('&')[0]
            embed_url = f"https://www.youtube.com/embed/{video_id_yt}"
        elif 'youtu.be/' in embed_url:
            video_id_yt = embed_url.split('youtu.be/')[1]
            embed_url = f"https://www.youtube.com/embed/{video_id_yt}"
        
        # Update video
        for v in videos:
            if v['id'] == video_id:
                v['title'] = title
                v['embed_url'] = embed_url
                v['description'] = description
                break
        
        save_videos(videos)
        flash('Video berhasil diperbarui', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_video.html', video=video)

@app.route('/delete-video/<int:video_id>')
@login_required
def delete_video(video_id):
    videos = get_videos()
    new_videos = [v for v in videos if v['id'] != video_id]
    
    if len(videos) == len(new_videos):
        flash('Video tidak ditemukan', 'danger')
    else:
        save_videos(new_videos)
        flash('Video berhasil dihapus', 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/add-photo', methods=['GET', 'POST'])
@login_required
def add_photo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        
        # Validasi input
        if not title or 'photo' not in request.files:
            flash('Judul dan file foto wajib diisi', 'danger')
            return redirect(url_for('add_photo'))
        
        photo_file = request.files['photo']
        
        if photo_file.filename == '':
            flash('Tidak ada file yang dipilih', 'danger')
            return redirect(url_for('add_photo'))
        
        if photo_file and allowed_file(photo_file.filename):
            # Mengamankan nama file
            filename = secure_filename(photo_file.filename)
            
            # Menambahkan timestamp untuk menghindari nama file yang sama
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            
            # Menyimpan file
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Menyimpan informasi foto ke JSON
            photos = get_photos()
            photos.append({
                'id': len(photos) + 1,
                'title': title,
                'description': description,
                'category': category,
                'filename': filename,
                'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            save_photos(photos)
            flash('Foto berhasil ditambahkan', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Format file tidak diizinkan. Gunakan: png, jpg, jpeg, gif', 'danger')
            
    # Mengambil kategori yang sudah ada untuk dropdown
    categories = get_photo_categories()
    
    return render_template('admin/add_photo.html', categories=categories)

@app.route('/edit-photo/<int:photo_id>', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    photos = get_photos()
    photo = None
    
    for p in photos:
        if p['id'] == photo_id:
            photo = p
            break
    
    if photo is None:
        flash('Foto tidak ditemukan', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        
        # Validasi input
        if not title:
            flash('Judul wajib diisi', 'danger')
            return redirect(url_for('edit_photo', photo_id=photo_id))
        
        # Cek apakah ada upload file baru
        new_filename = photo['filename']
        if 'photo' in request.files and request.files['photo'].filename != '':
            photo_file = request.files['photo']
            
            if photo_file and allowed_file(photo_file.filename):
                # Hapus file lama jika ada
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo['filename'])
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                
                # Simpan file baru
                new_filename = secure_filename(photo_file.filename)
                new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{new_filename}"
                photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            else:
                flash('Format file tidak diizinkan. Gunakan: png, jpg, jpeg, gif', 'danger')
                return redirect(url_for('edit_photo', photo_id=photo_id))
        
        # Update foto
        for p in photos:
            if p['id'] == photo_id:
                p['title'] = title
                p['description'] = description
                p['category'] = category
                p['filename'] = new_filename
                break
        
        save_photos(photos)
        flash('Foto berhasil diperbarui', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Mengambil kategori yang sudah ada untuk dropdown
    categories = get_photo_categories()
    
    return render_template('admin/edit_photo.html', photo=photo, categories=categories)

@app.route('/delete-photo/<int:photo_id>')
@login_required
def delete_photo(photo_id):
    photos = get_photos()
    photo_to_delete = None
    
    for p in photos:
        if p['id'] == photo_id:
            photo_to_delete = p
            break
    
    if photo_to_delete is None:
        flash('Foto tidak ditemukan', 'danger')
    else:
        # Hapus file foto
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_to_delete['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Hapus dari data JSON
        new_photos = [p for p in photos if p['id'] != photo_id]
        save_photos(new_photos)
        flash('Foto berhasil dihapus', 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/send-message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message_text = request.form.get('message')
        
        # Validasi input
        if not all([name, email, subject, message_text]):
            flash('Semua field wajib diisi', 'danger')
            return redirect(url_for('index', _anchor='contact'))
        
        # Simpan pesan
        message = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message_text,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': False
        }
        
        save_message(message)
        flash('Pesan berhasil dikirim. Terima kasih!', 'success')
        return redirect(url_for('index', _anchor='contact'))
    
    return redirect(url_for('index'))

@app.route('/mark-message-read/<int:message_index>')
@login_required
def mark_message_read(message_index):
    messages = get_messages()
    
    if 0 <= message_index < len(messages):
        messages[message_index]['read'] = True
        
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=4)
            
        flash('Pesan ditandai sebagai sudah dibaca', 'success')
    else:
        flash('Pesan tidak ditemukan', 'danger')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/delete-message/<int:message_index>')
@login_required
def delete_message(message_index):
    messages = get_messages()
    
    if 0 <= message_index < len(messages):
        messages.pop(message_index)
        
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=4)
        
        flash('Pesan berhasil dihapus', 'success')
    else:
        flash('Pesan tidak ditemukan', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validasi input
        if not all([current_password, new_password, confirm_password]):
            flash('Semua field wajib diisi', 'danger')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('Password baru dan konfirmasi password tidak cocok', 'danger')
            return redirect(url_for('change_password'))
        
        # Verifikasi password lama
        with open(ADMIN_FILE, 'r') as f:
            admin = json.load(f)
        
        if not check_password_hash(admin['password'], current_password):
            flash('Password saat ini salah', 'danger')
            return redirect(url_for('change_password'))
        
        # Update password
        admin['password'] = generate_password_hash(new_password)
        
        with open(ADMIN_FILE, 'w') as f:
            json.dump(admin, f, indent=4)
        
        flash('Password berhasil diubah', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/change_password.html')

# API untuk mengambil data
@app.route('/api/videos')
def api_videos():
    videos = get_videos()
    return jsonify(videos)

@app.route('/api/photos')
def api_photos():
    photos = get_photos()
    return jsonify(photos)

@app.route('/api/photo-categories')
def api_photo_categories():
    categories = get_photo_categories()
    return jsonify(categories)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Main function
if __name__ == '__main__':
    # Inisialisasi file data
    init_data_files()
    
    # Jalankan aplikasi
    app.run(host='0.0.0.0', port=8080, debug=True)