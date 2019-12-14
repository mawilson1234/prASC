##############################################################################################
##### Master script prASC.py for processing ASCs to R-ready data frame by Michael Wilson #####
########### Based on Preprocessing_FromASCs.py and question_acc.py by Brian Dillon ###########
########################### Calls fix_align by Andrew Cohen (2013) ###########################
##############################################################################################

import os, re, sys, subprocess, argparse
from pathlib import Path

# Define the arguments, and deal with some of their combinations
parser = argparse.ArgumentParser()
parser.add_argument('filename', nargs = '?', default = Path(os.path.dirname(os.path.realpath(__file__))) / "parameters.py", 
	help = "Optional argument to provide the parameter file. Default assumes filename 'parameters.py' in the executing directory.")
parser.add_argument('-o', '--overwrite', default = False, action = 'store_true', 
	help = "Optional argument to specify whether to overwrite existing results.")
parser.add_argument('-k', '--keepall', default = False, action = 'store_true', 
	help = "Optional argument to keep non-combined results files.")
parser.add_argument('-r', '--refix', default = False, action = 'store_true', 
	help = "Optional argument to re-fix align ASCs that have existing fix aligned versions.")
parser.add_argument('-nf', '--nofix', default = False, action = "store_true", 
	help = "Optional argument to not fix align ASCs. When this is set, further analysis will use ASCs in the ASC directory specified in parameters.py, which can lead to missing data if they have not been previously cleaned. To use pre-existing fix aligned ASCs, set fa_output_dir to the directory containing them, and do not use the '--refix' option.")
parser.add_argument('-ns', '--nosentences', default = False, action = "store_true", 
	help = "Optional argument to not process sentence information using SideEye.")
parser.add_argument('-v', '--verbose', default = False, action="store_true", 
	help = "Optional argument to print information about question accuracy to the console.")
parser.add_argument('-nq', '--noquestions', default = False, action = "store_true", 
	help = "Optional argument to not process question information from ASCs.")
parser.add_argument('-nc', '--nocombine', default = False, action = "store_true", 
	help = "Optional argument to not combine results files. If this is set, keepall will automatically be set.")

args = parser.parse_args()
if args.filename:
	parameters_loc = args.filename
else:	
	parameters_loc = Path(os.path.dirname(os.path.realpath(__file__))) / "parameters.py"

if args.nofix and args.nosentences and args.noquestions and args.nocombine:
	print("Nothing to do with all of nofix, nosentences, noquestions, and nocombine set. Exiting...")
	sys.exit(0)

if args.refix and args.nofix:
	print("Warning: refix and nofix cannot both be set. nofix will be respected.")
	args.refix = False

if args.nocombine:
	args.keepall = True

if not args.nocombine and args.nofix:
	print("Warning: combining results without fix aligning ASCs. If your ASCs have not been previously corrected, this can lead to errors due to missing data.")

if not args.nosentences:
	import sideeye

if not args.nocombine:
	import pandas

