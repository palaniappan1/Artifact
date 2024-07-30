import pandas as pd
import matplotlib.pyplot as plt
import math
import os
import numpy as np
import matplotlib.colors as mcolors
from scipy.stats import pearsonr

# Get the current directory of aggregate_csv_files.py
current_directory = os.path.dirname(os.path.abspath(__file__))
playstore_results_folder = os.path.join(current_directory, '..', 'results/results_aggregated')
playstore_plots_folder = os.path.join(current_directory, '..', 'plots')

allowed_configurations = ['CHA', 'RTA', 'VTA', 'SPARK', 'T-1o', 'M-2o', 'Z-2o', 's-2c']

configuration_list = [('CHA', 'CHA'), ('RTA', 'RTA'), ('VTA', 'VTA'), ('SPARK', 'SPARK'), ('T-1o', 'T-1obj'),
                      ('M-2o', 'M-2obj'), ('Z-2o', 'Z-2obj'), ('s-2c', 's-2cfa')]

succesful_cases = [('CHA', 20), ('RTA', 15), ('VTA', 13), ('SPARK', 19), ('T-1o', 20),
                   ('M-2o', 20), ('Z-2o', 19), ('s-2c', 20)]

succesful_cases_dict = dict(succesful_cases)

df_headers = ['app_name', 'cg_construction_time', 'analysis_time', 'analysis_memory',
              'num_of_methods_propagated', 'num_edges_propagated']

# Convert the list of tuples into a dictionary
configuration_dict = dict(configuration_list)

rgba_color = [0.12156863, 0.46666667, 0.70588235, 1.0]
hex_color = mcolors.to_hex(rgba_color)


def get_successful_numbers(key):
    return succesful_cases_dict[key]


# Function to get the value given a key
def get_config_name(key):
    return configuration_dict.get(key)


def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df


def get_config_results(directory, name):
    filtered_data = {config: [] for config in allowed_configurations}

    # Loop through each CSV file in the directory
    for filename in os.listdir(directory):
        # Check if the file is a CSV file
        if filename.endswith(".csv"):
            # Create the file path
            filepath = os.path.join(directory, filename)

            # Read CSV file into a DataFrame
            df = pd.read_csv(filepath)

            # Iterate over allowed configurations
            for config in allowed_configurations:
                # Filter data based on configuration
                filtered_df = df[df['cg_name'] == config]

                # Store num_of_methods_propagated and analysis_time for the configuration
                filtered_data[config].extend(
                    filtered_df[['app_name', name, 'analysis_time', 'analysis_memory']].values.tolist())
    return filtered_data


def draw_sub_plots(directory, name):
    filtered_data = get_config_results(directory, name)

    # Create a figure and axes for subplots
    fig, axes = plt.subplots(4, 2, figsize=(12, 16))

    # Flatten axes for easy iteration
    axes = axes.flatten()

    # Create lists to store all x and y values
    all_x_values = []
    all_y_values = []

    # Create a scatter plot for each configuration
    for i, (config, data) in enumerate(filtered_data.items()):
        # Convert filtered data to DataFrame
        filtered_df = pd.DataFrame(data, columns=['app_name', name, 'analysis_time', 'analysis_memory'])
        x_values = filtered_df[name]
        y_values = filtered_df['analysis_time']
        valid_indices = x_values > 0
        x_values = np.log10(x_values[valid_indices])
        y_values = np.log10(y_values[valid_indices])
        axes[i].scatter(x_values, y_values, label=f"{config}", color=hex_color)
        # Append x and y values to the lists
        all_x_values.extend(x_values)
        all_y_values.extend(y_values)
        x_label = ""
        if name == "num_of_methods_propagated":
            x_label = "#Interprocedural Edges"
        else:
            x_label = "#Propagations"
        axes[i].set_xlabel(x_label, fontsize=14)
        axes[i].set_ylabel('Runtime', fontsize=14)
        axes[i].set_title(f'{get_config_name(config)}', fontsize=16, fontweight='bold')
        axes[i].tick_params(axis='y', labelsize=14)
        axes[i].tick_params(axis='x', labelsize=14)
        # Perform polynomial regression on log-transformed data
        coefficients = np.polyfit(x_values, y_values, deg=1)  # Fit a first degree polynomial
        poly = np.poly1d(coefficients)

        # Generate x-values for the regression line
        # line_x = np.linspace(min(x_values), max(x_values), 100)
        line_x = np.unique(x_values)

        # Calculate y-values for the regression line
        line_y = poly(line_x)

        # Plot the regression line on the scatter plot
        axes[i].plot(line_x, line_y, c='#AAAAAA', mfc='#808080', mec='#808080', marker='o', linestyle='dotted',
                     linewidth=2, markersize=2)
    # Set the same limits for all subplots
    min_limit = min(min(all_x_values), min(all_y_values))
    max_limit = max(max(all_x_values), max(all_y_values))
    for ax in axes:
        ax.set_xlim(min_limit, max_limit)
        ax.set_ylim(min_limit, max_limit)
    # Adjust layout
    plt.tight_layout()
    plot_name = ""
    if name == "num_of_methods_propagated":
        plot_name = "scatter_plot_methods"
    else:
        plot_name = "scatter_plot_edges"
    # plt.savefig(os.path.join(plots_folder, plot_name + '.pdf'))
    # Show plot
    plt.show()


