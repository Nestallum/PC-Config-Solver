from constraint import Problem
from utils import load_all_data, save_final_configuration
import pandas as pd

def interactive_pc_builder_with_solver():
    """
    Interactive PC configurator using the constraint solver with enhanced display, budget constraint, 
    and step-by-step guided selection.
    """
    # Load data
    data = load_all_data()
    cpus = data["CPU"]
    motherboards = data["Motherboard"]
    ram = data["RAM"]
    gpus = data["GPU"]
    psus = data["PSU"]
    cases = data["Case"]

    # Create the solver instance
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
        return cpus.loc[cpus["id"] == cpu_id, "socket"].values[0] == \
               motherboards.loc[motherboards["id"] == motherboard_id, "socket"].values[0]
    
    def motherboard_ram_compatibility(motherboard_id, ram_id):
        return motherboards.loc[motherboards["id"] == motherboard_id, "ram_type"].values[0] == \
               ram.loc[ram["id"] == ram_id, "ram_type"].values[0]
    
    def motherboard_case_compatibility(motherboard_id, case_id):
        return motherboards.loc[motherboards["id"] == motherboard_id, "size"].values[0] in \
               eval(cases.loc[cases["id"] == case_id, "supported_motherboard_sizes"].values[0])
    
    def psu_case_compatibility(psu_id, case_id):
        return psus.loc[psus["id"] == psu_id, "size"].values[0] in \
               eval(cases.loc[cases["id"] == case_id, "supported_psu_sizes"].values[0])
    
    def gpu_psu_compatibility(gpu_id, psu_id, safety_margin=1.2):
        return int(gpus.loc[gpus["id"] == gpu_id, "power_draw"].values[0]) * safety_margin <= \
               int(psus.loc[psus["id"] == psu_id, "wattage"].values[0])

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

    # Start interactive process
    print("\n🚀 Bienvenue dans le Configurateur de PC interactif ! (Approche Solver)")

    # Résolution sans contrainte budgétaire pour connaître toutes les configurations possibles
    all_solutions = problem.getSolutions()
    print(f"\n🔎 Nombre total de configurations valides (sans contrainte budgétaire) : {len(all_solutions)}")

    if not all_solutions:
        print("\n❌ Aucune configuration valide trouvée.")
        return

    # Trouver la configuration la moins chère
    min_cost_solution = min(all_solutions, key=calculate_cost)
    min_cost = calculate_cost(min_cost_solution)

    # Afficher la configuration minimale en coût
    print("\n💰 **Configuration minimale en coût :**")
    for component, component_id in min_cost_solution.items():
        component_name = data[component].loc[data[component]["id"] == component_id, "name"].values[0]
        component_price = data[component].loc[data[component]["id"] == component_id, "price"].values[0]
        print(f"🔹 {component}: {component_name} ({component_price}€)")
    print(f"💰 **Coût total minimum : {min_cost}€**")

    # Demande du budget utilisateur (doit être >= min_cost)
    while True:
        try:
            budget = int(input(f"\n💰 Entrez votre budget maximal (€) (minimum {min_cost}€) : "))
            if budget >= min_cost:
                break
            else:
                print(f"⚠️  Le budget doit être au moins de {min_cost}€. ")
        except ValueError:
            print("⚠️  Entrée invalide. Veuillez entrer un montant numérique.")

    # Ajout de la contrainte budgétaire
    def budget_constraint(cpu_id, motherboard_id, ram_id, gpu_id, psu_id, case_id):
        return calculate_cost({
            "CPU": cpu_id, "Motherboard": motherboard_id, "RAM": ram_id,
            "GPU": gpu_id, "PSU": psu_id, "Case": case_id
        }) <= budget

    problem.addConstraint(budget_constraint, ("CPU", "Motherboard", "RAM", "GPU", "PSU", "Case"))

    # Résolution avec la contrainte de budget
    budget_solutions = problem.getSolutions()
    print(f"\n🔎 Nombre de configurations respectant le budget : {len(budget_solutions)}")

    if not budget_solutions:
        print("\n❌ Aucune configuration valide trouvée dans le budget.")
        return

    # Sélection interactive avec affichage de l'assistant
    selected_config = {}

    for component in ["CPU", "Motherboard", "RAM", "GPU", "PSU", "Case"]:
        available_options = set(sol[component] for sol in budget_solutions if all(sol[k] == v for k, v in selected_config.items()))
        available_components = data[component].loc[data[component]["id"].isin(available_options)]

        print(f"\n🛠️ **Sélection du composant : {component}**")

        if component == "CPU":
            print("💡 Choisissez un processeur.")
        elif component == "Motherboard":
            print(f"💡 La carte mère doit être compatible avec le socket du CPU sélectionné : ({cpus.loc[cpus['id'] == selected_config['CPU'], 'socket'].values[0]}).")
        elif component == "RAM":
            print(f"💡 La RAM doit être de type : {motherboards.loc[motherboards['id'] == selected_config['Motherboard'], 'ram_type'].values[0]}.")
        elif component == "GPU":
            print("💡 Choisissez une carte graphique en fonction de vos besoins.")
        elif component == "PSU":
            print(f"💡 L'alimentation doit fournir au moins {gpus.loc[gpus['id'] == selected_config['GPU'], 'power_draw'].values[0] * 1.2}W.")
        elif component == "Case":
            print(f"💡 Le boîtier doit supporter une carte mère de type : {motherboards.loc[motherboards['id'] == selected_config['Motherboard'], 'size'].values[0]} "
          f"et une alimentation de taille : {psus.loc[psus['id'] == selected_config['PSU'], 'size'].values[0]}.")


        print("\n📌 Options disponibles :")
        for idx, row in available_components.iterrows():
            print(f"{row['id']}: {row['name']} - ({row['price']}€)")

        while True:
            try:
                user_choice = int(input("✏️  Entrez votre choix (ID) : "))
                if user_choice in available_options:
                    selected_config[component] = user_choice
                    break
                else:
                    print("❌ ID invalide. Veuillez choisir une option valide.")
            except ValueError:
                print("⚠️  Entrée invalide. Veuillez entrer un ID numérique.")

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
    interactive_pc_builder_with_solver()
