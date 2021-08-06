


dicotr1 = {'jopa': {'zalupa': 'zalupa', 'ananas': 'jopa'},
            'kartoha': {'ololo': 'zalupa', 'ananas': 'jopa'},
            'gorlo': {'zalupa': 'zalupa', 'ananas': 'jopa'},
}   

dicotr2 = {'makaka': {'zalupa': 'zalupa', 'ananas': 'jopa'},
            'kartoha': {'ololo': 'zalupa', 'ananas': 'jopa'},
            'olivec': {'zalupa': 'zalupa', 'ananas': 'jopa'},
}   

global_projects = set(list(dicotr1.keys())) - set(list(dicotr2.keys()))

print(global_projects)

