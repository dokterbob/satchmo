#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Webda 0.9.8. Loader of CSV data.
Copyright (c) 2006,  Webda Project

Released under the BSD license.

Jonás Melián <jonas.esp AT gmail com>
http://webda.python-hosting.com
"""

import csv
import fileinput
import glob
import os
import os.path
import re
import sys

try:
    from django.conf import settings  # 'conf.settings' is passed to syncdb.
except ImportError, err:
    sys.stderr.write("Error: %s. Are you sure Django is installed?\n" % err)
    sys.exit(1)

from django.core.management import call_command
from django.db import transaction

def get_data_models(models_file):
    """Get the name of all models and fields. And add information about
    numeric fields and keys.

    The numeric fields have as format:
    #[numeric X position]...

    And the keys:
    :K-[num. pos. of key],[model related]
    """
    list_models = []
    model = []
    pos_numeric = []  # Position of numeric fields
    info_keys = []  # Info. about keys
    re_field = re.compile('\s+\w+\s*=\s*models\.')  # Line with field name
    re_class = re.compile('\s+class ')  # For Admin and Meta
    re_def = re.compile('\s+def ')
    is_new_model = False

    for line in open(models_file):
        # The models start with 'class'
        if not is_new_model and line.startswith('class'):
            model_name = line.replace('class','').split('(')[0].strip()
            model.append(model_name)
            is_new_model = True
        elif is_new_model:
            if re_field.match(line):
                field_name = line.split('=')[0].strip()
                model.append(field_name)

                if 'models.DecimalField' in line or 'models.IntegerField' in line:
                    pos_numeric.append(len(model)-2)  # Discard model name.
                elif 'models.ForeignKey' in line:
                    key_name = line.split('(')[-1].strip().strip(')')
                    position = len(model)-2  # Discard model name.
                    info_keys.append(':')
                    info_keys.append(str(position) + ',')
                    info_keys.append(key_name)
            # It is supposed that models in localization has at the end:
            # ('class Meta', 'class Admin', or some 'def')
            elif re_class.match(line) or re_def.match(line):
                if pos_numeric:
                    pos_num2str = '#'
                    for num in pos_numeric:
                        pos_num2str += str(num)
                    model.append(pos_num2str)
                    model.append(':N')  # To detect the numeric field.
                    pos_numeric = []
                if info_keys:
                    all_keys = ""
                    for key in info_keys:
                        all_keys += key
                    model.append(all_keys)
                    model.append(':K')  # To detect fastly some key.
                    info_keys = []
                list_models.append(model)
                model = []
                is_new_model = False

    return list_models

def sort_models(data_dir, list_models):
    """The models with keys (foreign, etc) go at the end.
    """
    list_new_models = []  # Only left fields in CSV file.

    try:
        os.chdir(data_dir)
    except OSError, err:
        sys.stderr.write("Error: %r. %s.\n" % (err.filename, err.strerror))
        sys.exit(1)

    csv_files = glob.glob('*.csv')
    if not csv_files:
        sys.stderr.write('Error: Not found CSV files.\n')
        sys.exit(1)

    for csv in csv_files:
        list_new_models.append(check_header(csv, list_models))

    for model in list_new_models[:]:
        # Put models with ForeignKey in the last positions
        if ':K' in model and \
          list_new_models.index(model) < len(list_new_models)-1:
            list_new_models.append(model)
            list_new_models.remove(model)

    return list_new_models

def check_header(csv_file, list_models):
    """Get and check data from CSV header, create a new list of models and
    insert the file CSV name in model line.

    Format: -*- [Model_name]> [field_1]:[field_2]:[field_n] -*-
    """
    new_model = []
    is_code = False
    is_full_code = False
    code = '-*-'

    # Get line with info. about model.
    try:
        read_f = open(csv_file)
    except IOError, err:
        sys.stderr.write("Error: %r. %s.\n" % (err.filename, err.strerror))
        sys.exit(1)

    for line in read_f:
#        if line[:1] == '#':  #  For use in list of strings
        if line[0] == '#':
            if not is_code and code in line:
                is_code = True
                code_line = line.rstrip().split('>')
                if code_line[-1].endswith(code):
                    is_full_code = True
                    break
            elif is_code:
                if ':' in line:
                    code_line.append(line.rstrip())
                    if code_line[-1].endswith(code):
                        is_full_code = True
                        break
                else:
                    break
        else:  # No comments.
            break
    read_f.close()

    if not is_code:
        sys.stderr.write("Error: %r. Code line not found.\n" % csv_file)
        sys.exit(1)
    if not is_full_code:
        sys.stderr.write("Error: %r. Code line not finished with %r.\n" \
            % (csv_file, code))
        sys.exit(1)

    # Delete '#', code symbol, and strip spaces.
    fields = ''
    i = 0
    for part in code_line[:]:
        code_line[i] = part.replace('#','').replace(code,'').strip()
        if i > 0:  # Adjust the separation character, ':'
            if code_line[i].startswith(':'):
                code_line[i] = code_line[i][1:]
            if not part.endswith(':'):
                code_line[i] += ':'
            fields += code_line[i]
        i += 1

    model = code_line[0]
    fields = fields[:-1]  # Delete the last ':'
    # Fields name of model in CSV file separated by ':'
    csv_fields = [ x.strip() for x in fields.split(':') ]

    # Check header and build new list.
    for data_model in list_models:
        if data_model[0] == model:  # Check model name.
            new_model.append(model)  # Add model name.
            for field in csv_fields:
                if field in data_model:  # Check fields.
                    new_model.append(field)  # Add field.
                elif field:  # Could be an empty field.
                    sys.stderr.write("Error: %r. Field name %r is not\
 correct.\n" % (csv_file, field))
                    sys.exit(1)

            # Insert name of CSV file
            new_model.insert(0, csv_file)
            # Insert both numeric and key fields
            new_model += [ x for x in data_model if '#' in x or ':' in x ]
            break

    if not new_model:
        sys.stderr.write("Error: %r. Model name %r is not correct.\n" \
            % (csv_file, model))
        sys.exit(1)

    return new_model

def comment_stripper(iterator):
    """Generator that filters comments and blank lines.
    Used as input to 'cvs.reader'.
    """
    for line in iterator:
        if line [:1] == '#':
            continue
        if not line.strip ():
            continue
        yield line

def load_data(model, i18n_model, i18n_dirname):
    """Get the fields position where there are numbers.
    """
    position_num = []
    dic_keys = {}
    csv_separator = ':'
    re_num = re.compile('\d+$')

    # Get only the fields name
    fields = [ x for x in model[2:] if not (':' in x or '#' in x) ]
    # Get left data.
    fields_number = len(fields)
    csv_file = model[0]
    model_name = model[1]
    print "Adding data in %s.%s table" % (i18n_dirname, model_name)
    # Load the class of the models file
    exec "%s = getattr(i18n_model, model_name)" % model_name

    # Get the position of numeric fields
    if ':N' in model:
        pos = model.index(':N')
        position_num = model[pos-1]  # The field numeric is before of ':N'
        position_num = [ int(x) for x in position_num if not '#' in x ]

    # Info. about keys
    if ':K' in model:
        pos = model.index(':K')
        info_keys = model[pos-1]
        # Format-> :[position],[model name]:...
        info_keys = info_keys.split(':')[1:]
        keys = [ (int(x.split(',')[0]), x.split(',')[1]) for x in info_keys ]
        dic_keys = dict(keys)

        # To store the keys. Set to values null
        model_id = {}
        for x in dic_keys.keys():
            model_id.setdefault(x, None)

    # Convert from CSV to Django ORM
    reader = csv.reader(comment_stripper(
                        open(csv_file)), delimiter=csv_separator)

    line_bool = []  # Lines where is enabled a boolean field.
    bool_found = False
    line_number = 0
    for csv_line in reader:
        #debug
#        if \
#        model_name == "Phone" or \
#        model_name == "AddressFormat":
#        model_name == "Country" or \
#        model_name == "CountryLanguage" or \
#        model_name == "Language" or \
#        model_name == "Subdivision" or \
#        model_name == "TimeZone" or
#            print "\tskip"
#            break

        object_line = []
        key_line_s = []
        line_number += 1

        object_line.append("c%d = %s(" % (line_number, model_name))

        for position in range(0, fields_number):
            field_text = csv_line[position]
            if field_text == 'True':
                if not bool_found:
                    bool_field = fields[position]
                    bool_found = True
                line_bool.append(line_number)
            elif field_text:  # If is not empty
                key_line = []
                if object_line[-1][-1] != '(':  # Check the last character
                    object_line.append(', ')
                # If is a key
                if dic_keys and dic_keys.has_key(position):
                    object_line.append('%s=key_id%d'
                                       % (fields[position], position))
                    key_model = dic_keys.get(position)

                    # Load the class of the foreigner model.
                    try:
                        eval("%s" % key_model)
                    except NameError:
                        exec "%s = getattr(i18n_model, key_model)" %key_model

                    if csv_line[position] != model_id.get(position):
                        model_id[position] = csv_line[position]

                        key_line.append('key_id%d = %s.objects.get(pk='
                                        % (position, key_model))
                        if re_num.match(model_id.get(position)):  # integer
                            key_line.append('%d)' % model_id.get(position))
                        else:
                            key_line.append('"%s")' % model_id.get(position))

                        key_line = ''.join(key_line)
                        key_line_s.append(key_line)

                # If is an integer
                elif position in position_num:
                    object_line.append('%s=%s' \
                        % (fields[position], csv_line[position]))
                # If is a string.
                else:
                    object_line.append('%s="%s"' \
                        % (fields[position], csv_line[position]))

        if key_line_s:
            for key in key_line_s:
#                print key #debug
                exec(key)

        object_line.append(")")
        load_object = ''.join(object_line)
#        print load_object #debug
        exec(load_object)  # Load the object

    # At the end, save all objects together
    if model_name == 'Language':
        # Display the english language.
        for num in range(1, line_number+1):
            obj = eval("c%d" % num)
            if obj.iso3_code == 'eng':
                obj.display = True
            obj.save()
    else:
        for num in range(1, line_number+1):
            obj = eval("c%d" % num)
            if num in line_bool:
                exec("obj.%s = True" % bool_field)
            try:
            	obj.save()
            except:
                print "Problem loading data.  Entry will not be loaded."
                try:
                    transaction.rollback()
                except:
                    #Some databases were having trouble with the rollback
                    pass

def show_license(license):
    """Show the license and continues if the user is agree with it.
    """
    if not os.path.isfile(license):
        sys.stderr.write("Error: %r. Not exist such license file.\n\
The data license has to be there before of continue.\n" % license)
        sys.exit(1)

    try:
        read_f = open(license)
    except IOError, err:
        sys.stderr.write("Error: %r. %s.\n" % (err.filename, err.strerror))
        sys.exit(1)

    print
    print ('=' * 78)
    for line in read_f:
        print line.rstrip()
    read_f.close()
    print ('=' * 78)
    print "\nBy writing 'yes' I am affirmatively declaring that"
    print "I have read, understand and agree to the license above."

    try:
        answer = raw_input('Do you accept the license? ')
        if answer.lower() != 'yes':
            sys.exit(0)
    except KeyboardInterrupt:
        print
        sys.exit(0)

    print

def setup_environ(project_dir, i18n_dirname, set_file):
    """Configure the runtime environment.
    Based on django.core.management.setup_environ()
    """
    if not os.path.exists(set_file):
        sys.stderr.write("Error: You are not into a Django's project\
 directory.\n")
        sys.exit(1)

    project_name = os.path.basename(project_dir)
    i18n_app = "%s.%s" % (project_name, i18n_dirname)  # Name of I18n app.
    # Set DJANGO_SETTINGS_MODULE appropriately.
    os.environ['DJANGO_SETTINGS_MODULE'] = "%s.settings" % project_name

    # Add parent's directory to sys.path so that the module is importable.
    sys.path.append(os.path.dirname(project_dir))
    try:
        i18n_model = __import__("%s.models" % (i18n_app), {}, {}, [''])
    except ImportError, err:
        sys.stderr.write("Error: %s. Are you sure I18n app. is installed?\n" \
            % err)
        sys.exit(1)
    sys.path.pop()

    # If it is not installed, it looking for the line and insert it.
    if i18n_app not in settings.INSTALLED_APPS:
        print "Activating %s application" % i18n_dirname
        is_header = False  # Look for 'INSTALLED_APPS'.
        try:
            write_f = fileinput.input(set_file, inplace=1)
        except IOError, err:
            sys.stderr.write("Error: %r. %s.\n" % (err.filename, err.strerror))
            sys.exit(1)

        for line in write_f:
            if not is_header and 'INSTALLED_APPS' in line:
                is_header = True
            elif is_header and ')' in line:
                print "    '%s'," % i18n_app
                is_header = False
            print line[:-1]
        write_f.close()

        # Create the tables for I18n application.
        # Could add I18n application to the variable but don't
        # since that is only necessary create the tables for I18n.
        settings.INSTALLED_APPS = []
        settings.INSTALLED_APPS.append("%s" % i18n_app)
        call_command('syncdb')

    return i18n_model


def main():
    """Prepopulate the information from CSV data into tables.
    The header format in the CSV files has to be:
    * [Model name], [field 1] [, field 2, ... field n] *
    """
    actual_dir = os.getcwd()
    i18n_dir = os.path.join(actual_dir, 'i18n')  # Directory of I18n app.
    i18n_dirname = os.path.basename(i18n_dir)
    models_file = os.path.join(i18n_dir, 'models.py')
    data_dir = os.path.join(i18n_dir, 'data')  # CSV files.
    data_license = os.path.join(data_dir, 'LICENSE_CC')
    project_dir = os.path.dirname(i18n_dir)
    settings_file = os.path.join(project_dir, 'settings.py')

    show_license(data_license)
    i18n_model = setup_environ(project_dir, i18n_dirname, settings_file)
    models = get_data_models(models_file)
    new_models = sort_models(data_dir, models)
    for model in new_models:
        load_data(model, i18n_model, i18n_dirname)

if __name__ == '__main__':
    main()
