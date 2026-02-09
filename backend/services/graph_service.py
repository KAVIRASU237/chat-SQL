import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import matplotlib

# Set non-interactive backend to avoid UI issues in backend
matplotlib.use('Agg')

class GraphGeneratorService:
    def __init__(self):
        pass

    def generate_graph(self, columns, rows):
        """
        Generates a graph based on the provided data.
        Returns a base64 encoded string of the PNG image.
        """
        if not rows or not columns:
            return None

        # Create DataFrame
        df = pd.DataFrame(rows, columns=columns)

        # Identify potential X and Y axes
        # Heuristic:
        # X-axis: First non-numeric column (categorical) or date, or index if all numeric
        # Y-axis: All numeric columns
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()

        if not numeric_cols:
            return None # Cannot plot without numeric data

        x_col = None
        if non_numeric_cols:
            x_col = non_numeric_cols[0] # Pick first categorical column as X
        
        # Decide Chart Type
        plt.figure(figsize=(10, 6))
        
        # Style
        # plt.style.use('ggplot') # Optional: make it look nicer

        chart_type = "bar" # Default
        
        if x_col:
            # If we have an X column
            unique_vals = df[x_col].nunique()
            if unique_vals > 20:
                # Too many categories for vertical bar, maybe line or horizontal bar?
                # If sorted, line might be good.
                chart_type = "line"
            elif unique_vals < 5 and len(numeric_cols) == 1:
                # Few categories, single metric -> Pie chart option
                # But bar is safer. Let's stick to Bar/Line for now to be robust.
                chart_type = "bar"
        else:
            # No categorical X, just use index
            chart_type = "line"

        # Plotting
        try:
            if chart_type == "bar":
                if x_col:
                    x_data = df[x_col].astype(str).tolist()
                    # Plot each numeric column
                    for y_col in numeric_cols:
                        plt.bar(x_data, df[y_col], label=y_col, alpha=0.7)
                    plt.xlabel(x_col)
                    plt.xticks(rotation=45, ha='right')
                else:
                    # Index based bar
                    for y_col in numeric_cols:
                        plt.bar(df.index, df[y_col], label=y_col, alpha=0.7)

            elif chart_type == "line":
                if x_col:
                    # Sort by X for line chart to make sense
                    # df = df.sort_values(by=x_col) # Sorting might break intended order
                    x_data = df[x_col].astype(str).tolist()
                    for y_col in numeric_cols:
                        plt.plot(x_data, df[y_col], marker='o', label=y_col)
                    plt.xlabel(x_col)
                    plt.xticks(rotation=45, ha='right')
                else:
                    for y_col in numeric_cols:
                        plt.plot(df.index, df[y_col], marker='o', label=y_col)

            plt.title("Query Result Visualization")
            plt.legend()
            plt.tight_layout()

            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            return image_base64

        except Exception as e:
            print(f"Error generating graph: {e}")
            plt.close()
            return None