# Read in the parameters file and set default values
with Path(os.path.dirname(os.path.realpath(__file__))) as current_dir:
	# Read in and execute the parameters file
	while True:
		try:
			if not re.match('.*\.py$', str(parameters_loc)):
				parameters_loc = Path(str(parameters_loc) + '.py')
			parameters = open(parameters_loc,'r')
			whole_file = parameters.read()
			exec(whole_file)
			break
		except:
			parameters_loc = Path(input("Error: no parameters file found. Please specify a parameters file location: "))
			if not re.match('.*\.py$', str(parameters_loc)):
				parameters_loc = Path(str(parameters_loc) + '.py')

	# If there is no asc_files_dir specified in the parameters file, assume it's in the current directory
	
	# If the directory does not contain ASC files, prompt for one until we get one that does
	while True:
		if not 'asc_files_dir' in globals():
			asc_files_dir = current_dir / "ASC"

		if not args.nofix or not args.nosentences or not args.noquestions:
			if not asc_files_dir:
				asc_files_dir = "."
			try:
				if len([f for f in os.listdir(asc_files_dir) if '.asc' in f]) == 0:
					asc_files_dir = Path(input(f"Error: no ASC files found in '{asc_files_dir}'. If your ASC files have already been fix aligned, set the asc_files_dir to the location of your fix aligned files, and use the '--nofix' ('-nf') option. Please enter a directory containing ASC files: "))
					if not asc_files_dir:
						asc_files_dir = current_dir / "ASC"
				else:
					break
			except:
				asc_files_dir = Path(input(f"Error: no ASC files found in '{asc_files_dir}'. If your ASC files have already been fix aligned, set the asc_files_dir to the location of your fix aligned files, and use the '--nofix' ('-nf') option. Please enter a directory containing ASC files: "))
				if not asc_files_dir:
					asc_files_dir = current_dir / "ASC"

			asc_files_dir = Path(asc_files_dir)
		else:
			break

	if not args.nosentences or not args.noquestions or not args.nocombine:
		if not 'output_dir' in globals():
			output_dir = Path(current_dir) / "prASCed results"
		else:
			output_dir = Path(output_dir)
		
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

		output_dir = Path(output_dir)

	if not args.nosentences or not args.noquestions:
		if not 'config_json_loc' in globals():
			config_json_loc = current_dir / "config.json"

		if not re.match('.*\.json$', str(config_json_loc).lower()):
			config_json_loc = Path(str(config_json_loc) + '.json')

		while not os.path.isfile(config_json_loc):		
			config_json_loc = Path(input("Error: no SideEye config file found. Please enter a valid location: "))			
			if not re.match('.*\.json$', str(config_json_loc).lower()):
				config_json_loc = Path(str(config_json_loc) + '.json')
			if not config_json_loc:
				config_json_loc = current_dir / "config.json"

		config_json_loc = Path(config_json_loc)

	if not args.nosentences:
		if not 'sentences_txt_loc' in globals():
			sentences_txt_loc = current_dir / "sentences.txt"

		if not re.match('.*\.txt$', str(sentences_txt_loc).lower()):
			sentences_txt_loc = Path(str(sentences_txt_loc) + '.txt')

		while not os.path.isfile(sentences_txt_loc):
			sentences_txt_loc = Path(input("Error: no sentences.txt file found. Please enter a valid location: "))			
			if not re.match('.*\.txt$', str(sentences_txt_loc).lower()):
				sentences_txt_loc = Path(str(sentences_txt_loc) + '.txt')
			if not sentences_txt_loc:
				sentences_txt_loc = current_dir / "sentences.txt"

		sentences_txt_loc = Path(sentences_txt_loc)

	if not args.noquestions:
		if not 'start_flag' in globals():
			start_flag = "TRIALID"
		else:
			start_flag = str(start_flag).upper()

		while not re.match('^TRIALID$|^SYNCTIME$', start_flag):
			start_flag = str(input("Error: invalid setting for start_flag. Please enter one of: TRIALID, SYNCTIME: ")).upper()
		if not start_flag:
			start_flag = "TRIALID"

		def strip_quotes(input):
			return re.sub(r'^\'|^"|\'$|"$', '', str(input))

	# Stimuli loc is optional, but print a warning if we're not using it, also check for file_encoding
	if not args.nocombine:
		if not 'stimuli_loc' in globals():
			stimuli_loc = "".join([current_dir / f for f in os.listdir(current_dir) if '-formatted.csv' in f])

		if not re.match('.csv$', str(stimuli_loc).lower()):
			stimuli_loc = Path(str(stimuli_loc) + '.csv')

		if not os.path.isfile(stimuli_loc):
			print("Warning: stimuli-formatted.csv not found. Stimuli information will not be added to results.")
			stimuli_loc = ""

		if len(re.findall("-formatted.csv", str(stimuli_loc))) > 1:
			print("Error: multiple stimuli files found. Not adding stimuli to results.")
			stimuli_loc = ""

		stimuli_loc = Path(stimuli_loc)

		# This can be determined automatically, but it takes a looooong time
		if not 'file_encoding' in globals():
			file_encoding = 'latin1'

	if not args.nofix:
		if not 'fix_align_loc' in globals():
			fix_align_loc = current_dir / "fix_align_v0p92.r"

		if not re.match('.*\.r$', str(fix_align_loc).lower()):
			fix_align_loc = Path(str(fix_align_loc) + '.r')

		while not os.path.isfile(fix_align_loc):
			fix_align_loc = Path(input("Error: no fix_align file found. Please enter a valid location: "))			
			if not re.match('.*\.r$', str(fix_align_loc).lower()):
				fix_align_loc = Path(str(fix_align_loc) + '.r')
			if not fix_align_loc:
				fix_align_loc = current_dir / "fix_align_v0p92.R"

		fix_align_loc = Path(fix_align_loc)

		if not 'script_loc' in globals():
			script_loc = "".join([f for f in os.listdir(current_dir) if '.script' in f])

		if not re.match('.*\.script$', str(script_loc).lower()):
			script_loc = Path(str(script_loc) + '.script')

		if len(re.findall("\.script$", str(script_loc).lower())) > 1:
			print("Error: multiple script files found. Not importing start_pts from script.")
			script_loc = ""

	if not args.nosentences or not args.nocombine:
		csv_loc = Path(output_dir) / "results.csv"

