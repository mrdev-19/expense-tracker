import streamlit as st
from streamlit_option_menu import option_menu
import backend as db
import validations as val
import time
import send_mail as sm
import hasher as hs
import matplotlib.pyplot as plt
import pandas as pd

#---------------------------------------------------
# page config settings:

page_title="Expense Tracker"
page_icon=":dollar:"
layout="centered"

st.set_page_config(page_title=page_title,page_icon=page_icon,layout=layout)
st.title(page_title+" "+page_icon)

#--------------------------------------------------
#hide the header and footer     

hide_ele="""
        <style>
        #Mainmenu {visibility:hidden;}
        footer {visibility:hidden;}
        header {visibility:hidden;}
        </style>
        """
st.markdown(hide_ele,unsafe_allow_html=True)
#---------------------------------------------------
curlogin=""
otp=""

def log_sign():
    selected=option_menu(
        menu_title=None,
        options=["Login","Signup"],
        icons=["bi bi-fingerprint","bi bi-pencil-square"],
        orientation="horizontal"
    )
    global submit
    if(selected=="Login"):
        tab1,tab2=st.tabs(["Login","Forgot Password"])
        with tab1:
            with st.form("Login",clear_on_submit=True):
                st.header("Login")
                username=st.text_input("Username")
                password=st.text_input("Password",type="password")
                submit=st.form_submit_button()
                if(submit):
                    if(username=="" or password==""):
                        st.warning("Enter your login credentials")
                    else:
                        password=hs.hasher(password)
                        if(db.authenticate(username,password)):
                            st.session_state["curlogin"]=username
                            st.session_state["key"]="main"
                            st.experimental_rerun()
                        else:
                            st.error("Please check your username / password ")
        with tab2:
            with st.form("Forgot Password",clear_on_submit=True):
                st.header("Forgot Password")
                email=st.text_input("Email")
                submit=st.form_submit_button()
                if(submit):
                    if(email==""):
                        st.warning("Enter your email")
                    elif(not db.emailexists(email)):
                        st.warning("User with associated email is not found,kindly recheck the email!")
                    else:
                        otp=sm.forgot_password(email)
                        db.forgot_pass(email,otp)
                        st.success("Check your email for password reset instructions!.")
                
    elif(selected=="Signup"):
         with st.form("Sign Up",clear_on_submit=False):
            st.header("Sign Up")
            email=st.text_input("Enter your email")
            number=st.text_input("Enter your Mobile Number")
            username=st.text_input("Enter your username")
            password=st.text_input("Enter your password",type="password")
            submit=st.form_submit_button()
            if(submit):
                var=True
                emails=db.get_all_emails()
                numbers=db.get_all_numbers()
                usernames=db.get_all_usernames()
                if(db.check_user_existence(username,email,number)):
                   var=False
                if(val.validate_email(email)==False):
                    st.error("Enter email in a valid format like 'yourname@org.com'")
                elif(email in emails):
                    st.error("email already exists!\nTry with another email !")
                elif(val.validate_mobile(number)==False):
                    st.error("Please Check your mobile Number")
                elif(number in numbers):
                    st.error("Phone number already exists\nTry with another number")
                elif(val.validate_username(username)==False):
                    st.error("Invalid Username!\nUsername must be between 4-20 characters and can contain only _ and . , and username cannot begin with special characters")
                elif(username in usernames):
                    st.error("Username already exists!\nTry another username !")
                elif(val.validate_password(password)==False):
                    st.error("Password must be between 6-20 characters in length and must have at least one Uppercase Letter , Lowercase letter , numeric character and A Special Symbol(#,@,$,%,^,&,+,=)")
                elif(var):
                    password=hs.hasher(password)
                    db.insert_user(username,password,email,number)
                    st.success("Signed Up Successfully....Redirecting!!")
                    time.sleep(2)
                    st.session_state["curlogin"]=username
                    st.session_state["key"]="main"
                    st.experimental_rerun()
    
