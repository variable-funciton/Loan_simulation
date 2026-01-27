
import math
import streamlit as st

class LoanSimulator:
    def __init__(self, annual_rate, loan_amount, term_year):
        self.term_year = term_year
        self.loan_amount = loan_amount
        self.total_months = 12 * term_year
        # 月利 (パーセントを小数に変換)
        self.monthly_rate = annual_rate / 12 / 100
        
        # 毎月の支払額 (元利均等返済の公式)
        # 実務では円未満切り捨てが多いため floor を使用
        if self.monthly_rate > 0:
            numerator = self.loan_amount * self.monthly_rate * ((1 + self.monthly_rate) ** self.total_months)
            denominator = ((1 + self.monthly_rate) ** self.total_months) - 1
            self.monthly_payment = math.floor(numerator / denominator)
        else:
            self.monthly_payment = math.floor(self.loan_amount / self.total_months)

    def remaining_balance(self, year):
        """指定した年数経過後の返済残高を計算"""
        if year > self.term_year:
            return 0
        
        n = year * 12
        r = self.monthly_rate
        # 残高計算式: A*(1+r)^n - P*((1+r)^n - 1)/r
        if r > 0:
            balance = self.loan_amount * ((1 + r) ** n) - self.monthly_payment * (((1 + r) ** n - 1) / r)
        else:
            balance = self.loan_amount - (self.monthly_payment * n)
            
        return max(0, math.floor(balance))

    def total_paid(self, year):
        """指定した年数までの累計支払額"""
        months = min(year * 12, self.total_months)
        return self.monthly_payment * months

st.title("元利均等返済シミュレーション(簡易版)")

# 入力セクション
st.header("情報入力")

col = st.columns(1)
Loan_amount = st.number_input("借入金額(万)", 0, 10000, 100)
Rate = st.number_input("年利(%)", 0.0, 100.0, 3.0)
Years = st.number_input("借入年数", 1, 50, 1)

# 計算ロジック
Total_Price = 10000 * Loan_amount
loan = LoanSimulator(Rate, Total_Price, Years)

# 出力セクション
st.divider()
st.header("計算結果")

st.write(f"**毎月の支払額:** {loan.monthly_payment}円")
st.success(f"**最終的な利息** {loan.total_paid(Years) - Total_Price}円")
st.success(f"**累計支払額:** {loan.total_paid(Years)}円")

