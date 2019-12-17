######################################################################################################################
######################################### Parameters file for prASC.py ###############################################
######################################################################################################################
# asc_files_dir: the directory where your non-fix aligned ASC files are located. #####################################
###### Default is %current_dir%/ASC/. Required if doing anything other combining pre-existing results. ###############
######################################################################################################################
# fa_output_dir: the filepath to where you want to output the fix aligned ASCs. ######################################
###### Default is %current_dir%/ASC/Fix Aligned/. Required if processing ASCs with fix_align. ########################
######################################################################################################################
# script_loc: (optional) the location of a script file that contains start_pts information. ##########################
###### Default is %current_dir%/*.script. If not included (or if start_pts are not in the script), ###################
###### start_pts must be specified here or upon running prASC.py if you are fix aligning ASCs. #######################
######################################################################################################################
# fix_align_loc: the filepath to your fix_align file. ################################################################
###### Default is %current_dir%/fix_align_v0p92.R. Required if processing ASCs with fix_align. #######################
######################################################################################################################
# config_json_loc: the filepath to your config_json_file. Default is %current_dir%/config.json. ######################
###### Required if doing anything other than running fix_align. ######################################################
######################################################################################################################
# sentences_txt_loc: the filepath to your sentences.txt file (specifies analysis regions). ###########################
###### Default is %current_dir%/sentences.txt. Required if processing (fix aligned or not) sentences with sideeye. ###
######################################################################################################################
# stimuli_loc: the filepath to your stimuli file, if you want to combine stimuli with results. #######################
###### To work correctly, this file must have columns named item_id and item_condition that tag each item ############
###### with the item numbers and item condition numbers in the EyeTrack script you ran to get the ASCs. ##############
###### Default is any single file in the current directory ending with '-formatted.csv' ##############################
###### (as this is the name that scriptR gives to this file). ########################################################
######################################################################################################################
# file_encoding: the file encoding to use when opening files to combine. Only used if combining results. #############
###### Default is 'latin1'. This can be determined automatically, but it takes a loooong time, #######################
###### so just adjust this if it doesn't work for you and it'll be quicker overall. ##################################
######################################################################################################################
# output_dir: the directory where you want to output the results. ####################################################
###### Default is %current_dir%/prASCed results. Required if doing anything other than running fix_align. ############
######################################################################################################################

#asc_files_dir = "ASC"

#fa_output_dir = "ASC/Fix Aligned"
#script_loc = "Resources"
#fix_align_loc = "fix_align_v0p92"

#config_json_loc = "config"
#sentences_txt_loc = "sentences"

#stimuli_loc = "Stimuli-formatted"
#file_encoding = 'latin1'

#output_dir = "prASCed results"

######################################################################################################################
# The following parameters are optionally set to be passed to the fix_align call. ####################################
# They are only needed if you are running fix_align. #################################################################
# Any omitted parameters will have the defaults in Cohen (2013 Behav Res) with the exception of trial_plots = FALSE. #
# Explanations of how to use them can be found in Cohen (2013 Behav Res). ############################################
# start_pts must be set manually if no script file is provided and fix_align is run, #################################
# or if the optionally provided script file doesn't include them. ####################################################
######################################################################################################################
start_pts = ""
#xy_bounds = "NULL"
#keep_y_var = "FALSE"
#use_run_rule = "TRUE"
#trial_plots = "FALSE"
#save_trial_plots = "FALSE"
#summary_file = "TRUE"
#show_image = "FALSE"
#start_flag = "TRIALID"
#den_sd_cutoff = "Inf"
#den_ratio_cutoff = "1"
#k_bounds = "c(-.1, .1)"
#o_bounds = "c(-50, 50)"
#s_bounds = "c(1, 20)"
