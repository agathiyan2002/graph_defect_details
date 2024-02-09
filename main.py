import os
import psycopg2
import plotly.graph_objects as go
from decimal import Decimal

# Create a color scale based on the decimal values, defect type, and maximum score
def generate_color(decimal_value, defect_type, max_score):
    try:
        scaled_value = round(float(decimal_value), 1)
        rgb_value = min(
            int(scaled_value / max_score * 255), 255
        )  # Limit to 255 to ensure it is within the valid range
        inverted_rgb_value = (
            255 - rgb_value
        )  # Invert the value to make lower scores lighter and higher scores darker
        colors = {
            1: f"rgb(0, 0, {inverted_rgb_value})",  # Blue
            2: f"rgb(0, {inverted_rgb_value}, 0)",  # Green
            3: f"rgb({inverted_rgb_value}, 0, 0)",  # Red
            4: f"rgb({inverted_rgb_value}, 0, {inverted_rgb_value})",  # Purple
            5: f"rgb({inverted_rgb_value}, {int(inverted_rgb_value/2)}, 0)",  # Orange
            6: f"rgb({inverted_rgb_value}, {inverted_rgb_value}, 0)",  # Yellow
            7: f"rgb(0, {inverted_rgb_value}, {inverted_rgb_value})",  # Cyan
            8: f"rgb({inverted_rgb_value}, 0, {int(inverted_rgb_value/2)})",  # Magenta
            9: f"rgb(0, {int(inverted_rgb_value/2)}, 0)",  # Lime
        }
        return colors[defect_type], scaled_value
    except ValueError as e:
        print(f"Error: {e}")
        return "black", 0.0  # Default color in case of an error


# Establish a connection to the database
try:
    connection = psycopg2.connect(
        user="postgres", password="soft", host="localhost", port="5432", database="test1"
    )

    cursor = connection.cursor()

    # Take input from the user
    roll_id = input("Enter the roll_id: ")

    # Execute a SQL query to select specific columns from the table based on user input
    cursor.execute(
        f"""
        SELECT revolution::numeric, angle::numeric, defecttyp_id, score
        FROM defect_details
        WHERE roll_id = {roll_id}
        ORDER BY angle::numeric, revolution::numeric;
    """
    )

    # Fetch the data
    data = cursor.fetchall()

    # Check if data is available
    if not data:
        print(f"Roll ID {roll_id} is not available.")
    else:
        # Create a scatter plot
        fig = go.Figure()
        legend_labels = set()
        point_gap = 0.5  # Adjust this value to control the gap between points
        for index, row in enumerate(data):
            rev, ang, typ, score = row
            rev_float = float(rev)
            ang_float = float(ang)
            color, scaled_value = generate_color(
                score, typ, 1
            )  # Replace '1' with the maximum score value in your dataset
            defect_type_meaning = {
                1: "lycra",
                2: "hole",
                3: "shut_off",
                4: "needln",
                5: "oil",
                6: "twoply",
                7: "stop_line",
                8: "count_mix",
                9: "two_ply",
            }
            label = f"{defect_type_meaning[typ]} ({scaled_value})"
            legend_labels.add(
                (typ, label, color)
            )  # Collecting the defect type, label, and color for the legend

            fig.add_trace(
                go.Scatter(
                    x=[ang_float + point_gap * index],
                    y=[rev_float + point_gap * index],
                    mode="markers",
                    name=label,
                    marker=dict(color=color, symbol="square", size=20),
                    showlegend=False,
                )
            )

        # Manually create legend items with unique colors
        for typ, label, color in legend_labels:
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(color=color),
                    name=label,
                    showlegend=True,
                )
            )

        fig.update_layout(
            title=f"Roll ID {roll_id}",
            xaxis_title="Angle",
            yaxis_title="Revolution",
            legend_title="Defect Types",
            legend=dict(
                x=1,
                y=1,
                traceorder="normal",
                bgcolor="LightSteelBlue",
                bordercolor="Black",
                borderwidth=2,
            ),
            legend_itemsizing="constant",
            showlegend=True,
        )

        # Save the plot as an HTML file in the download folder
        download_folder = os.path.expanduser("~/Downloads")
        fig.write_html(os.path.join(download_folder, f"plot_{roll_id}.html"))

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    # Close the connection
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
