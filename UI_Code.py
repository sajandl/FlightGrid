import os
import tkinter as tk
from tkinter import filedialog
import Drone_Grid_UI


class GridInputUI:
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.output_file = None
        self.master.title('Grid Parameters')
        self.master.columnconfigure(2, weight=1)
        self.master.config(padx=11, pady=11)
        self.init_ui()

    def file_select(self):
        self.output_file = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('csv', '*.csv'), ('CSV', '*.CSV')],
            initialdir=os.getcwd(),
            parent=self.master,
            title='Select output file location'
        )
        self.collect_parameters()
        Drone_Grid_UI.write_file(self.calced_points)

    def collect_parameters(self):
        self.lat = float(self.lat_entry.get())
        self.lat_h = float(self.lat_h_entry.get())
        self.lon = float(self.lon_entry.get())
        self.lon_h = float(self.lon_h_entry.get())
        self.alt = int(self.alt_entry.get())
        self.head = int(self.head_entry.get())
        self.len_p = int(self.len_p_entry.get())
        self.len_h = int(self.len_h_entry.get())
        self.overlap = int(self.overlap_entry.get())
        self.sample = int(self.overlap_entry.get())
        if self.direction_str.get() == 'To Right':
            self.direction = 1
        else:
            self.direction = -1
        if self.mode_str.get() == 'Photo':
            self.mode = 1
        else:
            self.mode = 0
        if self.contour_str.get() == 'Follow Contour':
            self.contour = 1
        else:
            self.contour = 0
        if self.north_str.get() == 'True North':
            self.north = 1
        else:
            self.north = 0

        self.calced_points = Drone_Grid_UI.calculate_points(
            lat=self.lat,
            lat_h=self.lat_h,
            lon=self.lon,
            lon_h=self.lon_h,
            altitude=self.alt,
            heading_input=self.head,
            length_p=self.len_p,
            length_h=self.len_h,
            overlap=self.overlap,
            sample=self.overlap,
            direction=self.direction,
            mode=self.mode,
            output_file=self.output_file,
            contour=self.contour,
            north=self.north
        )

    def init_ui(self):
        # create labels for entry boxes
        self.lat_lbl = tk.Label(self.master, text='Latitude Start/Home')
        self.lon_lbl = tk.Label(self.master, text='Longitude Start/Home')
        self.alt_lbl = tk.Label(
            self.master,
            text='Altitude above home position (ft)'
        )
        self.head_lbl = tk.Label(
            self.master,
            text='Initial Heading (North=0)'
        )
        self.len_p_lbl = tk.Label(self.master,
                                  text='Length perpendicular to Heading (ft)')
        self.len_h_lbl = tk.Label(
            self.master,
            text='Length in direction of Heading (ft)'
        )
        self.overlap_lbl = tk.Label(self.master, text='Overlap Percent')
        self.sample_lbl = tk.Label(self.master, text='# Contour Samples btw Points')
        self.direction_lbl = tk.Label(self.master, text='Column Direction w/r Heading')
        self.mode_lbl = tk.Label(self.master, text='Mode Selection')
        self.contour_lbl = tk.Label(self.master, text='Elevation Mode')
        self.north_lbl = tk.Label(self.master, text='True or Magnetic North')
        # labels for displayed values
        self.col_lbl = tk.Label(self.master, text='Columns', bg='darkblue',
                                fg='white')
        self.row_lbl = tk.Label(self.master, text='Rows', bg='darkblue',
                                fg='white')
        self.area_lbl = tk.Label(self.master, text='Area (acres)',
                                 bg='darkblue', fg='white')
        self.route_len_lbl = tk.Label(
            self.master,
            text='Route Length (miles)',
            bg='darkblue', fg='white'
        )
        self.col_ol_lbl = tk.Label(self.master, text='Column Overlap (%)',
                                   bg='darkblue', fg='white')
        self.row_ol_lbl = tk.Label(self.master, text='Row Overlap (%)',
                                   bg='darkblue', fg='white')
        self.home_lbl = tk.Label(self.master, text='Home Point', bg='darkblue',
                                 fg='white')
        self.c1_lbl = tk.Label(self.master, text='Start Corner', bg='darkblue',
                               fg='white')
        self.c2_lbl = tk.Label(self.master, text='Second Corner',
                               bg='darkblue', fg='white')
        self.c3_lbl = tk.Label(self.master, text='Third Corner', bg='darkblue',
                               fg='white')
        self.c4_lbl = tk.Label(self.master, text='Fourth Corner',
                               bg='darkblue', fg='white')

        # create entry boxes for parameters
        self.lat_entry = tk.Entry(self.master)
        self.lat_h_entry = tk.Entry(self.master)
        self.lon_entry = tk.Entry(self.master)
        self.lon_h_entry = tk.Entry(self.master)
        self.alt_entry = tk.Entry(self.master)
        self.head_entry = tk.Entry(self.master)
        self.len_p_entry = tk.Entry(self.master)
        self.len_h_entry = tk.Entry(self.master)
        self.overlap_entry = tk.Entry(self.master)
        self.sample_entry = tk.Entry(self.master)
        self.direction_str = tk.StringVar(self.master)
        self.direction_str.set('To Right')
        self.direction_opmenu = tk.OptionMenu(
            self.master,
            self.direction_str,
            'To Right',
            'To Left'
        )
        self.mode_str = tk.StringVar(self.master)
        self.mode_str.set('Photo')
        self.mode_opmenu = tk.OptionMenu(
            self.master,
            self.mode_str,
            'Photo',
            'Video'
        )
        self.contour_str = tk.StringVar(self.master)
        self.contour_str.set('Follow Contour')
        self.contour_opmenu = tk.OptionMenu(
            self.master,
            self.contour_str,
            'Follow Contour',
            'Constant'
        )
        self.north_str = tk.StringVar(self.master)
        self.north_str.set('True North')
        self.north_opmenu = tk.OptionMenu(
            self.master,
            self.north_str,
            'True North',
            'Magnetic North'
        )
        # create display values button
        self.display_vals_btn = tk.Button(
            self.master,
            text='Display Values',
            command=self.display_values,
            pady=11,
            padx=11
        )
        # create output file button
        self.output_btn = tk.Button(
            self.master,
            text='Create File',
            command=self.file_select,
            pady=11,
            padx=11
        )

        # add labels to the master window
        self.lat_lbl.grid(row=1, column=1, sticky=tk.E)
        self.lon_lbl.grid(row=2, column=1, sticky=tk.E)
        self.alt_lbl.grid(row=3, column=1, sticky=tk.E)
        self.head_lbl.grid(row=4, column=1, sticky=tk.E)
        self.len_p_lbl.grid(row=5, column=1, sticky=tk.E)
        self.len_h_lbl.grid(row=6, column=1, sticky=tk.E)
        self.overlap_lbl.grid(row=7, column=1, sticky=tk.E)
        self.sample_lbl.grid(row=8, column=1, sticky=tk.E)
        self.direction_lbl.grid(row=9, column=1, sticky=tk.E)
        self.mode_lbl.grid(row=10, column=1, sticky=tk.E)
        self.contour_lbl.grid(row=11, column=1, sticky=tk.E)
        self.north_lbl.grid(row=12, column=1, sticky=tk.E)
        # add labels for displayed values to the master window
        self.col_lbl.grid(row=13, column=1, sticky=tk.E)
        self.row_lbl.grid(row=14, column=1, sticky=tk.E)
        self.area_lbl.grid(row=15, column=1, sticky=tk.E)
        self.route_len_lbl.grid(row=16, column=1, sticky=tk.E)
        self.col_ol_lbl.grid(row=17, column=1, sticky=tk.E)
        self.row_ol_lbl.grid(row=18, column=1, sticky=tk.E)
        self.home_lbl.grid(row=19, column=1, sticky=tk.E)
        self.c1_lbl.grid(row=20, column=1, sticky=tk.E)
        self.c2_lbl.grid(row=21, column=1, sticky=tk.E)
        self.c3_lbl.grid(row=22, column=1, sticky=tk.E)
        self.c4_lbl.grid(row=23, column=1, sticky=tk.E)

        # add entry boxes to the master window
        self.lat_entry.grid(row=1, column=2, sticky=tk.EW)
        self.lat_h_entry.grid(row=1, column=3, sticky=tk.EW)
        self.lon_entry.grid(row=2, column=2, sticky=tk.EW)
        self.lon_h_entry.grid(row=2, column=3, sticky=tk.EW)
        self.alt_entry.grid(row=3, column=2, sticky=tk.EW)
        self.head_entry.grid(row=4, column=2, sticky=tk.EW)
        self.len_p_entry.grid(row=5, column=2, sticky=tk.EW)
        self.len_h_entry.grid(row=6, column=2, sticky=tk.EW)
        self.overlap_entry.grid(row=7, column=2, sticky=tk.EW)
        self.sample_entry.grid(row=8, column=2, sticky=tk.EW)
        self.direction_opmenu.grid(row=9, column=2, sticky=tk.EW)
        self.mode_opmenu.grid(row=10, column=2, sticky=tk.EW)
        self.contour_opmenu.grid(row=11, column=2, sticky=tk.EW)
        self.north_opmenu.grid(row=12, column=2, sticky=tk.EW)

        # add display values button
        self.display_vals_btn.grid(row=24, column=3, sticky=tk.EW)
        # add create file button
        self.output_btn.grid(row=25, column=3, sticky=tk.EW)
        # create labels which house the values, to be displayed
        self.colval_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                   relief='sunken')
        self.rowval_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                   relief='sunken')
        self.areaval_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                    relief='sunken')
        self.routeval_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                     relief='sunken')
        self.col_ol_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                   relief='sunken')
        self.row_ol_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                   relief='sunken')
        self.homeval_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                    relief='sunken')
        self.c1val_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                  relief='sunken')
        self.c2val_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                  relief='sunken')
        self.c3val_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                  relief='sunken')
        self.c4val_lbl = tk.Label(self.master, bg='darkgrey', fg='white',
                                  relief='sunken')
        # add labels which house the values, to the master window
        self.colval_lbl.grid(row=13, column=2, sticky=tk.EW)
        self.rowval_lbl.grid(row=14, column=2, sticky=tk.EW)
        self.areaval_lbl.grid(row=15, column=2, sticky=tk.EW)
        self.routeval_lbl.grid(row=16, column=2, sticky=tk.EW)
        self.col_ol_lbl.grid(row=17, column=2, sticky=tk.EW)
        self.row_ol_lbl.grid(row=18, column=2, sticky=tk.EW)
        self.homeval_lbl.grid(row=19, column=2, sticky=tk.EW)
        self.c1val_lbl.grid(row=20, column=2, sticky=tk.EW)
        self.c2val_lbl.grid(row=21, column=2, sticky=tk.EW)
        self.c3val_lbl.grid(row=22, column=2, sticky=tk.EW)
        self.c4val_lbl.grid(row=23, column=2, sticky=tk.EW)

    def display_values(self):
        self.collect_parameters()
        output_values = self.calc_output_values()
        # add text to labels to show the output values
        self.colval_lbl.config(text=output_values['columns'])
        self.rowval_lbl.config(text=output_values['rows'])
        self.areaval_lbl.config(text=output_values['area'])
        self.routeval_lbl.config(text=output_values['route_length'])
        self.homeval_lbl.config(text='{} {}'.format(*output_values['home']))
        self.c1val_lbl.config(text='{} {}'.format(*output_values['c1']))
        self.col_ol_lbl.config(text=output_values['col_ol'])
        self.row_ol_lbl.config(text=output_values['row_ol'])
        self.c2val_lbl.config(text='{} {}'.format(*output_values['c2']))
        self.c3val_lbl.config(text='{} {}'.format(*output_values['c3']))
        self.c4val_lbl.config(text='{} {}'.format(*output_values['c4']))

    def calc_output_values(self):
        lat_h = self.calced_points[0]
        lon_h = self.calced_points[1]
        columns = self.calced_points[4]
        rows = self.calced_points[8]
        length_h = self.calced_points[12]
        length_p = self.calced_points[13]
        a_overlap_h = self.calced_points[14]
        a_overlap_p = self.calced_points[15]
        lat = self.calced_points[17]
        lon = self.calced_points[18]
        lat_b2 = self.calced_points[22]
        lon_b2 = self.calced_points[23]
        lat_b3 = self.calced_points[24]
        lon_b3 = self.calced_points[25]
        lat_b4 = self.calced_points[26]
        lon_b4 = self.calced_points[27]
        route_length_f = self.calced_points[28]

        area = round(length_p * length_h / 43560, 1)
        route_length = round(route_length_f / 5280, 1)
        col_overlap = round(a_overlap_p, 1)
        row_overlap = round(a_overlap_h, 1)
        home = (round(lat_h, 6), round(lon_h, 6))
        c1 = (round(lat, 6), round(lon, 6))
        c2 = (round(lat_b2, 6), round(lon_b2, 6))
        c3 = (round(lat_b3, 6), round(lon_b3, 6))
        c4 = (round(lat_b4, 6), round(lon_b4, 6))

        vals_dictionary = {
            'columns': columns,
            'rows': rows,
            'area': area,
            'route_length': route_length,
            'col_ol': col_overlap,
            'row_ol': row_overlap,
            'home': home,
            'c1': c1,
            'c2': c2,
            'c3': c3,
            'c4': c4
        }
        return vals_dictionary