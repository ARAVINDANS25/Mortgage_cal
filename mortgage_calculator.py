import streamlit as st
import pandas as pd
import math

def calculate_monthly_payment(loan_amount, monthly_interest_rate, number_of_payments):
    if monthly_interest_rate == 0:  # Edge case for 0% interest
        return loan_amount / number_of_payments
    return (
        loan_amount
        * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
        / ((1 + monthly_interest_rate) ** number_of_payments - 1)
    )

def generate_payment_schedule(loan_amount, monthly_payment, monthly_interest_rate, number_of_payments):
    schedule = []
    remaining_balance = loan_amount

    for i in range(1, number_of_payments + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        year = math.ceil(i / 12)  # Calculate the year into the loan
        schedule.append(
            [
                i,
                monthly_payment,
                principal_payment,
                interest_payment,
                remaining_balance,
                year,
            ]
        )

    df = pd.DataFrame(
        schedule,
        columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance", "Year"],
    )
    return df

def calculate_arm_schedule(home_value, deposit, arm_periods):
    loan_amount = home_value - deposit
    schedule = []
    remaining_balance = loan_amount

    month = 1
    for period in arm_periods:
        interest_rate, years = period
        monthly_interest_rate = (interest_rate / 100) / 12
        number_of_payments = years * 12
        monthly_payment = calculate_monthly_payment(remaining_balance, monthly_interest_rate, number_of_payments)
        
        for i in range(1, number_of_payments + 1):
            interest_payment = remaining_balance * monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment
            year = math.ceil(month / 12)  # Calculate the year into the loan
            schedule.append(
                [
                    month,
                    monthly_payment,
                    principal_payment,
                    interest_payment,
                    remaining_balance,
                    year,
                ]
            )
            month += 1

    df = pd.DataFrame(
        schedule,
        columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance", "Year"],
    )
    return df

def main():
    st.title("Mortgage Repayments Calculator")

    st.write("### Input Data")
    mortgage_type = st.radio("Select Mortgage Type", ("Fixed Rate Mortgage (FRM)", "Adjustable Rate Mortgage (ARM)"))

    col1, col2 = st.columns(2)
    home_value = col1.number_input("Home Value ($)", min_value=0, value=500000, step=1000)
    deposit = col1.number_input("Deposit ($)", min_value=0, value=100000, step=1000)

    if mortgage_type == "Fixed Rate Mortgage (FRM)":
        interest_rate = col2.number_input("Interest Rate (%)", min_value=0.0, value=5.0, step=0.1)
        loan_term = col2.number_input("Loan Term (years)", min_value=1, value=30)

        if home_value <= deposit:
            st.error("Deposit cannot exceed or equal home value.")
            return

        loan_amount = home_value - deposit
        monthly_payment = calculate_monthly_payment(loan_amount, (interest_rate / 100) / 12, loan_term * 12)

        total_payments = monthly_payment * loan_term * 12
        total_interest = total_payments - loan_amount

        st.write("### Repayments")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="Monthly Repayments", value=f"${monthly_payment:,.2f}")
        col2.metric(label="Total Repayments", value=f"${total_payments:,.0f}")
        col3.metric(label="Total Interest", value=f"${total_interest:,.0f}")
        col4.metric(label="Loan Amount", value=f"${loan_amount:,.0f}")

        df = generate_payment_schedule(loan_amount, monthly_payment, (interest_rate / 100) / 12, loan_term * 12)

        st.write("### Payment Schedule")
        payments_df = df[["Year", "Remaining Balance"]].groupby("Year").min()
        st.line_chart(payments_df)

    elif mortgage_type == "Adjustable Rate Mortgage (ARM)":
        arm_periods = []
        num_periods = st.number_input("Number of ARM Periods", min_value=1, value=1, step=1)

        for i in range(num_periods):
            st.write(f"### ARM Period {i + 1}")
            interest_rate = st.number_input(f"Interest Rate for Period {i + 1} (%)", min_value=0.0, value=5.0, step=0.1, key=f"arm_rate_{i}")
            period_years = st.number_input(f"Years for Period {i + 1}", min_value=1, value=5, step=1, key=f"arm_years_{i}")
            arm_periods.append((interest_rate, period_years))

        if home_value <= deposit:
            st.error("Deposit cannot exceed or equal home value.")
            return

        df = calculate_arm_schedule(home_value, deposit, arm_periods)

        total_payments = df["Payment"].sum()
        total_interest = df["Interest"].sum()

        st.write("### Repayments")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="Monthly Repayments", value=f"${df.iloc[0]['Payment']:,.2f}")
        col2.metric(label="Total Repayments", value=f"${total_payments:,.0f}")
        col3.metric(label="Total Interest", value=f"${total_interest:,.0f}")
        col4.metric(label="Loan Amount", value=f"${home_value - deposit:,.0f}")

        st.write("### Payment Schedule")
        payments_df = df[["Year", "Remaining Balance"]].groupby("Year").min()
        st.line_chart(payments_df)

if __name__ == "__main__":
    main()
