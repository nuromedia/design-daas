import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_summary(data, column, origin, method, output_dir):
    plt.figure()

    # Define colors for domains
    line_styles = {"0": "-", "1": "--", "2": ":"}  # Solid, dashed, dotted
    colors = {
        "0": "black",
        "1": "orange",
        "2": "lightblue",
        "3": "lightgreen",
        "4": "red",
        "5": "blue",
        "6": "green",
    }

    # Create a mapping for domain colors
    domains = sorted(list(set(data.keys())))
    domain_colors = {domain: colors[f"{i}"] for i, domain in enumerate(domains)}

    # Plot data from each domain
    for domain, df in data.items():
        label = f"{domain}"
        color = domain_colors[domain]

        plt.plot(
            df["CNT"],
            df[column],
            label=label,
            linewidth=0.8,
            linestyle="-",
            color=color,
        )

    plt.xlabel("Count")
    plt.ylabel(column)
    plt.title(f"Summary Plot for {column} ({origin}-{method})")

    # Sort the legend labels
    handles, labels = plt.gca().get_legend_handles_labels()
    sorted_labels, sorted_handles = zip(
        *sorted(zip(labels, handles), key=lambda t: t[0])
    )
    plt.legend(
        sorted_handles,
        sorted_labels,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize="small",
    )

    plt.grid(True)

    # Save the plot as a PDF file
    output_file = os.path.join(
        output_dir, f"methods_{origin}_{method}_{column}.pdf"
    )
    plt.savefig(output_file, format="pdf", bbox_inches="tight")
    plt.close()


def main():
    # Directory containing the CSV files
    input_directory = "data/results/csv"

    # Directory to save the summary plots
    output_directory = "data/results/methods"

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

            # Create the key for the combination
            combination_key = (origin, method, domain)

            # Store the dataframe in the dictionary under the appropriate origin and method
            if origin not in categorized_data:
                categorized_data[origin] = {}
            if method not in categorized_data[origin]:
                categorized_data[origin][method] = {}
            categorized_data[origin][method][domain] = df

    # Create summary plots for each column, origin, and method
    for origin, methods in categorized_data.items():
        for method, domains in methods.items():
            for column in columns_to_plot:
                plot_summary(domains, column, origin, method, output_directory)


if __name__ == "__main__":
    print("-- Plotting methods")
    main()
