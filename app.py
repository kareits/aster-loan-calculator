# КАЛЬКУЛЯТОР ДЛЯ АВТОКРЕДИТОВ
# import os

import numpy_financial as npf
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
# from PIL import Image


# Словари ставок, тарифов страхования и первоначального взноса
car_rate_dict = {"used_car": 0.33, "new_car": 0.28}
insurance_rates = {"new_car": 0.045, "used_car": 0.025}
default_down_payment = {"new_car": 20, "used_car": 30}

# # Путь к PNG-логотипу
# logo_path = os.path.join(os.path.dirname(__file__), "media", "solva_logo.png")
# logo_image = Image.open(logo_path)

# Заголовок с логотипом
st.title("Калькулятор автокредитования 🚗")

# col1, col2 = st.columns([1, 0.2])
# with col1:
#     st.markdown(
#         '<span style="font-size:32px; font-weight:bold;">Калькулятор автокредитования</span>',
#         unsafe_allow_html=True
#     )
# with col2:
#     st.image(logo_image, width=120)  # ширина 120 px

# Выбор типа автомобиля
car_type = st.selectbox(
    "Тип автомобиля", ["Новый автомобиль", "Автомобиль с пробегом"]
)
car_key = "new_car" if car_type == "Новый автомобиль" else "used_car"

# Стоимость автомобиля
car_price = st.number_input(
    "Стоимость автомобиля (в тенге)",
    min_value=0,
    max_value=200_000_000,
    value=10_000_000,
    step=100_000
)

# Отображаем значение с разрядами
st.write(f"💰 Введенная стоимость автомобиля: **{car_price:,.0f} тенге**")

# Первоначальный взнос
down_payment_percent = st.slider(
    "Первоначальный взнос (%)",
    0,
    100,
    default_down_payment.get(car_key, 30),
    step=5
)

# Расчет страховой премии
st.subheader("Страхование КАСКО")
insurance_switch = st.toggle("Страхование Каско на 1 год", value=False)
insurance_premium = 0
if insurance_switch:
    insurance_premium = car_price * insurance_rates[car_key]
    st.write(
        f"💰 Стоимость страховой премии: **{insurance_premium:,.0f} тенге**"
    )
else:
    st.write("КАСКО не выбрано.")

# Сумма займа со страховой премией
principal_net = car_price * (1 - down_payment_percent / 100)
loan_amount = principal_net + insurance_premium 

# Субсидия от дистрибьютера
has_subsidy = False
if car_key == "new_car":
    st.subheader("Субсидия от дистрибьютера")
    has_subsidy = st.toggle("Наличие субсидии от дистрибьютера", value=False)
subsidy_percent = 0
subsidy_amount = 0
if has_subsidy:
    subsidy_percent = st.slider("Размер субсидии (%)", 0, 20, 5, step=1)
    subsidy_amount = car_price * subsidy_percent / 100
    st.write(f"💸 Сумма субсидии: **{subsidy_amount:,.0f} тенге**")
else:
    st.write("Субсидия не применяется.")

# Срок займа
st.subheader("Срок займа")
loan_term = st.slider("Срок займа (в месяцах)", 0, 84, 60, step=12)

# Расчет аннуитетного платежа и общей суммы вознаграждения
rate = car_rate_dict[car_key]
monthly_rate = rate / 12
monthly_payment = -npf.pmt(monthly_rate, loan_term, loan_amount)
total_payment = monthly_payment * loan_term
total_interest = total_payment - loan_amount
if has_subsidy:
    total_interest -= subsidy_amount
    monthly_payment = (loan_amount + total_interest) / loan_term
    monthly_rate = npf.rate(loan_term, -monthly_payment, loan_amount, 0, when=0)
    rate = monthly_rate * 12

st.markdown(f"## Результаты расчета")
if has_subsidy and rate < 0:
    st.write(f"#### Невозможно рассчитать. Измените первоначальный взнос и/или размер субсидий!")
else:
    st.write(f"#### 📊 Сумма займа: **{loan_amount:,.2f} тенге**")
    st.write(f"#### 📈 Ставка вознаграждения: **{rate * 100:.2f}% годовых**")
    st.write(f"#### 💳 Ежемесячный платеж: {monthly_payment:,.2f} тенге")
    st.write(f"#### 🧾 Сумма переплаты: {total_interest:,.2f} тенге")

# Функция форматирования чисел
def format_number(value):
    if isinstance(value, (int, float)):
        return f"{value:.2f}".replace(".", ",")
    return value

# Формируем таблицу с результатами
results_data = {
    "Параметр": [
        "Тип автомобиля",
        "Стоимость автомобиля, ₸",
        "Первоначальный взнос, %",
        "Первоначальный взнос, ₸",
        "Страховая премия, ₸",
        "Субсидия, %",
        "Субсидия, ₸",
        "Срок займа, мес.",
        "Ставка вознаграждения, % годовых",
        "Сумма займа, ₸",
        "Ежемесячный платеж, ₸",
        "Переплата, ₸",
    ],
    "Значение": [
        car_type,
        format_number(car_price),
        format_number(down_payment_percent),
        format_number(car_price * down_payment_percent / 100),
        format_number(insurance_premium),
        format_number(subsidy_percent),
        format_number(subsidy_amount),
        format_number(loan_term),
        format_number(rate * 100),
        format_number(loan_amount),
        format_number(monthly_payment),
        format_number(total_interest),
    ],
}

df_results = pd.DataFrame(results_data)

# Формируем текст для копирования в TSV (табами)
copy_text = df_results.to_csv(index=False, sep="\t", header=True)

# Кнопка копирования (через HTML-компонент)
components.html(
    f"""
    <button id="copyBtn"
        style="
            background-color:white;
            color:#db330d;
            padding:10px 16px;
            border:2px solid #db330d;
            border-radius:8px;
            font-size:16px;
            font-weight:600;
            cursor:pointer;
        ">
        📎 Копировать в буфер
    </button>
    <script>
        const btn = document.getElementById('copyBtn');
        btn.addEventListener('click', () => {{
            navigator.clipboard.writeText(`{copy_text}`).then(() => {{
                alert('✅ Данные скопированы! Теперь можно вставить в Excel (Ctrl+V)');
            }}).catch(err => {{
                alert('❌ Ошибка копирования: ' + err);
            }});
        }});
    </script>
    """,
    height=100,
)
