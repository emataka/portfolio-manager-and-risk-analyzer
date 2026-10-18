from cli.backtest_cli import main as run_backtest
from cli.main import main as run_portfolio_manager
from cli.portfolio_storage_cli import manage_portfolio_storage
from cli.recommend import main as run_recommendation
from cli.transactions_cli import manage_transactions
from core.models.portfolio import Portfolio


def show_menu():
    portfolio = None
    while True:
        print("1. مدیریت پرتفوی")
        print("2. دریافت پیشنهاد")
        print("3. اجرای بک تست")
        print("4. ذخیره/بارگذاری پرتفوی")
        print("5. دفتر معاملات")
        print("6. خروج")
        
        choice = input("انتخاب شما: ")
        if choice == "1":
            portfolio = run_portfolio_manager(portfolio)
        elif choice == "2":
            run_recommendation()
        elif choice == "3":
            run_backtest()
        elif choice == "4":
            portfolio = manage_portfolio_storage(portfolio)
        elif choice == "5":
            if portfolio is None:
                portfolio = Portfolio()
            portfolio = manage_transactions(portfolio)
        elif choice == "6":
            break

if __name__ == "__main__":
    show_menu()
