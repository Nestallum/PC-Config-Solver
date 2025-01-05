from utils import load_all_data

def interactive_pc_builder_with_mac():
    """
    Interactive PC configurator using MAC (Maintaining Arc Consistency).
    """
    # Load data
    data            = load_all_data() # Returns a dictionary of DataFrames
    cpus            = data["CPU"]
    motherboards    = data["Motherboard"]
    ram             = data["RAM"]
    gpus            = data["GPU"]
    psus            = data["PSU"]
    cases           = data["Case"]

    # Initialize domains
    domains = {
        "CPU"           : set(cpus["id"]),
        "Motherboard"   : set(motherboards["id"]),
        "RAM"           : set(ram["id"]),
        "GPU"           : set(gpus["id"]),
        "PSU"           : set(psus["id"]),
        "Case"          : set(cases["id"]),
    }

    # Define constraints
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
        case_supported_sizes = eval(cases.loc[cases["id"] == case_id, "supported_motherboard_sizes"].values[0])
        return motherboard_size in case_supported_sizes

    # 4. PSU size must match case size
    def psu_case_compatibility(psu_id, case_id):
        psu_size = psus.loc[psus["id"] == psu_id, "size"].values[0]
        case_supported_sizes = eval(cases.loc[cases["id"] == case_id, "supported_psu_sizes"].values[0])
        return psu_size in case_supported_sizes

    # 5. PSU wattage must match GPU power draw
    def gpu_psu_compatibility(gpu_id, psu_id, safety_margin=1.2):
        gpu_power_draw = int(gpus.loc[gpus["id"] == gpu_id, "power_draw"].values[0].replace("W", ""))
        psu_wattage = int(psus.loc[psus["id"] == psu_id, "wattage"].values[0].replace("W", ""))
        return gpu_power_draw * safety_margin <= psu_wattage

    # Constraints propagation
    def propagate(domains):
        for cpu in list(domains["CPU"]):
            if not any(cpu_motherboard_compatibility(cpu, mb) for mb in domains["Motherboard"]):
                domains["CPU"].remove(cpu)

        for mb in list(domains["Motherboard"]):
            if not any(cpu_motherboard_compatibility(cpu, mb) for cpu in domains["CPU"]):
                domains["Motherboard"].remove(mb)
            if not any(motherboard_ram_compatibility(mb, ram) for ram in domains["RAM"]):
                domains["Motherboard"].remove(mb)
            if not any(motherboard_case_compatibility(mb, case) for case in domains["Case"]):
                domains["Motherboard"].remove(mb)

        for ram in list(domains["RAM"]):
            if not any(motherboard_ram_compatibility(mb, ram) for mb in domains["Motherboard"]):
                domains["RAM"].remove(ram)

        for case in list(domains["Case"]):
            if not any(motherboard_case_compatibility(mb, case) for mb in domains["Motherboard"]):
                domains["Case"].remove(case)
            if not any(psu_case_compatibility(psu, case) for psu in domains["PSU"]):
                domains["Case"].remove(case)

        for psu in list(domains["PSU"]):
            if not any(gpu_psu_compatibility(gpu, psu) for gpu in domains["GPU"]):
                domains["PSU"].remove(psu)

        for gpu in list(domains["GPU"]):
            if not any(gpu_psu_compatibility(gpu, psu) for psu in domains["PSU"]):
                domains["GPU"].remove(gpu)

    # Start interactive process
    print("\nWelcome to the Interactive PC Configurator! (MAC approach)")
    propagate(domains)  # Initial propagation

    for component in ["CPU", "Motherboard", "RAM", "GPU", "PSU", "Case"]:
        while True:  # Loop until valid input is provided
            # Display available options for the current component
            available_components = data[component].loc[data[component]["id"].isin(domains[component])]

            print(f"\nChoose a {component}:")
            for idx, row in available_components.iterrows():
                print(f"{row['id']}: {row['name']} ({row['price']}€)")

            try:
                user_choice = int(input("Enter your choice (ID): "))
                if user_choice in domains[component]:
                    # Fix the user's choice and propagate constraints
                    domains[component] = {user_choice}
                    propagate(domains)
                    break
                else:
                    print("Invalid ID. Please choose a valid option.")
            except ValueError:
                print("Invalid input. Please enter a numeric ID.")

        # Check if any domain is empty
        if any(len(domain) == 0 for domain in domains.values()):
            print(f"\nNo compatible solutions found after selecting {component}. Please restart.")
            return

    # Final configuration
    print("\nYour final configuration:")
    for component, ids in domains.items():
        component_name = data[component].loc[data[component]["id"].isin(ids), "name"].values[0]
        print(f"{component}: {component_name}")

if __name__ == "__main__":
    interactive_pc_builder_with_mac()
