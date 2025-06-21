import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Define the roadmap topics with icon, label, and year
topics = [
    {"year": "2011", "label": "Foundations", "icon": "💡"},
    {"year": "2013", "label": "Docker", "icon": "🐳"},
    {"year": "2014", "label": "Kubernetes", "icon": "🚢"},
    {"year": "2017", "label": "DevOps", "icon": "⚙️"},
    {"year": "2021", "label": "Copilot", "icon": "🤖"},
    {"year": "2025", "label": "AI Future", "icon": "🧠"}
]

# Set coordinates for each node (evenly spaced, with a zigzag vertical layout)
x_coords = [0, 2, 4, 6, 8, 10]
y_coords = [0, 1, 0, 1, 0, 1]  # Alternate to create a dynamic path

# Create the figure and axis with a modern light background
fig, ax = plt.subplots(figsize=(12, 4))
ax.set_facecolor('#f4f4f4')  # Light grey background

# Define node dimensions
node_width = 1.2
node_height = 0.6

# Function to add a rounded node box with centered text
def add_node(ax, x, y, text):
    # Calculate bottom-left coordinate for the rectangle (centered at x,y)
    bl_x = x - node_width / 2
    bl_y = y - node_height / 2
    box = FancyBboxPatch((bl_x, bl_y), node_width, node_height,
                         boxstyle="round,pad=0.1,rounding_size=10",
                         fc="white", ec="#007ACC", lw=2)
    ax.add_patch(box)
    # Add text with icon, label, and year centered inside the box
    ax.text(x, y, text, ha="center", va="center",
            fontsize=10, fontweight='bold', color="#333333")

# Draw each node with its text
for i, topic in enumerate(topics):
    text = f"{topic['icon']}\n{topic['label']}\n{topic['year']}"
    add_node(ax, x_coords[i], y_coords[i], text)

# Connect the nodes with smooth, curved arrows
for i in range(len(topics) - 1):
    # Define start and end points adjusted to node boundaries
    start = (x_coords[i] + node_width / 2, y_coords[i])
    end = (x_coords[i+1] - node_width / 2, y_coords[i+1])
    # Set arrow curvature: upward arrow gets a positive curve, downward a negative one
    rad = 0.3 if y_coords[i+1] > y_coords[i] else -0.3
    arrow = FancyArrowPatch(start, end,
                            connectionstyle=f"arc3,rad={rad}",
                            arrowstyle='-|>', mutation_scale=20,
                            lw=2, color="#007ACC")
    ax.add_patch(arrow)

# Set limits and remove axes for a cleaner presentation
ax.set_xlim(-1, 11)
ax.set_ylim(-1, 2)
ax.axis("off")
plt.title("Modern Tech Roadmap", fontsize=16, fontweight="bold", color="#333333")
plt.tight_layout()
plt.show()
