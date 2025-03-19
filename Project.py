import pygame
import random
import math
import datetime
import os
import sys

# Ensure the console uses UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (20, 20, 30)
OBJECT_COLOR = (100, 200, 255)
FORCE_COLOR = (255, 100, 100)
PIVOT_COLOR = (255, 255, 0)
BUTTON_COLOR = (50, 150, 50)
TEXT_COLOR = (255, 255, 255)
LOG_FILE = os.path.join(os.path.dirname(__file__), "simulation_log.txt")

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Force and Moment Simulation")

# Object properties
max_object_size = int(0.3 * min(WIDTH, HEIGHT))
min_object_size = 50
object_size = random.randint(min_object_size, max_object_size)
object_pos = [WIDTH // 2, HEIGHT // 2]
pivot_pos = [WIDTH // 2, HEIGHT // 2]
object_angle = 0
running = False
warning_message = ""
log_data = []
total_applied_force = 0
user_input_force = 0
max_force = 3000
min_force = 500

# Button properties
button_font = pygame.font.Font(None, 24)
buttons = {
    "Start": pygame.Rect(600, 50, 100, 40),
    "Stop": pygame.Rect(600, 100, 100, 40),
    "Undo": pygame.Rect(600, 150, 100, 40),
    "Reset": pygame.Rect(600, 200, 100, 40),
    "Input Force": pygame.Rect(600, 250, 100, 40),
    "Give Up": pygame.Rect(600, 300, 100, 40),
}

# Force generation and modification
forces = []
force_count = random.randint(4, 6)

def generate_random_forces():
    forces = []
    num_forces = random.randint(4, 6)
    for _ in range(num_forces):
        angle = random.uniform(0, 2 * math.pi)
        magnitude = random.randint(200, 800)
        force_pos = [random.randint(200, 600), random.randint(150, 450)]
        forces.append((force_pos, magnitude, angle))
    return forces

forces = generate_random_forces()

def log_event(event):
    global log_data
    log_data.append(f"{datetime.datetime.now()}: {event}\n")

def save_log():
    with open(LOG_FILE, "w", encoding='utf-8') as log_file:
        log_file.writelines(log_data)

def get_force_color(force_percentage, is_manual_force=False):
    if is_manual_force:
        return (255, 0, 0)
    if force_percentage <= 20:
        return (0, 255, 0)
    elif force_percentage <= 50:
        return (255, 255, 0)
    else:
        return (255, 0, 0)

def draw_system_status_window():
    font = pygame.font.Font(None, 30)
    if total_applied_force > 0:
        percentage_difference = abs(total_applied_force - user_input_force) / total_applied_force * 100
        if percentage_difference <= 10:
            force_percentage = percentage_difference
        else:
            force_percentage = (total_applied_force / max_force) * 100
    else:
        force_percentage = 0
    force_color = get_force_color(force_percentage)

    pygame.draw.rect(screen, (40, 40, 60), (10, 10, 300, 130), border_radius=10)

    force_percentage_text = f"Usage: {force_percentage:.2f}%"
    force_percentage_surf = font.render(force_percentage_text, True, force_color)
    screen.blit(force_percentage_surf, (20, 50))

    return force_color == (0, 255, 0)


def draw_object():
    house_base_width = object_size
    house_base_height = object_size * 0.7
    house_base = pygame.Surface((house_base_width, house_base_height), pygame.SRCALPHA)
    house_base.fill((0, 0, 0, 0))
    pygame.draw.rect(house_base, OBJECT_COLOR, (0, 0, house_base_width, house_base_height))

    roof_height = object_size * 0.3
    roof = pygame.Surface((house_base_width, roof_height), pygame.SRCALPHA)
    roof.fill((0, 0, 0, 0))
    pygame.draw.polygon(roof, OBJECT_COLOR, [(0, roof_height), (house_base_width // 2, 0), (house_base_width, roof_height)])

    rotated_surface = pygame.Surface((house_base_width, house_base_height + roof_height), pygame.SRCALPHA)
    rotated_surface.fill((0, 0, 0, 0))
    rotated_surface.blit(house_base, (0, roof_height))
    rotated_surface.blit(roof, (0, 0))

    rotated_surface = pygame.transform.rotate(rotated_surface, -object_angle)
    rect = rotated_surface.get_rect(center=(object_pos[0], object_pos[1]))
    screen.blit(rotated_surface, rect.topleft)

    pygame.draw.circle(screen, PIVOT_COLOR, pivot_pos, 7)

def draw_forces():
    for force in forces:
        pos, magnitude, angle = force
        force_percentage = (magnitude / max_force) * 100
        force_color = get_force_color(force_percentage)
        end_x = pos[0] + magnitude * 0.02 * math.cos(angle)
        end_y = pos[1] + magnitude * 0.02 * math.sin(angle)
        pygame.draw.line(screen, force_color, pos, (end_x, end_y), 3)
        pygame.draw.circle(screen, force_color, pos, 5)

def calculate_moment():
    global warning_message, total_applied_force
    total_moment = 0
    total_applied_force = sum(magnitude for pos, magnitude, angle in forces)

    for force in forces:
        pos, magnitude, angle = force
        dx = pos[0] - pivot_pos[0]
        dy = pos[1] - pivot_pos[1]
        r = math.sqrt(dx**2 + dy**2)

        force_angle = math.atan2(dy, dx)
        theta = abs(force_angle - angle)

        force_perpendicular = magnitude * math.sin(theta)
        moment = r * force_perpendicular
        total_moment += moment

    warning_message = ""
    if total_moment < 1300:
        warning_message += "Warning: Moment is too low! "
    elif total_moment > 2000:
        warning_message += "Warning: Moment exceeds limit! "
    if total_applied_force < min_force:
        warning_message += "Warning: Force is too low! "
    elif total_applied_force > max_force:
        warning_message += "Warning: Force is too high! "

    return max(1300, min(total_moment, 2000))

def draw_numerical_report(moment):
    font = pygame.font.Font(None, 24)
    report_text = [
        f"Numerical Report:",
        f"Moment: {moment:.2f} Nm",
        f"Object Angle: {object_angle:.2f} degrees",
    ]
    pygame.draw.rect(screen, (30, 30, 50), (10, 500, 300, 100), border_radius=10)
    for i, text in enumerate(report_text):
        text_surf = font.render(text, True, TEXT_COLOR)
        screen.blit(text_surf, (20, 510 + i * 20))

button_width = 60
button_height = 25
button_spacing = 5
horizontal_gap = 120

def draw_input_box():
    if input_active:
        font = pygame.font.Font(None, 30)
        input_box = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 50, 100, 30)
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        text_surface = font.render(input_text, True, (255, 255, 255))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    for text, rect in buttons.items():
        pygame.draw.rect(screen, BUTTON_COLOR, rect)
        text_surface = button_font.render(text, True, TEXT_COLOR)
        screen.blit(text_surface, (rect.x + 10, rect.y + 10))

def is_point_inside_object(x, y):
    dx = x - object_pos[0]
    dy = y - object_pos[1]
    angle_rad = math.radians(object_angle)
    transformed_x = dx * math.cos(angle_rad) + dy * math.sin(angle_rad)
    transformed_y = -dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
    half_width = object_size / 2
    half_height = object_size * 0.7 / 2

    if -half_width < transformed_x < half_width and -half_height < transformed_y < half_height:
        return True
    return False

show_total_applied_force = False
input_active = False
input_text = ""
selected_force_index = None

def reduce_rotation_speed(user_force):
    global object_angular_velocity

    if user_force > 0:
        reduction_factor = max(0.5, min(1.5, 1 - (user_force / max_force)))
        object_angular_velocity *= reduction_factor

        print(f" Rotation Speed Reduced: Factor {reduction_factor:.2f}")
        print(f" New Angular Velocity: {object_angular_velocity:.5f}")

def handle_input_force():
    global user_input_force, input_text, total_applied_force, object_angular_velocity

    if input_text.isdigit():
        user_input_force = int(input_text)
        log_event(f"User input force: {user_input_force} N")
        print(f" User input force: {user_input_force} N")

        if total_applied_force > 0:
            percentage_difference = abs(total_applied_force - user_input_force) / total_applied_force * 100
            print(f" Percentage difference: {percentage_difference:.2f}%")
        else:
            percentage_difference = 0

        if total_applied_force > 0 and percentage_difference > 10:
            print(" User input force exceeds ±10% of total applied force.")
            input_text = ""
            return

        reduce_rotation_speed(user_input_force)
        input_text = ""

def draw_conclusion_screen():
    """Displays the final conclusion screen when the user gives up."""
    log_event("Drawing conclusion screen.")  # Log when the conclusion screen is displayed

    screen.fill(BACKGROUND_COLOR)
    font = pygame.font.Font(None, 36)
    conclusion_text = [
        "Conclusion",
        f"Total Applied Force: {total_applied_force} N",
        f"Manually Input Force: {user_input_force} N"
    ]
    
    force_percentage = (user_input_force / max_force) * 100 if user_input_force > 0 else 0
    manual_force_color = get_force_color(force_percentage, is_manual_force=True)
    
    for i, text in enumerate(conclusion_text):
        text_surf = font.render(text, True, TEXT_COLOR if i != 2 else manual_force_color)
        screen.blit(text_surf, (WIDTH // 2 - text_surf.get_width() // 2, HEIGHT // 2 - 100 + i * 40))

    try_again_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 120, 40)
    close_button = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 + 50, 230, 40)
    pygame.draw.rect(screen, BUTTON_COLOR, try_again_button)
    pygame.draw.rect(screen, BUTTON_COLOR, close_button)
    
    try_again_text = font.render("Try Again", True, TEXT_COLOR)
    close_text = font.render("Close Simulation", True, TEXT_COLOR)
    
    screen.blit(try_again_text, (try_again_button.x + 10, try_again_button.y + 5))
    screen.blit(close_text, (close_button.x + 10, close_button.y + 5))

    pygame.display.flip()

    log_event("Conclusion screen drawn. Waiting for user action.")  # Log waiting state
    return try_again_button, close_button


def main():
    """Main game loop that runs the simulation."""
    global object_angle, running, forces, pivot_pos, object_angular_velocity, input_active, input_text, selected_force_index, user_input_force
    clock = pygame.time.Clock()
    pivot_set_once = False

    object_angular_velocity = 0.01
    object_angular_damping = 0.01

    running = True
    show_conclusion = False

    log_event("Simulation started.")  # Log when the simulation begins

    while True:
        if show_conclusion:
            log_event("User reached the conclusion screen.")  # Log when user sees conclusion
            try_again_button, close_button = draw_conclusion_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    log_event("User closed the simulation.")
                    save_log()
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    log_event("User pressed ESC. Returning to simulation.")
                    show_conclusion = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if try_again_button.collidepoint(x, y):
                        log_event("User clicked 'Try Again'. Restarting simulation.")
                        show_conclusion = False
                        forces = generate_random_forces()
                        pivot_pos = [WIDTH // 2, HEIGHT // 2]
                        object_angle = 0
                        object_angular_velocity = 0.05
                        pivot_set_once = False
                    elif close_button.collidepoint(x, y):
                        log_event("User clicked 'Close Simulation'. Exiting program.")
                        save_log()
                        pygame.quit()
                        return
            continue

        screen.fill(BACKGROUND_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log_event("User closed the simulation.")
                save_log()
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if buttons["Start"].collidepoint(x, y):
                    running = True
                    log_event("User started the simulation.")
                    total_moment = calculate_moment()
                    if total_moment != 0:
                        object_angular_velocity = total_moment * 0.0001
                elif buttons["Stop"].collidepoint(x, y):
                    running = False
                    log_event("User stopped the simulation.")
                    object_angular_velocity = 0
                elif buttons["Undo"].collidepoint(x, y) and forces:
                    forces.pop()
                    log_event("User undid the last force change.")
                elif buttons["Reset"].collidepoint(x, y):
                    forces = generate_random_forces()
                    pivot_pos = [WIDTH // 2, HEIGHT // 2]
                    object_angle = 0
                    log_event("Simulation reset.")
                elif buttons["Input Force"].collidepoint(x, y):
                    input_active = True
                    log_event("User activated input force box.")
                elif buttons["Give Up"].collidepoint(x, y):
                    log_event("User gave up. Showing conclusion screen.")
                    show_conclusion = True
                elif is_point_inside_object(x, y):
                    new_pivot_x, new_pivot_y = x, y
                    if not pivot_set_once:
                        object_left = object_pos[0] - object_size / 2
                        object_right = object_pos[0] + object_size / 2
                        object_top = object_pos[1] - object_size * 0.7 / 2
                        object_bottom = object_pos[1] + object_size * 0.7 / 2
                        if object_left <= new_pivot_x <= object_right and object_top <= new_pivot_y <= object_bottom:
                            pivot_pos = [new_pivot_x, new_pivot_y]
                            pivot_set_once = True
                            log_event(f"User set new pivot at {pivot_pos}.")
                        else:
                            log_event(f"Invalid pivot position: {new_pivot_x}, {new_pivot_y} (outside object).")
            elif event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        log_event(f"User entered input force: {input_text}.")
                        handle_input_force()
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            if running:
                if object_angular_velocity == 0:
                    object_angular_velocity = 0.05

                object_angle += object_angular_velocity
                object_angular_velocity *= (1 - object_angular_damping)

                if abs(object_angular_velocity) < 0.002:
                    object_angular_velocity = 0.002

        moment = calculate_moment()
        if draw_system_status_window():
            log_event("User achieved force balance. Showing conclusion screen.")
            show_conclusion = True
        draw_object()
        draw_forces()
        draw_input_box()
        draw_numerical_report(moment)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
