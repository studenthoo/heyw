# !/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import re
import time
import json
import datetime

# constant
base_yaml_txt = "base_yaml_path.txt"
base_yaml_json = "base_yaml_path.json"
base_dir = os.path.dirname(os.path.abspath(__file__))
base_yaml_txt_path = os.path.join(base_dir, 'yaml', base_yaml_txt)
base_yaml_json_path = os.path.join(base_dir, 'yaml', base_yaml_json)
base_yaml_file = os.path.join(base_dir, 'yaml', 'base_yaml.yaml')


class ManageYamlFile(object):

    def __init__(self, base_yaml):
        self._base_yaml = base_yaml
        self._base_yaml_path_list = []
        self._new_yaml_path_dir = os.path.join(base_dir, 'yaml')

    def get_base_yaml_path_list(self):
        return self._base_yaml_path_list

    def load_base_yaml_path_json(self):
        with open(base_yaml_json_path, 'r+') as r_file:
            for line in r_file.readlines():
                line = json.loads(line)
                print line
                self.base_yaml_path.append(line)

    def load_base_yaml_path_txt(self):
        with open(base_yaml_txt_path, 'r+') as r_file:
            for line in r_file.readlines():
                li = eval(line)
                self._base_yaml_path_list.append(li)

        pass

    def create_new_yaml(self, base_yaml, arguments,
                        new_yaml="new_yaml_03.yaml",
                        selector_name="base-01",
                        labels_name="base-01",
                        metadata_name="base-01",
                        kind="ReplicationController",
                        image="hyperaidev:caffetf20171204",
                        command='["/usr/bin/python2"]',
                        replicas=str(1),
                        **kwargs):

        if not isinstance((base_yaml, new_yaml, arguments,
                           selector_name, labels_name,
                           metadata_name, kind, image, command,
                           replicas), str):
            raise ValueError("Not all string.")
        if base_yaml:
            new_yaml = os.path.join(self._new_yaml_path_dir, new_yaml)
            with open(base_yaml, mode='r+') as r_file:
                with open(new_yaml, 'w+') as w_file:
                    for line in r_file.readlines():

                        if line.find("$kind$") >= 0:
                            new_line = line.replace("$kind$", kind)
                            w_file.write(new_line)
                        elif line.find("$replicas$") >= 0:
                            new_line = line.replace("$replicas$", replicas)
                            w_file.write(new_line)
                        elif line.find("$metadata-name$") >= 0:
                            new_line = line.replace("$metadata-name$", metadata_name)
                            w_file.write(new_line)
                        elif line.find("$selector-name$") >= 0:
                            new_line = line.replace("$selector-name$", selector_name)
                            w_file.write(new_line)
                        elif line.find("$labels-name$") >= 0:
                            new_line = line.replace("$labels-name$", labels_name)
                            w_file.write(new_line)
                        elif line.find("$image$") >= 0:
                            new_line = line.replace("$image$", image)
                            w_file.write(new_line)
                        elif line.find("$command$") >= 0:
                            new_line = line.replace("$command$", command)
                            w_file.write(new_line)
                        elif line.find("$args$") >= 0:
                            new_line = line.replace("$args$", args)
                            w_file.write(new_line)
                        else:
                            w_file.write(line)
            return new_yaml
        else:
            print "Not found the file."
            return None
        pass

        pass

    def get_base_yaml_path(self, base_yaml):
        """

        :param base_yaml:
        :return: string
        """
        # base_yaml_pattern = re.compile(r'{}'.format(base_yaml))
        if self.base_yaml_path:
            for i in self.base_yaml_path:
                # if i[]
                pass

    def save_baes_yaml_path_json(self, meta):
        """

        :param meta:
        :return:
        """
        current_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if meta:
            file_name = meta[0] if not meta[0].startswith(r"/") else meta[1]
            base_yaml_path = meta[1] if meta[1].startswith(r"/") else meta[0]
            data = {"name": file_name, "path": base_yaml_path, "time": current_time}
            with open(base_yaml_json_path, 'a') as w_file:
                json.dump(data, w_file)
                w_file.write("\n")

    def save_baes_yaml_path_txt(self, meta):
        """

        :param meta:  
        :return:
        """
        current_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if meta:
            file_name = meta[0] if not meta[0].startswith(r"/") else meta[1]
            base_yaml_path = meta[1] if meta[1].startswith(r"/") else meta[0]
            data = {"name": file_name, "path": base_yaml_path, "time": current_time}
            with open(base_yaml_txt_path, 'a') as w_file:
                w_file.write(str(data))
                w_file.write("\n")
