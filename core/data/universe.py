import pandas as pd

US_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META",  # فناوری
    "TSLA", "WMT", "PG", "KO",                         # مصرفی
    "JNJ", "UNH", "PFE",                                # سلامت
    "JPM", "BAC", "V",                                  # مالی
    "XOM", "CVX",                                       # انرژی
    "BA", "CAT",                                        # صنعتی
    "DIS", "NFLX",                                      # ارتباطات
    "NEE",                                               # انرژی تجدیدپذیر (نوسان کمتر، برای تنوع بیشتر)
]

SP500_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"

def get_us_universe():
    df = pd.read_csv(SP500_URL)
    tickers = df["Symbol"].tolist()
    return [ticker.replace(".", "-") for ticker in tickers]

def get_screened_universe(tickers_per_sector=3, random_seed=42):
    df = pd.read_csv(SP500_URL)
    sampled = df.groupby("GICS Sector").apply(
        lambda group: group.sample(n=min(tickers_per_sector, len(group)), random_state=random_seed),
        include_groups=False,
    )
    tickers = sampled["Symbol"].tolist()
    return [ticker.replace(".", "-") for ticker in tickers]
