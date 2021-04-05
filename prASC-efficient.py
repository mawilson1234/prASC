##############################################################################################
##### Master script prASC.py for processing ASCs to R-ready data frame by Michael Wilson #####
########### Based on Preprocessing_FromASCs.py and question_acc.py by Brian Dillon ###########
########################### Calls fix_align by Andrew Cohen (2013) ###########################
##############################################################################################

import os, re, sys, subprocess, argparse
from pathlib import Path

# Define the arguments and parse them
parser = argparse.ArgumentParser()
parser.add_argument('filename', nargs = '?', default = Path(os.path.dirname(os.path.realpath(__file__))) / "parameters.py", 
	help = "Optional argument to provide the parameter file. Default assumes filename 'parameters.py' in the executing directory.")
parser.add_argument('-o', '--overwrite', default = False, action = 'store_true', 
	help = "Optional argument to specify whether to overwrite existing results.")
parser.add_argument('-k', '--keepall', default = False, action = 'store_true', 
	help = "Optional argument to keep non-combined results files.")
parser.add_argument('-rf', '--refix', default = False, action = 'store_true', 
	help = "Optional argument to re-fix align ASCs that have existing fix aligned versions.")
parser.add_argument('-nf', '--nofix', default = False, action = "store_true", 
	help = "Optional argument to not fix align ASCs. When this is set, further analysis will use ASCs in the ASC directory specified in parameters.py, which can lead to missing data if they have not been previously cleaned. To use pre-existing fix aligned ASCs, set fa_output_dir to the directory containing them, and do not use the '--refix' option.")
parser.add_argument('-rs', '--resentences', default = False, action = 'store_true',
	help = "Optional argument to reprocess all sentence data using SideEye.")
parser.add_argument('-ns', '--nosentences', default = False, action = "store_true", 
	help = "Optional argument to not process sentence information using SideEye.")
parser.add_argument('-v', '--verbose', default = False, action="store_true", 
	help = "Optional argument to print information about question accuracy to the console.")
parser.add_argument('-rq', '--requestions', default = False, action = "store_true",
	help = "Optional argument to reprocess all question data.")
parser.add_argument('-nq', '--noquestions', default = False, action = "store_true", 
	help = "Optional argument to not process question information from ASCs.")
parser.add_argument('-nc', '--nocombine', default = False, action = "store_true", 
	help = "Optional argument to not combine results files. If this is set, keepall will automatically be set.")
parser.add_argument('-re', '--reeverything', default = False, action = "store_true",
	help = "Convenient argument to set all of --refix, --resentences, and --requestions at once, reprocessing the entire set of results.")

args = parser.parse_args()
if args.filename:
	parameters_loc = args.filename
else:	
	parameters_loc = Path(os.path.dirname(os.path.realpath(__file__))) / "parameters.py"

if args.reeverything:
	args.refix = True
	args.resentences = True
	args.requestions = True

# Deal with odd combinations of arguments and print appropriate warning/error messages
if args.nofix and args.nosentences and args.noquestions and args.nocombine:
	print("Nothing to do with all of nofix, nosentences, noquestions, and nocombine set. Exiting.")
	sys.exit(0)

# Safest thing is to do nothing
if args.refix and args.nofix:
	print("Warning: refix and nofix cannot both be set. nofix will be respected.")
	args.refix = False

if args.resentences and args.nosentences:
	print("Error: can't do both resentences and nosentences. nosentences will be respected.")
	args.resentences = False

if args.noquestions and args.requestions:
	print("Error: can't do both args.requestions and args.noquestions. args.noquestions will be respected.")
	args.requestions = False

# If we're not combining results, then make sure to keep them
if args.nocombine:
	args.keepall = True

# If we are combining results without attempting to fix align them, we might lose data. Print a warning in this case
if not args.nocombine and args.nofix:
	print("Warning: combining results without fix aligning ASCs. If your ASCs have not been previously corrected, this can lead to errors due to missing data.")

# We need pandas if we're doing these things, but not otherwise
if not args.resentences or not args.requestions or not args.nocombine:
	import pandas

