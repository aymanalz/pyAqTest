from typing import Callable, Optional, Tuple, Dict
from types import SimpleNamespace
import inspect
import numpy as np
from scipy.stats import linregress
from scipy.optimize import curve_fit, least_squares
import statsmodels.api as sm


class Result(SimpleNamespace):
    """Simple result object with a serializable dict view."""

    def to_dict(self, include_y_pred: bool = True) -> Dict:
        def _to_serializable(obj):
            if isinstance(obj, np.generic):
                return obj.item()
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, SimpleNamespace):
                # Best effort
                return {
                    k: _to_serializable(v)
                    for k, v in obj.__dict__.items()
                }
            if isinstance(obj, dict):
                return {k: _to_serializable(v) for k, v in obj.items()}
            if callable(obj):
                return None
            try:
                # Primitives and iterables
                return obj
            except Exception:
                return None

        data = {}
        for key, value in self.__dict__.items():
            if key in {"predict", "sm_results"}:
                continue
            if key == "y_pred" and not include_y_pred:
                continue
            data[key] = _to_serializable(value)
        return data


def _ensure_contiguous_1d_array(arr):
    """Return a contiguous 1D numpy array without changing values."""
    return np.asarray(arr).reshape(-1)


def _compute_basic_fit_stats(y_obs, y_pred, num_predictors=None, verbose=False):
    """
    Evaluate regression fit statistics
    Parameters:
    - y_obs: array-like, observed values
    - y_pred: array-like, predicted values
    - num_predictors: int, optional. Number of independent variables (for adjusted R²)
    - verbose: bool, print results if True

    Returns:
    - results: dict containing R², adjusted R², RMSE, MAE, MSE, etc.
    """
    y_obs = _ensure_contiguous_1d_array(y_obs)
    y_pred = _ensure_contiguous_1d_array(y_pred)
    n = len(y_obs)

    if n < 2:
        return {
            "R_squared": np.nan, "Adjusted_R_squared": np.nan,
            "RMSE": np.nan, "MAE": np.nan, "MSE": np.nan,
            "SS_res": np.nan, "SS_tot": np.nan,
            "Residual_Mean": np.nan, "Residual_Std": np.nan,
            "num_data": n,
        }
    
    # Residuals and basic stats
    residuals = y_obs - y_pred
    
    # Sum of squares
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_obs - np.mean(y_obs)) ** 2)

    # Metrics
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else np.nan
    mse = ss_res / n
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(residuals))

    # Adjusted R²
    if num_predictors is not None and n > num_predictors + 1:
        adjusted_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - num_predictors - 1)
    else:
        adjusted_r_squared = np.nan

    results = {
        "R_squared": r_squared,
        "Adjusted_R_squared": adjusted_r_squared,
        "RMSE": rmse,
        "MAE": mae,
        "MSE": mse,
        "SS_res": ss_res,
        "SS_tot": ss_tot,
        "Residual_Mean": np.mean(residuals),
        "Residual_Std": np.std(residuals, ddof=1),
        "num_data": n,
    }

    if verbose:
        print(f"R²:           {r_squared:.4f}")
        if num_predictors is not None:
            print(f"Adjusted R²:    {adjusted_r_squared:.4f}")
        print(f"RMSE:         {rmse:.4f}")
        print(f"MAE:          {mae:.4f}")
        print(f"MSE:          {mse:.4f}")
        print(f"Residual Mean:  {results['Residual_Mean']:.4f}")
        print(f"Residual Std:   {results['Residual_Std']:.4f}")

    return results


def _infer_num_params_from_model(model: Callable) -> Optional[int]:
    """
    Infer number of parameters for model(x, *params).
    Returns None if ambiguous.
    """
    try:
        sig = inspect.signature(model)
        params = list(sig.parameters.values())
        if not params:
            return None
        # Exclude the first parameter (x)
        tail = params[1:]
        count = 0
        for p in tail:
            if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                count += 1
            elif p.kind == inspect.Parameter.VAR_POSITIONAL:
                # *args -> cannot infer
                return None
        return count
    except Exception:
        return None