# Fix align parameters to use for function call, defaults are as in Cohen (2013), except for file_plots
if not args.nofix:
	if not 'fa_output_dir' in globals():
		fa_output_dir = Path(asc_files_dir) / "Fix Aligned"
	else:
		fa_output_dir = Path(fa_output_dir)

	if not 'xy_bounds' in globals():
		xy_bounds = "NULL"
	else:
		xy_bounds = str(xy_bounds).upper()

	while not re.match('^NULL$|^c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*\)\s*$|^rbind\s*\((\s*c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*\)\s*,\s*)+\s*c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*\)\s*\)$', xy_bounds):
		xy_bounds = str(input("Error: xy_bounds improperly defined. Please enter xy_bounds: ")).upper()
		if not xy_bounds:
			xy_bounds = "NULL"

	boolean_check = re.compile('^T$|^F$|^TRUE$|^FALSE$')

	if not 'keep_y_var' in globals():
		keep_y_var = "FALSE"
	else:
		keep_y_var = str(keep_y_var).upper()

	while not boolean_check.match(keep_y_var):
		keep_y_var = str(input("Error: invalid setting for keep_y_var. Please enter T or F: ")).upper()
		if not keep_y_var:
			keep_y_var = "FALSE"

	if not 'use_run_rule' in globals():
		use_run_rule = "TRUE"
	else:
		use_run_rule = str(use_run_rule).upper()

	while not boolean_check.match(use_run_rule):
		use_run_rule = str(input("Error: invalid setting for use_run_rule. Please enter T or F: ")).upper()
		if not use_run_rule:
			use_run_rule = "TRUE"

	if not 'trial_plots' in globals():
		trial_plots = "FALSE"
	else:
		trial_plots = str(trial_plots).upper()

	while not boolean_check.match(trial_plots):
		trial_plots = str(input("Error: invalid setting for trial_plots. Please enter T or F: ")).upper()
		if not trial_plots:
			trial_plots = "FALSE"

	if not 'save_trial_plots' in globals():
		save_trial_plots = "FALSE"
	else:
		save_trial_plots = str(save_trial_plots).upper()

	while not boolean_check.match(save_trial_plots):
		save_trial_plots = str(input("Error: invalid setting for save_trial_plots. Please enter T or F: ")).upper()
		if not save_trial_plots:
			save_trial_plots = "FALSE"

	if not 'summary_file' in globals():
		summary_file = "TRUE"
	else:
		summary_file = str(summary_file).upper()

	while not boolean_check.match(summary_file):
		summary_file = str(input("Error: invalid setting for whether to generate fix_align summary file. Please enter T or F: ")).upper()
		if not summary_file:
			summary_file = "TRUE"

	if not 'show_image' in globals():
		show_image = "FALSE"
	else:
		show_image = str(show_image).upper()

	while not boolean_check.match(show_image):
		show_image = str(input("Error: invalid setting for show_image. Please enter T or F: ")).upper()
		if not show_image:
			show_image = "FALSE"

	if not 'start_flag' in globals():
		start_flag = "TRIALID"
	else:
		start_flag = str(start_flag).upper()

	while not re.match('^TRIALID$|^SYNCTIME$', start_flag):
		start_flag = str(input("Error: invalid setting for start_flag. Please enter one of: TRIALID, SYNCTIME: ")).upper()
		if not start_flag:
			start_flag = "TRIALID"

	if not 'den_sd_cutoff' in globals():
		den_sd_cutoff = "Inf"
	else:
		den_sd_cutoff = str(den_sd_cutoff)

	while not re.match('^Inf$|^-?[0-9]+(\.?[0-9]+)?$', den_sd_cutoff):
		den_sd_cutoff = str(input("Error: invalid setting for den_sd_cutoff. Please enter a number or 'Inf': "))
		if not den_sd_cutoff:
			den_sd_cutoff = "Inf"

	if not 'den_ratio_cutoff' in globals():
		den_ratio_cutoff = "1"
	else:
		den_ratio_cutoff = str(den_ratio_cutoff)

	while not re.match('^Inf$|^-?[0-9]+(\.?[0-9]+)?$', den_ratio_cutoff):
		den_ratio_cutoff = str(input("Error: invalid setting for den_ratio_cutoff. Please enter a number: "))
		if not den_ratio_cutoff:
			den_ratio_cutoff = "1"

	if not 'k_bounds' in globals():
		k_bounds = "c(-.1, .1)"
	else:
		k_bounds = str(k_bounds)

	while not re.match('^c\s*\(\s*-?[0-9]*(\.[0-9]+)?\s*,\s*-?[0-9]*(\.[0-9]+)?\s*\)\s*$', k_bounds):
		k_bounds = str(input("Error: invalid setting for k_bounds. Please enter a 1 x 2 matrix of numbers in the format 'c(x, y)': "))
		if not k_bounds:
			k_bounds = "c(-.1, .1)"

	if not 'o_bounds' in globals():
		o_bounds = "c(-50, 50)"
	else:
		o_bounds = str(o_bounds)

	while not re.match('^c\s*\(\s*-?[0-9]*(\.[0-9]+)?\s*,\s*-?[0-9]*(\.[0-9]+)?\s*\)\s*$', o_bounds):
		o_bounds = str(input("Error: invalid setting for o_bounds. Please enter a 1 x 2 matrix of numbers in the format 'c(x, y)': "))
		if not o_bounds:
			o_bounds = "c(-50, 50)"
	
	if not 's_bounds' in globals():
		s_bounds = "c(1, 20)"
	else:
		s_bounds = str(s_bounds)

	while not re.match('^c\s*\(\s*-?[0-9]*(\.[0-9]+)?\s*,\s*-?[0-9]*(\.[0-9]+)?\s*\)\s*$', s_bounds):
		s_bounds = str(input("Error: invalid setting for s_bounds. Please enter a 1 x 2 matrix of numbers in the format 'c(x, y)': "))
		if not s_bounds:
			s_bounds = "c(1, 20)"

	def strip_quotes(input):
		return re.sub(r'^\'|^"|\'$|"$', '', str(input))

	if not os.path.exists(fa_output_dir):
		os.makedirs(fa_output_dir)

	if not args.refix:
		# Get only the files that we haven't got _fa.asc variants of
		to_align_list = [strip_quotes(str(Path(asc_files_dir) / f)) for f in os.listdir(asc_files_dir) if not re.sub(r'\.asc', '_fa.asc', f) in os.listdir(fa_output_dir) and '.asc' in f and not '_fa.asc' in f]
		if to_align_list:
			asc_files_dir = 'c("' + '", "'.join(to_align_list) + '")'
			start_pts_regex = re.compile('^rbind\s*\(\s*(c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*\))?(\s*,\s*c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*\))?\s*\)$')
			if 'script_loc' and 'start_pts' in globals() and os.path.isfile(script_loc):
				with open(script_loc, "r") as file:
					script = file.read()
					start_pts_param = str(start_pts).replace(" ", "")
					start_pts_stim = "".join(re.findall("start_pts = (.*)", script)).replace(" ", "")
					if not start_pts_regex.match(start_pts_param) and start_pts_regex.match(start_pts_stim):
						print("start_pts in parameter file not correctly formatted. Using start_pts from script file.")
						start_pts = start_pts_stim
					elif not start_pts_regex.match(start_pts_stim) and start_pts_regex.match(start_pts_param):
						print("start_pts from script file not correctly formatted. Using start_pts from parameters file.")
						start_pts = start_pts_param
					elif start_pts_param != start_pts_stim:
						print("Warning: start_pts specified in both parameters file and script file. Using value from parameters file.")
						start_pts = start_pts_param
			elif 'script_loc' in globals() and not 'start_pts' in globals() and os.path.isfile(script_loc):
				with open(script_loc, "r") as file:
					script = file.read()
					start_pts = "".join(re.findall("start_pts = (.*)", script))
					while not start_pts:
						start_pts = input("Error: start_pts matrix not found in script. What is your start_pts matrix? ")
			elif not 'start_pts' in globals():
				while not 'start_pts' in globals():
					start_pts = str(input("Error: start_pts not provided in script file. What is your start_pts matrix? "))

			while not start_pts_regex.match(start_pts):
				start_pts = str(input("Error: start_pts not formatted correctly. start_pts should be of the form 'rbind(c(x, y) [, c(x, y), ...])'. Please enter a valid start_pts matriX: "))
		else:
			asc_files_dir = ""
	else:
		if [f for f in os.listdir(Path(asc_files_dir)) if '.asc' in f and not '_fa.asc' in f]:
			start_pts_regex = re.compile('^rbind\s*\(\s*(c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*\))?(\s*,\s*c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*\))?\s*\)$')
			if 'script_loc' and 'start_pts' in globals() and os.path.isfile(script_loc):
				with open(script_loc, "r") as file:
					script = file.read()
					start_pts_param = str(start_pts).replace(" ", "")
					start_pts_stim = "".join(re.findall("start_pts = (.*)", script)).replace(" ", "")
					if not start_pts_regex.match(start_pts_param) and start_pts_regex.match(start_pts_stim):
						print("start_pts in parameter file not correctly formatted. Using start_pts from script file.")
						start_pts = start_pts_stim
					elif not start_pts_regex.match(start_pts_stim) and start_pts_regex.match(start_pts_param):
						print("start_pts in script file not correctly formatted. Using start_pts from parameters file.")
						start_pts = start_pts_param
					elif start_pts_param != start_pts_stim:
						print("Warning: start_pts specified in both parameters file and script file. Using value from parameters file.")
						start_pts = start_pts_param
			elif 'script_loc' in globals() and not 'start_pts' in globals() and os.path.isfile(script_loc):
				with open(script_loc, "r") as file:
					script = file.read()
					start_pts = "".join(re.findall("start_pts = (.*)", script))
					while not start_pts:
						start_pts = input("Error: start_pts matrix not found in script. What is your start_pts matrix? ")
			elif not 'start_pts' in globals():
				while not 'start_pts' in globals():
					start_pts = str(input("Error: start_pts not provided in script file. What is your start_pts matrix? "))
			
			while not start_pts_regex.match(start_pts):
				start_pts = str(input("Error: start_pts not formatted correctly. start_pts should be of the form 'rbind(c(x, y) [, c(x, y), ...])'. Please enter a valid start_pts matrix: "))

		asc_files_dir = '"' + strip_quotes(str(asc_files_dir)) + '"'

	start_flag = '"' + strip_quotes(start_flag) + '"'

	# If there are ASC files to process, process them
	if strip_quotes(asc_files_dir):
		# Construct the function call
		fa_call = "fix_align(start_pts = " + start_pts + ", " + 'asc_files = ' + asc_files_dir.replace(os.sep, '/') + ', ' + "xy_bounds = " + xy_bounds + ", " + "keep_y_var = " + keep_y_var + ", " + "use_run_rule = " + use_run_rule + ", " + "trial_plots = " + trial_plots + ", " + "save_trial_plots = " + save_trial_plots + ", " + "summary_file = " + summary_file + ", "  +"show_image = " + show_image + ", " + 'fa_dir = "' + strip_quotes(str(fa_output_dir)).replace(os.sep, '/') + '", ' + "start_flag = " + start_flag + ", " +"den_sd_cutoff = " + den_sd_cutoff + ", " + "den_ratio_cutoff = " + den_ratio_cutoff + ", " + "k_bounds = " + k_bounds + ", " + "o_bounds = " + o_bounds + ", " + "s_bounds = " + s_bounds + ")"

		# Write out a temp fix_align file with the function call, run it, and delete it
		fix_align = open(fix_align_loc, "r").read()
		# Fix a problem with directory file name specifications in Windows
		fix_align = re.sub(r"format\((.*)\)\)", "gsub(':', ';', format(\\1)))", fix_align)
		# Make the processing messages shorter
		fix_align = re.sub("print\(paste\('Processing: ', files\[i\], sep=\"\"\)\)", "cat('Processing ', gsub('([A-Z]:\\\\\\\\/|\\\\\\\\/)?(.*\\\\\\\\/)*(.*.asc)', '\\\\\\\\3', files[i]), '...\\n', sep=\"\")", fix_align)
		fix_align_with_call = fix_align + fa_call
		if os.path.isfile("fix_align_tmp.r"):
			try:
				os.remove("fix_align_tmp.r")
			except:
				print("Unable to delete existing fix_align_tmp file. Exiting...")
				sys.exit(1)

		# Get rid of the old summary files if we're refix aliging files. If we're not, then we're only
		# Fix aligning files that don't have existing ones, and we might want to keep the old summary
		if args.refix:
			old_fas = [Path(fa_output_dir) / file for file in os.listdir(Path(fa_output_dir)) if '.fas' in file]
			try:	
				for file in old_fas:
					os.remove(file)
			except:
				print("Unable to delete old fas files.")

		open("fix_align_tmp.r", "a").write(fix_align_with_call)
		print("Processing ASC files with fix_align...")
		try:
			subprocess.check_call("Rscript --vanilla fix_align_tmp.r", shell = True)
		except:
			print("Error: fix_align terminated unexpectedly. Exiting...")
			try:
				os.remove("fix_align_tmp.r")
			except:
				print("Unable to delete fix_align_tmp file.")
				sys.exit(1)

		try:
			os.remove("fix_align_tmp.r")
		except:
			print("Unable to delete fix_align_tmp file. Make sure to delete manually before running this script again.")
	else:
		# There aren't any asc files to process, so print a message to that effect
		#if [Path(old_asc_files_dir) / file for file in os.listdir(Path(old_asc_files_dir)) if '.asc' in file]:
		print("All ASC files have existing fix aligned versions. Skipping fix_align. Use '--refix' ('-r') to re-fix align ASCs.")
	
	file_list = os.listdir(fa_output_dir)
	file_list = [str(Path(fa_output_dir) / f) for f in file_list if '_fa.asc' in f]