# Read in the parameters file and set default values
with Path(os.path.dirname(os.path.realpath(__file__))) as current_dir:
	# Read in and execute the parameters file
	while True:
		try:
			# Add the file extension if it's not provided by the user
			if not re.match('.*\.py$', str(parameters_loc)):
				parameters_loc = Path(str(parameters_loc) + '.py')

			# Read in and execute the parameters file, then break
			parameters = open(parameters_loc,'r')
			whole_file = parameters.read()
			exec(whole_file)
			break
		except Exception:
			# If we can't find the parameters file, try again
			parameters_loc = Path(input("Error: no parameters file found. Please specify a parameters file location: "))
			if not re.match('.*\.py$', str(parameters_loc)):
				parameters_loc = Path(str(parameters_loc) + '.py')

	# If there is no asc_files_dir specified in the parameters file, assume it's in the current directory. If the directory does not contain ASC files, prompt for one until we get one that does
	while True:
		if not 'asc_files_dir' in globals():
			asc_files_dir = current_dir / "ASC"
		elif not asc_files_dir:
			asc_files_dir = current_dir / "ASC"

		# If we need the ASC files and it been set to an empty string, assume it's the current directory
		if not args.nofix or not args.nosentences or not args.noquestions:
			try:
				if len([f for f in os.listdir(asc_files_dir) if '.asc' in f]) == 0:
					asc_files_dir = Path(input(f"Error: no ASC files found in '{asc_files_dir}'. If your ASC files have already been fix aligned, set the asc_files_dir to the location of your fix aligned files, and use the '--nofix' ('-nf') option. Please enter a directory containing ASC files: "))
					if not asc_files_dir:
						asc_files_dir = current_dir / "ASC"
				else:
					break
			except Exception:
				asc_files_dir = Path(input(f"Error: no ASC files found in '{asc_files_dir}'. If your ASC files have already been fix aligned, set the asc_files_dir to the location of your fix aligned files, and use the '--nofix' ('-nf') option. Please enter a directory containing ASC files: "))
				if not asc_files_dir:
					asc_files_dir = current_dir / "ASC"

			asc_files_dir = Path(asc_files_dir)
		else:
			break

	# If we're generating output, get the output directory and create it if it doesn't exist
	if not args.nosentences or not args.noquestions or not args.nocombine:
		if not 'output_dir' in globals():
			output_dir = Path(current_dir) / "prASCed results"
		else:
			output_dir = Path(output_dir)
		
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

		output_dir = Path(output_dir)

	# If we're combining results, the results file already exists, and we're not overwriting, exit
	if not args.nocombine and os.path.isfile(output_dir / 'results_combined.csv') and not args.overwrite:
		print("Error: results_combined.csv already exists in " + str(output_dir) + ". Use '--overwrite' ('-o') to overwrite existing results_combined.csv files. Exiting.")
		sys.exit(1)

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

	# Stimuli loc is optional, but print a warning if we're not using it
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
		if os.path.isfile(csv_loc) and not args.overwrite:
			print("Error: results.csv already exists in " + str(output_dir) + ". Use '--overwrite' ('-o') to overwrite existing results files. Exiting.")
			sys.exit(1)

	if not args.noquestions or not args.nocombine:
		# Set up the question file locations
		subj_quest_file_name = output_dir / 'subject_question_info.txt'
		summary_file_name = output_dir / 'question_summary.txt'
		if (os.path.isfile(subj_quest_file_name) or os.path.isfile(summary_file_name)) and not args.overwrite:
			print("Error: question results file(s) already exist in " + output_dir + ". Use '--overwrite' ('-o') to overwrite existing results files. Exiting.")
			sys.exit(1)

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
			start_pts_regex = re.compile('^rbind\s*\(\s*(c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*\)){1}(\s*,\s*c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*\))*\s*\)$')
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
			start_pts_regex = re.compile('^rbind\s*\(\s*(c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*\)){1}(\s*,\s*c\s*\(\s*[0-9]+\s*,\s*[0-9]+\s*\))*\s*\)$')
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
			except Exception:
				print("Unable to delete existing fix_align_tmp file. Exiting.")
				sys.exit(1)

		# Get rid of the old summary files if we're refix aliging files. If we're not, then we're only fix aligning files that don't have existing ones, and we might want to keep the old summary
		if args.refix:
			old_fas = [Path(fa_output_dir) / file for file in os.listdir(Path(fa_output_dir)) if '.fas' in file]
			try:	
				for file in old_fas:
					os.remove(file)
			except Exception:
				print("Unable to delete old fas files.")

		open("fix_align_tmp.r", "a").write(fix_align_with_call)
		print("Processing ASC files with fix_align...")
		try:
			subprocess.check_call("Rscript --vanilla fix_align_tmp.r", shell = True)
		except Exception:
			print("Error: fix_align terminated unexpectedly. Exiting.")
			try:
				os.remove("fix_align_tmp.r")
			except Exception:
				print("Unable to delete fix_align_tmp file.")
				sys.exit(1)

		try:
			os.remove("fix_align_tmp.r")
		except Exception:
			print("Unable to delete fix_align_tmp file. Make sure to delete manually before running this script again.")
	else:
		# There aren't any asc files to process, so print a message to that effect
		print("All ASC files have existing fix aligned versions. Skipping fix_align. Use '--refix' ('-rf') to re-fix align ASCs.")
	
	file_list = os.listdir(fa_output_dir)
	file_list = [str(Path(fa_output_dir) / f) for f in file_list if '_fa.asc' in f]