def main():
    btn=st.button("Logout")
    if(btn):
        st.session_state["key"] = "log_sign"
        st.experimental_rerun()
    selected=option_menu(
            menu_title=None,
            options=["Manage Expenses","View Spendings"],
            icons=["bi bi-search","bi bi-box"],
            orientation="horizontal"
        )
    if selected=="Manage Expenses":
            st.header("Budget Remaining : "+str(db.get_budget(st.session_state["curlogin"])[0]))
            if(int(db.get_budget(st.session_state["curlogin"])[0])<int(db.get_budget(st.session_state["curlogin"])[1])):
                st.error("Budget is less than your st threshold")
            else:
                st.success("You are in the safe zone now")
            tab1,tab2=st.tabs(["Expense","Revenue"])
            with tab1:    
                with st.form("expense_input",clear_on_submit=True):
                    st.header("Expense")
                    date=st.date_input("Enter the date of the expense")
                    reason=st.text_input("Enter the reason for spending",placeholder="Canteen , Records etc.")
                    amount=st.text_input("Amount in Rupees?",placeholder="1000 etc..")
                    submitted=st.form_submit_button("Submit")
                    if(submitted):
                        if(db.get_budget(st.session_state["curlogin"])[0]>=int(amount)):
                            db.insert_expense(st.session_state["curlogin"],date.strftime("%d/%m/%Y"),reason,int(amount))

            with tab2:
                with st.form("revenue_input",clear_on_submit=True):
                    st.header("Revenue")
                    date=st.date_input("Enter the date of the revenue")
                    reason=st.text_input("Enter the source of revenue",placeholder="Allowance , Pocket Money etc.")
                    amount=st.text_input("Amount in Rupees?",placeholder="1000 etc..")
                    submitted=st.form_submit_button("Submit")
                    if(submitted):
                        db.insert_revenue(st.session_state["curlogin"],date.strftime("%d/%m/%Y"),reason,int(amount))
            with st.form("Update threshold",clear_on_submit=True):
                st.write("Update Threshold value")
                threshold=st.text_input("Enter the new threshold")
                sub=st.form_submit_button("Submit")
                if(sub):
                    if(int(threshold)>int(db.get_budget(st.session_state["curlogin"])[0])):
                        st.error("Threshold cannot be greater than budget")
                    else:
                        db.set_budget(st.session_state["curlogin"],db.get_budget(st.session_state["curlogin"])[0],int(threshold))


    else:
        def plot_bar_charts(expenses, revenues):
            if expenses and len(expenses) > 0:
                df_expenses = pd.DataFrame(expenses, columns=["Date", "Reason", "Amount"])
                df_expenses = df_expenses.sort_values(by="Date")
                st.subheader("Expense Data:")
                st.dataframe(df_expenses)
                fig, ax1 = plt.subplots()
                ax1.bar(df_expenses["Date"], df_expenses["Amount"], color='red', alpha=0.7)
                ax1.set_xlabel('Date')
                ax1.set_ylabel('Amount Spent', color='red')
                ax1.tick_params('y', colors='red')
                ax1.set_title("Expense Overview")
                plt.xticks(rotation=45)
                st.pyplot(fig)
                fig, ax3 = plt.subplots()
                expense_reasons = df_expenses.groupby("Reason").sum()["Amount"]
                ax3.pie(expense_reasons, labels=expense_reasons.index, autopct='%1.1f%%', startangle=90)
                ax3.axis('equal') 
                ax3.set_title("Expense Distribution by Reasons")
                st.pyplot(fig)

            if revenues and len(revenues) > 0:
                df_revenues = pd.DataFrame(revenues, columns=["Date", "Reason", "Amount"])
                df_revenues = df_revenues.sort_values(by="Date")

                st.subheader("Revenue Data:")
                st.dataframe(df_revenues)

                fig, ax2 = plt.subplots()
                ax2.bar(df_revenues["Date"], df_revenues["Amount"], color='green', alpha=0.7)
                ax2.set_xlabel('Date')
                ax2.set_ylabel('Amount Received', color='green')
                ax2.tick_params('y', colors='green')
                ax2.set_title("Revenue Overview")
                plt.xticks(rotation=45)
                st.pyplot(fig)
                fig, ax4 = plt.subplots()
                revenue_reasons = df_revenues.groupby("Reason").sum()["Amount"]
                ax4.pie(revenue_reasons, labels=revenue_reasons.index, autopct='%1.1f%%', startangle=90)
                ax4.axis('equal') 
                ax4.set_title("Revenue Distribution by Reasons")
                st.pyplot(fig)
        expenses, revenues = db.get_user_transactions(st.session_state["curlogin"])
        plot_bar_charts(expenses, revenues)

if "key" not in st.session_state:
    st.session_state["key"] = "log_sign"

if st.session_state["key"] == "log_sign":
    log_sign()

elif st.session_state["key"] == "main":
    main()