import os
import re
import glob
import numpy as np
from tqdm import tqdm
from datetime import date
from pywinauto.application import Application
import pywinauto.mouse as mouse
import pywinauto.keyboard as keyboard

class AutoPW:

    def __init__(self, pw_path, pw_case, input_file, output_file, freq='y', post_api=None):
        self.pw_path = pw_path
        self.pw_case = pw_case
        self.input_file = input_file
        self.output_file = output_file
        self.post_api = post_api
        self.app = Application(backend="uia").start(self.pw_path)
        self.dlg = None
        self.window = self.app.top_window()
        self.check_output_path()

    def check_output_path(self):
        """ check the output path, if the path is not exist, create it"""
        if not os.path.exists(self.output_file):
            os.makedirs(self.output_file)

    def get_file(self, freq='y'):
        """ get all the files in the file_path and return the date of each file
        @param file_path: the path of the file with extension ie: 'C:/Users/.../*.csv'
        @param freq: the frequency of the data, 'y' for yearly and 'm' for monthly
        """

        files = np.array(glob.glob(self.input_file))  # get all of files
        Date = []
        # print(files)
        for i, file in enumerate(tqdm(files, desc="extract date from files…", ncols=100, unit="file")):  # list of file
            if freq == 'M':  # for monthly data
                raw_date = re.search(r"([12]\d{3}).(0[1-9]|1[0-2])", os.path.basename(file))
                if raw_date: Date.append([date(int(raw_date[1]), int(raw_date[2]), 1), i])
            else:  # for yearly data
                raw_date = re.search(r"[1-3][0-9]{3}", os.path.basename(file))
                if raw_date: Date.append([date(int(raw_date[0]), 1, 1), i])  # for yearly data
        return files, Date

    def open_case(self):
        """ open the powerworld case"""
        self.window.set_focus()
        keyboard.send_keys('^o')
        dlg = app.top_window()
        dlg.FileNameEdit.set_edit_text(self.pw_case)
        dlg.Open.child_window(title="Open", auto_id="1", control_type="Button").click()
        return self.app, window, dlg

    def select_load_file(self,file_type='AUX'):
        """ extract the dlg from case name and select the load file type"""
        case_name=os.path.basename(self.pw_case)
        self.window.set_focus()
        if file_type=='AUX':
            app.EIA860_2021Gens_WithModels_StateZonespwbStatusInitializedSimulator23.LoadAuxFile.click()




if __name__ == "__main__":
    pass