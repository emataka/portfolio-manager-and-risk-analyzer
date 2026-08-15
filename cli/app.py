from cli.backtest_cli import main as run_backtest
from cli.main import main as run_portfolio_manager
from cli.recommend import main as run_recommendation


def show_menu():
    while True:
        print("1. مدیریت پرتفوی")
        print("2. دریافت پیشنهاد")
        print("3. اجرای بک تست")
        print("4. خروج")
        
        choice = input("انتخاب شما: ")
        if choice == "1":
            run_portfolio_manager()
        elif choice == "2":
            run_recommendation()
        elif choice == "3":
            run_backtest()
        elif choice == "4":
            break

if __name__ == "__main__":
    show_menu()
