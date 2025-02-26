# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: create_plugin_doc
   :platform: Unix
   :synopsis: A module to automatically create plugin documentation

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import os
import re
import sys

from itertools import chain

import savu.plugins.utils as pu


def add_package_entry(f, files_present, output, module_name):
    """Create a contents page for the files and directories contained
    in 'files'. Create links to all the plugin classes which load without
    errors
    """
    if files_present:
        # If files are present in this directory then, depending on the
        # number of nested directories, determine which section heading
        # and title to apply
        title = module_name.replace("savu.", "").split(".")

        if len(title) >= 1:
            f.write(set_heading(title[len(title) - 1], len(title) - 1))

        # For directory contents
        f.write("\n.. toctree::\n")
        # Contents display level is set to have plugin names only
        f.write("   :maxdepth: 1 \n\n")

        for fi in files_present:
            mod_path = module_name + "." + fi.split(".py")[0]
            if "plugin" in output:
                try:
                    # If the plugin class exists, put it's name into the contents
                    plugin_class = pu.load_class(mod_path)
                    file_path = get_path_format(mod_path.replace("savu.", ""),
                                                output)
                    _write_to_contents(f, fi, output, file_path)
                except ValueError:
                    pass
            else:
                file_path = get_path_format(mod_path, output)
                _write_to_contents(f, fi, output, file_path)
        f.write("\n\n")


def _write_to_contents(f, fi, output, file_path):
    """Add the rst file name to the contents page

    :param f: Contents file to write to
    :param fi: file name
    :param output: output directory at which rst files are located
    :param file_path: path to file to include in contents page
    """
    name = convert_title(fi.split(".py")[0])
    f.write(f"   {name} <{output}/{file_path}>\n")


def set_underline(level: int, length: int) -> str:
    """Create an underline string of a certain length

    :param level: The underline level specifying the symbol to use
    :param length: The string length
    :return: Underline string
    """
    underline_symbol = ["`", "#", "*", "-", "^", '"', "="]
    symbol_str = underline_symbol[level] * length
    return f"\n{symbol_str}\n"


def set_heading(title: str, level: int) -> str:
    """Return the plugin heading string

    :param title: Plugin title
    :param level: Heading underline level
    :return: Heading string
    """
    plugin_type = convert_title(title)
    return f"{plugin_type}{set_underline(level, 56)}"


def get_path_format(mod_path, output):
    """Use the module path '.' file name for api documentation
    Use the file path '/' file name for plugin documentation

    :param mod_path: module path for file
    :param output: the type of file output required eg. api or plugin
    :return: string in correct path format
    """
    if output == "plugin_documentation":
        mod_path = mod_path.replace(".", "/")
    return mod_path


def create_plugin_documentation(files, output, module_name, savu_base_path):
    plugin_guide_path = "plugin_guides/"
    for fi in files:
        py_module_name = module_name + "." + fi.split(".py")[0]
        mod_path = py_module_name.replace("savu.", "")
        file_path = get_path_format(mod_path, output)
        try:
            plugin_class = pu.load_class(py_module_name)()
        except (ModuleNotFoundError, AttributeError) as er:
            p_name = py_module_name.split('plugins.')[1]
            print(f"Cannot load {p_name}: {er}")
            plugin_class = None

        if plugin_class:
            tools = plugin_class.get_plugin_tools()
            tools._populate_default_parameters()
            try:
                plugin_tools = plugin_class.tools.tools_list
                if plugin_tools:
                    # Create rst additional documentation directory
                    # and file and image directory
                    create_documentation_directory(
                        savu_base_path, plugin_guide_path, fi
                    )
                    # Create an empty rst file inside this directory where
                    # the plugin tools documentation will be stored
                    full_file_path = f"{savu_base_path}doc/source/reference/{output}/{file_path}.rst"
                    pu.create_dir(full_file_path)
                    with open(full_file_path, "w+") as new_rst_file:
                        # Populate this file
                        populate_plugin_doc_files(
                            new_rst_file,
                            plugin_tools,
                            file_path,
                            plugin_class,
                            savu_base_path,
                            plugin_guide_path,
                        )
            except:
                print(f"Tools file missing for {py_module_name}")


def convert_title(original_title):
    """Remove underscores from string"""
    new_title = original_title.replace("_", " ").title()
    new_title = new_title.replace("Api", "API")
    return new_title


