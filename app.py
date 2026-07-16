import io
import random
import string
import base64
from flask import Flask, render_template_string, request, session
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
# Секретный ключ нужен для работы сессий (хранения правильного ответа)
app.secret_key = random.randint(100000, 999999)
print(app.secret_key)


def create_captcha():
    """Генерирует текст капчи и возвращает её изображение в формате Base64"""
    text = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session["captcha_text"] = text  # Сохраняем правильный ответ в сессию

    # Создание изображения
    width, height = 180, 60
    image = Image.new("RGB", (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)

    # Добавление шума (линии)
    for _ in range(10):
        draw.line(
            [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height)),
            ],
            fill=(180, 180, 180),
            width=2,
        )

    # Отрисовка текста
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    draw.text((30, 10), text, fill=(50, 50, 50), font=font)

    # Конвертация изображения в строку Base64 для HTML
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    return base64.b64encode(img_byte_arr).decode("utf-8")


# Обновленный HTML-шаблон со скриптом задержки
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Проверка безопасности</title>
    
    <!-- Современный шрифт -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #5b69d8 100%);
            --success-color: #10b981;
            --error-color: #ef4444;
            --bg-light: #f8fafc;
            --text-dark: #1e293b;
            --border-radius: 16px;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-light);
            color: var(--text-dark);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .captcha-container {
            width: 100%;
            max-width: 420px;
            background: white;
            border-radius: var(--border-radius);
            padding: 40px 30px;
            box-shadow: var(--shadow-lg);
            text-align: center;
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.5s ease-out forwards;
        }

        h2 {
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        p.subtitle {
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 30px;
            opacity: 0.9;
        }

        /* Сообщение об успехе или ошибке */
        .message {
            font-weight: 500;
            padding: 14px 18px;
            border-radius: 12px;
            margin-bottom: 25px;
            transform: translateY(0);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .message.success {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success-color);
            border: 1px solid rgba(16, 185, 129, 0.3);
            transform: translateY(-5px);
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
        }

        .message.error {
            background: rgba(239, 68, 68, 0.1);
            color: var(--error-color);
            border: 1px solid rgba(239, 68, 68, 0.3);
            transform: translateY(-5px);
            box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.1);
        }

        /* Поле ввода */
        input[type="text"] {
            width: 100%;
            padding: 16px;
            font-size: 1.1rem;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            outline: none;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }

        /* Иконка внутри поля ввода */
        input[type="text"]::before {
            content: '';
            display: inline-block;
            vertical-align: middle;
            margin-right: 14px;
            height: 22px;
            width: 22px;
            pointer-events: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M7 9v1H5c-.6 0-1 .4-1 1v11a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1V9c0-.6-.4-1-1-1h-1v1h-4V5l-5 5zm-3 3h2v10c0 .6-.4 1-1 1H4V12h1zM4 3h14a2 2 0 0 1 2 2v6h-2V5a2 2 0 0 0-2-2H4c-1.1 0-2 .9-2 2v6H0V5c0-1.1.9-2 2-2z' fill='%2364748B'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
        }

        input[type="text"]:focus,
        input[type="text"]:hover {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Кнопка */
        button.submit-btn {
            width: 100%;
            padding: 16px;
            margin-top: 15px;
            font-size: 1.1rem;
            font-weight: 600;
            color: white;
            background: var(--primary-gradient); /* Фиолетовый градиент */
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        button.submit-btn::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            transform: translate(-50%, -50%);
            transition: width 0.4s ease, height 0.4s ease;
        }

        button.submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(102, 126, 234, 0.4);
        }

        button.submit-btn:active::after {
            width: 200px;
            height: 200px;
        }

        /* Блок обновления и лого внизу */
        .refresh-btn {
            position: absolute;
            right: 12px;
            bottom: 12px;
            width: 36px;
            height: 36px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }

        .refresh-btn svg {
            width: 16px;
            height: 16px;
            stroke: #64748b;
            transition: stroke 0.2s ease;
        }

        .refresh-btn:hover {
            background: #f8fafc;
            transform: scale(1.05);
            box-shadow: var(--shadow-md);
        }

        .refresh-btn:hover svg {
            stroke: #475569;
        }

        .powered-by {
            margin-top: 35px;
            padding-top: 25px;
            border-top: 1px dashed #cbd5e1;
            font-size: 0.85rem;
            color: #94a3b8;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 480px) {
            .captcha-container { padding: 30px 20px; }
            h2 { font-size: 1.5rem; }
            img.captcha-img { width: 240px; height: 80px; }
        }
    </style>
</head>
<body>
<div class="captcha-container">
    <h2>Подтвердите, что вы не робот</h2>
    <p class="subtitle">Введите код с картинки в поле ниже</p>

    {% if message %}
        <div class="message {{ 'success' if is_correct else 'error' }}">
            {{ message }}
        </div>
    {% endif %}

    <div class="captcha-wrapper">
        <img src="data:image/png;base64,{{ captcha_img }}" alt="Капча" class="captcha-img">
        <button type="button" class="refresh-btn" onclick="location.reload()" aria-label="Обновить капчу">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.004 8.004 0 0 0 17.8 8l-4.56 4.56a8 8 0 0 1 0 11.32l-4.56 4.56a8.004 8.004 0 0 1-11.32 0L4 17.8m15.356-13A8.004 8.004 0 0 1 20 8a8.004 8.004 0 0 1-11.356 6.23"></path></svg>
        </button>
    </div>

    <form method="POST">
        <input type="text" name="user_input" placeholder="КОД ЗДЕСЬ" autocomplete="off" required pattern="[A-Z0-9]{5}">
        <br><br>
        <button type="submit" class="submit-btn">Продолжить</button>
    </form>

    <div class="powered-by">
        ⚡️ Защита от ботов • Powered by Amnezia Captcha
    </div>

    {% if is_correct %}
    <script>
        // Добавляем класс успеха для финальной анимации перед редиректом
        document.querySelector('.captcha-container').classList.add('success-state');
        setTimeout(function () {
            window.location.replace("https://almaks-it.ru");
        }, 3000);
    </script>
    <style>
        .success-state {
            animation: successPulse 2s ease-in-out;
        }
        @keyframes successPulse {
            0%, 100% { 
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); 
            }
            70% { 
                box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); 
            }
        }
    </style>
    {% endif %}
</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    is_correct = False

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip().upper()
        correct_text = session.get("captcha_text", "")

        if user_input == correct_text:
            message = "🎉 Капча пройдена успешно!"
            is_correct = True
        else:
            message = "❌ Неверный код. Попробуйте еще раз."

    # Генерируем новую капчу для следующего отображения
    captcha_img = create_captcha()
    return render_template_string(
        HTML_TEMPLATE,
        captcha_img=captcha_img,
        message=message,
        is_correct=is_correct,
    )


if __name__ == "__main__":
    app.run(debug=True)
