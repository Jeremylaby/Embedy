example = "key -c 123 123 5; 123 123 5; 123 123 5; 123 123 5; 123 123 5; 123 123 5; 123 123 5;\n"
parts = example.strip().split()
key, prefix, *args = parts
print(args)
commands = " ".join(args).rstrip(";").split("; ")
print(commands)