# Visualization Skill

Create publication-quality, interactive, and accessible visualizations for GCMS data, sensor readings, time series, and scientific plots using Plotly or Matplotlib.

## When to use this skill

Automatically use this skill when the user:
- Mentions plots, charts, graphs, or visualizations
- Needs GCMS chromatogram visualization
- Wants sensor data time series plots
- Requests multi-panel scientific figures
- Asks for interactive dashboards or exploratory plots
- Needs publication-ready figures for papers
- Wants to explore data visually

## Capabilities

### Plotly (Interactive Visualizations)
- Interactive plots with hover tooltips, zoom, and pan
- Multi-panel layouts with linked axes
- Real-time updating plots for live data
- Export to HTML for sharing or embedding
- Range sliders for time series exploration
- 3D plots and animations when needed

### Matplotlib (Static Publication Figures)
- High-resolution figures for papers and reports
- Precise control over every element
- Multi-panel layouts with shared axes
- Custom styling and themes
- Export to PNG, PDF, SVG at publication DPI
- Integration with scientific journals' requirements

## GCMS-Specific Visualizations

**Chromatograms**:
- Time vs intensity plots
- Peak detection and annotation
- Baseline visualization
- Overlaid chromatograms for comparison
- Retention time markers

**Mass Spectra**:
- m/z vs abundance stick plots
- Spectral matching visualization
- Compound identification highlights
- Library comparison overlays

**Quantitative Analysis**:
- Calibration curves with confidence intervals
- Concentration bar charts
- Quality control charts
- Trend analysis over time

## Sensor Data Visualizations

**Time Series**:
- Multiple sensors on same plot
- Zooming and panning for exploration
- Anomaly highlighting
- Moving average overlays
- Event markers and annotations

**Multi-Sensor Comparison**:
- Synchronized time axes
- Correlation heatmaps
- Scatter plots with regression
- Box plots for distribution comparison

## Best Practices (Always Follow)

### Color Schemes
- **Use colorblind-friendly palettes**: viridis, plasma, cividis, colorbrewer
- Avoid red-green combinations
- Use sufficient contrast (WCAG AA standard minimum)
- Include patterns/textures for black & white printing

### Typography & Sizing
- **Minimum font size**: 10pt for axis labels, 12pt for titles
- **Line widths**: 1.5-2.5pt for main lines
- **Marker sizes**: 6-10pt for scatter plots
- **DPI**: 300+ for publication, 100-150 for web

### Labels & Annotations
- Always include axis labels with units
- Add descriptive titles
- Include legends when multiple series
- Use scientific notation appropriately
- Add data source citations when relevant

### Layout & Whitespace
- Use appropriate figure sizes (match target medium)
- Include proper margins and padding
- Align elements cleanly
- Use tight_layout() or constrained_layout in Matplotlib

### Accessibility
- Sufficient color contrast
- Alternative text descriptions
- Keyboard-accessible controls (for Plotly)
- Screen reader compatible labels

## Common Plot Types

**Time Series**: Line plots with proper date formatting
```python
# Plotly
fig = px.line(df, x='timestamp', y='value',
              title='Sensor Reading Over Time')
fig.update_xaxes(title='Time', tickformat='%Y-%m-%d %H:%M')
fig.update_yaxes(title='Temperature (°C)')
```

**Distributions**: Histograms, KDE plots, violin plots, box plots
```python
# Matplotlib
fig, ax = plt.subplots(figsize=(8, 6))
ax.hist(data, bins=30, edgecolor='black', alpha=0.7)
ax.set_xlabel('Value')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of Measurements')
```

**Relationships**: Scatter plots with regression, correlation heatmaps
```python
# Plotly with trendline
fig = px.scatter(df, x='variable1', y='variable2',
                 trendline='ols', title='Correlation Analysis')
```

**Comparisons**: Bar charts, grouped bars, stacked bars
```python
# Matplotlib
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(categories, values, color='steelblue', edgecolor='black')
ax.set_ylabel('Value')
ax.set_title('Comparison Across Groups')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
```

