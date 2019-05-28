import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

import sys
sys.path.append("./")

"""
    A few utils functions to calculate the luminance in Lux given a specific setting for the background in the GUI and
    for calculating the contrast of the loom given the selected background and loom color settings. 
"""


class Calculator:
    def __init__(self):

        measurements_file = "Utils/measurements.xlsx"
        self.data = pd.read_excel(measurements_file,
            sheetname=0,
            header=0,
            index_col=False,
            keep_default_na=True
            )

        self.fit()

    def fit(self):
        lux_coeff = np.polyfit(self.data["Background Luminance"], self.data["Lux"], 2)
        self.lux_fit = np.poly1d(lux_coeff)
        ldr_coeff = np.polyfit(self.data["Background Luminance"], self.data["LDR readout - Python"], 2)
        self.ldr_fit = np.poly1d(ldr_coeff)
        self.x = np.linspace(0, 255, 25)

        self.fits = {
            "Lux": self.lux_fit, 
            "LDR readout - Python": self.ldr_fit
        }

        


    def plot(self, y):
        f, ax = plt.subplots()

        ax.scatter(self.data["Background Luminance"], self.data[y],s=250, color='k')
        ax.plot(self.x, [self.fits[y](xx) for xx in self.x],  color='r')

        ax.set(xlabel="GUI bg luminance", ylabel=y)


    def contrast_calc(self, bg, loom):
        bg_lux = self.lux_fit(bg)
        loom_lux = self.lux_fit(loom)

        contrast = round((bg_lux - loom_lux)/bg_lux, 2)

        print("""
            Contrast for:
                - background:  {}
                - loom:        {}

                ---------------------

                --> {}
        
        """.format(bg, loom, contrast))


    def loom_angle_calculator(self, diameter, distance):
        theta = round(math.degrees(math.atan((diameter*0.5)/distance)),2) * 2
        print("""
            Loom angle for:
                - diameter:  {}
                - distance:  {}

                ---------------------

                --> {}
        
        """.format(diameter, distance, theta))


if __name__ == "__main__":
    c = Calculator()

    # c.plot("Lux")
    c.plot("LDR readout - Python")

    # c.contrast_calc(125, 10)

    # c.loom_angle_calculator(90, 170)

    plt.show()

