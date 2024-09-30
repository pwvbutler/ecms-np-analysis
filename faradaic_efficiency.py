import numpy as np
# import matplotlib.pyplot as plt


class FaradaicEfficiencyECMS():
    """"""
    def __init__(
            self,
            ecms_data,
            start_time,
            step_duration,
            duration_averaged,
    ):
        
        self._ecms = ecms_data
        self.start_time = start_time
        self.step_duration = step_duration
        self.duration_averaged = duration_averaged


    def _interval_times_from_step_numbers(self, steps):
        """
        convert ordinal number of each step to the corresponding time intervals 
        required for calculations 
        """
        return [
            (
                self.start_time + self.step_duration*(x)-self.duration_averaged, 
                self.start_time + self.step_duration*(x)
            )
            for x in steps
        ]


    def calc_HER_background_current(self, start_time, end_time):
        """
        calculate HER background current as average current between 
        start and end times.
        """
        tspan = (start_time, end_time)
        _, currents = self._ecms.grab(item="M2 [A]", tspan=tspan)
        
        return currents.mean()


    def linear_fit_HER_calibration_factor(self, step_nums, background_current):
        """
        conversion from MS current to cell current by linearly fitting HER current 
        assuming 100% faradaic efficiency.
        """
        HER_calibration_intervals = self._interval_times_from_step_numbers(step_nums)

        raw_currents, HER_currents = [], []

        for interval in HER_calibration_intervals:
            raw_currents.append(
                self._ecms.grab(item="raw_current", tspan=interval)[1].mean(),
            )
            HER_currents.append(
                self._ecms.grab(item="M2 [A]", tspan=interval)[1].mean(),
            )

        raw_currents = np.array(raw_currents)
        HER_currents = np.array(HER_currents) - background_current

        m, b = np.polyfit(
            HER_currents,
            raw_currents,
            1
        )

        return m, b
    

    def calculate_CO2RR_faradaic_efficiencies(self, step_nums, fit_coefs, background_current):
        data6 = []

        m, b = fit_coefs

        CO2RR_intervals = self._interval_times_from_step_numbers(step_nums)

        for interval in CO2RR_intervals:
            raw_current = self._ecms.grab(item="raw_current", tspan=interval)[1].mean()
            HER_current = self._ecms.grab(item="M2 [A]", tspan=interval)[1].mean() - background_current
            
            HER_cell_current = np.abs(HER_current) * m + b
            CO2RR_current = np.abs(raw_current) - HER_cell_current

            if CO2RR_current < 0 or  CO2RR_current < background_current:
                CO2RR_current = 0.00
                faradaic_efficiency = 0
            else:
                faradaic_efficiency = (CO2RR_current / np.abs(raw_current)) * 100
            
            data6.append([interval[0], interval[1], raw_current, HER_current, HER_cell_current, CO2RR_current, faradaic_efficiency])


