def print_header(msg, start_newline=False, end_newline=False):
    if start_newline:
        print()

    print(f"----- {msg.upper()} -----")

    if end_newline:
        print()


def print_subheader(msg, start_newline=False, end_newline=False):
    if start_newline:
        print()

    print(f"--- {msg.title()} ---")

    if end_newline:
        print()


def print_messages(msgs, errors_only=False, start_newline=False, end_newline=False):
    if start_newline:
        print()

    for msg in msgs:
        if not (errors_only and msg[:5] != 'Error'):
            print(f"- {msg}")

    if end_newline:
        print()
