from constraint import Problem
from utils import load_all_data

def interactive_pc_builder_with_solver():
    """
    Interactive PC configurator using the constraint solver.
    """
    # Load data
    data            = load_all_data() # Returns a dictionary of DataFrames
    cpus            = data["CPU"]
    motherboards    = data["Motherboard"]
    ram             = data["RAM"]
    gpus            = data["GPU"]
    psus            = data["PSU"]
    cases           = data["Case"]

    # Create a solver instance
    problem = Problem()

    # Add variables
    problem.addVariable("CPU", cpus["id"].tolist())
    problem.addVariable("Motherboard", motherboards["id"].tolist())
    problem.addVariable("RAM", ram["id"].tolist())
    problem.addVariable("GPU", gpus["id"].tolist())
    problem.addVariable("PSU", psus["id"].tolist())
    problem.addVariable("Case", cases["id"].tolist())

    # Add constraints
    # 1. CPU socket must match Motherboard socket
    def cpu_motherboard_compatibility(cpu_id, motherboard_id):
        cpu_socket = cpus.loc[cpus["id"] == cpu_id, "socket"].values[0]
        motherboard_socket = motherboards.loc[motherboards["id"] == motherboard_id, "socket"].values[0]
        return cpu_socket == motherboard_socket
    
    # 2. Motherboard RAM type must match RAM type
    def motherboard_ram_compatibility(motherboard_id, ram_id):
        motherboard_ram_type = motherboards.loc[motherboards["id"] == motherboard_id, "ram_type"].values[0]
        ram_type = ram.loc[ram["id"] == ram_id, "ram_type"].values[0]
        return motherboard_ram_type == ram_type
    
    # 3. Motherboard size must match case size
    def motherboard_case_compatibility(motherboard_id, case_id):
        motherboard_size = motherboards.loc[motherboards["id"] == motherboard_id, "size"].values[0]
        case_supported_motherboard_sizes = eval(cases.loc[cases["id"] == case_id, "supported_motherboard_sizes"].values[0])
        return motherboard_size in case_supported_motherboard_sizes
    
    # 4. PSU size must match case size
    def psu_case_compatibility(psu_id, case_id):
        psu_size = psus.loc[psus["id"] == psu_id, "size"].values[0]
        case_supported_psu_sizes = eval(cases.loc[cases["id"] == case_id, "supported_psu_sizes"].values[0])
        return psu_size in case_supported_psu_sizes
    
    # 5. PSU wattage must match GPU power draw
    def gpu_psu_compatibility(gpu_id, psu_id, safety_margin=1.2):
        gpu_power_draw = int(gpus.loc[gpus["id"] == gpu_id, "power_draw"].values[0].replace("W", ""))
        psu_wattage = int(psus.loc[psus["id"] == psu_id, "wattage"].values[0].replace("W", ""))
        return gpu_power_draw * safety_margin <= psu_wattage
    
    problem.addConstraint(cpu_motherboard_compatibility, ("CPU", "Motherboard"))
    problem.addConstraint(motherboard_ram_compatibility, ("Motherboard", "RAM"))
    problem.addConstraint(motherboard_case_compatibility, ("Motherboard", "Case"))
    problem.addConstraint(psu_case_compatibility, ("PSU", "Case"))
    problem.addConstraint(gpu_psu_compatibility, ("GPU", "PSU"))

    # Generate all initial solutions
    solutions = problem.getSolutions()

    # Start interactive process
    print("\nWelcome to the Interactive PC Configurator! (Solver approach)")
    remaining_solutions = solutions # List of solutions where each solution is a dictionary of composant IDs

    # Interactive steps
    for component in ["CPU", "Motherboard", "RAM", "GPU", "PSU", "Case"]:
        while True:  # Loop until valid input is provided
            # Display available options for the current component
            available_ids = set(sol[component] for sol in remaining_solutions) # Extracts all valid IDs for the current component from the remaining solutions.
            available_components = data[component].loc[data[component]["id"].isin(available_ids)]

            print(f"\nChoose a {component}:")
            for idx, row in available_components.iterrows():
                print(f"{row['id']}: {row['name']} ({row['price']}€)")

            # Get user choice
            try:
                user_choice = int(input("Enter your choice (ID): "))
                if user_choice in available_ids:
                    # Valid choice, break out of the loop
                    remaining_solutions = [sol for sol in remaining_solutions if sol[component] == user_choice] # Update remaining solutions
                    break
                else:
                    print("Invalid ID. Please choose a valid option.")
            except ValueError:
                print("Invalid input. Please enter a numeric ID.")

        # Check if there are still compatible solutions
        if not remaining_solutions:
            print(f"\nNo compatible solutions found after selecting {component}. Please restart.")
            return

    # Final configuration
    print("\nYour final configuration:")
    final_solution = remaining_solutions[0]  # There should only be one solution left
    for component, component_id in final_solution.items():
        component_name = data[component].loc[data[component]["id"] == component_id, "name"].values[0]
        print(f"{component}: {component_name}")

if __name__ == "__main__":
    interactive_pc_builder_with_solver()
