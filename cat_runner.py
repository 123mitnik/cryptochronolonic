import pandas as pd
import os

class HistWorker:

    currentHists = {}
    
    def get_hist_files():
        histFiles = os.listdir(os.path.join(os.path.dirname(__file__), 'histories'))
        return histFiles

    def get_data_frame(fname):
        frame = pd.read_csv('./histories/'+fname)
        return frame

    def append_coin_to_col_names(df, c_name):
        
    def get_file_symbol(f):
    f = f.split("_", 2)
    return f[1]
    
    def combine_frames():
        fileNames = get_hist_files()
        df_list = []
        for x in range(0,len(fileNames)):
            df = get_data_frame(fileNames[x])
            col_prefix = get_file_symbol(fileNames[x])
            df.rename(columns = lambda x: col_prefix+'_'+x, inplace=True)
            df_list.append(df)
        main = df_list[0]

        for i in range(1, len(df_list)):
            main = main.join(df_list[i])
        
        return main
    def __init__(self):
        self.data_full = self.combine_frames()
        return

    
