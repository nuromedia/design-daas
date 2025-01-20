import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_summary(data, column, category, output_dir):
    plt.figure()

    # Plot data from each method
    for method, df in data.items():
        plt.plot(df["CNT"], df[column], linewidth=0.8, label=method)

    # Calculate and plot the mean line across all methods for the category
    all_values = pd.concat([df[column] for df in data.values()])
    mean_value = all_values.mean()
    plt.axhline(y=mean_value, color="r", linestyle="--", label=f"Mean {column}")

    plt.xlabel("Count")
    plt.ylabel(column)
    plt.title(f"Summary Plot for {column} ({category})")
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize="small")
    plt.grid(True)

    # Save the plot as a PDF file
    output_file = os.path.join(output_dir, f"origins_{category}_{column}.pdf")
    plt.savefig(output_file, format="pdf", bbox_inches="tight")
    plt.close()


def main():
    # Directory containing the CSV files
    input_directory = "data/results/csv"

    # Directory to save the summary plots
    output_directory = "data/results/origins"

    # Create the output directory if it does not exist
    os.makedirs(output_directory, exist_ok=True)

    # Columns to plot
    columns_to_plot = [
        "RPS",
        "DIFF",
        "DELAY_CLI",
        "DELAY_BCK",
        "CTXTIME",
        "PROCTIME",
        "AUTHTIME",
    ]

    # Dictionary to hold categorized data
    categorized_data = {}

    # Read and process each CSV file
    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(input_directory, filename)
            df = pd.read_csv(filepath)

            # Sort the dataframe by the 'CNT' column
            df = df.sort_values(by="CNT")

            # Parse the filename to categorize
            parts = filename.split("-")
            origin = parts[0]  # e.g., "curl"
            method = parts[1]  # e.g., "sequence"
            domain = parts[-1].split(".")[0]  # e.g., "baseline3"

            # Create the category name
            category = f"{origin}-{domain}"

            # Store the dataframe in the dictionary under the appropriate category and method
            if category not in categorized_data:
                categorized_data[category] = {}
            categorized_data[category][method] = df

    # Create summary plots for each category and column
    for category, data in categorized_data.items():
        for column in columns_to_plot:
            plot_summary(data, column, category, output_directory)


if __name__ == "__main__":
    print("-- Plotting origins")
    main()