else:
	fa_output_dir = asc_files_dir
	file_list = os.listdir(fa_output_dir)
	file_list = [str(Path(fa_output_dir) / f) for f in file_list if '.asc' in f]

# Sentences
if not args.nosentences:
	if os.path.isfile(csv_loc) and not args.overwrite:
		print("Error: results.csv already exists in " + str(output_dir) + ". Use '--overwrite' ('-o') to overwrite existing results.csv files. Not processing ASC files with SideEye.")
	else:
		sideEyeConfig = sideeye.config.Configuration(str(config_json_loc))

		print("Processing ASC files with SideEye (this may take a while)...")

		asc_files = sideeye.parser.experiment.parse_files(file_list, str(sentences_txt_loc), sideEyeConfig)

		sideeye.calculate_all_measures(asc_files, csv_loc, sideEyeConfig)

# Get correct names for columns to use when joining results from the settings in the config file
if not args.noquestions or not args.nocombine:
	with open(Path(config_json_loc), "r") as file:
		config_txt = file.read()
		filename_col_name = re.findall(r'"trial_output"[\s\S]*?"filename"[\s\S]*?"header":\s*"(.*)"', config_txt)[0]
		item_id_col_name = re.findall(r'"trial_output"[\s\S]*?"item_id"[\s\S]*?"header":\s*"(.*)"', config_txt)[0]
		item_condition_col_name = re.findall(r'"trial_output"[\s\S]*?"item_condition"[\s\S]*?"header":\s*"(.*)"', config_txt)[0]

