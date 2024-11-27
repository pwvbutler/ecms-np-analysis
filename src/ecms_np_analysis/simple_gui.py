import streamlit as st
import os
from ixdat import Measurement
from faradaic_efficiency import FaradaicEfficiencyECMS

import zipfile
import io
import tempfile
import datetime
st.write(datetime.datetime.now().astimezone().tzname())

##############################################
################# FUNCTIONS ##################
##############################################

def validate_form():

    valid = False

    if st.session_state.ms_datafile is None:
        st.warning("MS data has not been uploaded, cannot process data")
    elif st.session_state.ec_cp_datafile is None and st.session_state.ec_ca_datafile is None:
        st.warning("EC data has not been uploaded, cannot process data")
    elif st.session_state.HER_background_current == "" and st.session_state.HER_background_steps == "":
        st.warning("enter HER background current or step numbers ")
    elif st.session_state.HER_only_steps == "":
        st.warning("enter HER only steps")
    else:
        valid = True

    return valid

@st.cache_data
def get_ms_data(ms_uploadedfile):
    try:
        MS_data = ms_uploadedfile.read()
    except:
        ValueError("Cannot read uploaded MS data")
    # st.write(ms_datafile.name)
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(MS_data)
    ms = Measurement.read(
        tmp.name,
        reader="zilien",
        technique="MS"
    )
    tmp.close()

    return ms

@st.cache_data
def get_ec_data(ec_uploadedfile):
    try:
        EC_data = ec_uploadedfile.read()
    except:
        ValueError("Cannot read uploaded EC data")
    # st.write(ms_datafile.name)
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(EC_data)
    ec = Measurement.read(
        tmp.name,
        reader="biologic",
        technique="EC",
        # suffix=".mpt"
    )
    tmp.close()

    return ec

def plot_ecms_data(ecms, name, **kwargs):

    mass_to_species = {
        "M2": "H$_{2}$",
        "M4": "He",
        "M15": "CH$_{4}$",
        "M18": "H$_{2}$O",
        "M26": "C$_{2}$H$_{4}$",
        "M28": "CO/N$_{2}$",
        "M32": "O$_{2}$",
        "M40": "Ar",
        "M44": "CO$_{2}$",
    }

    axes = ecms.plot()
    fig = axes[0].get_figure()
    fig.set_size_inches(
        st.session_state.get("plot_width", 7), 
        st.session_state.get("plot_height", 8),
    )
    fig.suptitle(name)

    _, labels = axes[0].get_legend_handles_labels()
    new_labels = [ mass_to_species[x] for x in labels]

    axes[0].legend(
        loc=(
            st.session_state.get("legend_x", 1.05),
            st.session_state.get("legend_y", 0.50),
        ),
        labels=new_labels,
    )

    return fig, axes



# @st.cache_data
def calc_faradaic_efficiencies(
    ecms,
):
    
    try:
        start_time = float(st.session_state["start_time"])
        duration_averaged = float(st.session_state["duration_averaged"])
        step_duration = float(st.session_state["step_duration"])
        HER_only_step_nums = [int(x) for x in st.session_state["HER_only_steps"].split()]
    except Exception as e:
        raise ValueError("cannot pass options: {}".format(e))

    HER_background_current = st.session_state["HER_background_current"]
    HER_background_steps = st.session_state["HER_background_steps"]

    FE_calculator = FaradaicEfficiencyECMS(
        ecms_data=ecms,
        start_time=start_time,
        step_duration=step_duration,
        duration_averaged=duration_averaged
    )

    if HER_background_current != "":
        HER_background = float(HER_background_current)
    else:
        HER_background = FE_calculator.calc_HER_background_current(
            [int(x) for x in HER_background_steps.split()]
        )

    coefs = FE_calculator.linear_fit_HER_MS_to_cell_current_conversion(
        step_nums=HER_only_step_nums,
        background_current=HER_background,
    )

    data = FE_calculator.calculate_CO2RR_faradaic_efficiencies(
        [x+1 for x in range(ecms.selector._data[-1] + 1)], # all intervals
        coefs,
        HER_background,
    )

    return data



##############################################
################## SIDEBAR ###################
##############################################

st.sidebar.title(
    "ECMS NP Faradaic Efficiency Analysis"
)

st.sidebar.markdown(
    "Notes:\n"
    "- Step numbers start from 1 and should be given as a space separated list (e.g. 1 2 3)"
)

st.sidebar.markdown(
    "Plotting Options:"
)

plot_width = st.sidebar.slider(
    "plot width", 1, 14, 7, key="plot_width",
)
plot_height = st.sidebar.slider(
    "plot height", 1, 14, 8, key="plot_height",
)

legend_x = st.sidebar.slider(
    "legend x", -0.5, 1.5, 1.05, key="legend_x",
)

legend_y = st.sidebar.slider(
    "legend y", -0.5, 1.5, 0.50, key="legend_y",
)



##############################################
##### File upload and processing options #####
##############################################

ms_datafile = st.file_uploader(
    "MS tsv file",
    key="ms_datafile",
)

col1, col2 = st.columns(2)

with col1:
    ec_cp_datafile = st.file_uploader(
        "EC CP mpt files",
        # accept_multiple_files=True,
        key="ec_cp_datafile",
    )
    HER_background_current = st.text_input("HER_background_current", value="", key="HER_background_current")
    HER_only_steps = st.text_input("HER only step numbers", key="HER_only_steps")
    average_over_duration = st.text_input("duration average signal over (s)", value=100, key="duration_averaged")
    

