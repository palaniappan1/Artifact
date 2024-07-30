import pandas as pd
import os
import csv


def process_taintbench_results():
    # Initialize counters
    total_ground_truth = 0

    # Directory containing the CSV files
    current_directory = os.path.dirname(os.path.abspath(__file__))
    taintbench_results_folder = os.path.join(current_directory, '..', 'results/taintbench_results')
    output_file = os.path.join(current_directory, '..', 'results/taintbench_stats_new.csv')
    # Dictionary to store counts for each cg_name
    cg_counts = {}

    # Loop through each file in the directory
    for filename in os.listdir(taintbench_results_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(taintbench_results_folder, filename)
            print(filename)
            # Read CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Group by cg_name and sum the counts
            grouped = df.groupby('cg_name').agg({'expected_leaks': 'sum', 'unexpected_leaks': 'sum', 'cg_edges': 'sum',
                                                 'reachable_methods': 'sum'}).reset_index()

            # Iterate through each group
            for index, row in grouped.iterrows():
                cg_name = row['cg_name']
                expected_leaks = row['expected_leaks']
                unexpected_leaks = row['unexpected_leaks']
                cg_edges = row['cg_edges']
                reachable_methods = row['reachable_methods']

                # Update counts in the dictionary
                if cg_name in cg_counts:
                    cg_counts[cg_name]['expected_leaks'] += expected_leaks
                    cg_counts[cg_name]['unexpected_leaks'] += unexpected_leaks
                    cg_counts[cg_name]['cg_edges'] += cg_edges
                    cg_counts[cg_name]['reachable_methods'] += reachable_methods
                else:
                    cg_counts[cg_name] = {'expected_leaks': expected_leaks, 'unexpected_leaks': unexpected_leaks,
                                          'cg_edges': cg_edges, 'reachable_methods': reachable_methods}
            # Accumulate ground_truth counts for all files
            total_ground_truth += df['ground_truth'].iloc[0]

    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['cg_name', 'tp', 'fp', 'precision', 'recall', 'f1_measure', 'cg_edges', 'reachable_methods']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cg_name, counts in cg_counts.items():
            true_positive = counts['expected_leaks']
            false_positive = counts['unexpected_leaks']
            cg_edges = int(counts['cg_edges'] / len(cg_counts))
            reachable_methods = int(counts['reachable_methods'] / len(cg_counts))
            true_negative = total_ground_truth - (true_positive + false_positive)
            false_negative = total_ground_truth - true_positive
            precision = round((true_positive / (true_positive + false_positive)), 2)
            recall = round((true_positive / (true_positive + false_negative)), 2)
            f1_measure = round((2 * precision * recall / (precision + recall)), 2)

            writer.writerow({
                'cg_name': cg_name,
                'tp': true_positive,
                'fp': false_positive,
                # 'tn': true_negative,
                # 'fn': false_negative,
                'precision': precision,
                'recall': recall,
                'f1_measure': f1_measure,
                'cg_edges': cg_edges,
                'reachable_methods': reachable_methods
            })


if __name__ == "__main__":
    process_taintbench_results()
