import numpy as np
# import matplotlib.pyplot as plt


class FaradaicEfficiencyECMS():
    
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

    def linear_fit_HER_calibration_factor(self, steps, background_current):
        """
        conversion from MS current to cell current by linearly fitting HER current 
        assuming 100% faradaic efficiency.
        """
        HER_calibration_intervals = self._interval_times_from_step_numbers(steps)

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
    


