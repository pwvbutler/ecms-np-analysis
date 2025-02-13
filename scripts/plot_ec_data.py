from ixdat import Measurement
import matplotlib.pyplot as plt
from ecms_np_analysis import MASS_TO_SPECIES_PLOT

def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("mpt_file", type=str)
    
    parser.add_argument("-s", "--save-plot", type=str, default=None, help="save plot to filename", metavar="filename")
    
    args = parser.parse_args()
    
    ec = Measurement.read_set(
        args.mpt_file,
        suffix=".mpt",
    )
    
    axes = ec.plot()
    fig = axes[0].get_figure()

    if args.save_plot is not None:
        fig.savefig(args.save_plot + ".png", dpi=300, bbox_inches='tight',)
    else:
        plt.show()
    
if __name__ == "__main__":
    main()