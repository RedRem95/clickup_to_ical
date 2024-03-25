

def main():
    import logging
    from clickup_to_ical.clickup import get_teams, get_spaces, get_lists, get_folders, get_tasks

    teams = {x.id: x for x in get_teams()}
    logging.info(f"Found {len(teams)} teams")

    spaces = {}
    folders = {}
    lists = {}
    for t in teams.values():
        spaces[t.id] = {x.id: x for x in get_spaces(team=t)}
        for s in spaces[t.id].values():
            lists[s.id] = {x.id: x for x in get_lists(origin=s)}
            folders[s.id] = {x.id: x for x in get_folders(space=s)}
            for f in folders[s.id].values():
                lists[f.id] = {x.id: x for x in get_lists(origin=f)}

    print("Your available resources:")
    for t in teams.values():
        print(f"{t}: {', '.join(f'{y}' for y in t.members) if len(t.members) < 5 else f'{len(t.members)} members'}")
        for s in spaces[t.id].values():
            print(f"{' ' * 2}-> {s}")
            for l in lists[s.id].values():
                print(f"{' ' * 4}-> {l}: {len(get_tasks(lst=l, with_closed=True, with_subtasks=True))} tasks")
            for f in folders[s.id].values():
                print(f"{' ' * 4}-> {f}")
                for l in lists[f.id].values():
                    print(f"{' ' * 6}-> {l}: {len(get_tasks(lst=l, with_closed=True, with_subtasks=True))} tasks")


if __name__ == '__main__':
    main()
