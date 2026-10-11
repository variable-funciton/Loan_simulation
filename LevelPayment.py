import math
import pandas as pd
import streamlit as st


class LoanSimulator:
    """元利均等返済シミュレータ(月次ループで円未満切り捨て)"""

    def __init__(self, annual_rate: float, loan_amount: int, term_year: int):
        self.annual_rate = annual_rate
        self.loan_amount = loan_amount
        self.term_year = term_year
        self.total_months = 12 * term_year
        self.monthly_rate = annual_rate / 12 / 100
        self.monthly_payment = self._calc_monthly_payment()
        self.schedule = self._build_schedule()

    def _calc_monthly_payment(self) -> int:
        """毎月の支払額(円未満切り上げ。最終回で調整するため不足が出ないようにする)"""
        if self.loan_amount == 0:
            return 0
        if self.monthly_rate > 0:
            factor = (1 + self.monthly_rate) ** self.total_months
            payment = self.loan_amount * self.monthly_rate * factor / (factor - 1)
        else:
            payment = self.loan_amount / self.total_months
        return math.ceil(payment)

    def _build_schedule(self) -> pd.DataFrame:
        """月ごとの返済表を作成"""
        rows = []
        balance = self.loan_amount

        for month in range(1, self.total_months + 1):
            interest = math.floor(balance * self.monthly_rate)
            # 最終回は残高+利息を全額支払う
            if month == self.total_months:
                payment = balance + interest
            else:
                payment = min(self.monthly_payment, balance + interest)
            principal = payment - interest
            balance -= principal
            rows.append({
                "回数": month,
                "年": (month - 1) // 12 + 1,
                "支払額": payment,
                "元金": principal,
                "利息": interest,
                "残高": balance,
            })

        return pd.DataFrame(rows)

    @property
    def total_paid(self) -> int:
        return int(self.schedule["支払額"].sum())

    @property
    def total_interest(self) -> int:
        return int(self.schedule["利息"].sum())

    @property
    def final_payment(self) -> int:
        return int(self.schedule["支払額"].iloc[-1])

    def yearly_summary(self) -> pd.DataFrame:
        """年ごとの集計(年末残高つき)"""
        grouped = self.schedule.groupby("年").agg(
            支払額=("支払額", "sum"),
            元金=("元金", "sum"),
            利息=("利息", "sum"),
            年末残高=("残高", "last"),
        )
        return grouped.reset_index()


# ---------------- UI ----------------
st.set_page_config(page_title="ローンシミュレーション", layout="centered")
st.title("元利均等返済シミュレーション")

st.header("情報入力")
loan_amount_man = st.number_input("借入金額(万円)", min_value=0, max_value=100000, value=1000, step=10)
rate = st.number_input("年利(%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1, format="%.2f")
years = st.number_input("借入年数(年)", min_value=1, max_value=50, value=20, step=1)

total_price = loan_amount_man * 10_000

if total_price == 0:
    st.warning("借入金額を1万円以上で入力してください。")
    st.stop()

loan = LoanSimulator(rate, total_price, years)

st.divider()
st.header("計算結果")

c1, c2 = st.columns(2)
c1.metric("毎月の支払額", f"{loan.monthly_payment:,} 円")
c2.metric("最終回の支払額", f"{loan.final_payment:,} 円")

c3, c4 = st.columns(2)
c3.metric("総利息", f"{loan.total_interest:,} 円")
c4.metric("累計支払額", f"{loan.total_paid:,} 円")

st.subheader("残高の推移")
yearly = loan.yearly_summary()
st.line_chart(yearly.set_index("年")["年末残高"])

st.subheader("年別の内訳")
st.dataframe(
    yearly.style.format("{:,}", subset=["支払額", "元金", "利息", "年末残高"]),
    use_container_width=True,
    hide_index=True,
)

with st.expander("月別の返済表を見る"):
    st.dataframe(loan.schedule, use_container_width=True, hide_index=True)

st.caption("※ 概算です。実際の返済額は金融機関の計算方法(端数処理・ボーナス払い等)により異なります。")
