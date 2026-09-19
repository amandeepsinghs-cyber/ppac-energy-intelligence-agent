"""Institutional Asset & Logo Generator for PPAC & MoPNG Publications."""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def generate_institutional_logos(assets_dir: Path):
    """Generates clean institutional badge logos for headers."""
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 1. MoPNG Emblem Badge
    crest_path = assets_dir / "mopng_crest.png"
    if not crest_path.exists():
        fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=300)
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")

        # Golden outer circle
        circle_outer = patches.Circle((0.5, 0.5), 0.45, fill=False, edgecolor="#C68A4C", linewidth=3)
        circle_inner = patches.Circle((0.5, 0.5), 0.41, fill=True, facecolor="#1B365D")
        ax.add_patch(circle_outer)
        ax.add_patch(circle_inner)

        # Central Emblem geometry
        ax.text(0.5, 0.56, "SATYAMEVA JAYATE", color="#FFFFFF", fontsize=6, ha="center", va="center", fontweight="bold")
        ax.text(0.5, 0.45, "MoPNG", color="#C68A4C", fontsize=11, ha="center", va="center", fontweight="bold", family="sans-serif")
        ax.text(0.5, 0.35, "GOVT OF INDIA", color="#E2E8F0", fontsize=5.5, ha="center", va="center", fontweight="bold")

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(crest_path, bbox_inches="tight", pad_inches=0.02, transparent=False)
        plt.close()

    # 2. PPAC Emblem Logo
    ppac_path = assets_dir / "ppac_logo.png"
    if not ppac_path.exists():
        fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=300)
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")

        # Circular gear / compass
        circle = patches.Circle((0.5, 0.5), 0.44, fill=True, facecolor="#F0F4F8", edgecolor="#2E5B88", linewidth=2.5)
        ax.add_patch(circle)

        # Inner flame / hydrocarbon droplet
        wedge = patches.Wedge((0.5, 0.5), 0.35, 45, 315, facecolor="#1B365D", edgecolor="#C68A4C", linewidth=1.5)
        ax.add_patch(wedge)

        ax.text(0.5, 0.53, "PPAC", color="#FFFFFF", fontsize=12, ha="center", va="center", fontweight="bold")
        ax.text(0.5, 0.38, "ENERGY CELL", color="#C68A4C", fontsize=5.5, ha="center", va="center", fontweight="bold")

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(ppac_path, bbox_inches="tight", pad_inches=0.02, transparent=False)
        plt.close()

    return crest_path, ppac_path
