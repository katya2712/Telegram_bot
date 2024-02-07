from commands_list import cmds


def input_parser(string: str):
    strings = string.lower().split()
    cmd = strings[0]
    arg = ' '.join(strings[1:])
    try:
        cmds[cmd](arg)
    except KeyError:
        print(f'Неизвестная команда: {string}')
    except Exception as error:
        print(error)

