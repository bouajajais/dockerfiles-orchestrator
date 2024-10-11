import os
import subprocess
import shutil

SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")

GITHUB_USERNAME = "bouajajais"

# Repositories and Dockerfiles
REPO_NAMES = [
    "poetry",
    "poetry-init",
    "cuda-python",
    "cuda-poetry"
]

# Versions
CUDA_VERSIONS = ["12.3.2", "12.4.1", "12.6.1"]
CUDA_CUDNN_OPTIONS = ["", "-cudnn9", "-cudnn"] # -cudnn9 for 12.3.2
CUDA_TYPES = ["-devel"] # -base, -runtime, -devel
CUDA_OS_OPTIONS = ["-ubuntu22.04"]
PYTHON_VERSIONS = ["3.10", "3.11", "3.12"]
PYTHON_TYPES = ["", "-slim"]
POETRY_VERSION = ["1.8"]

def get_github_repo(
    repo_name: str,
    github_username: str = GITHUB_USERNAME
    ) -> str:
    """
    Get the GitHub repository URL for a given repository name.
    """
    return f"git@github.com:{github_username}/{repo_name}.git"

def run_command(command, cwd=None, shell=False, capture_output=False):
    """
    Utility to run shell commands and print output.
    """
    try:
        result = subprocess.run(command, shell=shell, check=True, cwd=cwd, stdout=subprocess.PIPE if capture_output else None, stderr=subprocess.PIPE if capture_output else None)
        if capture_output and result.stdout is not None:
            return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        if e.stderr is not None:
            print(e.stderr.decode())
        raise
    
def start_ssh_agent_and_add_key(ssh_key_path: str = SSH_KEY_PATH):
    """
    Start the SSH agent and add the SSH key.
    """
    # Start SSH agent and capture environment variables
    print("Starting SSH agent...")
    ssh_agent_output = run_command(["ssh-agent", "-s"], shell=True, capture_output=True)

    # Extract SSH_AGENT_PID and SSH_AUTH_SOCK from the output and set them in the current environment
    for line in ssh_agent_output.splitlines():
        if "SSH_AUTH_SOCK" in line:
            os.environ["SSH_AUTH_SOCK"] = line.split(";")[0].split("=")[1]
        elif "SSH_AGENT_PID" in line:
            os.environ["SSH_AGENT_PID"] = line.split(";")[0].split("=")[1]

    # Add SSH key (You may need to replace the path if your key is stored in a custom location)
    print("Adding SSH key...")
    run_command([f"ssh-add {ssh_key_path}"], shell=True)

def clone_repos(repo_names: list[str] = REPO_NAMES):
    """
    Clones all the repositories using SSH.
    """
    for repo_name in repo_names:
        if os.path.exists(repo_name.replace('-', '_')):
            print(f"Repository {repo_name.replace('-', '_')} already exists, removing it.")
            shutil.rmtree(repo_name.replace('-', '_'))
        print(f"Cloning repository {repo_name}...")
        run_command(f"git clone {get_github_repo(repo_name)} {repo_name.replace('-', '_')}", shell=True)
        
def build_and_push_images(
    repo_names: list[str] = REPO_NAMES,
    cuda_versions: list[str] = CUDA_VERSIONS,
    cuda_cudnn_options: list[str] = CUDA_CUDNN_OPTIONS,
    cuda_types: list[str] = CUDA_TYPES,
    cuda_os_options: list[str] = CUDA_OS_OPTIONS,
    python_versions: list[str] = PYTHON_VERSIONS,
    python_types: list[str] = PYTHON_TYPES,
    poetry_versions: list[str] = POETRY_VERSION
    ):
    """
    Builds and pushes Docker images for all the combinations.
    """
    if "poetry" in repo_names:
        print("Building and pushing poetry images...")
        from poetry.publish_images import publish_images as poetry_publish_images
        poetry_publish_images(
            poetry_versions=poetry_versions,
            python_versions=python_versions,
            python_types=python_types,
            cwd="poetry",
            verbose=2
        )
        
    if "poetry-init" in repo_names:
        print("Building and pushing poetry-init images...")
        from poetry_init.publish_images import publish_images as poetry_init_publish_images
        poetry_init_publish_images(
            poetry_versions=poetry_versions,
            python_versions=python_versions,
            python_types=python_types,
            cwd="poetry_init",
            verbose=1
        )
        
    if "cuda-python" in repo_names:
        print("Building and pushing cuda-python images...")
        from cuda_python.publish_images import publish_images as cuda_python_publish_images
        cuda_python_publish_images(
            cuda_versions=cuda_versions,
            cuda_cudnn_options=cuda_cudnn_options,
            cuda_types=cuda_types,
            cuda_os_options=cuda_os_options,
            python_versions=python_versions,
            cwd="cuda_python",
            verbose=1
        )
        
    if "cuda-poetry" in repo_names:
        print("Building and pushing cuda-poetry images...")
        from cuda_poetry.publish_images import publish_images as cuda_poetry_publish_images
        cuda_poetry_publish_images(
            cuda_versions=cuda_versions,
            cuda_cudnn_options=cuda_cudnn_options,
            cuda_types=cuda_types,
            cuda_os_options=cuda_os_options,
            python_versions=python_versions,
            poetry_versions=poetry_versions,
            cwd="cuda_poetry",
            verbose=1
        )

def cleanup(repo_names: list[str] = REPO_NAMES):
    """
    Removes cloned repositories after building.
    """
    for repo_name in repo_names:
        repo_name = repo_name.replace("-", "_")
        if os.path.exists(repo_name):
            print(f"Removing directory {repo_name}...")
            shutil.rmtree(repo_name)

if __name__ == "__main__":
    # Step 1: Start SSH Agent and Add Key
    start_ssh_agent_and_add_key()

    # Step 2: Clone repositories
    clone_repos()

    # Step 3: Build and push Docker images
    build_and_push_images()

    # Step 4: Cleanup repositories
    cleanup()
