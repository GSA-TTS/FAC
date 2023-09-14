import openpyxl
import glob

folder_path = '../output/excel/xlsx'

for filename in glob.glob(f'{folder_path}/*.xlsx'):
    print(f'File: {filename}')
    wb = openpyxl.load_workbook(filename)

    for sheet in wb._sheets:
        nrows = sheet.max_row
        print(f'Sheet {sheet.title} has {nrows} rows')
