######################################################################################################################
######################################### Parameters file for prASC.py ###############################################
######################################################################################################################
# asc_files_dir: the directory where your non-fix aligned ASC files are located. #####################################
###### Default is %current_dir%/ASC/. Required if doing anything other combining pre-existing results. ###############
######################################################################################################################
# fa_output_dir: the filepath where you want to output the fix aligned ASCs. #########################################
###### Default is %asc_files_dir%/Fix Aligned. Required if processing ASCs with fix_align. ###########################
######################################################################################################################
# da1_output_dir: the filepath where you want to output da1 files. Default is %asc_files_dir%/da1 files ##############
###### Required if processing ASCs or fix aligned ASCs with Robodoc ##################################################
######################################################################################################################
# script_loc: (optional) the location of a script file that contains start_pts information. ##########################
###### Default is %current_dir%/*.script. If not included (or if start_pts are not in the script), ###################
###### start_pts must be specified here or upon running prASC.py if you are fix aligning ASCs. #######################
######################################################################################################################
# fix_align_loc: the filepath to your fix_align file. ################################################################
###### Default is %current_dir%/fix_align_v0p92.R. Required if processing ASCs with fix_align. #######################
######################################################################################################################
# robodoc_loc: the filepath to Robodoc.py. Default is %current_dir%/Robodoc.py #######################################
###### Required if processing ASCs with Robodoc. #####################################################################
######################################################################################################################
######################################################################################################################
# make_regions_loc: the filepath to makeRegions_forRobodoc.py. Default is %current_dir%/makeRegions_forRobodoc.py ####
###### Required if processing ASCs with Robodoc. #####################################################################
######################################################################################################################
# config_json_loc: the filepath to your config_json_file. Default is %current_dir%/config.json. ######################
###### Required if doing anything other than running fix_align. ######################################################
######################################################################################################################
# sentences_txt_loc: the filepath to your sentences.txt file (specifies analysis regions). ###########################
###### Default is %current_dir%/sentences.txt. Required if processing (fix aligned or not) sentences with sideeye ####
###### and/or Robodoc. ###############################################################################################
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
#da1_output_dir = "ASC/da1 files"
#script_loc = ""
#fix_align_loc = "fix_align_v0p92"
#robodoc_loc = "Robodoc"
#make_regions_loc = "makeRegions_forRobodoc"

#config_json_loc = "config"
#sentences_txt_loc = "sentences"

#stimuli_loc = ""
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

######################################################################################################################
# The following parameters are needed if you are running Robodoc.py ##################################################
######################################################################################################################
# DC: 0 if you don't have display changes, 1 if you do ###############################################################
##### If you provide a script_loc, this is calculated automatically from the script file #############################
######################################################################################################################
# min_change_time: how many ms before the end of the saccade must the display change take place? #####################
######################################################################################################################
# auto_exclude: set to 1 if you want to drop subjects who lost too many trials due to blinks, 0 otherwise ############
######################################################################################################################
# exclude_threshold: max number of rejected trials in any one condition due to exclusion by a blink ##################
######################################################################################################################
# abs_exclude_threshold: max number of rejected trials overall for blinks ############################################
######################################################################################################################
# auto_exclude_DC: set to 1 to automatically drop subjects who had too many display change errors, 0 to not ##########
######################################################################################################################
# blink_num_crit: if a trial has over this number of blinks, it will be excluded #####################################
######################################################################################################################
# blink_dur_crit: if a trial has a blink over this duration, it will be excluded #####################################
######################################################################################################################
# blink_reg_exclude: "y" or "n": if a trial has a blink on the critical region, exclude it ###########################
######################################################################################################################
# blink_region: if blink_reg_exclude is "y", the number corresponding to the critical region. ########################
##### Note that this requires critical regions to be the same for all items you are analyzing ########################
######################################################################################################################
# blink_gopast: 0 to exclude trials when blinks occur during first pass on your region, 1 to exclude trials with #####
########## blinks during gopast (only used if blink_reg_exclude is "y") ##############################################
######################################################################################################################
# saccade_dur_crit: the trial will be excluded if there is a saccade longer than this coming into, in, or exiting ####
########## the critical region (set as blink_region). 1000 won't exclude anything ####################################
######################################################################################################################
# short_crit: if a fixation is shorter than this, it will be combined with a preceding/following fixation within #####
########## a one-character distance. 1 will result in no combination #################################################
######################################################################################################################
# lowest_cond: the lowest condition number you want to analyze (default is lowest value in sentences.txt) ############
######################################################################################################################
# highest_cond: the highest condition number you want to analyze (default is the highest value for this ##############
########## in sentences.txt) #########################################################################################
######################################################################################################################
#DC = 0
#min_change_time = -7
#auto_exclude = 0
#exclude_threshold = 4
#abs_exclude_threshold = 9
#auto_exclude_DC = 0
#blink_num_crit = 1000
#blink_dur_crit = 10000
#blink_reg_exclude = "n"
#blink_region = 2
#blink_gopast = 0
#saccade_dur_crit = 1000
#short_crit = 1
#lowest_cond = 
#highest_cond = 