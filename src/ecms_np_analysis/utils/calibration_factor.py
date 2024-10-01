from ixdat.constants import FARADAY_CONSTANT

def convert_HER_current_by_calibration_factor(HER_calibration_factor, raw_current):
    """
    estimates the total MS current from the applied raw current using the HER
    calibration factor (C/mol) which is determined by fitting to HER only currents
    (with the ixdat.ecms_calibration_curve function).

    Deriviation:
    calibration factor = MS_current / molar_flux
    where
    molar_flux = raw_current/(z*F), where z is electron per molecule and F is
    Faraday's constant (9.64853321233100184e4 C / mol)
    hence
    total_MS_current = calibration_factor * (raw_current/zF)
    """
    return HER_calibration_factor*(raw_current/(2*FARADAY_CONSTANT))
