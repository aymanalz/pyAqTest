import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 1. Generate synthetic data
np.random.seed(42)
X = np.linspace(1, 100, 50).reshape(-1, 1)

# Base exponential decay (linear on log scale)
true_slope = -0.05
true_intercept_log = np.log(1) # Start near 1 on the y-axis
y_log_true = true_intercept_log + true_slope * X.flatten()

# Add log-normal noise (additive noise on the log scale)
noise = np.random.normal(0, 0.2, X.shape[0])
y_log = y_log_true + noise

# Convert back to linear scale
y = np.exp(y_log)

# 2. Introduce outliers (points with high leverage that pull the line down)
outlier_indices = [5, 10, 15]
y[outlier_indices] = [0.0001, 0.005, 0.00005] # Very low values to pull OLS

# Ensure y is within the specified range (though it should be by design)
y = np.clip(y, 0.00001, 1)

# 3. Fit standard OLS (sensitive to outliers)
ols = LinearRegression()
ols.fit(X, np.log(y))
ols_pred_log = ols.predict(X)
ols_pred = np.exp(ols_pred_log)

# 4. Define the 'Robust' line (close to the true underlying relationship, ignoring outliers)
# For illustration, we'll use the true underlying parameters as the "robust" fit
robust_pred_log = true_intercept_log + true_slope * X.flatten()
robust_pred = np.exp(robust_pred_log)

# 5. Plotting
plt.figure(figsize=(6, 6))

# Scatter plot of the data - now green!
plt.scatter(X, y, label='Slug Test Data (with Outliers)', color='green', alpha=0.7)

# Plot OLS Regression Line (pulled down by outliers)
plt.plot(X, ols_pred, color='red', linestyle='--', linewidth=2, label='OLS Regression (Sensitive to Outliers)')

# Plot Robust Regression Line (representing the underlying trend)
plt.plot(X, robust_pred, color='blue', linestyle='-', linewidth=3, label='Robust Regression (Ignores Outliers)')

# 6. Apply user-requested modifications
plt.yscale('log')
plt.ylim(0.00001, 1) # Set y-axis range
plt.ylabel(r'$H/H_0$') # Use LaTeX for H/H0
plt.xlabel('Time')
plt.title(' Illustration of Robust Regression')
plt.legend()
plt.grid(True, which="both", ls="--", c='0.7')
plt.tight_layout()

# Save the plot
plot_filename = "robust_regression_log_scale_negative_slope_green_dots.png"
plt.savefig(plot_filename)
print(plot_filename)