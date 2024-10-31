#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
from readsettings import ReadSettings
import pandas as pd
import argparse

def read_feva(dataset_path, file_name_b):
    """
    Reads and processes annotation data from FEVA to create a dataframe.
    Parameters:
        dataset_path (str): Path to the folder containing the data.
        file_name_b (str): Filename of the FEVA annotation file.
    Returns:
        pd.DataFrame: Processed data with columns ['id_label', 'left_label', 'video_start', 'video_end'].
    """
    # Load JSON annotation data
    data = pd.read_json(dataset_path + file_name_b)
    res = []
    # Process each data row and format it
    for i in range(len(data) - 6):  # Adjusting the range based on data structure
        a = data["data"][i]
        a[0] = int(a[0])  # Ensure label ID is integer
        del a[3]  # Remove irrelevant data
        res.append(a)
    df = pd.DataFrame(res)
    df = df.sort_values([1], ascending=[True]).reset_index(drop=True)  # Sort by video start time
    df.columns = ['id_label', 'video_start', 'video_end']

    # Read label descriptions from an external CSV file
    label_data = pd.read_csv(dataset_path + 'labels.csv')
    res = []
    # Match label IDs with descriptive names
    for label_id in df['id_label']:
        match = label_data[label_data['id'] == label_id]['label']
        if not match.empty:
            res.append(match.values[0])
        else:
            res.append(None)
    df.insert(1, "left_label", res, True)  # Insert descriptive labels into data

    return df

def main(dataset_path, file_name_b):
    # Load and process data for the "Mask on" and "Mask off" segments
    df_b = read_feva(dataset_path, file_name_b)

    # Filter the data into separate DataFrames for "Mask on" and "Mask off"
    M_on = df_b[df_b['left_label'] == 'Mask_on']
    M_off = df_b[df_b['left_label'] == 'Mask_off']

    # Calculate the total duration for "Mask on" and "Mask off"
    r_on = (M_on['video_end'] - M_on['video_start']).sum()
    r_off = (M_off['video_end'] - M_off['video_start']).sum()

    # Calculate the percentage of time with mask on and off
    mask_off_percentage = (r_off / (r_on + r_off)) * 100
    mask_on_percentage = (r_on / (r_on + r_off)) * 100

    # Display results
    print(f"Percentage of time with mask off (false negatives): {mask_off_percentage:.2f}%")
    print(f"Percentage of time with mask on (true positives): {mask_on_percentage:.2f}%")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Calculate false negative rate of masking algorithm")
    parser.add_argument("dataset_path", type=str, help="Path to the dataset directory")
    parser.add_argument("file_name_b", type=str, help="Name of the FEVA annotation file")

    args = parser.parse_args()

    # Run main function with provided arguments
    main(args.dataset_path, args.file_name_b)
