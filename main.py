import time
import glob
import os
import re
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import pandas as pd
from pywinauto.application import Application
from tqdm import tqdm
import numpy as np
import pywinauto.mouse as mouse
import pywinauto.keyboard as keyboard
from datetime import date, datetime, timedelta
import requests
#from plotly_calplot import calplot
from subprocess import Popen
import json
import Record_mouse_click as helper


def get_position():
    import pyautogui as py  # Import pyautogui
    import time  # Import Time

    while True:  # Start loop
        print(py.position())
        time.sleep(1)


def get_file(file_path, freq='y'):
    files = np.array(glob.glob(file_path))
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


def get_files(file_path):
    files, Date = get_file(file_path)
    years_list = [[[Date[0][0], Date[0][1]]]]
    flag1 = True
    for data in (tqdm(Date, desc="converting file…", ncols=100, unit="file")):
        if flag1: flag1 = False; continue;
        # date = (data[0].replace(day=1) - timedelta(days=1)).replace(day=1)
        # end_date = (date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(1)
        # start_date = date.replace(day=1) - timedelta(days=1)
        # print(f'First day{start_date.strftime("%#m/%#d/%Y")}')
        # print(f'Last day{end_date.strftime("%m/%d/%Y").replace("0", " ")}')
        # print(f' day{date.strftime("%m/%d/%Y")}')
        repeated = False

        for i, years in enumerate(years_list):
            if years[0][0].year == data[0].year:
                repeated = True
                years_list[i].append([data[0], data[1]])
                break
            # if year don't exist, create new one
        if not repeated: years_list.append([[data[0], data[1]]])
    return files, years_list


def get_missing_date():
    files = np.array(glob.glob("D:/tsb_file/*.tsb"))
    Date = []
    # print(files)
    for i, file in enumerate(tqdm(files, desc="extract date from files…", ncols=100, unit="file")):  # list of file
        raw_date = re.search(r"([12]\d{3}).(0[1-9]|1[0-2])", os.path.basename(file))
        Date.append([date(int(raw_date[1]), int(raw_date[2]), 1), i])
    df = pd.DataFrame(Date, columns=['date', 'index'])
    df_v = pd.date_range(date(1935, 1, 1), date(2022, 3, 1), freq='MS', )
    df['date'] = pd.to_datetime(df['date'])
    df['exist'] = df['date'].isin(df_v.date)
    return (df[~df["exist"]])

def change_date():
    ### Assuming PowerWorld is already running and on TSB tab, changes date to 1/2
    record = helper.MouseClickRecorder()
    record.move_mouse(json.load(open('central_mon\change_date.json')))
    record.move_mouse(json.load(open('right_mon\change_date.json')))

