import matplotlib.pyplot as plt
from utils.astro_utils import AstroUtils
from matplotlib.patches import Rectangle

def plot_north_indian_chart(planet_positions, lagna_sign):
    zodiac_signs = AstroUtils.get_zodiac_signs()
    # House order and coordinates as per the user's image
    house_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    coords = [
        (5, 5),   # 1 (center)
        (5, 9),   # 2 (top)
        (1, 9),   # 3 (top-left corner)
        (1, 5),   # 4 (left)
        (1, 1),   # 5 (bottom-left corner)
        (5, 1),   # 6 (bottom)
        (5, 3),   # 7 (bottom-center)
        (9, 1),   # 8 (bottom-right corner)
        (9, 5),   # 9 (right)
        (9, 9),   # 10 (top-right corner)
        (7, 7),   # 11 (top-center-right)
        (3, 7),   # 12 (top-center-left)
    ]
    # Adjust house numbers for lagna_sign (Lagna always at center)
    house_numbers = [((lagna_sign + i - 1) % 12) + 1 for i in range(12)]

    # Prepare planet text for each house
    house_planets = {i+1: [] for i in range(12)}
    for planet, pos in planet_positions.items():
        house_planets[pos['house']].append(planet[:2])  # Use short name

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Draw the square
    ax.plot([1, 9], [1, 1], color='black')
    ax.plot([9, 9], [1, 9], color='black')
    ax.plot([9, 1], [9, 9], color='black')
    ax.plot([1, 1], [9, 1], color='black')
    # Draw the main diagonals
    ax.plot([1, 9], [1, 9], color='black')
    ax.plot([1, 9], [9, 1], color='black')
    # Draw the 'X' diagonals (from midpoints)
    ax.plot([1, 5], [5, 9], color='black')
    ax.plot([5, 9], [9, 5], color='black')
    ax.plot([9, 5], [5, 1], color='black')
    ax.plot([5, 1], [1, 5], color='black')

    # Place house numbers and planets
    for i, (x, y) in enumerate(coords):
        house_num = house_order[i]
        ax.text(x, y, f'{house_num}', ha='center', va='center', fontsize=14, color='black', fontweight='bold')
        # If you want to show planets, uncomment below:
        # planets = ' '.join(house_planets[house_num])
        # ax.text(x, y-0.5, planets, ha='center', va='center', fontsize=10, color='green')

    plt.tight_layout()
    return fig

def plot_south_indian_chart(planet_positions, lagna_sign):
    zodiac_signs = AstroUtils.get_zodiac_signs()
    # South Indian chart house order (fixed, starting from top-left, going clockwise)
    house_coords = [
        (0, 3), (1, 3), (2, 3), (3, 3),
        (3, 2), (3, 1), (3, 0), (2, 0),
        (1, 0), (0, 0), (0, 1), (0, 2)
    ]
    house_order = [((lagna_sign + i) % 12) + 1 for i in range(12)]  # 1-based house numbers

    # Prepare planet text for each house
    house_planets = {i+1: [] for i in range(12)}
    for planet, pos in planet_positions.items():
        house_planets[pos['house']].append(planet[:2])  # Use short name

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.axis('off')

    # Draw the 4x4 grid
    for x in range(5):
        ax.plot([x, x], [0, 4], color='orange', lw=2)
        ax.plot([0, 4], [x, x], color='orange', lw=2)

    # Draw diagonals
    ax.plot([0, 4], [0, 4], color='orange', lw=2)
    ax.plot([0, 4], [4, 0], color='orange', lw=2)

    # Draw mini rectangle inside diagonals
    ax.add_patch(Rectangle((1, 1), 2, 2, fill=False, edgecolor='orange', lw=2))

    # Place house numbers, signs, and planets
    for i, (x, y) in enumerate(house_coords):
        house_num = house_order[i]
        sign = zodiac_signs[(lagna_sign + i) % 12]
        planets = ' '.join(house_planets[house_num])
        ax.text(x+0.5, y+0.7, f'{house_num}', ha='center', va='center', fontsize=12, color='black', fontweight='bold')
        ax.text(x+0.5, y+0.4, sign, ha='center', va='center', fontsize=11, color='blue')
        ax.text(x+0.5, y+0.1, planets, ha='center', va='center', fontsize=10, color='green')

    plt.tight_layout()
    return fig 