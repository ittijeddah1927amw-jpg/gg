import os, uuid
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import yt_dlp

app = Flask(__name__)
app.secret_key = "secret123"  # علشان الفلاش ميسج

FFMPEG_PATH = os.path.join(os.getcwd(), "bin", "ffmpeg.exe")
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")

if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)


def download_video(url, fmt, quality):
    outtmpl = os.path.join(DOWNLOADS_DIR, f"{uuid.uuid4()}.%(ext)s")

    if fmt == "MP4":
        height_map = {"4K": 2160, "2K": 1440}
        q = height_map.get(quality, quality)
        format_str = f"bestvideo[height<={q}]+bestaudio/best"
        opts = {
            "format": format_str,
            "outtmpl": outtmpl,
            "merge_output_format": "mp4",
            "ffmpeg_location": FFMPEG_PATH,
            "noplaylist": True,
            "ignoreerrors": True,
        }
    else:  # MP3
        opts = {
            "format": "bestaudio",
            "outtmpl": outtmpl,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }],
            "ffmpeg_location": FFMPEG_PATH,
            "noplaylist": True,
            "ignoreerrors": True,
        }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    # نحصل على أحدث ملف نزل
    file_path = max(
        [os.path.join(DOWNLOADS_DIR, f) for f in os.listdir(DOWNLOADS_DIR)],
        key=os.path.getctime
    )
    return file_path


# ---------- الصفحات ----------
@app.route("/")
def home():
    apps = ["YouTube", "Instagram", "TikTok", "تطبيق آخر"]
    return render_template("home.html", apps=apps)


@app.route("/download/<app_name>", methods=["GET", "POST"])
def download_page(app_name):
    if request.method == "POST":
        url = request.form.get("url")
        fmt = request.form.get("format")
        quality = request.form.get("quality")

        if not url:
            flash("❌ يرجى إدخال رابط")
            return redirect(request.url)

        try:
            file_path = download_video(url, fmt, quality)
            filename = os.path.basename(file_path)
            return redirect(url_for("finished", filename=filename))
        except Exception as e:
            flash(f"⚠️ خطأ: {e}")
            return redirect(request.url)

    return render_template("download.html", app_name=app_name)


@app.route("/finished/<filename>")
def finished(filename):
    return render_template("finished.html", filename=filename)


@app.route("/get/<filename>")
def get_file(filename):
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