def draw_summary_plots(directory):
    # Initialize an empty dictionary to store filtered data for each configuration
    filtered_data = {config: [] for config in allowed_configurations}

    # Loop through each CSV file in the directory
    for filename in os.listdir(directory):
        # Check if the file is a CSV file
        if filename.endswith(".csv"):
            # Create the file path
            filepath = os.path.join(directory, filename)

            # Read CSV file into a DataFrame
            df = pd.read_csv(filepath)

            # Iterate over allowed configurations
            for config in allowed_configurations:
                # Filter data based on configuration
                filtered_df = df[df['cg_name'] == config]

                # Store num_of_methods_propagated and analysis_time for the configuration
                filtered_data[config].extend(
                    filtered_df[
                        ['app_name', 'cg_construction_time', 'analysis_time', 'analysis_memory']].values.tolist())

    fig, ax = plt.subplots(figsize=(10, 8))

    bar_width = 0.6
    index = range(len(allowed_configurations))

    # Assign colors for construction and analysis times
    construction_color = '#CCCCCC'
    analysis_color = '#F2F2F2'

    average_times = []
    average_memory = []
    for i, config in enumerate(allowed_configurations):
        construction_times = [data[1] for data in filtered_data[config]]
        analysis_times = [data[2] for data in filtered_data[config]]
        memory_consumption = [data[3] for data in filtered_data[config]]
        analysis_times = np.array(analysis_times) - np.array(construction_times)
        # Calculate total construction and analysis times for the current configuration
        total_construction_time = sum(construction_times)
        total_memory_consumption = sum(memory_consumption)
        total_analysis_time = sum(analysis_times)
        num_samples = get_successful_numbers(config)

        average_construction_time = total_construction_time / num_samples
        average_analysis_time = total_analysis_time / num_samples
        average_times.append(average_analysis_time)
        average_memory_consumption = total_memory_consumption / num_samples
        average_memory.append(average_memory_consumption / 1024)
        print(config, num_samples, total_analysis_time, average_analysis_time)

        percentage_construction_time = (average_construction_time / average_analysis_time) * 100
        percentage_analysis_time = 100

        # print(config + "\t" + str(average_analysis_time) + "\t" + str(average_construction_time) + "\t" + str(
        #     percentage_construction_time) + "\t" + str(average_memory_consumption))

        # Adjust the plotting part
        # Plot bars for construction time percentage
        bars_construction = ax.bar(i, percentage_construction_time, bar_width, label='Construction Time %',
                                   color=construction_color, edgecolor="black")

        # Plot bars for analysis time percentage on top of construction time percentage
        bars_analysis = ax.bar(i, percentage_analysis_time - percentage_construction_time, bar_width,
                               bottom=percentage_construction_time, label='Analysis Time %', color=analysis_color,
                               edgecolor="black")

        ax.text(i - bar_width * 0.5, 101, str(int(average_analysis_time)), fontsize=18, rotation=0)

    plt.axhline(y=100, color='black', linestyle='dotted', linewidth=1, label="Baseline")
    ax.text(-1.6, 102, "Runtime\n(s)", fontsize=14, color='#606060')

    ax2 = ax.twinx()

    memory_line, = ax2.plot(index, average_memory,
                            marker='o', linestyle='-',
                            color='#FF0000', label='Memory Consumption (GB)')
    print(average_memory)
    ax.set_ylim([0, 110])
    ax.tick_params(axis='y', labelsize=18)
    ax.set_xticks(index)
    config_names = [get_config_name(config) for config in allowed_configurations]
    ax.set_xticklabels(config_names, fontsize=18)

    # Combine legend handles for both bar plots and line plot
    legend_handles = [bars_construction[0], bars_analysis[0], memory_line]
    legend_labels = ['CG Construction Time', 'Taint Analysis Time', 'Memory Consumption']

    legend = ax.legend(legend_handles, legend_labels,
                       loc='upper center', bbox_to_anchor=(0.5, 1.09),
                       ncol=3, fancybox=False, shadow=False, prop={'size': 14})

    ax2.set_ylabel('Memory Consumption (GB)', fontsize=16)
    ax2.tick_params(axis='y', labelcolor='red', labelsize=16)
    ax2.set_ylim([0, 200])

    plt.tight_layout()
    # plt.savefig(os.path.join(plots_folder, 'stacked_times' + '.pdf'))
    plt.show()


def drawPlots():
    draw_sub_plots(playstore_results_folder, "num_of_methods_propagated")
    draw_sub_plots(playstore_results_folder, "num_edges_propagated")
    draw_summary_plots(playstore_results_folder)


if __name__ == "__main__":
    drawPlots()
