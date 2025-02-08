from utils import load_all_data, save_final_configuration

def interactive_pc_builder():
    """
    Interactive PC configurator using MAC approach.
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
        gpu_power_draw = int(gpus.loc[gpus["id"] == gpu_id, "power_draw"].values[0])
        psu_wattage = int(psus.loc[psus["id"] == psu_id, "wattage"].values[0])
        return gpu_power_draw * safety_margin <= psu_wattage

    def propagate_constraints(domains):
        """
        MAC (Maintaining Arc Consistency) Approach: Ensures that the domains of variables remain consistent 
        by reducing them based on compatibility constraints. 

        This function follows a unidirectional propagation approach, making it suitable for interactive processes 
        where user choices progressively narrow down the possible solutions.

        Arguments:
        domains -- a dictionary containing the possible domains for each component.
        """

        for mb in list(domains["Motherboard"]):
            # Remove the motherboard if it is not compatible with any remaining CPU
            if not any(cpu_motherboard_compatibility(cpu, mb) for cpu in domains["CPU"]):
                domains["Motherboard"].remove(mb)

        for ram in list(domains["RAM"]):
            # Remove the RAM if it is not compatible with any remaining motherboard
            if not any(motherboard_ram_compatibility(mb, ram) for mb in domains["Motherboard"]):
                domains["RAM"].remove(ram)

        for case in list(domains["Case"]):
            # Remove the case if it is not compatible with any remaining motherboard
            if not any(motherboard_case_compatibility(mb, case) for mb in domains["Motherboard"]):
                domains["Case"].remove(case)

        for psu in list(domains["PSU"]):
            # Remove the PSU if it is not compatible with any remaining case
            if not any(psu_case_compatibility(psu, case) for case in domains["Case"]):
                domains["PSU"].remove(psu)
            # Remove the PSU if it is not compatible with any remaining GPU
            if not any(gpu_psu_compatibility(gpu, psu) for gpu in domains["GPU"]):
                domains["PSU"].remove(psu)

    # Start interactive process
    print("\n🚀 Bienvenue dans le Configurateur de PC interactif ! (Approche MAC)")
    propagate_constraints(domains)  # Initial propagation

    selected_config = {}

    for component in ["CPU", "Motherboard", "RAM", "GPU", "PSU", "Case"]:
        while True:
            available_components = data[component].loc[data[component]["id"].isin(domains[component])]

            print(f"\n🛠️ **Sélection du composant : {component}**")

            # Ajout des indications pour guider l'utilisateur
            if component == "CPU":
                print("💡 Choisissez un processeur.")
            elif component == "Motherboard":
                print(f"💡 La carte mère doit être compatible avec le socket du CPU sélectionné : "
                      f"({cpus.loc[cpus['id'] == selected_config['CPU'], 'socket'].values[0]}).")
            elif component == "RAM":
                print(f"💡 La RAM doit être de type : "
                      f"{motherboards.loc[motherboards['id'] == selected_config['Motherboard'], 'ram_type'].values[0]}.")
            elif component == "GPU":
                print("💡 Choisissez une carte graphique en fonction de vos besoins.")
            elif component == "PSU":
                print(f"💡 L'alimentation doit fournir au moins "
                      f"{gpus.loc[gpus['id'] == selected_config['GPU'], 'power_draw'].values[0] * 1.2}W.")
            elif component == "Case":
                print(f"💡 Le boîtier doit supporter une carte mère de type : "
                      f"{motherboards.loc[motherboards['id'] == selected_config['Motherboard'], 'size'].values[0]} "
                      f"et une alimentation de taille : {psus.loc[psus['id'] == selected_config['PSU'], 'size'].values[0]}.")

            print("\n📌 Options disponibles :")
            for idx, row in available_components.iterrows():
                print(f"{row['id']}: {row['name']} ({row['price']}€)")

            try:
                user_choice = int(input("✏️  Entrez votre choix (ID) : "))
                if user_choice in domains[component]:
                    selected_config[component] = user_choice
                    domains[component] = {user_choice}  # Fix the user's choice
                    propagate_constraints(domains)  # Apply constraints
                    break
                else:
                    print("❌ ID invalide. Veuillez choisir une option valide.")
            except ValueError:
                print("⚠️ Entrée invalide. Veuillez entrer un ID numérique.")

        # Check if any domain is empty
        if any(len(domain) == 0 for domain in domains.values()):
            print(f"\n❌ Aucune solution compatible trouvée après la sélection de {component}. Veuillez recommencer.")
            return

    # Final configuration
    print("\n✅ **Configuration finale :**")
    total_cost = sum(data[comp].loc[data[comp]["id"] == cid, "price"].values[0] for comp, cid in selected_config.items())
    for component, component_id in selected_config.items():
        component_name = data[component].loc[data[component]["id"] == component_id, "name"].values[0]
        component_price = data[component].loc[data[component]["id"] == component_id, "price"].values[0]
        print(f"🔹 {component}: {component_name} ({component_price}€)")
    print(f"💰 **Coût total : {total_cost}€**")

    # Enregistrer la configuration dans un CSV
    save_final_configuration(selected_config, data)

if __name__ == "__main__":
    interactive_pc_builder()