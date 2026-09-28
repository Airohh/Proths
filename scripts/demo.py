"""Démo de la boucle complète, hors Docker, sur de vraies données AG News.

Démarrage à froid : le premier champion n'a vu que 5 000 articles. Le trafic est
d'abord équilibré, puis 70 % Sports. Les vrais labels reviennent par /feedback.
Le monitor détecte le drift, réentraîne sur base + feedback, et le holdout décide.

    python scripts/prepare_ag_news.py   # une fois
    python scripts/demo.py              # -> reports/demo.json, reports/demo.png

Tout est isolé dans data/demo/ et mlruns/demo.db : le registry normal n'est pas touché.
"""

import argparse
import json
import os
import shutil
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

DEMO_DIR = ROOT / "data" / "demo"


def _isolate() -> None:
    """Environnement dédié, à fixer AVANT de lire la config."""
    if DEMO_DIR.exists():
        shutil.rmtree(DEMO_DIR)
    (DEMO_DIR / "processed").mkdir(parents=True)
    db = ROOT / "mlruns" / "demo.db"
    db.unlink(missing_ok=True)
    os.environ.update(
        {
            "DATA_DIR": str(DEMO_DIR / "processed"),
            "PREDICTIONS_DB": str(DEMO_DIR / "predictions.db"),
            "MLFLOW_TRACKING_URI": f"sqlite:///{db}",
            "MODEL_POLL_SECONDS": "0",
            "RETRAIN_COOLDOWN": "0",
            "API_RELOAD_URL": "http://127.0.0.1:9/unused",  # l'API est rechargée ici même
            "GIT_PYTHON_REFRESH": "quiet",
            "LOG_LEVEL": "WARNING",
        }
    )


def run(initial_size: int, steps_balanced: int, steps_skewed: int, per_step: int) -> list[dict]:
    import pandas as pd
    from fastapi.testclient import TestClient

    from scripts.simulate_traffic import run_traffic
    from src import data, registry
    from src.inference import api
    from src.inference.store import PredictionStore
    from src.monitoring.monitor import Monitor
    from src.training.train import train_and_register

    source = ROOT / "data" / "processed"
    train = data.stratified_sample(pd.read_csv(source / "train.csv"), initial_size, 42)
    train.to_csv(DEMO_DIR / "processed" / "train.csv", index=False)
    for name in ("holdout", "stream"):
        shutil.copy(source / f"{name}.csv", DEMO_DIR / "processed" / f"{name}.csv")

    client = registry.setup_mlflow()
    first = train_and_register(train, data.load("holdout"), client=client)
    print(f"champion v{first.version} : F1 holdout {first.candidate['f1_macro']:.4f}")

    monitor = Monitor(PredictionStore(), client)
    stream = data.load("stream")
    timeline = []
    with TestClient(api.app) as http:
        for step in range(1, steps_balanced + steps_skewed + 1):
            skewed = step > steps_balanced
            traffic = run_traffic(
                http,
                stream,
                n=per_step,
                skew="Sports" if skewed else None,
                ratio=0.7,
                feedback=1.0 if skewed else 0.5,
                seed=step,
            )
            status = monitor.step()
            if status.get("retrain", {}) and status["retrain"]["decision"] == "promoted":
                api.service.reload()
            champion = monitor.champion()
            row = {
                "step": step,
                "phase": "Sports 70 %" if skewed else "équilibré",
                "batch_accuracy": traffic["accuracy"],
                "psi": status["drift"]["psi"],
                "ks": status["drift"]["ks_stat"],
                "window": status["drift"]["n"],
                "drift": status["drift"]["drift"],
                "live_accuracy": status["live_accuracy"],
                "champion_version": champion.version,
                "champion_f1": champion.holdout.get("f1_macro"),
                "retrain": status["retrain"],
            }
            timeline.append(row)
            event = ""
            if status["retrain"]:
                r = status["retrain"]
                event = (
                    f" -> retrain v{r['version']} {r['decision'].upper()}"
                    f" ({r['champion_f1']:.4f} -> {r['candidate_f1']:.4f})"
                )
            print(
                f"step {step:2d} [{row['phase']:11s}] PSI {row['psi']:.3f} "
                f"KS {row['ks']:.3f} drift={row['drift']!s:5s} "
                f"champion v{row['champion_version']}{event}"
            )
    return timeline