# If we're not fix aligning files, set the ASC files directory as the fa directory so the later processing steps will look there for files
else:
	fa_output_dir = asc_files_dir
	file_list = os.listdir(fa_output_dir)
	file_list = [str(Path(fa_output_dir) / f) for f in file_list if '.asc' in f]

# Get correct names for columns to use when not reprocessing all data
if not args.resentences or not args.requestions or not args.noquestions or not args.nocombine:
	import json

	with open(Path(config_json_loc), "r") as file:
		config = json.load(file)

	# Filter to the trial output that's included according to the config file
	trial_output = []
	if 'trial_output' in config:
		trial_output = config['trial_output']

	trial_output_excluded = [column for column in trial_output if 'exclude' in trial_output[column] and trial_output[column]['exclude'] == True]
	trial_output_included = trial_output

	for column in trial_output_excluded:
		del trial_output_included[column]

	# Filter to the region output that's included according to the config file
	region_output = []
	if 'region_output' in config:
		region_output = config['region_output']

	region_output_excluded = [column for column in region_output if 'exclude' in region_output[column] and region_output[column]['exclude'] == True]
	region_output_included = region_output

	for column in region_output_excluded:
		del region_output_included[column]

	# Get a list of column names. Choose trial_output over region_output if both are included
	included_column_names = []
	for column in region_output_included:
		if column in trial_output_included:
			included_column_names.append(trial_output_included[column]['header'])
		else:
			included_column_names.append(region_output_included[column]['header'])

	for column in trial_output_included:
		if trial_output_included[column]['header'] not in included_column_names:
			included_column_names.append(trial_output_included[column]['header'])

	# If sideeye is outputting in wide format
	if config['wide_format'] == True:

		# Figure out the trial measures included
		trial_measures = []

		if 'trial_measures' in config:
			trial_measures = config['trial_measures']
			trial_measures_excluded = [column for column in trial_measures if 'exclude' in trial_measures[column] and trial_measures[column]['exclude'] == True]

		trial_measures_included = trial_measures

		for column in trial_measures_excluded:
			del trial_measures_included[column]

		# Figure out the region measures included
		region_measures = []

		if 'region_measures' in config:
			region_measures = config['region_measures']
			region_measures_excluded = [column for column in region_measures if 'exclude' in region_measures[column] and region_measures[column]['exclude'] == True]

		region_measures_included = region_measures

		for column in region_measures_excluded:
			del region_measures_included[column]

		# Add the included fields to the included_column_names
		for column in region_measures_included:
			included_column_names.append(column)

		for column in trial_measures_included:
			if column not in included_column_names:
				included_column_names.append(column)

	# Get variables corresponding to the filename, item_id, and item_condition column names, since we'll use those to join the results. That way we can rename the stimuli columns if the configuration file gives different ones to the sentences CSV
	if 'filename' in trial_output_included:
		filename_col_name = trial_output_included['filename']['header']
	elif 'filename' in region_output_included:
		filename_col_name = region_output_included['filename']['header']
	else:
		filename_col_name = 'filename'

	if 'item_id' in trial_output_included:
		item_id_col_name = trial_output_included['item_id']['header']
	elif 'item_id' in region_output_included:
		item_id_col_name = region_output_included['item_id']['header']
	else:
		item_id_col_name = 'item_id'

	if 'item_condition' in trial_output_included:
		item_condition_col_name = trial_output_included['item_condition']['header']
	elif 'item_condition' in region_output_included:
		item_condition_col_name = region_output_included['item_condition_col_name']['header']
	else:
		item_condition_col_name = 'item_condition'

	is_item_id_included = 'item_id' in trial_output_included or 'item_id' in region_output_included
	is_filename_included = 'filename' in trial_output_included or 'filename' in region_output_included
	is_item_condition_included = 'item_condition' in trial_output_included or 'item_condition' in region_output_included

