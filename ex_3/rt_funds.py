import yfinance as yf
import matplotlib.pyplot as plt

def fetch_stock_data():
    data = yf.Ticker("INFY.NS").history(period="10d")
    data['Close'].plot(title="INFY – Last 10 Days")
    plt.xlabel("Date")
    plt.ylabel("Close Price (₹)")
    plt.tight_layout()
    plt.show()
