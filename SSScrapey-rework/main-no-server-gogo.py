# ################################### #
# ################################### #
#                                     #
#  USED BY THE DAILY LAMBDA FUNCTION  #
#                                     #
# ################################### #
# ################################### #

from controllers.mainController import kickit, kickit_just_gera
import env_file as env_varz

if __name__ == "__main__":
    if env_varz.JUST_GERA == "True" or env_varz.JUST_GERA_ENV == "True":
        kickit_just_gera()
        exit(0)
    else:
        kickit()