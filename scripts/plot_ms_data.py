from ixdat import Measurement
import matplotlib.pyplot as plt
from ecms_np_analysis import MASS_TO_SPECIES_PLOT

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("tsv_file", type=str)
    
    parser.add_argument("-s", "--save-plot", type=str, default=None, help="save plot to filename", metavar="filename")
    
    args = parser.parse_args()
    
    ms = Measurement.read(
        args.tsv_file,
        reader="zilien",
        technique="MS",
    )
    
    axes = ms.plot()
    fig = axes.get_figure()
    _, labels = axes.get_legend_handles_labels()
    new_labels = [ MASS_TO_SPECIES_PLOT[x] for x in labels]

    if args.save_plot is not None:
        axes.legend(
            loc=(1.05, 0.5), # uncomment to change legend position
            labels=new_labels,
        )
        fig.savefig(args.save_plot + ".png", dpi=300, bbox_inches='tight',)
    else:
        axes.legend(
            # loc=(1.05, 0.5), # uncomment to change legend position
            labels=new_labels,
        )
        plt.show()
    
if __name__ == "__main__":
    main()