"""
Module to generate DGAs
"""
import argparse
import glob
import math
import os
import pathlib
import random
import subprocess


class GenerateDGA:
    """Class to generate domains"""
    __org_path = os.getcwd() + "/"
    __files = list(glob.glob("generators" + "/**/dga*.py", recursive=True))
    __dict_based = ["gozi", "nymaim2", "pizd", "suppobox"]
    __limited = ["bazarbackdoor", "chinad", "locky", "padcrypt", "pushdo", "qsnatch", "ranbyus",
                    "sisron", "tempedreve", "tinba", "unnamed_downloader"]
    __multiple = ["bazarbackdoor", "kraken", "locky", "murofet", "necurs", "pykspa", "qsnatch",
                    "vawtrak"]

    ###
    # Number of samples:    Final number of generated domains by each algorithm
    #                       to be written to a .txt file
    # Gen num:  Initial number of domains to be generated before being sampled
    #           again for the final output
    # NOTE: Gen num > Number of samples
    ###
    def __init__(self, python_path, number_of_samples, gen_num = None, output_dir = None):
        self.__domain_list = []
        self.__multiple_list = []
        self.__number_of_samples = number_of_samples
        self.__python_path = python_path
        self.__gen_num = gen_num
        self.__output_dir = output_dir
        if not os.path.isabs(self.__python_path):
            self.__python_path = os.path.abspath("") + "/" + self.__python_path
        if not self.__output_dir:
            self.__output_dir = ""
        else:
            if not self.__output_dir.endswith("\\") or not self.__output_dir.endswith("/"):
                self.__output_dir = self.__output_dir + "/"
            if not os.path.isdir(self.__output_dir):
                os.makedirs(self.__output_dir)
        if self.__gen_num:
            if self.__gen_num < self.__number_of_samples:
                print("Number of domains to be generate is smaller than number of samples\n"
                        "Changing it to", self.__number_of_samples)
        if not self.__gen_num or self.__gen_num < self.__number_of_samples:
            self.__gen_num = self.__number_of_samples

    def get_attack_dict_based(self):
        """Get random dict based domains."""
        print("Generating dict based domains...")
        for file in self.__files:
            is_dict_based = self.__check_name_list_in_file(self.__dict_based, file)[0]
            if is_dict_based:
                print(file)
            else:
                continue
            self.__exec_dict_based(pathlib.PurePath(file).as_posix())
        domain_list_expanded = self.__flatten_list(self.__domain_list)
        self.__write_attack_to_file(domain_list_expanded, self.__output_dir + "attack_dict_based_" +
                                    str(self.__number_of_samples) + "_each.txt")
        self.__domain_list.clear()

    def get_attack_char_based(self):
        """Get random char based domains"""
        self.__gen_attack_char_based()
        domain_list_expanded = self.__flatten_list(self.__domain_list)
        self.__write_attack_to_file(domain_list_expanded, self.__output_dir + "attack_char_based_" +
                                    str(self.__number_of_samples) + "_each.txt")
        self.__domain_list.clear()

    def get_attack_char_based_mutually_exclusive(self, number_of_files):
        """
        Get random char based domains and divide them into files.
        The algorithms between files are mutually exclusive to each other.
        Please be aware that some scripts in this algorithm are hardcoded
        and may not generate enough samples from an arbitrary number.
        Number of samples in the final .txt file can be less than expected.
        """
        self.__gen_attack_char_based()
        algo_per_file = math.floor(len(self.__domain_list) / number_of_files)
        remain = len(self.__domain_list) % number_of_files
        algo_per_file_list = []
        for index in range(number_of_files):
            if index < remain:
                algo_per_file_list.append(algo_per_file)
            else:
                algo_per_file_list.append(algo_per_file+1)
        random.shuffle(algo_per_file_list)
        for index in range(number_of_files):
            temp_list = self.__flatten_list(
                            self.__domain_list.pop(random.randrange(len(self.__domain_list)))
                            for _ in range(algo_per_file_list[index]))
            self.__write_attack_to_file(temp_list, self.__output_dir +
                                        "attack_char_based_mutually_exclusive" + "_" +
                                        str(index+1).zfill(2) + ".txt")
        self.__domain_list.clear()

    def get_attack_by_algo(self, algo_name, number_of_files):
        """Get attack domains by algorithm name"""
        samples_per_file = math.ceil(self.__number_of_samples / number_of_files)
        algo_list = os.listdir("generators")
        is_exist = self.__check_name_in_list(algo_name, algo_list)
        if not is_exist:
            print("Algorithm doesn't exist. Please check again!")
        else:
            print("Generating " + algo_name + " domains...")
            is_dict_based = self.__check_name_in_list(algo_name, self.__dict_based)
            is_limited = self.__check_name_in_list(algo_name, self.__limited)
            if is_limited:
                print("Please be aware that some scripts in this algorithm are hardcoded "
                        "and may not generate enough samples from an arbitrary number.\n"
                        "Number of generated files can be less than expected.")
            for file in self.__files:
                if algo_name in file:
                    print(file)
                    if not is_dict_based:
                        self.__exec_char_based(pathlib.PurePath(file).as_posix())
                    else:
                        self.__exec_dict_based(pathlib.PurePath(file).as_posix())
            if self.__multiple_list:
                self.__process_multiple()
                self.__multiple_list.clear()
            if len(self.__domain_list[0]) < self.__number_of_samples:
                number_of_files = math.ceil(len(self.__domain_list[0]) / samples_per_file)
            for index in range(number_of_files):
                temp_list = self.__domain_list[0][index*samples_per_file:
                                                    (index+1)*samples_per_file]
                self.__write_attack_to_file(temp_list, self.__output_dir + algo_name + "_" +
                                            str(samples_per_file) + "_" +
                                            str(index+1).zfill(2) + ".txt")
            self.__domain_list.clear()

    def __run_algorithm(self, arguments, file):
        """Run each algorithm script"""
        command_list = [self.__python_path, os.path.basename(file)]
        command_list.extend(arguments)
        os.chdir(self.__org_path + os.path.dirname(file))
        with subprocess.Popen(command_list, stdout=subprocess.PIPE) as proc:
            out = proc.communicate()[0]
        if os.name == "nt":
            temp_domain_list = out.decode("utf-8").split("\r\n")
        else:
            temp_domain_list = out.decode("utf-8").split("\n")
        temp_domain_list.pop()
        if len(temp_domain_list) > self.__number_of_samples:
            temp_domain_list = random.sample(temp_domain_list, self.__number_of_samples)
        elif len(temp_domain_list) < self.__number_of_samples:
            is_limited = self.__check_name_list_in_file(self.__limited, file)[0]
            if not is_limited:
                print("Not enough samples were generated. Generated:", len(temp_domain_list))
        is_multiple = self.__check_name_list_in_file(self.__multiple, file)[0]
        if is_multiple:
            self.__multiple_list.extend(temp_domain_list)
        else:
            self.__domain_list.append(temp_domain_list)

    def __exec_dict_based(self, file):
        """
        Execute the corresponding dict based script.\n
        This function evaluates algorithm name and execute with corresponding params.
        """
        if "suppobox" in file:
            self.__run_algorithm([str(random.randint(1,3)), "-n", str(self.__gen_num)], file)
        else:
            self.__run_algorithm(["-n", str(self.__gen_num)], file)

    def __write_attack_to_file(self, domain_list, output_name):
        """Write the generated samples to a text file"""
        os.chdir(self.__org_path)
        with open(output_name, "w", encoding="utf-8") as file:
            for element in domain_list:
                file.write(element + "\n")

    def __gen_attack_char_based(self):
        """Generate random char based domains"""
        print("Generating char based domains...")
        current_multiple = None
        for file in self.__files:
            which_mul = self.__check_name_list_in_file(self.__multiple, file)[1]
            if current_multiple != which_mul:
                if self.__multiple_list:
                    self.__process_multiple()
                    self.__multiple_list.clear()
                current_multiple = which_mul
            is_dict_based = self.__check_name_list_in_file(self.__dict_based, file)[0]
            if not is_dict_based:
                print(file)
            else:
                continue
            self.__exec_char_based(pathlib.PurePath(file).as_posix())

    def __exec_char_based(self, file):
        """
        Execute the corresponding char based script.\n
        This function evaluates algorithm name and execute with corresponding params.
        """
        char_based_case = {
            "banjori": lambda: self.__case_4(file),
            "corebot": lambda: self.__case_4(file),
            "dircrypt": lambda: self.__case_3(file),
            "dnschanger": lambda: self.__case_3(file),
            "fobber": lambda: self.__case_2(file),
            "fosniw": lambda: self.__case_4(file),
            "kraken": lambda: self.__case_4(file),
            "locky/dgav3.py": lambda: self.__case_4(file),
            "murofet": lambda: self.__case_4(file),
            "mydoom": lambda: self.__case_4(file),
            "necurs": lambda: self.__case_4(file),
            "newgoz": lambda: self.__case_4(file),
            "nymaim": lambda: self.__case_4(file),
            "pitou": lambda: self.__case_4(file),
            "pizd": lambda: self.__case_4(file),
            "proslikefan": lambda: self.__case_4(file),
            "pykspa": lambda: self.__case_4(file),
            "qadars": lambda: self.__case_4(file),
            "qakbot": lambda: self.__case_4(file),
            "ramdo": lambda: self.__case_4(file),
            "ramnit": lambda: self.__case_3(file),
            "ranbyus": lambda: self.__case_1(file),
            "reconyc": lambda: self.__case_4(file),
            "shiotob": lambda: self.__case_0(file),
            "simda": lambda: self.__case_4(file),
            "symmi": lambda: self.__case_4(file),
            "vawtrak": lambda: self.__case_4(file),
            "zloader": lambda: self.__case_4(file),
        }
        is_char_based_with_params = False
        for item in char_based_case.items():
            if item[0] in file:
                is_char_based_with_params = True
                item[1]()
                break
        if not is_char_based_with_params:
            self.__run_algorithm([], file)

    def __case_0(self, file):
        """For shiotob"""
        os.chdir(self.__org_path)
        with open("benign.txt", "r", encoding="utf-8") as temp_file:
            while random.randrange(self.__gen_num):
                temp_file.readline()
            seed_domain = temp_file.readline().rstrip("\n")
        self.__run_algorithm([seed_domain, "-n", str(self.__gen_num)], file)

    def __case_1(self, file):
        """For ranbyus"""
        self.__run_algorithm([], file)

    def __case_2(self, file):
        """For fobber"""
        self.__run_algorithm([str(random.randint(1,2)), "-n", str(self.__gen_num)], file)

    def __case_3(self, file):
        """For dircrypt, dnstracker and ramnit"""
        self.__run_algorithm([str(random.randint(0, self.__gen_num)), "-n",
                                str(self.__gen_num)], file)

    def __case_4(self, file):
        """Most of the cases"""
        self.__run_algorithm(["-n", str(self.__gen_num)], file)

    def __process_multiple(self):
        """Process algorithm that have multiple scripts"""
        if len(self.__multiple_list) <= self.__number_of_samples:
            self.__domain_list.append(self.__multiple_list)
        else:
            self.__domain_list.append(random.sample(self.__multiple_list, self.__number_of_samples))

    @staticmethod
    def __flatten_list(nested_list):
        """Flatten out a 2D nested list"""
        temp = []
        list(map(temp.extend, nested_list))
        return temp

    @staticmethod
    def __check_name_in_list(name, alist):
        """Check if a name is in a list"""
        for elem in alist:
            if name == elem:
                return True
        return False

    @staticmethod
    def __check_name_list_in_file(name_list, file):
        """Check if a list of names is in a filename"""
        for elem in name_list:
            if elem in file:
                return True, elem
        return False, None

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Generate DGAs randomly")
    parser.add_argument("samples", type=int, help="samples per algorithm")
    parser.add_argument("--py_path",
                        help="python path to run algorithm scripts, default to /usr/bin/python3",
                        default= "/usr/bin/python3")
    parser.add_argument("--init_num",
                        help="initial number of generated domains "
                                "before being randomly sampled again",
                        type=int)
    parser.add_argument("--out_dir",
                        help="output directory of the generated domains, "
                                "default to Client/train_file/",
                        default="Client/train_file/")
    extended = parser.add_argument_group("extended functions")
    extended.add_argument("--algo",
                            help="algorithm to generate attack domains")
    extended.add_argument("--file_num",
                            help="number of files to be divided into. "
                                    "This argument usually goes with --algo. "
                                    "If it is specified alone, the script will generate char-based "
                                    "attack domains and divide them into files, the algorithms in "
                                    "all of which will be mutually exclusive to each other",
                            type=int)
    args = parser.parse_args()

    gen = GenerateDGA(args.py_path, args.samples, args.init_num, args.out_dir)
    if args.algo and args.file_num:
        gen.get_attack_by_algo(args.algo, args.file_num)
    elif args.file_num:
        gen.get_attack_char_based_mutually_exclusive(args.file_num)
    elif args.algo:
        parser.error("Both --algo and --file_num flags must be specified together.")
    else:
        for i in range(2):
            if i == 0:
                gen.get_attack_dict_based()
            if i == 1:
                gen.get_attack_char_based()