# Sentences
if not args.nosentences:

	# The base case is to do everything in the file_list
	sentences_file_list = file_list

	# If we're not reprocessing all of the sentences, filter the file list to just those not in the results file
	if not args.resentences:
		# Pre-compile a regex so we can compare the filenames without the directories added
		undir = re.compile(r'(^[A-Z]:)?(\/|\\)?.*(\/|\\)(.*\.asc$)')
		s_existing_results = pandas.DataFrame(columns = [""])
		s_already_processed = []

		# Look in the base results.csv, since we'll recreate it even if it doesn't exist
		try:
			s_existing_results = pandas.read_csv(csv_loc, encoding = file_encoding)
			#os.remove(csv_loc)
		except OSError:
			try:
				s_existing_results = pandas.read_csv(output_dir / 'results_combined.csv', encoding = file_encoding, low_memory = False)
			except OSError:
				print("Unable to find existing sentence results. All sentences will be processed.")

		# If we found existing results
		if not s_existing_results.empty and is_filename_included:
			s_existing_results = pandas.DataFrame(s_existing_results)
			s_existing_results = s_existing_results[included_column_names]
			s_already_processed = s_existing_results[filename_col_name].unique().tolist()
			s_already_processed = [undir.sub('\\4', subj) for subj in s_already_processed]
		elif not is_filename_included:
			print("filename column not found in existing results file(s). All sentences will be processed.")

		sentences_file_list = [file for file in file_list if undir.sub('\\4', file) not in s_already_processed]

	if sentences_file_list:
		import sideeye
		print("Processing sentences with SideEye (this may take a while)...")
		sideEyeConfig = sideeye.config.Configuration(str(config_json_loc))
		asc_files = sideeye.parser.experiment.parse_files(sentences_file_list, str(sentences_txt_loc), sideEyeConfig)
		sideeye.calculate_all_measures(asc_files, csv_loc, sideEyeConfig)
	else:
		print("All sentences have already been processed with SideEye. Skipping SideEye. Use '--resentences' ('-rs') to reprocess sentences with SideEye.")

	# If the sentences file list isn't the full file list and the partial results file already exists, join the existing results to the results we just put out. Checking whether the file exists is in case we didn't use overwrite and skipped writing it out
	if not args.resentences and s_already_processed and not all(file in s_already_processed for file in [undir.sub('\\4', f) for f in file_list]) and os.path.isfile(csv_loc):
		new_results = pandas.read_csv(csv_loc, encoding = file_encoding)
		#os.remove(csv_loc)
		new_results = pandas.DataFrame(new_results)
		added_results = s_existing_results.append(new_results)
		added_results.to_csv(csv_loc, index = False, na_rep = 'NA')
	# If we're keeping all the intermediate results, even if we didn't process anything, we can still regenerate the intermediate file
	elif not args.resentences and not s_existing_results.empty and args.keepall:
		s_existing_results.to_csv(csv_loc, index = False, na_rep = 'NA')