**Heatmaps**: Correlation matrices, pivot tables, spatial data
```python
# Plotly
fig = px.imshow(correlation_matrix, text_auto=True,
                aspect='auto', color_continuous_scale='RdBu_r')
```

**Multi-Panel**: Subplots with consistent styling
```python
# Matplotlib
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
# Plot on each axis: axes[0, 0], axes[0, 1], etc.
# Add panel labels
for i, ax in enumerate(axes.flat):
    ax.text(0.05, 0.95, f'({chr(65+i)})',
            transform=ax.transAxes, fontsize=14, fontweight='bold',
            va='top')
plt.tight_layout()
```

## Code Template Structure

```python
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Colorblind-friendly colors
COLORS = px.colors.qualitative.Safe  # or px.colors.sequential.Viridis

# Configuration for styling
PLOTLY_CONFIG = {
    'font': {'family': 'Arial, sans-serif', 'size': 12},
    'xaxis': {'title': {'font': {'size': 14}}},
    'yaxis': {'title': {'font': {'size': 14}}},
    'title': {'font': {'size': 16}}
}

# Matplotlib style
plt.style.use('seaborn-v0_8-darkgrid')  # or 'seaborn-v0_8-whitegrid'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 13
plt.rcParams['axes.titlesize'] = 15
plt.rcParams['legend.fontsize'] = 11
```

## Output & Saving

**Plotly**:
```python
# Interactive HTML
fig.write_html('plot.html')

# Static image (requires kaleido)
fig.write_image('plot.png', width=1200, height=800, scale=2)
```

**Matplotlib**:
```python
# High-resolution for publication
plt.savefig('figure.png', dpi=300, bbox_inches='tight')

# Vector format for editing
plt.savefig('figure.pdf', bbox_inches='tight')

# Multiple formats
for ext in ['png', 'pdf', 'svg']:
    plt.savefig(f'figure.{ext}', dpi=300, bbox_inches='tight')
```

## Performance Tips

- Use appropriate data reduction for large datasets
- Implement decimation for time series with many points
- Use rasterization in Matplotlib for dense scatter plots
- Aggregate data before plotting when appropriate
- Use webgl rendering in Plotly for large datasets

## Example: GCMS Chromatogram

```python
import plotly.graph_objects as go

def plot_chromatogram(time, intensity, peaks=None, title='GCMS Chromatogram'):
    fig = go.Figure()

    # Main chromatogram
    fig.add_trace(go.Scatter(
        x=time, y=intensity,
        mode='lines',
        name='Intensity',
        line=dict(color='royalblue', width=1.5)
    ))

    # Add detected peaks
    if peaks is not None:
        fig.add_trace(go.Scatter(
            x=time[peaks], y=intensity[peaks],
            mode='markers',
            name='Detected Peaks',
            marker=dict(color='red', size=8, symbol='x')
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Retention Time (min)',
        yaxis_title='Abundance',
        template='plotly_white',
        hovermode='x unified'
    )

    return fig
```

## Example: Multi-Sensor Time Series

```python
import matplotlib.pyplot as plt

def plot_sensors(timestamps, sensor_data_dict):
    fig, axes = plt.subplots(len(sensor_data_dict), 1,
                             figsize=(12, 3*len(sensor_data_dict)),
                             sharex=True)

    if len(sensor_data_dict) == 1:
        axes = [axes]

    for ax, (sensor_name, data) in zip(axes, sensor_data_dict.items()):
        ax.plot(timestamps, data, linewidth=1.5)
        ax.set_ylabel(f'{sensor_name}\n(units)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=10)

    axes[-1].set_xlabel('Time', fontsize=12)
    axes[0].set_title('Multi-Sensor Data', fontsize=14, fontweight='bold')

    plt.tight_layout()
    return fig
```

## Remember

- Choose Plotly for interactive exploration and web sharing
- Choose Matplotlib for publication-ready static figures
- Always use colorblind-friendly palettes
- Include proper labels, titles, and units
- Test plots at target size/resolution
- Add clear legends when showing multiple series
- Consider your audience (scientific paper vs internal dashboard)