with col2:
    ec_ca_datafile = st.file_uploader(
        "EC CA mpt files",
        # accept_multiple_files=True,
        key="ec_ca_datafile",
    )
    # HER_background_type = st.selectbox("", ("step numbers", "current",), index=0, key="HER_background_type")
    HER_background_steps = st.text_input("HER_background_steps", key="HER_background_steps")
    step_duration = st.text_input("step duration", value=300, key="step_duration")
    start_time = st.text_input("Sequence start time (s)", value=0, key="start_time")



##############################################
################ PROCESS DATA ################
##############################################

col1, col2 = st.columns(2)
ecms_ca_fig = ecms_cp_fig = None

with col1:
    if st.button("process data") and validate_form():
            name = ms_datafile.name[:-4]
            st.write(HER_background_current)
            ms = get_ms_data(ms_datafile)
            ec_cp = get_ec_data(ec_cp_datafile) if ec_cp_datafile is not None else None
            ec_ca = get_ec_data(ec_ca_datafile) if ec_ca_datafile is not None else None

            if ec_cp is not None:
                if datetime.datetime.now().astimezone().tzname() == "UTC":
                    ec_cp["time/s"]._data -= 7200
                ecms_cp = ec_cp + ms
                ecms_cp["raw_potential"]._data = ecms_cp["<Ewe/V>"]._data # quick fix: for some reason raw_potential is not correct
                ecms_cp.tstamp += ecms_cp.t[0] - 1

                ecms_cp_fig, ecms_cp_axes = plot_ecms_data(ecms_cp, name + " CP")

                ecms_cp_data = calc_faradaic_efficiencies(ecms_cp)


            if ec_ca is not None:
                ecms_ca = ec_ca + ms
                ecms_ca["raw_potential"]._data = ecms_ca["Ewe/V"]._data
                ecms_ca.tstamp += ecms_ca.t[0] - 1

                ecms_ca_fig, ecms_ca_axes = plot_ecms_data(ecms_ca, name + " CA")

                ecms_ca_data = calc_faradaic_efficiencies(ecms_ca)
            
            st.session_state["data_processed"] = True


##############################################
############### DOWNLOAD DATA ################
##############################################


if st.session_state.get("data_processed", False):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        if ecms_cp_fig is not None:
            buf = io.BytesIO()
            ecms_cp_fig.savefig(buf, dpi=300)
            zf.writestr(name + "_cp_ecms_plot.png", buf.getvalue())
            zf.writestr(name + "_cp_ecms_fe.csv", ecms_cp_data.to_csv())
        if ecms_ca_fig is not None:
            buf = io.BytesIO()
            ecms_ca_fig.savefig(buf, dpi=300)
            zf.writestr(name + "_ca_ecms_plot.png", buf.getvalue())
            zf.writestr(name + "_ca_ecms_fe.csv", ecms_ca_data.to_csv())

    with col2:
        st.download_button(
            label="download results",
            data=zip_buffer,
            file_name="results.zip",
        )


##############################################
################### RESULTS ##################
##############################################

tab1, tab2 = st.tabs(["ECMS CP Results", "ECMS CA Results"],)

with tab1:
    if ecms_cp_fig is not None:
        st.write(ecms_cp_fig)
        st.dataframe(ecms_cp_data)
    else:
        st.write("upload CP data and press process")

with tab2:
    if ecms_ca_fig is not None:
        st.write(ecms_ca_fig)
        st.dataframe(ecms_ca_data)
    else:
        st.write("upload CA data and press process")





















# st.markdown(
#     "### EC-MS Data Plotter"
# )

# col1, col2 = st.columns(2)




# with col1:

#     # tsv_file = st.file_uploader(
#     #     "tsv file",
#     # )
#     # if tsv_file is not None:
#     #     st.write("tsv_file:", dir(tsv_file))

#     # if st.button("browse"):
#     #     dialog = wx.DirDialog(None, "Select a folder:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
#     #     if dialog.ShowModal() == wx.ID_OK:
#     #         tsv_filepath = dialog.GetPath() # folder_path will contain the path of the folder you have selected as string
#     tsv_filepath = st.text_input(
#         "tsv absolute filepath",
#         label_visibility="collapsed",
#         placeholder="tsv filepath",
#     )
#     expt_dir = st.text_input(
#         "expt folder",
#         label_visibility="collapsed",
#         placeholder="expt folder",
#     )
#     expt_prefix = st.text_input(
#         "expt prefix",
#         label_visibility="collapsed",
#         placeholder="expt prefix",
#     )
#     save_dir = st.text_input(
#         "save",
#         label_visibility="collapsed",
#         placeholder="save plot folder",
#     )

# with col2:
#     width = st.slider(
#         "width", 1, 14, 7,
#     )
#     height = st.slider(
#         "height", 1, 14, 5,
#     )
# # st.write(tsv_filepath == "")
# if not os.path.isfile(tsv_filepath):
#     st.write("tsv filepath required")
# elif not os.path.isdir(expt_dir):
#     st.write("expt folder required")
# else:
#     tsv_file_name=os.path.basename(tsv_filepath)[:-4]
#     fig, ecms = process_data(
#         tsv_filepath,
#         os.path.join(expt_dir, expt_prefix),
#         # save_dir,
#     )

#     fig.set_size_inches(width, height, forward=True)
#     st.write(fig)


# if st.sidebar.button("save results"):
#     if save_dir is None:
#         st.warning("save folder required")
    
#     try:
#         fig.savefig(
#             os.path.join(save_dir, tsv_file_name + '.png'), 
#             dpi=300,
#         )
#         ecms.export(
#             os.path.join(save_dir, tsv_file_name + "_calibration.csv"), 
#             time_step=1
#         )

#     except Exception as e:
#         st.warning("unable to save results: ", e)

