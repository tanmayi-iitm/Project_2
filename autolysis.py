import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API with proxy
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    print("Error: AIPROXY_TOKEN not set in environment variables.")
    sys.exit(1)

openai.api_key = AIPROXY_TOKEN
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"

# Check for CSV filename
csv_file = input("Enter the name of the CSV file: ").strip() # Replace with sys.argv[1] if needed

if not os.path.exists(csv_file):
    print(f"Error: File '{csv_file}' not found.")
    sys.exit(1)

# Load the dataset
data = pd.read_csv(csv_file)

# Perform exploratory data analysis
def analyze_dataset(df):
    analysis = {
        "summary": df.describe(include="all").to_dict(),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
    }
    return analysis

analysis = analyze_dataset(data)

# Generate visualizations
def create_visualizations(df):
    visualizations = []

    # Example: Histogram of the first numerical column
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[numeric_cols[0]], kde=True)
        plt.title(f"Distribution of {numeric_cols[0]}")
        plt.savefig("histogram.png")
        visualizations.append("histogram.png")

    # Example: Correlation heatmap
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 6))
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm")
        plt.title("Correlation Heatmap")
        plt.savefig("correlation_heatmap.png")
        visualizations.append("correlation_heatmap.png")

    return visualizations

visualizations = create_visualizations(data)

# Generate narrative using LLM
def generate_narrative(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"].strip()

prompt = (
    f"You are a data analyst. Based on the dataset columns: {analysis['columns']} and insights: {analysis['summary']}, "
    "write a narrative explaining the key trends, outliers, and patterns in the data. Include potential use cases "
    "or implications of the analysis."
)

narrative = generate_narrative(prompt)

# Create README.md

def create_readme(narrative, visualizations):
    try:
        with open("README.md", "w") as f:
            f.write("# Automated Data Analysis Report\n\n")
            f.write(narrative + "\n\n")
            for viz in visualizations:
                f.write(f"![{viz}]({viz})\n")
        print("README.md file created successfully.")
    except Exception as e:
        print("Error creating README.md:", e)

create_readme(narrative, visualizations)
print("Analysis complete. Results saved to README.md and visualizations as PNG files.")
