import os
import random
import subprocess
import time  # Import time module for delays

FEATURE_DIR = "features"

def get_feature_files():
    """Get all feature files in the features directory."""
    feature_files = []
    for root, _, files in os.walk(FEATURE_DIR):
        for file in files:
            if file.endswith(".feature"):
                feature_files.append(os.path.join(root, file))
    return feature_files

def run_behave_random():
    """Run behave tests in random order with delays."""
    feature_files = get_feature_files()
    random.shuffle(feature_files)  # Shuffle the feature files

    print("\n Running Behave Tests in Random Order:\n")

    for feature in feature_files:
        print(f"➡ Running: {feature}")
        time.sleep(2)  # Pause before executing the next test

        result = subprocess.run(["behave", feature], capture_output=True, text=True)

        print("\n Behave Output:\n")
        print_slow(result.stdout)  # Slow down output printing

        if result.stderr:
            print("\n⚠ Errors:\n")
            print_slow(result.stderr)

def print_slow(text, delay=0.001):
    """Print text slowly to record video."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  

if __name__ == "__main__":
    run_behave_random()
