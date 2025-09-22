# I need a function that fit a different regression models to the data,
# including robust regression models
from typing import Callable, Optional, Tuple
from types import SimpleNamespace
import inspect
import numpy as np
from scipy.stats import linregress
from scipy.optimize import curve_fit, least_squares
import statsmodels.api as sm


def _ensure_1d_array(arr):
    """Return a contiguous 1D numpy array without changing values."""
    return np.asarray(arr).reshape(-1)


def _compute_basic_fit_stats(y_obs: np.ndarray, y_pred: np.ndarray) -> dict:
    y_obs = _ensure_1d_array(y_obs)
    y_pred = _ensure_1d_array(y_pred)
    residuals = y_obs - y_pred
    n = y_obs.size
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((y_obs - float(np.mean(y_obs))) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    mse = ss_res / n if n > 0 else np.nan
    rmse = float(np.sqrt(mse)) if np.isfinite(mse) else np.nan
    return {
        "residuals": residuals,
        "R_squared": float(r_squared),
        "RMSE": rmse,
        "MSE": float(mse) if np.isfinite(mse) else np.nan,
        "SS_res": ss_res,
        "SS_tot": ss_tot,
        "num_data": int(n),
    }


def _infer_num_params_from_model(model: Callable) -> Optional[int]:
    """
    Infer number of parameters for model(x, *params).
    Returns None if ambiguous.
    """
    try:
        sig = inspect.signature(model)
        # Expect first parameter to be x, rest are params (positional only or
        # positional-or-keyword)
        params = list(sig.parameters.values())
        if not params:
            return None
        # Exclude the first parameter (x)
        tail = params[1:]
        # Count only positional parameters; stop at VAR_POSITIONAL (e.g.,
        # *args) which implies unknown
        count = 0
        for p in tail:
            if p.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            ):
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
    robust: bool = False,
    loss: str = 'linear',
    f_scale: float = 1.0,
    max_nfev: Optional[int] = None,
):
    """
    Fit linear or non-linear models to data with optional robust loss.

    Parameters:
    - x, y: array-like data.
    - method: 'linear'|'scipy'|'Huber'|'Tukey' for linear;
      'nonlinear'|'curve_fit'|'least_squares' for generic models.
    - model: callable like f(x, *params) for non-linear fitting.
    - p0: initial parameter guesses for non-linear fitting.
    - bounds: parameter bounds for non-linear fitting; default (-inf, inf).
    - robust: if True, use robust loss (least_squares) for non-linear;
      for linear, uses RLM.
    - loss: least_squares loss: 'linear'|'soft_l1'|'huber'|'cauchy'|'arctan'.
    - f_scale: scaling for robust loss in least_squares.
    - max_nfev: max function evaluations (least_squares) / maxfev
      (curve_fit).

    Returns:
    - SimpleNamespace with fields depending on method, always including at
      least:
        params, predict(x_new), y_pred, stats (R_squared, RMSE, ...)
      For linear (scipy), also includes slope, intercept, rvalue, pvalue,
      stderr.
    """

    x = _ensure_1d_array(x)
    y = _ensure_1d_array(y)

    # Handle linear cases (default)
    linear_aliases = {'linear', 'scipy', 'ols'}
    if (
        model is None
        and (
            method in linear_aliases
            or method in {'Huber', 'Tukey'}
            or not (method and method.startswith('non'))
        )
    ):
        if method in {'Huber', 'Tukey'} or robust:
            # Robust linear model with intercept
            X = x.reshape(-1, 1)
            X = sm.add_constant(X, has_constant='add')
            if method == 'Tukey':
                norm = sm.robust.norms.TukeyT()
                used_method = 'rlm_tukey'
            else:
                # Default to Huber for robust
                norm = sm.robust.norms.HuberT()
                used_method = 'rlm_huber'
            rlm = sm.RLM(y, X, M=norm)
            rres = rlm.fit()
            intercept, slope = float(rres.params[0]), float(rres.params[1])
            y_pred = intercept + slope * x
            stats = _compute_basic_fit_stats(y, y_pred)
            return SimpleNamespace(
                method=used_method,
                params=np.array([intercept, slope], dtype=float),
                intercept=intercept,
                slope=slope,
                sm_results=rres,
                predict=(
                    lambda x_new: float(intercept)
                    + float(slope) * np.asarray(x_new)
                ),
                y_pred=y_pred,
                stats=stats,
            )
        else:
            lr = linregress(x, y)
            y_pred = lr.slope * x + lr.intercept
            stats = _compute_basic_fit_stats(y, y_pred)
            return SimpleNamespace(
                method='linear_scipy',
                params=np.array([lr.intercept, lr.slope], dtype=float),
                intercept=float(lr.intercept),
                slope=float(lr.slope),
                rvalue=float(lr.rvalue),
                pvalue=float(lr.pvalue),
                stderr=(
                    float(lr.stderr) if lr.stderr is not None else np.nan
                ),
                intercept_stderr=(
                    float(lr.intercept_stderr)
                    if hasattr(lr, 'intercept_stderr')
                    else np.nan
                ),
                predict=(
                    lambda x_new: float(lr.intercept)
                    + float(lr.slope) * np.asarray(x_new)
                ),
                y_pred=y_pred,
                stats=stats,
            )

    # Non-linear cases require a model
    if model is None:
        raise ValueError(
            "Non-linear fitting requested but no model was provided."
        )

    if bounds is None:
        bounds = (-np.inf, np.inf)

    # Guess p0 if not provided
    if p0 is None:
        n_params = _infer_num_params_from_model(model)
        if n_params is None:
            raise ValueError(
                "p0 must be provided when the number of model parameters "
                "cannot be inferred."
            )
        p0 = np.ones(n_params, dtype=float)
    p0 = np.asarray(p0, dtype=float)

    # Robust or custom loss -> least_squares
    if (
        robust
        or (loss is not None and loss != 'linear')
        or method in {'least_squares', 'nonlinear'}
    ):
        def residual_fn(p):
            return y - np.asarray(model(x, *p))

        lsq = least_squares(
            residual_fn,
            x0=p0,
            bounds=bounds,
            loss=loss if loss else 'linear',
            f_scale=f_scale,
            max_nfev=max_nfev,
        )
        params = lsq.x
        y_pred = np.asarray(model(x, *params))

        # Approximate covariance from Jacobian
        try:
            n = x.size
            m = params.size
            dof = max(n - m, 1)
            J = lsq.jac
            JTJ = J.T @ J
            # lsq.cost = 0.5 * sum(residuals**2)
            s_sq = 2 * lsq.cost / dof
            cov = s_sq * np.linalg.inv(JTJ)
        except Exception:
            cov = np.full((params.size, params.size), np.nan, dtype=float)

        stats = _compute_basic_fit_stats(y, y_pred)
        return SimpleNamespace(
            method='nonlinear_least_squares',
            params=params,
            pcov=cov,
            success=bool(lsq.success),
            message=str(lsq.message),
            cost=float(lsq.cost),
            residuals=lsq.fun,
            predict=(
                lambda x_new: np.asarray(
                    model(np.asarray(x_new), *params)
                )
            ),
            y_pred=y_pred,
            stats=stats,
        )

    # Default non-robust -> curve_fit
    popt, pcov = curve_fit(
        model,
        x,
        y,
        p0=p0,
        bounds=bounds,
        maxfev=max_nfev,
    )
    y_pred = np.asarray(model(x, *popt))
    stats = _compute_basic_fit_stats(y, y_pred)
    return SimpleNamespace(
        method='nonlinear_curve_fit',
        params=popt,
        pcov=pcov,
        predict=(
            lambda x_new: np.asarray(
                model(np.asarray(x_new), *popt)
            )
        ),
        y_pred=y_pred,
        stats=stats,
    )
