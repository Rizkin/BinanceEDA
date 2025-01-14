import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM
import matplotlib.pyplot as plt


class MarketRegimeAnalyzer:
    def __init__(self, file_path, columns, n_states=3):
        """
        Initialize the MarketRegimeAnalyzer.

        :param file_path: Path to the CSV file containing market data.
        :param columns: List of columns to analyze (must include 'close' and 'volume').
        :param n_states: Number of hidden states for HMM.
        """
        self.file_path = file_path
        self.columns = columns
        self.n_states = n_states
        self.data = None
        self.features = None
        self.hmm_model = None

    def load_data(self):
        """Load and preprocess the data."""
        self.data = pd.read_csv(self.file_path, parse_dates=["timestamp"])

        # Ensure all required columns are present
        for col in self.columns:
            if col not in self.data.columns:
                raise ValueError(f"Column {col} is not found in the dataset.")

        # Calculate log returns
        self.data["log_return"] = np.log(self.data["close"] / self.data["close"].shift(1))

        # Calculate volatility as rolling standard deviation of log returns
        self.data["volatility"] = self.data["log_return"].rolling(window=20).std()

        # Normalize volume
        self.data["normalized_volume"] = self.data["volume"] / self.data["volume"].rolling(window=20).mean()

        # Drop NaN values introduced by rolling calculations
        self.data = self.data.dropna()

        # Prepare features for HMM
        self.features = self.data[["log_return", "volatility", "normalized_volume"]].values

    def train_hmm(self):
        """Train the Gaussian HMM model on the prepared features."""
        self.hmm_model = GaussianHMM(n_components=self.n_states, covariance_type="full", random_state=42)
        self.hmm_model.fit(self.features)

    def predict_regimes(self):
        """Predict market regimes using the trained HMM."""
        self.data["regime"] = self.hmm_model.predict(self.features)

        # Map regimes to descriptive labels
        regime_map = {i: f"Regime {i}" for i in range(self.n_states)}
        self.data["regime_tag"] = self.data["regime"].map(regime_map)

    def visualize_regimes(self):
        """Visualize market regimes on a plot."""
        plt.figure(figsize=(15, 7))
        for regime, group in self.data.groupby("regime"):
            plt.plot(group["timestamp"], group["close"], label=f"Regime {regime}")
        plt.title("Market Regimes Identified by HMM")
        plt.xlabel("Timestamp")
        plt.ylabel("Close Price")
        plt.legend()
        plt.show()

    def save_results(self, output_file):
        """Save the data with regimes to a CSV file."""
        self.data.to_csv(output_file, index=False)
        print(f"Data with regimes saved to {output_file}")
