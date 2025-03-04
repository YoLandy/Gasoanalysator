import numpy as np
from utils.datamanager.data import DataManager

PURPLE_CONST_1 = 0.9
PURPLE_CONST_2 = 10000

COEFFS = {
    "C": PURPLE_CONST_1 / 60 / 22.4 * 12 / PURPLE_CONST_2,
    "S": PURPLE_CONST_1 / 60 / 22.4 * 32 / PURPLE_CONST_2,
}


class Calculator:
    def __init__(self, data=[], gastype="C") -> None:
        self.data = np.array(data)
        self.gastype = gastype

        self.naves_mass = DataManager.get_param("Naves mass")

        if gastype == "C":
            self.koeff_recalc = DataManager.get_param("Koeff C")
            self.last_ce = DataManager.get_param("Control exp C")

        else:
            self.koeff_recalc = DataManager.get_param("Koeff S")
            self.last_ce = DataManager.get_param("Control exp S")

    def update_koeff(self):
        if self.gastype == "C":
            self.koeff_recalc = DataManager.get_param("Koeff C")
            self.last_ce = DataManager.get_param("Control exp C")

        else:
            self.koeff_recalc = DataManager.get_param("Koeff S")
            self.last_ce = DataManager.get_param("Control exp S")

    def set_mass(self, mass):
        self.naves_mass = mass

    def set_data(self, data):
        self.data = np.array(data)

    def data_with_coef(self):
        return self.data * self.calc_coeffs()[self.gastype]

    def calc_pure_integral(self):
        return np.trapz(self.data)

    def line(self):
        a = self.data[:5].mean()
        b = self.data[-5:].mean()
        lined_part = np.linspace(a, b, len(self.data) - 10)
        return np.concatenate((a * np.ones(5), lined_part, b * np.ones(5)), axis=None)

    def calc_pure_integral_with_coeff(self):
        I = self.calc_pure_integral()
        coeffs = self.calc_coeffs()
        a = {gas_type: I * coeff for gas_type, coeff in coeffs.items()}
        return a[self.gastype]

    def calc_coeffs(self):
        return {
            "C": PURPLE_CONST_1 / 60 / 22.4 * 12 / PURPLE_CONST_2,
            "S": PURPLE_CONST_1 / 60 / 22.4 * 32 / PURPLE_CONST_2,
        }

    def calc_i7(self):
        Iline = np.trapz(self.line())
        I = self.calc_pure_integral()
        return I - Iline

    def calc_mass(self):
        I7 = self.calc_i7()
        return I7 * COEFFS[self.gastype]

    def calc_concentrate(self):
        self.update_koeff()
        return (
            self.koeff_recalc
            * (self.calc_mass() - self.last_ce)
            / self.naves_mass
            * 100
        )

    def calc_concentrate_int(self):
        self.update_koeff()
        return (
            self.koeff_recalc
            * (self.calc_pure_integral_with_coeff())
            / self.naves_mass
            * 100
        )
