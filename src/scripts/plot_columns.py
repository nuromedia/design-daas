import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_data(df, column, filename, output_dir):
    plt.figure()

    # Plot the column data
    plt.plot(df["CNT"], df[column], linewidth=0.8, label=f"{column}")

    # Calculate and plot the mean line
    mean_value = df[column].mean()
    plt.axhline(y=mean_value, color="r", linestyle="--", label=f"Mean {column}")

    plt.xlabel("Count")
    plt.ylabel(column)
    plt.title(f"{column} over Count for {filename}")
    plt.legend()
    plt.grid(True)

    # Save the plot as a PDF file
    output_file = os.path.join(
        output_dir, f"{os.path.splitext(filename)[0]}_{column}.pdf"
    )
    plt.savefig(output_file, format="pdf")
    plt.close()


def main():
    # Directory containing the CSV files
    input_directory = "data/results/csv"

    # Directory to save the summary plots
    output_directory = "data/results/columns"

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

    # Read and process each CSV file
    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(input_directory, filename)
            df = pd.read_csv(filepath)

            # Sort the dataframe by the 'CNT' column
            df = df.sort_values(by="CNT")

            # Plot each column
            for column in columns_to_plot:
                plot_data(df, column, filename, output_directory)


if __name__ == "__main__":
    print("-- Plotting columns")
    main()
