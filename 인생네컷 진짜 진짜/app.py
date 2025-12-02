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
        frames = [f for f in os.listdir(frame_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if request.method == 'POST':
        selected = request.form.get('frame') or ''
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
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400

        images = data.get('images', [])
        frame_name = data.get('frame', '')

        if not images:
            return jsonify({'error': 'No images received'}), 400

        imgs = []
        for img_b64 in images:
            header, encoded = img_b64.split(',', 1)
            binary = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(binary)).convert('RGB')
            imgs.append(img)

        w, h = imgs[0].size
        for i in range(len(imgs)):
            if imgs[i].size != (w, h):
                imgs[i] = imgs[i].resize((w, h))

        margin = 40
        spacing = 60
        footer_height = 180

        result_h = footer_height + (h * len(imgs)) + (spacing * (len(imgs) - 1)) + spacing
        result_w = w + margin * 2

        result = Image.new('RGB', (result_w, result_h), (255, 255, 255))
        draw = ImageDraw.Draw(result)

        y_offset = spacing
        for img in imgs:
            x = (result_w - w) // 2
            result.paste(img, (x, y_offset))
            y_offset += h + spacing

        footer_text = datetime.now().strftime("%Y.%m.%d  |  OnAir")
        try:
            font_info = ImageFont.truetype("arial.ttf", 56)
        except:
            font_info = ImageFont.load_default()

        bbox_f = draw.textbbox((0, 0), footer_text, font=font_info)
        fw = bbox_f[2] - bbox_f[0]

        draw.text(
            ((result_w - fw) / 2, result_h - footer_height + 50),
            footer_text,
            fill=(100, 100, 100),
            font=font_info
        )

        if frame_name:
            frame_path = os.path.join(app.static_folder, 'frames', frame_name)
            if os.path.exists(frame_path):
                frame_img = Image.open(frame_path).convert('RGBA')
                frame_img = frame_img.resize(result.size)
                result = result.convert('RGBA')
                result = Image.alpha_composite(result, frame_img)
                result = result.convert('RGB')

        #인화지(1181×1748px) 고려함
        target_w, target_h = 1181*2, 1748*2
        canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))

        result.thumbnail((target_w, target_h), Image.LANCZOS)
        # 중앙 배치
        x = (target_w - result.width) // 2
        y = (target_h - result.height) // 2
        canvas.paste(result, (x, y))

        result = canvas

        # 저장
        out_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg')
        result.save(out_path, format='JPEG', quality=90)

        return jsonify({'result_url': '/' + out_path})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500


@app.route('/result')
def result():
    return render_template('result.html', ts=int(datetime.now().timestamp()))


if __name__ == '__main__':
    app.run(debug=True)
