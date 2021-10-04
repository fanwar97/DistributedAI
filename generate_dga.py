"""
Module to generate DGAs
"""
import glob
import os
import random
import subprocess

class GenerateDGA:
    """Class to generate domains"""
    def __init__(self, number_of_samples, python_path):
        self.org_path = os.getcwd() + "/"
        self.files = list(glob.glob("generators" + "/**/dga*.py", recursive=True))
        self.dict_based = ["gozi", "nymaim2", "pizd", "suppobox"]
        self.domain_list = []
        self.number_of_samples = number_of_samples
        self.python_path = python_path

    # Random probability = 1/out_of
    # If the generated samples were not enough, pass a lower out_of argument
    # Currently default at 100
    def get_benign(self, out_of = 100):
        """Get random benign domains"""
        print("Generating benign domains...")
        with open(self.org_path + "benign.txt", "r", encoding="utf-8") as file1:
            counter = 0
            with open("benign_" + str(self.number_of_samples) + ".txt", "w",
                        encoding="utf-8") as file2:
                for aline in file1:
                    if random.randrange(out_of):
                        continue
                    file2.write(aline)
                    counter += 1
                    if counter == self.number_of_samples:
                        return True
        return False

    def run_algorithm(self, arguments, file):
        """Run each algorithm script"""
        command_list = [self.org_path + self.python_path, os.path.basename(file)]
        command_list.extend(arguments)
        os.chdir(self.org_path + file.replace(os.path.basename(file), ""))
        with subprocess.Popen(command_list, stdout=subprocess.PIPE) as proc:
            out = proc.communicate()[0]
        temp_domain_list = out.decode("utf-8").split("\r\n")
        temp_domain_list.pop()
        if len(temp_domain_list) > self.number_of_samples:
            temp_domain_list = random.sample(temp_domain_list, self.number_of_samples)
        elif len(temp_domain_list) < self.number_of_samples:
            print("Not enough")
        self.domain_list.extend(temp_domain_list)


    def get_attack_dict_based(self):
        """Get random dict based domains."""
        print("Generating dict based domains...")
        for file in self.files:
            is_dict_based = False
            for element in self.dict_based:
                if element in file:
                    is_dict_based = True
                    print(file)
            if not is_dict_based:
                continue
            if is_dict_based and "suppobox" in file:
                self.run_algorithm([str(random.randint(1,3)), "-n",
                                    str(self.number_of_samples)], file)
            elif is_dict_based:
                self.run_algorithm(["-n", str(self.number_of_samples)], file)
        self.write_attack_to_file("dict_based")

    def write_attack_to_file(self, attack_type):
        """Write the generated samples to a text file"""
        os.chdir(self.org_path)
        with open("attack_" + attack_type + ".txt", "w", encoding="utf-8") as file:
            for element in self.domain_list:
                file.write(element + "\n")

    def get_attack_char_based(self):
        """Get random char based domains"""
        print("Generating char based domains...")
        for file in self.files:
            is_char_based = True
            for element in self.dict_based:
                if element in file:
                    is_char_based = False
            if is_char_based:
                print(file)
            else:
                continue
            self.exec_char_based(file)
        self.write_attack_to_file("char_based")

    def exec_char_based(self, file):
        """
        Execute the corresponding algorithm script.\n
        This function evaluates algorithm name and execute with corresponding params.
        """
        char_based_case = {
            "corebot": lambda: self.case_4(file),
            "dircrypt": lambda: self.case_3(file),
            "dnschanger": lambda: self.case_3(file),
            "fobber": lambda: self.case_2(file),
            "kraken": lambda: self.case_4(file),
            "mydoom": lambda: self.case_4(file),
            "newgoz": lambda: self.case_4(file),
            "nymaim": lambda: self.case_4(file),
            "pizd": lambda: self.case_4(file),
            "pykspa": lambda: self.case_4(file),
            "qakbot": lambda: self.case_4(file),
            "ramnit": lambda: self.case_3(file),
            "shiotob": lambda: self.case_0(file),
            "unknown_malware": lambda: self.case_1(file),
            "vawtrak": lambda: self.case_4(file)
        }
        is_char_based_with_params = False
        for item in char_based_case.items():
            if item[0] in file:
                is_char_based_with_params = True
                item[1]()
        if not is_char_based_with_params:
            self.run_algorithm([], file)

    def case_0(self, file):
        """For shiotob"""
        os.chdir(self.org_path)
        with open("benign_" + str(self.number_of_samples) + ".txt", "r",
                        encoding="utf-8") as temp_file:
            if random.randrange(self.number_of_samples):
                temp_file.readline()
            seed_domain = temp_file.readline()
        self.run_algorithm([seed_domain, "-n", str(self.number_of_samples)], file)

    def case_1(self, file):
        """For unknown_malware"""
        choice_list = ["sn", "al"]
        self.run_algorithm([random.choice(choice_list), "-n", str(self.number_of_samples)], file)

    def case_2(self, file):
        """For fobber"""
        self.run_algorithm([str(random.randint(1,2)), "-n", str(self.number_of_samples)], file)

    def case_3(self, file):
        """For dircrypt, dnstracker and ramnit"""
        self.run_algorithm([str(random.randint(0, self.number_of_samples)), "-n",
                            str(self.number_of_samples)], file)
    
    def case_4(self, file):
        """For corebot, kraken, mydoom, newgoz, nymaim, pizd, qakbot and vawtrak"""
        self.run_algorithm(["-n", str(self.number_of_samples)], file)

### Example with 500 samples
### Must clear domain list before generating a new one
if __name__=="__main__":
    gen = GenerateDGA(5000, ".venv/Scripts/python.exe")
    for i in range(2):
        if i == 0:
            gen.get_attack_dict_based()
        if i == 1:
            gen.get_attack_char_based()
        gen.domain_list.clear()
