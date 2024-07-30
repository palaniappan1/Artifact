import pandas as pd
import os
import sys

# Get the current directory of aggregate_csv_files.py
current_directory = os.path.dirname(os.path.abspath(__file__))
playstore_results_folder = os.path.join(current_directory, '..', 'results/playstore_results')
aggregated_playstore_results_folder = os.path.join(current_directory, '..',
                                                   'results/results_aggregated')


def aggregate_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)

    # Define the custom aggregator
    custom_agg = {
        'app_name': 'first',
        'ground_truth': 'first',  # Keep the first value
        'analysis_time': 'mean',
        'no_of_leaks': 'max',
        'cg_edges': 'max',
        'analysis_memory': 'mean',
        'cg_construction_time': 'mean',
        'reachable_methods': 'max',
        'num_of_methods_propagated': 'max',
        'num_edges_propagated': 'max'
    }

    # Group by 'cg_name' and apply the custom aggregation
    agg_df = df.groupby('cg_name').agg(custom_agg).reset_index()

    # Sort the DataFrame by 'cg_edges' in descending order
    sorted_df = agg_df.sort_values(by='cg_edges', ascending=False).reset_index(drop=True)

    # Round all decimal values to 2 places
    sorted_df = sorted_df.round(decimals=2)

    csv_write_path = os.path.join(aggregated_playstore_results_folder,
                                  sorted_df['app_name'].iloc[0] + '_aggregated' + '.csv')

    sorted_df.to_csv(csv_write_path, index=False)


def aggregate_all_csv():
    for filename in os.listdir(playstore_results_folder):
        if filename.endswith("csv"):
            file_path = os.path.join(playstore_results_folder, filename)
            if os.path.isfile(file_path):
                aggregate_csv(file_path)


if __name__ == "__main__":
    aggregate_all_csv()