def to_tsb(powerWorld_path=r"C:\Program Files\PowerWorld\Simulator 23\pwrworld.exe", # typically stays same
           case_path=r"C:\Users\lyrich237339\Documents\HardDriveStorage\PW_Case_Files\B7flat.pwb", 
           file_path=r"C:/Users/lyrich237339/Documents/HardDriveStorage/FarnazTest/*.aux", # must be a folder, direction of slashes important
           tsb_path=r"C:\Users\lyrich237339\Documents\HardDriveStorage\tsb_file_new", # must be a folder
           delay=0.6
           ):
    
    recorder = helper.MouseClickRecorder()
    app = Application(backend="uia").start(powerWorld_path) # opens powerworld
    window = app.top_window()
    window.set_focus()
    
    # Opens case path
    keyboard.send_keys('^o')
    dlg = app.top_window()
    dlg.FileNameEdit.set_edit_text(case_path)
    dlg.Open.child_window(title="Open", auto_id="1", control_type="Button").click()
    window = app.top_window()
    window.set_focus()
    
    # Sets window for coordinates, coords change depending on moniter set-up
    window.Maximize.click()
    window.Maximize.click()
    recorder.move_mouse(json.load(open('right_mon\setup_positions.json'))) # run, tool, time step
    

    ##### loop trough all aux file#####
    files, Date = get_file(file_path)
    for i, data in enumerate(tqdm(Date, desc="converting file…", ncols=100, unit="file")):
        data[0] = data[0] + timedelta(days=366)  # add other year due to pervous bug
        end_date = (data[0]).replace(day=1) - timedelta(days=1)
        start_date = (end_date - timedelta(days=360)).replace(day=1) - timedelta(days=1)
        print(f'First day{start_date.strftime("%#m/%#d/%Y")}')
        print(f'Last day{end_date.strftime("%m/%d/%Y").replace("0", " ")}')

        if post_api is not None: requests.post(post_api, params={"state": "run"})  # send state to monitor sever
        aux_path = os.path.normpath(files[data[1]])
        tsb_date = fr'\{end_date.strftime("%Y")}'
        start_date = start_date.strftime("%#m/%#d/%Y")  # there are some date misplacement in raw data
        end_date = end_date.strftime("%#m/%#d/%Y")
        
        ##### input file path
        recorder.move_mouse(json.load(open('right_mon\LoadAuxFile.json')))
        dlg = app.top_window()  # get the popup window
        dlg.FileNameEdit.set_edit_text(aux_path)
        # dlg.Open.child_window(title="Open", control_type="Button").click()
        dlg.Open.child_window(title="Open", auto_id="1", control_type="Button").click()
        window = app.top_window()
        
        # Gets past any pop-ups
        if window.child_window(title="Confirm").exists(timeout=0.5):
            window.Confirm.No.click()
        time.sleep(delay)
        if window.child_window(title="List index out of bounds (-1)", control_type="Text").exists(timeout=delay):
                window.ok.click()  # just click " ok "
        time.sleep(delay)
        if window.child_window(title="Yes to All", control_type="Button").exists(timeout=delay):
            window.Confirm.YestoAll.click()
        time.sleep(delay)
        try:
            if window.child_window(title="ok").exists(timeout=delay):
                window.ok.click()
        except:
            print("ok button not found")
        print("Past the pop-ups")
        time.sleep(delay)
        
        # sets run with correct dates
        window.ResetRun.click()
        # window.ClearResults.click() # sometimes this one, depends on computer
        # window.yes.ok() # used with above line
        # change_date() # for quick test cases

        print("Starting Run")
        recorder.move_mouse(json.load(open('right_mon\DoRun.json')))
        # window.DoRun.click()
        # app.CaseB7FLATpwbStatusInitializedSimulator23.SaveTSBFile.click()
        window.SaveTSBFile.wait("ready", timeout=18000, retry_interval = 10)
        print("Run Completed")

        # Saves the run after its finished
        window.SaveTSBFile.click() 
        dlg = app.top_window()
        dlg.FileNameEdit.type_keys(tsb_path + tsb_date)
        dlg.Save.click()
        if window.child_window(title="Yes").exists(timeout=2):
            window.Yes.click()
        app.CaseB7FLATpwbStatusInitializedSimulator23.DeleteAll.click()
        window.Confirm.Yes.click()
        if post_api is not None: requests.post(post_api, params={"state": "complete", "message": f"${data[0]}saved"})
    dlg.Close.click()
    dlg.Close.click()
    dlg.Close.click()


