import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Set page config
st.set_page_config(page_title="DIPS Salary-Performance Dashboard", layout="wide")

# Display logo
st.image(st.secrets["logo_url"], width=275)

# Load data
@st.cache_data
def load_data():
    salary_df = pd.read_csv(st.secrets["salary_data_url"])
    standings_df = pd.read_csv(st.secrets["standings_data_url"])
    return salary_df, standings_df

salary_df, standings_df = load_data()

# Extract year from standings data
year = standings_df['Year'].iloc[0]

# Main title and subtitle
st.title("Max Salary vs Team Performance")
st.subheader(f"{year} Season")

# Add controls
col1, col2, col3 = st.columns(3)

with col1:
    available_weeks = sorted(standings_df['Week'].unique())
    selected_week = st.selectbox("Select Week", available_weeks, index=len(available_weeks)-1)

with col2:
    x_options = {
        'max': 'Salary of highest-cost player',
        'max_rank': 'Salary of highest-cost player, ranked',
        'variance': 'Variance of roster salaries'
    }
    x_column = st.selectbox("Select X-axis", options=list(x_options.keys()), format_func=lambda x: x_options[x])

with col3:
    y_options = {
        'pwr_rating': 'CBSSports Power Rating',
        'pwr_rank': 'CBSSports Power Rating, ranked',
        'PF': 'Points For, season to date'
    }
    y_column = st.selectbox("Select Y-axis", options=list(y_options.keys()), format_func=lambda y: y_options[y])

# Process data
selected_standings = standings_df[standings_df['Week'] == selected_week]
merged_df = pd.merge(selected_standings, salary_df, on='Owner')

# Determine if axes should be inverted
invert_y = y_column == 'pwr_rank'
invert_x = x_column == 'max_rank'

# Create scatter plot
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=merged_df[x_column],
    y=merged_df[y_column],
    mode='markers+text',
    marker=dict(
        size=10,
        color=merged_df[y_column],
        colorscale='bluered',
        reversescale=invert_y,  # Reverse color scale if y-axis is inverted
        showscale=False,
        line=dict(width=0.5, color='gray')  # Add outline to points
    ),
    text=merged_df['Owner'],
    textposition='bottom right',  # Position text above and to the right of markers
    textfont=dict(size=11),
    hoverinfo='text',
    hovertext=[f"{owner}<br>{x_column}: {x:.2f}<br>{y_column}: {y:.2f}" 
               for owner, x, y in zip(merged_df['Owner'], merged_df[x_column], merged_df[y_column])],
    showlegend=False
))

# Add trend line
x = merged_df[x_column]
y = merged_df[y_column]
z = np.polyfit(x, y, 1)
p = np.poly1d(z)

fig.add_trace(go.Scatter(
    x=x,
    y=p(x),
    mode='lines',
    line=dict(color='red', width=2),
    showlegend=False
))

# Calculate appropriate ranges with 5% padding
x_range = [x.min() - 0.05 * (x.max() - x.min()), x.max() + 0.05 * (x.max() - x.min())]
y_range = [y.min() - 0.05 * (y.max() - y.min()), y.max() + 0.05 * (y.max() - y.min())]

# Invert axes if needed
if invert_y:
    y_range = y_range[::-1]
if invert_x:
    x_range = x_range[::-1]

# Update layout
fig.update_layout(
    xaxis_title=x_options[x_column],
    yaxis_title=y_options[y_column],
    width=800,
    height=600,
    plot_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='lavender', range=x_range),
    yaxis=dict(showgrid=True, gridcolor='lavender', range=y_range)
)

# Add subtitle with specific axis labels
subtitle = f'{y_options[y_column]} vs {x_options[x_column]} - Week {selected_week}'
fig.add_annotation(
    text=f'<b>{subtitle}</b>',  # Bold text
    xref="paper", yref="paper",
    x=0.5, y=1.05,
    showarrow=False,
    font=dict(size=16),
    align="center",
)

# Display the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Display equation below the graph
# Display centered equation below the graph
# equation = f"Trend line equation: y = {z[0]:.2f}x + {z[1]:.2f}"
# st.markdown(f"<p style='text-align: center;'>{equation}</h4>", unsafe_allow_html=True)
