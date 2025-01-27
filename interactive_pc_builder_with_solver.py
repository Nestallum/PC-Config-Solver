from constraint import Problem
from utils import load_all_data

def interactive_pc_builder_with_solver():
    """
    Interactive PC configurator using the constraint solver.
    """
    # Load data
    data = load_all_data()  # Returns a dictionary of DataFrames
    cpus = data["CPU"]
    motherboards = data["Motherboard"]
    ram = data["RAM"]
    gpus = data["GPU"]
    psus = data["PSU"]
    cases = data["Case"]

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
    def cpu_motherboard_compatibility(cpu_id, motherboard_id):
        cpu_socket = cpus.loc[cpus["id"] == cpu_id, "socket"].values[0]
        motherboard_socket = motherboards.loc[motherboards["id"] == motherboard_id, "socket"].values[0]
        return cpu_socket == motherboard_socket

    def motherboard_ram_compatibility(motherboard_id, ram_id):
        motherboard_ram_type = motherboards.loc[motherboards["id"] == motherboard_id, "ram_type"].values[0]
        ram_type = ram.loc[ram["id"] == ram_id, "ram_type"].values[0]
        return motherboard_ram_type == ram_type

    def motherboard_case_compatibility(motherboard_id, case_id):
        motherboard_size = motherboards.loc[motherboards["id"] == motherboard_id, "size"].values[0]
        case_supported_sizes = eval(cases.loc[cases["id"] == case_id, "supported_motherboard_sizes"].values[0])
        return motherboard_size in case_supported_sizes

    def psu_case_compatibility(psu_id, case_id):
        psu_size = psus.loc[psus["id"] == psu_id, "size"].values[0]
        case_supported_sizes = eval(cases.loc[cases["id"] == case_id, "supported_psu_sizes"].values[0])
        return psu_size in case_supported_sizes

    def gpu_psu_compatibility(gpu_id, psu_id, safety_margin=1.2):
        gpu_power_draw = int(gpus.loc[gpus["id"] == gpu_id, "power_draw"].values[0].replace("W", ""))
        psu_wattage = int(psus.loc[psus["id"] == psu_id, "wattage"].values[0].replace("W", ""))
        return gpu_power_draw * safety_margin <= psu_wattage

    def budget_constraint(cpu_id, motherboard_id, ram_id, gpu_id, psu_id, case_id):
        total_cost = sum(
            [
                cpus.loc[cpus["id"] == cpu_id, "price"].values[0],
                motherboards.loc[motherboards["id"] == motherboard_id, "price"].values[0],
                ram.loc[ram["id"] == ram_id, "price"].values[0],
                gpus.loc[gpus["id"] == gpu_id, "price"].values[0],
                psus.loc[psus["id"] == psu_id, "price"].values[0],
                cases.loc[cases["id"] == case_id, "price"].values[0],
            ]
        )
        return total_cost <= budget

    # Add constraints to the problem
    problem.addConstraint(cpu_motherboard_compatibility, ("CPU", "Motherboard"))
    problem.addConstraint(motherboard_ram_compatibility, ("Motherboard", "RAM"))
    problem.addConstraint(motherboard_case_compatibility, ("Motherboard", "Case"))
    problem.addConstraint(psu_case_compatibility, ("PSU", "Case"))
    problem.addConstraint(gpu_psu_compatibility, ("GPU", "PSU"))

    # Solve the problem to find the minimum cost configuration
    def calculate_cost(solution):
        return sum(
            [
                cpus.loc[cpus["id"] == solution["CPU"], "price"].values[0],
                motherboards.loc[motherboards["id"] == solution["Motherboard"], "price"].values[0],
                ram.loc[ram["id"] == solution["RAM"], "price"].values[0],
                gpus.loc[gpus["id"] == solution["GPU"], "price"].values[0],
                psus.loc[psus["id"] == solution["PSU"], "price"].values[0],
                cases.loc[cases["id"] == solution["Case"], "price"].values[0],
            ]
        )

    all_solutions = problem.getSolutions()

    if not all_solutions:
        print("\nNo configurations found.")
        return

    min_cost_solution = min(all_solutions, key=calculate_cost)
    min_cost = calculate_cost(min_cost_solution)

    # Display the minimum cost configuration
    print("\nMinimum cost configuration:")
    for component, component_id in min_cost_solution.items():
        component_name = data[component].loc[data[component]["id"] == component_id, "name"].values[0]
        component_price = data[component].loc[data[component]["id"] == component_id, "price"].values[0]
        print(f"{component}: {component_name} ({component_price}€)")
    print(f"Total cost: {min_cost}€")

    # Get budget from user
    while True:
        try:
            budget = int(input(f"\nEnter your maximum budget (€) (minimum {min_cost}€): "))
            if budget >= min_cost:
                break
            else:
                print(f"Budget must be at least {min_cost}€.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    problem.addConstraint(budget_constraint, ("CPU", "Motherboard", "RAM", "GPU", "PSU", "Case"))
    solutions = problem.getSolutions()

    if not solutions:
        print("\nNo configurations found within the specified budget.")
        return

    print(f"\n{len(solutions)} configurations found within the budget.")

    # Interactive selection process
    remaining_solutions = solutions

    for component in ["CPU", "Motherboard", "RAM", "GPU", "PSU", "Case"]:
        available_options = set(sol[component] for sol in remaining_solutions)
        available_components = data[component].loc[data[component]["id"].isin(available_options)]

        print(f"\nChoose a {component}:")
        for idx, row in available_components.iterrows():
            print(f"{row['id']}: {row['name']} ({row['price']}€)")

        while True:
            try:
                user_choice = int(input("Enter your choice (ID): "))
                if user_choice in available_options:
                    remaining_solutions = [sol for sol in remaining_solutions if sol[component] == user_choice]
                    break
                else:
                    print("Invalid ID. Please choose a valid option.")
            except ValueError:
                print("Invalid input. Please enter a numeric ID.")

        if not remaining_solutions:
            print(f"\nNo compatible solutions found after selecting {component}. Please restart.")
            return

    # Final configuration
    print("\nYour final configuration:")
    final_solution = remaining_solutions[0]  # There should only be one solution left
    total_cost = calculate_cost(final_solution)
    for component, component_id in final_solution.items():
        component_name = data[component].loc[data[component]["id"] == component_id, "name"].values[0]
        component_price = data[component].loc[data[component]["id"] == component_id, "price"].values[0]
        print(f"{component}: {component_name} ({component_price}€)")
    print(f"Total cost: {total_cost}€")

if __name__ == "__main__":
    interactive_pc_builder_with_solver()