def merge_tsb(powerWorld_path=r"E:/PW_V23_64_April22_2023/pwrworld.exe",
              case_path=r"C:\Users\Thoma\Downloads\B7FLAT.pwb", file_path="D://tsb_file/tsb_file/*.tsb"):
    app = Application(backend="uia").start(powerWorld_path)
    window = app.top_window()
    window.set_focus()
    keyboard.send_keys('^o')
    # pyautogui.hotkey('ctrl', 'o')
    dlg = app.top_window()
    dlg.FileNameEdit.set_edit_text(case_path)
    dlg.Open.child_window(title="Open", auto_id="1", control_type="Button").click()
    window = app.top_window()
    window.set_focus()
    mouse.double_click('left', (18, 160))  # select run mode
    mouse.double_click('left', (481, 71))  # open tool
    mouse.double_click('left', (1163, 134))  # select run mode
    # pyautogui.click(x=1163, y=134, clicks=2)  # open time step Simulation

    ##### loop trough all TSB files Group by year#####
    fileList, files = get_tsb(file_path)
    for file in tqdm(files, desc="converting year", ncols=100, unit="file"):
        print(file[0][0].year)
        if post_api is not None: requests.post(post_api, params={"state": "run"})  # send state to monitor sever
        first_month = True
        start_date = None
        merge_tsb_path = fr"D:\tsb_file(yearly)\{file[0][0].year}"
        ##### loop trough all TSB file by month#####
        for i, data in enumerate(tqdm(file, desc="converting month…", ncols=100, unit="file")):
            Date = (data[0].replace(day=1) + timedelta(days=1)).replace(day=1)
            if first_month:
                start_date = Date.replace(day=1) - timedelta(days=1)
                start_date = start_date.strftime("%#m/%#d/%Y")  # there are some date misplacement in raw data
            end_date = (Date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(1)

            # print(f'First day{start_date.strftime("%#m/%#d/%Y")}')
            # print(f'Last day{end_date.strftime("%m/%d/%Y").replace("0", " ")}')
            # print(f' day{data.strftime("%m/%d/%Y")}')
            end_date = end_date.strftime("%#m/%#d/%Y")
            tsb_path = os.path.normpath(fileList[data[1]])  # path.abspath(data[1])
            # print(start_date, end_date, tsb_path, Date.strftime(r'%Y'))
            ##### input file path
            app.CaseB7FLATpwbStatusInitializedSimulator23.ReadTSBFile.click()
            time.sleep(1)
            dlg = app.top_window()  # get the popup window
            dlg.FileNameEdit.set_edit_text(tsb_path)  # set_edit_text(tsb_path)
            keyboard.send_keys('%o')
            # dlg=dlg.child_window(title="File name:", auto_id="1148", control_type="ComboBox")
            # dlg.Open.child_window(title="Open", auto_id="1", control_type="SplitButton").click()
            window = app.top_window()
            start = time.time()
            while not (window.child_window(title=start_date, control_type="Pane").exists() and window.child_window(
                    title=end_date, control_type="Pane").exists()) or int(
                time.time() - start) > 500:  # if the time displace match the input file, we are good to go
                if window.child_window(title="Confirm").exists(timeout=0.3):
                    if first_month:  # if is the first month, overwrite the data
                        window.Confirm.yes.click()
                    else:
                        window.Confirm.No.click()
                if window.child_window(title="Yes", auto_id="CommandButton_6", control_type="Button").exists(
                        timeout=0.3):
                    if first_month:  # if is the first month, overwrite the data
                        window.Confirm.yes.click()
                    else:
                        window.Confirm.No.click()
                if window.child_window(title="List index out of bounds (-1)", control_type="Text").exists(timeout=0.5):
                    window.ok.click()  # just click " ok "
                if window.child_window(title="Yes to All", control_type="Button").exists(timeout=0.3):
                    window.Confirm.YestoAll.click()
                if window.child_window(title="ok", control_type="Text").exists(timeout=0.3):
                    window.ok.click()  # just click " ok "
                time.sleep(0.5)
            first_month = False
        app.CaseB7FLATpwbStatusInitializedSimulator23.SaveTSBFile.click()
        # window.SaveTSBFile.click()
        time.sleep(1)
        dlg = app.top_window()
        # dlg.FileNameEdit.set_edit_text(r"D:\tsbdata\2020_03.tsb")
        dlg.FileNameEdit.type_keys(merge_tsb_path)
        dlg.Save.click()
        if window.child_window(title="Yes").exists(timeout=2):
            window.Yes.click()
        app.CaseB7FLATpwbStatusInitializedSimulator23.DeleteAll.click()
        window.Confirm.Yes.click()
        # requests.post(post_api, params={"state": "complete", "message": f"${file[0][0].year}saved"})
        time.sleep(35)
    dlg.Close.click()
    dlg.Close.click()
    dlg.Close.click()


from AutoPW import AutoPW


def process_weather_data():

    PW = AutoPW("E:/PW_V23_64_April22_2023/pwrworld.exe",
                 r"C:\Users\Thoma\Downloads\EIA860_2021Gens_WithModels_StateZones.pwb",
                 "D://multiple_weather_data/*aux", "D://multiple_weather_data_csv/")
    files, Data = PW.get_file()
    for i, file in enumerate(tqdm(files, desc="process data", ncols=100, unit="file")):
        app, window, dlg = PW.open_case()
        window = app.top_window()
        window.set_focus()
        mouse.double_click('left', (35, 136))  # select run mode
        mouse.double_click('left', (410, 60))  # open tool
        mouse.double_click('left', (1032, 116))  # select run mode
        time.sleep(1)
        app.EIA860_2021Gens_WithModels_StateZonespwbStatusInitializedSimulator23.LoadAuxFile.click()
        time.sleep(1)
        dlg = app.top_window()  # get the popup window
        raw_date = re.search(r"[1-3][0-9]{3}", os.path.basename(file))
        csv_path = fr"D:\GEN_wind_solar_csv_file_yearly_new\{raw_date[0]}"
        tsb_path = os.path.normpath(file)
        dlg.FileNameEdit.set_edit_text(tsb_path)  # set_edit_text(tsb_path)
        keyboard.send_keys('%o')
        if window.child_window(title="Yes", auto_id="CommandButton_6", control_type="Button").exists(timeout=30):
            window.Confirm.yes.click()  # replay the old data
        mouse.click('left', (930, 564))  # select yes
        # dlg=dlg.child_window(title="File name:", auto_id="1148", control_type="ComboBox")
        # dlg.Open.child_window(title="Open", auto_id="1", control_type="SplitButton").click()
        window = app.top_window()
        app.wait_cpu_usage_lower(threshold=2.5, timeout=60)  # wait for file to load
        mouse.click('left', (754, 762))  # disable refresh
        mouse.double_click('left', (764, 432))  # toggel solver type
        time.sleep(1)
        mouse.click('left', (873, 630))  # select all
        time.sleep(1)
        mouse.double_click('left', (969, 750))  # apply on to weather
        time.sleep(2)
        mouse.double_click('left', (63, 363))  # Results section, only click the frist time
        time.sleep(2)
        mouse.double_click('left', (93, 644))  # zones
        time.sleep(1)
        mouse.double_click('left', (381, 382))  # view
        time.sleep(1)
        mouse.double_click('left', (492, 363))  # view
        time.sleep(1)
        mouse.double_click('left', (509, 447))  # view
        time.sleep(1)
        mouse.double_click('left', (621, 440))  # view
        time.sleep(1)
        mouse.double_click('left', (782, 230))  # add field
        time.sleep(3)
        mouse.double_click('left', (119, 311))  # gen type unit fuel
        time.sleep(1)
        mouse.double_click('left', (141, 330))  # MW
        time.sleep(1)
        mouse.click('left', (191, 369))  # solar
        time.sleep(1)
        mouse.double_click('left', (414, 132))  # add
        time.sleep(1)
        # mouse.scroll((348, 233), -1)  # scroll down
        # time.sleep(1)
        mouse.double_click('left', (192, 448))  # wind
        time.sleep(1)
        mouse.click('left', (414, 132))  # add
        time.sleep(1)
        mouse.double_click('left', (280, 60))  # save
        time.sleep(1)
        mouse.double_click('left', (117, 607))  # ok
        time.sleep(1)
        mouse.double_click('left', (253, 227))  # save and close
        time.sleep(1)
        mouse.click('left', (416, 242))  # run
        app.wait_cpu_usage_lower(threshold=3, timeout=3600)
        time.sleep(5)
        mouse.click('left', (799, 465))
        time.sleep(1)
        mouse.click('left', (981, 684))  # select csv format
        time.sleep(1)
        dlg = app.top_window()  # save the file to csv
        dlg.Save.click()
        time.sleep(1)
        dlg.FileNameEdit.type_keys([csv_path])
        dlg.Save.click()
        # if window.child_window(title="Yes").exists(timeout=2):
        #     window.Yes.click()
        time.sleep(15)
        dlg.Close.click()
        if window.child_window(title="Yes", auto_id="CommandButton_6", control_type="Button").exists(
                timeout=3):
            window.Confirm.yes.click()
        time.sleep(2)
        dlg.Close.click()
        if window.child_window(title="Confirm").exists(timeout=3):
            window.Confirm.ok.click()
        if window.child_window(title="Confirm").exists(timeout=3):
            window.Confirm.no.click()


def estimate_load(powerWorld_path=r"E:/PW_V23_64_JAN23_2023/pwrworld.exe",
                  case_path=r"D:\Texas7k_20230131_WithPFWModels_loadscaledmidnight.PWB",
                  load_file=r"D:\fullyearOPF7kNoWeather.tsb",
                  weather_files_path=r"D:\tsb_file_new/*.tsb",
                  output_path=r"D:\GEN_Output_TX",      #changed some stuff to get rid of f-string errors
                  ):
    fileList, Date = get_file(weather_files_path)
    # print(fileList, Date)
    for i, file in enumerate(tqdm(fileList, desc="process data", ncols=100, unit="file")):
        app = Application(backend="uia").start(powerWorld_path)
        window = app.top_window()
        window.set_focus()
        keyboard.send_keys('^o')
        dlg = app.top_window()
        dlg.FileNameEdit.set_edit_text(case_path)
        dlg.Open.child_window(title="Open", auto_id="1", control_type="Button").click()
        window = app.top_window()
        window.set_focus()
        mouse.double_click('left', (35, 136))  # select run mode
        mouse.double_click('left', (410, 60))  # open tool
        mouse.double_click('left', (1032, 116))  # select run mode
        time.sleep(1)
        '---------------------read the load file---------------------'
        app.Texas7k_20230131_WithPFWModels_loadscaledmidnightpwbStatusInitializedSimulator23.ReadTSBFile.click()
        time.sleep(1)
        dlg = app.top_window()  # get the popup window
        tsb_path = os.path.normpath(load_file)
        dlg.FileNameEdit.set_edit_text(tsb_path)
        keyboard.send_keys('%o')
        app.wait_cpu_usage_lower(threshold=2.5, timeout=60)  # wait for file to load
        '---------------------read the weather file---------------------'
        app.Texas7k_20230131_WithPFWModels_loadscaledmidnightpwbStatusInitializedSimulator23.ReadTSBFile.click()
        time.sleep(1)
        app.wait_cpu_usage_lower(threshold=2.5, timeout=60)  # wait for file to load
        dlg = app.top_window()  # get the popup window
        raw_date = re.search(r"[1-3][0-9]{3}", os.path.basename(file))
        csv_path_voltage = fr"D:\GEN_Output_TX\limit\{raw_date[0]}"
        csv_path_percent = fr"D:\GEN_Output_TX\voltage\{raw_date[0]}"
        tsb_path = os.path.normpath(file)
        dlg.FileNameEdit.set_edit_text(tsb_path)  # set_edit_text(tsb_path)
        keyboard.send_keys('%o')
        window = app.top_window()
        window.set_focus()
        if window.child_window(title="Yes", auto_id="CommandButton_6", control_type="Button").exists(timeout=30):
            window.Confirm.yes.click()  # replay the old data
        mouse.click('left', (930, 564))  # select yes
        window = app.top_window()
        app.wait_cpu_usage_lower(threshold=2.5, timeout=60)  # wait for file to load
        GUI = helper.MouseClickRecorder()
        # read the json file
        with open('mouse_move_data/Eastimate_load_positions.json', 'r') as f:
            positions = json.load(f)
            GUI.move_mouse(positions)
        time.sleep(25)
        app.wait_cpu_usage_lower(threshold=1, timeout=11800)  # wait for file to load
        mouse.click('left', (784, 427))
        time.sleep(1)
        mouse.click('left', (848, 650))
        time.sleep(1)
        dlg = app.top_window()  # save the file to csv
        dlg.Save.click()
        time.sleep(1)
        dlg.FileNameEdit.type_keys(csv_path_percent)
        dlg.Save.click()
        time.sleep(25)
        app.wait_cpu_usage_lower(threshold=1, timeout=1200)  # wait for file to load
        '''---------------------save the voltage file---------------------'''
        mouse.click('left', (66, 368))  # select the bus
        time.sleep(1)
        mouse.click('left', (784, 427))
        time.sleep(1)
        mouse.click('left', (848, 650))
        time.sleep(1)
        dlg = app.top_window()  # save the file to csv
        dlg.Save.click()
        time.sleep(1)
        dlg.FileNameEdit.type_keys(csv_path_voltage)
        dlg.Save.click()
        app.wait_cpu_usage_lower(threshold=2, timeout=1200)  # wait for file to load
        mouse.click('left', (1897, 19))
        time.sleep(2)
        mouse.click('left', (1033, 593))
        time.sleep(2)
        mouse.click('left', (1033, 593))


def check_file():
    gauth = GoogleAuth()  # https://docs.iterative.ai/PyDrive2/quickstart/
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    Date = []
    file_list = drive.ListFile(
        {'q': "'1nK38QBemG0bNsKB78mqnCpIEJnruz4YP' in parents and trashed=false"}).GetList()
    for i, file in enumerate(file_list):
        raw_date = re.search(r"([12]\d{3}).(0[1-9]|1[0-2])", file['title'])
        Date.append([date(int(raw_date[1]), int(raw_date[2]), 1), i])
    df = pd.DataFrame(Date, columns=['date', 'index'])
    df_v = pd.date_range(date(1935, 1, 1), date(2022, 3, 1), freq='MS', )
    df['date'] = pd.to_datetime(df['date'])
    df['exist'] = df['date'].isin(df_v.date)
    print(df["exist"])

    df['exist'] = df['exist'].apply(lambda x: 10 if x else 0)
    # fig = calplot(df, x="date", y="exist")
    # fig.show()
    # fig.to_image()
    # print(Date)


if __name__ == '__main__':
    # process_weather_data()
    # import Record_mouse_click as MC
    # helper = MC.MouseClickRecorder()
    # helper.move_mouse(json.load(open('positions.json')))  # import a list of positions
    # time.sleep(10)
    # get_position()
    # estimate_load()
    # get_position()
    post_api = None  # "https://cronitor.link/p/cb436a006559492cadd8beb0a8d6980d/Mc4GDg"
    to_tsb()
    # E:\PW_V23_64_JAN23_2023
    # process_weather_data(powerWorld_path=r"E:/PW_V23_64_JAN23_2023/pwrworld.exe",file_path="D://tsb_file_new/*.tsb")
    # to_tsb(
    #     powerWorld_path=r"E:/PW_V23_64_July26_2022/pwrworld.exe",#r"E:/PW_V23_64_JAN23_2023/pwrworld.exe", #
    #     case_path=r"C:\Users\Thoma\Downloads\B7FLAT.pwb",
    #        file_path=r"D:\multiple_weather_data\*aux")

# years_list = [[[Date[0][0], files[0]]]]
# print(years_list)
# flag1 = True
# repeated = False
# for data in (tqdm(Date, desc="converting file…", ncols=100, unit="file")):
#     if flag1: flag1 = False; continue;
#     date = (data[0].replace(day=1) - timedelta(days=1)).replace(day=1)
#     end_date = (date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(1)
#     start_date = date.replace(day=1) - timedelta(days=1)
#     # print(f'First day{start_date.strftime("%#m/%#d/%Y")}')
#     # print(f'Last day{end_date.strftime("%m/%d/%Y").replace("0", " ")}')
#     # print(f' day{date.strftime("%m/%d/%Y")}')
#     repeated = False
#
#     for i, years in enumerate(years_list):
#         if years[0][0].year == data[0].year:
#             repeated = True
#             years_list[i].append([data[0], files[data[1]]])
#             break
#         # if year don't exist, create new one
#     if not repeated: years_list.append([[data[0], files[data[1]]]])
# for data in years_list:
#     date = (data[-1][0].replace(day=1) - timedelta(days=1)).replace(day=1)
#     start_date = date.replace(day=1) - timedelta(days=1)
#     print(start_date)
# print(*years_list, sep="\n")
# print(files)

# to_tsb(powerWorld_path=r"E:\PW_V23_64_July26_2022\pwrworld.exe",case_path=r"C:\Users\Thoma\Downloads\B7FLAT.pwb")
# print(files[data[1]])
# For printing results

# get_position()
# app = Application(backend="uia").start(r"D:\PW_V23_64_July07_2022\pwrworld.exe")
# window = app.top_window()
# window.set_focus()
# keyboard.send_keys('^o')
# pyautogui.hotkey('ctrl', 'o')

# #app.dialog.wait('visible')
# #dlg = app['Simulator23']
# dlg_spec = app.Dialog#.print_control_identifiers()
# window = app.CaseB7FLATpwbStatusInitializedSimulator23.LoadAuxFile.click()
# dlg = app.top_window()
# dlg.FileNameEdit.set_edit_text(r"D:\2000_01.aux")
# dlg.Open.child_window(title="Open", auto_id="1", control_type="Button").click()
# dlg.Confirm.Yes.click()
# print(app.Dialog.print_control_identifiers())
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
