import streamlit as st
import math

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Stock Averaging Calculator", page_icon="📈")

# تنسيق CSS مخصص لجعل الواجهة تشبه Dark Mode و Material Design
st.markdown("""
    <style>
    .main {
        background-color: #121212;
    }
    div.stButton > button:first-child {
        background-color: #BB86FC;
        color: black;
        border-radius: 20px;
        width: 100%;
        font-weight: bold;
    }
    .result-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1E1E1E;
        border: 1px solid #333333;
        font-family: 'Consolas', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Stock Averaging Calculator")
st.write("احسب الكمية المطلوبة لتعديل متوسط السعر")

# --- منطقة المدخلات ---
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        target_price = st.number_input("Target Average (المستهدف)", value=3.10, format="%.3f")
        current_price = st.number_input("Market Price (سعر السوق الحالي)", value=3.0, format="%.3f")
    
    with col2:
        old_price = st.number_input("Current Average (متوسطك الحالي)", value=4.08, format="%.3f")
        old_qty = st.number_input("Shares Owned (عدد أسهمك)", value=1000, step=1)

# عمولة التداول (يمكنك تغييرها من هنا)
commission_rate = 0.006 

if st.button("CALCULATE"):
    try:
        # الحسابات الرياضية
        comm_per_share = current_price * commission_rate
        effective_price = current_price + comm_per_share

        if target_price <= effective_price:
            st.error(f"⚠️ يجب أن يكون السعر المستهدف أكبر من سعر الشراء مع العمولة ({effective_price:.3f})")
        else:
            # معادلة التعديل
            q2 = math.ceil((old_qty * (old_price - target_price)) / (target_price - effective_price))
            
            total_shares = old_qty + q2
            total_investment = (old_qty * old_price) + (q2 * effective_price)
            final_avg = total_investment / total_shares

            # عرض النتائج بتنسيق مرتب
            st.markdown("### 📋 Summary Report")
            output = f"""
            <div class="result-box">
            Effective Price (Current + Comm): {effective_price:.3f} <br>
            <b>Required Shares to Buy: {q2:,}</b> <br>
            New Investment Needed: {q2 * effective_price:,.2f} <br>
            <hr>
            Total Shares: {total_shares:,} <br>
            Final Average Price: {final_avg:.3f}
            </div>
            """
            st.markdown(output, unsafe_allow_html=True)
            st.balloons() # تأثير احتفالي عند النجاح

    except ZeroDivisionError:
        st.error("❌ خطأ في الحسابات، يرجى مراجعة الأرقام.")