def plot(timeline: list[dict], out: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, muted, grid, surface = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    blue, orange = "#2a78d6", "#eb6834"
    steps = [r["step"] for r in timeline]
    first_skewed = next((r["step"] for r in timeline if r["phase"] != "équilibré"), None)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 6.4), sharex=True, gridspec_kw={"hspace": 0.35}, facecolor=surface
    )
    for ax in (ax1, ax2):
        ax.set_facecolor(surface)
        ax.grid(axis="y", color=grid, linewidth=0.8)
        ax.tick_params(colors=muted, labelsize=9)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(grid)
        if first_skewed:
            ax.axvspan(first_skewed - 0.5, steps[-1] + 0.5, color=grid, alpha=0.35, lw=0)

    ax1.plot(steps, [r["psi"] for r in timeline], color=blue, lw=2, marker="o", ms=4)
    ax1.axhline(0.2, color=muted, lw=1, ls="--")
    ax1.text(steps[0], 0.2, " seuil de drift (PSI 0,2)", color=muted, fontsize=8, va="bottom")
    ax1.set_title(
        "Drift : PSI du mix de classes prédites vs référence du champion",
        loc="left",
        color=ink,
        fontsize=11,
    )
    if first_skewed:
        ax1.text(
            first_skewed - 0.4,
            ax1.get_ylim()[1] * 0.92,
            "trafic 70 % Sports",
            color=muted,
            fontsize=8,
        )

    live = [(r["step"], r["live_accuracy"]) for r in timeline if r["live_accuracy"] is not None]
    ax2.plot(
        [s for s, _ in live],
        [a for _, a in live],
        color=orange,
        lw=2,
        marker="o",
        ms=4,
        label="précision live (labels de feedback)",
    )
    ax2.step(
        steps,
        [r["champion_f1"] for r in timeline],
        where="post",
        color=blue,
        lw=2,
        label="F1 macro holdout du champion",
    )
    for r in timeline:
        if r["retrain"]:
            promoted = r["retrain"]["decision"] == "promoted"
            ax2.axvline(r["step"], color=muted, lw=1, ls="-" if promoted else ":")
            label = f"v{r['retrain']['version']} {'promu' if promoted else 'rejeté'}"
            ax2.text(
                r["step"] + 0.1,
                0.02,
                label,
                color=muted,
                fontsize=8,
                rotation=90,
                transform=ax2.get_xaxis_transform(),
                va="bottom",
            )
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax2.set_title(
        "Performance : précision live et juge fixe (holdout)", loc="left", color=ink, fontsize=11
    )
    ax2.set_xlabel("pas de temps (100 requêtes chacun)", color=muted, fontsize=9)
    ax2.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
    ax2.set_xlim(0.5, steps[-1] + 0.5)
    ax2.legend(
        frameon=False,
        fontsize=8,
        labelcolor=ink,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.2),
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor=surface)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--initial-size", type=int, default=5000)
    parser.add_argument("--balanced", type=int, default=5)
    parser.add_argument("--skewed", type=int, default=15)
    parser.add_argument("--per-step", type=int, default=100)
    args = parser.parse_args()

    _isolate()
    timeline = run(args.initial_size, args.balanced, args.skewed, args.per_step)
    reports = ROOT / "reports"
    (reports / "demo.json").write_text(json.dumps(timeline, indent=2), encoding="utf-8")
    plot(timeline, reports / "demo.png")
    print(f"-> {reports / 'demo.json'} · {reports / 'demo.png'}")


if __name__ == "__main__":
    main()