# Questions
if not args.noquestions:
	# Default is do everything in the file list
	questions_file_list = file_list

	# If we're not redoing all of the questions, filter the file list to just those not in the results files
	if not args.requestions:

		# Pre-compile a regex so we can compare the filenames without the directories added
		undir = re.compile(r'(^[A-Z]:)?(\/|\\)?.*(\/|\\)(.*\.asc$)')

		# These first two are needed if we're reading in the two separate files
		existing_subj_quest = pandas.DataFrame(columns = [''])
		existing_summary_file = pandas.DataFrame(columns = [''])

		# This is used if we are reading in the combined results file
		q_existing_results = pandas.DataFrame(columns = [''])

		# This is to store the list of already processed subjects
		q_already_processed = []

		# If both questions files already exist, pull from the one with the least number of subjects
		try:
			# Read in the existing files and delete them to overwrite later
			existing_subj_quest = pandas.read_csv(subj_quest_file_name, encoding = file_encoding, sep = " ")
			#os.remove(subj_quest_file_name)
			existing_summary_file = pandas.read_csv(summary_file_name, encoding = file_encoding, sep = " ")
			#os.remove(summary_file_name)

			# Get the list of subjects from each
			existing_subj_quest_subjs = pandas.DataFrame(existing_subj_quest)
			existing_summary_file_subjs = pandas.DataFrame(existing_summary_file)
			existing_subj_quest_subjs = existing_subj_quest[filename_col_name].unique().tolist()
			existing_summary_file_subjs = existing_summary_file[filename_col_name].unique().tolist()

			# Get the subjects in common between the two files, and put them in the file_list
			q_already_processed = list(set(existing_subj_quest_subjs) & set(existing_summary_file_subjs))
			q_already_processed = [undir.sub('\\4', subj) for subj in q_already_processed]

			# Retain only the subjects in common between the two for later
			# We have to do this carefully so we don't actually overwrite the column text with the undirectorified version
			#existing_subj_quest = existing_subj_quest[filename_col_name].isin([subj for subj in existing_subj_quest[filename_col_name].unique().tolist() if undir.sub('\\4', subj) in q_already_processed])
			#existing_summary_file = existing_summary_file[filename_col_name].isin([subj for subj in existing_summary_file[filename_col_name].unique().tolist() if undir.sub('\\4', subj) in q_already_processed])
			# Get all the rows of existing_subj_quest and existing_summary_file for which the filename of that row is in the list of unique subjects already processed, once we strip off the directory information
			existing_subj_quest = existing_subj_quest[existing_subj_quest[filename_col_name].isin([subj for subj in existing_subj_quest[filename_col_name].unique().tolist() if undir.sub('\\4', subj) in q_already_processed])]
			existing_summary_file = existing_summary_file[existing_summary_file[filename_col_name].isin([subj for subj in existing_summary_file[filename_col_name].unique().tolist() if undir.sub('\\4', subj) in q_already_processed])]
		except Exception:
			if os.path.isfile(output_dir / 'results_combined.csv') and is_filename_included:
				q_existing_results = pandas.read_csv(output_dir / 'results_combined.csv', encoding = file_encoding, low_memory = False)
				q_existing_results = pandas.DataFrame(q_existing_results)
				q_already_processed = q_existing_results[filename_col_name].unique().tolist()
				q_already_processed = [undir.sub('\\4', subj) for subj in q_already_processed]
			elif not is_filename_included:
				print("filename not included in existing results file(s). All questions will be processed.")
			else:
				print("Unable to find existing question results. All questions will be processed.")

		questions_file_list = [file for file in file_list if undir.sub('\\4', file) not in q_already_processed]

	if questions_file_list:

		print("Creating question summaries...")

		subj_sum = []
		subj_quest_file = open(subj_quest_file_name, 'w+')
		subj_quest_file.write(filename_col_name + " question_type " + item_id_col_name + " correct_answer response was_response_correct response_RT\n")
		summary_file = open(summary_file_name,'w+')
		summary_file.write(filename_col_name + ' s_number_questions s_num_correct_answers s_total_prop_correct\n')	

		#Testing
		for file in questions_file_list:

			try:
				filename = open(file, 'r')
			except Exception:
				print("File %s could not be found." %file)
				sys.exit(1)

			if args.verbose:
				print(file)
					
			search_strings = [strip_quotes(start_flag), 'QUESTION_ANSWER', 'TRIAL_RESULT']
			temp_quest_file = open(output_dir / 'temp_quest_file','w+')
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
			os.remove(output_dir / 'temp_quest_file')
		except Exception:
			print("Unable to delete temp_quest_file. Continuing...")

		subj_quest_file.close()
		summary_file.close()
	else:
		print("All questions have already been processed. Skipping questions. Use '--requestions' ('-rq') to reprocess questions.")

	# If we only processed a subset of the questions. Check whether the file exists in case we skipped writing it due to overwrite not be set
	if not args.requestions and q_already_processed and not all(file in q_already_processed for file in [undir.sub('\\4', f) for f in file_list]) and os.path.isfile(subj_quest_file_name) and os.path.isfile(summary_file_name):
		# Read in the new results to combine
		new_subj_quest_results = pandas.read_csv(subj_quest_file_name, encoding = file_encoding, sep = " ")
		new_subj_quest_results = pandas.DataFrame(new_subj_quest_results)
		
		new_question_summary_results = pandas.read_csv(summary_file_name, encoding = file_encoding, sep = " ")
		new_question_summary_results = pandas.DataFrame(new_question_summary_results)

		# If we got the old results from the question txt files
		if not existing_subj_quest.empty and not existing_summary_file.empty:
			# Append the new files we just wrote out to the existing results
			added_subj_quest_results = existing_subj_quest.append(new_subj_quest_results)
			added_subj_quest_results.to_csv(subj_quest_file_name, index = False, sep = ' ', mode = 'w+')

			added_question_summary_results = existing_summary_file.append(new_question_summary_results)
			added_question_summary_results.to_csv(summary_file_name, index = False, sep = ' ', mode = 'w+')
		# Otherwise, we got the existing results from the results_combined file
		elif not q_existing_results.empty:

			# We need to recreate the question files that went into the combined results file
			existing_subj_quest = q_existing_results[[filename_col_name, 'question_type', item_id_col_name, 'correct_answer', 'response', 'was_response_correct', 'response_RT']].drop_duplicates().reset_index(drop = True)
			added_subj_quest_results = existing_subj_quest.append(new_subj_quest_results)
			added_subj_quest_results.to_csv(subj_quest_file_name, index = False, sep = ' ', mode = 'w+', na_rep = "NA")

			existing_summary_file = q_existing_results[[filename_col_name, 's_number_questions', 's_num_correct_answers', 's_total_prop_correct']].drop_duplicates().reset_index(drop = True)
			added_question_summary_results = existing_summary_file.append(new_question_summary_results)
			added_question_summary_results.to_csv(summary_file_name, index = False, sep = ' ', mode = 'w+', na_rep = "NA")
	elif not args.requestions and not q_existing_results.empty:
		if not os.path.isfile(subj_quest_file_name):
			existing_subj_quest = q_existing_results[[filename_col_name, 'question_type', item_id_col_name, 'correct_answer', 'response', 'was_response_correct', 'response_RT']].drop_duplicates().reset_index(drop = True)
			existing_subj_quest.to_csv(subj_quest_file_name, index = False, sep = ' ', mode = 'w+', na_rep = "NA")

		if not os.path.isfile(summary_file_name):
			existing_summary_file = q_existing_results[[filename_col_name, 's_number_questions', 's_num_correct_answers', 's_total_prop_correct']].drop_duplicates().reset_index(drop = True)
			existing_summary_file.to_csv(summary_file_name, index = False, sep = ' ', mode = 'w+', na_rep = "NA")