# Questions
if not args.noquestions:
	subj_quest_file_name = output_dir / 'subject_question_info.txt'
	summary_file_name = output_dir / 'question_summary.txt'

	if (os.path.isfile(Path(subj_quest_file_name)) or os.path.isfile(Path(summary_file_name))) and not args.overwrite:
		if os.path.isfile(Path(subj_quest_file_name)) and os.path.isfile(Path(summary_file_name)):
			print("Error: " + subj_quest_file_name.name + " and " + summary_file_name.name + " already exist in " + str(output_dir) + ". Use '--overwrite' ('-o') to overwrite existing files. Not creating question summaries.")
		elif os.path.isfile(Path(subj_quest_file_name)):
			print("Error: " + subj_quest_file_name.name + " already exists in " + str(output_dir) + ". Use '--overwrite' ('-o') to overwrite existing files. Not creating question summaries.")
		elif os.path.isfile(Path(summary_file_name)):
			print("Error: " + summary_file_name.name + " already exists in " + str(output_dir) + ". Use '--overwrite' (-'o') to overwrite existing files. Not creating question summaries.")
	else:
		print("Creating question summaries...")

		subj_sum = []
		subj_quest_file = open(subj_quest_file_name, 'w')
		subj_quest_file.write(filename_col_name + " question_type " + item_id_col_name + " correct_answer response was_response_correct response_RT\n")
		summary_file = open(summary_file_name,'w')
		summary_file.write(filename_col_name + ' s_number_questions s_num_correct_answers s_total_prop_correct\n')

		for file in file_list:

			try:
				filename = open(file, 'r')
			except:
				print("File %s could not be found." %file)
				sys.exit(1)

			if args.verbose:
				print(file)
				
			search_strings = [strip_quotes(start_flag), 'QUESTION_ANSWER', 'TRIAL_RESULT']
			temp_quest_file = open('temp_quest_file','w+')
			for line in filename:
				for entry in search_strings:
					if entry in line:
						temp_quest_file.write(line)
						
			temp_quest_file.seek(0,0)
			qcount = 0		# count of questions
			acount = 0		# count of accurate answers
			for line in temp_quest_file:
				if search_strings[0] in line:
					correct = 'none'
				
					fields = line.split()
					start_time = int(fields[1])
					trialid = fields[3]
					first_split = trialid.split('I')#split into the condition, and then item and dependent
					condition = first_split[0]
					cond_num = condition[1:] #strip off the letter from the beginning of condition
					second_split = first_split[1].split('D')#split into item and dependent
					item_num = second_split[0]
				
				elif search_strings[1] in line:
					fields = line.split()
					correct = fields[3]
					
				else:
					fields = line.split()
					end_time = int(fields[1])
					answer = fields[3]
					
					#write out line, if the item had a question
					if correct != 'none':
						qcount = qcount + 1
						was_response_correct = "FALSE"
						if correct == answer:
							was_response_correct = "TRUE"
							acount = acount + 1
						output_line = ['"' + file + '"', cond_num, item_num, correct, answer, was_response_correct, str(end_time - start_time)]
						subj_quest_file.write(' '.join(output_line))
						subj_quest_file.write('\n')

			temp_quest_file.close()

			if args.verbose:
				print(file,qcount,acount,float(acount/qcount))

			subj_sum = ['"' + file + '"', str(qcount), str(acount),str(float(acount/qcount))]
			subj_sum_join = ' '.join(subj_sum)
			summary_file.write(subj_sum_join)
			summary_file.write('\n')

		try:
			os.remove('temp_quest_file')
		except:
			print("Unable to delete temp_quest_file. Continuing...")

		subj_quest_file.close()
		summary_file.close()

