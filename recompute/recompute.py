
import subprocess
import re

def recompute(url):
    https_clone_url = url + ".git"
    # subprocess.check_call(["git", "clone", https_clone_url])

    repo_name = re.split("/", https_clone_url)[-1].replace(".git", "")
    subprocess.check_call(["cd", repo_name], shell=True)
    subprocess.check_call(["pipreqs", repo_name])

def main():
    url = "https://github.com/cjw-charleswu/Kinect2Kit"
    recompute(url)

if __name__ == "__main__":
    main()
