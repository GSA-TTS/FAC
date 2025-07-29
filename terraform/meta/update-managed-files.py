import os

def update_module_files(template_dir, dir, exclude_files, suffix="-managed"):
    root_path = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(template_dir):
        if file in exclude_files:
            continue

        template_path = os.path.join(template_dir, file)
        if os.path.isfile(template_path):
            with open(template_path, 'r') as loaded_file:
                content = loaded_file.read()

            basename, ext = os.path.splitext(file)
            new_file = f"{basename}{suffix}.tf"
            output_path = os.path.join(f"{root_path}/../{dir}", new_file)

            with open(output_path, 'w') as output_file:
                output_file.write(content)
                os.chmod(output_path, 0o644)

            print(f"Updated {dir}/{new_file}")

environment_directory = ["sandbox", "preview", "dev", "staging", "production"]
excluded_templates = ["main.tf-template", "init.sh-template"]
for dir in environment_directory:
    update_module_files("./bootstrap-env/templates/", dir, excluded_templates)
