from ecms_np_analysis import FaradaicEfficiencyECMS
from ixdat import Measurement
import os

RE_VS_RHE=0.0
ELECTRODE_AREA=0.196
OHMIC_DROP=0.0

MASS_TO_SPECIES_PLOT = {
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

MASS_TO_SPECIES = {
    "M2": "H2",
    "M4": "He",
    "M15": "CH4",
    "M18": "H2O",
    "M26": "C2H2",
    "M28": "CO/N2",
    "M32": "O2",
    "M40": "Ar",
    "M44": "CO2",
}

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
        "-her",
        "--her-only-steps",
        type=int,
        nargs="+",
        required=True,
        help="HER are only step numbers (steps start from 1)",
    )

    parser.add_argument(
        "-s",
        "--step-length",
        default=300,
        type=float,
        help="length of steps in ECMS experiment",
    )

    parser.add_argument(
        "-bg",
        "--ms-background-interval",
        type=float,
        nargs=2,
        required=True,
        help="start and end time for calculating HER MS background current",
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
    # ecms["raw_potential"]._data = ecms["Ewe/V"]._data # fix for raw_potential being always 0 (not read correctly) 
    ecms["raw_potential"]._data = ecms["<Ewe/V>"]._data
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

    if args.pH is not None:
        ecms.calibrate( # do this first
            RE_vs_RHE=0.1976 + 0.059*args.pH, # if use RHE reference electrode assume that the potential difference between our reference electrode and the RHE potential is zero.
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
        fig.savefig("ecms_plot_Ag_AgCl.png", dpi=300, bbox_inches='tight',)



    FE_calculator = FaradaicEfficiencyECMS(
        ecms,
        start_time=args.start_time,
        step_duration=args.step_length,
        duration_averaged=args.time_averaged_over,
    )

    import pdb; pdb.set_trace()
    HER_background = FE_calculator.calc_HER_background_current(
        *args.ms_background_interval
    )

    # import pdb;pdb.set_trace()
    coefs = FE_calculator.linear_fit_HER_MS_to_cell_current_conversion(
        step_nums=args.her_only_steps,
        background_current=HER_background,
    )

    # import pdb; pdb.set_trace()
    data = FE_calculator.calculate_CO2RR_faradaic_efficiencies(
        [x+1 for x in range(ecms.selector._data[-1] + 1)], # all intervals
        coefs,
        HER_background,
    )

    data.to_csv("CO2RR_faradaic_efficiencies.csv", index=False)



if __name__ == "__main__":
    main()

