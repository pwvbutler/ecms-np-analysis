# ECMS NP Analysis

Scripts and code for analysing EC-MS data of nanoparticle electrocatalysts and calculating faradaic efficiencies


## Getting Started

### Dependencies

* python>=3.12.9
* ixdat>=0.2.12 
* pandas>=2.2.2

for the GUI:

* streamlit>=1.38.0

### Installing

Create a virtual environment. For example with conda:

```
conda create -n ecms-analysis python=3.12
```

Activate the environment. For example, 

```
conda activate ecms-analysis
```

then clone the repo and change into the base directory:

```
git clone https://gitlab.com/pwvbutler/ecms_np_analysis.git
cd ecms_np_analysis
```

Run the following command in the base directory to install:

```
python -m pip install .
```

If using a python virtual environment:

Mac/linux:
```
python -m venv ecms_venv
source ecms_venv/bin/activate
python -m pip install .
```

Windows:
```
python -m venv ecms_venv
ecms_venv\Scripts\activate
python -m pip install .
```

### Usage

The easiest way to use the analysis is throught the streamlit gui, where can upload the CP/CA (.mpt) and MS data (.tsv) files, create the ECMS plot, and calculate the faradaic efficiency based on provided parameters. To run the GUI, activate the virtual environment 
if using one and go to the src/ecms_np_anlysis directory, then execute the command:

```
streamlit run simple_gui.py
```
or 
```
python -m streamlit run simple_gui.py
```

This will start a local server and launch it in your default browser.

Alternatively, the script CO2RR_faradaic_efficiencies_analysis.py in the scripts directory can be used to run the analysis from the command line. The parameters for the script:

```
usage: CO2RR_faradaic_efficiencies_analysis.py [-h] -her HER_ONLY_STEPS [HER_ONLY_STEPS ...] [-s STEP_LENGTH] -bg MS_BACKGROUND_STEPS [MS_BACKGROUND_STEPS ...] [-ave TIME_AVERAGED_OVER] [-st START_TIME]
                                               [-pH PH] [-ca]
                                               tsv_file mpt_files_path_prefix

calculate and plot CO2RR faradaic efficiencies from ecms data

positional arguments:
  tsv_file              Mass spec tsv data file
  mpt_files_path_prefix
                        EC potentiostat mpt data files path prefix, e.g. .../03__02_CP

options:
  -h, --help            show this help message and exit
  -her HER_ONLY_STEPS [HER_ONLY_STEPS ...], --her-only-steps HER_ONLY_STEPS [HER_ONLY_STEPS ...]
                        HER are only step numbers (steps start from 1)
  -s STEP_LENGTH, --step-length STEP_LENGTH
                        length of steps in ECMS experiment
  -bg MS_BACKGROUND_STEPS [MS_BACKGROUND_STEPS ...], --ms-background-steps MS_BACKGROUND_STEPS [MS_BACKGROUND_STEPS ...]
                        start and end step for calculating HER MS background current
  -ave TIME_AVERAGED_OVER, --time-averaged-over TIME_AVERAGED_OVER
                        time duration to average currents over
  -st START_TIME, --start-time START_TIME
                        set t=0 of step sequence if desired
  -pH PH, --pH PH       pH of Ag/AgCl reference electrode
  -ca, --ca             data is from CA experiment instead of CP
```

Other scripts are available for creating individual ECMS, EC, and MS plots.