# Combine
if not args.nocombine:
	if os.path.isfile(Path(output_dir) / 'results_combined.csv') and not args.overwrite:
		print("Error: results-combined.csv already exists in " +  str(output_dir) + ". Use '--overwrite' ('-o') to overwrite existing results-combined.csv files. Not combining results.")
	else:
		if args.noquestions and not args.nosentences:
			print("Combining pre-existing question files. Assuming column names as specified in " + config_json_loc.name + ", and filenames 'subj_question_info.txt', 'question_summary.txt'. Assuming files are located in " + str(output_dir) + ".")
		elif args.nosentences and not args.noquestions:
			print("Combining pre-existing results. Assuming column names as specified in " + config_json_loc.name + ", and filename 'results.csv'. Assuming results file is located in " + str(output_dir) + '.')
		elif args.nosentences and args.noquestions:
			print("Combining pre-existing results. Assuming column names as specified in " + config_json_loc.name + ", and filenames 'subj_question_info.txt', 'question_summary.txt', 'results.csv'. Assuming files are located in " + str(output_dir) + '.')


		if (not os.path.isfile(subj_quest_file_name) and 
			not os.path.isfile(summary_file_name) and 
			not os.path.isfile(csv_loc)):
			print("No results found to combine. Exiting...")
			sys.exit(1)

		print("Combining results...")
		# Check if the columns we need to conjoin the output are included in the output, and if not, exit
		is_item_id_included = re.findall(r'"region_output"[\s\S]*?"item_id"[\s\S]*?"exclude":\s*"(.*)"', config_txt) == "false"  or len(re.findall(r'"region_output[\s\S]*?"item_id"[\s\S]*?"exclude":\s*"(.*)"', config_txt)) == 0
		if not is_item_id_included:
			print("item_id not included in results. Cannot combine results.")
			sys.exit(1)

		is_filename_included = re.findall(r'"region_output"[\s\S]*?"filename"[\s\S]*?"exclude":\s*"(.*)"', config_txt) == "false" or len(re.findall(r'"region_output[\s\S]*?"filename"[\s\S]*?"exclude":\s*"(.*)"', config_txt)) == 0

		is_item_condition_included = re.findall(r'"region_output[\s\S]*?"item_condition"[\s\S]*?"exclude":\s*"(.*)"', config_txt) == "false" or len(re.findall(r'"region_output[\s\S]*?"item_condition"[\s\S]*?"exclude":\s*"(.*)"', config_txt)) == 0

		# Set variables corresponding to whether any results were combined to false
		combined_s_subj_quest = False
		combined_s_questsum = False
		combined_s_stimuli = False
		combined_q_stimuli = False
		combined_q_questsum = False

		# If we have sentences
		if os.path.isfile(csv_loc):
			results = pandas.read_csv(csv_loc, encoding = file_encoding)

			# If we have questions and we have the right column to join them on
			if os.path.isfile(subj_quest_file_name) and os.path.isfile(summary_file_name) and is_filename_included:
				questions = pandas.read_csv(subj_quest_file_name, sep = " ", encoding = file_encoding)
				questions = questions[questions['question_type'] != 1]
				subj_questions = pandas.read_csv(summary_file_name, sep = " ", encoding = file_encoding)
				questions = pandas.merge(questions, subj_questions, how = 'right')
				results = pandas.merge(results, questions, how = 'left')
				combined_s_subj_quest = True
				combined_s_questsum = True
			elif os.path.isfile(summary_file_name) and is_filename_included:
				questions = pandas.read_csv(summary_file_name, sep = " ", encoding = file_encoding)
				results = pandas.merge(results, questions, how = 'right')
				combined_s_questsum = True
			elif not is_filename_included:
				print("filename not included in results. Cannot combine results and questions.")
			# If we have stimuli and the right column to join them on (add checks for blank values or incorrect values)
			if os.path.isfile(stimuli_loc) and is_item_condition_included:
				stimuli = pandas.read_csv(stimuli_loc, encoding = file_encoding)

				# If the columns exist, check whether to rename them
				if not 'item_id' in stimuli.columns and not item_id_col_name in stimuli.columns:
					print("item_id not included in stimuli. Cannot combine results and stimuli.")
				elif not item_id_col_name in stimuli.columns:
					stimuli.rename(columns = {'item_id': item_id_col_name }, inplace = True)

				if not 'item_condition' in stimuli.columns and not item_condition_col_name in stimuli.columns:
					print("item_condition not included in stimuli. Cannot combine results and stimuli.")
				elif not item_condition_col_name in stimuli.columns:
					stimuli.rename(columns = {'item_condition': item_condition_col_name}, inplace = True)

				# Check that the columns needed exist and are formatted correctly
				if item_id_col_name in stimuli.columns and item_condition_col_name in stimuli.columns:
					if (stimuli[item_id_col_name].isnull().any() or 
						stimuli[item_id_col_name].apply(lambda x: bool(re.match('^$', str(x)))).any() or
						not stimuli[item_id_col_name].apply(lambda x: bool(re.match(r'^[0-9]*$', str(x)))).all() or
						not set(x for x in set(results[item_id_col_name].unique().tolist()) if pandas.notna(x)).issubset(stimuli[item_id_col_name].unique().tolist())):
						print("Error: stimuli file has improperly specified item ids. Not combining stimuli with results.")
					elif (stimuli[item_condition_col_name].isnull().any() or
						stimuli[item_condition_col_name].apply(lambda x: bool(re.match('^$', str(x)))).any() or 
						not stimuli[item_condition_col_name].apply(lambda x: bool(re.match(r'^[0-9]*$', str(x)))).all() or
						not set(x for x in set(results[item_condition_col_name].unique().tolist()) if pandas.notna(x)).issubset(stimuli[item_condition_col_name].unique().tolist())):
						print("Error: stimuli file has improperly specified item conditions. Not combining stimuli with results.")
					else:
						results = pandas.merge(results, stimuli, how = 'left')
						combined_s_stimuli = True

			elif not is_item_condition_included:
				print("item_condition not included in results. Cannot combine results with stimuli.")
		# If we have questions (but no sentences)		
		elif os.path.isfile(subj_quest_file_name):
			results = pandas.read_csv(subj_quest_file_name, sep = " ", encoding = file_encoding)
			results = results[results['question_type'] != 1]

			if os.path.isfile(summary_file_name):
				subj_questions = pandas.read_csv(summary_file_name, sep = " ", encoding = file_encoding)
				results = pandas.merge(results, subj_questions, how = 'right')
				combined_q_questsum = True

			# If we have stimuli (add checks for blank values or incorrect values)
			if os.path.isfile(stimuli_loc):
				stimuli = pandas.read_csv(stimuli_loc, encoding = file_encoding)

				# If the columns exist, check whether to rename them
				if not 'item_id' in stimuli.columns and not item_id_col_name in stimuli.columns:
					print('item_id not included in stimuli. Cannot combine results and stimuli.')
				elif not item_id_col_name in stimuli.columns:
					stimuli.rename(columns = {'item_id': item_id_col_name }, inplace = True)

				if item_id_col_name in stimuli.columns:
					if (stimuli[item_id_col_name].isnull().any() or 
						stimuli[item_id_col_name].apply(lambda x: bool(re.match('^$', str(x)))).any() or
						not stimuli[item_id_col_name].apply(lambda x: bool(re.match(r'^[0-9]*$', str(x)))).all() or
						not set(x for x in set(results[item_id_col_name].unique().tolist()) if pandas.notna(x)).issubset(stimuli[item_id_col_name].unique().tolist())):
						print("Error: stimuli file has improperly specified item ids. Not combining stimuli with results.")
					else:
						results = pandas.merge(results, stimuli, how = 'left')
						combined_q_stimuli = True

		# If any combining happened
		if combined_s_subj_quest or combined_s_questsum or combined_s_stimuli or combined_q_stimuli or combined_q_questsum:
			# Write out the combined results
			print("Writing out combined output...")
			results.to_csv(Path(output_dir) / 'results_combined.csv', index = False, na_rep = 'NA')
			# Then delete the appropriate files if we're not keeping them
			if not args.keepall:
				# If we combined the sentences into the results, delete them
				if combined_s_subj_quest or combined_s_questsum or combined_s_stimuli:
					try:
						os.remove(csv_loc)
					except:
						print("Unable to delete non-combined results file.")

				# If we combined the questions into the results, delete them
				if combined_s_subj_quest or combined_q_stimuli:
					try:
						os.remove(subj_quest_file_name)
					except:
						print("Unable to delete non-combined questions file.")

				if combined_s_questsum or combined_q_questsum:
					try:
						os.remove(summary_file_name)
					except:
						print("Unable to delete non-combined questions summary file.")

print("Completed successfully!")
sys.exit(0)