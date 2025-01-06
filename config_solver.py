from constraint import Problem
from utils import load_all_data

def solve_pc_configuration():
    """
    Solves the PC configuration problem using python-constraint.
    """
    # Load data
    data            = load_all_data()
    cpus            = data["CPU"]
    motherboards    = data["Motherboard"]
    ram             = data["RAM"]
    gpus            = data["GPU"]
    psus            = data["PSU"]
    cases           = data["Case"]

    # Create a constraint satisfaction problem instance
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

    # Solve the problem
    solutions = problem.getSolutions()

   # Print valid solutions
    if solutions:
        print(f"\nFound {len(solutions)} solution(s):")
        for idx, solution in enumerate(solutions):
            # Retrieve components
            cpu = cpus.loc[cpus["id"] == solution["CPU"]]
            motherboard = motherboards.loc[motherboards["id"] == solution["Motherboard"]]
            ram_component = ram.loc[ram["id"] == solution["RAM"]]
            gpu = gpus.loc[gpus["id"] == solution["GPU"]]
            psu = psus.loc[psus["id"] == solution["PSU"]]
            case = cases.loc[cases["id"] == solution["Case"]]

            # Retrieve components
            cpu = cpus.loc[cpus["id"] == solution["CPU"]]
            motherboard = motherboards.loc[motherboards["id"] == solution["Motherboard"]]
            ram_component = ram.loc[ram["id"] == solution["RAM"]]
            gpu = gpus.loc[gpus["id"] == solution["GPU"]]
            psu = psus.loc[psus["id"] == solution["PSU"]]
            case = cases.loc[cases["id"] == solution["Case"]]

            # Calculate total price
            total_price = (
                cpu["price"].values[0]
                + motherboard["price"].values[0]
                + ram_component["price"].values[0]
                + gpu["price"].values[0]
                + psu["price"].values[0]
                + case["price"].values[0]
            )

            # Print configuration details
            print(f"\nConfiguration {idx+1}:")
            print(f"CPU: {cpu['name'].values[0]} (Socket: {cpu['socket'].values[0]})")
            print(f"Motherboard: {motherboard['name'].values[0]} (Size: {motherboard['size'].values[0]}, Socket: {motherboard['socket'].values[0]})")
            print(f"RAM: {ram_component['name'].values[0]} (Type: {ram_component['ram_type'].values[0]}, Speed: {ram_component['speed'].values[0]})")
            print(f"GPU: {gpu['name'].values[0]} (Power Draw: {gpu['power_draw'].values[0]})")
            print(f"PSU: {psu['name'].values[0]} (Wattage: {psu['wattage'].values[0]}, Size: {psu['size'].values[0]})")
            print(f"Case: {case['name'].values[0]} (Supports Motherboard: {case['supported_motherboard_sizes'].values[0]}, PSU: {case['supported_psu_sizes'].values[0]})")
            print(f"Total Price: {total_price}€")
    else:
        print("No solutions found.")


if __name__ == "__main__":
    solve_pc_configuration()
