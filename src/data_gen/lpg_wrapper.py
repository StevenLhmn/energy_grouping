import numpy as np
import os
import random
import shutil
import stat
from datetime import date
from pathlib import Path
from pylpg import lpg_execution, lpgdata
from src.utilities.seed_container import Seed_Container

class LPG_Wrapper():
    hh_names = []
    seed_container: Seed_Container = None
    house_names = []

    def __init__(self, seed: int):
        self.seed_container = Seed_Container
        self.hh_names = self._get_hh_name_list()
        self.house_names = self._get_house_name_list()

    def _get_hh_name_list(self):
        hhs = [
            name 
            for name, value in vars(lpgdata.Households).items() 
            if not name.startswith("_")
        ]

        return hhs
    
    def _get_house_name_list(self):
        houses = [
                name 
                for name, value in vars(lpgdata.HouseTypes).items() 
                if not name.startswith("_")
            ]

        return houses

    def _hh_data_from_name(self, name: str):
        return lpgdata.HouseholdData(
                    HouseholdNameSpec=lpgdata.HouseholdNameSpecification(getattr(lpgdata.Households, name)),
                    HouseholdDataSpecification=lpgdata.HouseholdDataSpecificationType.ByHouseholdName,
                )

    def _delete_calculations_folder(self):
        def remove_readonly(func, path, exc):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        lpg_folder = Path(lpg_execution.__file__).parent
        calc_folder = lpg_folder / "C1"
        if calc_folder.exists():
            shutil.rmtree(calc_folder, onerror=remove_readonly)
    
    def generate_appartment(self, n_hhs: int, start: date, end:date, interval: str):
        """
        Generates a profile of households in an apartment based on the provided number of households.

        Parameters:
        - n_hhs: number of households that should be considerd in the profile generation. 0-100
        - start: start date of the profile generation.
        - end: end date of the profile generation.
        - interval: the interval at which to generate the profile. '1h'

        """
        if start == None or end == None or interval == None:
            raise ValueError(f'start, end or interval was None')
        if n_hhs < 0 or n_hhs > 100:
            raise ValueError(f'nhh is {n_hhs} but has to be in the range of 0-100.')
        elif n_hhs == 0:
            days = (end - start).days + 1
            return np.zeros(days * 24)
        if end < start:
            raise ValueError(f'star {start} is later then end {end} which is not allowed.')
        if interval not in ['1h']:
           raise ValueError(f'interval {interval} is not one of the valid options.')

        hh_names = random.choices(self.hh_names, k=n_hhs)
        hhs_data = [
            self._hh_data_from_name(hh_name)
            for hh_name in hh_names
        ]
        housetype = getattr(lpgdata.HouseTypes, random.choice(self.house_names))
        print(f'using households: {hh_names} and house: {housetype}')
        self._delete_calculations_folder()
        data = lpg_execution.execute_lpg_with_many_householdata(
            year=2022,
            householddata=hhs_data,
            housetype=housetype,
            startdate=start.strftime("%Y-%m-%d"),
            enddate=end.strftime("%Y-%m-%d"),
            clear_previous_calc=True,
            random_seed=self.seed_container.seed()
        )
        print(data.columns)
        print(data.dtypes)
        if data is None or data.empty is True:
            raise RuntimeError("LPG returned no results. Check the simulation configuration and LPG logs.")
        # if data["Electricity_House"] exists, put it in varables and sum them up. If not, just sum the HH values.
        if "Electricity_House" in data.columns:
            electricity_house = data["Electricity_House"]
        else:
            electricity_house = 0
        data["Electricity_Total"] = (
            data.filter(regex=r"Electricity_HH\d+").sum(axis=1)
            + electricity_house
        )
        result = data["Electricity_Total"].resample(interval).sum()
        print(type(result))
        return np.array(result)






    