# Combine
if not args.nocombine:
	if args.noquestions and not args.nosentences:
		print("Combining pre-existing question files. Assuming column names as specified in " + config_json_loc.name + ", and filenames 'subj_question_info.txt', 'question_summary.txt'. Assuming files are located in " + str(output_dir) + ".")
	elif args.nosentences and not args.noquestions:
		print("Combining pre-existing results. Assuming column names as specified in " + config_json_loc.name + ", and filename 'results.csv'. Assuming results file is located in " + str(output_dir) + '.')
	elif args.nosentences and args.noquestions:
		print("Combining pre-existing results. Assuming column names as specified in " + config_json_loc.name + ", and filenames 'subj_question_info.txt', 'question_summary.txt', 'results.csv'. Assuming files are located in " + str(output_dir) + '.')


	if (not os.path.isfile(subj_quest_file_name) and 
		not os.path.isfile(summary_file_name) and 
		not os.path.isfile(csv_loc)):
		print("No new results found to combine. Exiting.")
		sys.exit(1)

	print("Combining results...")
	# Check if the columns we need to conjoin the output are included in the output, and if not, exit
	if not is_item_id_included:
		print("item_id not included in results. Cannot combine results.")
		sys.exit(1)

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
				except Exception:
					print("Unable to delete non-combined results file.")

			# If we combined the questions into the results, delete them
			if combined_s_subj_quest or combined_q_stimuli:
				try:
					os.remove(subj_quest_file_name)
				except Exception:
					print("Unable to delete non-combined questions file.")

			if combined_s_questsum or combined_q_questsum:
				try:
					os.remove(summary_file_name)
				except Exception:
					print("Unable to delete non-combined questions summary file.")

print("Completed successfully!")
sys.exit(0)