def populate_plugin_doc_files(new_rst_file, tool_class_list, file_path,
                     plugin_class, savu_base_path, plugin_guide_path):
    """Create the restructured text file containing parameter, citation
    and documentation information for the plugin_class

    :param new_rst_file: The new restructured text file which will hold all
                            of the plugin details for this plugin class
    :param tool_class_list: The list of base tool classes for this plugin
    :param file_path: Path to the plugin file
    :param plugin_class: Plugin class
    :param savu_base_path: Savu file path
    """

    title = file_path.split("/")
    # Depending on the number of nested directories, determine which section
    # heading and title to apply
    new_rst_file.write(set_heading(title[-1], 1))

    plugin_data = plugin_class.tools.get_param_definitions()
    plugin_citations = plugin_class.tools.get_citations()
    plugin_docstring = plugin_class.tools.get_doc()

    tool_class = tool_class_list[-1]
    docstring_info = plugin_docstring.get("verbose")

    if docstring_info:
        new_rst_file.write(f"\nDescription{set_underline(3,26)}")
        new_rst_file.write("\n")
        new_rst_file.write(docstring_info)
        new_rst_file.write("\n")

        # Locate documentation file
        doc_folder = savu_base_path + "doc/source/"
        file_str = f"{doc_folder}{plugin_guide_path}{file_path}_doc.rst"
        inner_file_str = f"/../../../{plugin_guide_path}{file_path}_doc.rst"
        if os.path.isfile(file_str):
            # If there is a documentation file
            new_rst_file.write("\n")
            new_rst_file.write(".. toctree::")
            new_rst_file.write(f"\n    Plugin documention and guidelines"
                               f" on use <{inner_file_str}>")
            new_rst_file.write("\n")

    if tool_class.define_parameters.__doc__:
        # Check define parameters exists
        new_rst_file.write(f"\nParameters{set_underline(3,26)}")
        new_rst_file.write("\n.. code-block:: yaml")
        new_rst_file.write("\n")

        if plugin_data:
            # Go through all plugin parameters
            for p_name, p_dict in plugin_data.items():
                new_rst_file.write("\n"
                       + pu.indent_multi_line_str
                           (get_parameter_info(p_name, p_dict), 2))

        # Key to explain parameters
        new_rst_file.write(f"\nKey{set_underline(4,10)}")
        new_rst_file.write("\n")
        new_rst_file.write(
            ".. literalinclude:: "
            "/../source/files_and_images/"
            + plugin_guide_path
            + "short_parameter_key.yaml"
        )
        new_rst_file.write("\n    :language: yaml\n")

    if plugin_citations:
        # If documentation information is present, then display it
        new_rst_file.write(f"\nCitations{set_underline(3,26)}")

        write_citations_to_file(new_rst_file, plugin_citations)


def get_parameter_info(p_name, parameter):
    exclude_keys = ["display"]
    parameter_info = p_name + ":\n"
    try:
        keys_display = {k:v for k,v in parameter.items() if k not in exclude_keys}
        parameter_info = create_disp_format(keys_display, parameter_info)
    except Exception as e:
        print(str(e))
    return parameter_info


def create_disp_format(in_dict, disp_string, indent_level=1):
    """ Create specific documentation display string in yaml format

    :param dict: dictionary to display
    :param disp_string: input string to append to
    :return: final display string
    """
    for k, v in in_dict.items():
        list_display = isinstance(v, list) and indent_level > 1
        if isinstance(v, dict):
            indent_level += 1
            str_dict = create_disp_format(v, "", indent_level)
            indent_level -= 1
            str_val= f"{k}: \n{str_dict}"
        elif list_display:
            indent_level += 1
            list_str = ''
            for item in v:
                list_str += pu.indent(f"{item}\n", indent_level)
            indent_level -= 1
            str_val = f"{k}: \n{list_str}"
        elif isinstance(v, str):
            # Check if the string contains characters which may need
            # to be surrounded by quotes
            v = v.strip()
            str_val = f'{k}: {v}' if no_yaml_char(v) else f'{k}: "{v}"'
        elif isinstance(v, type(None)):
            str_val = f"{k}: None"
        else:
            str_val = f'{k}: "{v}"'
        if not isinstance(v, dict) and not list_display:
            # Don't append a new line for dictionary entries
            str_val += "\n"
        disp_string += pu.indent(str_val, indent_level)
    return disp_string


def no_yaml_char(s):
    """Check for characters which prevent the yaml syntax highlighter
    from being applied. For example [] and ? and '
    """
    return bool(re.match(r"^[a-zA-Z0-9()%|#\"/._,+\-=: {}<>]*$", s))


