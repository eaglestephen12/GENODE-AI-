"""Presentation-ready figures."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.metrics import confusion_matrix  # noqa: E402

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
TEAL, DARK, GREY, WARM = "#2bb5a0", "#0b7a75", "#9aa5b1", "#e07a5f"


def fig_validation(results, chance, path):
    keys = ["majority | cluster-split (honest)", "logreg | cluster-split (honest)",
            "random_forest | cluster-split (honest)", "random_forest | random split (leaky)",
            "random_forest | shuffled labels (control)"]
    labels = ["Majority\nbaseline", "LogReg\n(honest)", "Random forest\n(honest)",
              "Random forest\n(leaky split)", "Shuffled-label\ncontrol"]
    vals = [results[k]["macro_f1"] for k in keys]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(labels, vals, color=[GREY, TEAL, DARK, WARM, GREY])
    ax.axhline(chance, ls="--", c="k", lw=1)
    ax.text(4.45, chance + 0.01, "chance", ha="right", fontsize=9)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}", ha="center")
    ax.set_ylabel("Macro-F1")
    ax.set_ylim(0, 1.05)
    ax.set_title("Phage host-genus prediction: honest vs leaky validation")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def fig_confusion(y, y_pred, classes, path):
    cm = confusion_matrix(y, y_pred, labels=classes, normalize="true")
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(cm, cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(classes)), classes, rotation=45, ha="right")
    ax.set_yticks(range(len(classes)), classes)
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, f"{cm[i, j]:.2f}", ha="center", va="center",
                    color="w" if cm[i, j] < 0.6 else "k", fontsize=9)
    ax.set_xlabel("Predicted host genus")
    ax.set_ylabel("True host genus")
    ax.set_title("Random forest, cluster-split CV (row-normalised)")
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def fig_importance(rf, names, path, top=15):
    order = np.argsort(rf.feature_importances_)[::-1][:top]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.barh([names[i] for i in order][::-1], rf.feature_importances_[order][::-1], color=DARK)
    ax.set_xlabel("Importance")
    ax.set_title("Most informative features")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return [[names[i], float(rf.feature_importances_[i])] for i in order]
