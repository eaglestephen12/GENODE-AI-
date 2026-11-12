"""Models and validation: honest (cluster-grouped) vs leaky splits, plus controls."""
import numpy as np
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def build_models(seed=0):
    return {
        "majority": DummyClassifier(strategy="most_frequent"),
        "logreg": make_pipeline(StandardScaler(),
                                LogisticRegression(max_iter=3000, class_weight="balanced")),
        "random_forest": RandomForestClassifier(500, class_weight="balanced", n_jobs=-1,
                                                random_state=seed),
    }


def run_cv(model, X, y, splitter, groups=None):
    y_pred = np.empty(len(y), dtype=object)
    fold_f1 = []
    for tr, te in splitter.split(X, y, groups):
        p = clone(model).fit(X[tr], y[tr]).predict(X[te])
        y_pred[te] = p
        fold_f1.append(f1_score(y[te], p, average="macro", zero_division=0))
    y_pred = y_pred.astype(str)
    return {
        "macro_f1": float(f1_score(y, y_pred, average="macro", zero_division=0)),
        "balanced_acc": float(balanced_accuracy_score(y, y_pred)),
        "fold_f1_mean": float(np.mean(fold_f1)),
        "fold_f1_sd": float(np.std(fold_f1)),
    }, y_pred


def choose_splits(y, groups, requested=5):
    """Folds are limited by the genus with the fewest homology clusters."""
    min_clusters = min(len(set(groups[y == c])) for c in set(y))
    return max(2, min(requested, min_clusters))


def evaluate_all(X, y, groups, n_splits, seed=0):
    honest = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    leaky = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    models = build_models(seed)
    results, preds = {}, {}
    for name, m in models.items():
        results[f"{name} | cluster-split (honest)"], preds[name] = run_cv(m, X, y, honest, groups)
    rf = models["random_forest"]
    results["random_forest | random split (leaky)"], _ = run_cv(rf, X, y, leaky)
    y_shuf = np.random.RandomState(seed).permutation(y)
    results["random_forest | shuffled labels (control)"], _ = run_cv(rf, X, y_shuf, honest, groups)
    final_rf = clone(rf).fit(X, y)  # for feature importance only
    return results, preds, final_rf
