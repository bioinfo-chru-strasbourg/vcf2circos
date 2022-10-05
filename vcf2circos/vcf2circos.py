# enable dash only in dash module, disable dash here
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from genericpath import isfile
from itertools import count
import numpy as np
#import colorlover as cl

from config import coord_config, json_config
from IPython.display import HTML
from plotly.graph_objs import *
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#init_notebook_mode(connected=True)

import argparse
from argparse import ArgumentParser

from Complex import Complex
from fig import Figure
import maths
import colors
from time import time

from vcfreader import VcfReader

import vcf
import plotly
import pathlib
import json
import copy

import argparse
from argparse import RawTextHelpFormatter

import pandas as pd

__author__ = 'Jin Cui, Antony Le Bechec'
__version__ = '2.0.0'
__date__ = 'September 18 2022'

if (sys.version_info[0]!=3):
    raise Exception('vcf2circos requires Python 3, your current Python version is {}.{}.{}'.
                    format(sys.version_info[0],sys.version_info[1],sys.version_info[2]))


def run_vcf2circos():

    # DEV

    # print(list(dict(chr_info_pd)["chr_name"]))
    # for i in chr_info_pd.keys():
    #     print(i)
    # for i in chr_info_pd.items():
    #     print(i)
    # print(chr_info_pd.items())
    # chr_info = np.array(chr_info_pd.iloc[:])
    # print(chr_info)
    # exit()

    # Params

    param_previous_format = True
    try:
        input_file = sys.argv[1]
        if os.path.exists(input_file):
            input_format = pathlib.Path(input_file).suffix.replace(".","")
        else:
            param_previous_format = False
    except IndexError:
        param_previous_format = False

    try:
        output_file = sys.argv[2]
        output_format = pathlib.Path(output_file).suffix.replace(".","")
    except IndexError:
        output_file = None
        output_format = None

    try:
        export_file = sys.argv[3]
    except IndexError:
        export_file = ""


    if param_previous_format:

        init_notebook_mode(connected=True)

        print("[INFO] Previous parameters format (Deprecated). Please use --help")

        if input_file:
            print(f"[INFO] Input file: {input_file} (format '{input_format}')")
        if output_file:
            print(f"[INFO] Output file: {output_file} (format '{output_format}')")
        if export_file:
            print(f"[INFO] Export file: {export_file} (format 'json')")

    else:

        # Define args
        parser = argparse.ArgumentParser(prog="python vcf2circos.py", formatter_class=RawTextHelpFormatter)
        parser.add_argument(
            "-i",
            "--input",
            type = str,
            required = True,
            help = "Input file.\nFormat will be autodetected from file path.\nSupported format:\n   'json', 'vcf'",
        )
        parser.add_argument(
            "-o",
            "--output",
            type = str,
            required = True,
            help = """Output file.\nFormat will be autodetected from file path.\nSupported format:\n   'png', 'jpg', 'jpeg', 'webp', 'svg', 'pdf', 'eps', 'json'""",
        )
        parser.add_argument(
            "-e",
            "--export",
            type = str,
            required = False,
            help = """Export file.\nFormat is 'json'.\nGenerate json file from VCF input file""",
        )
        parser.add_argument(
            "-p",
            "--options",
            type = str,
            required = False,
            help = """Options file or string.\nFormat is 'json', either in a file or as a string.""",
        )
        parser.add_argument(
            "-n",
            "--notebook_mode",
            type = bool,
            required = False,
            help = """Notebook mode.\nDefault False""",
        )

        # Parse args
        args = parser.parse_args()

        # Input
        input_file = args.input
        if os.path.exists(input_file):
            input_format = pathlib.Path(input_file).suffix.replace(".","")
            print(f"[INFO] Input file: {input_file} (format '{input_format}')")
        else:
            print(f"[ERROR] No input file '{input_file}")
            exit()

        # Output
        output_file = args.output
        output_format = pathlib.Path(output_file).suffix.replace(".","")
        
        if output_format not in ['html', 'png', 'jpg', 'jpeg', 'webp', 'svg', 'pdf', 'eps', 'json']:
            print(f"[ERROR] Output file format '{output_file}' not supported")
        print(f"[INFO] Output file: {output_file} (format '{output_format}')")

        # Export
        export_file = args.export
        if export_file:
            print(f"[INFO] Export file: {export_file} (format 'json')")

        # Options
        options_input = args.options or {}
        if options_input:
            if os.path.isfile(options_input):
                with open(options_input, 'r') as f:
                    options = json.loads(f.read())
                f.close()
            else:
                try:
                    options = json.loads(options_input)
                except IndexError:
                    options = {}
        else:
            options = {}
        if options:
            print(f"[INFO] Options provided.")
            options["File"] = options_input
        else:
            print(f"[INFO] Options not provided.")

        # Notebook mode
        notebook_mode = args.notebook_mode
        if notebook_mode:
            init_notebook_mode(connected=True)


    # Input

    if input_format in ["vcf", "gz"]:

        vcfreader = VcfReader(filename=input_file, options=options.copy())

        fig_instance = Figure(dash_dict=vcfreader.get_json())

        # Export in vcf2circos JSON
        if export_file:
            vcfreader_export = VcfReader(filename=input_file, options=options.copy())
            if not os.path.exists(os.path.dirname(export_file)):
                os.mkdir(os.path.dirname(export_file))
            f = open(export_file, "w")
            f.write(json.dumps(copy.deepcopy(vcfreader_export.get_json()),indent=4))
            f.close()

    elif input_format in ["json"]:

        fig_instance = Figure(input_json_path=input_file)
    
    else:
    
        print("[ERROR] input format not supported")

    # Fig
    
    fig = fig_instance.fig()

    try:
        if not output_format:
            plot(fig)
        elif output_format in ["html"]:
            if not os.path.exists(os.path.dirname(output_file)):
                os.mkdir(os.path.dirname(output_file))
            plot(fig, filename=output_file)
        elif output_format in ['png', 'jpg', 'jpeg', 'webp', 'svg', 'pdf', 'eps', 'json']:
            if not os.path.exists(os.path.dirname(output_file)):
                os.mkdir(os.path.dirname(output_file))
            plotly.io.write_image(fig, output_file, format=output_format)
        else:
            print("[ERROR] output format not supported")
    except IndexError:
        plot(fig)


# if __name__ == "__main__":
#     t=time()
#     run_vcf2circos()
#     print ('[INFO] total run time:')
#     print ('[INFO] '+str(time()-t)+' sec')
    
def main(): # == "__main__":
    t=time()
    run_vcf2circos()
    print ('[INFO] total run time:')
    print ('[INFO] '+str(time()-t)+' sec')
    

if __name__ == "__main__":
    main()