def write_citations_to_file(new_rst_file, plugin_citations):
    """Create the citation text format """
    for name, citation in plugin_citations.items():
        new_rst_file.write(
            f"\n{name.lstrip()}{set_underline(4, 182).rstrip()}"
        )
        if citation.dependency:
            # If the citation is dependent upon a certain parameter value
            # being chosen
            for (
                citation_dependent_parameter,
                citation_dependent_value,
            ) in citation.dependency.items():
                new_rst_file.write(
                    "\n(Please use this citation if "
                    "you are using the "
                    + citation_dependent_value
                    + " "
                    + citation_dependent_parameter
                    + ")\n"
                )
        bibtex = citation.bibtex
        endnote = citation.endnote
        # Where new lines are, append an indentation
        if bibtex:
            new_rst_file.write(f"\nBibtex{set_underline(5,42)}")
            new_rst_file.write("\n.. code-block:: none")
            new_rst_file.write("\n\n")
            new_rst_file.write(pu.indent_multi_line_str(bibtex, True))
            new_rst_file.write("\n")

        if endnote:
            new_rst_file.write(f"\nEndnote{set_underline(5,42)}")
            new_rst_file.write("\n.. code-block:: none")
            new_rst_file.write("\n\n")
            new_rst_file.write(pu.indent_multi_line_str(endnote, True))
            new_rst_file.write("\n")

    new_rst_file.write("\n")


def create_documentation_directory(savu_base_path,
                                   plugin_guide_path,
                                   plugin_file):
    """ Create plugin directory inside documentation and
    documentation file and image folders
    """
    # Create directory inside
    doc_path = f"{savu_base_path}doc/source/"
    doc_image_path = f"{savu_base_path}doc/source/files_and_images/" \
                     f"{plugin_guide_path}plugins/"

    # find the directories to create
    doc_dir = doc_path + plugin_guide_path + plugin_file
    image_dir = doc_image_path + plugin_file
    pu.create_dir(doc_dir)
    pu.create_dir(image_dir)


def _select_relevant_files(api_type):
    """ Select the folder related to the api_type
    Exclude certain files and directories based on api_type

    :param api_type: framework or plugin api
    :return: The base file path for the api files to document
       The list of files to exclude from api
    """
    if api_type == 'framework':
        base_path = savu_base_path + "savu"
        exclude_dir = ["__pycache__",
                       "test",
                       "plugins"]
        exclude_file = ["__init__.py", "win_readline.py"]
    elif api_type == 'plugin':
        base_path = savu_base_path + "savu/plugins"
        exclude_file = [
            "__init__.py",
            "docstring_parser.py",
            "plugin.py",
            "plugin_datasets.py",
            "plugin_datasets_notes.py",
            "utils.py",
            "plugin_tools.py",
        ]
        exclude_dir = ["driver",
                       "utils",
                       "unregistered",
                       "under_revision",
                       "templates",
                       "__pycache__",
                       "test"
                       ]
    else:
        raise Exception('Unknown API type', api_type)
    return base_path, exclude_file, exclude_dir


def _create_api_content(savu_base_path, out_folder, api_type,
                        base_path, exclude_file, exclude_dir, f):
    """Populate API contents pages"""
    for root, dirs, files in os.walk(base_path, topdown=True):
        tools_files = [fi for fi in files if "tools" in fi]
        template_files = [fi for fi in files if "template" in fi]
        base_files = [fi for fi in files if fi.startswith("base")]
        driver_files = [fi for fi in files if "driver" in fi]
        exclude_files = [
            exclude_file,
            tools_files,
            base_files,
            driver_files,
            template_files
        ]
        dirs[:] = [d for d in dirs if d not in exclude_dir]
        files[:] = [fi for fi in files if fi not in chain(*exclude_files)]
        files[:] = [fi for fi in files if fi.split('.')[-1] == 'py']

        # Exclude the tools files from html view sidebar
        if "__" not in root:
            pkg_path = root.split("Savu/")[1]
            module_name = pkg_path.replace("/", ".")
            if "plugins" in module_name and api_type == 'plugin':
                add_package_entry(f, files, out_folder, module_name)
                if out_folder == "plugin_documentation":
                    create_plugin_documentation(
                        files, out_folder, module_name, savu_base_path
                    )
            elif api_type == 'framework':
                add_package_entry(f, files, out_folder, module_name)


if __name__ == "__main__":
    out_folder, rst_file, api_type = sys.argv[1:]

    # determine Savu base path
    main_dir = \
        os.path.dirname(os.path.realpath(__file__)).split("/Savu/")[0]
    savu_base_path = f"{main_dir}/Savu/"

    base_path, exclude_file, exclude_dir = _select_relevant_files(api_type)

    # Create the directory if it does not exist
    pu.create_dir(f"{savu_base_path}doc/source/reference/{out_folder}")

    # open the autosummary file
    with open(f"{savu_base_path}doc/source/reference/{rst_file}", "w") as f:

        document_title = convert_title(out_folder)
        f.write(".. _" + out_folder + ":\n")
        f.write(f"{set_underline(2,22)}{document_title} "
                f"{set_underline(2,22)}\n")

        _create_api_content(savu_base_path, out_folder, api_type, base_path,
                            exclude_file, exclude_dir, f)
