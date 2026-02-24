import numpy_financial as npf
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

VAT_RATE = 0.16
default_down_payment = {"new_car": 20, "used_car": 30}

st.title("Калькулятор автокредитования 🚗")

# ================================
# Тип автомобиля
# ================================
car_type = st.selectbox(
    "Тип автомобиля", ["Новый автомобиль", "Автомобиль с пробегом"]
)
car_key = "new_car" if car_type == "Новый автомобиль" else "used_car"

# ================================
# Стоимость автомобиля
# ================================
car_price = st.number_input(
    "Стоимость автомобиля (в тенге)",
    min_value=0,
    max_value=200_000_000,
    value=12_000_000,
    step=100_000
)

st.write(f"💰 Введенная стоимость автомобиля: **{car_price:,.0f} тенге**")

# ================================
# Первоначальный взнос
# ================================
down_payment_percent = st.slider(
    "Первоначальный взнос (%)",
    0,
    100,
    default_down_payment.get(car_key, 30),
    step=5
)

# ================================
# Ставка вознаграждения
# ================================
st.subheader("Процентная ставка")

interest_rate_percent = st.slider(
    "Ставка вознаграждения (% годовых)",
    min_value=0.5,
    max_value=40.0,
    value=25.0,
    step=0.1
)

rate = interest_rate_percent / 100
monthly_rate = rate / 12

# ================================
# Срок займа
# ================================
st.subheader("Срок займа")

loan_term = st.slider(
    "Срок займа (в месяцах)",
    12,
    84,
    60,
    step=12
)

# ================================
# Страхование
# ================================
st.subheader("Страхование КАСКО")

insurance_switch = st.toggle("Добавить КАСКО", value=True)

insurance_rate_percent = 0
insurance_term_years = 0
insurance_premium = 0

if insurance_switch:

    insurance_rate_percent = st.slider(
        "Тариф КАСКО (% от стоимости авто в год)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.1
    )

    max_insurance_term = min(7, loan_term // 12)

    insurance_term_years = st.slider(
        "Срок страхования (лет)",
        min_value=0,
        max_value=max_insurance_term,
        value=min(2, max_insurance_term),
        step=1
    )

    insurance_rate = insurance_rate_percent / 100
    insurance_premium = car_price * insurance_rate * insurance_term_years

    st.write(
        f"💰 Стоимость страховой премии: **{insurance_premium:,.0f} тенге**"
    )
else:
    st.write("КАСКО не выбрано.")

# ================================
# Сумма займа
# ================================
principal_net = car_price * (1 - down_payment_percent / 100)
loan_amount = principal_net + insurance_premium

# ================================
# Субсидия (только для новых авто)
# ================================
has_subsidy = False
subsidy_percent = 0
subsidy_amount = 0

if car_key == "new_car":
    st.subheader("Субсидия от дистрибьютера")
    has_subsidy = st.toggle("Наличие субсидии", value=True)

if has_subsidy:
    subsidy_percent = st.slider("Размер субсидии (%)", 0, 20, 10, step=1)
    subsidy_amount = car_price * subsidy_percent / 100
    st.write(f"💸 Сумма субсидии: **{subsidy_amount:,.0f} тенге**")
else:
    if car_key == "new_car":
        st.write("Субсидия не применяется.")

# ================================
# Расчет платежей
# ================================
monthly_payment = -npf.pmt(monthly_rate, loan_term, loan_amount)
total_payment = monthly_payment * loan_term
total_interest = total_payment - loan_amount

# Перерасчет при субсидии
if has_subsidy:
    total_interest -= subsidy_amount / (1 + VAT_RATE)
    monthly_payment = (loan_amount + total_interest) / loan_term
    monthly_rate = npf.rate(loan_term, -monthly_payment, loan_amount, 0, when=0)
    rate = monthly_rate * 12

# ================================
# Вывод результатов
# ================================
st.markdown("## Результаты расчета")

if has_subsidy and rate < 0:
    st.write("#### Невозможно рассчитать. Измените параметры!")
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