def fit_regression(
    x,
    y,
    method: str = 'linear',
    model: Optional[Callable] = None,
    p0: Optional[Tuple[float, ...]] = None,
    bounds: Optional[Tuple] = None,
    robust_method: Optional[str] = None,
    loss: str = 'linear',
    f_scale: float = 1.0,
    max_nfev: Optional[int] = None,
):
    """
    Fit linear or non-linear models to data with optional robust loss.

    Parameters:
    - x, y: array-like data.
    - method: 'linear' for linear models, 'nonlinear' for generic models.
    - model: callable like f(x, *params) for non-linear fitting.
    - p0: initial parameter guesses for non-linear fitting.
    - bounds: parameter bounds for non-linear fitting; default (-inf, inf).
    - robust_method: None (for OLS), 'huber', or 'tukey' for robust linear
      fitting; for non-linear, uses least_squares with specified loss.
    - loss: least_squares loss: 'linear'|'soft_l1'|'huber'|'cauchy'|'arctan'.
      Only used for non-linear robust fitting.
    - f_scale: scaling for robust loss in least_squares.
    - max_nfev: max function evaluations (least_squares) / maxfev (curve_fit).

    Returns:
    - SimpleNamespace with fields including:
        params, predict(x_new), y_pred, stats (R_squared, RMSE, ...),
        and additional method-specific fields.
    """
    x = _ensure_contiguous_1d_array(x)
    y = _ensure_contiguous_1d_array(y)

    if x.size != y.size or x.size < 2:
        return Result(
            success=False,
            message="Input arrays must have the same size and at least 2 elements.",
            stats=_compute_basic_fit_stats([], []),
            params=np.array([]),
            y_pred=np.array([]),
            predict=lambda x_new: np.array([]),
        )

    # Handle linear cases
    if method == 'linear':
        if robust_method:
            try:
                X = sm.add_constant(x)
                if robust_method == 'tukey':
                    norm = sm.robust.norms.TukeyT()
                    used_method = 'rlm_tukey'
                else:
                    norm = sm.robust.norms.HuberT()
                    used_method = 'rlm_huber'
                rlm = sm.RLM(y, X, M=norm)
                rres = rlm.fit()
                intercept, slope = float(rres.params[0]), float(rres.params[1])
                y_pred = intercept + slope * x
                stats = _compute_basic_fit_stats(y, y_pred, num_predictors=1)
                return Result(
                    method=used_method,
                    params=np.array([intercept, slope], dtype=float),
                    intercept=intercept,
                    slope=slope,
                    sm_results=rres,
                    predict=lambda x_new: intercept + slope * np.asarray(x_new),
                    y_pred=y_pred,
                    stats=stats,
                    success=True,
                    message="Fit successful."
                )
            except Exception as e:
                return Result(
                    success=False,
                    message=f"RLM fit failed: {e}",
                    stats=_compute_basic_fit_stats([], []),
                    params=np.array([]),
                    y_pred=np.array([]),
                    predict=lambda x_new: np.array([]),
                )
        else: # OLS using scipy.linregress
            try:
                lr = linregress(x, y)
                y_pred = lr.slope * x + lr.intercept
                stats = _compute_basic_fit_stats(y, y_pred, num_predictors=1)
                return Result(
                    method='linear_scipy',
                    params=np.array([lr.intercept, lr.slope], dtype=float),
                    intercept=float(lr.intercept),
                    slope=float(lr.slope),
                    rvalue=float(lr.rvalue),
                    pvalue=float(lr.pvalue),
                    stderr=float(lr.stderr) if lr.stderr is not None else np.nan,
                    intercept_stderr=float(lr.intercept_stderr) if hasattr(lr, 'intercept_stderr') else np.nan,
                    predict=lambda x_new: float(lr.intercept) + float(lr.slope) * np.asarray(x_new),
                    y_pred=y_pred,
                    stats=stats,
                    success=True,
                    message="Fit successful."
                )
            except Exception as e:
                return Result(
                    success=False,
                    message=f"Linregress fit failed: {e}",
                    stats=_compute_basic_fit_stats([], []),
                    params=np.array([]),
                    y_pred=np.array([]),
                    predict=lambda x_new: np.array([]),
                )

    # Handle non-linear cases
    elif method == 'nonlinear':
        if model is None:
            return Result(
                success=False,
                message="Non-linear fitting requires a 'model' callable.",
                stats=_compute_basic_fit_stats([], []),
                params=np.array([]),
                y_pred=np.array([]),
                predict=lambda x_new: np.array([]),
            )

        # Guess p0 if not provided
        if p0 is None:
            n_params = _infer_num_params_from_model(model)
            if n_params is None:
                return Result(
                    success=False,
                    message="p0 must be provided when model parameters cannot be inferred.",
                    stats=_compute_basic_fit_stats([], []),
                    params=np.array([]),
                    y_pred=np.array([]),
                    predict=lambda x_new: np.array([]),
                )
            p0 = np.ones(n_params, dtype=float)
        p0 = np.asarray(p0, dtype=float)

        if bounds is None:
            bounds = (-np.inf, np.inf)

        # Robust or custom loss -> least_squares
        if robust_method is not None or (loss is not None and loss != 'linear'):
            try:
                def residual_fn(p):
                    return y - np.asarray(model(x, *p))

                lsq = least_squares(
                    residual_fn, x0=p0, bounds=bounds,
                    loss=robust_method if robust_method else loss,
                    f_scale=f_scale, max_nfev=max_nfev
                )
                params = lsq.x
                y_pred = np.asarray(model(x, *params))
                num_params = len(params)
                stats = _compute_basic_fit_stats(y, y_pred, num_predictors=num_params)

                # Approximate covariance from Jacobian
                try:
                    dof = max(len(x) - num_params, 1)
                    J = lsq.jac
                    JTJ = J.T @ J
                    s_sq = 2 * lsq.cost / dof
                    cov = s_sq * np.linalg.inv(JTJ)
                except Exception:
                    cov = np.full((num_params, num_params), np.nan, dtype=float)

                return Result(
                    method='nonlinear_least_squares',
                    params=params,
                    pcov=cov,
                    success=bool(lsq.success),
                    message=str(lsq.message),
                    cost=float(lsq.cost),
                    residuals=lsq.fun,
                    predict=lambda x_new: np.asarray(model(np.asarray(x_new), *params)),
                    y_pred=y_pred,
                    stats=stats,
                )
            except Exception as e:
                return Result(
                    success=False,
                    message=f"Least squares fit failed: {e}",
                    stats=_compute_basic_fit_stats([], []),
                    params=np.array([]),
                    y_pred=np.array([]),
                    predict=lambda x_new: np.array([]),
                )
        # Default non-robust -> curve_fit
        else:
            try:
                popt, pcov = curve_fit(model, x, y, p0=p0, bounds=bounds) 
                y_pred = np.asarray(model(x, *popt))
                num_params = len(popt)
                stats = _compute_basic_fit_stats(y, y_pred, num_predictors=num_params)
                
                return Result(
                    method='nonlinear_curve_fit',
                    params=popt,
                    pcov=pcov,
                    success=True,
                    message="Fit successful.",
                    predict=lambda x_new: np.asarray(model(np.asarray(x_new), *popt)),
                    y_pred=y_pred,
                    stats=stats,
                )
            except Exception as e:
                return Result(
                    success=False,
                    message=f"Curve fit failed: {e}",
                    stats=_compute_basic_fit_stats([], []),
                    params=np.array([]),
                    y_pred=np.array([]),
                    predict=lambda x_new: np.array([]),
                )

    else:
        return Result(
            success=False,
            message="Invalid 'method' specified. Choose 'linear' or 'nonlinear'.",
            stats=_compute_basic_fit_stats([], []),
            params=np.array([]),
            y_pred=np.array([]),
            predict=lambda x_new: np.array([]),
        )