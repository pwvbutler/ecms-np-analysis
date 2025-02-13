from ecms_np_analysis import FaradaicEfficiencyECMS, MASS_TO_SPECIES_PLOT
from ixdat import Measurement
import os

RE_VS_RHE=0.0
ELECTRODE_AREA=0.196
OHMIC_DROP=0.0

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="calculate and plot CO2RR faradaic efficiencies from ecms data"
    )

    parser.add_argument(
        "tsv_file",
        type=str,
        help="Mass spec tsv data file",
    )

    parser.add_argument(
        "mpt_files_path_prefix",
        type=str,
        help="EC potentiostat mpt data files path prefix, e.g. .../03__02_CP",
    )


    parser.add_argument(
        "-ave",
        "--time-averaged-over",
        type=float,
        default=100,
        help="time duration to average currents over",
    )

    parser.add_argument(
        "-st",
        "--start-time",
        type=float,
        default=0,
        help="set t=0 of step sequence if desired",
    )

    parser.add_argument(
        "-pH",
        "--pH",
        type=float,
        default=None,
        help="pH of Ag/AgCl reference electrode",
    )
    
    parser.add_argument(
        "-ca",
        "--ca",
        action="store_true",
        default=False,
        help="data is from CA experiment instead of CP",
    )

    args = parser.parse_args()

    TSV_FILENAME = os.path.basename(args.tsv_file)[:-4]
    TSV_FILE_DIR = os.path.dirname(args.tsv_file)


    ms = Measurement.read(
        args.tsv_file,
        reader="zilien",
        technique="MS",
    )

    ec = Measurement.read_set(
        args.mpt_files_path_prefix,
        suffix=".mpt",
    )

    ecms = ec + ms
    
    # fix for raw_potential being always 0 (not read correctly) 
    if not args.ca:
        ecms["raw_potential"]._data = ecms["<Ewe/V>"]._data
    else:
        ecms["raw_potential"]._data = ecms["Ewe/V"]._data
        
    ecms.t[0]
    ecms.tstamp += ecms.t[0] - 1

    ecms.calibrate( # do this first
        RE_vs_RHE=RE_VS_RHE, # if use RHE reference electrode assume that the potential difference between our reference electrode and the RHE potential is zero.
        A_el=ELECTRODE_AREA, # We know the geometric area of the electrode, so we can normalize the current: it’s a 5mm diameter disk, area = 0.196 cm^2
        R_Ohm=OHMIC_DROP, # We did not determine the Ohmic drop, but we will assume that it was 0 
    )


    axes = ecms.plot()
    fig = axes[0].get_figure()
    fig.set_size_inches(
        7, # figure width
        8, # figure height
        # forward=True
    )

    _, labels = axes[0].get_legend_handles_labels()
    new_labels = [ MASS_TO_SPECIES_PLOT[x] for x in labels]
    new_labels

    axes[0].legend(
        loc=(1.05, 0.5), # uncomment to change legend position
        labels=new_labels,
    )

    fig.suptitle(TSV_FILENAME)

    fig.savefig("ecms_plot.png", dpi=300, bbox_inches='tight',)

if __name__=="__main__":
    main()