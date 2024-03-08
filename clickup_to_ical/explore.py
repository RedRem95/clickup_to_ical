

def main():
    import logging
    from clickup_to_ical.clickup import get_teams, get_spaces, get_lists_folder, get_lists_space, get_folders, get_tasks

    teams = {x.id: x for x in get_teams()}
    logging.info(f"Found {len(teams)} teams")

    spaces = {}
    folders = {}
    lists = {}
    for t in teams.values():
        spaces[t.id] = {x.id: x for x in get_spaces(team=t.id)}
        for s in spaces[t.id].values():
            lists[s.id] = {x.id: x for x in get_lists_space(space=s.id)}
            folders[s.id] = {x.id: x for x in get_folders(space=s.id)}
            for f in folders[s.id].values():
                lists[f.id] = {x.id: x for x in get_lists_folder(folder=f.id)}

    print("Your available resources:")
    for t in teams.values():
        print(f"{t}: {', '.join(f'{y}' for y in t.members) if len(t.members) < 5 else f'{len(t.members)} members'}")
        for s in spaces[t.id].values():
            print(f"  -> {s}")
            for l in lists[s.id].values():
                print(f"    -> {l}: {len(get_tasks(lst=l.id, with_closed=True))} tasks")
            for f in folders[s.id].values():
                print(f"    -> {f}")
                for l in lists[f.id].values():
                    print(f"      -> {l}: {len(get_tasks(lst=l.id, with_closed=True))} tasks")


if __name__ == '__main__':
    main()
