import ixdat

MASS_TO_SPECIES = {
    "M2": "H$_{2}$",
    "M4": "He",
    "M15": "CH$_{4}$",
    "M18": "H$_{2}$O",
    "M26": "C$_{2}$H$_{2}$",
    "M28": "CO/N$_{2}$",
    "M32": "O$_{2}$",
    "M40": "Ar",
    "M44": "CO$_{2}$",
}

def plot_ecms_data(ecms, **kwargs):
    axes = ecms.plot()
    fig = axes[0].get_figure()
    fig.set_size_inches(
        kwargs.get("width", 7), 
        kwargs.get("height", 8), 
    )

    _, labels = axes[0].get_legend_handles_labels()
    if kwargs.get("use_species"):
        labels = [ MASS_TO_SPECIES[x] for x in labels]

    axes[0].legend(
        loc=kwargs.get("legend_position", (1.05, 0.5)),
        labels=labels,
    )

    if kwargs.get("save_figure", False) or kwargs.get("save_figure_path", False):
        fig.savefig(
            kwargs.get("save_figure_path", "ecms_plot.png"), 
            dpi=300, 
            bbox_inches='tight',
        )

    return fig, axes