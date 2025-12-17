from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image, ImageDraw, ImageFont
import base64, io, os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/frame', methods=['GET', 'POST'])
def frame():
    frames = []
    frame_dir = os.path.join(app.static_folder, 'frames')

    if os.path.exists(frame_dir):
        frames = [
            d for d in os.listdir(frame_dir)
            if os.path.isdir(os.path.join(frame_dir, d))
        ]

    if request.method == 'POST':
        selected = request.form.get('frame')
        return redirect(url_for('camera', frame=selected))

    return render_template('frame.html', frames=frames)

@app.route('/camera')
def camera():
    frame = request.args.get('frame', '')
    return render_template('camera.html', frame=frame)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.get_json()
        images = data.get('images', [])
        frame_name = data.get('frame', '')

        imgs = []
        for img_b64 in images:
            _, encoded = img_b64.split(',', 1)
            binary = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(binary)).convert('RGB')
            img = img.resize((1920, 1080))
            imgs.append(img)

        for idx, img in enumerate(imgs):
            pose_path = os.path.join(
                app.static_folder,
                'frames',
                frame_name,
                f'pose{idx+1}.png'
            )
            if os.path.exists(pose_path):
                pose = Image.open(pose_path).convert('RGBA')
                pose = pose.resize(img.size)
                img = img.convert('RGBA')
                img = Image.alpha_composite(img, pose)
                imgs[idx] = img.convert('RGB')

        w, h = 1920, 1080
        spacing = 60
        footer_height = 180

        result_h = footer_height + (h * 4) + (spacing * 4)
        result_w = w + 80

        result = Image.new('RGB', (result_w, result_h), (255, 255, 255))
        draw = ImageDraw.Draw(result)

        y = spacing
        for img in imgs:
            x = (result_w - w) // 2
            result.paste(img, (x, y))
            y += h + spacing

        footer_text = datetime.now().strftime("%Y.%m.%d  |  OnAir")
        try:
            font = ImageFont.truetype("arial.ttf", 56)
        except:
            font = ImageFont.load_default()

        fw = draw.textbbox((0, 0), footer_text, font=font)[2]
        draw.text(
            ((result_w - fw) // 2, result_h - footer_height + 50),
            footer_text,
            fill=(120, 120, 120),
            font=font
        )

        target_w, target_h = 1181 * 2, 1748 * 2
        canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
        result.thumbnail((target_w, target_h), Image.LANCZOS)

        x = (target_w - result.width) // 2
        y = (target_h - result.height) // 2
        canvas.paste(result, (x, y))

        out_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg')
        canvas.save(out_path, 'JPEG', quality=90)

        saved_files = []

        for i in range(4):
            filename = f"result{i}.jpg"
            path = os.path.join(app.static_folder, filename)
            imgs[i].save(path, format="JPEG", quality=90)
            saved_files.append(filename)


        return jsonify({'result_url': '/static/result.jpg'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/result')
def result():
    return render_template('result.html', ts=int(datetime.now().timestamp()))

@app.route('/print')
def print_page():
    images = [
        "result0.jpg",
        "result1.jpg",
        "result2.jpg",
        "result3.jpg"
    ]
    return render_template("print.html", images=images)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)